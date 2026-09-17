import os
import subprocess
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

import app.admin_duty.dynamic_router as dynamic_router
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.repositories import (
    SESSION_TTL,
    InMemoryScenarioRepository,
    InMemorySessionRepository,
)
from app.admin_duty.services import DynamicIncidentService
from app.main import app

FIXED_NOW = datetime(2026, 8, 25, 20, 0, tzinfo=UTC)
client = TestClient(app)


def build_service(*, max_sessions=500, generator=None):
    scenarios = InMemoryScenarioRepository()
    sessions = InMemorySessionRepository(max_sessions=max_sessions)
    service = DynamicIncidentService(
        generator=generator or DeterministicIncidentGenerator(),
        scenario_repository=scenarios,
        session_repository=sessions,
    )
    return service, scenarios, sessions


@pytest.fixture
def api_context(monkeypatch):
    service, scenarios, sessions = build_service()
    clock = {"now": FIXED_NOW}
    app.dependency_overrides[dynamic_router.get_dynamic_incident_service] = lambda: (
        service
    )
    monkeypatch.setattr(dynamic_router, "utc_now", lambda: clock["now"])

    yield {
        "service": service,
        "scenarios": scenarios,
        "sessions": sessions,
        "clock": clock,
    }

    app.dependency_overrides.clear()


def start_easy(*, seed=1):
    return client.post(
        "/admin-duty/dynamic/api/start",
        json={"difficulty": "easy", "seed": seed},
    )


def test_complete_dynamic_api_flow(api_context):
    clock = api_context["clock"]
    started_response = start_easy()

    assert started_response.status_code == 200
    started = started_response.json()
    session_id = started["session_id"]
    assert started["scenario_id"]
    assert started["difficulty"] == "easy"
    assert started["progress"]["status"] == "active"
    assert started["incident"]["title"] == "Niedostępność API platformy"
    assert started["incident"]["briefing"]
    assert started["hint_limit"] == 3
    assert started["revealed_hints"] == []
    assert started["infrastructure"]["nodes"]
    assert started["game_map"]["theme"] == "modern-noc"
    assert started["game_map"]["world_id"] == "modern-noc"
    assert {item["type"] for item in started["game_map"]["interactions"]} == {
        "terminal",
        "monitoring",
        "rack",
        "support",
    }
    assert started["monitoring"]["signals"]
    assert started["shell"] == {
        "user": "operator",
        "hostname": "app-01",
        "current_working_directory": "/home/operator",
        "prompt": "operator@app-01:~$",
    }
    assert len(started["support_center"]["runbooks"]) >= 2
    assert started["support_center"]["operational_guidance"]
    assert "filesystem" not in started
    assert "virtual_rocky" not in started

    current = client.get(f"/admin-duty/dynamic/api/sessions/{session_id}")
    assert current.status_code == 200
    assert current.json()["progress"]["commands_used"] == 0

    clock["now"] += timedelta(minutes=1)
    status = client.post(
        "/admin-duty/dynamic/api/command",
        json={
            "session_id": session_id,
            "command": "systemctl status service-api",
        },
    )
    assert status.status_code == 200
    assert "Active: failed" in status.json()["output"]
    assert status.json()["progress"]["commands_used"] == 1

    clock["now"] += timedelta(minutes=1)
    restart = client.post(
        "/admin-duty/dynamic/api/command",
        json={
            "session_id": session_id,
            "command": "systemctl restart service-api",
        },
    )
    assert restart.status_code == 200
    assert restart.json()["progress"]["commands_used"] == 2
    assert restart.json()["progress"]["mission_complete"] is True
    assert restart.json()["progress"]["status"] == "completed"

    completed = client.get(f"/admin-duty/dynamic/api/sessions/{session_id}")
    assert completed.status_code == 200
    assert completed.json()["progress"]["status"] == "completed"

    clock["now"] += timedelta(minutes=1)
    rejected = client.post(
        "/admin-duty/dynamic/api/command",
        json={
            "session_id": session_id,
            "command": "systemctl status service-api",
        },
    )
    assert rejected.status_code == 409

    clock["now"] += timedelta(minutes=1)
    ended = client.post(
        "/admin-duty/dynamic/api/end",
        json={"session_id": session_id},
    )
    assert ended.status_code == 200
    assert ended.json()["ended"] is True
    assert ended.json()["progress"]["status"] == "ended"

    after_end = client.get(f"/admin-duty/dynamic/api/sessions/{session_id}")
    assert after_end.status_code == 200
    assert after_end.json()["progress"]["status"] == "ended"

    rejected_after_end = client.post(
        "/admin-duty/dynamic/api/command",
        json={
            "session_id": session_id,
            "command": "systemctl status service-api",
        },
    )
    assert rejected_after_end.status_code == 409


