import pytest
from pydantic import ValidationError

from app.admin_duty.components import (
    ENVIRONMENT_TEMPLATES,
    FAULT_TEMPLATES,
    MAP_TEMPLATES,
    ResourceRole,
)
from app.admin_duty.domain.definition import ResourceType
from app.admin_duty.domain.difficulty import DifficultyLevel


def test_catalog_contains_three_easy_environments_and_matching_maps():
    assert {item.component_id for item in ENVIRONMENT_TEMPLATES} == {
        "web-application",
        "internal-business-service",
        "reverse-proxy-stack",
    }
    assert len(MAP_TEMPLATES) == 3
    assert {item.map_component_id for item in ENVIRONMENT_TEMPLATES} == {
        item.component_id for item in MAP_TEMPLATES
    }

    for environment in ENVIRONMENT_TEMPLATES:
        hosts = [
            resource
            for resource in environment.resources
            if resource.resource_type is ResourceType.HOST
        ]
        assert len(hosts) == 2
        assert DifficultyLevel.EASY in environment.compatible_difficulties

    for template in MAP_TEMPLATES:
        assert template.snapshot.width == 1800
        assert template.snapshot.height == 1100
        assert {item.capability_id for item in template.snapshot.interactions} == {
            "terminal",
            "monitoring",
            "rack",
            "support",
        }
        assert len(template.snapshot.collision_zones) >= 18


def test_environment_baselines_are_healthy_and_have_required_roles():
    expected_roles = {
        ResourceRole.PRIMARY_SERVICE,
        ResourceRole.PRIMARY_HOST,
        ResourceRole.SUPPORT_HOST,
        ResourceRole.EXECUTABLE_FILE,
    }

    for environment in ENVIRONMENT_TEMPLATES:
        resources = {item.resource_id: item for item in environment.resources}
        bindings = {item.role: item.resource_id for item in environment.bindings}
        service = resources[bindings[ResourceRole.PRIMARY_SERVICE]]
        executable = resources[bindings[ResourceRole.EXECUTABLE_FILE]]
        service_attributes = {item.key: item.value for item in service.attributes}
        file_attributes = {item.key: item.value for item in executable.attributes}

        assert set(bindings) == expected_roles
        assert service.state == "running"
        assert (
            service_attributes["configured_exec_start"]
            == service_attributes["expected_exec_start"]
        )
        variable = service_attributes["required_environment_variable"]
        assert (
            service_attributes[f"environment.{variable}"]
            == service_attributes["expected_environment_value"]
        )
        assert file_attributes["current_mode"] == file_attributes["expected_mode"]


def test_catalog_contains_four_distinct_solvable_fault_specs():
    assert {item.fault_type for item in FAULT_TEMPLATES} == {
        "systemd_service_failed",
        "systemd_wrong_exec_start",
        "systemd_missing_environment_variable",
        "systemd_permission_denied",
    }
    assert len({item.required_capabilities for item in FAULT_TEMPLATES}) == 3
    assert len({item.fault_type for item in FAULT_TEMPLATES}) == 4

    for fault in FAULT_TEMPLATES:
        assert fault.state_mutations
        assert fault.symptom
        assert fault.objective.required is True
        assert 1 <= len(fault.hints) <= 3
        assert fault.solution
        assert fault.forbidden_public_terms


def test_component_templates_are_deeply_immutable_and_json_serializable():
    environment = ENVIRONMENT_TEMPLATES[0]
    restored = type(environment).model_validate_json(environment.model_dump_json())

    assert restored == environment

    with pytest.raises(ValidationError):
        environment.organization = "Zmieniona organizacja"

    with pytest.raises(ValidationError):
        environment.resources[0].state = "failed"
