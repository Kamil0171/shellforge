import re
from functools import partial

from app.admin_duty.rocky.common import _resolve_path
from app.admin_duty.rocky.system import finish


def selinux(
    definition, state, *, resource_id, arguments=(), engine=None, now=None, action
):
    security = state.virtual_rocky.selinux
    if action == "getenforce":
        output = security.mode
    elif action == "sestatus":
        output = f"SELinux status: {'disabled' if security.mode == 'Disabled' else 'enabled'}\nCurrent mode: {security.mode.lower()}\nLoaded policy name: targeted"
    elif action == "setenforce":
        if security.mode == "Disabled":
            return finish(
                definition,
                state,
                "SELinux jest wyłączony.",
                False,
                engine=engine,
                now=now,
            )
        security.mode = (
            "Enforcing" if resource_id.lower() in {"1", "enforcing"} else "Permissive"
        )
        output = ""
    elif action == "restorecon":
        path = _resolve_path(state, resource_id)
        if path not in state.virtual_rocky.filesystem:
            return finish(
                definition,
                state,
                f"restorecon: {path}: brak pliku.",
                False,
                engine=engine,
                now=now,
            )
        selected = [
            key
            for key in security.expected_file_contexts
            if key == path
            or ("-R" in arguments and key.startswith(path.rstrip("/") + "/"))
        ]
        for key in selected:
            security.file_contexts[key] = security.expected_file_contexts[key]
        output = (
            "\n".join(
                f"Relabeled {key} to {security.file_contexts[key]}" for key in selected
            )
            or "Brak zmian kontekstu."
        )
    else:
        output = "Konteksty plików (dokładne ścieżki):\n" + "\n".join(
            f"{path} {context}"
            for path, context in security.expected_file_contexts.items()
        )
    return finish(
        definition,
        state,
        output,
        engine=engine,
        now=now,
        fact_id=f"selinux-inspected:{state.active_host_id}",
    )


def firewall(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    fw = state.virtual_rocky.firewall
    permanent = "--permanent" in arguments
    services = fw.permanent_services if permanent else fw.runtime_services
    ports = fw.permanent_ports if permanent else fw.runtime_ports
    option = next(value for value in arguments if value != "--permanent")
    output = "success"
    if option == "--state":
        output = "running" if fw.running else "not running"
    elif option == "--reload":
        fw.runtime_services = set(fw.permanent_services)
        fw.runtime_ports = set(fw.permanent_ports)
    elif option == "--get-active-zones":
        output = f"{fw.active_zone}\n  interfaces: " + " ".join(
            state.virtual_rocky.network.interfaces
        )
    elif option == "--list-services":
        output = " ".join(sorted(services))
    elif option == "--list-ports":
        output = " ".join(sorted(ports))
    elif option == "--list-all":
        output = f"{fw.active_zone} (active)\n  target: default\n  services: {' '.join(sorted(services))}\n  ports: {' '.join(sorted(ports))}"
    else:
        operation, _, value = option.partition("=")
        if operation.endswith("service"):
            if value not in {"ssh", "http", "https", "dns", "dhcpv6-client"}:
                return finish(
                    definition,
                    state,
                    f"INVALID_SERVICE: {value}",
                    False,
                    engine=engine,
                    now=now,
                )
            selected = services
        else:
            if (
                not re.fullmatch(r"[0-9]{1,5}/(tcp|udp)", value)
                or not 1 <= int(value.split("/")[0]) <= 65535
            ):
                return finish(
                    definition,
                    state,
                    f"INVALID_PORT: {value}",
                    False,
                    engine=engine,
                    now=now,
                )
            selected = ports
        if operation.startswith("--add-"):
            selected.add(value)
        else:
            selected.discard(value)
    return finish(
        definition,
        state,
        output,
        engine=engine,
        now=now,
        fact_id=f"firewall-inspected:{state.active_host_id}",
    )


HANDLERS = {
    f"selinux.{action}": partial(selinux, action=action)
    for action in ("getenforce", "sestatus", "setenforce", "restorecon", "semanage")
}
HANDLERS["firewalld.command"] = firewall
