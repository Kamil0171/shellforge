from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.admin_duty.domain.definition import ResourceType
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.runtime import SessionRuntimeState, create_session_runtime
from app.admin_duty.dynamic_command_parser import CommandParseError
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.generators import DeterministicIncidentGenerator

NOW = datetime(2026, 8, 28, 20, 0, tzinfo=UTC)


def build_shell(seed=3):
    definition = DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY,
        seed=seed,
        now=NOW,
    )
    state = create_session_runtime(definition, now=NOW)
    return definition, state, DynamicCommandService()


def execute(definition, state, service, command):
    return service.execute(definition, state, command, now=NOW)


def test_pwd_and_cd_support_absolute_relative_parent_and_home_paths():
    definition, state, service = build_shell()

    assert execute(definition, state, service, "pwd").output == "/home/operator"
    absolute = execute(definition, state, service, "cd /etc/systemd/system")
    assert absolute.current_working_directory == "/etc/systemd/system"
    assert absolute.prompt == "operator@incident:/etc/systemd/system$"
    execute(definition, state, service, "cd ..")
    assert state.current_working_directory == "/etc/systemd"
    execute(definition, state, service, "cd system")
    assert state.current_working_directory == "/etc/systemd/system"
    execute(definition, state, service, "cd ~")
    assert state.current_working_directory == "/home/operator"
    execute(definition, state, service, "cd /")
    execute(definition, state, service, "cd home/operator")
    assert state.current_working_directory == "/home/operator"


def test_cd_errors_are_realistic_accounted_and_do_not_change_cwd():
    definition, state, service = build_shell()

    missing = execute(definition, state, service, "cd /does/not/exist")
    denied = execute(definition, state, service, "cd /root")

    assert missing.output == "cd: /does/not/exist: No such file or directory"
    assert denied.output == "cd: /root: Permission denied"
    assert not missing.success
    assert not denied.success
    assert state.current_working_directory == "/home/operator"
    assert state.commands_used == 2
    assert state.revision == 2


def test_ls_cat_head_tail_grep_and_stat_use_only_virtual_filesystem():
    definition, state, service = build_shell()
    execute(definition, state, service, "cd /etc/systemd/system")

    listing = execute(definition, state, service, "ls -la")
    unit = execute(definition, state, service, "cat example-api.service")
    head = execute(definition, state, service, "head -n 2 example-api.service")
    tail = execute(definition, state, service, "tail -n 2 example-api.service")
    grep = execute(definition, state, service, "grep ExecStart example-api.service")
    stat = execute(definition, state, service, "stat example-api.service")
    missing = execute(definition, state, service, "cat C:/Windows/System32/drivers/etc/hosts")

    assert "example-api.service" in listing.output
    assert "ExecStart=/opt/example-api/legacy-api-server" in unit.output
    assert head.output.startswith("[Unit]\nDescription=")
    assert tail.output.endswith("WantedBy=multi-user.target")
    assert grep.output == "ExecStart=/opt/example-api/legacy-api-server"
    assert "File: /etc/systemd/system/example-api.service" in stat.output
    assert "No such file or directory" in missing.output


def test_virtual_filesystem_tracks_exec_start_and_permission_fault_repairs():
    definition, state, service = build_shell(seed=3)

    before_listing = execute(
        definition,
        state,
        service,
        "ls /opt/example-api",
    )
    before_unit = execute(
        definition,
        state,
        service,
        "cat /etc/systemd/system/example-api.service",
    )
    execute(
        definition,
        state,
        service,
        "systemctl set-exec-start example-api api-server",
    )
    after_unit = execute(
        definition,
        state,
        service,
        "cat /etc/systemd/system/example-api.service",
    )

    assert before_listing.output == "api-server"
    assert "legacy-api-server" in before_unit.output
    assert "ExecStart=/opt/example-api/api-server" in after_unit.output
    assert "legacy-api-server" not in after_unit.output

    permission_definition, permission_state, permission_service = build_shell(seed=0)
    permission_file = next(
        resource
        for resource in permission_state.world_state.resources.values()
        if resource.resource_type is ResourceType.FILE
    )
    permission_unit = next(
        resource
        for resource in permission_state.world_state.resources.values()
        if resource.resource_type is ResourceType.SERVICE
    )
    permission_service_name = str(permission_unit.attributes["service_name"])
    permission_app_name = permission_service_name.removesuffix(".service")
    permission_target = str(permission_unit.attributes["expected_exec_start"])
    permission_path = f"/opt/{permission_app_name}/{permission_target}"
    before_mode = execute(
        permission_definition,
        permission_state,
        permission_service,
        f"stat {permission_path}",
    )
    execute(
        permission_definition,
        permission_state,
        permission_service,
        f"chmod restore {permission_file.resource_id}",
    )
    after_mode = execute(
        permission_definition,
        permission_state,
        permission_service,
        f"stat {permission_path}",
    )

    assert "Access: (0644/" in before_mode.output
    assert "Access: (0755/" in after_mode.output


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("hostname", "app-01"),
        ("uname", "Linux"),
        ("uname -a", "GNU/Linux"),
        ("uptime", "load average"),
        ("whoami", "operator"),
        ("id", "uid=1000(operator)"),
        ("free -h", "available"),
        ("df -h", "/dev/mapper/rl-root"),
        ("ip addr", "ens192"),
        ("ip route", "default via"),
        ("ss -lntp", "0.0.0.0:22"),
    ],
)
def test_system_resource_and_network_commands_have_deterministic_rocky_output(
    command,
    expected,
):
    definition, state, service = build_shell()

    first = execute(definition, state, service, command)
    other_state = create_session_runtime(definition, now=NOW)
    second = execute(definition, other_state, service, command)

    assert expected in first.output
    assert first.output == second.output
    assert first.success


