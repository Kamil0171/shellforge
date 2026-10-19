from ipaddress import ip_address
from urllib.parse import urlsplit

from app.admin_duty.domain.definition import (
    ConfigurationRequirement,
    IncidentDefinition,
    NetworkProtocol,
    PackageRequirement,
    ResourceType,
    ServiceDependency,
)
from app.admin_duty.domain.runtime import RuntimeResource, SessionRuntimeState


def _firewall_allows(
    state: SessionRuntimeState, host_id: str, port: int, protocol: str
) -> bool:
    runtime = state.host_runtimes[host_id]
    firewall = runtime.firewall
    if not firewall.running:
        return True
    if f"{port}/{protocol}" in firewall.runtime_ports:
        return True
    return (
        (port == 22 and "ssh" in firewall.runtime_services)
        or (port == 80 and "http" in firewall.runtime_services)
        or (port == 443 and "https" in firewall.runtime_services)
        or (port == 53 and "dns" in firewall.runtime_services)
    )


def _network_is_up(state: SessionRuntimeState, host_id: str) -> bool:
    runtime = state.host_runtimes[host_id]
    return any(
        interface.state == "up"
        and runtime.network.connections.get(interface.connection, False)
        for interface in runtime.network.interfaces.values()
    )


def resolve_address(state: SessionRuntimeState, source_host_id: str, host: str):
    if host in {"localhost", "127.0.0.1", "::1"}:
        return "127.0.0.1", source_host_id, True
    runtime = state.host_runtimes[source_host_id]
    try:
        address = str(ip_address(host))
    except ValueError:
        dns_ready = _dns_is_ready(state, source_host_id)
        address = runtime.network.dns_records.get(host) if dns_ready else None
    target_host_id = next(
        (
            host_id
            for host_id, target in state.host_runtimes.items()
            if any(
                interface.address.split("/")[0] == address
                for interface in target.network.interfaces.values()
            )
        ),
        None,
    )
    return address, target_host_id, False


def _dns_is_ready(state, source_host_id):
    network = state.host_runtimes[source_host_id].network
    for name, active in network.connections.items():
        if not active:
            continue
        expected = set(network.expected_dns_servers.get(name, ()))
        for server in network.connection_dns_servers.get(name, ()):
            if server not in expected:
                continue
            target_host_id = next(
                (
                    host_id
                    for host_id, runtime in state.host_runtimes.items()
                    if any(
                        interface.address.split("/")[0] == server
                        for interface in runtime.network.interfaces.values()
                    )
                ),
                None,
            )
            if target_host_id is None or transport_service(
                state, source_host_id, target_host_id, 53, "udp"
            ):
                return True
    return False


def host_reachable(state, source_host_id, target_host_id, *, local=False, address=None):
    if target_host_id is None:
        return (
            address is not None
            and address
            == state.host_runtimes[source_host_id].network.dns_records.get(
                "probe.internal"
            )
            and _network_is_up(state, source_host_id)
        )
    return target_host_id in state.host_runtimes and (
        local
        or _network_is_up(state, source_host_id)
        and _network_is_up(state, target_host_id)
    )


def transport_service(
    state, source_host_id, target_host_id, port, protocol="tcp", *, local=False
):
    if not host_reachable(state, source_host_id, target_host_id, local=local):
        return None
    if not local and not _firewall_allows(state, target_host_id, port, protocol):
        return None
    return next(
        (
            resource
            for resource in state.world_state.resources.values()
            if resource.resource_type is ResourceType.SERVICE
            and resource.parent_resource_id == target_host_id
            and resource.current_state == "running"
            and resource.attributes.get("port", 8080) == port
        ),
        None,
    )


def tcp_available(state, source_host_id, target_host_id, port, *, local=False):
    if transport_service(state, source_host_id, target_host_id, port, local=local):
        return True
    return (
        port == 22
        and host_reachable(state, source_host_id, target_host_id, local=local)
        and (local or _firewall_allows(state, target_host_id, port, "tcp"))
        and any(
            process.command.startswith("sshd:")
            for process in state.host_runtimes[target_host_id].processes.values()
        )
    )


