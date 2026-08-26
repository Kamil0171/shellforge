from datetime import UTC, datetime

import pytest

from app.admin_duty.domain.definition import ComponentType, SolutionStep
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.validators import IncidentValidationError, IncidentValidator

FIXED_NOW = datetime(2026, 8, 26, 12, 0, tzinfo=UTC)


def generated(seed=4):
    return DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY, seed=seed, now=FIXED_NOW
    )


def replace_resources(definition, resources):
    world = definition.initial_world_state.model_copy(update={"resources": resources})
    return definition.model_copy(update={"initial_world_state": world})


def test_validator_accepts_generated_definition_without_mutation():
    definition = generated()
    before = definition.model_dump_json()

    result = IncidentValidator().validate(definition)

    assert result is definition
    assert definition.model_dump_json() == before


def test_validator_rejects_host_count_outside_profile():
    definition = generated()
    resources = tuple(
        resource
        for resource in definition.initial_world_state.resources
        if resource.resource_id != "host-monitoring-01"
    )

    with pytest.raises(IncidentValidationError, match="Liczba hostów"):
        IncidentValidator().validate(replace_resources(definition, resources))


def test_validator_rejects_fault_count_outside_profile():
    definition = generated()

    with pytest.raises(IncidentValidationError, match="Liczba faultów"):
        IncidentValidator().validate(
            definition.model_copy(update={"faults": definition.faults * 2})
        )


def test_validator_rejects_duplicate_resource_ids():
    definition = generated()
    resources = (
        *definition.initial_world_state.resources,
        definition.initial_world_state.resources[0],
    )

    with pytest.raises(IncidentValidationError, match="nie są unikalne"):
        IncidentValidator().validate(replace_resources(definition, resources))


@pytest.mark.parametrize("reference", ["fault", "symptom", "objective", "map"])
def test_validator_rejects_unknown_resource_references(reference):
    definition = generated()

    if reference == "fault":
        value = definition.model_copy(
            update={
                "faults": (
                    definition.faults[0].model_copy(
                        update={"target_resource_id": "missing-resource"}
                    ),
                )
            }
        )
    elif reference == "symptom":
        value = definition.model_copy(
            update={
                "symptoms": (
                    definition.symptoms[0].model_copy(
                        update={"source_resource_id": "missing-resource"}
                    ),
                )
            }
        )
    elif reference == "objective":
        condition = definition.objectives[0].completion_condition.model_copy(
            update={"resource_id": "missing-resource"}
        )
        value = definition.model_copy(
            update={
                "objectives": (
                    definition.objectives[0].model_copy(
                        update={"completion_condition": condition}
                    ),
                )
            }
        )
    else:
        snapshot = definition.initial_world_state.map
        interaction = snapshot.interactions[0].model_copy(
            update={"target_resource_id": "missing-resource"}
        )
        world = definition.initial_world_state.model_copy(
            update={"map": snapshot.model_copy(update={"interactions": (interaction,)})}
        )
        value = definition.model_copy(update={"initial_world_state": world})

    with pytest.raises(IncidentValidationError, match="nieznany zasób"):
        IncidentValidator().validate(value)


def test_validator_requires_required_objective():
    definition = generated()
    objective = definition.objectives[0].model_copy(update={"required": False})

    with pytest.raises(IncidentValidationError, match="przynajmniej jednego celu"):
        IncidentValidator().validate(
            definition.model_copy(update={"objectives": (objective,)})
        )


def test_validator_enforces_easy_hint_limit():
    definition = generated()
    extra = definition.hints[-1].model_copy(update={"order": 4})

    with pytest.raises(IncidentValidationError, match="podpowiedzi"):
        IncidentValidator().validate(
            definition.model_copy(update={"hints": (*definition.hints, extra)})
        )


def test_validator_rejects_initially_completed_required_objective():
    definition = generated()
    objective_resource_id = definition.objectives[0].completion_condition.resource_id
    resources = tuple(
        resource.model_copy(update={"state": "running"})
        if resource.resource_id == objective_resource_id
        else resource
        for resource in definition.initial_world_state.resources
    )

    with pytest.raises(IncidentValidationError, match="initial state"):
        IncidentValidator().validate(replace_resources(definition, resources))


def test_validator_rejects_incomplete_provenance():
    definition = generated()
    components = tuple(
        item
        for item in definition.generation.components
        if item.component_type is not ComponentType.SYMPTOM
    )
    generation = definition.generation.model_copy(update={"components": components})

    with pytest.raises(IncidentValidationError, match="Provenance"):
        IncidentValidator().validate(
            definition.model_copy(update={"generation": generation})
        )


def test_validator_rejects_fault_provenance_version_mismatch():
    definition = generated()
    components = tuple(
        item.model_copy(update={"version": "2.0"})
        if item.component_type is ComponentType.FAULT
        else item
        for item in definition.generation.components
    )
    generation = definition.generation.model_copy(update={"components": components})

    with pytest.raises(IncidentValidationError, match="Provenance faultów"):
        IncidentValidator().validate(
            definition.model_copy(update={"generation": generation})
        )


def test_validator_rejects_root_cause_leak_in_public_presentation():
    definition = generated(seed=4)
    presentation = definition.presentation.model_copy(
        update={"briefing": f"{definition.presentation.briefing} DATABASE_URL"}
    )

    with pytest.raises(IncidentValidationError, match="root cause"):
        IncidentValidator().validate(
            definition.model_copy(update={"presentation": presentation})
        )


def test_validator_rejects_nondeterministic_ordering():
    definition = generated(seed=4)
    hints = tuple(reversed(definition.hints))

    with pytest.raises(IncidentValidationError, match="Kolejność hints"):
        IncidentValidator().validate(definition.model_copy(update={"hints": hints}))


def test_validator_rejects_solution_capability_mismatch():
    definition = generated(seed=4)
    step = definition.solution[0].model_copy(
        update={"capability_id": "environment.inspect"}
    )
    solution = (step, *definition.solution[1:])

    with pytest.raises(IncidentValidationError, match="nie odpowiada"):
        IncidentValidator().validate(
            definition.model_copy(update={"solution": solution})
        )


def test_validator_rejects_solution_with_unavailable_capability():
    definition = generated(seed=4)
    capabilities = definition.capabilities.model_copy(
        update={
            "command_capability_ids": tuple(
                capability
                for capability in definition.capabilities.command_capability_ids
                if capability != "environment.restore"
            )
        }
    )

    with pytest.raises(IncidentValidationError, match="niedostępnego capability"):
        IncidentValidator().validate(
            definition.model_copy(update={"capabilities": capabilities})
        )


def test_validator_rejects_reference_solution_that_does_not_complete_mission():
    definition = generated(seed=3)
    final_step = SolutionStep(
        order=4,
        capability_id="systemd.status",
        input="systemctl status service-api",
        purpose="Ponownie sprawdź stan.",
    )
    solution = (*definition.solution[:-1], final_step)

    with pytest.raises(IncidentValidationError, match="nie kończy"):
        IncidentValidator().validate(
            definition.model_copy(update={"solution": solution})
        )
