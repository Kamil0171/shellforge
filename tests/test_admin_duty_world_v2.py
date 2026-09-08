from pathlib import Path

import pytest
from pydantic import ValidationError

from app.admin_duty.components.maps.definition import MapDefinition
from app.admin_duty.components.maps.loader import MODERN_NOC, load_map
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
    assert game_map.collision_zones == MODERN_NOC.collision_zones
    assert {item.id for item in game_map.interactions} == {
        item.interaction_id for item in snapshot.interactions
    }
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
    execute(definition, state, service, "systemctl restart example-api")
    after = project_public_monitoring(definition, state)
    assert all(signal.severity == "ok" for signal in after.signals)
    assert "attributes" not in after.model_dump_json()