def dependency_port(state, dependency):
    if dependency.port_configuration_file_id is None:
        return dependency.port
    resource = state.world_state.resources[dependency.port_configuration_file_id]
    entry = state.host_runtimes[dependency.source_host_id].filesystem.get(
        resource.attributes.get("path")
    )
    if entry is None:
        return None
    values = [
        line.partition("=")[2].strip()
        for line in entry.content.splitlines()
        if line.partition("=")[0].strip() == "UPSTREAM_PORT"
    ]
    if len(values) != 1 or not values[0].isascii() or not values[0].isdigit():
        return None
    port = int(values[0])
    return port if 1 <= port <= 65535 else None


def dependency_transport_is_healthy(state, dependency):
    source = state.world_state.resources[dependency.source_service_id]
    required_dns_name = source.attributes.get("required_dns_name")
    if isinstance(required_dns_name, str):
        address, target_host_id, _ = resolve_address(
            state, dependency.source_host_id, required_dns_name
        )
        if not address or (
            dependency.protocol is not NetworkProtocol.UDP
            and target_host_id != dependency.target_host_id
        ):
            return False
    protocol = "udp" if dependency.protocol is NetworkProtocol.UDP else "tcp"
    target = transport_service(
        state,
        dependency.source_host_id,
        dependency.target_host_id,
        dependency_port(state, dependency),
        protocol,
    )
    return target is not None and target.resource_id == dependency.target_service_id


def flow_verification_fact(flow):
    return (
        f"endpoint-verified:{flow.entry_endpoint_id}:{flow.verification_source_host_id}"
    )


def flow_entry_transport(definition, state):
    flow = definition.multi_host_flow
    endpoint = state.world_state.resources[flow.entry_endpoint_id]
    parsed = urlsplit(str(endpoint.attributes.get("url", "")))
    address, host_id, local = resolve_address(
        state, flow.verification_source_host_id, parsed.hostname or ""
    )
    if not address or local:
        return None
    service = transport_service(
        state,
        flow.verification_source_host_id,
        host_id,
        parsed.port or (443 if parsed.scheme == "https" else 80),
    )
    return service if service and service.resource_id == flow.service_path[0] else None


def flow_is_healthy(definition, state):
    flow = definition.multi_host_flow
    return flow_entry_transport(definition, state) is not None and all(
        state.world_state.resources[service_id].attributes.get("public_health")
        == "healthy"
        for service_id in flow.service_path
    )


def qualifies_flow_verification(definition, state, url, target_host_id, port, local):
    flow = definition.multi_host_flow
    if not flow or local or state.active_host_id != flow.verification_source_host_id:
        return False
    endpoint = state.world_state.resources[flow.entry_endpoint_id]
    expected = urlsplit(str(endpoint.attributes.get("url", "")))
    actual = urlsplit(url if "://" in url else "http://" + url)
    entry = state.world_state.resources[flow.service_path[0]]
    return (
        target_host_id == entry.parent_resource_id
        and port == entry.attributes.get("port")
        and actual.scheme == expected.scheme
        and (actual.path or "/") == (expected.path or "/")
        and actual.query == expected.query
        and not actual.username
        and not actual.password
        and flow_is_healthy(definition, state)
    )


def _package_is_available(
    state: SessionRuntimeState,
    requirement: PackageRequirement,
) -> bool:
    return (
        requirement.package_name
        in state.host_runtimes[requirement.host_id].packages.installed_packages
    )


def _configuration_is_valid(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    requirement: ConfigurationRequirement,
) -> bool:
    resource = state.world_state.resources[requirement.file_resource_id]
    attributes = resource.attributes
    path = attributes.get("path")
    if not isinstance(path, str):
        return False
    entry = state.host_runtimes[requirement.host_id].filesystem.get(path)
    if entry is None or entry.kind != "file":
        return False
    expected = attributes.get("expected_content")
    content_valid = not isinstance(expected, str) or entry.content == expected
    mode_valid = (
        requirement.expected_mode is None or entry.mode == requirement.expected_mode
    )
    owner_valid = (
        requirement.expected_owner is None or entry.owner == requirement.expected_owner
    )
    return content_valid and mode_valid and owner_valid


