from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.admin_duty.components.maps import (
    WORLD_DEFINITIONS,
    get_map_template,
    get_world_definition,
    instantiate_map_snapshot,
    select_world_id,
)
from app.admin_duty.components.maps.definition import MapDefinition
from app.admin_duty.components.maps.loader import (
    DATACENTER_HALL,
    MODERN_NOC,
    load_map,
)
from app.admin_duty.domain.definition import ResourceType
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.runtime import create_session_runtime
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.services.public_gameplay import (
    project_public_game_map,
    project_public_monitoring,
)
from tests.test_admin_duty_virtual_shell import build_shell, execute


def test_json_map_loading_and_round_trip():
    loaded = load_map(Path("app/admin_duty/components/maps/modern_noc.json"))
    assert loaded == MODERN_NOC
    assert MapDefinition.model_validate_json(loaded.model_dump_json()) == loaded
    assert {item.variant for item in loaded.objects if item.kind == "server-rack"} == {
        "core",
        "compute",
        "prod",
        "storage",
        "edge",
        "spare",
    }
    assert (
        len({item.variant for item in loaded.objects if item.kind == "floor-zone"}) >= 4
    )
    assert {item.type for item in loaded.interactions} == {
        "terminal",
        "monitoring",
        "rack",
        "support",
    }
    assert "�" not in loaded.model_dump_json()


def test_world_registry_contains_both_layouts_and_rejects_unknown_id():
    assert {world.id for world in WORLD_DEFINITIONS} == {
        "modern-noc",
        "datacenter-hall",
    }
    assert get_world_definition("modern-noc") is MODERN_NOC
    assert get_world_definition("datacenter-hall") is DATACENTER_HALL
    with pytest.raises(ValueError, match="Nieznany layout świata"):
        get_world_definition("unknown-world")
    with pytest.raises(ValueError, match="Nieznany komponent mapy"):
        get_map_template("unknown-map-component")


def test_world_selection_is_deterministic_and_does_not_change_component_id():
    for seed in range(20):
        assert select_world_id(seed) == select_world_id(seed)
        first = instantiate_map_snapshot("web-operations-room", seed=seed)
        second = instantiate_map_snapshot("web-operations-room", seed=seed)
        assert first == second
        assert first.map_id == "web-operations-room"
        assert first.world_id == select_world_id(seed)
    assert {select_world_id(seed) for seed in range(4)} == {
        "modern-noc",
        "datacenter-hall",
    }


def test_world_selection_preserves_existing_scenario_determinism():
    now = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)
    generator = DeterministicIncidentGenerator()
    first = generator.generate(DifficultyLevel.MEDIUM, seed=8, now=now)
    second = generator.generate(DifficultyLevel.MEDIUM, seed=8, now=now)
    assert first.initial_world_state.map == second.initial_world_state.map
    assert first.presentation == second.presentation
    assert first.faults == second.faults
    assert first.objectives == second.objectives


def test_modern_noc_snapshot_remains_functionally_compatible():
    canonical = get_map_template("web-operations-room").snapshot
    selected = instantiate_map_snapshot("web-operations-room", seed=1)
    assert selected == canonical


def test_datacenter_snapshot_uses_selected_world_geometry_and_interaction_ids():
    snapshot = instantiate_map_snapshot("web-operations-room", seed=0)
    assert snapshot.world_id == DATACENTER_HALL.id
    assert snapshot.width == DATACENTER_HALL.width
    assert snapshot.height == DATACENTER_HALL.height
    assert [zone.model_dump() for zone in snapshot.collision_zones] == [
        zone.model_dump() for zone in DATACENTER_HALL.collision_zones
    ]
    assert {item.world_interaction_id for item in snapshot.interactions} == {
        item.id for item in DATACENTER_HALL.interactions
    }


def test_datacenter_definition_has_valid_objects_interactions_and_collisions():
    world = DATACENTER_HALL
    assert len(world.sectors) == 5
    assert len(world.objects) == 59
    assert len(world.interactions) == 5
    assert len({item.id for item in world.objects}) == len(world.objects)
    assert all(item.object_id for item in world.interactions)
    assert {item.object_id for item in world.interactions} <= {
        item.id for item in world.objects
    }
    collision_rects = {
        (zone.x, zone.y, zone.width, zone.height) for zone in world.collision_zones
    }
    solid_kinds = {
        "server-rack",
        "network-rack",
        "patch-panel",
        "operator-desk",
        "monitor-wall",
        "ups-unit",
        "cooling-unit",
        "access-panel",
        "partition",
        "cabinet",
        "wall-panel",
    }
    for item in world.objects:
        if item.kind in solid_kinds:
            rect = item.rect
            assert (rect.x, rect.y, rect.width, rect.height) in collision_rects
    boundaries = {
        (0, 0, 2200, 36), (0, 1364, 2200, 36),
        (0, 0, 36, 1400), (2164, 0, 36, 1400),
    }
    assert collision_rects == boundaries | {
        (item.rect.x, item.rect.y, item.rect.width, item.rect.height)
        for item in world.objects if item.kind in solid_kinds
    }
    assert len(world.collision_zones) == len(collision_rects) == 38


