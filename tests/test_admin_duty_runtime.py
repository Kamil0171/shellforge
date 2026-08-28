from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.admin_duty.domain.definition import ResourceType
from app.admin_duty.domain.runtime import (
    InactiveSessionError,
    RuntimeResource,
    RuntimeWorldState,
    SessionRuntimeState,
    SessionStatus,
    apply_score_penalty,
    create_session_runtime,
    end_session_runtime,
    mark_solution_viewed,
    register_command,
    register_hint,
    touch_session,
)
from tests.test_admin_duty_incident_definition import build_incident_definition

FIXED_NOW = datetime(2026, 8, 24, 14, 30, tzinfo=UTC)


def build_runtime():
    return create_session_runtime(
        build_incident_definition(),
        now=FIXED_NOW,
    )


def test_runtime_can_be_created_from_incident_definition():
    definition = build_incident_definition()

    runtime = create_session_runtime(definition, now=FIXED_NOW)

    assert runtime.scenario_id == definition.scenario_id
    assert isinstance(runtime.session_id, UUID)
    assert runtime.status is SessionStatus.ACTIVE
    assert runtime.world_state.resources


def test_explicit_session_id_is_preserved():
    session_id = uuid4()

    runtime = create_session_runtime(
        build_incident_definition(),
        session_id=session_id,
        now=FIXED_NOW,
    )

    assert runtime.session_id == session_id


def test_automatic_session_ids_are_unique():
    definition = build_incident_definition()

    first = create_session_runtime(definition, now=FIXED_NOW)
    second = create_session_runtime(definition, now=FIXED_NOW)

    assert first.session_id != second.session_id


def test_runtime_timestamps_use_supplied_time():
    runtime = build_runtime()

    assert runtime.created_at == FIXED_NOW
    assert runtime.last_activity == FIXED_NOW


def test_runtime_starts_with_initial_scoring_and_empty_progress():
    definition = build_incident_definition()

    runtime = create_session_runtime(definition, now=FIXED_NOW)

    assert runtime.score == definition.scoring.initial_score
    assert runtime.commands_used == 0
    assert runtime.hints_used == 0
    assert runtime.solution_viewed is False
    assert runtime.completed_objective_ids == set()
    assert runtime.discovered_fact_ids == set()
    assert runtime.revision == 0


def test_runtime_world_is_created_from_initial_world_state():
    definition = build_incident_definition()

    runtime = create_session_runtime(definition, now=FIXED_NOW)
    service = runtime.world_state.resources["service-api"]

    assert len(runtime.world_state.resources) == len(
        definition.initial_world_state.resources
    )
    assert service.resource_type is ResourceType.SERVICE
    assert service.current_state == "failed"
    assert service.parent_resource_id == "host-app"
    assert service.attributes == {
        "manager": "systemd",
        "port": 8100,
    }


def test_runtime_mutation_does_not_change_incident_definition():
    definition = build_incident_definition()
    original_snapshot = definition.model_dump_json()
    runtime = create_session_runtime(definition, now=FIXED_NOW)
    service = runtime.world_state.resources["service-api"]

    service.current_state = "active"
    service.parent_resource_id = None
    service.dependencies.append("service-database")
    service.attributes["port"] = 8200
    service.attributes["new_attribute"] = True

    assert definition.model_dump_json() == original_snapshot
    definition_service = next(
        resource
        for resource in definition.initial_world_state.resources
        if resource.resource_id == "service-api"
    )
    assert definition_service.state == "failed"
    assert dict(
        (attribute.key, attribute.value)
        for attribute in definition_service.attributes
    ) == {
        "manager": "systemd",
        "port": 8100,
    }


def test_sessions_from_same_definition_are_independent():
    definition = build_incident_definition()
    first = create_session_runtime(definition, now=FIXED_NOW)
    second = create_session_runtime(definition, now=FIXED_NOW)
    first_service = first.world_state.resources["service-api"]
    second_service = second.world_state.resources["service-api"]

    first_service.current_state = "active"
    first_service.dependencies.append("service-database")
    first_service.attributes["port"] = 8200
    first.completed_objective_ids.add("restore-service")
    first.discovered_fact_ids.add("service-failed")

    assert second_service.current_state == "failed"
    assert second_service.dependencies == []
    assert second_service.attributes["port"] == 8100
    assert second.completed_objective_ids == set()
    assert second.discovered_fact_ids == set()
    assert first.world_state is not second.world_state
    assert first_service is not second_service
    assert first_service.dependencies is not second_service.dependencies
    assert first_service.attributes is not second_service.attributes


