import builtins
import os
import socket
import subprocess
from datetime import timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.admin_duty.domain.runtime import (
    InactiveSessionError,
    SessionStatus,
    create_session_runtime,
)
from app.admin_duty.dynamic_command_parser import CommandParseError
from tests.test_admin_duty_virtual_shell import NOW, build_shell, execute


def test_filesystem_mutations_and_editor_round_trip_are_isolated():
    definition, state, service = build_shell()
    other = create_session_runtime(definition, now=NOW)
    commands = ("mkdir -p ~/work/nested", "touch ~/work/nested/file.txt")
    for command in commands:
        assert execute(definition, state, service, command).success
    saved = service.save_file(
        definition,
        state,
        path="~/work/nested/file.txt",
        content="Pierwsza\nDruga\n",
        now=NOW,
    )
    assert saved.success
    assert (
        execute(
            definition, state, service, "nano ~/work/nested/file.txt"
        ).editor.content
        == "Pierwsza\nDruga\n"
    )
    assert execute(
        definition, state, service, "cp ~/work/nested/file.txt ~/work/copy.txt"
    ).success
    assert execute(
        definition, state, service, "mv ~/work/copy.txt ~/work/moved.txt"
    ).success
    assert (
        execute(definition, state, service, "cat ~/work/moved.txt").output
        == "Pierwsza\nDruga"
    )
    assert execute(definition, state, service, "chmod 600 ~/work/moved.txt").success
    assert execute(
        definition, state, service, "chown app:root ~/work/moved.txt"
    ).success
    assert "app" in execute(definition, state, service, "stat ~/work/moved.txt").output
    assert (
        "moved.txt"
        in execute(definition, state, service, 'find ~/work -name "*.txt"').output
    )
    assert execute(definition, state, service, "du -sh ~/work").output.endswith(
        "/home/operator/work"
    )
    assert not execute(definition, state, service, "rmdir ~/work").success
    assert execute(definition, state, service, "rm -r ~/work/nested").success
    assert execute(definition, state, service, "rm ~/work/moved.txt").success
    assert execute(definition, state, service, "rmdir ~/work").success
    assert other.commands_used == 0
    assert (
        other.virtual_rocky.filesystem
        == create_session_runtime(definition, now=NOW).virtual_rocky.filesystem
    )


def test_copy_does_not_replace_a_directory_and_mkdir_p_is_idempotent():
    definition, state, service = build_shell()
    for command in ("mkdir -p ~/target/README.txt", "mkdir -p ~/target"):
        assert execute(definition, state, service, command).success
    assert not execute(definition, state, service, "cp ~/README.txt ~/target").success
    assert (
        state.virtual_rocky.filesystem["/home/operator/target/README.txt"].kind
        == "directory"
    )
    assert not execute(
        definition, state, service, "mkdir -p ~/README.txt/child"
    ).success
    assert not execute(definition, state, service, "rm -r /home").success


@pytest.mark.parametrize(
    "command",
    [
        "touch ~/atomic",
        "dnf install nginx",
        "nmcli connection down System-ens192",
        "firewall-cmd --add-service=http",
        "setenforce 0",
        "systemctl restart orders-api",
        "chmod 600 ~/README.txt",
        "chown app:app ~/README.txt",
        "cp ~/README.txt ~/copy",
        "mv ~/README.txt ~/renamed",
        "rm ~/README.txt",
    ],
)
def test_mutating_commands_are_atomic_on_invalid_timestamp(command):
    definition, state, service = build_shell()
    before = state.model_dump_json()
    with pytest.raises(ValueError, match="nie może cofać"):
        service.execute(definition, state, command, now=NOW - timedelta(seconds=1))
    assert state.model_dump_json() == before


@pytest.mark.parametrize(
    "command",
    [
        "dnf install nginx",
        "firewall-cmd --add-service=http",
        "systemctl disable orders-api",
        "nmcli connection down System-ens192",
        "setenforce 0",
    ],
)
def test_runtime_subsystems_are_isolated_between_sessions(command):
    definition, first, service = build_shell()
    second = create_session_runtime(definition, now=NOW)
    before = second.model_dump_json()
    assert execute(definition, first, service, command).success
    assert second.model_dump_json() == before
    assert first.virtual_rocky != second.virtual_rocky


def test_editor_save_rolls_back_file_and_reload_flag_on_accounting_error():
    definition, state, service = build_shell()
    before = state.model_dump_json()
    with pytest.raises(ValueError, match="nie może cofać"):
        service.save_file(
            definition,
            state,
            path="/etc/systemd/system/orders-api.service",
            content="[Service]\nExecStart=/new\n",
            now=NOW - timedelta(seconds=1),
        )
    assert state.model_dump_json() == before


