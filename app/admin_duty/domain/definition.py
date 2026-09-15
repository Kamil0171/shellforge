from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

from app.admin_duty.domain.difficulty import DifficultyLevel

Identifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$",
    ),
]
Version = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._+-]*$",
    ),
]
type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | tuple[JsonScalar, ...]


class FrozenDomainModel(BaseModel):
    model_config = ConfigDict(
        allow_inf_nan=False,
        extra="forbid",
        frozen=True,
    )


class ComponentType(StrEnum):
    MAP = "map"
    ENVIRONMENT = "environment"
    FAULT = "fault"
    OBJECTIVE = "objective"
    SYMPTOM = "symptom"
    CAPABILITY = "capability"
    SCORING_POLICY = "scoring_policy"


class ResourceType(StrEnum):
    HOST = "host"
    SERVICE = "service"
    FILE = "file"
    PROCESS = "process"
    LISTENER = "listener"
    ENDPOINT = "endpoint"
    DOMAIN = "domain"


class DependencyType(StrEnum):
    SERVICE = "service"
    NETWORK = "network"


class NetworkProtocol(StrEnum):
    TCP = "tcp"
    UDP = "udp"
    HTTP = "http"
    HTTPS = "https"


class ObjectiveType(StrEnum):
    CONFIRM_SYMPTOM = "confirm_symptom"
    INSPECT_SERVICE = "inspect_service"
    IDENTIFY_DEPENDENCY = "identify_dependency"
    RESTORE_DEPENDENCY = "restore_dependency"
    VERIFY_SERVICE = "verify_service"
    VERIFY_END_TO_END = "verify_end_to_end"


class GenerationSource(StrEnum):
    DETERMINISTIC = "deterministic"
    AI = "ai"


class ValidationStatus(StrEnum):
    DRAFT = "draft"
    VALID = "valid"
    INVALID = "invalid"


class FaultSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FaultRelationType(StrEnum):
    DEPENDENCY_CHAIN = "dependency_chain"


class IncidentRecoveryState(StrEnum):
    BROKEN = "broken"
    PARTIALLY_RECOVERED = "partially_recovered"
    HEALTHY = "healthy"


class SymptomVisibility(StrEnum):
    BRIEFING = "briefing"
    MONITORING = "monitoring"
    DIAGNOSTIC = "diagnostic"
    HIDDEN = "hidden"


class ConditionOperator(StrEnum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    CONTAINS = "contains"


class InterfaceCapability(StrEnum):
    TERMINAL = "terminal"
    MONITORING = "monitoring"
    TICKET = "ticket"
    FILE_EDITOR = "file_editor"


class DataField(FrozenDomainModel):
    key: Identifier
    value: JsonValue


class ComponentReference(FrozenDomainModel):
    component_type: ComponentType
    component_id: Identifier
    version: Version


class GenerationMetadata(FrozenDomainModel):
    generator_id: Identifier
    generator_version: Version
    seed: int | None = Field(
        default=None,
        ge=0,
        le=2**63 - 1,
    )
    components: tuple[ComponentReference, ...] = Field(
        min_length=2,
        max_length=128,
    )
    generation_source: GenerationSource = GenerationSource.DETERMINISTIC
    model: str | None = Field(default=None, min_length=1, max_length=120)


class IncidentPresentation(FrozenDomainModel):
    title: str = Field(min_length=1, max_length=120)
    organization: str = Field(min_length=1, max_length=120)
    environment_label: str = Field(min_length=1, max_length=80)
    briefing: str = Field(min_length=1, max_length=4000)
    main_objective: str = Field(min_length=1, max_length=600)
    ticket_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
    )
    tags: tuple[Annotated[str, Field(min_length=1, max_length=40)], ...] = Field(
        default=(), max_length=12
    )
    estimated_time_minutes: int = Field(ge=1, le=240)


class Point(FrozenDomainModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)


class CollisionZone(FrozenDomainModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)


class MapInteraction(FrozenDomainModel):
    interaction_id: Identifier
    capability_id: Identifier
    label: str = Field(min_length=1, max_length=160)
    position: Point
    radius: float = Field(gt=0, le=1000)
    target_resource_id: Identifier | None = None
    parameters: tuple[DataField, ...] = Field(default=(), max_length=32)


