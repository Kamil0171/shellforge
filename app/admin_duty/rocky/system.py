import posixpath
import shlex
from datetime import datetime, timedelta
from functools import partial

from app.admin_duty.domain.definition import ResourceType
from app.admin_duty.domain.runtime import VirtualProcess
from app.admin_duty.dynamic_commands import _get_systemd_service
from app.admin_duty.rocky.common import _account, _result


def finish(
    definition, state, output="", success=True, *, engine=None, now=None, fact_id=None
):
    return _result(
        output,
        success,
        _account(definition, state, fact_id=fact_id, engine=engine, now=now),
    )


def service_failure(state, service, *, synchronize=True):
    attrs = service.attributes
    name = str(attrs.get("service_name", f"{service.resource_id}.service"))
    content = state.virtual_rocky.systemd_unit_cache.get(name, "")
    executable = ""
    environment = {}
    section = ""
    for raw in content.splitlines():
        line = raw.strip()
        if line.startswith("["):
            section = line
        if section != "[Service]" or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key == "ExecStart":
            try:
                executable = shlex.split(value)[0] if value.strip() else ""
            except ValueError:
                return "Nieprawidłowe cytowanie ExecStart."
        if key == "Environment":
            try:
                for pair in shlex.split(value):
                    variable, separator, setting = pair.partition("=")
                    if separator:
                        environment[variable] = setting
            except ValueError:
                return "Nieprawidłowe cytowanie Environment."
    entry = state.virtual_rocky.filesystem.get(executable)
    if not entry or entry.kind != "file":
        return f"Failed at step EXEC spawning {executable or '(brak ExecStart)'}: No such file or directory"
    if not int(entry.mode, 8) & 0o111:
        return f"Failed at step EXEC spawning {executable}: Permission denied"
    if entry.owner not in {"app", "root"}:
        return f"{executable}: nieprawidłowy właściciel pliku usługi."
    variable = attrs.get("required_environment_variable")
    if variable and environment.get(variable) != attrs.get(
        "expected_environment_value"
    ):
        return f"Required environment variable {variable} is not set or invalid"
    required_package = attrs.get("required_package")
    if (
        required_package
        and required_package not in state.virtual_rocky.packages.installed_packages
    ):
        return f"Brak wymaganego pakietu: {required_package}"
    if state.virtual_rocky.selinux.mode == "Enforcing":
        for (
            path,
            expected,
        ) in state.virtual_rocky.selinux.expected_file_contexts.items():
            if executable == path or executable.startswith(path + "/"):
                if state.virtual_rocky.selinux.file_contexts.get(path) != expected:
                    return f"SELinux: AVC denied execute {executable}"
    if synchronize:
        attrs["configured_exec_start"] = posixpath.basename(executable)
        for key in tuple(attrs):
            if key.startswith("environment."):
                attrs.pop(key)
        attrs.update(
            {f"environment.{key}": value for key, value in environment.items()}
        )
    return None


def systemctl(
    definition, state, *, resource_id, arguments=(), engine=None, now=None, action
):
    rocky = state.virtual_rocky
    if action == "daemon-reload":
        rocky.systemd_unit_cache = {
            posixpath.basename(path): entry.content
            for path, entry in rocky.filesystem.items()
            if path.startswith("/etc/systemd/system/")
            and path.endswith(".service")
            and entry.kind == "file"
        }
        rocky.daemon_reload_required = False
        return finish(
            definition,
            state,
            "Przeładowano definicje jednostek.",
            engine=engine,
            now=now,
        )
    if action == "list-units" or (action == "status" and resource_id == "."):
        lines = ["UNIT                         LOAD   ACTIVE   SUB"]
        lines.extend(
            f"{resource.attributes.get('service_name', resource.resource_id):28} loaded {('active running' if resource.current_state == 'running' else 'failed failed')}"
            for resource in state.world_state.resources.values()
            if resource.resource_type is ResourceType.SERVICE
            and resource.parent_resource_id == state.active_host_id
        )
        return finish(definition, state, "\n".join(lines), engine=engine, now=now)
    service = _get_systemd_service(
        definition, state, resource_id=resource_id, capability_id=f"systemd.{action}"
    )
    name = str(service.attributes.get("service_name", f"{service.resource_id}.service"))
    path = f"/etc/systemd/system/{name}"
    if action == "cat":
        entry = rocky.filesystem.get(path)
        return finish(
            definition,
            state,
            f"# {path}\n{entry.content}"
            if entry
            else f"Unit {name} could not be found.",
            bool(entry),
            engine=engine,
            now=now,
        )
    if action == "status":
        active = (
            "active (running)"
            if service.current_state == "running"
            else f"{service.current_state} (Result: exit-code)"
        )
        enabled = "enabled" if name in rocky.systemd_enabled_units else "disabled"
        output = f"● {name}\n   Loaded: loaded ({path}; {enabled})\n   Active: {active}"
        if rocky.daemon_reload_required:
            output += (
                "\nUwaga: plik jednostki zmienił się. Wykonaj systemctl daemon-reload."
            )
        return finish(
            definition,
            state,
            output,
            engine=engine,
            now=now,
            fact_id=f"service-status-inspected:{service.resource_id}",
        )
    if action in {"enable", "disable", "is-enabled"}:
        if action == "enable":
            rocky.systemd_enabled_units.add(name)
        if action == "disable":
            rocky.systemd_enabled_units.discard(name)
        enabled = name in rocky.systemd_enabled_units
        return finish(
            definition,
            state,
            "enabled" if enabled else "disabled",
            enabled if action == "is-enabled" else True,
            engine=engine,
            now=now,
        )
    if action == "is-active":
        active = service.current_state == "running"
        return finish(
            definition,
            state,
            "active" if active else "inactive",
            active,
            engine=engine,
            now=now,
        )
    failure = None if action == "stop" else service_failure(state, service)
    service.current_state = (
        "stopped" if action == "stop" else "failed" if failure else "running"
    )
    rocky.processes = {
        pid: process
        for pid, process in rocky.processes.items()
        if process.service_resource_id != service.resource_id
    }
    if service.current_state == "running":
        pid = 1421 + sum(
            1 for item in state.world_state.resources if item < service.resource_id
        )
        rocky.processes[pid] = VirtualProcess(
            pid=pid, user="app", command=name, service_resource_id=service.resource_id
        )
    stamp = (now or state.last_activity).isoformat()
    detail = failure or ("Stopped" if action == "stop" else "Started")
    rocky.journal_entries = [
        *rocky.journal_entries[-1999:],
        f"{stamp} {rocky.hostname} systemd[1]: {name}: {detail}",
    ]
    return finish(
        definition,
        state,
        f"Job for {name} failed. {failure}" if failure else "",
        not failure,
        engine=engine,
        now=now,
    )


