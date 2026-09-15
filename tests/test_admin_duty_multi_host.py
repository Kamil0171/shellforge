from datetime import UTC, datetime, timedelta

import pytest

from app.admin_duty.components.scenarios import build_medium_draft
from app.admin_duty.domain.generation import convert_draft_to_definition
from app.admin_duty.domain.runtime import create_session_runtime
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.validators import IncidentValidator

NOW = datetime(2026, 9, 8, 12, 0, tzinfo=UTC)


def build_session(category="dependency-firewall-blocked"):
    definition = convert_draft_to_definition(
        build_medium_draft(category, seed=11),
        created_at=NOW,
    )
    IncidentValidator().validate(definition)
    return definition, create_session_runtime(definition, now=NOW)


def execute(definition, state, command, seconds):
    return DynamicCommandService().execute(
        definition,
        state,
        command,
        now=NOW + timedelta(seconds=seconds),
    )


def test_virtual_ssh_switches_host_and_updates_prompt_without_real_io(monkeypatch):
    definition, state = build_session()

    def forbidden(*args, **kwargs):
        raise AssertionError("Virtual ssh próbował użyć hosta lub sieci.")

    monkeypatch.setattr("subprocess.run", forbidden)
    monkeypatch.setattr("subprocess.Popen", forbidden)
    monkeypatch.setattr("socket.create_connection", forbidden)

    result = execute(definition, state, "ssh app-01", 1)

    assert result.success
    assert state.active_host_id == "host-app-01"
    assert state.virtual_rocky.hostname == "app-01"
    assert result.prompt == "operator@app-01:~$"


def test_virtual_ssh_rejects_unknown_host_without_changing_context():
    definition, state = build_session()
    before = state.model_dump_json()

    result = execute(definition, state, "ssh missing-01", 1)

    assert not result.success
    assert state.active_host_id == "host-edge-01"
    assert state.virtual_rocky.hostname == "edge-01"
    assert state.commands_used == 1
    assert state.model_dump_json() != before


def test_host_switch_preserves_per_host_cwd_and_filesystem_mutations():
    definition, state = build_session()
    execute(definition, state, "cd /var/log", 1)
    execute(definition, state, "touch /tmp/edge-marker", 2)
    execute(definition, state, "ssh app-01", 3)
    execute(definition, state, "cd /etc", 4)
    execute(definition, state, "touch /tmp/app-marker", 5)

    assert "/tmp/app-marker" in state.virtual_rocky.filesystem
    assert "/tmp/edge-marker" not in state.virtual_rocky.filesystem

    edge = execute(definition, state, "ssh edge-01", 6)
    assert edge.current_working_directory == "/var/log"
    assert "/tmp/edge-marker" in state.virtual_rocky.filesystem
    assert "/tmp/app-marker" not in state.virtual_rocky.filesystem

    app = execute(definition, state, "ssh app-01", 7)
    assert app.current_working_directory == "/etc"
    assert "/tmp/app-marker" in state.virtual_rocky.filesystem


def test_each_host_has_isolated_rocky_subsystems_and_local_services():
    definition, state = build_session()
    edge = state.host_runtimes["host-edge-01"]
    app = state.host_runtimes["host-app-01"]
    data = state.host_runtimes["host-data-01"]

    assert edge.filesystem is not app.filesystem
    assert edge.packages is not app.packages
    assert edge.processes is not app.processes
    assert edge.network is not app.network
    assert edge.firewall is not app.firewall
    assert edge.selinux is not app.selinux
    assert edge.systemd_unit_cache == {"edge-proxy.service": edge.systemd_unit_cache["edge-proxy.service"]}
    assert "orders-api.service" in app.systemd_unit_cache
    assert "database.service" in data.systemd_unit_cache


def test_multi_host_state_is_isolated_between_sessions():
    definition, first = build_session()
    second = create_session_runtime(definition, now=NOW)

    execute(definition, first, "ssh app-01", 1)
    execute(definition, first, "touch /tmp/private-marker", 2)

    assert "/tmp/private-marker" in first.virtual_rocky.filesystem
    assert "/tmp/private-marker" not in second.host_runtimes["host-app-01"].filesystem
    assert second.active_host_id == "host-edge-01"


def test_systemd_commands_cannot_control_service_on_another_host():
    definition, state = build_session()

    with pytest.raises(ValueError, match="innym hoście"):
        execute(definition, state, "systemctl status orders-api", 1)
