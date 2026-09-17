from typing import Literal

from app.admin_duty.components.maps.definition import (
    PublicGameMap,
    PublicMonitoring,
    PublicMonitoringSignal,
)
from app.admin_duty.components.maps.registry import get_world_definition
from app.admin_duty.domain.definition import (
    IncidentDefinition,
    MapSnapshot,
    ResourceType,
)
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.recovery import (
    IncidentRecoveryState,
    get_incident_recovery_state,
)
from app.admin_duty.domain.runtime import SessionRuntimeState


def project_public_game_map(
    snapshot: MapSnapshot, state: SessionRuntimeState
) -> PublicGameMap:
    world = get_world_definition(snapshot.world_id)
    primary = next(
        (
            i.target_resource_id
            for i in snapshot.interactions
            if i.capability_id == "terminal"
        ),
        None,
    )
    support = next(
        (
            i.target_resource_id
            for i in snapshot.interactions
            if i.target_resource_id is not None and i.target_resource_id != primary
        ),
        None,
    )
    hosts = sorted(
        (
            resource
            for resource in state.world_state.resources.values()
            if resource.resource_type is ResourceType.HOST
        ),
        key=lambda resource: resource.resource_id,
    )
    services = sorted(
        (
            resource
            for resource in state.world_state.resources.values()
            if resource.resource_type is ResourceType.SERVICE
        ),
        key=lambda resource: resource.resource_id,
    )
    primary_service = next(
        (
            resource.resource_id
            for resource in services
            if resource.parent_resource_id == primary
        ),
        None,
    )
    support_service = next(
        (
            resource.resource_id
            for resource in services
            if resource.parent_resource_id == support
        ),
        None,
    )
    slots = {
        "primary-host": primary,
        "support-host": support,
        "primary-service": primary_service,
        "support-service": support_service,
        **{
            f"host-{index}": resource.resource_id
            for index, resource in enumerate(hosts, 1)
        },
        **{
            f"service-{index}": resource.resource_id
            for index, resource in enumerate(services, 1)
        },
    }
    objects = tuple(
        item.model_copy(
            update={
                "resource_id": slots.get(item.binding_slot)
                if item.binding_slot is not None
                else primary_service
                if item.binding_role == "service"
                else primary
                if item.binding_role == "host"
                else None
            }
        )
        for item in world.objects
    )
    interactions_by_id = {
        item.world_interaction_id: item for item in snapshot.interactions
    }
    interactions = tuple(
        item.model_copy(
            update={
                "id": source.interaction_id,
                "resource_id": source.target_resource_id,
            }
        )
        for item in world.interactions
        if (source := interactions_by_id.get(item.id)) is not None
    )
    return world.model_copy(
        update={
            "id": snapshot.map_id,
            "world_id": world.id,
            "version": snapshot.component_version,
            "objects": objects,
            "interactions": interactions,
        }
    )


def _public_label(resource) -> str:
    label = resource.attributes.get("label")
    if isinstance(label, str):
        return label
    hostname = resource.attributes.get("hostname")
    if resource.resource_type is ResourceType.HOST and isinstance(hostname, str):
        return hostname
    service_name = resource.attributes.get("service_name")
    if resource.resource_type is ResourceType.SERVICE and isinstance(service_name, str):
        return service_name
    return resource.resource_id


def _public_status(resource) -> str:
    health = resource.attributes.get("public_health")
    if resource.resource_type is ResourceType.SERVICE and isinstance(health, str):
        return health
    return resource.current_state


def _signal_severity(status: str) -> Literal["ok", "warning", "critical"]:
    if status in {"running", "active", "present", "healthy"}:
        return "ok"
    if status in {
        "failed",
        "stopped",
        "missing",
        "unhealthy",
        "http-502",
        "unreachable",
    }:
        return "critical"
    return "warning"


def project_public_monitoring(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> PublicMonitoring:
    resources = tuple(
        resource
        for resource in state.world_state.resources.values()
        if resource.resource_type
        in {ResourceType.HOST, ResourceType.SERVICE, ResourceType.ENDPOINT}
    )
    signals = tuple(
        PublicMonitoringSignal(
            id=f"signal-{resource.resource_id}",
            label=_public_label(resource),
            status=_public_status(resource),
            severity=_signal_severity(_public_status(resource)),
            resource_id=resource.resource_id,
        )
        for resource in resources
    )
    if definition.difficulty is DifficultyLevel.HARD:
        recovery = get_incident_recovery_state(definition, state)
        overall_status = {
            IncidentRecoveryState.BROKEN: "critical",
            IncidentRecoveryState.PARTIALLY_RECOVERED: "improving",
            IncidentRecoveryState.HEALTHY: "nominal",
        }[recovery]
    else:
        overall_status = (
            "critical"
            if any(signal.severity == "critical" for signal in signals)
            else "nominal"
        )
    return PublicMonitoring(
        title=f"Monitoring · {definition.presentation.environment_label}",
        signals=signals,
        overall_status=overall_status,
    )
