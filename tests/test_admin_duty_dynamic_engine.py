from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.admin_duty.domain import engine as engine_module
from app.admin_duty.domain.definition import (
    CompletionCondition,
    ConditionOperator,
    IncidentDefinition,
    Objective,
)
from app.admin_duty.domain.engine import (
    DynamicIncidentEngine,
    DynamicIncidentEngineError,
    ResourceAttributeUpdate,
    ResourceStateUpdate,
)
from app.admin_duty.domain.objectives import ObjectiveEvaluationError
from app.admin_duty.domain.progress import (
    SessionProgress,
    SessionProgressConsistencyError,
)
from app.admin_duty.domain.runtime import (
    InactiveSessionError,
    SessionRuntimeState,
    SessionStatus,
    create_session_runtime,
)
from tests.test_admin_duty_incident_definition import build_incident_definition

FIXED_NOW = datetime(2026, 8, 25, 12, 0, tzinfo=UTC)
LATER = FIXED_NOW + timedelta(minutes=1)


def build_condition(
    *,
    field: str = "current_state",
    operator: ConditionOperator = ConditionOperator.EQUALS,
    expected="active",
) -> CompletionCondition:
    return CompletionCondition(
        resource_id="service-api",
        field=field,
        operator=operator,
        expected=expected,
    )


def build_objective(
    objective_id: str,
    *,
    condition: CompletionCondition | None = None,
    required: bool = True,
    order: int = 1,
) -> Objective:
    return Objective(
        objective_id=objective_id,
        label=f"Cel {objective_id}",
        required=required,
        completion_condition=condition or build_condition(),
        order=order,
    )


def build_definition(
    objectives: tuple[Objective, ...] | None = None,
) -> IncidentDefinition:
    definition = build_incident_definition()
    return definition.model_copy(
        update={
            "objectives": objectives
            or (build_objective("restore-service"),)
        }
    )


def build_context(
    objectives: tuple[Objective, ...] | None = None,
    *,
    session_id=None,
):
    definition = build_definition(objectives)
    state = create_session_runtime(
        definition,
        session_id=session_id,
        now=FIXED_NOW,
    )
    return definition, state, DynamicIncidentEngine()


def test_resource_state_update_runs_full_engine_flow():
    definition, state, engine = build_context()

    progress = engine.execute(
        definition,
        state,
        ResourceStateUpdate(
            resource_id="service-api",
            new_state="active",
        ),
        now=LATER,
    )

    assert state.world_state.resources["service-api"].current_state == "active"
    assert state.completed_objective_ids == {"restore-service"}
    assert state.status is SessionStatus.COMPLETED
    assert state.revision == 1
    assert state.last_activity == LATER
    assert progress.mission_complete is True
    assert progress.status is SessionStatus.COMPLETED


def test_resource_attribute_update_changes_existing_attribute():
    definition, state, engine = build_context()

    progress = engine.execute(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id="service-api",
            attribute="port",
            value=8200,
        ),
        now=LATER,
    )

    service = state.world_state.resources["service-api"]
    assert service.attributes["port"] == 8200
    assert state.status is SessionStatus.ACTIVE
    assert progress.score == state.score


def test_resource_attribute_update_can_add_attribute():
    definition, state, engine = build_context()

    engine.execute(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id="service-api",
            attribute="healthcheck",
            value="passing",
        ),
        now=LATER,
    )

    assert (
        state.world_state.resources["service-api"].attributes["healthcheck"]
        == "passing"
    )


@pytest.mark.parametrize(
    "action",
    [
        ResourceStateUpdate(
            resource_id="service-api",
            new_state="failed",
        ),
        ResourceAttributeUpdate(
            resource_id="service-api",
            attribute="manager",
            value="systemd",
        ),
    ],
)
def test_no_op_does_not_change_runtime_or_evaluate_objectives(
    action,
    monkeypatch,
):
    definition, state, engine = build_context()
    state.completed_objective_ids.add("restore-service")
    before = state.model_dump_json()

    def fail_evaluation(*args, **kwargs):
        raise AssertionError("Evaluator nie powinien zostać wywołany.")

    monkeypatch.setattr(engine_module, "evaluate_objectives", fail_evaluation)

    progress = engine.execute(definition, state, action, now=LATER)

    assert state.model_dump_json() == before
    assert state.revision == 0
    assert state.last_activity == FIXED_NOW
    assert state.completed_objective_ids == {"restore-service"}
    assert progress.revision == 0


