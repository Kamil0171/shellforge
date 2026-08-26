from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.admin_duty.domain.definition import (
    CompletionCondition,
    ConditionOperator,
    IncidentDefinition,
    Objective,
)
from app.admin_duty.domain.engine import (
    DynamicIncidentEngine,
    ResourceStateUpdate,
)
from app.admin_duty.domain.progress import get_session_progress
from app.admin_duty.domain.runtime import (
    InactiveSessionError,
    SessionRuntimeState,
    SessionStatus,
    create_session_runtime,
)
from app.admin_duty.dynamic_commands import (
    CommandExecutionError,
    CommandExecutionResult,
    get_systemd_service_status,
    restart_systemd_service,
)
from tests.test_admin_duty_incident_definition import build_incident_definition

FIXED_NOW = datetime(2026, 8, 25, 14, 0, tzinfo=UTC)
LATER = FIXED_NOW + timedelta(minutes=1)


def build_definition() -> IncidentDefinition:
    definition = build_incident_definition()
    capabilities = definition.capabilities.model_copy(
        update={
            "command_capability_ids": (
                *definition.capabilities.command_capability_ids,
                "systemd.status",
            )
        }
    )
    objective = Objective(
        objective_id="restart-service",
        label="Uruchom ponownie usługę",
        completion_condition=CompletionCondition(
            resource_id="service-api",
            field="current_state",
            operator=ConditionOperator.EQUALS,
            expected="running",
        ),
        order=1,
    )
    return definition.model_copy(
        update={
            "capabilities": capabilities,
            "objectives": (objective,),
        }
    )


def build_context():
    definition = build_definition()
    state = create_session_runtime(definition, now=FIXED_NOW)
    return definition, state


def test_restart_systemd_service_runs_complete_dynamic_flow():
    definition, state = build_context()

    result = restart_systemd_service(
        definition,
        state,
        resource_id="service-api",
        now=LATER,
    )

    assert result.success is True
    assert result.output == (
        "Usługa service-api została ponownie uruchomiona."
    )
    assert state.world_state.resources["service-api"].current_state == "running"
    assert state.completed_objective_ids == {"restart-service"}
    assert state.status is SessionStatus.COMPLETED
    assert state.revision == 1
    assert state.last_activity == LATER
    assert state.commands_used == 1
    assert state.score == (
        definition.scoring.initial_score - definition.scoring.command_cost
    )
    assert result.progress.status is SessionStatus.COMPLETED
    assert result.progress.mission_complete is True
    assert result.progress.revision == state.revision


def test_handler_delegates_resource_state_update_without_direct_mutation():
    definition, state = build_context()
    before = state.model_dump_json()

    class RecordingEngine(DynamicIncidentEngine):
        def __init__(self):
            self.action = None
            self.command_cost = None

        def execute_command(
            self,
            definition,
            state,
            action,
            *,
            command_cost,
            now=None,
        ):
            self.action = action
            self.command_cost = command_cost
            return get_session_progress(definition, state)

    engine = RecordingEngine()

    restart_systemd_service(
        definition,
        state,
        resource_id="service-api",
        engine=engine,
        now=LATER,
    )

    assert engine.action == ResourceStateUpdate(
        resource_id="service-api",
        new_state="running",
    )
    assert engine.command_cost == definition.scoring.command_cost
    assert state.model_dump_json() == before


def test_restart_of_running_service_is_full_no_op():
    definition, state = build_context()
    service = state.world_state.resources["service-api"]
    service.current_state = "running"
    state.completed_objective_ids.add("restart-service")

    result = restart_systemd_service(
        definition,
        state,
        resource_id="service-api",
        now=LATER,
    )

    assert result.success is True
    assert result.output == "Usługa service-api już działa."
    assert service.current_state == "running"
    assert state.commands_used == 1
    assert state.score == 995
    assert state.revision == 1
    assert state.last_activity == LATER
    assert state.completed_objective_ids == {"restart-service"}
    assert state.status is SessionStatus.COMPLETED
    assert result.progress.mission_complete is True


def test_no_op_still_propagates_timestamp_error_from_engine():
    definition, state = build_context()
    state.world_state.resources["service-api"].current_state = "running"

    with pytest.raises(ValueError, match="nie może cofać"):
        restart_systemd_service(
            definition,
            state,
            resource_id="service-api",
            now=FIXED_NOW - timedelta(seconds=1),
        )

    assert state.revision == 0
    assert state.last_activity == FIXED_NOW


