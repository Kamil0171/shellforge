from types import MappingProxyType
from typing import Final

from app.admin_duty.components.models import ComponentMetadata, MapTemplate
from app.admin_duty.domain.definition import (
    CollisionZone,
    DataField,
    MapInteraction,
    MapSnapshot,
    Point,
)

COMPONENT_VERSION = "1.0"


def _map(component_id, label, primary_host_id, support_host_id, *, theme):
    from app.admin_duty.components.maps.loader import MODERN_NOC

    return MapTemplate(
        component_id=component_id,
        version=COMPONENT_VERSION,
        metadata=ComponentMetadata(
            label=label, description="Modern NOC — centrum operacyjne."
        ),
        snapshot=MapSnapshot(
            map_id=component_id,
            component_version=COMPONENT_VERSION,
            width=MODERN_NOC.width,
            height=MODERN_NOC.height,
            player_spawn=Point(**MODERN_NOC.player_spawn.model_dump()),
            collision_zones=tuple(
                CollisionZone(**rect.model_dump())
                for rect in MODERN_NOC.collision_zones
            ),
            interactions=tuple(
                MapInteraction(
                    interaction_id=f"{item.id}-{primary_host_id if item.role == 'primary' else support_host_id}",
                    capability_id=item.type,
                    label=item.label,
                    position=Point(**item.position.model_dump()),
                    radius=item.radius,
                    target_resource_id=primary_host_id
                    if item.role == "primary"
                    else support_host_id,
                )
                for item in MODERN_NOC.interactions
            ),
            parameters=(DataField(key="theme", value=theme),),
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
