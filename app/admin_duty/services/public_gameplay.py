from typing import Literal

from app.admin_duty.components.maps.definition import (
    PublicGameMap,
    PublicMonitoring,
    PublicMonitoringSignal,
)
from app.admin_duty.components.maps.loader import MODERN_NOC
from app.admin_duty.domain.definition import (
    IncidentDefinition,
    MapSnapshot,
    ResourceType,
)
from app.admin_duty.domain.runtime import SessionRuntimeState


def project_public_game_map(
    snapshot: MapSnapshot, state: SessionRuntimeState
) -> PublicGameMap:
    primary = next(
        (
            i.target_resource_id
            for i in snapshot.interactions
            if i.capability_id == "terminal"
        ),
        None,
    )
    service = next(
        (
            r.resource_id
            for r in state.world_state.resources.values()
            if r.resource_type is ResourceType.SERVICE
            and r.parent_resource_id == primary
        ),
        None,
    )
    objects = tuple(
        item.model_copy(
            update={
                "resource_id": service
                if item.binding_role == "service"
                else primary
                if item.binding_role == "host"
                else None
            }
        )
        for item in MODERN_NOC.objects
    )
    interactions = tuple(
        item.model_copy(
            update={
                "id": source.interaction_id,
                "resource_id": source.target_resource_id,
            }
        )
        for item in MODERN_NOC.interactions
        for source in snapshot.interactions
        if source.capability_id == item.type
    )
    return MODERN_NOC.model_copy(
        update={
            "id": snapshot.map_id,
            "version": snapshot.component_version,
            "objects": objects,
            "interactions": interactions,
        }
    )


def _public_label(resource) -> str:
    hostname = resource.attributes.get("hostname")
    if resource.resource_type is ResourceType.HOST and isinstance(hostname, str):
        return hostname
    return resource.resource_id


def _signal_severity(status: str) -> Literal["ok", "warning", "critical"]:
    if status in {"running", "active", "present", "healthy"}:
        return "ok"
    if status in {"failed", "stopped", "missing", "unhealthy"}:
        return "critical"
    return "warning"


def project_public_monitoring(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> PublicMonitoring:
    resources = tuple(
        resource
        for resource in state.world_state.resources.values()
        if resource.resource_type in {ResourceType.HOST, ResourceType.SERVICE}
    )
    return PublicMonitoring(
        title=f"Monitoring · {definition.presentation.environment_label}",
        signals=tuple(
            PublicMonitoringSignal(
                id=f"signal-{resource.resource_id}",
                label=_public_label(resource),
                status=resource.current_state,
                severity=_signal_severity(resource.current_state),
                resource_id=resource.resource_id,
            )
            for resource in resources
        ),
    )
