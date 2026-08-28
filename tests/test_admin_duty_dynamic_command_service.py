from datetime import UTC, datetime, timedelta

import pytest

from app.admin_duty.domain.runtime import (
    InactiveSessionError,
    SessionRuntimeState,
    SessionStatus,
    create_session_runtime,
)
from app.admin_duty.dynamic_command_parser import CommandParseError
from app.admin_duty.dynamic_command_registry import CommandDispatchError
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.dynamic_commands import (
    CommandExecutionError,
    CommandExecutionResult,
)
from tests.test_admin_duty_systemd_commands import build_definition

FIXED_NOW = datetime(2026, 8, 25, 18, 0, tzinfo=UTC)
STATUS_TIME = FIXED_NOW + timedelta(minutes=1)
RESTART_TIME = FIXED_NOW + timedelta(minutes=2)


def build_context():
    definition = build_definition()
    state = create_session_runtime(definition, now=FIXED_NOW)
    return definition, state, DynamicCommandService()


def test_execute_status_text_runs_complete_backend_flow():
    definition, state, service = build_context()
    world_before = state.world_state.model_dump_json()

    result = service.execute(
        definition,
        state,
        "systemctl status service-api",
        now=STATUS_TIME,
    )

    assert isinstance(result, CommandExecutionResult)
    assert "Active: failed" in result.output
    assert state.world_state.model_dump_json() == world_before
    assert state.commands_used == 1
    assert state.score == 995
    assert state.revision == 1
    assert state.last_activity == STATUS_TIME
    assert state.discovered_fact_ids == {
        "service-status-inspected:service-api"
    }
    assert result.progress.revision == 1


def test_execute_restart_text_runs_complete_backend_flow():
    definition, state, service = build_context()

    result = service.execute(
        definition,
        state,
        "systemctl restart service-api",
        now=STATUS_TIME,
    )

    assert state.world_state.resources["service-api"].current_state == "running"
    assert state.commands_used == 1
    assert state.score == 995
    assert state.revision == 1
    assert state.last_activity == STATUS_TIME
    assert state.completed_objective_ids == {"restart-service"}
    assert state.status is SessionStatus.COMPLETED
    assert result.progress.mission_complete is True


def test_status_then_restart_accumulates_runtime_state():
    definition, state, service = build_context()

    service.execute(
        definition,
        state,
        "systemctl status service-api",
        now=STATUS_TIME,
    )
    result = service.execute(
        definition,
        state,
        "systemctl restart service-api",
        now=RESTART_TIME,
    )

    assert state.world_state.resources["service-api"].current_state == "running"
    assert state.commands_used == 2
    assert state.score == 990
    assert state.revision == 2
    assert state.last_activity == RESTART_TIME
    assert state.discovered_fact_ids == {
        "service-status-inspected:service-api"
    }
    assert state.completed_objective_ids == {"restart-service"}
    assert state.status is SessionStatus.COMPLETED
    assert result.progress.mission_complete is True
    assert result.progress.revision == 2


def test_parser_error_leaves_runtime_unchanged():
    definition, state, service = build_context()
    before = state.model_dump_json()

    with pytest.raises(CommandParseError):
        service.execute(
            definition,
            state,
            "systemctl destroy service-api",
            now=STATUS_TIME,
        )

    assert state.model_dump_json() == before


def test_dispatch_error_leaves_runtime_unchanged():
    definition, state, service = build_context()
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

    with pytest.raises(CommandDispatchError):
        service.execute(
            definition,
            state,
            "systemctl restart service-api",
            now=STATUS_TIME,
        )

    assert state.model_dump_json() == before


def test_handler_error_leaves_runtime_unchanged_and_is_not_masked():
    definition, state, service = build_context()
    before = state.model_dump_json()

    with pytest.raises(CommandExecutionError) as error:
        service.execute(
            definition,
            state,
            "systemctl status missing-service",
            now=STATUS_TIME,
        )

    assert type(error.value) is CommandExecutionError
    assert state.model_dump_json() == before


@pytest.mark.parametrize(
    "status",
    [SessionStatus.COMPLETED, SessionStatus.ENDED],
)
def test_inactive_session_error_is_not_masked_or_accounted(status):
    definition, state, service = build_context()
    state.status = status
    before = state.model_dump_json()

    with pytest.raises(InactiveSessionError):
        service.execute(
            definition,
            state,
            "systemctl status service-api",
            now=STATUS_TIME,
        )

    assert state.model_dump_json() == before


def test_service_keeps_sessions_independent():
    definition = build_definition()
    first = create_session_runtime(definition, now=FIXED_NOW)
    second = create_session_runtime(definition, now=FIXED_NOW)
    service = DynamicCommandService()

    service.execute(
        definition,
        first,
        "systemctl status service-api",
        now=STATUS_TIME,
    )

    assert first.commands_used == 1
    assert second.commands_used == 0
    assert second.discovered_fact_ids == set()
    assert second.revision == 0


def test_service_does_not_mutate_incident_definition():
    definition, state, service = build_context()
    definition_before = definition.model_dump_json()

    service.execute(
        definition,
        state,
        "systemctl status service-api",
        now=STATUS_TIME,
    )

    assert definition.model_dump_json() == definition_before


def test_runtime_json_round_trip_after_full_command_sequence():
    definition, state, service = build_context()
    service.execute(
        definition,
        state,
        "systemctl status service-api",
        now=STATUS_TIME,
    )
    service.execute(
        definition,
        state,
        "systemctl restart service-api",
        now=RESTART_TIME,
    )

    restored = SessionRuntimeState.model_validate_json(state.model_dump_json())

    assert restored == state


def test_dynamic_command_service_is_stateless():
    assert DynamicCommandService().__dict__ == {}
