from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.admin_duty.components.scenarios import build_hard_draft, build_medium_draft
from app.admin_duty.domain.definition import (
    ComponentType,
    ConfigurationRequirement,
    SolutionStep,
)
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.generation import convert_draft_to_definition
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.validators import IncidentValidationError, IncidentValidator

FIXED_NOW = datetime(2026, 8, 26, 12, 0, tzinfo=UTC)


def generated(seed=4):
    return DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY, seed=seed, now=FIXED_NOW
    )


def medium(category):
    return convert_draft_to_definition(
        build_medium_draft(category, seed=23),
        created_at=FIXED_NOW,
    )


def hard(combination_id):
    return convert_draft_to_definition(
        build_hard_draft(combination_id, seed=23),
        created_at=FIXED_NOW,
    )


def replace_attribute(resource, key, value):
    attributes = tuple(
        field.model_copy(update={"value": value}) if field.key == key else field
        for field in resource.attributes
    )
    return resource.model_copy(update={"attributes": attributes})


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
        update={"capability_id": "filesystem.read"}
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
                if capability != "filesystem.edit"
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
        order=definition.solution[-1].order,
        capability_id="systemd.status",
        input="systemctl status service-api",
        purpose="Ponownie sprawdź stan.",
    )
    solution = (*definition.solution[:-1], final_step)

    with pytest.raises(IncidentValidationError, match="nie kończy"):
        IncidentValidator().validate(
            definition.model_copy(update={"solution": solution})
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (("expected_mode", "999"), ("expected_owner", "root user")),
)
def test_configuration_requirement_rejects_invalid_access_metadata(field, value):
    payload = {
        "requirement_id": "config-access",
        "service_id": "service-api",
        "host_id": "host-app-01",
        "file_resource_id": "file-api-config",
        field: value,
    }

    with pytest.raises(ValidationError):
        ConfigurationRequirement.model_validate(payload)


def test_validator_rejects_config_access_requirement_for_missing_file():
    definition = medium("service-config-permission-denied")
    requirement = definition.configuration_requirements[0].model_copy(
        update={"file_resource_id": "file-missing"}
    )

    with pytest.raises(IncidentValidationError, match="nieznany zasób"):
        IncidentValidator().validate(
            definition.model_copy(update={"configuration_requirements": (requirement,)})
        )


def test_validator_requires_current_access_metadata_for_config_requirement():
    definition = medium("service-config-permission-denied")
    resources = tuple(
        resource.model_copy(
            update={
                "attributes": tuple(
                    field
                    for field in resource.attributes
                    if field.key != "current_mode"
                )
            }
        )
        if resource.resource_id == "file-api-config"
        else resource
        for resource in definition.initial_world_state.resources
    )

    with pytest.raises(IncidentValidationError, match="bieżącego trybu"):
        IncidentValidator().validate(replace_resources(definition, resources))


def test_validator_rejects_config_access_without_required_capability():
    definition = medium("service-config-permission-denied")
    capabilities = definition.capabilities.model_copy(
        update={
            "command_capability_ids": tuple(
                capability
                for capability in definition.capabilities.command_capability_ids
                if capability != "filesystem.chown"
            )
        }
    )

    with pytest.raises(IncidentValidationError, match="niedostępnego capability"):
        IncidentValidator().validate(
            definition.model_copy(update={"capabilities": capabilities})
        )


def test_validator_rejects_config_access_with_unreachable_resolution_condition():
    definition = hard("H-06")
    fault = definition.faults[1]
    condition = fault.resolution_condition.model_copy(update={"expected": "daemon"})
    faults = (
        definition.faults[0],
        fault.model_copy(update={"resolution_condition": condition}),
    )

    with pytest.raises(IncidentValidationError, match="Replay|Reference"):
        IncidentValidator().validate(definition.model_copy(update={"faults": faults}))