def test_api_rejects_invalid_and_supports_medium_and_hard(api_context):
    invalid = client.post(
        "/admin-duty/dynamic/api/start",
        json={"difficulty": "expert"},
    )
    assert invalid.status_code == 422

    medium = client.post(
        "/admin-duty/dynamic/api/start",
        json={"difficulty": "medium", "seed": 1},
    )
    assert medium.status_code == 200
    assert medium.json()["difficulty"] == "medium"

    hard = client.post(
        "/admin-duty/dynamic/api/start",
        json={"difficulty": "hard", "seed": 1},
    )
    assert hard.status_code == 200
    assert hard.json()["difficulty"] == "hard"
    assert hard.json()["monitoring"]["overall_status"] == "critical"


def test_api_maps_invalid_command_and_unknown_session(api_context):
    started = start_easy().json()
    invalid_command = client.post(
        "/admin-duty/dynamic/api/command",
        json={
            "session_id": started["session_id"],
            "command": "systemctl destroy service-api",
        },
    )
    unknown = client.get(f"/admin-duty/dynamic/api/sessions/{uuid4()}")
    invalid_uuid = client.get("/admin-duty/dynamic/api/sessions/not-a-uuid")

    assert invalid_command.status_code == 400
    assert unknown.status_code == 404
    assert invalid_uuid.status_code == 422


def test_api_request_models_forbid_extra_and_limit_command_length(api_context):
    extra_field = client.post(
        "/admin-duty/dynamic/api/start",
        json={"difficulty": "easy", "unexpected": True},
    )
    too_long = client.post(
        "/admin-duty/dynamic/api/command",
        json={
            "session_id": str(uuid4()),
            "command": "x" * 1025,
        },
    )

    assert extra_field.status_code == 422
    assert too_long.status_code == 422


def test_expired_api_session_and_scenario_are_removed(api_context):
    started = start_easy().json()
    api_context["clock"]["now"] += SESSION_TTL

    response = client.get(f"/admin-duty/dynamic/api/sessions/{started['session_id']}")

    assert response.status_code == 404
    assert not api_context["scenarios"].exists(UUID(started["scenario_id"]))


def test_api_enforces_session_limit(monkeypatch):
    service, _, _ = build_service(max_sessions=1)
    app.dependency_overrides[dynamic_router.get_dynamic_incident_service] = lambda: (
        service
    )
    monkeypatch.setattr(dynamic_router, "utc_now", lambda: FIXED_NOW)

    try:
        assert start_easy(seed=1).status_code == 200
        limited = start_easy(seed=2)
        assert limited.status_code == 503
    finally:
        app.dependency_overrides.clear()


def test_two_api_sessions_are_independent_and_seed_is_deterministic(api_context):
    first = start_easy(seed=555).json()
    second = start_easy(seed=555).json()

    client.post(
        "/admin-duty/dynamic/api/command",
        json={
            "session_id": first["session_id"],
            "command": "systemctl status service-api",
        },
    )
    second_view = client.get(
        f"/admin-duty/dynamic/api/sessions/{second['session_id']}"
    ).json()
    first_definition = api_context["scenarios"].get(UUID(first["scenario_id"]))
    second_definition = api_context["scenarios"].get(UUID(second["scenario_id"]))

    assert first["scenario_id"] != second["scenario_id"]
    assert second_view["progress"]["commands_used"] == 0
    assert first_definition.model_dump(
        exclude={"scenario_id", "created_at"}
    ) == second_definition.model_dump(exclude={"scenario_id", "created_at"})


def test_public_api_does_not_expose_backend_only_definition_data(api_context):
    response = start_easy(seed=123).json()
    forbidden_keys = {
        "faults",
        "solution",
        "symptoms",
        "generation",
        "seed",
        "initial_world_state",
        "completion_condition",
        "attributes",
        "expected_exec_start",
        "configured_exec_start",
        "expected_mode",
        "fault_type",
        "root_cause",
        "command_capabilities",
        "parameters",
        "capability_id",
        "map_snapshot",
    }

    def collect_keys(value):
        if isinstance(value, dict):
            return set(value) | {
                key for item in value.values() for key in collect_keys(item)
            }
        if isinstance(value, list):
            return {key for item in value for key in collect_keys(item)}
        return set()

    assert forbidden_keys.isdisjoint(collect_keys(response))


