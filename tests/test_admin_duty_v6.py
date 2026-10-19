from datetime import UTC, datetime, timedelta

import pytest

from app.admin_duty.components.scenarios import build_hard_draft, build_medium_draft
from app.admin_duty.domain.definition import DataField
from app.admin_duty.domain.dependencies import (
    flow_is_healthy,
    flow_verification_fact,
    reconcile_dependencies,
)
from app.admin_duty.domain.generation import convert_draft_to_definition
from app.admin_duty.domain.progress import get_session_progress
from app.admin_duty.domain.recovery import resolved_fault_ids
from app.admin_duty.domain.runtime import create_session_runtime
from app.admin_duty.dynamic_command_parser import (
    CommandParseError,
    parse_dynamic_command,
)
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.repositories import (
    InMemoryScenarioRepository,
    InMemorySessionRepository,
)
from app.admin_duty.services import DynamicIncidentService
from app.admin_duty.services.public_gameplay import (
    project_public_game_map,
    project_public_monitoring,
)
from app.admin_duty.validators import IncidentValidationError, IncidentValidator

NOW = datetime(2026, 10, 7, 12, tzinfo=UTC)


def runtime(draft):
    definition = convert_draft_to_definition(draft, created_at=NOW)
    return definition, create_session_runtime(definition, now=NOW)


def command(definition, state, text):
    return DynamicCommandService().execute(
        definition,
        state,
        text,
        now=NOW + timedelta(seconds=len(state.command_history) + 1),
    )


@pytest.mark.parametrize(
    "category", ["dependency-port-mismatch", "selinux-proxy-context-invalid"]
)
def test_entry_endpoint_includes_proxy_health(category):
    definition, state = runtime(build_medium_draft(category, seed=17))
    assert (
        state.world_state.resources["service-proxy"].attributes["public_health"]
        == "unhealthy"
    )
    assert state.world_state.resources["endpoint-portal"].current_state != "healthy"
    assert not get_session_progress(definition, state).mission_complete


def test_down_target_has_no_ping_tcp_or_http_reachability():
    definition, state = runtime(
        build_medium_draft("networkmanager-connection-inactive", seed=17)
    )
    for text in (
        "ping 10.24.8.20",
        "nc -z 10.24.8.20 8080",
        "curl http://10.24.8.20:8080",
    ):
        assert not command(definition, state, text).success


def test_tcp_success_and_http_503_do_not_mean_healthy_application():
    definition, state = runtime(
        build_medium_draft("service-config-permission-denied", seed=17)
    )
    assert command(definition, state, "nc -z 10.24.8.20 8080").success
    response = command(definition, state, "curl http://10.24.8.20:8080")
    assert response.success
    assert "503 Service Unavailable" in response.output
    assert "endpoint-healthy:host-app-01:8080" not in state.discovered_fact_ids
    proxy = state.world_state.resources["service-proxy"]
    assert proxy.attributes["transport_health"] == "healthy"
    assert proxy.attributes["downstream_health"] == "unhealthy"


def test_localhost_does_not_verify_public_ingress():
    definition, state = runtime(build_hard_draft("H-02", seed=17))
    for text in (
        "ssh app-0017",
        "nmcli connection modify System-ens192 ipv4.dns 10.24.8.53",
        "ssh edge-0017",
        "curl http://localhost",
        "firewall-cmd --permanent --add-service=http",
        "firewall-cmd --reload",
    ):
        assert command(definition, state, text).success
    assert not get_session_progress(definition, state).mission_complete
    assert "endpoint-healthy:host-edge-01:80" not in state.discovered_fact_ids
    command(definition, state, "ssh client-0017")
    assert command(
        definition, state, "curl http://portal.internal"
    ).progress.mission_complete


def test_verification_fact_is_invalidated_by_unhealthy_path():
    definition, state = runtime(build_medium_draft("dependency-port-mismatch", seed=17))
    state.discovered_fact_ids.add("endpoint-healthy:host-edge-01:80")
    reconcile_dependencies(definition, state)
    assert "endpoint-healthy:host-edge-01:80" not in state.discovered_fact_ids