def test_runtime_is_mutable_and_validates_assignments():
    runtime = build_runtime()
    service = runtime.world_state.resources["service-api"]

    runtime.score = 950
    runtime.commands_used = 1
    runtime.hints_used = 1
    runtime.solution_viewed = True
    runtime.revision = 1
    runtime.status = SessionStatus.COMPLETED
    runtime.completed_objective_ids.add("restore-service")
    runtime.discovered_fact_ids.add("service-failed")
    service.current_state = "active"

    assert runtime.score == 950
    assert runtime.commands_used == 1
    assert runtime.hints_used == 1
    assert runtime.solution_viewed is True
    assert runtime.revision == 1
    assert runtime.status is SessionStatus.COMPLETED
    assert service.current_state == "active"

    with pytest.raises(ValidationError):
        runtime.score = -1


def test_runtime_json_round_trip():
    runtime = build_runtime()
    runtime.completed_objective_ids.add("restore-service")
    runtime.discovered_fact_ids.add("service-failed")

    restored = SessionRuntimeState.model_validate_json(runtime.model_dump_json())

    assert restored == runtime
    assert isinstance(restored.completed_objective_ids, set)
    assert isinstance(restored.world_state.resources, dict)
    assert isinstance(restored.world_state.resources["service-api"].attributes, dict)


@pytest.mark.parametrize(
    "field",
    [
        "score",
        "commands_used",
        "hints_used",
        "revision",
    ],
)
def test_negative_runtime_counters_are_rejected(field):
    payload = build_runtime().model_dump(mode="json")
    payload[field] = -1

    with pytest.raises(ValidationError):
        SessionRuntimeState.model_validate(payload)


def test_last_activity_cannot_precede_session_creation():
    payload = build_runtime().model_dump(mode="json")
    payload["last_activity"] = (FIXED_NOW - timedelta(seconds=1)).isoformat()

    with pytest.raises(
        ValidationError,
        match="Ostatnia aktywność nie może być wcześniejsza",
    ):
        SessionRuntimeState.model_validate(payload)


@pytest.mark.parametrize("timestamp_field", ["created_at", "last_activity"])
def test_runtime_timestamps_must_include_timezone(timestamp_field):
    payload = build_runtime().model_dump(mode="json")
    payload[timestamp_field] = "2026-08-24T14:30:00"

    with pytest.raises(ValidationError):
        SessionRuntimeState.model_validate(payload)


def test_current_working_directory_is_absolute_and_normalized():
    runtime = create_session_runtime(
        build_incident_definition(),
        now=FIXED_NOW,
        current_working_directory="/home/operator/../admin",
    )

    assert runtime.current_working_directory == "/home/admin"

    with pytest.raises(ValidationError):
        runtime.current_working_directory = "home/operator"


def test_default_current_working_directory_is_operator_home():
    assert build_runtime().current_working_directory == "/home/operator"


def test_runtime_world_rejects_resource_key_mismatch():
    resource = RuntimeResource(
        resource_id="host-app",
        resource_type=ResourceType.HOST,
        current_state="healthy",
    )

    with pytest.raises(
        ValidationError,
        match="Klucz zasobu runtime musi odpowiadać jego resource_id",
    ):
        RuntimeWorldState(resources={"different-id": resource})


def test_runtime_resource_rejects_arbitrary_attribute_values():
    with pytest.raises(ValidationError):
        RuntimeResource(
            resource_id="host-app",
            resource_type=ResourceType.HOST,
            current_state="healthy",
            attributes={"invalid": object()},
        )


def test_touch_session_updates_activity_and_revision_once():
    runtime = build_runtime()
    later = FIXED_NOW + timedelta(minutes=1)

    touch_session(runtime, now=later)

    assert runtime.last_activity == later
    assert runtime.revision == 1


def test_touch_session_cannot_move_activity_backwards():
    runtime = build_runtime()
    later = FIXED_NOW + timedelta(minutes=2)
    touch_session(runtime, now=later)

    with pytest.raises(
        ValueError,
        match="Czas operacji nie może cofać aktywności sesji",
    ):
        touch_session(runtime, now=later - timedelta(seconds=1))

    assert runtime.last_activity == later
    assert runtime.revision == 1


def test_operation_time_requires_timezone():
    runtime = build_runtime()

    with pytest.raises(ValueError, match="musi zawierać strefę czasową"):
        touch_session(runtime, now=datetime(2026, 8, 24, 15, 0))

    assert runtime.last_activity == FIXED_NOW
    assert runtime.revision == 0


def test_score_penalty_updates_score_activity_and_revision():
    runtime = build_runtime()
    later = FIXED_NOW + timedelta(minutes=1)

    apply_score_penalty(runtime, 125, now=later)

    assert runtime.score == 875
    assert runtime.last_activity == later
    assert runtime.revision == 1