class MapSnapshot(FrozenDomainModel):
    map_id: Identifier
    component_version: Version
    width: int = Field(ge=1, le=10000)
    height: int = Field(ge=1, le=10000)
    player_spawn: Point
    collision_zones: tuple[CollisionZone, ...] = Field(
        default=(),
        max_length=512,
    )
    interactions: tuple[MapInteraction, ...] = Field(
        min_length=1,
        max_length=128,
    )
    parameters: tuple[DataField, ...] = Field(default=(), max_length=32)

    @model_validator(mode="after")
    def validate_coordinates(self):
        points = [
            self.player_spawn,
            *(interaction.position for interaction in self.interactions),
        ]

        if any(point.x > self.width or point.y > self.height for point in points):
            raise ValueError("Punkt mapy znajduje się poza jej granicami.")

        if any(
            zone.x + zone.width > self.width or zone.y + zone.height > self.height
            for zone in self.collision_zones
        ):
            raise ValueError("Strefa kolizji znajduje się poza granicami mapy.")

        return self


class WorldResource(FrozenDomainModel):
    resource_id: Identifier
    resource_type: ResourceType
    state: Identifier
    parent_id: Identifier | None = None
    dependencies: tuple[Identifier, ...] = Field(default=(), max_length=32)
    attributes: tuple[DataField, ...] = Field(default=(), max_length=64)


class ServiceDependency(FrozenDomainModel):
    dependency_id: Identifier
    source_host_id: Identifier
    source_service_id: Identifier
    target_service_id: Identifier
    target_host_id: Identifier
    dependency_type: DependencyType
    protocol: NetworkProtocol
    port: int = Field(ge=1, le=65535)
    required: bool = True
    publicly_visible: bool = True


class PackageRequirement(FrozenDomainModel):
    requirement_id: Identifier
    service_id: Identifier
    host_id: Identifier
    package_name: Identifier


class ConfigurationRequirement(FrozenDomainModel):
    requirement_id: Identifier
    service_id: Identifier
    host_id: Identifier
    file_resource_id: Identifier


class SymptomPropagationRule(FrozenDomainModel):
    rule_id: Identifier
    dependency_id: Identifier
    affected_resource_id: Identifier
    unhealthy_state: Identifier
    healthy_state: Identifier


class InitialWorldState(FrozenDomainModel):
    environment_id: Identifier
    environment_version: Version
    map: MapSnapshot
    resources: tuple[WorldResource, ...] = Field(
        min_length=1,
        max_length=1024,
    )


class CompletionCondition(FrozenDomainModel):
    resource_id: Identifier
    field: Identifier
    operator: ConditionOperator
    expected: JsonValue = None


class FaultInstance(FrozenDomainModel):
    fault_id: Identifier
    fault_type: Identifier
    version: Version
    target_resource_id: Identifier
    severity: FaultSeverity
    parameters: tuple[DataField, ...] = Field(default=(), max_length=64)
    resolution_condition: CompletionCondition | None = None


class FaultRelation(FrozenDomainModel):
    relation_type: FaultRelationType
    primary_fault_id: Identifier
    secondary_fault_id: Identifier


class Symptom(FrozenDomainModel):
    symptom_id: Identifier
    symptom_type: Identifier
    source_resource_id: Identifier | None = None
    visibility: SymptomVisibility
    misleading: bool = False
    data: tuple[DataField, ...] = Field(default=(), max_length=64)


class Objective(FrozenDomainModel):
    objective_id: Identifier
    label: str = Field(min_length=1, max_length=240)
    required: bool = True
    completion_condition: CompletionCondition | None = None
    order: int = Field(ge=1, le=100)
    weight: int = Field(default=1, ge=1, le=100)
    objective_type: ObjectiveType = ObjectiveType.RESTORE_DEPENDENCY
    completion_fact_ids: tuple[Identifier, ...] = Field(default=(), max_length=16)


class CapabilitySet(FrozenDomainModel):
    interfaces: tuple[InterfaceCapability, ...] = Field(
        min_length=1,
        max_length=len(InterfaceCapability),
    )
    command_capability_ids: tuple[Identifier, ...] = Field(
        min_length=1,
        max_length=128,
    )


class ScoringRules(FrozenDomainModel):
    policy_id: Identifier
    initial_score: int = Field(ge=0, le=1_000_000)
    command_cost: int = Field(ge=0, le=100_000)
    solution_penalty: int = Field(ge=0, le=1_000_000)
    solution_score_cap: int | None = Field(
        default=None,
        ge=0,
        le=1_000_000,
    )


