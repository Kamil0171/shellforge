import posixpath
from datetime import datetime

from app.admin_duty.domain.definition import IncidentDefinition, ResourceType
from app.admin_duty.domain.engine import DynamicIncidentEngine, ResourceStateUpdate
from app.admin_duty.domain.runtime import SessionRuntimeState, VirtualFileEntry
from app.admin_duty.dynamic_commands import (
    CommandExecutionResult,
    _account_read_only_command,
    _get_systemd_service,
    _restart_prerequisites_met,
)

SHELL_CAPABILITIES = (
    "shell.pwd",
    "shell.cd",
    "filesystem.list",
    "filesystem.read",
    "filesystem.head",
    "filesystem.tail",
    "filesystem.grep",
    "filesystem.path-stat",
    "system.hostname",
    "system.uname",
    "system.uptime",
    "system.whoami",
    "system.id",
    "systemd.status",
    "systemd.restart",
    "systemd.cat",
    "systemd.start",
    "systemd.stop",
    "journal.read",
    "journal.xe",
    "resources.memory",
    "resources.disk",
    "network.addr",
    "network.route",
    "network.listeners",
)


def _engine(engine: DynamicIncidentEngine | None) -> DynamicIncidentEngine:
    return engine if engine is not None else DynamicIncidentEngine()


def _account(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    fact_id: str,
    engine: DynamicIncidentEngine | None,
    now: datetime | None,
):
    return _account_read_only_command(
        definition,
        state,
        fact_id=fact_id,
        engine=engine,
        now=now,
    )


def _result(output: str, success: bool, progress) -> CommandExecutionResult:
    return CommandExecutionResult(output=output[:1000], success=success, progress=progress)


def _resolve_path(state: SessionRuntimeState, path: str) -> str:
    home = state.virtual_rocky.home_directory
    if path == "~":
        return home
    if path.startswith("~/"):
        path = f"{home}/{path[2:]}"
    if not path.startswith("/"):
        path = posixpath.join(state.current_working_directory, path)
    return "/" + posixpath.normpath(path).lstrip("/")


def _is_denied(path: str) -> bool:
    return path == "/root" or path.startswith("/root/")


def _entry(state: SessionRuntimeState, path: str) -> VirtualFileEntry | None:
    return state.virtual_rocky.filesystem.get(path)


def _mode_string(entry: VirtualFileEntry) -> str:
    permissions = entry.mode[-3:]
    pieces = []
    for value in permissions:
        digit = int(value)
        pieces.append("r" if digit & 4 else "-")
        pieces.append("w" if digit & 2 else "-")
        pieces.append("x" if digit & 1 else "-")
    return ("d" if entry.kind == "directory" else "-") + "".join(pieces)


def _children(state: SessionRuntimeState, directory: str) -> list[VirtualFileEntry]:
    prefix = "/" if directory == "/" else f"{directory}/"
    return sorted(
        (
            entry
            for path, entry in state.virtual_rocky.filesystem.items()
            if path.startswith(prefix) and "/" not in path[len(prefix) :]
        ),
        key=lambda item: (item.kind != "directory", item.path),
    )


def _path_error(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    program: str,
    path: str,
    reason: str,
    engine: DynamicIncidentEngine | None,
    now: datetime | None,
) -> CommandExecutionResult:
    progress = _account(
        definition,
        state,
        fact_id=f"shell-error:{program}",
        engine=engine,
        now=now,
    )
    return _result(f"{program}: {path}: {reason}", False, progress)


