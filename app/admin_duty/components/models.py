from enum import StrEnum
from string import Formatter

from pydantic import Field, model_validator

from app.admin_duty.domain.definition import (
    CompletionCondition,
    DataField,
    FaultSeverity,
    FrozenDomainModel,
    Hint,
    Identifier,
    JsonValue,
    MapSnapshot,
    ResourceType,
    SymptomVisibility,
    Version,
    WorldResource,
)
from app.admin_duty.domain.difficulty import DifficultyLevel


class ResourceRole(StrEnum):
    PRIMARY_SERVICE = "primary_service"
    PRIMARY_HOST = "primary_host"
    SUPPORT_HOST = "support_host"
    EXECUTABLE_FILE = "executable_file"


class ComponentMetadata(FrozenDomainModel):
    label: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=600)


class ResourceBinding(FrozenDomainModel):
    role: ResourceRole
    resource_id: Identifier


class EnvironmentTemplate(FrozenDomainModel):
    component_id: Identifier
    version: Version
    metadata: ComponentMetadata
    compatible_difficulties: tuple[DifficultyLevel, ...] = Field(min_length=1)
    organization: str = Field(min_length=1, max_length=120)
    environment_label: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=120)
    briefing: str = Field(min_length=1, max_length=2000)
    main_objective: str = Field(min_length=1, max_length=400)
    ticket_prefix: Identifier
    tags: tuple[str, ...] = Field(default=(), max_length=12)
    map_component_id: Identifier
    resources: tuple[WorldResource, ...] = Field(min_length=1)
    bindings: tuple[ResourceBinding, ...] = Field(min_length=4)
    context: tuple[DataField, ...] = Field(default=(), max_length=32)

    @model_validator(mode="after")
    def validate_bindings(self):
        resource_ids = {resource.resource_id for resource in self.resources}
        roles = [binding.role for binding in self.bindings]

        if len(roles) != len(set(roles)):
            raise ValueError("Role zasobów środowiska muszą być unikalne.")

        if any(binding.resource_id not in resource_ids for binding in self.bindings):
            raise ValueError("Binding środowiska wskazuje nieznany zasób.")

        return self


class MapTemplate(FrozenDomainModel):
    component_id: Identifier
    version: Version
    metadata: ComponentMetadata
    snapshot: MapSnapshot

    @model_validator(mode="after")
    def validate_snapshot_identity(self):
        if (
            self.snapshot.map_id != self.component_id
            or self.snapshot.component_version != self.version
        ):
            raise ValueError("Snapshot mapy nie odpowiada template mapy.")

        return self


class StateMutationTemplate(FrozenDomainModel):
    resource_role: ResourceRole
    new_state: Identifier


class AttributeMutationTemplate(FrozenDomainModel):
    resource_role: ResourceRole
    attribute: Identifier | None = None
    attribute_context_key: Identifier | None = None
    attribute_prefix: str = Field(default="", max_length=32)
    value: JsonValue = None
    value_context_key: Identifier | None = None
    remove: bool = False

    @model_validator(mode="after")
    def validate_sources(self):
        if (self.attribute is None) == (self.attribute_context_key is None):
            raise ValueError("Mutacja wymaga dokładnie jednego źródła nazwy pola.")

        if self.attribute is not None and self.attribute_prefix:
            raise ValueError("Prefix pola wymaga nazwy pobieranej z context.")

        if self.remove and self.value_context_key is not None:
            raise ValueError("Mutacja usuwająca nie może definiować wartości.")

        return self


class SymptomTemplate(FrozenDomainModel):
    component_id: Identifier
    version: Version
    symptom_id: Identifier
    symptom_type: Identifier
    source_role: ResourceRole | None = None
    visibility: SymptomVisibility
    data: tuple[DataField, ...] = Field(default=(), max_length=64)


class ObjectiveTemplate(FrozenDomainModel):
    component_id: Identifier
    version: Version
    objective_id_template: str = Field(min_length=1, max_length=160)
    label_template: str = Field(min_length=1, max_length=240)
    resource_role: ResourceRole
    condition: CompletionCondition
    required: bool = True
    order: int = Field(ge=1, le=100)
    weight: int = Field(default=1, ge=1, le=100)


class SolutionStepTemplate(FrozenDomainModel):
    order: int = Field(ge=1, le=200)
    capability_id: Identifier
    input_template: str = Field(min_length=1, max_length=1024)
    purpose: str = Field(min_length=1, max_length=600)

    @model_validator(mode="after")
    def validate_placeholders(self):
        for _, field_name, _, _ in Formatter().parse(self.input_template):
            if field_name is not None:
                if not field_name.replace("_", "a").isalnum():
                    raise ValueError(
                        "Template komendy zawiera nieprawidłowy placeholder."
                    )

        return self


class FaultTemplate(FrozenDomainModel):
    component_id: Identifier
    version: Version
    metadata: ComponentMetadata
    fault_type: Identifier
    compatible_difficulties: tuple[DifficultyLevel, ...] = Field(min_length=1)
    target_role: ResourceRole
    required_resource_types: tuple[ResourceType, ...] = Field(min_length=1)
    required_context_keys: tuple[Identifier, ...] = Field(default=())
    severity: FaultSeverity
    state_mutations: tuple[StateMutationTemplate, ...] = Field(min_length=1)
    attribute_mutations: tuple[AttributeMutationTemplate, ...] = Field(default=())
    required_capabilities: tuple[Identifier, ...] = Field(min_length=1)
    symptom: SymptomTemplate
    objective: ObjectiveTemplate
    hints: tuple[Hint, ...] = Field(min_length=1, max_length=3)
    solution: tuple[SolutionStepTemplate, ...] = Field(min_length=1)
    briefing_addition: str = Field(min_length=1, max_length=1000)
    forbidden_public_terms: tuple[str, ...] = Field(min_length=1, max_length=16)