def test_composition_replacements_shrink_collisions_and_clear_old_footprints():
    world = DATACENTER_HALL
    removed_rects = {
        (730, 390, 86, 170), (530, 630, 86, 170),
        (1180, 120, 72, 190), (1440, 120, 72, 190),
        (1360, 590, 100, 130), (1360, 780, 100, 130),
        (1775, 420, 150, 150),
    }
    replaced_rects = {
        "maintenance-cart": (1150, 1210, 250, 82),
        "fiber-distribution-frame": (1310, 120, 72, 190),
        "service-crate": (1210, 780, 100, 130),
        "power-distribution-panel": (1775, 670, 150, 150),
    }
    collisions = {
        (rect.x, rect.y, rect.width, rect.height) for rect in world.collision_zones
    }
    assert not collisions & (removed_rects | set(replaced_rects.values()))
    for object_id, (x, y, width, height) in replaced_rects.items():
        item = next(item for item in world.objects if item.id == object_id)
        rect = item.rect
        assert rect.x == x and rect.y == y
        assert rect.width <= width and rect.height < height
        assert rect.width * rect.height < width * height
        assert (rect.x, rect.y, rect.width, rect.height) in collisions
        assert item.binding_slot is None and item.resource_id is None
        assert all(point.object_id != item.id for point in world.interactions)


def test_network_east_corridor_has_comfortable_clearance_and_matching_patch_collision():
    world = DATACENTER_HALL
    objects = {item.id: item for item in world.objects}
    east = objects["patch-panel-east"].rect
    west = objects["patch-panel-west"].rect
    partition = objects["partition-power-top"].rect
    right_clearance = partition.x - (east.x + east.width)
    panel_clearance = east.x - (west.x + west.width)
    assert right_clearance >= 80
    assert panel_clearance >= 70
    assert (east.x, east.y, east.width, east.height) == (1280, 340, 170, 42)
    collisions = {
        (zone.x, zone.y, zone.width, zone.height) for zone in world.collision_zones
    }
    assert (1280, 340, 170, 42) in collisions
    assert (1310, 340, 170, 42) not in collisions
    corridors = [
        (east.x + east.width, 120, right_clearance, 360),
        (west.x + west.width, east.y, panel_clearance, east.height),
    ]
    for x, y, width, height in corridors:
        assert min(width, height) >= 2 * 20
        for zone in world.collision_zones:
            assert not (
                x < zone.x + zone.width
                and x + width > zone.x
                and y < zone.y + zone.height
                and y + height > zone.y
            ), zone


def test_operations_entrance_has_comfortable_clearance_and_no_old_console_collision():
    world = DATACENTER_HALL
    objects = {item.id: item for item in world.objects}
    console = objects["desk-admin"].rect
    monitor = objects["monitor-wall-dc"].rect
    player_width, player_height = 20, 12
    clearance = monitor.x - (console.x + console.width)
    assert clearance >= 70
    assert clearance >= 2 * player_width
    assert (console.x, console.y, console.width, console.height) == (710, 1100, 300, 92)
    assert (world.player_spawn.x, world.player_spawn.y) == (1100, 1290)
    assert not any(
        (zone.x, zone.y, zone.width, zone.height) == (770, 1100, 300, 92)
        for zone in world.collision_zones
    )
    path = [(x, 1290) for x in range(1045, 1101)]
    path.extend((1045, y) for y in range(970, 1291))
    for x, y in path:
        for zone in world.collision_zones:
            assert not (
                x + player_width > zone.x
                and x - player_width < zone.x + zone.width
                and y + player_height > zone.y
                and y - player_height < zone.y + zone.height
            ), (x, y, zone)


@pytest.mark.parametrize(
    "passage",
    [
        (1000, 750, 50, 240),
        (1400, 390, 100, 170),
        (1490, 400, 490, 70),
        (1740, 330, 220, 330),
    ],
    ids=["storage-entry", "network-entry", "network-to-power", "power-aisle"],
)
def test_critical_passages_keep_clear_corridors(passage):
    x, y, width, height = passage
    assert min(width, height) >= 2 * 20
    for zone in DATACENTER_HALL.collision_zones:
        assert not (
            x < zone.x + zone.width
            and x + width > zone.x
            and y < zone.y + zone.height
            and y + height > zone.y
        ), zone


