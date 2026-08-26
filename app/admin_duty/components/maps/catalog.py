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
    target_host_id: str,
    *,
    spawn: Point,
    terminal: Point,
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
            width=800,
            height=500,
            player_spawn=spawn,
            collision_zones=(CollisionZone(x=300, y=100, width=80, height=120),),
            interactions=(
                MapInteraction(
                    interaction_id=f"terminal-{target_host_id}",
                    capability_id="terminal",
                    label="Terminal hosta operacyjnego",
                    position=terminal,
                    radius=60,
                    target_resource_id=target_host_id,
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
        spawn=Point(x=80, y=250),
        terminal=Point(x=650, y=250),
        theme="web-operations",
    ),
    _map(
        "business-service-room",
        "Stanowisko systemu biznesowego",
        "host-business-01",
        spawn=Point(x=110, y=410),
        terminal=Point(x=620, y=150),
        theme="business-operations",
    ),
    _map(
        "edge-operations-room",
        "Stanowisko infrastruktury brzegowej",
        "host-edge-01",
        spawn=Point(x=100, y=90),
        terminal=Point(x=670, y=390),
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