@pytest.mark.parametrize("status", [SessionStatus.COMPLETED, SessionStatus.ENDED])
def test_editor_rejects_inactive_sessions_atomically(status):
    definition, state, service = build_shell()
    state.status = status
    before = state.model_dump_json()
    with pytest.raises(InactiveSessionError):
        service.save_file(
            definition,
            state,
            path="/etc/systemd/system/orders-api.service",
            content="[Service]",
            now=NOW,
        )
    assert state.model_dump_json() == before


def test_unit_editor_requires_daemon_reload_then_updates_processes_and_journal():
    definition, state, service = build_shell()
    path = "/etc/systemd/system/orders-api.service"
    original_cache = dict(state.virtual_rocky.systemd_unit_cache)
    editor = execute(definition, state, service, f"nano {path}").editor
    assert editor
    content = editor.content.replace("legacy-api-server", "api-server")
    assert service.save_file(
        definition, state, path=path, content=content, now=NOW
    ).success
    assert execute(definition, state, service, f"nano {path}").editor.content == content
    assert state.virtual_rocky.systemd_unit_cache == original_cache
    assert not execute(
        definition, state, service, "systemctl restart orders-api"
    ).success
    assert (
        "daemon-reload"
        in execute(definition, state, service, "systemctl status orders-api").output
    )
    assert execute(definition, state, service, "systemctl daemon-reload").success
    assert not state.virtual_rocky.daemon_reload_required
    assert execute(
        definition, state, service, "systemctl restart orders-api"
    ).progress.mission_complete
    assert any(
        p.service_resource_id == "service-api"
        for p in state.virtual_rocky.processes.values()
    )
    assert "Started" in state.virtual_rocky.journal_entries[-1]


@pytest.mark.parametrize(
    "command",
    [
        "install nginx",
        "update nginx",
        "remove nginx",
        "clean all",
        "list installed",
        "repolist",
        "info nginx",
    ],
)
def test_yum_and_dnf_share_exactly_the_same_state_and_output(command):
    definition, left, service = build_shell()
    right = create_session_runtime(definition, now=NOW)
    for state in (left, right):
        execute(definition, state, service, "dnf install nginx")
    dnf = execute(definition, left, service, "dnf " + command)
    yum = execute(definition, right, service, "yum " + command)
    assert dnf.output == yum.output
    assert dnf.success == yum.success
    assert left.virtual_rocky == right.virtual_rocky
    assert left.world_state == right.world_state


def test_packages_install_rpm_update_remove_and_disabled_repository():
    definition, state, service = build_shell()
    assert not execute(definition, state, service, "rpm -q nginx").success
    assert not execute(definition, state, service, "dnf update nginx").success
    assert execute(definition, state, service, "yum install nginx -y").success
    assert "nginx-" in execute(definition, state, service, "rpm -qa").output
    assert "Version" in execute(definition, state, service, "rpm -qi nginx").output
    assert execute(definition, state, service, "systemctl start nginx").success
    assert "nginx" in execute(definition, state, service, "ps aux").output
    assert ":80" in execute(definition, state, service, "ss -lntp").output
    assert execute(definition, state, service, "dnf remove nginx").success
    assert "/usr/sbin/nginx" not in state.virtual_rocky.filesystem
    assert "nginx.service" not in state.virtual_rocky.systemd_unit_cache
    assert "nginx" not in execute(definition, state, service, "ps -ef").output
    state.virtual_rocky.packages.enabled_repositories.discard("appstream")
    assert not execute(definition, state, service, "dnf install nginx").success


def test_firewall_permanent_reload_network_and_nmcli_interact():
    definition, state, service = build_shell()
    for command in ("dnf install nginx", "systemctl start nginx"):
        assert execute(definition, state, service, command).success
    assert execute(definition, state, service, "curl http://localhost").success
    assert not execute(definition, state, service, "curl http://app-01").success
    execute(definition, state, service, "firewall-cmd --permanent --add-service=http")
    assert "http" not in state.virtual_rocky.firewall.runtime_services
    execute(definition, state, service, "firewall-cmd --reload")
    assert execute(definition, state, service, "curl http://app-01").success
    assert not execute(
        definition, state, service, "curl http://probe.internal"
    ).success
    execute(definition, state, service, "firewall-cmd --remove-service=http")
    execute(definition, state, service, "firewall-cmd --add-port=80/tcp")
    assert execute(definition, state, service, "curl http://app-01").success
    execute(definition, state, service, "firewall-cmd --remove-port=80/tcp")
    assert not execute(definition, state, service, "curl http://app-01").success
    assert execute(definition, state, service, "ping -c 1 probe.internal").success
    assert (
        "10.24.8.40"
        in execute(definition, state, service, "dig probe.internal").output
    )
    assert (
        "10.24.8.40"
        in execute(definition, state, service, "getent hosts probe.internal").output
    )
    execute(definition, state, service, "nmcli connection down System-ens192")
    assert (
        "disconnected"
        in execute(definition, state, service, "nmcli device status").output
    )
    assert execute(definition, state, service, "ip route").output == ""
    assert not execute(definition, state, service, "ping probe.internal").success
    assert execute(definition, state, service, "curl localhost").success
    execute(definition, state, service, "nmcli connection up System-ens192")
    assert "default via" in execute(definition, state, service, "ip route").output


