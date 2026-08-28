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


def _map(
    component_id: str,
    label: str,
    primary_host_id: str,
    support_host_id: str,
    *,
    theme: str,
) -> MapTemplate:
    return MapTemplate(
        component_id=component_id,
        version=COMPONENT_VERSION,
        metadata=ComponentMetadata(
            label=label,
            description="Kontrolowana mapa stanowiska operacyjnego.",
        ),
        snapshot=MapSnapshot(
            map_id=component_id,
            component_version=COMPONENT_VERSION,
            width=1800,
            height=1100,
            player_spawn=Point(x=900, y=944),
            collision_zones=(
                CollisionZone(x=0, y=0, width=1800, height=42),
                CollisionZone(x=0, y=1058, width=1800, height=42),
                CollisionZone(x=0, y=0, width=42, height=1100),
                CollisionZone(x=1758, y=0, width=42, height=1100),
                CollisionZone(x=650, y=112, width=500, height=108),
                CollisionZone(x=770, y=258, width=260, height=72),
                CollisionZone(x=445, y=590, width=238, height=94),
                CollisionZone(x=760, y=500, width=260, height=94),
                CollisionZone(x=770, y=690, width=240, height=82),
                CollisionZone(x=105, y=420, width=205, height=90),
                CollisionZone(x=1300, y=180, width=92, height=176),
                CollisionZone(x=1430, y=180, width=92, height=176),
                CollisionZone(x=1560, y=180, width=92, height=176),
                CollisionZone(x=1300, y=480, width=92, height=176),
                CollisionZone(x=1430, y=480, width=92, height=176),
                CollisionZone(x=1560, y=480, width=92, height=176),
                CollisionZone(x=1196, y=60, width=24, height=350),
                CollisionZone(x=1196, y=620, width=24, height=320),
                CollisionZone(x=336, y=220, width=24, height=230),
                CollisionZone(x=336, y=650, width=24, height=250),
            ),
            interactions=(
                MapInteraction(
                    interaction_id=f"terminal-{primary_host_id}",
                    capability_id="terminal",
                    label="Otwórz terminal",
                    position=Point(x=565, y=742),
                    radius=82,
                    target_resource_id=primary_host_id,
                ),
                MapInteraction(
                    interaction_id=f"monitoring-{support_host_id}",
                    capability_id="monitoring",
                    label="Sprawdź monitoring",
                    position=Point(x=900, y=378),
                    radius=86,
                    target_resource_id=support_host_id,
                ),
                MapInteraction(
                    interaction_id=f"rack-{primary_host_id}",
                    capability_id="rack",
                    label="Sprawdź rack",
                    position=Point(x=1260, y=548),
                    radius=90,
                    target_resource_id=primary_host_id,
                ),
                MapInteraction(
                    interaction_id=f"support-{support_host_id}",
                    capability_id="support",
                    label="Otwórz centrum wsparcia",
                    position=Point(x=205, y=545),
                    radius=88,
                    target_resource_id=support_host_id,
                ),
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
