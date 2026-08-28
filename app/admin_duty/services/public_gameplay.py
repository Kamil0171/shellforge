from typing import Literal

from pydantic import Field

from app.admin_duty.domain.definition import (
    FrozenDomainModel,
    Identifier,
    IncidentDefinition,
    MapSnapshot,
    ResourceType,
)
from app.admin_duty.domain.runtime import SessionRuntimeState


class PublicGamePoint(FrozenDomainModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)


class PublicGameRect(FrozenDomainModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)


class PublicGameObject(FrozenDomainModel):
    id: Identifier
    kind: Literal[
        "floor-zone",
        "wall-panel",
        "server-rack",
        "operator-desk",
        "monitor-wall",
        "light-strip",
        "plant",
        "floor-marking",
        "chair",
        "partition",
        "door",
        "cable-tray",
    ]
    rect: PublicGameRect
    label: str | None = Field(default=None, min_length=1, max_length=80)
    tone: Literal["cyan", "blue", "amber", "green", "neutral", "danger"]


class PublicGameInteraction(FrozenDomainModel):
    id: Identifier
    type: Literal["terminal", "monitoring", "rack", "support"]
    label: str = Field(min_length=1, max_length=160)
    position: PublicGamePoint
    radius: float = Field(gt=0, le=1000)
    resource_id: Identifier | None = None


class PublicGameSector(FrozenDomainModel):
    id: Identifier
    label: str = Field(min_length=1, max_length=80)
    rect: PublicGameRect


class PublicGameMap(FrozenDomainModel):
    id: Identifier
    version: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=120)
    theme: Literal["modern-noc"]
    width: int = Field(ge=1, le=10000)
    height: int = Field(ge=1, le=10000)
    player_spawn: PublicGamePoint
    collision_zones: tuple[PublicGameRect, ...]
    objects: tuple[PublicGameObject, ...]
    interactions: tuple[PublicGameInteraction, ...]
    sectors: tuple[PublicGameSector, ...]


class PublicMonitoringSignal(FrozenDomainModel):
    id: Identifier
    label: str = Field(min_length=1, max_length=160)
    status: Identifier
    severity: Literal["ok", "warning", "critical"]
    resource_id: Identifier


class PublicMonitoring(FrozenDomainModel):
    title: str = Field(min_length=1, max_length=120)
    signals: tuple[PublicMonitoringSignal, ...]


_MAP_NAMES = {
    "web-operations-room": "Modern NOC · Platforma webowa",
    "business-service-room": "Modern NOC · System biznesowy",
    "edge-operations-room": "Modern NOC · Warstwa brzegowa",
}


def _rect(x: float, y: float, width: float, height: float) -> PublicGameRect:
    return PublicGameRect(x=x, y=y, width=width, height=height)


def _object(
    object_id: str,
    kind: str,
    rect: PublicGameRect,
    tone: str,
    label: str | None = None,
) -> PublicGameObject:
    return PublicGameObject(
        id=object_id,
        kind=kind,
        rect=rect,
        tone=tone,
        label=label,
    )