@pytest.mark.parametrize(
    "text",
    [
        "nc host 80",
        "nc -z host 80-90",
        "nc -z host 0",
        "nc -z host 65536",
        "nc -vz host 80",
        "nc -l 80",
        "nc -z host 80 443",
        "nc -z $(hostname) 80",
        "nc -z host 80; pwd",
        "nc -z host 80 | cat",
        "nc -z host ８０",
    ],
)
def test_tcp_probe_rejects_unapproved_syntax(text):
    with pytest.raises(CommandParseError):
        parse_dynamic_command(text)


def replay_step(definition, state, step):
    result = command(definition, state, step.input)
    if step.capability_id == "filesystem.edit":
        result = DynamicCommandService().save_file(
            definition,
            state,
            path=result.editor.path,
            content=next(
                field.value for field in step.parameters if field.key == "content"
            ),
            now=state.last_activity + timedelta(milliseconds=500),
        )
    assert result.success is step.expected_success
    return result


FLOW_CASES = [
    ("medium", "dependency-port-mismatch", 2),
    ("medium", "systemd-stale-unit-config", 2),
    ("medium", "service-config-permission-denied", 3),
    ("medium", "dependency-firewall-blocked", 3),
    ("hard", "H-03", 2),
    ("hard", "H-04", 3),
    ("hard", "H-05", 3),
    ("hard", "H-02", 5),
]


@pytest.mark.parametrize("seed,world", [(0, "datacenter-hall"), (1, "modern-noc")])
@pytest.mark.parametrize("level,category,hosts", FLOW_CASES)
def test_flow_replays_real_path_on_both_worlds(level, category, hosts, seed, world):
    draft = (build_medium_draft if level == "medium" else build_hard_draft)(
        category, seed=seed
    )
    definition, state = runtime(draft)
    IncidentValidator().validate(definition)
    flow = definition.multi_host_flow
    assert len(state.host_runtimes) == hosts
    assert (
        project_public_game_map(definition.initial_world_state.map, state).world_id
        == world
    )
    assert not flow_is_healthy(definition, state)
    assert (
        state.world_state.resources[flow.entry_endpoint_id].current_state != "healthy"
    )
    partial = False
    initial_signals = project_public_monitoring(definition, state).signals
    for step in definition.solution:
        expected_host = next(
            field.value for field in step.parameters if field.key == "expected_host_id"
        )
        assert state.active_host_id == expected_host
        result = replay_step(definition, state, step)
        if level == "hard" and len(resolved_fault_ids(definition, state)) == 1:
            partial = True
            assert not result.progress.mission_complete
            assert (
                initial_signals != project_public_monitoring(definition, state).signals
            )
    assert result.progress.mission_complete
    assert flow_is_healthy(definition, state)
    assert flow_verification_fact(flow) in state.discovered_fact_ids
    assert partial is (level == "hard")


def repaired_unverified_flow():
    definition, state = runtime(
        build_medium_draft("service-config-permission-denied", seed=17)
    )
    for step in definition.solution[:-1]:
        replay_step(definition, state, step)
    assert flow_is_healthy(definition, state)
    assert not get_session_progress(definition, state).mission_complete
    return definition, state


def test_flow_verification_requires_source_entry_port_and_path():
    definition, state = repaired_unverified_flow()
    fact = flow_verification_fact(definition.multi_host_flow)
    for text in (
        "curl http://localhost",
        "curl http://api.internal:8080",
        "curl http://portal.internal/other",
        "curl http://portal.internal:8080",
    ):
        command(definition, state, text)
        assert fact not in state.discovered_fact_ids
        assert not get_session_progress(definition, state).mission_complete
    command(definition, state, "ssh app-01")
    assert command(definition, state, "curl http://portal.internal").success
    assert fact not in state.discovered_fact_ids
    command(definition, state, "ssh edge-01")
    assert command(
        definition, state, "curl http://portal.internal"
    ).progress.mission_complete


def test_flow_verification_expires_when_transport_breaks():
    definition, state = repaired_unverified_flow()
    fact = flow_verification_fact(definition.multi_host_flow)
    command(definition, state, "ssh app-01")
    state.discovered_fact_ids.add(fact)
    command(definition, state, "nmcli connection down System-ens192")
    assert state.status.value == "active"
    assert not flow_is_healthy(definition, state)
    assert fact not in state.discovered_fact_ids
    assert not get_session_progress(definition, state).mission_complete


