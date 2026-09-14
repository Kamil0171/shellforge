from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.admin_duty.components.scenarios import build_medium_draft
from app.admin_duty.domain.definition import ServiceDependency
from app.admin_duty.domain.generation import convert_draft_to_definition
from app.admin_duty.validators import IncidentValidationError, IncidentValidator

NOW = datetime(2026, 9, 8, 12, 0, tzinfo=UTC)


def definition(category="dependency-firewall-blocked"):
    return convert_draft_to_definition(
        build_medium_draft(category, seed=17),
        created_at=NOW,
    )


def replace_dependencies(value, dependencies):
    return value.model_copy(update={"service_dependencies": dependencies})


def test_incident_definition_v3_round_trips_and_is_immutable():
    value = definition()

    restored = type(value).model_validate_json(value.model_dump_json())

    assert restored == value
    assert restored.schema_version == "3.0"
    with pytest.raises(ValidationError):
        restored.service_dependencies[0].port = 9999


def test_validator_accepts_typed_multi_service_chain():
    value = IncidentValidator().validate(definition())

    assert [item.dependency_id for item in value.service_dependencies] == [
        "dep-proxy-api",
        "dep-api-database",
    ]
    assert all(isinstance(item, ServiceDependency) for item in value.service_dependencies)


@pytest.mark.parametrize(
    ("field", "replacement", "message"),
    [
        ("source_service_id", "missing-service", "nieznaną usługę"),
        ("target_service_id", "missing-service", "nieznaną usługę"),
        ("source_host_id", "missing-host", "host źródłowy"),
        ("target_host_id", "missing-host", "nieznany host"),
    ],
)
def test_validator_rejects_dangling_dependency_references(field, replacement, message):
    value = definition()
    dependency = value.service_dependencies[0].model_copy(update={field: replacement})

    with pytest.raises(IncidentValidationError, match=message):
        IncidentValidator().validate(
            replace_dependencies(value, (dependency, *value.service_dependencies[1:]))
        )


def test_validator_rejects_self_dependency():
    value = definition()
    dependency = value.service_dependencies[0].model_copy(
        update={
            "target_service_id": "service-proxy",
            "target_host_id": "host-edge-01",
            "port": 80,
        }
    )

    with pytest.raises(IncidentValidationError, match="samej siebie"):
        IncidentValidator().validate(
            replace_dependencies(value, (dependency, *value.service_dependencies[1:]))
        )


def test_validator_rejects_dependency_cycle():
    value = definition()
    cycle = value.service_dependencies[0].model_copy(
        update={
            "dependency_id": "dep-database-proxy",
            "source_host_id": "host-data-01",
            "source_service_id": "service-database",
            "target_host_id": "host-edge-01",
            "target_service_id": "service-proxy",
            "port": 80,
        }
    )

    with pytest.raises(IncidentValidationError, match="cykl"):
        IncidentValidator().validate(
            replace_dependencies(value, (*value.service_dependencies, cycle))
        )


def test_validator_rejects_dependency_port_mismatch():
    value = definition()
    dependency = value.service_dependencies[0].model_copy(update={"port": 9000})

    with pytest.raises(IncidentValidationError, match="Port dependency"):
        IncidentValidator().validate(
            replace_dependencies(value, (dependency, *value.service_dependencies[1:]))
        )


def test_medium_definition_rejects_two_related_faults():
    value = definition()
    second = value.faults[0].model_copy(update={"fault_id": "fault-related-secondary"})

    with pytest.raises(IncidentValidationError, match="Liczba faultów"):
        IncidentValidator().validate(
            value.model_copy(update={"faults": (*value.faults, second)})
        )