def test_no_op_still_validates_timestamp_before_detection():
    definition, state, engine = build_context()
    action = ResourceStateUpdate(
        resource_id="service-api",
        new_state="failed",
    )

    with pytest.raises(ValueError, match="nie może cofać"):
        engine.execute(
            definition,
            state,
            action,
            now=FIXED_NOW - timedelta(seconds=1),
        )

    assert state.revision == 0
    assert state.last_activity == FIXED_NOW


def test_missing_resource_is_rejected_without_mutation():
    definition, state, engine = build_context()
    before = state.model_dump_json()

    with pytest.raises(DynamicIncidentEngineError, match="nie istnieje"):
        engine.execute(
            definition,
            state,
            ResourceStateUpdate(
                resource_id="missing-service",
                new_state="active",
            ),
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_scenario_mismatch_is_rejected_without_mutation():
    definition, state, engine = build_context()
    state.scenario_id = uuid4()
    before = state.model_dump_json()

    with pytest.raises(DynamicIncidentEngineError, match="różne scenario_id"):
        engine.execute(
            definition,
            state,
            ResourceStateUpdate(
                resource_id="service-api",
                new_state="active",
            ),
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_invalid_timestamp_is_rejected_without_mutation():
    definition, state, engine = build_context()
    before = state.model_dump_json()

    with pytest.raises(ValueError, match="musi zawierać strefę czasową"):
        engine.execute(
            definition,
            state,
            ResourceStateUpdate(
                resource_id="service-api",
                new_state="active",
            ),
            now=datetime(2026, 8, 25, 12, 1),
        )

    assert state.model_dump_json() == before


@pytest.mark.parametrize(
    "status",
    [SessionStatus.COMPLETED, SessionStatus.ENDED],
)
def test_inactive_session_rejects_action_without_mutation(status):
    definition, state, engine = build_context()
    state.status = status
    before = state.model_dump_json()

    with pytest.raises(InactiveSessionError):
        engine.execute(
            definition,
            state,
            ResourceStateUpdate(
                resource_id="service-api",
                new_state="active",
            ),
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_required_and_optional_objectives_are_synchronized():
    objectives = (
        build_objective("restore-service"),
        build_objective(
            "identify-manager",
            condition=build_condition(
                field="attributes.manager",
                expected="systemd",
            ),
            required=False,
            order=2,
        ),
    )
    definition, state, engine = build_context(objectives)

    progress = engine.execute(
        definition,
        state,
        ResourceStateUpdate(
            resource_id="service-api",
            new_state="active",
        ),
        now=LATER,
    )

    assert state.completed_objective_ids == {
        "restore-service",
        "identify-manager",
    }
    assert progress.completed_objectives == 2
    assert progress.mission_complete is True


def test_session_stays_active_when_required_objective_is_incomplete():
    definition, state, engine = build_context()

    progress = engine.execute(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id="service-api",
            attribute="owner",
            value="operations",
        ),
        now=LATER,
    )

    assert state.completed_objective_ids == set()
    assert state.status is SessionStatus.ACTIVE
    assert progress.status is SessionStatus.ACTIVE
    assert progress.mission_complete is False


def test_returned_progress_matches_final_runtime():
    definition, state, engine = build_context()

    progress = engine.execute(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id="service-api",
            attribute="owner",
            value="operations",
        ),
        now=LATER,
    )

    assert isinstance(progress, SessionProgress)
    assert progress.scenario_id == state.scenario_id
    assert progress.session_id == state.session_id
    assert progress.status is state.status
    assert progress.score == state.score
    assert progress.revision == state.revision


def test_engine_does_not_mutate_incident_definition():
    definition, state, engine = build_context()
    definition_before = definition.model_dump_json()

    engine.execute(
        definition,
        state,
        ResourceStateUpdate(
            resource_id="service-api",
            new_state="active",
        ),
        now=LATER,
    )

    assert definition.model_dump_json() == definition_before


def test_sessions_remain_independent():
    definition = build_definition()
    first = create_session_runtime(definition, now=FIXED_NOW)
    second = create_session_runtime(definition, now=FIXED_NOW)
    engine = DynamicIncidentEngine()

    engine.execute(
        definition,
        first,
        ResourceStateUpdate(
            resource_id="service-api",
            new_state="active",
        ),
        now=LATER,
    )

    assert first.status is SessionStatus.COMPLETED
    assert second.status is SessionStatus.ACTIVE
    assert second.world_state.resources["service-api"].current_state == "failed"
    assert second.completed_objective_ids == set()
    assert second.revision == 0


def test_runtime_json_round_trip_after_engine_operation():
    definition, state, engine = build_context()
    engine.execute(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id="service-api",
            attribute="owner",
            value="operations",
        ),
        now=LATER,
    )

    restored = SessionRuntimeState.model_validate_json(state.model_dump_json())

    assert restored == state