def test_selinux_context_controls_service_start_and_restorecon_repairs_it():
    definition, state, service = build_shell(seed=1)
    state.virtual_rocky.selinux.file_contexts["/opt/orders-api"] = (
        "system_u:object_r:wrong_t:s0"
    )
    assert not execute(
        definition, state, service, "systemctl restart orders-api"
    ).success
    assert (
        "SELinux"
        in execute(definition, state, service, "journalctl -u orders-api -n 1").output
    )
    assert "Enforcing" in execute(definition, state, service, "getenforce").output
    execute(definition, state, service, "setenforce 0")
    assert state.virtual_rocky.selinux.mode == "Permissive"
    execute(definition, state, service, "setenforce 1")
    assert (
        "/opt/orders-api"
        in execute(definition, state, service, "semanage fcontext -l").output
    )
    assert execute(definition, state, service, "restorecon -R /opt").success
    assert execute(definition, state, service, "systemctl restart orders-api").success


def test_systemd_enable_disable_stop_and_journal_time_filter():
    definition, state, service = build_shell()
    execute(definition, state, service, "systemctl disable orders-api")
    assert not execute(
        definition, state, service, "systemctl is-enabled orders-api"
    ).success
    execute(definition, state, service, "systemctl enable orders-api")
    assert execute(
        definition, state, service, "systemctl is-enabled orders-api"
    ).success
    execute(definition, state, service, "systemctl stop orders-api")
    assert not execute(
        definition, state, service, "systemctl is-active orders-api"
    ).success
    assert "Stopped" in execute(definition, state, service, "journalctl -n 1").output
    assert (
        "Stopped"
        in execute(
            definition, state, service, 'journalctl --since "2026-08-28 00:00:00"'
        ).output
    )
    assert (
        "Brak wpisów"
        in execute(definition, state, service, "journalctl --since 2027-01-01").output
    )


@pytest.mark.parametrize(
    "command",
    [
        "curl http://[bad",
        "curl http://host:invalid",
        "curl file:///etc/passwd",
        "curl http://",
        "firewall-cmd --add-port=99999/tcp",
        "dnf install unknown",
    ],
)
def test_invalid_arguments_return_controlled_failure(command):
    definition, state, service = build_shell()
    assert not execute(definition, state, service, command).success


def test_no_host_access_for_commands_or_editor(monkeypatch):
    definition, state, service = build_shell()

    def forbidden(*args, **kwargs):
        raise AssertionError("Host access from virtual command")

    with monkeypatch.context() as patch:
        for owner, name in (
            (builtins, "open"),
            (os, "system"),
            (subprocess, "run"),
            (subprocess, "Popen"),
            (socket, "socket"),
            (socket, "getaddrinfo"),
            (Path, "open"),
            (Path, "read_text"),
            (Path, "write_text"),
        ):
            patch.setattr(owner, name, forbidden)
        for command in (
            "pwd",
            "find /etc",
            "ps aux",
            "systemctl status",
            "journalctl -xe",
            "dnf install nginx",
            "yum info nginx",
            "rpm -qa",
            "systemctl start nginx",
            "curl localhost",
            "ping probe.internal",
            "getenforce",
            "firewall-cmd --list-all",
            "nmcli connection show",
        ):
            assert execute(definition, state, service, command).success
        assert service.save_file(
            definition, state, path="/etc/os-release", content="virtual only", now=NOW
        ).success
        assert not execute(definition, state, service, "cat C:/Windows/win.ini").success
        for command in (
            "pwd && whoami",
            "ls | cat",
            "echo x > /tmp/x",
            "systemctl set-exec-start orders-api api-server",
            "env restore orders-api DATABASE_URL",
            "chmod restore /opt/orders-api/api-server",
        ):
            with pytest.raises(CommandParseError):
                execute(definition, state, service, command)


def test_editor_size_limit_and_runtime_capacity_are_atomic():
    definition, state, service = build_shell()
    before = state.virtual_rocky.model_dump_json()
    assert not service.save_file(
        definition, state, path="/etc/os-release", content="ą" * 20000, now=NOW
    ).success
    assert state.virtual_rocky.model_dump_json() == before
    with pytest.raises(ValidationError):
        state.virtual_rocky.model_validate(
            {
                **state.virtual_rocky.model_dump(),
                "filesystem": {
                    "bad": state.virtual_rocky.filesystem["/etc/os-release"]
                },
            }
        )
