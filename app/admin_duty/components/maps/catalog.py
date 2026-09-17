from types import MappingProxyType
from typing import Final

from app.admin_duty.components.maps.registry import (
    get_world_definition,
    select_world_id,
)
from app.admin_duty.components.models import ComponentMetadata, MapTemplate
from app.admin_duty.domain.definition import (
    CollisionZone,
    DataField,
    MapInteraction,
    MapSnapshot,
    Point,
)

COMPONENT_VERSION = "1.0"


def _snapshot(
    component_id,
    world_id,
    primary_host_id,
    support_host_id,
    *,
    theme,
):
    world = get_world_definition(world_id)

    return MapSnapshot(
        map_id=component_id,
        world_id=world.id,
        component_version=COMPONENT_VERSION,
        width=world.width,
        height=world.height,
        player_spawn=Point(**world.player_spawn.model_dump()),
        collision_zones=tuple(
            CollisionZone(**rect.model_dump()) for rect in world.collision_zones
        ),
        interactions=tuple(
            MapInteraction(
                interaction_id=f"{item.id}-{primary_host_id if item.role == 'primary' else support_host_id}",
                world_interaction_id=item.id,
                capability_id=item.type,
                label=item.label,
                position=Point(**item.position.model_dump()),
                radius=item.radius,
                target_resource_id=(
                    primary_host_id
                    if item.role == "primary"
                    else support_host_id
                ),
            )
            for item in world.interactions
        ),
        parameters=(DataField(key="theme", value=theme),),
    )


def _map(component_id, label, primary_host_id, support_host_id, *, theme):
    return MapTemplate(
        component_id=component_id,
        version=COMPONENT_VERSION,
        metadata=ComponentMetadata(
            label=label, description="Środowisko operacyjne Dynamic Incident."
        ),
        snapshot=_snapshot(
            component_id,
            "modern-noc",
            primary_host_id,
            support_host_id,
            theme=theme,
        ),
    )


MAP_TEMPLATES = (
    _map(
        "web-operations-room",
        "Centrum operacyjne aplikacji webowej",
        "host-app-01",
        "host-monitoring-01",
        theme="web-operations",
    ),
    _map(
        "business-service-room",
        "Stanowisko systemu biznesowego",
        "host-business-01",
        "host-database-01",
        theme="business-operations",
    ),
    _map(
        "edge-operations-room",
        "Stanowisko infrastruktury brzegowej",
        "host-edge-01",
        "host-backend-01",
        theme="edge-operations",
    ),
)

MAPS_BY_ID: Final = MappingProxyType(
    {template.component_id: template for template in MAP_TEMPLATES}
)


def get_map_template(component_id: str) -> MapTemplate:
    try:
        return MAPS_BY_ID[component_id]
    except KeyError as error:
        raise ValueError(f"Nieznany komponent mapy: {component_id}.") from error


def instantiate_map_snapshot(
    component_id: str,
    *,
    seed: int,
    primary_host_id: str | None = None,
    support_host_id: str | None = None,
) -> MapSnapshot:
    template = get_map_template(component_id)
    canonical = template.snapshot
    primary = primary_host_id or next(
        item.target_resource_id
        for item in canonical.interactions
        if item.capability_id == "terminal"
    )
    support = support_host_id or next(
        item.target_resource_id
        for item in canonical.interactions
        if item.target_resource_id != primary
    )
    theme = next(
        field.value for field in canonical.parameters if field.key == "theme"
    )
    return _snapshot(
        component_id,
        select_world_id(seed),
        primary,
        support,
        theme=theme,
    )
