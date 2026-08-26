from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.admin_duty.domain.engine import DynamicIncidentEngine
from app.admin_duty.domain.progress import get_session_progress
from app.admin_duty.domain.runtime import (
    InactiveSessionError,
    SessionStatus,
    create_session_runtime,
)
from app.admin_duty.dynamic_command_registry import (
    COMMAND_HANDLERS,
    CommandDispatchError,
    DynamicCommandDispatcher,
    DynamicCommandRequest,
)
from app.admin_duty.dynamic_commands import (
    CommandExecutionError,
    CommandExecutionResult,
    get_systemd_service_status,
    restart_systemd_service,
)
from tests.test_admin_duty_systemd_commands import build_definition

FIXED_NOW = datetime(2026, 8, 25, 16, 0, tzinfo=UTC)
LATER = FIXED_NOW + timedelta(minutes=1)


def build_context():
    definition = build_definition()
    state = create_session_runtime(definition, now=FIXED_NOW)
    return definition, state, DynamicCommandDispatcher()


def test_registry_contains_all_controlled_handlers():
    assert set(COMMAND_HANDLERS) == {
        "systemd.status",
        "systemd.restart",
        "systemd.cat",
        "systemd.set-exec-start",
        "environment.inspect",
        "environment.restore",
        "filesystem.stat",
        "filesystem.restore-permissions",
    }
    assert COMMAND_HANDLERS["systemd.status"] is get_systemd_service_status
    assert COMMAND_HANDLERS["systemd.restart"] is restart_systemd_service


def test_registry_is_immutable():
    with pytest.raises(TypeError):
        COMMAND_HANDLERS["systemd.stop"] = get_systemd_service_status


def test_dynamic_command_request_is_frozen_forbids_extra_and_round_trips_json():
    request = DynamicCommandRequest(
        command_id="systemd.status",
        resource_id="service-api",
    )

    restored = DynamicCommandRequest.model_validate_json(request.model_dump_json())

    assert restored == request

    with pytest.raises(ValidationError):
        request.command_id = "systemd.restart"

    with pytest.raises(ValidationError):
        DynamicCommandRequest(
            command_id="systemd.status",
            resource_id="service-api",
            payload={"unexpected": True},
        )


def test_dispatch_systemd_status_runs_handler_without_world_mutation():
    definition, state, dispatcher = build_context()
    world_before = state.world_state.model_dump_json()

    result = dispatcher.dispatch(
        definition,
        state,
        DynamicCommandRequest(
            command_id="systemd.status",
            resource_id="service-api",
        ),
        now=LATER,
    )

    assert isinstance(result, CommandExecutionResult)
    assert "Active: failed" in result.output
    assert state.world_state.model_dump_json() == world_before
    assert state.commands_used == 1
    assert state.score == 995
    assert state.revision == 1
    assert state.discovered_fact_ids == {"service-status-inspected:service-api"}


def test_dispatch_systemd_restart_runs_handler_and_completes_objective():
    definition, state, dispatcher = build_context()

    result = dispatcher.dispatch(
        definition,
        state,
        DynamicCommandRequest(
            command_id="systemd.restart",
            resource_id="service-api",
        ),
        now=LATER,
    )

    assert state.world_state.resources["service-api"].current_state == "running"
    assert state.commands_used == 1
    assert state.score == 995
    assert state.completed_objective_ids == {"restart-service"}
    assert state.status is SessionStatus.COMPLETED
    assert state.revision == 1
    assert result.progress.mission_complete is True


