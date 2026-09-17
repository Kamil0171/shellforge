from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.admin_duty.domain.definition import (
    CapabilitySet,
    CollisionZone,
    CompletionCondition,
    ComponentReference,
    ComponentType,
    ConditionOperator,
    DataField,
    FaultInstance,
    FaultSeverity,
    GenerationMetadata,
    Hint,
    IncidentDefinition,
    IncidentPresentation,
    InitialWorldState,
    InterfaceCapability,
    MapInteraction,
    MapSnapshot,
    Objective,
    Point,
    ResourceType,
    ScoringRules,
    SolutionStep,
    Symptom,
    SymptomVisibility,
    WorldResource,
)
from app.admin_duty.domain.difficulty import DifficultyLevel


def build_incident_definition(
    scenario_id=None,
):
    map_reference = ComponentReference(
        component_type=ComponentType.MAP,
        component_id="operations-center",
        version="1.0",
    )
    environment_reference = ComponentReference(
        component_type=ComponentType.ENVIRONMENT,
        component_id="web-application",
        version="1.0",
    )

    return IncidentDefinition(
        scenario_id=scenario_id or uuid4(),
        schema_version="1.0",
        difficulty=DifficultyLevel.EASY,
        created_at=datetime(2026, 8, 24, 12, 0, tzinfo=UTC),
        generation=GenerationMetadata(
            generator_id="deterministic",
            generator_version="1.0",
            seed=42,
            components=(
                map_reference,
                environment_reference,
                ComponentReference(
                    component_type=ComponentType.FAULT,
                    component_id="systemd-exec-path",
                    version="1.0",
                ),
                ComponentReference(
                    component_type=ComponentType.OBJECTIVE,
                    component_id="restore-service",
                    version="1.0",
                ),
                ComponentReference(
                    component_type=ComponentType.SYMPTOM,
                    component_id="http-bad-gateway",
                    version="1.0",
                ),
                ComponentReference(
                    component_type=ComponentType.CAPABILITY,
                    component_id="linux-basics",
                    version="1.0",
                ),
                ComponentReference(
                    component_type=ComponentType.SCORING_POLICY,
                    component_id="lenient",
                    version="1.0",
                ),
            ),
        ),
        presentation=IncidentPresentation(
            title="Portal zwraca błąd 502",
            organization="Example Systems",
            environment_label="Produkcja",
            briefing="Monitoring wykrył problem z portalem po wdrożeniu.",
            main_objective="Przywróć dostępność portalu.",
            ticket_reference="TICKET-42",
            tags=("Linux", "systemd"),
            estimated_time_minutes=15,
        ),
        initial_world_state=InitialWorldState(
            environment_id="web-application",
            environment_version="1.0",
            map=MapSnapshot(
                map_id="operations-center",
                world_id="modern-noc",
                component_version="1.0",
                width=960,
                height=540,
                player_spawn=Point(x=590, y=430),
                collision_zones=(
                    CollisionZone(x=100, y=140, width=120, height=60),
                ),
                interactions=(
                    MapInteraction(
                        interaction_id="terminal-ops",
                        world_interaction_id="terminal",
                        capability_id="terminal",
                        label="Otwórz terminal",
                        position=Point(x=160, y=236),
                        radius=72,
                        target_resource_id="host-app",
                    ),
                ),
            ),
            resources=(
                WorldResource(
                    resource_id="host-app",
                    resource_type=ResourceType.HOST,
                    state="healthy",
                    attributes=(
                        DataField(key="hostname", value="app-01"),
                    ),
                ),
                WorldResource(
                    resource_id="service-api",
                    resource_type=ResourceType.SERVICE,
                    state="failed",
                    parent_id="host-app",
                    attributes=(
                        DataField(key="manager", value="systemd"),
                        DataField(key="port", value=8100),
                    ),
                ),
                WorldResource(
                    resource_id="endpoint-portal",
                    resource_type=ResourceType.ENDPOINT,
                    state="degraded",
                    dependencies=("service-api",),
                    attributes=(
                        DataField(
                            key="url",
                            value="https://portal.example.internal",
                        ),
                        DataField(key="status_code", value=502),
                    ),
                ),
            ),
        ),
        faults=(
            FaultInstance(
                fault_id="fault-main",
                fault_type="systemd-exec-path",
                version="1.0",
                target_resource_id="service-api",
                severity=FaultSeverity.HIGH,
                parameters=(
                    DataField(
                        key="configured_path",
                        value="/opt/example-app/venv/bin/uvicorn",
                    ),
                    DataField(
                        key="expected_path",
                        value="/srv/example-app/venv/bin/uvicorn",
                    ),
                ),
            ),
        ),
        symptoms=(
            Symptom(
                symptom_id="symptom-502",
                symptom_type="http-status",
                source_resource_id="endpoint-portal",
                visibility=SymptomVisibility.BRIEFING,
                data=(DataField(key="status_code", value=502),),
            ),
        ),
        objectives=(
            Objective(
                objective_id="restore-service",
                label="Przywróć usługę aplikacyjną",
                completion_condition=CompletionCondition(
                    resource_id="service-api",
                    field="state",
                    operator=ConditionOperator.EQUALS,
                    expected="active",
                ),
                order=1,
            ),
        ),
        capabilities=CapabilitySet(
            interfaces=(
                InterfaceCapability.TERMINAL,
                InterfaceCapability.MONITORING,
            ),
            command_capability_ids=(
                "filesystem.read",
                "systemd.inspect",
                "systemd.restart",
            ),
        ),
        scoring=ScoringRules(
            policy_id="lenient",
            initial_score=1000,
            command_cost=5,
            solution_penalty=250,
            solution_score_cap=500,
        ),
        hints=(
            Hint(
                order=1,
                text="Sprawdź stan usługi za reverse proxy.",
                cost=25,
            ),
        ),
        solution=(
            SolutionStep(
                order=1,
                capability_id="systemd.inspect",
                input="systemctl status example-api",
                purpose="Sprawdź stan usługi aplikacyjnej.",
            ),
        ),
    )


