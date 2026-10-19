from app.admin_duty.components.maps import instantiate_map_snapshot
from app.admin_duty.domain.definition import (
    DataField,
    MultiHostIncidentFlow,
    ObjectiveType,
    ResourceType,
    SolutionStep,
)
from app.admin_duty.domain.dependencies import flow_verification_fact

TWO_HOST_MEDIUM = {"dependency-port-mismatch", "systemd-stale-unit-config"}
FLOW_MEDIUM = TWO_HOST_MEDIUM | {
    "service-config-permission-denied",
    "dependency-firewall-blocked",
}
FLOW_HARD = {"H-02", "H-03", "H-04", "H-05"}


def _step(capability, text, purpose="Sprawdź kolejną warstwę ścieżki.", success=True):
    return SolutionStep(
        order=1,
        capability_id=capability,
        input=text,
        purpose=purpose,
        expected_success=success,
    )


def _context_steps(steps, resources, source_host_id):
    hostnames = {
        next(
            field.value for field in resource.attributes if field.key == "hostname"
        ): resource.resource_id
        for resource in resources
        if resource.resource_type is ResourceType.HOST
    }
    host_id = source_host_id
    result = []
    for order, step in enumerate(steps, 1):
        result.append(
            step.model_copy(
                update={
                    "order": order,
                    "parameters": (
                        *step.parameters,
                        DataField(key="expected_host_id", value=host_id),
                    ),
                }
            )
        )
        if step.capability_id == "remote.ssh":
            host_id = hostnames[step.input.split()[1]]
    return tuple(result)


def materialize_flow(draft, *, two_hosts=False, preserve_ingress=False, steps=None):
    hosts = {"host-edge-01", "host-app-01"}
    if not two_hosts:
        hosts.add("host-data-01")
    if preserve_ingress:
        hosts |= {"host-client-01", "host-dns-01"}
    resources = []
    addresses = {
        next(
            field.value for field in resource.attributes if field.key == "address"
        ).split("/")[0]
        for resource in draft.initial_world_state.resources
        if resource.resource_type is ResourceType.HOST and resource.resource_id in hosts
    }
    for resource in draft.initial_world_state.resources:
        if (
            resource.resource_type is ResourceType.HOST
            and resource.resource_id not in hosts
        ):
            continue
        if resource.parent_id and resource.parent_id not in hosts:
            continue
        attributes = {field.key: field.value for field in resource.attributes}
        if (
            resource.resource_type is ResourceType.DOMAIN
            and attributes.get("address") not in addresses
        ):
            continue
        if two_hosts and resource.resource_id == "file-api-config":
            continue
        if two_hosts and resource.resource_id == "service-api":
            attributes.pop("required_dns_name", None)
            if draft.difficulty.value == "medium":
                attributes.pop("required_package", None)
        if resource.resource_type is ResourceType.SERVICE:
            attributes.pop("journal_clue", None)
            if resource.resource_id == "service-proxy":
                attributes["required_dns_name"] = "api.internal"
            if resource.resource_id == "service-api" and not two_hosts:
                attributes["required_dns_name"] = "database.internal"
        if resource.resource_id == "endpoint-portal":
            attributes["url"] = "http://portal.internal"
        resources.append(
            resource.model_copy(
                update={
                    "attributes": tuple(
                        DataField(key=key, value=value)
                        for key, value in attributes.items()
                    )
                }
            )
        )
    resource_ids = {resource.resource_id for resource in resources}
    dependencies = tuple(
        item.model_copy(update={"port_configuration_file_id": "file-proxy-config"})
        if item.dependency_id == "dep-proxy-api" and "file-proxy-config" in resource_ids
        else item
        for item in draft.service_dependencies
        if item.source_service_id in resource_ids
        and item.target_service_id in resource_ids
    )
    dependency_ids = {item.dependency_id for item in dependencies}
    flow = MultiHostIncidentFlow(
        entry_endpoint_id="endpoint-portal",
        service_path=("service-proxy", "service-api")
        if two_hosts
        else ("service-proxy", "service-api", "service-database"),
        verification_source_host_id="host-client-01"
        if preserve_ingress
        else "host-edge-01",
    )
    rules = tuple(
        item.model_copy(update={"dependency_id": "dep-proxy-api"})
        if item.dependency_id not in dependency_ids
        else item
        for item in draft.symptom_propagation
    )
    support_id = "host-app-01" if two_hosts else "host-data-01"
    world = draft.initial_world_state.model_copy(
        update={
            "resources": tuple(resources),
            "map": instantiate_map_snapshot(
                "web-operations-room",
                seed=draft.seed,
                primary_host_id=flow.verification_source_host_id,
                support_host_id=support_id,
            ),
        }
    )
    report = draft.post_incident.model_copy(
        update={
            "affected_service_ids": flow.service_path,
            "impact_path": ("sonda zewnętrzna", "reverse proxy", "API", "usługa danych")
            if preserve_ingress
            else ("reverse proxy", "API")
            if two_hosts
            else ("reverse proxy", "API", "usługa danych"),
        }
    )
    return draft.model_copy(
        update={
            "generator_version": "6.0",
            "multi_host_flow": flow,
            "initial_world_state": world,
            "service_dependencies": dependencies,
            "symptom_propagation": rules,
            "configuration_requirements": tuple(
                item
                for item in draft.configuration_requirements
                if item.file_resource_id in resource_ids
            ),
            "package_requirements": ()
            if two_hosts and draft.difficulty.value == "medium"
            else draft.package_requirements,
            "objectives": tuple(
                item.model_copy(
                    update={"completion_fact_ids": (flow_verification_fact(flow),)}
                )
                if item.objective_type is ObjectiveType.VERIFY_END_TO_END
                else item
                for item in draft.objectives
            ),
            "solution": _context_steps(
                steps or draft.solution, resources, flow.verification_source_host_id
            ),
            "post_incident": report,
        }
    )


