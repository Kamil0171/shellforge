from datetime import UTC, datetime, timedelta

import pytest

from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.runtime import SessionStatus, create_session_runtime
from app.admin_duty.dynamic_command_parser import CommandParseError
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.generators import DeterministicIncidentGenerator

FIXED_NOW = datetime(2026, 8, 26, 14, 0, tzinfo=UTC)
FAULT_SEEDS = {
    "systemd_service_failed": 1,
    "systemd_wrong_exec_start": 3,
    "systemd_missing_environment_variable": 4,
    "systemd_permission_denied": 0,
}


def build(seed):
    definition = DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY, seed=seed, now=FIXED_NOW
    )
    state = create_session_runtime(definition, now=FIXED_NOW)
    return definition, state


@pytest.mark.parametrize(("fault_type", "seed"), FAULT_SEEDS.items())
def test_each_fault_reference_flow_completes_through_command_layer(fault_type, seed):
    definition, state = build(seed)
    service = DynamicCommandService()
    result = None

    assert definition.faults[0].fault_type == fault_type
    for index, step in enumerate(definition.solution, start=1):
        result = service.execute(
            definition,
            state,
            step.input,
            now=FIXED_NOW + timedelta(minutes=index),
        )
        if result.editor:
            result = service.save_file(
                definition,
                state,
                path=result.editor.path,
                content=step.parameters[0].value,
                now=FIXED_NOW + timedelta(minutes=index, seconds=1),
            )
        assert result.success is True

    assert result is not None
    assert result.progress.mission_complete is True
    assert state.status is SessionStatus.COMPLETED
    action_count = len(definition.solution) + sum(
        step.capability_id == "filesystem.edit" for step in definition.solution
    )
    assert state.commands_used == action_count
    assert state.revision == action_count


@pytest.mark.parametrize("seed", [3, 4, 0])
def test_restart_before_fault_repair_is_accounted_but_does_not_complete(seed):
    definition, state = build(seed)
    service_id = definition.objectives[0].completion_condition.resource_id

    result = DynamicCommandService().execute(
        definition,
        state,
        f"systemctl restart {service_id}",
        now=FIXED_NOW + timedelta(minutes=1),
    )

    assert result.success is False
    assert state.world_state.resources[service_id].current_state == "failed"
    assert state.commands_used == 1
    assert (
        state.score
        == definition.scoring.initial_score - definition.scoring.command_cost
    )
    assert state.revision == 1
    assert state.status is SessionStatus.ACTIVE
    assert result.progress.mission_complete is False


def test_removed_exec_start_shortcut_is_rejected_without_accounting():
    definition, state = build(3)
    before = state.model_dump_json()

    with pytest.raises(CommandParseError):
        DynamicCommandService().execute(
            definition,
            state,
            "systemctl set-exec-start service-api arbitrary-target",
            now=FIXED_NOW + timedelta(minutes=1),
        )

    assert state.model_dump_json() == before


def test_removed_environment_shortcut_is_rejected_without_accounting():
    definition, state = build(4)
    before = state.model_dump_json()

    with pytest.raises(CommandParseError):
        DynamicCommandService().execute(
            definition,
            state,
            "env restore service-api UNKNOWN_VARIABLE",
            now=FIXED_NOW + timedelta(minutes=1),
        )

    assert state.model_dump_json() == before


def test_environment_repair_is_discoverable_in_virtual_deployment_documentation():
    definition, state = build(4)
    service = DynamicCommandService()
    target = next(
        resource
        for resource in state.world_state.resources.values()
        if resource.attributes.get("required_environment_variable")
    )
    app_name = target.attributes["service_name"].removesuffix(".service")
    result = service.execute(
        definition, state, f"cat /opt/{app_name}/README.md", now=FIXED_NOW
    )
    assert (
        f"{target.attributes['required_environment_variable']}={target.attributes['expected_environment_value']}"
        in result.output
    )