def shell_pwd(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    progress = _account(definition, state, fact_id="shell:pwd", engine=engine, now=now)
    return _result(state.current_working_directory, True, progress)


def shell_cd(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    if _is_denied(target):
        return _path_error(definition, state, program="cd", path=resource_id, reason="Permission denied", engine=engine, now=now)
    entry = _entry(state, target)
    if entry is None:
        return _path_error(definition, state, program="cd", path=resource_id, reason="No such file or directory", engine=engine, now=now)
    if entry.kind != "directory":
        return _path_error(definition, state, program="cd", path=resource_id, reason="Not a directory", engine=engine, now=now)
    previous = state.current_working_directory
    state.current_working_directory = target
    try:
        progress = _account(definition, state, fact_id="shell:cd", engine=engine, now=now)
    except Exception:
        state.current_working_directory = previous
        raise
    return _result("", True, progress)


def shell_ls(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    if _is_denied(target):
        return _path_error(definition, state, program="ls", path=resource_id, reason="Permission denied", engine=engine, now=now)
    entry = _entry(state, target)
    if entry is None:
        return _path_error(definition, state, program="ls", path=resource_id, reason="No such file or directory", engine=engine, now=now)
    long_format = "-l" in arguments or "-la" in arguments or "-al" in arguments
    entries = _children(state, target) if entry.kind == "directory" else [entry]
    if long_format:
        lines = [f"total {len(entries) * 4}"]
        if "-a" in arguments or "-la" in arguments or "-al" in arguments:
            lines.extend(("drwxr-xr-x  2 operator operator 4096 .", "drwxr-xr-x  3 root root 4096 .."))
        for item in entries:
            size = 4096 if item.kind == "directory" else len(item.content.encode("utf-8"))
            lines.append(f"{_mode_string(item)}  1 {item.owner:<8} {item.group:<8} {size:>5} {posixpath.basename(item.path)}")
        output = "\n".join(lines)
    else:
        output = "  ".join(posixpath.basename(item.path) for item in entries)
    progress = _account(definition, state, fact_id="filesystem:list", engine=engine, now=now)
    return _result(output, True, progress)


def _read_file(definition, state, *, program, resource_id, engine, now):
    target = _resolve_path(state, resource_id)
    if _is_denied(target):
        return None, _path_error(definition, state, program=program, path=resource_id, reason="Permission denied", engine=engine, now=now)
    entry = _entry(state, target)
    if entry is None:
        return None, _path_error(definition, state, program=program, path=resource_id, reason="No such file or directory", engine=engine, now=now)
    if entry.kind != "file":
        return None, _path_error(definition, state, program=program, path=resource_id, reason="Is a directory", engine=engine, now=now)
    return entry, None


def shell_cat(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    entry, error = _read_file(definition, state, program="cat", resource_id=resource_id, engine=engine, now=now)
    if error:
        return error
    progress = _account(definition, state, fact_id="filesystem:read", engine=engine, now=now)
    return _result(entry.content.rstrip(), True, progress)


def _head_tail(definition, state, *, resource_id, arguments, engine, now, tail):
    program = "tail" if tail else "head"
    entry, error = _read_file(definition, state, program=program, resource_id=resource_id, engine=engine, now=now)
    if error:
        return error
    count = int(arguments[0]) if arguments else 10
    lines = entry.content.splitlines()
    selected = lines[-count:] if tail else lines[:count]
    progress = _account(definition, state, fact_id=f"filesystem:{program}", engine=engine, now=now)
    return _result("\n".join(selected), True, progress)


def shell_head(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    return _head_tail(definition, state, resource_id=resource_id, arguments=arguments, engine=engine, now=now, tail=False)


def shell_tail(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    return _head_tail(definition, state, resource_id=resource_id, arguments=arguments, engine=engine, now=now, tail=True)


def shell_grep(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    pattern = arguments[0]
    entry, error = _read_file(definition, state, program="grep", resource_id=resource_id, engine=engine, now=now)
    if error:
        return error
    matches = [line for line in entry.content.splitlines() if pattern.lower() in line.lower()]
    progress = _account(definition, state, fact_id="filesystem:grep", engine=engine, now=now)
    return _result("\n".join(matches) or "grep: no matches", bool(matches), progress)


def shell_path_stat(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    entry = _entry(state, target)
    if entry is None or _is_denied(target):
        reason = "Permission denied" if _is_denied(target) else "No such file or directory"
        return _path_error(definition, state, program="stat", path=resource_id, reason=reason, engine=engine, now=now)
    size = 4096 if entry.kind == "directory" else len(entry.content.encode("utf-8"))
    output = f"  File: {target}\n  Size: {size}\tType: {entry.kind}\nAccess: ({entry.mode}/{_mode_string(entry)})  Uid: {entry.owner}  Gid: {entry.group}"
    progress = _account(definition, state, fact_id="filesystem:path-stat", engine=engine, now=now)
    return _result(output, True, progress)


def _static(definition, state, *, output, fact_id, engine, now):
    progress = _account(definition, state, fact_id=fact_id, engine=engine, now=now)
    return _result(output, True, progress)


def shell_hostname(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    return _static(definition, state, output=state.virtual_rocky.hostname, fact_id="system:hostname", engine=engine, now=now)


def shell_uname(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    output = "Linux" if "-a" not in arguments else f"Linux {state.virtual_rocky.hostname} 5.14.0-570.el9.x86_64 #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux"
    return _static(definition, state, output=output, fact_id="system:uname", engine=engine, now=now)


def shell_uptime(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    return _static(definition, state, output=" 21:37:12 up 14 days,  6:22,  1 user,  load average: 0.18, 0.21, 0.17", fact_id="system:uptime", engine=engine, now=now)


def shell_whoami(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    return _static(definition, state, output=state.virtual_rocky.user, fact_id="system:whoami", engine=engine, now=now)


def shell_id(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    return _static(definition, state, output="uid=1000(operator) gid=1000(operator) groups=1000(operator),10(wheel)", fact_id="system:id", engine=engine, now=now)


def shell_free(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    output = "               total        used        free      shared  buff/cache   available\nMem:           7.6Gi       2.1Gi       3.8Gi       112Mi       1.7Gi       5.2Gi\nSwap:          2.0Gi          0B       2.0Gi"
    return _static(definition, state, output=output, fact_id="resources:memory", engine=engine, now=now)


def shell_df(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    output = "Filesystem      Size  Used Avail Use% Mounted on\n/dev/mapper/rl-root   40G   13G   28G  32% /\n/dev/vda1       960M  312M  649M  33% /boot"
    return _static(definition, state, output=output, fact_id="resources:disk", engine=engine, now=now)


def shell_ip_addr(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    output = "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 state UNKNOWN\n    inet 127.0.0.1/8 scope host lo\n2: ens192: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 state UP\n    inet 10.24.8.17/24 brd 10.24.8.255 scope global ens192"
    return _static(definition, state, output=output, fact_id="network:addr", engine=engine, now=now)


def shell_ip_route(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    output = "default via 10.24.8.1 dev ens192 proto static metric 100\n10.24.8.0/24 dev ens192 proto kernel scope link src 10.24.8.17 metric 100"
    return _static(definition, state, output=output, fact_id="network:route", engine=engine, now=now)


def shell_ss(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    services = [resource for resource in state.world_state.resources.values() if resource.resource_type is ResourceType.SERVICE and resource.current_state == "running"]
    lines = ["State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process"]
    if services:
        lines.append('LISTEN 0      4096       0.0.0.0:8080      0.0.0.0:*    users:(("app",pid=1421,fd=7))')
    lines.append('LISTEN 0      128        0.0.0.0:22        0.0.0.0:*    users:(("sshd",pid=812,fd=3))')
    return _static(definition, state, output="\n".join(lines), fact_id="network:listeners", engine=engine, now=now)


def shell_journal(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    service = _get_systemd_service(definition, state, resource_id=resource_id, capability_id="journal.read")
    attrs = service.attributes
    name = str(attrs.get("service_name", resource_id))
    configured = attrs.get("configured_exec_start")
    expected = attrs.get("expected_exec_start")
    if configured != expected:
        detail = f"Failed at step EXEC spawning /opt/{name.removesuffix('.service')}/{configured}: No such file or directory"
    elif isinstance(attrs.get("required_environment_variable"), str) and attrs.get(f"environment.{attrs['required_environment_variable']}") != attrs.get("expected_environment_value"):
        detail = f"Required environment variable {attrs['required_environment_variable']} is not set"
    else:
        executable = state.world_state.resources.get(str(attrs.get("executable_resource_id", "")))
        detail = "Permission denied" if executable and executable.attributes.get("current_mode") != executable.attributes.get("expected_mode") else "Main process exited, code=exited, status=1/FAILURE"
    output = f"Aug 28 21:36:18 {state.virtual_rocky.hostname} systemd[1]: Starting {name}...\nAug 28 21:36:18 {state.virtual_rocky.hostname} {name}[1421]: {detail}\nAug 28 21:36:18 {state.virtual_rocky.hostname} systemd[1]: {name}: Failed with result 'exit-code'."
    progress = _account(definition, state, fact_id=f"journal:{service.resource_id}", engine=engine, now=now)
    return _result(output, True, progress)


def shell_journal_xe(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    output = f"Aug 28 21:36:18 {state.virtual_rocky.hostname} systemd[1]: A start job for a unit has failed.\n░░ Subject: A start job for unit failed\n░░ Support: https://access.redhat.com/support"
    return _static(definition, state, output=output, fact_id="journal:xe", engine=engine, now=now)


def shell_systemd_start(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    service = _get_systemd_service(definition, state, resource_id=resource_id, capability_id="systemd.start")
    if not _restart_prerequisites_met(state, service):
        progress = _account(definition, state, fact_id=f"systemd:start-failed:{service.resource_id}", engine=engine, now=now)
        return _result(f"Job for {service.attributes.get('service_name', resource_id)} failed. See 'systemctl status' and 'journalctl -xeu' for details.", False, progress)
    progress = _engine(engine).execute_command(definition, state, ResourceStateUpdate(resource_id=service.resource_id, new_state="running"), command_cost=definition.scoring.command_cost, now=now)
    return _result("", True, progress)


def shell_systemd_stop(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    service = _get_systemd_service(definition, state, resource_id=resource_id, capability_id="systemd.stop")
    progress = _engine(engine).execute_command(definition, state, ResourceStateUpdate(resource_id=service.resource_id, new_state="stopped"), command_cost=definition.scoring.command_cost, now=now)
    return _result("", True, progress)