def test_invalid_action_type_is_rejected_without_mutation():
    definition, state, engine = build_context()
    before = state.model_dump_json()

    with pytest.raises(DynamicIncidentEngineError, match="Nieobsługiwany typ"):
        engine.execute(
            definition,
            state,
            {"resource_id": "service-api"},
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_invalid_action_value_does_not_leave_partial_mutation():
    definition, state, engine = build_context()
    before = state.model_dump_json()
    action = ResourceAttributeUpdate.model_construct(
        resource_id="service-api",
        attribute="invalid",
        value=object(),
    )

    with pytest.raises(ValidationError):
        engine.execute(definition, state, action, now=LATER)

    assert state.model_dump_json() == before


def test_objective_evaluation_error_does_not_leave_partial_mutation():
    definition = build_incident_definition()
    state = create_session_runtime(definition, now=FIXED_NOW)
    engine = DynamicIncidentEngine()
    before = state.model_dump_json()

    with pytest.raises(ObjectiveEvaluationError, match="Nieobsługiwane pole"):
        engine.execute(
            definition,
            state,
            ResourceStateUpdate(
                resource_id="service-api",
                new_state="active",
            ),
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_progress_error_does_not_leave_partial_mutation(monkeypatch):
    definition, state, engine = build_context()
    before = state.model_dump_json()
    real_get_session_progress = engine_module.get_session_progress
    calls = 0

    def fail_progress(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise SessionProgressConsistencyError("Niespójna projekcja.")
        return real_get_session_progress(*args, **kwargs)

    monkeypatch.setattr(engine_module, "get_session_progress", fail_progress)

    with pytest.raises(SessionProgressConsistencyError):
        engine.execute(
            definition,
            state,
            ResourceStateUpdate(
                resource_id="service-api",
                new_state="active",
            ),
            now=LATER,
        )

    assert state.model_dump_json() == before
    assert calls == 2


def test_same_inputs_produce_identical_runtime_and_progress():
    definition = build_definition()
    session_id = uuid4()
    first = create_session_runtime(
        definition,
        session_id=session_id,
        now=FIXED_NOW,
    )
    second = create_session_runtime(
        definition,
        session_id=session_id,
        now=FIXED_NOW,
    )
    action = ResourceStateUpdate(
        resource_id="service-api",
        new_state="active",
    )
    engine = DynamicIncidentEngine()

    first_progress = engine.execute(
        definition,
        first,
        action,
        now=LATER,
    )
    second_progress = engine.execute(
        definition,
        second,
        action,
        now=LATER,
    )

    assert first == second
    assert first_progress == second_progress


def test_execute_command_accounts_world_change_and_objective_in_one_revision():
    definition, state, engine = build_context()
    state.revision = 7
    state.commands_used = 3
    state.score = 900

    progress = engine.execute_command(
        definition,
        state,
        ResourceStateUpdate(
            resource_id="service-api",
            new_state="active",
        ),
        command_cost=5,
        now=LATER,
    )

    assert state.world_state.resources["service-api"].current_state == "active"
    assert state.commands_used == 4
    assert state.score == 895
    assert state.completed_objective_ids == {"restore-service"}
    assert state.status is SessionStatus.COMPLETED
    assert state.last_activity == LATER
    assert state.revision == 8
    assert progress.revision == 8
    assert progress.mission_complete is True


def test_execute_command_score_does_not_fall_below_zero():
    definition, state, engine = build_context()
    state.score = 20

    engine.execute_command(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id="service-api",
            attribute="owner",
            value="operations",
        ),
        command_cost=100,
        now=LATER,
    )

    assert state.score == 0
    assert state.commands_used == 1
    assert state.revision == 1


def test_execute_command_accepts_zero_cost_as_logical_mutation():
    definition, state, engine = build_context()

    engine.execute_command(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id="service-api",
            attribute="owner",
            value="operations",
        ),
        command_cost=0,
        now=LATER,
    )

    assert state.score == definition.scoring.initial_score
    assert state.commands_used == 1
    assert state.last_activity == LATER
    assert state.revision == 1


@pytest.mark.parametrize("command_cost", [-1, True, 1.5, "5"])
def test_invalid_command_cost_is_rejected_without_mutation(command_cost):
    definition, state, engine = build_context()
    before = state.model_dump_json()

    with pytest.raises(DynamicIncidentEngineError, match="Koszt komendy"):
        engine.execute_command(
            definition,
            state,
            ResourceStateUpdate(
                resource_id="service-api",
                new_state="active",
            ),
            command_cost=command_cost,
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_execute_command_world_no_op_still_updates_accounting_and_activity():
    definition, state, engine = build_context()

    progress = engine.execute_command(
        definition,
        state,
        ResourceStateUpdate(
            resource_id="service-api",
            new_state="failed",
        ),
        command_cost=5,
        now=LATER,
    )

    assert state.world_state.resources["service-api"].current_state == "failed"
    assert state.commands_used == 1
    assert state.score == 995
    assert state.last_activity == LATER
    assert state.revision == 1
    assert state.status is SessionStatus.ACTIVE
    assert progress.revision == 1


def test_execute_command_world_no_op_still_evaluates_objectives():
    objective = build_objective(
        "observe-failed-service",
        condition=build_condition(
            field="current_state",
            operator=ConditionOperator.EQUALS,
            expected="failed",
        ),
    )
    definition, state, engine = build_context((objective,))

    progress = engine.execute_command(
        definition,
        state,
        ResourceStateUpdate(
            resource_id="service-api",
            new_state="failed",
        ),
        command_cost=5,
        now=LATER,
    )

    assert state.completed_objective_ids == {"observe-failed-service"}
    assert state.status is SessionStatus.COMPLETED
    assert state.revision == 1
    assert progress.mission_complete is True


@pytest.mark.parametrize(
    "status",
    [SessionStatus.COMPLETED, SessionStatus.ENDED],
)
def test_execute_command_rejects_inactive_session_without_accounting(status):
    definition, state, engine = build_context()
    state.status = status
    before = state.model_dump_json()

    with pytest.raises(InactiveSessionError):
        engine.execute_command(
            definition,
            state,
            ResourceStateUpdate(
                resource_id="service-api",
                new_state="active",
            ),
            command_cost=5,
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_invalid_command_action_does_not_leave_partial_accounting():
    definition, state, engine = build_context()
    before = state.model_dump_json()
    action = ResourceAttributeUpdate.model_construct(
        resource_id="service-api",
        attribute="invalid",
        value=object(),
    )

    with pytest.raises(ValidationError):
        engine.execute_command(
            definition,
            state,
            action,
            command_cost=5,
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_runtime_json_round_trip_after_command_execution():
    definition, state, engine = build_context()
    engine.execute_command(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id="service-api",
            attribute="owner",
            value="operations",
        ),
        command_cost=5,
        now=LATER,
    )

    restored = SessionRuntimeState.model_validate_json(state.model_dump_json())

    assert restored == state
    assert restored.commands_used == 1
    assert restored.score == 995
    assert restored.revision == 1


def test_diagnostic_command_without_action_updates_accounting_not_world():
    definition, state, engine = build_context()
    world_before = state.world_state.model_dump_json()

    progress = engine.execute_command(
        definition,
        state,
        action=None,
        command_cost=5,
        now=LATER,
    )

    assert state.world_state.model_dump_json() == world_before
    assert state.commands_used == 1
    assert state.score == 995
    assert state.last_activity == LATER
    assert state.revision == 1
    assert state.discovered_fact_ids == set()
    assert progress.revision == 1


def test_plain_execute_rejects_missing_action_without_mutation():
    definition, state, engine = build_context()
    before = state.model_dump_json()

    with pytest.raises(DynamicIncidentEngineError, match="wymaga akcji"):
        engine.execute(definition, state, None, now=LATER)

    assert state.model_dump_json() == before


def test_diagnostic_command_without_action_still_evaluates_objectives():
    definition, state, engine = build_context()
    state.world_state.resources["service-api"].current_state = "active"
    world_before = state.world_state.model_dump_json()

    progress = engine.execute_command(
        definition,
        state,
        command_cost=0,
        now=LATER,
    )

    assert state.world_state.model_dump_json() == world_before
    assert state.completed_objective_ids == {"restore-service"}
    assert state.status is SessionStatus.COMPLETED
    assert state.revision == 1
    assert progress.mission_complete is True


def test_diagnostic_command_adds_multiple_unique_discovered_facts():
    definition, state, engine = build_context()

    engine.execute_command(
        definition,
        state,
        command_cost=5,
        discovered_fact_ids=(
            "service-status-inspected:service-api",
            "service-status-inspected:service-api",
            "service-manager-inspected:service-api",
        ),
        now=LATER,
    )

    assert state.discovered_fact_ids == {
        "service-status-inspected:service-api",
        "service-manager-inspected:service-api",
    }
    assert state.commands_used == 1
    assert state.revision == 1


def test_diagnostic_command_materializes_fact_iterable_before_mutation():
    definition, state, engine = build_context()
    facts = (
        fact_id
        for fact_id in (
            "service-status-inspected:service-api",
            "service-manager-inspected:service-api",
        )
    )

    engine.execute_command(
        definition,
        state,
        command_cost=5,
        discovered_fact_ids=facts,
        now=LATER,
    )

    assert state.discovered_fact_ids == {
        "service-status-inspected:service-api",
        "service-manager-inspected:service-api",
    }


@pytest.mark.parametrize(
    "discovered_fact_ids",
    [
        "single-fact",
        ("",),
        ("fact with spaces",),
        ("_private-fact",),
    ],
)
def test_invalid_discovered_facts_are_rejected_without_mutation(
    discovered_fact_ids,
):
    definition, state, engine = build_context()
    before = state.model_dump_json()

    with pytest.raises(DynamicIncidentEngineError):
        engine.execute_command(
            definition,
            state,
            command_cost=5,
            discovered_fact_ids=discovered_fact_ids,
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_diagnostic_evaluation_error_does_not_leave_partial_mutation():
    definition = build_incident_definition()
    state = create_session_runtime(definition, now=FIXED_NOW)
    engine = DynamicIncidentEngine()
    before = state.model_dump_json()

    with pytest.raises(ObjectiveEvaluationError, match="Nieobsługiwane pole"):
        engine.execute_command(
            definition,
            state,
            command_cost=5,
            discovered_fact_ids=("service-status-inspected:service-api",),
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_runtime_json_round_trip_after_diagnostic_command():
    definition, state, engine = build_context()
    engine.execute_command(
        definition,
        state,
        command_cost=5,
        discovered_fact_ids=("service-status-inspected:service-api",),
        now=LATER,
    )

    restored = SessionRuntimeState.model_validate_json(state.model_dump_json())

    assert restored == state
    assert restored.discovered_fact_ids == {
        "service-status-inspected:service-api"
    }


def test_action_models_are_frozen_and_forbid_extra_or_invalid_values():
    action = ResourceStateUpdate(
        resource_id="service-api",
        new_state="active",
    )

    with pytest.raises(ValidationError):
        action.new_state = "failed"

    with pytest.raises(ValidationError):
        ResourceStateUpdate(
            resource_id="service-api",
            new_state="active",
            unexpected=True,
        )

    with pytest.raises(ValidationError):
        ResourceAttributeUpdate(
            resource_id="service-api",
            attribute="invalid",
            value=object(),
        )


def test_engine_is_stateless():
    assert DynamicIncidentEngine().__dict__ == {}