def test_systemd_status_cat_and_journal_accept_unit_name_or_resource_id():
    definition, state, service = build_shell()

    status = execute(definition, state, service, "systemctl status example-api")
    unit = execute(definition, state, service, "systemctl cat example-api.service")
    journal = execute(definition, state, service, "journalctl -u service-api")
    extended = execute(definition, state, service, "journalctl -xe")

    assert "Active: failed" in status.output
    assert "Loaded: loaded (/etc/systemd/system/example-api.service" in status.output
    assert "ExecStart=/opt/example-api/legacy-api-server" in unit.output
    assert "Failed at step EXEC" in journal.output
    assert "A start job for a unit has failed" in extended.output


def test_start_stop_and_restart_mutate_only_controlled_virtual_service():
    definition, restart_state, service = build_shell(seed=1)
    stop_state = create_session_runtime(definition, now=NOW)
    start_state = create_session_runtime(definition, now=NOW)

    restarted = execute(
        definition,
        restart_state,
        service,
        "systemctl restart example-api",
    )
    stopped = execute(definition, stop_state, service, "systemctl stop example-api")
    started = execute(definition, start_state, service, "systemctl start example-api")

    assert restarted.success
    assert stopped.success
    assert started.success
    assert restart_state.world_state.resources["service-api"].current_state == "running"
    assert stop_state.world_state.resources["service-api"].current_state == "stopped"
    assert start_state.world_state.resources["service-api"].current_state == "running"


def test_sessions_have_isolated_serializable_virtual_filesystems():
    definition, first, service = build_shell()
    second = create_session_runtime(definition, now=NOW)

    execute(definition, first, service, "cd /var/log")
    restored = SessionRuntimeState.model_validate_json(first.model_dump_json())

    assert first.current_working_directory == "/var/log"
    assert second.current_working_directory == "/home/operator"
    assert restored == first
    assert restored.virtual_rocky.filesystem is not first.virtual_rocky.filesystem


def test_incident_definition_remains_immutable_and_shell_has_no_host_escape():
    definition, state, service = build_shell()

    with pytest.raises((ValidationError, TypeError)):
        definition.presentation.title = "zmiana"

    before = state.model_dump_json()
    with pytest.raises(CommandParseError):
        execute(definition, state, service, "cat /etc/passwd; whoami")
    assert state.model_dump_json() == before


def test_wrong_exec_start_scenario_has_real_shell_diagnosis_and_controlled_repair():
    definition, state, service = build_shell(seed=3)
    commands = (
        "pwd",
        "cd /etc/systemd/system",
        "ls -la",
        "systemctl status example-api",
        "journalctl -u example-api",
        "systemctl cat example-api",
        "systemctl set-exec-start example-api api-server",
        "systemctl restart example-api",
    )

    results = [execute(definition, state, service, command) for command in commands]

    assert results[0].output == "/home/operator"
    assert "legacy-api-server" in results[4].output
    assert "legacy-api-server" in results[5].output
    assert results[-1].progress.mission_complete
    assert state.status.value == "completed"
    assert state.commands_used == len(commands)
    assert state.score == 1000 - len(commands) * definition.scoring.command_cost
