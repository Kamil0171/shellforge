from types import MappingProxyType
from typing import Final

from app.admin_duty.components.maps.loader import DATACENTER_HALL, MODERN_NOC

WORLD_DEFINITIONS = (MODERN_NOC, DATACENTER_HALL)
WORLD_DEFINITIONS_BY_ID: Final = MappingProxyType(
    {definition.id: definition for definition in WORLD_DEFINITIONS}
)


def get_world_definition(world_id: str):
    try:
        return WORLD_DEFINITIONS_BY_ID[world_id]
    except KeyError as error:
        raise ValueError(f"Nieznany layout świata: {world_id}.") from error


def select_world_id(seed: int) -> str:
    world_ids = tuple(WORLD_DEFINITIONS_BY_ID)
    return world_ids[(seed + 1) % len(world_ids)]
