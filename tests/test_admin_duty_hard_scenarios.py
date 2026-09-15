from datetime import UTC, datetime, timedelta

import pytest

from app.admin_duty.components.scenarios import (
    HARD_COMBINATIONS,
    build_hard_draft,
    get_hard_combination_for_pair,
)
from app.admin_duty.domain.difficulty import DifficultyLevel, get_difficulty_profile
from app.admin_duty.domain.generation import (
    convert_draft_to_definition,
    validate_and_convert_draft,
)
from app.admin_duty.domain.progress import get_session_progress
from app.admin_duty.domain.recovery import (
    IncidentRecoveryState,
    get_incident_recovery_state,
    resolved_fault_ids,
)
from app.admin_duty.domain.runtime import create_session_runtime
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.repositories import (
    InMemoryScenarioRepository,
    InMemorySessionRepository,
)
from app.admin_duty.services import DynamicIncidentService
from app.admin_duty.services.public_gameplay import project_public_monitoring
from app.admin_duty.validators import IncidentValidationError, IncidentValidator

NOW = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)


def _execute_step(definition, state, step, *, second):
    service = DynamicCommandService()
    result = service.execute(
        definition,
        state,
        step.input,
        now=NOW + timedelta(seconds=second),
    )
    if step.capability_id == "filesystem.edit":
        content = {field.key: field.value for field in step.parameters}["content"]
        result = service.save_file(
            definition,
            state,
            path=result.editor.path,
            content=content,
            now=NOW + timedelta(seconds=second + 1),
        )
    assert result.success is step.expected_success
    return result


@pytest.mark.parametrize("combination", HARD_COMBINATIONS)
def test_every_approved_hard_pair_materializes_and_replays(combination):
    draft = build_hard_draft(combination.combination_id, seed=23)
    definition = validate_and_convert_draft(draft, created_at=NOW)

    assert definition.schema_version == "4.0"
    assert definition.difficulty is DifficultyLevel.HARD
    assert len(definition.faults) == 2
    assert {fault.fault_id for fault in definition.faults} == {
        "fault-primary",
        "fault-secondary",
    }
    assert all(fault.resolution_condition for fault in definition.faults)
    assert len(definition.service_dependencies) == 4


def test_difficulty_profiles_enforce_v4_fault_counts():
    assert (get_difficulty_profile(DifficultyLevel.EASY).min_faults, get_difficulty_profile(DifficultyLevel.EASY).max_faults) == (1, 1)
    assert (get_difficulty_profile(DifficultyLevel.MEDIUM).min_faults, get_difficulty_profile(DifficultyLevel.MEDIUM).max_faults) == (1, 1)
    assert (get_difficulty_profile(DifficultyLevel.HARD).min_faults, get_difficulty_profile(DifficultyLevel.HARD).max_faults) == (2, 2)


@pytest.mark.parametrize("fault_count", [1, 3])
def test_hard_rejects_wrong_fault_count(fault_count):
    definition = convert_draft_to_definition(build_hard_draft("H-01", seed=1))
    faults = (definition.faults * 3)[:fault_count]

    with pytest.raises(IncidentValidationError, match="Liczba faultów"):
        IncidentValidator().validate(definition.model_copy(update={"faults": faults}))


def test_hard_rejects_duplicate_fault_ids():
    definition = convert_draft_to_definition(build_hard_draft("H-01", seed=1))
    duplicate = definition.faults[1].model_copy(update={"fault_id": "fault-primary"})

    with pytest.raises(IncidentValidationError, match="faultów"):
        IncidentValidator().validate(
            definition.model_copy(update={"faults": (definition.faults[0], duplicate)})
        )


def test_hard_catalog_rejects_unsupported_pair_environment_and_topology():
    with pytest.raises(ValueError, match="Nieobsługiwana para"):
        get_hard_combination_for_pair(
            "selinux-context-invalid",
            "dependency-package-missing",
        )

    definition = convert_draft_to_definition(build_hard_draft("H-01", seed=1))
    invalid_world = definition.initial_world_state.model_copy(
        update={"environment_id": "web-stack"}
    )
    with pytest.raises(IncidentValidationError, match="środowiskiem"):
        IncidentValidator().validate(
            definition.model_copy(update={"initial_world_state": invalid_world})
        )

    topology = tuple(
        dependency
        for dependency in definition.service_dependencies
        if dependency.dependency_id != "dep-api-database"
    )
    with pytest.raises(
        IncidentValidationError,
        match="topologia|Topologia|Propagacja",
    ):
        IncidentValidator().validate(
            definition.model_copy(update={"service_dependencies": topology})
        )


