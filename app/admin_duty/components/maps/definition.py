from typing import Literal

from pydantic import Field, model_validator

from app.admin_duty.domain.definition import (
    FrozenDomainModel,
    Identifier,
)


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
        "cabinet",
        "board",
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
        "network-rack",
        "patch-panel",
        "ups-unit",
        "cooling-unit",
        "access-panel",
    ]
    rect: PublicGameRect
    variant: str = Field(default="default", max_length=40)
    binding_role: Literal["service", "host"] | None = None
    binding_slot: Identifier | None = None
    resource_id: Identifier | None = None
    label: str | None = Field(default=None, min_length=1, max_length=80)
    tone: Literal["cyan", "blue", "amber", "green", "neutral", "danger"]


class PublicGameInteraction(FrozenDomainModel):
    id: Identifier
    type: Literal["terminal", "monitoring", "rack", "support"]
    label: str = Field(min_length=1, max_length=160)
    position: PublicGamePoint
    radius: float = Field(gt=0, le=1000)
    resource_id: Identifier | None = None
    role: Literal["primary", "support"] = "primary"
    object_id: Identifier | None = None


class PublicGameSector(FrozenDomainModel):
    id: Identifier
    label: str = Field(min_length=1, max_length=80)
    rect: PublicGameRect


class PublicGameMap(FrozenDomainModel):
    id: Identifier
    world_id: Identifier | None = None
    version: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=120)
    theme: Identifier
    width: int = Field(ge=1, le=10000)
    height: int = Field(ge=1, le=10000)
    player_spawn: PublicGamePoint
    collision_zones: tuple[PublicGameRect, ...]
    objects: tuple[PublicGameObject, ...]
    interactions: tuple[PublicGameInteraction, ...]
    sectors: tuple[PublicGameSector, ...]
    ambience: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_geometry(self):
        ids = [item.id for item in self.objects]
        interaction_ids = [item.id for item in self.interactions]
        sector_ids = [item.id for item in self.sectors]
        if (
            len(ids) != len(set(ids))
            or len(interaction_ids) != len(set(interaction_ids))
            or len(sector_ids) != len(set(sector_ids))
        ):
            raise ValueError("Mapa zawiera powtórzony identyfikator.")
        object_ids = set(ids)
        if any(
            item.object_id is not None and item.object_id not in object_ids
            for item in self.interactions
        ):
            raise ValueError("Interakcja wskazuje nieznany obiekt mapy.")
        for rect in (
            *self.collision_zones,
            *(item.rect for item in self.objects),
            *(item.rect for item in self.sectors),
        ):
            if rect.x + rect.width > self.width or rect.y + rect.height > self.height:
                raise ValueError("Geometria poza granicami mapy.")
        for point in (
            self.player_spawn,
            *(item.position for item in self.interactions),
        ):
            if point.x > self.width or point.y > self.height:
                raise ValueError("Punkt poza granicami mapy.")
        if any(
            zone.x <= self.player_spawn.x <= zone.x + zone.width
            and zone.y <= self.player_spawn.y <= zone.y + zone.height
            for zone in self.collision_zones
        ):
            raise ValueError("Spawn koliduje z wyposażeniem.")
        for item in self.interactions:
            if any(
                zone.x < item.position.x < zone.x + zone.width
                and zone.y < item.position.y < zone.y + zone.height
                for zone in self.collision_zones
            ):
                raise ValueError("Punkt interakcji wewnątrz kolizji.")
        return self


class PublicMonitoringSignal(FrozenDomainModel):
    id: Identifier
    label: str = Field(min_length=1, max_length=160)
    status: Identifier
    severity: Literal["ok", "warning", "critical"]
    resource_id: Identifier


class PublicMonitoring(FrozenDomainModel):
    title: str = Field(min_length=1, max_length=120)
    signals: tuple[PublicMonitoringSignal, ...]
    overall_status: Literal["critical", "improving", "nominal"]


MapDefinition = PublicGameMap
