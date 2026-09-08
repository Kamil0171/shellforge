from functools import partial
from ipaddress import ip_address
from urllib.parse import urlsplit

from app.admin_duty.domain.definition import ResourceType
from app.admin_duty.rocky.system import finish


def network(
    definition, state, *, resource_id, arguments=(), engine=None, now=None, action
):
    rocky = state.virtual_rocky
    interfaces = list(rocky.network.interfaces.values())
    connected = any(item.state == "up" for item in interfaces)
    success = True
    if action in {"addr", "link"}:
        lines = ["1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 state UNKNOWN"]
        if action == "addr":
            lines.append("    inet 127.0.0.1/8 scope host lo")
        for index, item in enumerate(interfaces, 2):
            lines.append(
                f"{index}: {item.name}: <BROADCAST,MULTICAST{',UP,LOWER_UP' if item.state == 'up' else ''}> mtu 1500 state {item.state.upper()}"
            )
            if action == "addr":
                lines.append(f"    inet {item.address} scope global {item.name}")
        output = "\n".join(lines)
    elif action == "route":
        output = "\n".join(rocky.network.routes) if connected else ""
    elif action == "listeners":
        lines = [
            "State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process",
            'LISTEN 0 128 0.0.0.0:22 0.0.0.0:* users:(("sshd",pid=812,fd=3))',
        ]
        for process in rocky.processes.values():
            if process.service_resource_id:
                service = state.world_state.resources[process.service_resource_id]
                if service.current_state == "running":
                    lines.append(
                        f'LISTEN 0 4096 0.0.0.0:{service.attributes.get("port", 8080)} 0.0.0.0:* users:(("app",pid={process.pid},fd=7))'
                    )
        output = "\n".join(lines)
    else:
        try:
            host = (
                urlsplit(
                    resource_id if "://" in resource_id else "//" + resource_id
                ).hostname
                if action == "curl"
                else resource_id
            )
        except ValueError:
            return finish(
                definition,
                state,
                "curl: nieprawidłowy adres URL.",
                False,
                engine=engine,
                now=now,
            )
        if not host:
            return finish(
                definition, state, "Brak nazwy hosta.", False, engine=engine, now=now
            )
        local = host in {"localhost", "127.0.0.1"}
        address = "127.0.0.1" if local else rocky.network.dns_records.get(host)
        try:
            address = str(ip_address(host))
        except ValueError:
            pass
        if not address or (not connected and not local):
            output, success = (
                f"{action}: {host}: brak trasy lub wpisu DNS w wirtualnej sieci.",
                False,
            )
        elif action in {"dig", "getent"}:
            output = (
                f";; ANSWER SECTION:\n{host}. 300 IN A {address}"
                if action == "dig"
                else f"{address} {host}"
            )
        elif action == "ping":
            output = f"PING {host} ({address}) 56(84) bytes of data.\n64 bytes from {address}: icmp_seq=1 ttl=64 time=0.120 ms\n--- {host} ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss"
        else:
            parsed = urlsplit(
                resource_id if "://" in resource_id else "http://" + resource_id
            )
            if parsed.scheme not in {"http", "https"}:
                return finish(
                    definition,
                    state,
                    "curl: obsługiwane są wyłącznie HTTP i HTTPS.",
                    False,
                    engine=engine,
                    now=now,
                )
            try:
                port = parsed.port or (443 if parsed.scheme == "https" else 80)
            except ValueError:
                return finish(
                    definition,
                    state,
                    "curl: nieprawidłowy port.",
                    False,
                    engine=engine,
                    now=now,
                )
            service = next(
                (
                    item
                    for item in state.world_state.resources.values()
                    if item.resource_type is ResourceType.SERVICE
                    and item.current_state == "running"
                    and item.attributes.get("port", 8080) == port
                ),
                None,
            )
            allowed = (
                local
                or not rocky.firewall.running
                or f"{port}/tcp" in rocky.firewall.runtime_ports
                or (port == 80 and "http" in rocky.firewall.runtime_services)
                or (port == 443 and "https" in rocky.firewall.runtime_services)
            )
            own_address = local or address in {
                item.address.split("/")[0] for item in interfaces
            }
            if service and allowed and own_address:
                output = (
                    'HTTP/1.1 200 OK\nContent-Type: application/json\n\n{"status":"ok"}'
                )
            else:
                output, success = (
                    f"curl: (7) Failed to connect to {host} port {port}",
                    False,
                )
    return finish(definition, state, output, success, engine=engine, now=now)


def nmcli(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    network_state = state.virtual_rocky.network
    if arguments[:2] == ("device", "status"):
        output = "DEVICE  TYPE      STATE          CONNECTION\n" + "\n".join(
            f"{item.name} ethernet {'connected' if item.state == 'up' else 'disconnected'} {item.connection}"
            for item in network_state.interfaces.values()
        )
    elif arguments[:2] == ("connection", "show"):
        output = "NAME              TYPE      DEVICE\n" + "\n".join(
            f"{item.connection} ethernet {item.name}"
            for item in network_state.interfaces.values()
        )
    else:
        name = arguments[2]
        if name not in network_state.connections:
            return finish(
                definition,
                state,
                f"nmcli: nieznane połączenie {name}.",
                False,
                engine=engine,
                now=now,
            )
        up = arguments[1] == "up"
        network_state.connections[name] = up
        for interface in network_state.interfaces.values():
            if interface.connection == name:
                interface.state = "up" if up else "down"
        output = (
            f"Connection {name} successfully {'activated' if up else 'deactivated'}."
        )
    return finish(definition, state, output, engine=engine, now=now)


HANDLERS = {
    f"network.{action}": partial(network, action=action)
    for action in (
        "addr",
        "link",
        "route",
        "listeners",
        "ping",
        "curl",
        "dig",
        "getent",
    )
}
HANDLERS["networkmanager.command"] = nmcli