class Hint(FrozenDomainModel):
    order: int = Field(ge=1, le=100)
    text: str = Field(min_length=1, max_length=1000)
    cost: int = Field(ge=0, le=100_000)


class SolutionStep(FrozenDomainModel):
    order: int = Field(ge=1, le=200)
    capability_id: Identifier
    input: str = Field(min_length=1, max_length=32768)
    purpose: str = Field(min_length=1, max_length=600)
    parameters: tuple[DataField, ...] = Field(default=(), max_length=64)
    expected_success: bool = True


class PostIncidentDefinition(FrozenDomainModel):
    root_cause: str = Field(min_length=1, max_length=1000)
    affected_service_ids: tuple[Identifier, ...] = Field(min_length=1, max_length=64)
    repair_capability_ids: tuple[Identifier, ...] = Field(min_length=1, max_length=64)
    root_cause_chain: tuple[str, ...] = Field(default=(), max_length=8)
    primary_fault: str | None = Field(default=None, min_length=1, max_length=500)
    secondary_fault: str | None = Field(default=None, min_length=1, max_length=500)
    impact_path: tuple[str, ...] = Field(default=(), max_length=16)
    repair_sequence: tuple[str, ...] = Field(default=(), max_length=16)
    partial_recovery_explanation: str | None = Field(
        default=None, min_length=1, max_length=1000
    )
    learning_summary: str | None = Field(default=None, min_length=1, max_length=1000)


class ScenarioPoolMetadata(FrozenDomainModel):
    scenario_id: UUID
    generation_source: GenerationSource
    model: str | None = Field(default=None, min_length=1, max_length=120)
    created_at: AwareDatetime
    difficulty: DifficultyLevel
    validation_status: ValidationStatus
    quality_score: int | None = Field(default=None, ge=0, le=100)
    quality_version: Version
    provider: Identifier | None = None
    schema_version: Literal["1.0", "3.0", "4.0"] = "3.0"


class IncidentDefinition(FrozenDomainModel):
    scenario_id: UUID
    schema_version: Literal["1.0", "3.0", "4.0"]
    difficulty: DifficultyLevel
    created_at: AwareDatetime
    generation: GenerationMetadata
    presentation: IncidentPresentation
    initial_world_state: InitialWorldState
    faults: tuple[FaultInstance, ...] = Field(min_length=1, max_length=2)
    fault_relation: FaultRelation | None = None
    symptoms: tuple[Symptom, ...] = Field(min_length=1, max_length=128)
    objectives: tuple[Objective, ...] = Field(min_length=1, max_length=64)
    capabilities: CapabilitySet
    scoring: ScoringRules
    hints: tuple[Hint, ...] = Field(default=(), max_length=20)
    solution: tuple[SolutionStep, ...] = Field(min_length=1, max_length=200)
    service_dependencies: tuple[ServiceDependency, ...] = Field(
        default=(), max_length=128
    )
    package_requirements: tuple[PackageRequirement, ...] = Field(
        default=(), max_length=128
    )
    configuration_requirements: tuple[ConfigurationRequirement, ...] = Field(
        default=(), max_length=128
    )
    symptom_propagation: tuple[SymptomPropagationRule, ...] = Field(
        default=(), max_length=128
    )
    post_incident: PostIncidentDefinition | None = None

    @model_validator(mode="after")
    def validate_component_snapshots(self):
        map_reference = self._get_single_component_reference(ComponentType.MAP)
        environment_reference = self._get_single_component_reference(
            ComponentType.ENVIRONMENT
        )
        map_snapshot = self.initial_world_state.map

        if (
            map_reference.component_id != map_snapshot.map_id
            or map_reference.version != map_snapshot.component_version
        ):
            raise ValueError("Snapshot mapy nie odpowiada referencji komponentu.")

        if (
            environment_reference.component_id
            != self.initial_world_state.environment_id
            or environment_reference.version
            != self.initial_world_state.environment_version
        ):
            raise ValueError("Snapshot środowiska nie odpowiada referencji komponentu.")

        return self

    def _get_single_component_reference(
        self,
        component_type: ComponentType,
    ) -> ComponentReference:
        references = [
            reference
            for reference in self.generation.components
            if reference.component_type is component_type
        ]

        if len(references) != 1:
            raise ValueError(
                "Definicja wymaga dokładnie jednej referencji komponentu "
                f"typu {component_type.value}."
            )

        return references[0]