def test_unknown_command_is_rejected_without_mutation():
    definition, state, dispatcher = build_context()
    before = state.model_dump_json()

    with pytest.raises(CommandDispatchError, match="Nieznana komenda"):
        dispatcher.dispatch(
            definition,
            state,
            DynamicCommandRequest(
                command_id="systemd.stop",
                resource_id="service-api",
            ),
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_known_disabled_command_is_rejected_without_mutation():
    definition, state, dispatcher = build_context()
    capabilities = definition.capabilities.model_copy(
        update={
            "command_capability_ids": tuple(
                capability
                for capability in definition.capabilities.command_capability_ids
                if capability != "systemd.restart"
            )
        }
    )
    definition = definition.model_copy(update={"capabilities": capabilities})
    before = state.model_dump_json()

    with pytest.raises(CommandDispatchError, match="nie jest dostępna"):
        dispatcher.dispatch(
            definition,
            state,
            DynamicCommandRequest(
                command_id="systemd.restart",
                resource_id="service-api",
            ),
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_dispatcher_passes_resource_and_same_engine_to_handler():
    definition, state, dispatcher = build_context()
    before = state.model_dump_json()

    class RecordingEngine(DynamicIncidentEngine):
        def __init__(self):
            self.action = "not-called"
            self.command_cost = None
            self.discovered_fact_ids = None

        def execute_command(
            self,
            definition,
            state,
            action=None,
            *,
            command_cost,
            discovered_fact_ids=(),
            now=None,
        ):
            self.action = action
            self.command_cost = command_cost
            self.discovered_fact_ids = tuple(discovered_fact_ids)
            return get_session_progress(definition, state)

    engine = RecordingEngine()

    dispatcher.dispatch(
        definition,
        state,
        DynamicCommandRequest(
            command_id="systemd.status",
            resource_id="service-api",
        ),
        engine=engine,
        now=LATER,
    )

    assert engine.action is None
    assert engine.command_cost == definition.scoring.command_cost
    assert engine.discovered_fact_ids == ("service-status-inspected:service-api",)
    assert state.model_dump_json() == before


def test_handler_resource_error_is_not_masked_by_dispatcher():
    definition, state, dispatcher = build_context()

    with pytest.raises(CommandExecutionError) as error:
        dispatcher.dispatch(
            definition,
            state,
            DynamicCommandRequest(
                command_id="systemd.status",
                resource_id="missing-service",
            ),
            now=LATER,
        )

    assert type(error.value) is CommandExecutionError


@pytest.mark.parametrize(
    "status",
    [SessionStatus.COMPLETED, SessionStatus.ENDED],
)
def test_dispatcher_does_not_mask_inactive_session_error(status):
    definition, state, dispatcher = build_context()
    state.status = status
    before = state.model_dump_json()

    with pytest.raises(InactiveSessionError):
        dispatcher.dispatch(
            definition,
            state,
            DynamicCommandRequest(
                command_id="systemd.status",
                resource_id="service-api",
            ),
            now=LATER,
        )

    assert state.model_dump_json() == before


def test_dispatcher_does_not_mask_timestamp_error():
    definition, state, dispatcher = build_context()
    before = state.model_dump_json()

    with pytest.raises(ValueError, match="nie może cofać"):
        dispatcher.dispatch(
            definition,
            state,
            DynamicCommandRequest(
                command_id="systemd.status",
                resource_id="service-api",
            ),
            now=FIXED_NOW - timedelta(seconds=1),
        )

    assert state.model_dump_json() == before


def test_dispatch_does_not_mutate_incident_definition():
    definition, state, dispatcher = build_context()
    definition_before = definition.model_dump_json()

    dispatcher.dispatch(
        definition,
        state,
        DynamicCommandRequest(
            command_id="systemd.status",
            resource_id="service-api",
        ),
        now=LATER,
    )

    assert definition.model_dump_json() == definition_before


def test_dispatch_keeps_sessions_independent():
    definition = build_definition()
    first = create_session_runtime(definition, now=FIXED_NOW)
    second = create_session_runtime(definition, now=FIXED_NOW)
    dispatcher = DynamicCommandDispatcher()

    dispatcher.dispatch(
        definition,
        first,
        DynamicCommandRequest(
            command_id="systemd.status",
            resource_id="service-api",
        ),
        now=LATER,
    )

    assert first.commands_used == 1
    assert second.commands_used == 0
    assert second.discovered_fact_ids == set()
    assert second.revision == 0


def test_dispatcher_is_stateless():
    assert DynamicCommandDispatcher().__dict__ == {}