def _modern_noc_objects() -> tuple[PublicGameObject, ...]:
    return (
        _object("zone-entry", "floor-zone", _rect(600, 800, 600, 240), "neutral", "WEJŚCIE / BRIEFING"),
        _object("zone-ops", "floor-zone", _rect(360, 360, 840, 440), "blue", "OPERATIONS FLOOR"),
        _object("zone-observability", "floor-zone", _rect(360, 60, 840, 300), "cyan", "OBSERVABILITY"),
        _object("zone-data-hall", "floor-zone", _rect(1220, 60, 520, 880), "amber", "DATA HALL"),
        _object("zone-support", "floor-zone", _rect(60, 220, 300, 680), "green", "SUPPORT BAY"),
        _object("monitor-wall", "monitor-wall", _rect(650, 112, 500, 108), "cyan", "ŚCIANA MONITORINGU"),
        _object("monitor-console", "operator-desk", _rect(770, 258, 260, 72), "cyan", "OBSERVABILITY CONSOLE"),
        _object("monitor-chair", "chair", _rect(872, 338, 56, 50), "neutral"),
        _object("desk-terminal", "operator-desk", _rect(445, 590, 238, 94), "blue", "OPS-01 · TERMINAL"),
        _object("chair-terminal", "chair", _rect(535, 700, 56, 50), "neutral"),
        _object("desk-triage", "operator-desk", _rect(760, 500, 260, 94), "neutral", "INCIDENT TRIAGE"),
        _object("chair-triage", "chair", _rect(862, 610, 56, 50), "neutral"),
        _object("desk-network", "operator-desk", _rect(770, 690, 240, 82), "green", "NETWORK OPS"),
        _object("support-desk", "operator-desk", _rect(105, 420, 205, 90), "green", "RUNBOOKS"),
        _object("rack-a", "server-rack", _rect(1300, 180, 92, 176), "cyan", "RACK A · CORE"),
        _object("rack-b", "server-rack", _rect(1430, 180, 92, 176), "blue", "RACK B · COMPUTE"),
        _object("rack-c", "server-rack", _rect(1560, 180, 92, 176), "amber", "RACK C · PROD"),
        _object("rack-d", "server-rack", _rect(1300, 480, 92, 176), "green", "RACK D · STORAGE"),
        _object("rack-e", "server-rack", _rect(1430, 480, 92, 176), "blue", "RACK E · EDGE"),
        _object("rack-f", "server-rack", _rect(1560, 480, 92, 176), "neutral", "RACK F · SPARE"),
        _object("data-partition-top", "partition", _rect(1196, 60, 24, 350), "neutral"),
        _object("data-partition-bottom", "partition", _rect(1196, 620, 24, 320), "neutral"),
        _object("support-partition-top", "partition", _rect(336, 220, 24, 230), "neutral"),
        _object("support-partition-bottom", "partition", _rect(336, 650, 24, 250), "neutral"),
        _object("entry-door", "door", _rect(820, 1002, 160, 18), "green", "NOC ACCESS"),
        _object("cable-core", "cable-tray", _rect(1250, 780, 430, 24), "amber"),
        _object("light-observability", "light-strip", _rect(430, 82, 700, 8), "cyan"),
        _object("light-ops", "light-strip", _rect(430, 390, 700, 8), "blue"),
        _object("marking-entry", "floor-marking", _rect(790, 840, 220, 5), "green"),
        _object("marking-data", "floor-marking", _rect(1248, 408, 440, 5), "amber"),
        _object("plant-entry-left", "plant", _rect(640, 906, 48, 48), "green"),
        _object("plant-entry-right", "plant", _rect(1112, 906, 48, 48), "green"),
    )


def _modern_noc_sectors() -> tuple[PublicGameSector, ...]:
    return (
        PublicGameSector(id="entry", label="Wejście NOC", rect=_rect(600, 800, 600, 240)),
        PublicGameSector(id="operations", label="Sala operacyjna", rect=_rect(360, 360, 840, 440)),
        PublicGameSector(id="observability", label="Monitoring", rect=_rect(360, 60, 840, 300)),
        PublicGameSector(id="data-hall", label="Serwerownia", rect=_rect(1220, 60, 520, 880)),
        PublicGameSector(id="support", label="Strefa wsparcia", rect=_rect(60, 220, 300, 680)),
    )


def project_public_game_map(snapshot: MapSnapshot) -> PublicGameMap:
    interaction_types = {"terminal", "monitoring", "rack", "support"}
    interactions = tuple(
        PublicGameInteraction(
            id=interaction.interaction_id,
            type=interaction.capability_id,
            label=interaction.label,
            position=PublicGamePoint(
                x=interaction.position.x,
                y=interaction.position.y,
            ),
            radius=interaction.radius,
            resource_id=interaction.target_resource_id,
        )
        for interaction in snapshot.interactions
        if interaction.capability_id in interaction_types
    )
    return PublicGameMap(
        id=snapshot.map_id,
        version=snapshot.component_version,
        name=_MAP_NAMES.get(snapshot.map_id, "Modern NOC"),
        theme="modern-noc",
        width=snapshot.width,
        height=snapshot.height,
        player_spawn=PublicGamePoint(
            x=snapshot.player_spawn.x,
            y=snapshot.player_spawn.y,
        ),
        collision_zones=tuple(
            PublicGameRect(
                x=zone.x,
                y=zone.y,
                width=zone.width,
                height=zone.height,
            )
            for zone in snapshot.collision_zones
        ),
        objects=_modern_noc_objects(),
        interactions=interactions,
        sectors=_modern_noc_sectors(),
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
