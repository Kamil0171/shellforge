from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.admin_duty.domain.definition import (
    CompletionCondition,
    ConditionOperator,
    Objective,
)
from app.admin_duty.domain.progress import (
    SessionProgress,
    SessionProgressConsistencyError,
    get_session_progress,
)
from app.admin_duty.domain.runtime import (
    SessionStatus,
    create_session_runtime,
)
from tests.test_admin_duty_incident_definition import build_incident_definition

FIXED_NOW = datetime(2026, 8, 24, 16, 0, tzinfo=UTC)


def build_objective(
    objective_id: str,
    *,
    order: int,
    required: bool = True,
) -> Objective:
    return Objective(
        objective_id=objective_id,
        label=f"Cel {objective_id}",
        required=required,
        completion_condition=CompletionCondition(
            resource_id="service-api",
            field="state",
            operator=ConditionOperator.EQUALS,
            expected="active",
        ),
        order=order,
    )


def build_progress_context():
    definition = build_incident_definition()
    definition = definition.model_copy(
        update={
            "objectives": (
                build_objective("verify-endpoint", order=2),
                build_objective("restore-service", order=2),
                build_objective(
                    "document-incident",
                    order=1,
                    required=False,
                ),
            )
        }
    )
    state = create_session_runtime(definition, now=FIXED_NOW)
    return definition, state


def test_session_progress_contains_session_data_and_all_objectives():
    definition, state = build_progress_context()
    state.score = 875
    state.commands_used = 4
    state.hints_used = 1
    state.solution_viewed = True
    state.status = SessionStatus.COMPLETED
    state.revision = 7
    state.completed_objective_ids.add("restore-service")

    progress = get_session_progress(definition, state)

    assert progress.scenario_id == definition.scenario_id
    assert progress.session_id == state.session_id
    assert progress.status is SessionStatus.COMPLETED
    assert progress.score == 875
    assert progress.commands_used == 4
    assert progress.hints_used == 1
    assert progress.solution_viewed is True
    assert progress.revision == 7
    assert progress.completed_objectives == 1
    assert progress.total_objectives == 3
    assert len(progress.objectives) == 3


def test_objectives_are_sorted_by_order_and_id_with_completion_flags():
    definition, state = build_progress_context()
    state.completed_objective_ids.add("verify-endpoint")

    progress = get_session_progress(definition, state)

    assert [objective.objective_id for objective in progress.objectives] == [
        "document-incident",
        "restore-service",
        "verify-endpoint",
    ]
    assert [objective.completed for objective in progress.objectives] == [
        False,
        False,
        True,
    ]
    assert [objective.required for objective in progress.objectives] == [
        False,
        True,
        True,
    ]


def test_mission_complete_requires_all_required_objectives():
    definition, state = build_progress_context()
    state.completed_objective_ids.add("restore-service")

    incomplete_progress = get_session_progress(definition, state)

    state.completed_objective_ids.add("verify-endpoint")
    complete_progress = get_session_progress(definition, state)

    assert incomplete_progress.mission_complete is False
    assert complete_progress.mission_complete is True
    assert complete_progress.status is SessionStatus.ACTIVE


def test_optional_objectives_do_not_block_mission_completion():
    definition, state = build_progress_context()
    state.completed_objective_ids.update(
        {"restore-service", "verify-endpoint"}
    )

    progress = get_session_progress(definition, state)
    optional_progress = progress.objectives[0]

    assert optional_progress.objective_id == "document-incident"
    assert optional_progress.completed is False
    assert progress.completed_objectives == 2
    assert progress.total_objectives == 3
    assert progress.mission_complete is True


def test_scenario_id_mismatch_is_rejected():
    definition, state = build_progress_context()
    state.scenario_id = uuid4()

    with pytest.raises(
        SessionProgressConsistencyError,
        match="różne scenario_id",
    ):
        get_session_progress(definition, state)


def test_unknown_completed_objective_is_rejected():
    definition, state = build_progress_context()
    state.completed_objective_ids.add("unknown-objective")

    with pytest.raises(
        SessionProgressConsistencyError,
        match="unknown-objective",
    ):
        get_session_progress(definition, state)


def test_projection_does_not_mutate_definition_or_runtime():
    definition, state = build_progress_context()
    state.completed_objective_ids.add("restore-service")
    definition_before = definition.model_dump_json()
    state_before = state.model_dump_json()
    revision_before = state.revision
    last_activity_before = state.last_activity
    completed_before = state.completed_objective_ids.copy()

    get_session_progress(definition, state)

    assert definition.model_dump_json() == definition_before
    assert state.model_dump_json() == state_before
    assert state.revision == revision_before
    assert state.last_activity == last_activity_before
    assert state.completed_objective_ids == completed_before


def test_session_progress_is_deeply_immutable_and_forbids_extra_fields():
    definition, state = build_progress_context()
    progress = get_session_progress(definition, state)

    with pytest.raises(ValidationError):
        progress.score = 500

    with pytest.raises(ValidationError):
        progress.objectives[0].completed = True

    payload = progress.model_dump(mode="json")
    payload["unexpected"] = True

    with pytest.raises(ValidationError):
        SessionProgress.model_validate(payload)

    assert isinstance(progress.objectives, tuple)


def test_session_progress_json_round_trip():
    definition, state = build_progress_context()
    state.completed_objective_ids.update(
        {"restore-service", "verify-endpoint"}
    )

    progress = get_session_progress(definition, state)
    restored = SessionProgress.model_validate_json(progress.model_dump_json())

    assert restored == progress
    assert isinstance(restored.objectives, tuple)