def incident_payload():
    return build_incident_definition().model_dump(mode="json")


def test_valid_minimal_incident_definition_can_be_created():
    incident = build_incident_definition()

    assert isinstance(incident.scenario_id, UUID)
    assert incident.schema_version == "1.0"
    assert incident.difficulty is DifficultyLevel.EASY
    assert len(incident.faults) == 1


def test_incident_definition_json_round_trip():
    incident = build_incident_definition()

    restored = IncidentDefinition.model_validate_json(incident.model_dump_json())

    assert restored == incident
    assert restored.initial_world_state.map.component_version == "1.0"


def test_incident_definition_is_deeply_immutable():
    incident = build_incident_definition()

    with pytest.raises(ValidationError):
        incident.difficulty = DifficultyLevel.HARD

    with pytest.raises(ValidationError):
        incident.presentation.title = "Zmieniony tytuł"

    with pytest.raises(ValidationError):
        incident.faults[0].parameters[0].value = "inna wartość"

    assert isinstance(incident.faults, tuple)
    assert isinstance(incident.faults[0].parameters, tuple)


def test_extra_fields_are_rejected():
    payload = incident_payload()
    payload["unexpected"] = True

    with pytest.raises(ValidationError):
        IncidentDefinition.model_validate(payload)


def test_invalid_scenario_id_is_rejected():
    payload = incident_payload()
    payload["scenario_id"] = "not-a-uuid"

    with pytest.raises(ValidationError):
        IncidentDefinition.model_validate(payload)


def test_difficulty_uses_difficulty_level():
    incident = build_incident_definition()

    assert incident.difficulty is DifficultyLevel.EASY

    payload = incident_payload()
    payload["difficulty"] = "unsupported"

    with pytest.raises(ValidationError):
        IncidentDefinition.model_validate(payload)


@pytest.mark.parametrize("schema_version", [None, "", "1", "2.0"])
def test_schema_version_is_required_and_versioned(schema_version):
    payload = incident_payload()

    if schema_version is None:
        payload.pop("schema_version")
    else:
        payload["schema_version"] = schema_version

    with pytest.raises(ValidationError):
        IncidentDefinition.model_validate(payload)


def test_empty_component_identifier_is_rejected():
    payload = incident_payload()
    payload["generation"]["components"][0]["component_id"] = ""

    with pytest.raises(ValidationError):
        IncidentDefinition.model_validate(payload)


@pytest.mark.parametrize("fault_count", [0, 3])
def test_definition_requires_between_one_and_two_faults(fault_count):
    payload = incident_payload()
    source_fault = payload["faults"][0]
    payload["faults"] = [source_fault for _ in range(fault_count)]

    with pytest.raises(ValidationError):
        IncidentDefinition.model_validate(payload)


def test_fault_parameters_are_json_serializable_and_immutable():
    field = DataField(
        key="accepted_statuses",
        value=(200, 204),
    )

    assert field.model_dump(mode="json") == {
        "key": "accepted_statuses",
        "value": [200, 204],
    }
    assert isinstance(field.value, tuple)

    with pytest.raises(ValidationError):
        field.value = (500,)


@pytest.mark.parametrize(
    "invalid_value",
    [
        {"nested": "object"},
        object(),
        lambda: None,
        float("nan"),
    ],
)
def test_data_field_rejects_arbitrary_python_objects(invalid_value):
    with pytest.raises(ValidationError):
        DataField(key="invalid", value=invalid_value)


def test_objective_condition_rejects_callable():
    payload = incident_payload()
    payload["objectives"][0]["completion_condition"]["expected"] = lambda: True

    with pytest.raises(ValidationError):
        IncidentDefinition.model_validate(payload)


def test_initial_world_state_contains_replayable_map_runtime_data():
    incident = build_incident_definition()
    map_snapshot = incident.initial_world_state.map

    assert map_snapshot.map_id == "operations-center"
    assert map_snapshot.component_version == "1.0"
    assert map_snapshot.player_spawn == Point(x=590, y=430)
    assert map_snapshot.collision_zones
    assert map_snapshot.interactions[0].capability_id == "terminal"
    assert len(incident.initial_world_state.resources) == 3


def test_map_snapshot_must_match_versioned_component_reference():
    payload = incident_payload()
    payload["initial_world_state"]["map"]["component_version"] = "2.0"

    with pytest.raises(
        ValidationError,
        match="Snapshot mapy nie odpowiada referencji komponentu",
    ):
        IncidentDefinition.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("title", "x" * 121),
        ("briefing", "x" * 4001),
        ("main_objective", "x" * 601),
    ],
)
def test_presentation_text_limits_are_enforced(field, value):
    payload = incident_payload()
    payload["presentation"][field] = value

    with pytest.raises(ValidationError):
        IncidentDefinition.model_validate(payload)


def test_different_scenario_ids_can_share_the_same_component_snapshot():
    first = build_incident_definition(scenario_id=uuid4())
    second = build_incident_definition(scenario_id=uuid4())

    assert first.scenario_id != second.scenario_id
    assert first.generation == second.generation
    assert first.initial_world_state == second.initial_world_state
    assert first.faults == second.faults
