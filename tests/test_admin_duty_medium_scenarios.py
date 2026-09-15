from collections import Counter
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.admin_duty.components.scenarios import (
    MEDIUM_SCENARIO_CATEGORIES,
    build_medium_draft,
)
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.generation import (
    convert_draft_to_definition,
    validate_and_convert_draft,
)
from app.admin_duty.domain.progress import get_session_progress
from app.admin_duty.domain.runtime import create_session_runtime
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.repositories import (
    InMemoryScenarioRepository,
    InMemorySessionRepository,
)
from app.admin_duty.services import DynamicIncidentService

NOW = datetime(2026, 9, 8, 12, 0, tzinfo=UTC)


@pytest.mark.parametrize("category", MEDIUM_SCENARIO_CATEGORIES)
def test_each_medium_scenario_validates_and_reference_replay_completes(category):
    definition = validate_and_convert_draft(
        build_medium_draft(category, seed=23),
        created_at=NOW,
    )
    state = create_session_runtime(definition, now=NOW)
    service = DynamicCommandService()

    assert get_session_progress(definition, state).mission_complete is False
    assert state.status.value == "active"

    for index, step in enumerate(definition.solution, 1):
        result = service.execute(
            definition,
            state,
            step.input,
            now=NOW + timedelta(seconds=index),
        )
        if step.capability_id == "filesystem.edit":
            parameters = {field.key: field.value for field in step.parameters}
            result = service.save_file(
                definition,
                state,
                path=result.editor.path,
                content=parameters["content"],
                now=NOW + timedelta(seconds=index, milliseconds=500),
            )
        assert result.success is step.expected_success

    assert get_session_progress(definition, state).mission_complete
    assert state.status.value == "completed"


def test_medium_generation_is_deterministic_and_covers_full_curated_catalog():
    generator = DeterministicIncidentGenerator()
    categories = Counter()

    for seed in range(100):
        first = generator.generate(DifficultyLevel.MEDIUM, seed=seed, now=NOW)
        second = generator.generate(DifficultyLevel.MEDIUM, seed=seed, now=NOW)
        assert first.model_dump(exclude={"scenario_id"}) == second.model_dump(
            exclude={"scenario_id"}
        )
        categories[first.faults[0].parameters[0].value] += 1

    assert len(MEDIUM_SCENARIO_CATEGORIES) == 12
    assert set(categories) == set(MEDIUM_SCENARIO_CATEGORIES)
    assert max(categories.values()) <= 3 * min(categories.values())


def test_stale_systemd_unit_stays_broken_until_daemon_reload():
    definition = convert_draft_to_definition(
        build_medium_draft("systemd-stale-unit-config", seed=29),
        created_at=NOW,
    )
    state = create_session_runtime(definition, now=NOW)
    service = DynamicCommandService()
    edit_step = next(
        step for step in definition.solution if step.capability_id == "filesystem.edit"
    )
    editor = service.execute(
        definition,
        state,
        "ssh app-01",
        now=NOW + timedelta(seconds=1),
    )
    assert editor.success
    editor = service.execute(
        definition,
        state,
        edit_step.input,
        now=NOW + timedelta(seconds=2),
    )
    content = {field.key: field.value for field in edit_step.parameters}["content"]
    service.save_file(
        definition,
        state,
        path=editor.editor.path,
        content=content,
        now=NOW + timedelta(seconds=3),
    )
    service.execute(
        definition,
        state,
        "systemctl restart orders-api",
        now=NOW + timedelta(seconds=4),
    )

    assert state.world_state.resources["service-api"].current_state == "failed"
    assert get_session_progress(definition, state).mission_complete is False


def test_running_service_can_have_degraded_dependency_health_and_502_symptom():
    definition = convert_draft_to_definition(
        build_medium_draft("dependency-firewall-blocked", seed=31),
        created_at=NOW,
    )
    state = create_session_runtime(definition, now=NOW)
    api = state.world_state.resources["service-api"]
    proxy = state.world_state.resources["service-proxy"]
    endpoint = state.world_state.resources["endpoint-portal"]

    assert api.current_state == "running"
    assert api.attributes["public_health"] == "unhealthy"
    assert proxy.current_state == "running"
    assert proxy.attributes["public_health"] == "unhealthy"
    assert endpoint.current_state == "http-502"

    status = DynamicCommandService().execute(
        definition,
        state,
        "ssh app-01",
        now=NOW + timedelta(seconds=1),
    )
    assert status.prompt == "operator@app-01:~$"
    status = DynamicCommandService().execute(
        definition,
        state,
        "systemctl status orders-api",
        now=NOW + timedelta(seconds=2),
    )
    assert "Active: active (running)" in status.output


def test_medium_can_be_completed_by_alternative_state_based_solution():
    definition = convert_draft_to_definition(
        build_medium_draft("dependency-package-missing", seed=41),
        created_at=NOW,
    )
    state = create_session_runtime(definition, now=NOW)
    service = DynamicCommandService()
    commands = (
        "ssh app-01",
        "dnf install python3-psycopg2",
        "systemctl start orders-api",
        "ssh edge-01",
        "curl http://portal.internal",
    )

    for index, command in enumerate(commands, 1):
        service.execute(definition, state, command, now=NOW + timedelta(seconds=index))

    assert get_session_progress(definition, state).mission_complete
    assert tuple(record.command for record in state.command_history) == commands


def test_medium_public_projection_contains_allowlisted_dependency_data_only():
    service = DynamicIncidentService(
        generator=DeterministicIncidentGenerator(),
        scenario_repository=InMemoryScenarioRepository(),
        session_repository=InMemorySessionRepository(),
    )
    started = service.start_session(DifficultyLevel.MEDIUM, seed=1, now=NOW)
    payload = started.model_dump(mode="json", exclude_none=True)

    assert len(payload["infrastructure"]["nodes"]) >= 6
    assert any(
        link.get("label") == "zależy od" for link in payload["infrastructure"]["links"]
    )
    serialized = str(payload).casefold()
    for hidden in (
        "root_cause",
        "faults",
        "generation",
        "forbidden_public_terms",
    ):
        assert hidden not in serialized
    assert "reference_solution" not in serialized
    assert "generation_seed" not in serialized
    assert "post_incident" not in payload
    assert UUID(payload["scenario_id"])


def test_post_incident_report_is_available_only_after_completion():
    scenarios = InMemoryScenarioRepository()
    sessions = InMemorySessionRepository()
    service = DynamicIncidentService(
        generator=DeterministicIncidentGenerator(),
        scenario_repository=scenarios,
        session_repository=sessions,
    )
    started = service.start_session(DifficultyLevel.MEDIUM, seed=1, now=NOW)
    assert service.get_progress(started.session_id, now=NOW).post_incident is None
    definition = scenarios.get(started.scenario_id)

    current = NOW
    for step in definition.solution:
        current += timedelta(seconds=2)
        service.execute_command(started.session_id, step.input, now=current)

    report = service.get_progress(
        started.session_id,
        now=current + timedelta(seconds=1),
    ).post_incident
    assert report is not None
    assert report.root_cause
    assert report.affected_services
    assert report.commands_used
    assert report.repair_actions
    assert report.final_state