def test_flow_validator_rejects_missing_edge_and_wrong_host_context():
    definition, _ = runtime(build_medium_draft("dependency-firewall-blocked", seed=17))
    flow = definition.multi_host_flow.model_copy(
        update={"service_path": ("service-proxy", "service-database")}
    )
    with pytest.raises(IncidentValidationError, match="grafie"):
        IncidentValidator().validate(
            definition.model_copy(update={"multi_host_flow": flow})
        )
    first = definition.solution[0].model_copy(
        update={
            "parameters": (DataField(key="expected_host_id", value="host-data-01"),)
        }
    )
    with pytest.raises(IncidentValidationError) as error:
        IncidentValidator().validate(
            definition.model_copy(
                update={"solution": (first, *definition.solution[1:])}
            )
        )
    assert "hosta" in str(error.value.__cause__)


def test_journal_tracks_transport_recovery_without_static_repair_hints():
    definition, state = runtime(
        build_medium_draft("dependency-firewall-blocked", seed=17)
    )
    app = state.host_runtimes["host-app-01"]
    assert any(
        "data-01:5432 transport niedostępny" in line for line in app.journal_entries
    )
    for step in definition.solution:
        replay_step(definition, state, step)
    entries = state.host_runtimes["host-app-01"].journal_entries
    assert any("data-01:5432 transport dostępny" in line for line in entries)
    assert not any("fault-" in line or "--add-port" in line for line in entries)


def test_dns_mismatch_agrees_between_dependency_and_tcp_probe():
    definition, state = repaired_unverified_flow()
    state.host_runtimes["host-edge-01"].network.dns_records["api.internal"] = (
        "10.24.8.30"
    )
    reconcile_dependencies(definition, state)
    assert (
        state.world_state.resources["service-proxy"].attributes["transport_health"]
        == "unhealthy"
    )
    assert not command(definition, state, "nc -z api.internal 8080").success
    assert command(definition, state, "nc -z 10.24.8.20 8080").success
    assert not flow_is_healthy(definition, state)


def test_wrong_dns_server_blocks_names_but_preserves_ip_connectivity():
    definition, state = repaired_unverified_flow()
    command(
        definition, state, "nmcli connection modify System-ens192 ipv4.dns 192.0.2.53"
    )
    assert not command(definition, state, "dig api.internal").success
    assert not command(definition, state, "nc -z api.internal 8080").success
    assert command(definition, state, "nc -z 10.24.8.20 8080").success
    assert not flow_is_healthy(definition, state)


@pytest.mark.parametrize("seed", [0, 1])
@pytest.mark.parametrize("level,category,hosts", FLOW_CASES)
def test_active_and_partial_public_projections_do_not_leak_private_flow(
    level, category, hosts, seed
):
    definition, _ = runtime(
        (build_medium_draft if level == "medium" else build_hard_draft)(
            category, seed=seed
        )
    )
    sessions = InMemorySessionRepository()
    service = DynamicIncidentService(
        generator=DeterministicIncidentGenerator(),
        scenario_repository=InMemoryScenarioRepository(),
        session_repository=sessions,
    )
    started = service._start_definition(definition, NOW)
    assert (
        sum(node.type.value == "host" for node in started.infrastructure.nodes) == hosts
    )
    payloads = [
        started.model_dump_json(),
        service.get_progress(started.session_id, now=NOW).model_dump_json(),
    ]
    if level == "hard":
        current = NOW
        for step in definition.solution:
            current += timedelta(seconds=2)
            result = service.execute_command(
                started.session_id, step.input, now=current
            )
            if step.capability_id == "filesystem.edit":
                current += timedelta(seconds=1)
                service.save_file(
                    started.session_id,
                    path=result.editor.path,
                    content=next(
                        field.value
                        for field in step.parameters
                        if field.key == "content"
                    ),
                    now=current,
                )
            if (
                len(
                    resolved_fault_ids(
                        definition, sessions.get(started.session_id, now=current)
                    )
                )
                == 1
            ):
                payloads.append(
                    service.get_progress(
                        started.session_id, now=current
                    ).model_dump_json()
                )
                break
    for payload in payloads:
        for private in (
            "fault-primary",
            "fault-secondary",
            '"faults"',
            '"fault_count"',
            '"fault_id"',
            '"repair_order"',
            '"multi_host_flow"',
            '"service_path"',
            '"entry_endpoint_id"',
            '"verification_source_host_id"',
            '"solution"',
            '"reference_solution"',
            '"resolution_condition"',
            '"port_configuration_file_id"',
            '"expected_host_id"',
        ):
            assert private not in payload