def journal(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    unit = None
    if resource_id != ".":
        unit = _get_systemd_service(
            definition, state, resource_id=resource_id, capability_id="journal.read"
        )
    name = (
        str(unit.attributes.get("service_name", f"{unit.resource_id}.service"))
        if unit
        else None
    )
    lines = [
        line
        for line in state.virtual_rocky.journal_entries
        if name is None or name in line
    ]
    count = 30
    since = None
    for index, value in enumerate(arguments):
        if value == "-n":
            count = int(arguments[index + 1])
        if value == "--since":
            raw = arguments[index + 1]
            if raw in {"today", "yesterday"}:
                since = state.last_activity.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) - timedelta(days=raw == "yesterday")
            else:
                try:
                    since = datetime.fromisoformat(raw).replace(
                        tzinfo=state.last_activity.tzinfo
                    )
                except ValueError:
                    return finish(
                        definition,
                        state,
                        "journalctl: podaj datę ISO lub today/yesterday.",
                        False,
                        engine=engine,
                        now=now,
                    )
    if since:
        selected = []
        for line in lines:
            try:
                if datetime.fromisoformat(line.split(" ", 1)[0]) >= since:
                    selected.append(line)
            except ValueError:
                continue
        lines = selected
    return finish(
        definition,
        state,
        "\n".join(lines[-count:]) or "-- Brak wpisów --",
        engine=engine,
        now=now,
        fact_id=f"service-journal-inspected:{unit.resource_id}" if unit else None,
    )


def system(
    definition, state, *, resource_id, arguments=(), engine=None, now=None, action
):
    rocky = state.virtual_rocky
    memory = rocky.memory_total_kib
    used = rocky.memory_used_kib + len(rocky.processes) * 2048
    disk_used = (
        rocky.disk_used_kib
        + sum(len(entry.content.encode("utf-8")) for entry in rocky.filesystem.values())
        // 1024
    )
    simple = {
        "hostname": rocky.hostname,
        "hostnamectl": f" Static hostname: {rocky.hostname}\n Operating System: Rocky Linux 9.6 (Blue Onyx)\n Kernel: Linux 5.14.0-570.el9.x86_64\n Architecture: x86-64",
        "uname": f"Linux {rocky.hostname} 5.14.0-570.el9.x86_64 x86_64 GNU/Linux"
        if arguments
        else "Linux",
        "whoami": rocky.user,
        "id": f"uid=1000({rocky.user}) gid=1000({rocky.user}) groups=1000({rocky.user}),10(wheel)",
        "date": state.last_activity.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "uptime": f" {state.last_activity:%H:%M:%S} up {rocky.uptime_seconds // 86400} days, 1 user, load average: {len(rocky.processes) * 0.05:.2f}, 0.21, 0.17",
    }
    if action in simple:
        return finish(definition, state, simple[action], engine=engine, now=now)
    if action == "ps":
        lines = ["USER       PID  %CPU %MEM STAT COMMAND"]
        lines.extend(
            f"{p.user:8} {p.pid:5}   0.0  0.1 Ss   {p.command}"
            for p in rocky.processes.values()
        )
        return finish(definition, state, "\n".join(lines), engine=engine, now=now)
    if action == "free":
        fmt = (lambda value: f"{value / 1048576:.1f}Gi") if "-h" in arguments else str
        output = f"               total       used       free  available\nMem:      {fmt(memory):>10} {fmt(used):>10} {fmt(memory - used):>10} {fmt(memory - used):>10}\nSwap:     {fmt(2097152):>10} {fmt(0):>10} {fmt(2097152):>10}"
    else:
        fmt = (lambda value: f"{value / 1048576:.1f}G") if "-h" in arguments else str
        output = f"Filesystem       Size      Used     Avail Use% Mounted on\n/dev/mapper/rl-root {fmt(rocky.disk_total_kib)} {fmt(disk_used)} {fmt(rocky.disk_total_kib - disk_used)} {disk_used * 100 // rocky.disk_total_kib}% /"
    return finish(definition, state, output, engine=engine, now=now)


HANDLERS = {
    **{
        f"systemd.{action}": partial(systemctl, action=action)
        for action in (
            "status",
            "start",
            "stop",
            "restart",
            "cat",
            "enable",
            "disable",
            "is-active",
            "is-enabled",
            "list-units",
            "daemon-reload",
        )
    },
    **{
        f"system.{action}": partial(system, action=action)
        for action in (
            "hostname",
            "hostnamectl",
            "uname",
            "whoami",
            "id",
            "date",
            "uptime",
        )
    },
    "processes.list": partial(system, action="ps"),
    "resources.memory": partial(system, action="free"),
    "resources.disk": partial(system, action="df"),
    "journal.read": journal,
}