def test_score_penalty_cannot_reduce_score_below_zero():
    runtime = build_runtime()

    apply_score_penalty(runtime, 5000, now=FIXED_NOW)

    assert runtime.score == 0
    assert runtime.revision == 1

    apply_score_penalty(runtime, 10, now=FIXED_NOW)

    assert runtime.score == 0
    assert runtime.revision == 2


def test_negative_score_penalty_is_rejected_without_mutation():
    runtime = build_runtime()

    with pytest.raises(ValueError, match="Kara punktowa nie może być ujemna"):
        apply_score_penalty(runtime, -1, now=FIXED_NOW)

    assert runtime.score == 1000
    assert runtime.last_activity == FIXED_NOW
    assert runtime.revision == 0


def test_register_command_counts_command_cost_and_one_revision():
    runtime = build_runtime()
    later = FIXED_NOW + timedelta(minutes=1)

    register_command(runtime, cost=5, now=later)

    assert runtime.commands_used == 1
    assert runtime.score == 995
    assert runtime.last_activity == later
    assert runtime.revision == 1


def test_register_hint_counts_hint_penalty_and_one_revision():
    runtime = build_runtime()
    later = FIXED_NOW + timedelta(minutes=1)

    register_hint(runtime, penalty=25, now=later)

    assert runtime.hints_used == 1
    assert runtime.score == 975
    assert runtime.last_activity == later
    assert runtime.revision == 1


def test_mark_solution_viewed_applies_penalty_only_once():
    runtime = build_runtime()
    first_time = FIXED_NOW + timedelta(minutes=1)
    second_time = FIXED_NOW + timedelta(minutes=2)

    mark_solution_viewed(runtime, penalty=250, now=first_time)

    assert runtime.solution_viewed is True
    assert runtime.score == 750
    assert runtime.last_activity == first_time
    assert runtime.revision == 1

    mark_solution_viewed(runtime, penalty=500, now=second_time)

    assert runtime.score == 750
    assert runtime.last_activity == first_time
    assert runtime.revision == 1


@pytest.mark.parametrize(
    "status",
    [SessionStatus.COMPLETED, SessionStatus.ENDED],
)
def test_runtime_operations_reject_inactive_sessions(status):
    runtime = build_runtime()
    runtime.status = status
    later = FIXED_NOW + timedelta(minutes=1)
    operations = (
        lambda: touch_session(runtime, now=later),
        lambda: apply_score_penalty(runtime, 5, now=later),
        lambda: register_command(runtime, cost=5, now=later),
        lambda: register_hint(runtime, penalty=25, now=later),
        lambda: mark_solution_viewed(runtime, penalty=250, now=later),
    )

    for operation in operations:
        with pytest.raises(InactiveSessionError):
            operation()

    assert runtime.last_activity == FIXED_NOW
    assert runtime.revision == 0


def test_runtime_json_round_trip_after_domain_operations():
    runtime = build_runtime()

    touch_session(runtime, now=FIXED_NOW + timedelta(minutes=1))
    register_command(
        runtime,
        cost=5,
        now=FIXED_NOW + timedelta(minutes=2),
    )
    register_hint(
        runtime,
        penalty=25,
        now=FIXED_NOW + timedelta(minutes=3),
    )
    mark_solution_viewed(
        runtime,
        penalty=250,
        now=FIXED_NOW + timedelta(minutes=4),
    )

    restored = SessionRuntimeState.model_validate_json(runtime.model_dump_json())

    assert restored == runtime
    assert restored.commands_used == 1
    assert restored.hints_used == 1
    assert restored.solution_viewed is True
    assert restored.score == 720
    assert restored.revision == 4


@pytest.mark.parametrize(
    "initial_status",
    [SessionStatus.ACTIVE, SessionStatus.COMPLETED],
)
def test_end_session_runtime_preserves_data_and_increments_revision(
    initial_status,
):
    runtime = build_runtime()
    runtime.status = initial_status
    runtime.completed_objective_ids = {"check-service"}
    runtime.discovered_fact_ids = {"service-status-inspected:service-api"}
    later = FIXED_NOW + timedelta(minutes=1)

    end_session_runtime(runtime, now=later)

    assert runtime.status is SessionStatus.ENDED
    assert runtime.completed_objective_ids == {"check-service"}
    assert runtime.discovered_fact_ids == {
        "service-status-inspected:service-api"
    }
    assert runtime.last_activity == later
    assert runtime.revision == 1


def test_end_session_runtime_rejects_repeated_end_as_full_no_op():
    runtime = build_runtime()
    first_end = FIXED_NOW + timedelta(minutes=1)
    end_session_runtime(runtime, now=first_end)
    before = runtime.model_dump_json()

    with pytest.raises(InactiveSessionError):
        end_session_runtime(
            runtime,
            now=FIXED_NOW + timedelta(minutes=2),
        )

    assert runtime.model_dump_json() == before