def test_datacenter_spawn_and_interactions_are_reachable_on_lightweight_grid():
    world = DATACENTER_HALL
    step = 20
    margin = 11

    def blocked(x, y):
        return any(
            zone.x - margin <= x <= zone.x + zone.width + margin
            and zone.y - margin <= y <= zone.y + zone.height + margin
            for zone in world.collision_zones
        )

    start = (
        round(world.player_spawn.x / step) * step,
        round(world.player_spawn.y / step) * step,
    )
    pending = [start]
    visited = {start}
    while pending:
        x, y = pending.pop()
        for point in ((x - step, y), (x + step, y), (x, y - step), (x, y + step)):
            xx, yy = point
            if (
                point in visited
                or xx < 0
                or yy < 0
                or xx > world.width
                or yy > world.height
                or blocked(xx, yy)
            ):
                continue
            visited.add(point)
            pending.append(point)

    assert not blocked(*start)
    for interaction in world.interactions:
        assert any(
            abs(x - interaction.position.x) <= step
            and abs(y - interaction.position.y) <= step
            for x, y in visited
        ), interaction.id
    samples = [
        (773, 475), (573, 715), (1216, 215), (1476, 215),
        (1410, 655), (1410, 845), (1850, 495),
        (980, 500), (1540, 500),
        *((x, y) for x in (270, 470, 670, 870) for y in (360, 600, 840)),
        *((x, 970) for x in (740, 1100, 1500, 1900)),
    ]
    for xx, yy in samples:
        assert not blocked(xx, yy), (xx, yy)
        assert any(abs(x - xx) <= step and abs(y - yy) <= step for x, y in visited)
    for sector in world.sectors:
        rect = sector.rect
        assert any(
            rect.x < x < rect.x + rect.width and rect.y < y < rect.y + rect.height
            for x, y in visited
        ), sector.id


def test_datacenter_resource_slots_place_multi_host_scenario_deterministically():
    definition = DeterministicIncidentGenerator().generate(
        DifficultyLevel.MEDIUM,
        seed=0,
    )
    state = create_session_runtime(definition)
    game_map = project_public_game_map(definition.initial_world_state.map, state)
    host_ids = sorted(
        resource.resource_id
        for resource in state.world_state.resources.values()
        if resource.resource_type is ResourceType.HOST
    )
    placed_host_ids = [
        item.resource_id
        for item in game_map.objects
        if item.binding_slot is not None
        and item.binding_slot.startswith("host-")
        and item.resource_id is not None
    ]
    assert game_map.world_id == "datacenter-hall"
    assert placed_host_ids == host_ids


@pytest.mark.parametrize(
    "fault",
    ["duplicate", "sector", "bounds", "spawn", "collision", "interaction", "kind"],
)
def test_map_definition_rejects_invalid_geometry(fault):
    data = MODERN_NOC.model_dump(mode="json")
    if fault == "duplicate":
        data["objects"].append(data["objects"][0])
    elif fault == "sector":
        data["sectors"].append(data["sectors"][0])
    elif fault == "bounds":
        data["objects"][0]["rect"]["width"] = 99999
    elif fault == "spawn":
        data["player_spawn"]["x"] = 99999
    elif fault == "collision":
        zone = data["collision_zones"][0]
        data["player_spawn"] = {"x": zone["x"] + 1, "y": zone["y"] + 1}
    elif fault == "interaction":
        data["interactions"][0]["position"]["x"] = 99999
    else:
        data["objects"][0]["kind"] = "arbitrary-code"
    with pytest.raises(ValidationError):
        MapDefinition.model_validate(data)


@pytest.mark.parametrize("seed", range(12))
def test_runtime_bindings_are_derived_from_resources_not_environment_names(seed):
    definition, state, service = build_shell(seed)
    snapshot = definition.initial_world_state.map
    game_map = project_public_game_map(snapshot, state)
    primary = next(
        item.target_resource_id
        for item in snapshot.interactions
        if item.capability_id == "terminal"
    )
    service_ids = {
        r.resource_id
        for r in state.world_state.resources.values()
        if r.parent_resource_id == primary and r.resource_type.value == "service"
    }
    assert service_ids
    assert all(
        item.resource_id in service_ids
        for item in game_map.objects
        if item.binding_role == "service"
    )
    assert all(
        item.resource_id == primary
        for item in game_map.objects
        if item.binding_role == "host"
    )
    world = get_world_definition(snapshot.world_id)
    assert game_map.world_id == snapshot.world_id
    assert game_map.collision_zones == world.collision_zones
    assert {item.id for item in game_map.interactions} == {
        item.interaction_id for item in snapshot.interactions
    }
    resource_ids = set(state.world_state.resources)
    assert all(
        item.resource_id is None or item.resource_id in resource_ids
        for item in game_map.objects
    )
    public = game_map.model_dump_json()
    for hidden in (
        "fault_type",
        "expected_exec_start",
        "expected_environment_value",
        "solution",
    ):
        assert hidden not in public


def test_public_monitoring_tracks_repair_without_root_cause():
    definition, state, service = build_shell(seed=1)
    before = project_public_monitoring(definition, state)
    assert any(signal.severity == "critical" for signal in before.signals)
    execute(definition, state, service, "systemctl restart orders-api")
    after = project_public_monitoring(definition, state)
    assert all(signal.severity == "ok" for signal in after.signals)
    assert "attributes" not in after.model_dump_json()