def test_hint_lifecycle_exposes_only_revealed_prefix(api_context):
    started = start_easy(seed=123).json()
    session_id = started["session_id"]
    definition = api_context["scenarios"].get(UUID(started["scenario_id"]))
    initial_score = started["progress"]["score"]

    assert "hint" not in started
    assert started["revealed_hints"] == []

    first = client.post(
        "/admin-duty/dynamic/api/hint",
        json={"session_id": session_id},
    )

    assert first.status_code == 200
    payload = first.json()
    assert payload["hint"] == {
        "order": definition.hints[0].order,
        "text": definition.hints[0].text,
        "cost": definition.hints[0].cost,
    }
    assert payload["revealed_hints"] == [payload["hint"]]
    assert payload["progress"]["hints_used"] == 1
    assert payload["progress"]["revision"] == 1
    assert payload["progress"]["score"] == max(
        0,
        initial_score - definition.hints[0].cost,
    )

    refreshed = client.get(f"/admin-duty/dynamic/api/sessions/{session_id}").json()
    assert refreshed["revealed_hints"] == payload["revealed_hints"]
    assert len(refreshed["revealed_hints"]) == refreshed["progress"]["hints_used"]
    assert all(
        future.text not in str(refreshed)
        for future in definition.hints[refreshed["progress"]["hints_used"] :]
    )


def test_hint_limit_and_inactive_session_rejection(api_context):
    started = start_easy(seed=321).json()
    session_id = started["session_id"]

    for expected_used in range(1, started["hint_limit"] + 1):
        response = client.post(
            "/admin-duty/dynamic/api/hint",
            json={"session_id": session_id},
        )
        assert response.status_code == 200
        assert response.json()["progress"]["hints_used"] == expected_used

    exhausted = client.post(
        "/admin-duty/dynamic/api/hint",
        json={"session_id": session_id},
    )
    assert exhausted.status_code == 409
    assert exhausted.json() == {
        "detail": "Wykorzystano wszystkie dostępne podpowiedzi."
    }

    ended = client.post(
        "/admin-duty/dynamic/api/end",
        json={"session_id": session_id},
    )
    assert ended.status_code == 200
    rejected = client.post(
        "/admin-duty/dynamic/api/hint",
        json={"session_id": session_id},
    )
    assert rejected.status_code == 409
    assert rejected.json()["detail"] == (
        "Operacja jest dostępna wyłącznie dla aktywnej sesji."
    )


def test_public_infrastructure_tracks_runtime_without_fault_leaks(api_context):
    started = start_easy(seed=1).json()
    session_id = started["session_id"]
    infrastructure = started["infrastructure"]
    service_nodes = [
        node for node in infrastructure["nodes"] if node["type"] == "service"
    ]

    assert len(service_nodes) == 1
    assert service_nodes[0]["status"] == "failed"
    assert infrastructure["links"] == [
        {
            "source": service_nodes[0]["parent_id"],
            "target": service_nodes[0]["id"],
            "label": "uruchamia",
        }
    ]

    restarted = client.post(
        "/admin-duty/dynamic/api/command",
        json={
            "session_id": session_id,
            "command": f"systemctl restart {service_nodes[0]['id']}",
        },
    )
    assert restarted.status_code == 200

    current = client.get(f"/admin-duty/dynamic/api/sessions/{session_id}").json()
    current_service = next(
        node
        for node in current["infrastructure"]["nodes"]
        if node["id"] == service_nodes[0]["id"]
    )
    assert current_service["status"] == "running"
    current_signal = next(
        signal
        for signal in current["monitoring"]["signals"]
        if signal["resource_id"] == service_nodes[0]["id"]
    )
    assert current_signal["status"] == "running"
    assert current_signal["severity"] == "ok"


def test_public_game_map_matches_selected_component_without_internal_wrapper(
    api_context,
):
    started = start_easy(seed=1).json()
    definition = api_context["scenarios"].get(UUID(started["scenario_id"]))
    public_map = started["game_map"]

    assert public_map["id"] == definition.initial_world_state.map.map_id
    assert public_map["version"] == definition.initial_world_state.map.component_version
    assert public_map["width"] == 1800
    assert public_map["height"] == 1100
    assert len(public_map["objects"]) >= 30
    assert {sector["id"] for sector in public_map["sectors"]} == {
        "entry",
        "operations",
        "observability",
        "data-hall",
        "support",
    }
    assert public_map["collision_zones"]
    assert "snapshot" not in public_map
    assert "parameters" not in str(public_map)
    assert "capability_id" not in str(public_map)


