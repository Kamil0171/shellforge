from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.runtime import (
    SessionStatus,
    create_session_runtime,
)
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.repositories import (
    SESSION_TTL,
    InMemoryScenarioRepository,
    InMemorySessionRepository,
    SessionLimitError,
)
from app.admin_duty.services import DynamicIncidentService, PublicGameMap

FIXED_NOW = datetime(2026, 8, 25, 20, 0, tzinfo=UTC)


def build_service(*, max_sessions=500):
    scenarios = InMemoryScenarioRepository()
    sessions = InMemorySessionRepository(max_sessions=max_sessions)
    service = DynamicIncidentService(
        generator=DeterministicIncidentGenerator(),
        scenario_repository=scenarios,
        session_repository=sessions,
    )
    return service, scenarios, sessions


def test_service_get_progress_is_read_only():
    service, scenarios, sessions = build_service()
    started = service.start_session(
        DifficultyLevel.EASY,
        seed=123,
        now=FIXED_NOW,
    )
    before = sessions.get(started.session_id, now=FIXED_NOW)

    view = service.get_progress(
        started.session_id,
        now=FIXED_NOW + timedelta(minutes=1),
    )
    after = sessions.get(
        started.session_id,
        now=FIXED_NOW + timedelta(minutes=1),
    )

    assert view.progress.revision == 0
    assert after.last_activity == before.last_activity
    assert after.revision == before.revision
    assert isinstance(view.game_map, PublicGameMap)
    definition = scenarios.get(started.scenario_id)
    assert view.game_map.id == definition.initial_world_state.map.map_id
    assert "snapshot" not in PublicGameMap.model_fields
    assert "parameters" not in PublicGameMap.model_fields


def test_service_cleanup_keeps_scenario_used_by_another_session():
    service, scenarios, sessions = build_service()
    started = service.start_session(
        DifficultyLevel.EASY,
        now=FIXED_NOW,
    )
    definition = scenarios.get(started.scenario_id)
    active_time = FIXED_NOW + timedelta(minutes=30)
    shared = create_session_runtime(
        definition,
        session_id=uuid4(),
        now=active_time,
    )
    sessions.save(shared, now=active_time)
    cleanup_time = FIXED_NOW + SESSION_TTL

    view = service.get_progress(shared.session_id, now=cleanup_time)

    assert view.progress.session_id == shared.session_id
    assert scenarios.exists(definition.scenario_id)


def test_failed_session_save_rolls_back_generated_scenario():
    service, scenarios, sessions = build_service(max_sessions=1)
    service.start_session(DifficultyLevel.EASY, now=FIXED_NOW)

    class RecordingGenerator(DeterministicIncidentGenerator):
        generated = None

        def generate(self, *args, **kwargs):
            self.generated = super().generate(*args, **kwargs)
            return self.generated

    generator = RecordingGenerator()
    limited_service = DynamicIncidentService(
        generator=generator,
        scenario_repository=scenarios,
        session_repository=sessions,
    )

    with pytest.raises(SessionLimitError):
        limited_service.start_session(DifficultyLevel.EASY, now=FIXED_NOW)

    assert generator.generated is not None
    assert not scenarios.exists(generator.generated.scenario_id)


def test_end_session_preserves_runtime_and_marks_ended():
    service, _, sessions = build_service()
    started = service.start_session(
        DifficultyLevel.EASY,
        seed=1,
        now=FIXED_NOW,
    )
    command_time = FIXED_NOW + timedelta(minutes=1)
    service.execute_command(
        started.session_id,
        "systemctl status service-api",
        now=command_time,
    )

    ended = service.end_session(
        started.session_id,
        now=command_time + timedelta(minutes=1),
    )
    state = sessions.get(
        started.session_id,
        now=command_time + timedelta(minutes=1),
    )

    assert ended.progress.status is SessionStatus.ENDED
    assert state.commands_used == 1
    assert state.discovered_fact_ids == {
        "service-status-inspected:service-api"
    }
    assert state.revision == 2


def test_request_hint_is_atomic_and_accounts_cost():
    service, scenarios, sessions = build_service()
    started = service.start_session(
        DifficultyLevel.EASY,
        seed=123,
        now=FIXED_NOW,
    )
    definition = scenarios.get(started.scenario_id)
    hint_time = FIXED_NOW + timedelta(minutes=1)

    result = service.request_hint(started.session_id, now=hint_time)
    state = sessions.get(started.session_id, now=hint_time)

    assert result.hint.text == definition.hints[0].text
    assert result.revealed_hints == (result.hint,)
    assert result.progress.hints_used == 1
    assert result.progress.revision == 1
    assert state.revision == 1
    assert state.last_activity == hint_time
    assert state.score == max(0, definition.scoring.initial_score - result.hint.cost)