@pytest.mark.parametrize("combination", ["H-03", "H-04", "H-05"])
def test_v6_hard_accepts_alternative_repair_order(combination):
    definition, state = runtime(build_hard_draft(combination, seed=17))
    if combination == "H-03":
        assert not command(definition, state, "nc -z api.internal 8080").success
        for text in (
            "ssh app-0017",
            "dnf install -y python3-psycopg2",
            "systemctl restart orders-api",
            "ssh edge-0017",
        ):
            assert command(definition, state, text).success
        assert command(definition, state, "nc -z api.internal 8080").success
        remaining = [
            step
            for step in definition.solution
            if step.capability_id in {"filesystem.edit", "systemd.daemon-reload"}
            or step.input == "systemctl restart edge-proxy"
        ]
    elif combination == "H-04":
        proxy_edit = next(
            step
            for step in definition.solution
            if step.input == "nano /opt/edge-proxy/upstream.conf"
        )
        replay_step(definition, state, proxy_edit)
        command(definition, state, "systemctl restart edge-proxy")
        assert command(definition, state, "nc -z api.internal 8080").success
        command(definition, state, "ssh app-0017")
        remaining = [
            step
            for step in definition.solution
            if step.input
            in {"nano /opt/orders-api/app.conf", "systemctl restart orders-api"}
        ]
    else:
        assert not command(definition, state, "nc -z database.internal 5432").success
        for text in (
            "ssh data-0017",
            "firewall-cmd --permanent --add-port=5432/tcp",
            "firewall-cmd --reload",
            "ssh edge-0017",
        ):
            assert command(definition, state, text).success
        assert command(definition, state, "nc -z database.internal 5432").success
        command(definition, state, "ssh app-0017")
        remaining = [
            step
            for step in definition.solution
            if step.input == "nmcli connection up System-ens192"
        ]
    assert len(resolved_fault_ids(definition, state)) == 1
    assert not get_session_progress(definition, state).mission_complete
    for step in remaining:
        replay_step(definition, state, step)
    assert len(resolved_fault_ids(definition, state)) == 2
    assert flow_is_healthy(definition, state)
    assert not get_session_progress(definition, state).mission_complete
    if state.active_host_id != "host-edge-01":
        command(definition, state, "ssh edge-0017")
    assert command(
        definition, state, "curl http://portal.internal"
    ).progress.mission_complete


def test_tcp_probe_never_calls_host_execution_or_real_network(monkeypatch):
    import builtins
    import os
    import socket
    import subprocess
    from pathlib import Path

    definition, state = runtime(build_medium_draft("dependency-port-mismatch", seed=17))

    def forbidden(*args, **kwargs):
        pytest.fail("Wirtualna sonda naruszyła granicę symulacji.")

    for target, name in (
        (builtins, "open"),
        (Path, "open"),
        (os, "system"),
        (socket, "socket"),
        (socket, "create_connection"),
        (subprocess, "run"),
        (subprocess, "Popen"),
    ):
        monkeypatch.setattr(target, name, forbidden)
    assert command(definition, state, "nc -z api.internal 8080").success
    assert not command(definition, state, "nc -z api.internal 8081").success
    assert not command(definition, state, "nc -z example.com 443").success


def test_tcp_probe_matches_sshd_listener_and_target_firewall():
    definition, state = runtime(build_medium_draft("dependency-port-mismatch", seed=17))
    assert ":22" in command(definition, state, "ss -lntp").output
    assert command(definition, state, "nc -z api.internal 22").success
    state.host_runtimes["host-app-01"].firewall.runtime_services.remove("ssh")
    assert not command(definition, state, "nc -z api.internal 22").success


def test_dynamic_journal_does_not_repeat_unchanged_observations():
    definition, state = runtime(build_medium_draft("dependency-port-mismatch", seed=17))
    initial = {
        host_id: list(host.journal_entries)
        for host_id, host in state.host_runtimes.items()
    }
    command(definition, state, "nc -z api.internal 8080")
    command(definition, state, "curl http://portal.internal")
    assert {
        host_id: host.journal_entries for host_id, host in state.host_runtimes.items()
    } == initial