def _dependency_is_healthy(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    dependency: ServiceDependency,
    service_health: dict[str, bool],
) -> bool:
    target = state.world_state.resources[dependency.target_service_id]
    if not service_health.get(target.resource_id, target.current_state == "running"):
        return False
    return dependency_transport_is_healthy(state, dependency)


def reconcile_dependencies(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> None:
    if not (
        definition.service_dependencies
        or definition.package_requirements
        or definition.configuration_requirements
        or definition.symptom_propagation
    ):
        return
    for resource in state.world_state.resources.values():
        if resource.resource_type is not ResourceType.HOST:
            continue
        runtime = state.host_runtimes[resource.resource_id]
        expected_dns = {
            server
            for servers in runtime.network.expected_dns_servers.values()
            for server in servers
        }
        active_dns = {
            server
            for name, servers in runtime.network.connection_dns_servers.items()
            if runtime.network.connections.get(name, False)
            for server in servers
        }
        expected_services = set(
            resource.attributes.get("expected_firewall_services", ())
        )
        expected_ports = set(resource.attributes.get("expected_firewall_ports", ()))
        attributes = resource.attributes.copy()
        attributes["network_health"] = (
            "healthy" if _network_is_up(state, resource.resource_id) else "unhealthy"
        )
        attributes["dns_health"] = (
            "healthy" if expected_dns <= active_dns else "unhealthy"
        )
        attributes["firewall_health"] = (
            "healthy"
            if (
                not runtime.firewall.running
                or expected_services <= runtime.firewall.runtime_services
                and expected_ports <= runtime.firewall.runtime_ports
            )
            else "unhealthy"
        )
        resource.attributes = attributes
    services = {
        resource.resource_id: resource
        for resource in state.world_state.resources.values()
        if resource.resource_type is ResourceType.SERVICE
    }
    outgoing: dict[str, list[ServiceDependency]] = {}
    for dependency in definition.service_dependencies:
        outgoing.setdefault(dependency.source_service_id, []).append(dependency)

    package_requirements: dict[str, list[PackageRequirement]] = {}
    for requirement in definition.package_requirements:
        package_requirements.setdefault(requirement.service_id, []).append(requirement)
    configuration_requirements: dict[str, list[ConfigurationRequirement]] = {}
    for requirement in definition.configuration_requirements:
        configuration_requirements.setdefault(requirement.service_id, []).append(
            requirement
        )

    service_health: dict[str, bool] = {}
    pending = set(services)
    for _ in range(len(services) + 1):
        changed = False
        for service_id in sorted(pending):
            service = services[service_id]
            dependencies = outgoing.get(service_id, [])
            unresolved = any(
                dependency.target_service_id in pending
                and dependency.target_service_id != service_id
                for dependency in dependencies
            )
            if unresolved:
                continue
            package_healthy = all(
                _package_is_available(state, requirement)
                for requirement in package_requirements.get(service_id, [])
            )
            configuration_healthy = all(
                _configuration_is_valid(definition, state, requirement)
                for requirement in configuration_requirements.get(service_id, [])
            )
            attributes = service.attributes.copy()
            attributes["package_health"] = "healthy" if package_healthy else "unhealthy"
            attributes["configuration_health"] = (
                "healthy" if configuration_healthy else "unhealthy"
            )
            local_healthy = (
                service.current_state == "running"
                and package_healthy
                and configuration_healthy
            )
            attributes["local_health"] = "healthy" if local_healthy else "unhealthy"
            attributes["transport_health"] = (
                "healthy"
                if all(
                    dependency_transport_is_healthy(state, dependency)
                    for dependency in dependencies
                    if dependency.required
                )
                else "unhealthy"
            )
            attributes["downstream_health"] = (
                "healthy"
                if all(
                    service_health.get(dependency.target_service_id, False)
                    for dependency in dependencies
                    if dependency.required
                )
                else "unhealthy"
            )
            service.attributes = attributes
            healthy = local_healthy
            healthy = healthy and all(
                _dependency_is_healthy(definition, state, dependency, service_health)
                for dependency in dependencies
                if dependency.required
            )
            service_health[service_id] = healthy
            pending.remove(service_id)
            changed = True
        if not pending or not changed:
            break

    for service_id in pending:
        service_health[service_id] = False

    for service_id, service in services.items():
        attributes = service.attributes.copy()
        attributes["public_health"] = (
            "healthy" if service_health[service_id] else "unhealthy"
        )
        service.attributes = attributes
        observation = (
            f"{service.current_state}:{attributes.get('local_health', 'unhealthy')}"
        )
        if attributes.get("observed_local_health") != observation:
            runtime = state.host_runtimes[service.parent_resource_id]
            name = attributes.get("service_name", service_id)
            runtime.journal_entries = [
                *runtime.journal_entries[-1999:],
                f"{state.last_activity.isoformat()} {runtime.hostname} {name}: "
                f"stan procesu {service.current_state}; usługa lokalna "
                f"{'zdrowa' if attributes.get('local_health') == 'healthy' else 'zdegradowana'}.",
            ]
            service.attributes = {**attributes, "observed_local_health": observation}

    for dependency in sorted(
        definition.service_dependencies, key=lambda item: item.dependency_id
    ):
        source = services[dependency.source_service_id]
        transport = dependency_transport_is_healthy(state, dependency)
        application = service_health[dependency.target_service_id]
        observation = f"{'dostępny' if transport else 'niedostępny'}; aplikacja {'zdrowa' if application else 'zdegradowana'}"
        key = f"dependency_status.{dependency.dependency_id}"
        if source.attributes.get(key) != observation:
            runtime = state.host_runtimes[dependency.source_host_id]
            target_name = state.host_runtimes[dependency.target_host_id].hostname
            name = source.attributes.get("service_name", source.resource_id)
            runtime.journal_entries = [
                *runtime.journal_entries[-1999:],
                f"{state.last_activity.isoformat()} {runtime.hostname} {name}: "
                f"{target_name}:{dependency_port(state, dependency) or '?'} transport {observation}.",
            ]
            source.attributes = {**source.attributes, key: observation}

    dependencies = {
        dependency.dependency_id: dependency
        for dependency in definition.service_dependencies
    }
    for rule in definition.symptom_propagation:
        dependency = dependencies[rule.dependency_id]
        healthy = _dependency_is_healthy(
            definition,
            state,
            dependency,
            service_health,
        )
        affected: RuntimeResource = state.world_state.resources[
            rule.affected_resource_id
        ]
        if rule.health_layer == "transport":
            healthy = dependency_transport_is_healthy(state, dependency)
        healthy = healthy and all(
            service_health[resource_id]
            for resource_id in affected.dependencies
            if resource_id in services
        )
        affected.current_state = rule.healthy_state if healthy else rule.unhealthy_state
    if definition.multi_host_flow:
        flow = definition.multi_host_flow
        endpoint = state.world_state.resources[flow.entry_endpoint_id]
        endpoint.current_state = (
            "healthy"
            if flow_is_healthy(definition, state)
            else "http-502"
            if flow_entry_transport(definition, state)
            else "unreachable"
        )
        if endpoint.current_state != "healthy":
            state.discovered_fact_ids.discard(flow_verification_fact(flow))
    for endpoint in state.world_state.resources.values():
        if endpoint.resource_type is not ResourceType.ENDPOINT:
            continue
        if endpoint.current_state != "healthy":
            for service_id in endpoint.dependencies:
                if service_id in services:
                    service = services[service_id]
                    state.discovered_fact_ids.discard(
                        f"endpoint-healthy:{service.parent_resource_id}:{service.attributes.get('port', 8080)}"
                    )
