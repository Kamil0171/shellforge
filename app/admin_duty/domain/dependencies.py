from app.admin_duty.domain.definition import (
    ConfigurationRequirement,
    IncidentDefinition,
    NetworkProtocol,
    PackageRequirement,
    ResourceType,
    ServiceDependency,
)
from app.admin_duty.domain.runtime import RuntimeResource, SessionRuntimeState


def _firewall_allows(state: SessionRuntimeState, host_id: str, port: int, protocol: str) -> bool:
    runtime = state.host_runtimes[host_id]
    firewall = runtime.firewall
    if not firewall.running:
        return True
    if f"{port}/{protocol}" in firewall.runtime_ports:
        return True
    return (port == 80 and "http" in firewall.runtime_services) or (
        port == 443 and "https" in firewall.runtime_services
    ) or (
        port == 53 and "dns" in firewall.runtime_services
    )


def _network_is_up(state: SessionRuntimeState, host_id: str) -> bool:
    runtime = state.host_runtimes[host_id]
    return any(
        interface.state == "up"
        and runtime.network.connections.get(interface.connection, False)
        for interface in runtime.network.interfaces.values()
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
    return not isinstance(expected, str) or entry.content == expected


def _dependency_is_healthy(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    dependency: ServiceDependency,
    service_health: dict[str, bool],
) -> bool:
    target = state.world_state.resources[dependency.target_service_id]
    source = state.world_state.resources[dependency.source_service_id]
    if not service_health.get(target.resource_id, target.current_state == "running"):
        return False
    if target.parent_resource_id != dependency.target_host_id:
        return False
    if target.attributes.get("port") != dependency.port:
        return False
    if not _network_is_up(state, dependency.source_host_id):
        return False
    if not _network_is_up(state, dependency.target_host_id):
        return False
    required_dns_name = source.attributes.get("required_dns_name")
    if isinstance(required_dns_name, str):
        source_runtime = state.host_runtimes[source.parent_resource_id]
        dns_ready = any(
            source_runtime.network.connection_dns_servers.get(name, ())
            for name, active in source_runtime.network.connections.items()
            if active
        )
        if not dns_ready or required_dns_name not in source_runtime.network.dns_records:
            return False
    protocol = (
        "udp" if dependency.protocol is NetworkProtocol.UDP else "tcp"
    )
    return _firewall_allows(
        state,
        dependency.target_host_id,
        dependency.port,
        protocol,
    )


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
        for service_id in tuple(pending):
            service = services[service_id]
            dependencies = outgoing.get(service_id, [])
            unresolved = any(
                dependency.target_service_id in pending
                and dependency.target_service_id != service_id
                for dependency in dependencies
            )
            if unresolved:
                continue
            healthy = service.current_state == "running"
            healthy = healthy and all(
                _package_is_available(state, requirement)
                for requirement in package_requirements.get(service_id, [])
            )
            healthy = healthy and all(
                _configuration_is_valid(definition, state, requirement)
                for requirement in configuration_requirements.get(service_id, [])
            )
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
        affected.current_state = rule.healthy_state if healthy else rule.unhealthy_state