@pytest.mark.parametrize("combination", HARD_COMBINATIONS)
def test_first_repair_changes_symptoms_but_does_not_complete(combination):
    definition = convert_draft_to_definition(
        build_hard_draft(combination.combination_id, seed=31),
        created_at=NOW,
    )
    state = create_session_runtime(definition, now=NOW)
    initial_states = {
        symptom.source_resource_id: state.world_state.resources[
            symptom.source_resource_id
        ].current_state
        for symptom in definition.symptoms
    }

    assert get_incident_recovery_state(definition, state) is IncidentRecoveryState.BROKEN
    assert project_public_monitoring(definition, state).overall_status == "critical"

    for index, step in enumerate(definition.solution, 1):
        result = _execute_step(definition, state, step, second=index * 3)
        if len(resolved_fault_ids(definition, state)) == 1:
            break
    else:
        pytest.fail("Reference solution nie osiągnęło partial recovery.")

    current_states = {
        symptom.source_resource_id: state.world_state.resources[
            symptom.source_resource_id
        ].current_state
        for symptom in definition.symptoms
    }
    assert current_states != initial_states
    assert get_incident_recovery_state(definition, state) is IncidentRecoveryState.PARTIALLY_RECOVERED
    assert project_public_monitoring(definition, state).overall_status == "improving"
    assert result.progress.mission_complete is False
    assert state.status.value == "active"


def test_reversed_repair_order_stays_partial_then_completes():
    definition = convert_draft_to_definition(build_hard_draft("H-01", seed=37), created_at=NOW)
    state = create_session_runtime(definition, now=NOW)
    service = DynamicCommandService()
    commands = (
        "ssh app-0037",
        "restorecon -R /opt/orders-api",
        "systemctl restart orders-api",
    )
    for index, command in enumerate(commands, 1):
        service.execute(definition, state, command, now=NOW + timedelta(seconds=index))

    assert resolved_fault_ids(definition, state) == {"fault-secondary"}
    assert get_session_progress(definition, state).mission_complete is False

    for index, command in enumerate(
        (
            "ssh data-0037",
            "firewall-cmd --permanent --add-port=5432/tcp",
            "firewall-cmd --reload",
            "ssh client-0037",
            "curl http://portal.internal",
        ),
        10,
    ):
        service.execute(definition, state, command, now=NOW + timedelta(seconds=index))

    assert resolved_fault_ids(definition, state) == {
        "fault-primary",
        "fault-secondary",
    }
    assert get_session_progress(definition, state).mission_complete


def test_reference_replay_rejects_solution_ending_after_first_repair():
    definition = convert_draft_to_definition(
        build_hard_draft("H-01", seed=39),
        created_at=NOW,
    )

    with pytest.raises(IncidentValidationError, match="Replay|Reference"):
        IncidentValidator().validate(
            definition.model_copy(update={"solution": definition.solution[:6]})
        )


def test_hard_seed_is_stable_and_selects_full_catalog():
    generator = DeterministicIncidentGenerator()
    pairs = set()

    for seed in range(100):
        first = generator.generate(DifficultyLevel.HARD, seed=seed, now=NOW)
        second = generator.generate(DifficultyLevel.HARD, seed=seed, now=NOW)
        assert first.model_dump(exclude={"scenario_id"}) == second.model_dump(
            exclude={"scenario_id"}
        )
        pairs.add(
            tuple(
                field.value
                for fault in first.faults
                for field in fault.parameters
                if field.key == "component_id"
            )
        )

    assert pairs == {
        (
            combination.primary_fault_category,
            combination.secondary_fault_category,
        )
        for combination in HARD_COMBINATIONS
    }


def test_hard_builder_seed_changes_cosmetics_without_breaking_references():
    first = build_hard_draft("H-01", seed=51)
    second = build_hard_draft("H-01", seed=52)

    assert first == build_hard_draft("H-01", seed=51)
    assert first.initial_world_state != second.initial_world_state
    assert tuple(fault.fault_type for fault in first.faults) == tuple(
        fault.fault_type for fault in second.faults
    )
    validate_and_convert_draft(second, created_at=NOW)


def test_active_hard_dto_hides_fault_chain_and_completed_report_reveals_it():
    scenarios = InMemoryScenarioRepository()
    sessions = InMemorySessionRepository()
    service = DynamicIncidentService(
        generator=DeterministicIncidentGenerator(),
        scenario_repository=scenarios,
        session_repository=sessions,
    )
    definition = validate_and_convert_draft(build_hard_draft("H-04", seed=43), created_at=NOW)
    started = service._start_definition(definition, NOW)
    active = started.model_dump(mode="json", exclude_none=True)
    serialized = str(active).casefold()

    for hidden in (
        "fault-primary",
        "fault-secondary",
        "root_cause_chain",
        "primary_fault",
        "secondary_fault",
        "reference solution",
        "shellforge.gemma",
    ):
        assert hidden not in serialized
    assert "post_incident" not in active

    current = NOW
    for step in definition.solution:
        current += timedelta(seconds=3)
        result = service.execute_command(started.session_id, step.input, now=current)
        if step.capability_id == "filesystem.edit":
            content = {field.key: field.value for field in step.parameters}["content"]
            current += timedelta(seconds=1)
            service.save_file(
                started.session_id,
                path=result.editor.path,
                content=content,
                now=current,
            )

    report = service.get_progress(started.session_id, now=current).post_incident
    assert report is not None
    assert len(report.root_cause_chain) == 2
    assert report.primary_fault and report.secondary_fault
    assert report.impact_path and report.repair_sequence
    assert report.partial_recovery_explanation
    assert report.learning_summary