def test_missing_restart_capability_is_rejected_without_mutation():
    definition, state = build_context()
    capabilities = definition.capabilities.model_copy(
        update={
            "command_capability_ids": (
                "filesystem.read",
                "systemd.inspect",
            )
        }
    )
    definition = definition.model_copy(update={"capabilities": capabilities})
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError, match="capability"):
        restart_systemd_service(
            definition,
            state,
            resource_id="service-api",
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_missing_resource_is_rejected_without_mutation():
    definition, state = build_context()
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError, match="nie istnieje"):
        restart_systemd_service(
            definition,
            state,
            resource_id="missing-service",
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_non_service_resource_is_rejected_without_mutation():
    definition, state = build_context()
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError, match="nie jest usługą"):
        restart_systemd_service(
            definition,
            state,
            resource_id="host-app",
            now=LATER,
        )

    assert state.model_dump_json() == before


@pytest.mark.parametrize("manager", [None, "supervisord"])
def test_service_without_systemd_manager_is_rejected(manager):
    definition, state = build_context()
    service = state.world_state.resources["service-api"]
    attributes = service.attributes.copy()

    if manager is None:
        attributes.pop("manager")
    else:
        attributes["manager"] = manager

    service.attributes = attributes
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError, match="zarządzana przez systemd"):
        restart_systemd_service(
            definition,
            state,
            resource_id="service-api",
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_scenario_mismatch_is_rejected_without_mutation():
    definition, state = build_context()
    state.scenario_id = uuid4()
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError, match="różne scenario_id"):
        restart_systemd_service(
            definition,
            state,
            resource_id="service-api",
            now=LATER,
        )

    assert state.model_dump_json() == before


@pytest.mark.parametrize(
    "status",
    [SessionStatus.COMPLETED, SessionStatus.ENDED],
)
def test_inactive_session_error_from_engine_is_not_hidden(status):
    definition, state = build_context()
    state.status = status
    before = state.model_dump_json()

    with pytest.raises(InactiveSessionError):
        restart_systemd_service(
            definition,
            state,
            resource_id="service-api",
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_handler_does_not_mutate_incident_definition():
    definition, state = build_context()
    definition_before = definition.model_dump_json()

    restart_systemd_service(
        definition,
        state,
        resource_id="service-api",
        now=LATER,
    )

    assert definition.model_dump_json() == definition_before


def test_sessions_remain_independent():
    definition = build_definition()
    first = create_session_runtime(definition, now=FIXED_NOW)
    second = create_session_runtime(definition, now=FIXED_NOW)

    restart_systemd_service(
        definition,
        first,
        resource_id="service-api",
        now=LATER,
    )

    assert first.world_state.resources["service-api"].current_state == "running"
    assert first.status is SessionStatus.COMPLETED
    assert second.world_state.resources["service-api"].current_state == "failed"
    assert second.status is SessionStatus.ACTIVE
    assert second.completed_objective_ids == set()
    assert second.revision == 0


def test_runtime_json_round_trip_after_restart():
    definition, state = build_context()
    restart_systemd_service(
        definition,
        state,
        resource_id="service-api",
        now=LATER,
    )

    restored = SessionRuntimeState.model_validate_json(state.model_dump_json())

    assert restored == state


def test_systemd_status_reports_failed_service_and_accounts_command():
    definition, state = build_context()
    world_before = state.world_state.model_dump_json()

    result = get_systemd_service_status(
        definition,
        state,
        resource_id="service-api",
        now=LATER,
    )

    assert result.success is True
    assert result.output == (
        "● service-api\n"
        "   Loaded: loaded\n"
        "   Active: failed"
    )
    assert state.world_state.model_dump_json() == world_before
    assert state.commands_used == 1
    assert state.score == 995
    assert state.revision == 1
    assert state.last_activity == LATER
    assert state.discovered_fact_ids == {
        "service-status-inspected:service-api"
    }
    assert state.status is SessionStatus.ACTIVE
    assert result.progress.revision == 1


def test_systemd_status_uses_service_name_and_reports_running_state():
    definition, state = build_context()
    service = state.world_state.resources["service-api"]
    service.current_state = "running"
    attributes = service.attributes.copy()
    attributes["service_name"] = "example-api.service"
    service.attributes = attributes
    world_before = state.world_state.model_dump_json()

    result = get_systemd_service_status(
        definition,
        state,
        resource_id="service-api",
        now=LATER,
    )

    assert result.output == (
        "● example-api.service\n"
        "   Loaded: loaded\n"
        "   Active: running"
    )
    assert state.world_state.model_dump_json() == world_before
    assert state.completed_objective_ids == {"restart-service"}
    assert state.status is SessionStatus.COMPLETED
    assert result.progress.mission_complete is True


def test_repeated_systemd_status_counts_again_without_duplicate_fact():
    definition, state = build_context()
    world_before = state.world_state.model_dump_json()
    second_time = LATER + timedelta(minutes=1)

    get_systemd_service_status(
        definition,
        state,
        resource_id="service-api",
        now=LATER,
    )
    get_systemd_service_status(
        definition,
        state,
        resource_id="service-api",
        now=second_time,
    )

    assert state.world_state.model_dump_json() == world_before
    assert state.discovered_fact_ids == {
        "service-status-inspected:service-api"
    }
    assert state.commands_used == 2
    assert state.score == 990
    assert state.revision == 2
    assert state.last_activity == second_time


def test_systemd_status_requires_capability_without_accounting():
    definition, state = build_context()
    capabilities = definition.capabilities.model_copy(
        update={
            "command_capability_ids": tuple(
                capability
                for capability in definition.capabilities.command_capability_ids
                if capability != "systemd.status"
            )
        }
    )
    definition = definition.model_copy(update={"capabilities": capabilities})
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError, match="systemd.status"):
        get_systemd_service_status(
            definition,
            state,
            resource_id="service-api",
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_systemd_status_rejects_missing_resource_without_accounting():
    definition, state = build_context()
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError, match="nie istnieje"):
        get_systemd_service_status(
            definition,
            state,
            resource_id="missing-service",
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_systemd_status_rejects_non_service_without_accounting():
    definition, state = build_context()
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError, match="nie jest usługą"):
        get_systemd_service_status(
            definition,
            state,
            resource_id="host-app",
            now=LATER,
        )

    assert state.model_dump_json() == before