def test_validator_rejects_unknown_required_dns_name():
    definition = medium("dependency-dns-name-mismatch")
    resources = tuple(
        replace_attribute(resource, "required_dns_name", "missing.internal")
        if resource.resource_id == "service-api"
        else resource
        for resource in definition.initial_world_state.resources
    )

    with pytest.raises(IncidentValidationError, match="nieznaną nazwę DNS"):
        IncidentValidator().validate(replace_resources(definition, resources))


def test_validator_rejects_dns_record_inconsistent_with_dependency_target():
    definition = medium("dependency-dns-name-mismatch")
    resources = tuple(
        replace_attribute(resource, "address", "10.24.8.10")
        if resource.resource_id == "domain-database"
        else resource
        for resource in definition.initial_world_state.resources
    )

    with pytest.raises(IncidentValidationError, match="grafem zależności"):
        IncidentValidator().validate(replace_resources(definition, resources))


def test_validator_rejects_invalid_dns_record_name():
    definition = medium("dependency-dns-name-mismatch")
    resources = tuple(
        replace_attribute(resource, "name", "bad dns name")
        if resource.resource_id == "domain-database"
        else resource
        for resource in definition.initial_world_state.resources
    )

    with pytest.raises(IncidentValidationError, match="nieprawidłowy rekord"):
        IncidentValidator().validate(replace_resources(definition, resources))


def test_validator_rejects_non_absolute_or_traversing_file_path():
    definition = medium("service-config-invalid")
    resources = tuple(
        replace_attribute(resource, "path", "/opt/../etc/orders-api.conf")
        if resource.resource_id == "file-api-config"
        else resource
        for resource in definition.initial_world_state.resources
    )

    with pytest.raises(IncidentValidationError, match="nieprawidłową ścieżkę"):
        IncidentValidator().validate(replace_resources(definition, resources))


def test_validator_rejects_fault_resolution_condition_for_missing_resource():
    definition = hard("H-08")
    fault = definition.faults[0]
    condition = fault.resolution_condition.model_copy(
        update={"resource_id": "resource-missing"}
    )
    faults = (
        fault.model_copy(update={"resolution_condition": condition}),
        definition.faults[1],
    )

    with pytest.raises(IncidentValidationError, match="nieznany zasób"):
        IncidentValidator().validate(definition.model_copy(update={"faults": faults}))


def test_dependency_model_rejects_out_of_range_port():
    definition = medium("dependency-port-mismatch")
    payload = definition.service_dependencies[0].model_dump(mode="json")
    payload["port"] = 65_536

    with pytest.raises(ValidationError):
        type(definition.service_dependencies[0]).model_validate(payload)


def test_validator_rejects_dependency_port_mismatching_target_service():
    definition = medium("dependency-port-mismatch")
    dependency = definition.service_dependencies[0].model_copy(update={"port": 8081})

    with pytest.raises(IncidentValidationError, match="Port dependency"):
        IncidentValidator().validate(
            definition.model_copy(
                update={
                    "service_dependencies": (
                        dependency,
                        *definition.service_dependencies[1:],
                    )
                }
            )
        )


def test_validator_rejects_dependency_targeting_missing_service():
    definition = medium("dependency-port-mismatch")
    dependency = definition.service_dependencies[0].model_copy(
        update={"target_service_id": "service-missing"}
    )

    with pytest.raises(IncidentValidationError, match="nieznaną usługę"):
        IncidentValidator().validate(
            definition.model_copy(
                update={
                    "service_dependencies": (
                        dependency,
                        *definition.service_dependencies[1:],
                    )
                }
            )
        )


def test_validator_rejects_stale_unit_solution_without_daemon_reload():
    definition = medium("systemd-stale-unit-config")
    solution = tuple(
        step.model_copy(
            update={
                "capability_id": "systemd.status",
                "input": "systemctl status orders-api",
                "purpose": "Sprawdź stan jednostki bez przeładowania cache.",
            }
        )
        if step.capability_id == "systemd.daemon-reload"
        else step
        for step in definition.solution
    )

    with pytest.raises(IncidentValidationError, match="Replay|Reference"):
        IncidentValidator().validate(
            definition.model_copy(update={"solution": solution})
        )
