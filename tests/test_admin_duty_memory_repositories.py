from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.runtime import (
    SessionStatus,
    create_session_runtime,
    touch_session,
)
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.repositories import (
    SESSION_TTL,
    InMemoryScenarioRepository,
    InMemorySessionRepository,
    ScenarioConflictError,
    SessionConflictError,
    SessionLimitError,
    SessionNotFoundError,
)

FIXED_NOW = datetime(2026, 8, 25, 20, 0, tzinfo=UTC)
LATER = FIXED_NOW + timedelta(minutes=1)


def build_definition():
    return DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY,
        seed=123,
        now=FIXED_NOW,
    )


def test_scenario_repository_is_idempotent_but_rejects_replacement():
    repository = InMemoryScenarioRepository()
    definition = build_definition()
    changed_presentation = definition.presentation.model_copy(
        update={"title": "Inny incydent"}
    )
    changed = definition.model_copy(
        update={"presentation": changed_presentation}
    )

    repository.save(definition)
    repository.save(definition)

    assert repository.exists(definition.scenario_id)
    assert repository.get(definition.scenario_id) is definition

    with pytest.raises(ScenarioConflictError):
        repository.save(changed)


def test_session_repository_deep_copies_on_save_and_get():
    definition = build_definition()
    repository = InMemorySessionRepository()
    original = create_session_runtime(definition, now=FIXED_NOW)
    repository.save(original, now=FIXED_NOW)

    original.world_state.resources["service-api"].current_state = "running"
    first = repository.get(original.session_id, now=FIXED_NOW)
    first.world_state.resources["service-api"].current_state = "running"
    second = repository.get(original.session_id, now=FIXED_NOW)

    assert second.world_state.resources["service-api"].current_state == "failed"
    assert first.world_state is not second.world_state
    assert first.completed_objective_ids is not second.completed_objective_ids


def test_session_update_uses_optimistic_revision():
    definition = build_definition()
    repository = InMemorySessionRepository()
    initial = create_session_runtime(definition, now=FIXED_NOW)
    repository.save(initial, now=FIXED_NOW)
    first = repository.get(initial.session_id, now=FIXED_NOW)
    stale = repository.get(initial.session_id, now=FIXED_NOW)

    touch_session(first, now=LATER)
    repository.update(first, expected_revision=0, now=LATER)
    touch_session(stale, now=LATER)

    with pytest.raises(SessionConflictError):
        repository.update(stale, expected_revision=0, now=LATER)

    stored = repository.get(initial.session_id, now=LATER)
    assert stored.revision == 1


def test_session_expires_exactly_at_ttl_boundary():
    definition = build_definition()
    repository = InMemorySessionRepository()
    state = create_session_runtime(definition, now=FIXED_NOW)
    repository.save(state, now=FIXED_NOW)

    expired = repository.cleanup_expired(now=FIXED_NOW + SESSION_TTL)

    assert [item.session_id for item in expired] == [state.session_id]

    with pytest.raises(SessionNotFoundError):
        repository.get(state.session_id, now=FIXED_NOW + SESSION_TTL)


def test_cleanup_runs_before_session_limit_check():
    definition = build_definition()
    repository = InMemorySessionRepository(max_sessions=1)
    expired = create_session_runtime(definition, now=FIXED_NOW)
    repository.save(expired, now=FIXED_NOW)
    current_time = FIXED_NOW + SESSION_TTL
    replacement = create_session_runtime(
        definition,
        session_id=uuid4(),
        now=current_time,
    )

    repository.save(replacement, now=current_time)

    assert repository.get(replacement.session_id, now=current_time)


@pytest.mark.parametrize("status", list(SessionStatus))
def test_session_limit_covers_every_non_expired_record(status):
    definition = build_definition()
    repository = InMemorySessionRepository(max_sessions=1)
    first = create_session_runtime(definition, now=FIXED_NOW)
    second = create_session_runtime(
        definition,
        session_id=uuid4(),
        now=FIXED_NOW,
    )
    first.status = status
    repository.save(first, now=FIXED_NOW)

    with pytest.raises(SessionLimitError):
        repository.save(second, now=FIXED_NOW)