def test_datacenter_map_survives_start_get_and_end_flow(api_context):
    started_response = start_easy(seed=0)
    assert started_response.status_code == 200
    started = started_response.json()
    game_map = started["game_map"]
    definition = api_context["scenarios"].get(UUID(started["scenario_id"]))
    assert game_map["id"] == definition.initial_world_state.map.map_id
    assert game_map["world_id"] == "datacenter-hall"
    assert game_map["theme"] == "datacenter-hall"
    assert game_map["width"] == 2200
    assert game_map["height"] == 1400
    assert len(game_map["objects"]) == 59
    assert {item["variant"] for item in game_map["objects"]} >= {
        "maintenance-cart", "fiber-frame", "service-crate", "power-distribution",
    }
    assert len(game_map["interactions"]) == 5

    current = client.get(
        f"/admin-duty/dynamic/api/sessions/{started['session_id']}"
    )
    assert current.status_code == 200
    assert current.json()["game_map"]["world_id"] == "datacenter-hall"
    assert current.json()["game_map"] == game_map

    ended = client.post(
        "/admin-duty/dynamic/api/end",
        json={"session_id": started["session_id"]},
    )
    assert ended.status_code == 200
    assert ended.json()["progress"]["status"] == "ended"


def test_unavailable_capability_maps_to_400(monkeypatch):
    class StatusOnlyGenerator(DeterministicIncidentGenerator):
        def generate(self, *args, **kwargs):
            definition = super().generate(*args, **kwargs)
            capabilities = definition.capabilities.model_copy(
                update={"command_capability_ids": ("systemd.status",)}
            )
            return definition.model_copy(update={"capabilities": capabilities})

    service, _, _ = build_service(generator=StatusOnlyGenerator())
    app.dependency_overrides[dynamic_router.get_dynamic_incident_service] = lambda: (
        service
    )
    monkeypatch.setattr(dynamic_router, "utc_now", lambda: FIXED_NOW)

    try:
        started = start_easy().json()
        response = client.post(
            "/admin-duty/dynamic/api/command",
            json={
                "session_id": started["session_id"],
                "command": "systemctl restart service-api",
            },
        )
        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


def test_dynamic_api_never_calls_host_execution(monkeypatch, api_context):
    def forbidden(*args, **kwargs):
        raise AssertionError("Próba wykonania operacji na hoście")

    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    started = start_easy().json()

    response = client.post(
        "/admin-duty/dynamic/api/command",
        json={
            "session_id": started["session_id"],
            "command": "systemctl status service-api",
        },
    )

    assert response.status_code == 200


def test_shared_admin_duty_lobby_still_responds(api_context):
    response = client.get("/admin-duty/")

    assert response.status_code == 200
    assert "Dyżur administratora" in response.text


def test_virtual_editor_api_round_trip_and_session_isolation(api_context):
    first = start_easy().json()["session_id"]
    second = start_easy().json()["session_id"]
    payload = {"session_id": first, "path": "/etc/os-release", "content": "test-host\n"}
    saved = client.post("/admin-duty/dynamic/api/file", json=payload)
    assert saved.status_code == 200
    assert saved.json()["success"]
    opened = client.post(
        "/admin-duty/dynamic/api/command",
        json={"session_id": first, "command": "nano /etc/os-release"},
    )
    assert opened.json()["editor"] == {
        "path": "/etc/os-release",
        "content": "test-host\n",
    }
    other = client.post(
        "/admin-duty/dynamic/api/command",
        json={"session_id": second, "command": "cat /etc/os-release"},
    )
    assert other.json()["output"] != "test-host"
    client.post("/admin-duty/dynamic/api/end", json={"session_id": first})
    assert client.post("/admin-duty/dynamic/api/file", json=payload).status_code == 409
    payload["session_id"] = str(uuid4())
    assert client.post("/admin-duty/dynamic/api/file", json=payload).status_code == 404


@pytest.mark.parametrize(
    "updates",
    [
        {"content": "x" * 32769},
        {"path": ""},
        {"path": "x" * 1025},
        {"unexpected": True},
        {"session_id": "invalid"},
    ],
)
def test_virtual_editor_api_rejects_invalid_payload_without_mutation(
    api_context, updates
):
    session_id = start_easy().json()["session_id"]
    before = client.get(f"/admin-duty/dynamic/api/sessions/{session_id}").json()
    payload = {
        "session_id": session_id,
        "path": "/etc/os-release",
        "content": "test-host\n",
        **updates,
    }
    response = client.post("/admin-duty/dynamic/api/file", json=payload)
    assert response.status_code == 422
    assert client.get(f"/admin-duty/dynamic/api/sessions/{session_id}").json() == before