def medium_flow(draft, category):
    steps = list(draft.solution)
    if category == "dependency-firewall-blocked":
        steps = [
            *steps[:3],
            _step("remote.ssh", "ssh app-01"),
            _step("systemd.status", "systemctl status orders-api"),
            _step("network.curl", "curl http://localhost:8080"),
            _step("network.tcp-probe", "nc -z database.internal 5432", success=False),
            *steps[3:7],
            _step("remote.ssh", "ssh app-01"),
            _step("network.tcp-probe", "nc -z database.internal 5432"),
            _step("network.curl", "curl http://localhost:8080"),
            *steps[7:],
        ]
    else:
        result = []
        for step in steps:
            result.append(step)
            if step.input == "ssh app-01":
                result.extend(
                    [
                        _step("systemd.status", "systemctl status orders-api"),
                        _step(
                            "network.curl",
                            "curl http://localhost:8080",
                            success=category != "systemd-stale-unit-config",
                        ),
                    ]
                )
            if (
                category == "dependency-port-mismatch"
                and step.input == "cat /opt/edge-proxy/upstream.conf"
            ):
                result.extend(
                    [
                        _step(
                            "network.tcp-probe",
                            "nc -z api.internal 8081",
                            success=False,
                        ),
                        _step("network.tcp-probe", "nc -z api.internal 8080"),
                    ]
                )
        steps = result
    return materialize_flow(draft, two_hosts=category in TWO_HOST_MEDIUM, steps=steps)


def hard_flow(draft, combination_id):
    if combination_id == "H-02":
        return materialize_flow(draft, preserve_ingress=True)
    steps = list(draft.solution)
    names = {
        resource.resource_id: next(
            field.value for field in resource.attributes if field.key == "hostname"
        )
        for resource in draft.initial_world_state.resources
        if resource.resource_type is ResourceType.HOST
    }
    edge = names["host-edge-01"]
    app = names["host-app-01"]
    if combination_id == "H-03":
        steps = [
            steps[0],
            steps[7],
            _step("systemd.cat", "systemctl cat edge-proxy"),
            *steps[8:11],
            _step(
                "network.curl",
                "curl http://portal.internal",
                "Sprawdź zmianę symptomu po uruchomieniu proxy.",
            ),
            _step("remote.ssh", f"ssh {app}"),
            _step("systemd.status", "systemctl status orders-api"),
            _step("journal.read", "journalctl -u orders-api"),
            *steps[2:5],
            _step("network.curl", "curl http://localhost:8080"),
            _step("remote.ssh", f"ssh {edge}"),
            steps[-1],
        ]
    else:
        result = []
        for step in steps:
            if step.input == f"ssh {names['host-client-01']}":
                step = step.model_copy(update={"input": f"ssh {edge}"})
            result.append(step)
            if step.input == f"ssh {app}":
                result.append(_step("systemd.status", "systemctl status orders-api"))
                if combination_id == "H-04":
                    result.extend(
                        [
                            _step("network.curl", "curl http://localhost:8080"),
                            _step("network.tcp-probe", "nc -z database.internal 5432"),
                            _step("filesystem.read", "cat /opt/orders-api/app.conf"),
                        ]
                    )
            if combination_id == "H-05" and step.input == "dig database.internal":
                result.extend(
                    [
                        _step("network.curl", "curl http://localhost:8080"),
                        _step(
                            "network.tcp-probe",
                            "nc -z database.internal 5432",
                            success=False,
                        ),
                    ]
                )
        steps = result
    result = materialize_flow(draft, two_hosts=combination_id == "H-03", steps=steps)
    if combination_id == "H-05":
        result = result.model_copy(
            update={
                "symptom_propagation": tuple(
                    item.model_copy(update={"health_layer": "transport"})
                    if item.affected_resource_id == "endpoint-primary-path"
                    else item
                    for item in result.symptom_propagation
                )
            }
        )
    return result