@pytest.mark.parametrize("manager", [None, "supervisord"])
def test_systemd_status_rejects_non_systemd_manager(manager):
    definition, state = build_context()
    service = state.world_state.resources["service-api"]
    attributes = service.attributes.copy()

    if manager is None:
        attributes.pop("manager")
    else:
        attributes["manager"] = manager

    service.attributes = attributes
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError, match="zarządzana przez systemd"):
        get_systemd_service_status(
            definition,
            state,
            resource_id="service-api",
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_systemd_status_rejects_scenario_mismatch_without_accounting():
    definition, state = build_context()
    state.scenario_id = uuid4()
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError, match="różne scenario_id"):
        get_systemd_service_status(
            definition,
            state,
            resource_id="service-api",
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_systemd_status_does_not_mutate_definition():
    definition, state = build_context()
    definition_before = definition.model_dump_json()

    get_systemd_service_status(
        definition,
        state,
        resource_id="service-api",
        now=LATER,
    )

    assert definition.model_dump_json() == definition_before


def test_systemd_status_keeps_sessions_independent():
    definition = build_definition()
    first = create_session_runtime(definition, now=FIXED_NOW)
    second = create_session_runtime(definition, now=FIXED_NOW)

    get_systemd_service_status(
        definition,
        first,
        resource_id="service-api",
        now=LATER,
    )

    assert first.commands_used == 1
    assert first.discovered_fact_ids == {
        "service-status-inspected:service-api"
    }
    assert second.commands_used == 0
    assert second.discovered_fact_ids == set()
    assert second.revision == 0


def test_command_execution_result_is_frozen_and_json_serializable():
    definition, state = build_context()
    result = restart_systemd_service(
        definition,
        state,
        resource_id="service-api",
        now=LATER,
    )

    restored = CommandExecutionResult.model_validate_json(
        result.model_dump_json()
    )

    assert restored == result

    with pytest.raises(ValidationError):
        result.success = False
