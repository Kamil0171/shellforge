import json
from datetime import UTC, datetime
from functools import cache
from typing import Literal, Protocol
from uuid import UUID, uuid4

from pydantic import AwareDatetime, Field

from app.admin_duty.domain.definition import (
    CapabilitySet,
    ComponentReference,
    ConfigurationRequirement,
    FaultInstance,
    FaultRelation,
    FrozenDomainModel,
    GenerationMetadata,
    GenerationSource,
    Hint,
    Identifier,
    IncidentDefinition,
    IncidentPresentation,
    InitialWorldState,
    Objective,
    PackageRequirement,
    PostIncidentDefinition,
    ResourceType,
    ScoringRules,
    ServiceDependency,
    SolutionStep,
    Symptom,
    SymptomPropagationRule,
    Version,
)
from app.admin_duty.domain.difficulty import DifficultyLevel, get_difficulty_profile


class IncidentGenerationRequest(FrozenDomainModel):
    difficulty: DifficultyLevel
    environment_preferences: tuple[Identifier, ...] = Field(default=(), max_length=16)
    allowed_fault_categories: tuple[Identifier, ...] = Field(default=(), max_length=32)
    map_id: Identifier | None = None
    lesson_id: int | None = Field(default=None, ge=1)
    lesson_topic: str | None = Field(default=None, min_length=1, max_length=160)
    skill_tags: tuple[Identifier, ...] = Field(default=(), max_length=32)
    seed: int | None = Field(default=None, ge=0, le=2**63 - 1)
    generation_source: GenerationSource = GenerationSource.DETERMINISTIC
    validation_feedback: tuple[Literal[
        "schema", "plan", "materialization", "capability", "semantic", "replay", "request_mismatch",
        "timeout", "transport", "api_error", "rate_limit", "unavailable",
        "rejected", "invalid_response", "invalid_json",
    ], ...] = Field(default=(), max_length=1)


class GeneratedIncidentDraft(FrozenDomainModel):
    draft_id: Identifier
    schema_version: Literal["3.0", "4.0"]
    difficulty: DifficultyLevel
    generator_id: Identifier
    generator_version: Version
    generation_source: GenerationSource
    model: str | None = Field(default=None, min_length=1, max_length=120)
    seed: int | None = Field(default=None, ge=0, le=2**63 - 1)
    components: tuple[ComponentReference, ...] = Field(min_length=2, max_length=128)
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
    post_incident: PostIncidentDefinition


class IncidentAIProvider(Protocol):
    async def generate_incident(
        self,
        request: IncidentGenerationRequest,
    ) -> GeneratedIncidentDraft: ...


class FakeIncidentAIProvider:
    def __init__(self, draft: GeneratedIncidentDraft) -> None:
        self._draft = draft

    async def generate_incident(
        self,
        request: IncidentGenerationRequest,
    ) -> GeneratedIncidentDraft:
        if request.generation_source is not GenerationSource.AI:
            raise ValueError("Fake provider wymaga generation_source=ai.")
        if request.difficulty is not self._draft.difficulty:
            raise ValueError("Draft nie odpowiada żądanemu poziomowi trudności.")
        return self._draft.model_copy(deep=True)


class DifficultyCapability(FrozenDomainModel):
    difficulty: DifficultyLevel
    min_hosts: int
    max_hosts: int
    min_faults: int
    max_faults: int
    hint_limit: int


class AICapabilityCatalog(FrozenDomainModel):
    supported_services: tuple[Identifier, ...]
    supported_commands: tuple[Identifier, ...]
    supported_fault_categories: tuple[Identifier, ...]
    supported_dependency_types: tuple[Identifier, ...]
    supported_packages: tuple[Identifier, ...]
    supported_rocky_subsystems: tuple[Identifier, ...]
    supported_package_operations: tuple[Identifier, ...]
    supported_network_features: tuple[Identifier, ...]
    supported_selinux_features: tuple[Identifier, ...]
    supported_firewall_features: tuple[Identifier, ...]
    supported_maps: tuple[Identifier, ...]
    supported_map_interactions: tuple[Identifier, ...]
    difficulty_constraints: tuple[DifficultyCapability, ...]
    supported_resource_attributes: tuple[Identifier, ...]
    supported_fault_types: tuple[Identifier, ...]


@cache
def get_ai_capability_catalog() -> AICapabilityCatalog:
    from app.admin_duty.components import ENVIRONMENT_TEMPLATES, FAULT_TEMPLATES
    from app.admin_duty.components.maps import MAP_TEMPLATES
    from app.admin_duty.components.scenarios import (
        HARD_COMBINATIONS,
        MEDIUM_SCENARIO_CATEGORIES,
        build_hard_draft,
        build_medium_draft,
    )
    from app.admin_duty.rocky.registry import HANDLERS

    examples = (
        *(build_medium_draft(category, seed=1) for category in MEDIUM_SCENARIO_CATEGORIES),
        *(build_hard_draft(item.combination_id, seed=1) for item in HARD_COMBINATIONS),
    )
    return AICapabilityCatalog(
        supported_resource_attributes=tuple(sorted({
            field.key
            for resources in (
                *(environment.resources for environment in ENVIRONMENT_TEMPLATES),
                *(example.initial_world_state.resources for example in examples),
            )
            for resource in resources for field in resource.attributes
        })),
        supported_fault_types=tuple(sorted({fault.fault_type for fault in FAULT_TEMPLATES} | {
            fault.fault_type for example in examples for fault in example.faults
        })),
        supported_services=(
            "systemd-service",
            "reverse-proxy",
            "web-api",
            "database",
            "worker",
        ),
        supported_commands=tuple(sorted(HANDLERS)),
        supported_fault_categories=(
            "systemd-service-failed",
            "systemd-wrong-exec-start",
            "systemd-missing-environment-variable",
            "systemd-permission-denied",
            "dependency-firewall-blocked",
            "dependency-package-missing",
            "selinux-context-invalid",
            "networkmanager-dns-invalid",
            "external-firewall-mismatch",
            "service-config-invalid",
            "dependency-port-mismatch",
            "networkmanager-connection-inactive",
        ),
        supported_dependency_types=("network", "service"),
        supported_packages=(
            "bash",
            "bind-utils",
            "nginx",
            "policycoreutils-python-utils",
            "python3-psycopg2",
            "rocky-release",
            "systemd",
        ),
        supported_rocky_subsystems=(
            "filesystem",
            "firewalld",
            "network",
            "networkmanager",
            "packages",
            "processes",
            "selinux",
            "systemd",
        ),
        supported_package_operations=("info", "install", "list", "remove", "update"),
        supported_network_features=(
            "curl",
            "dns",
            "listeners",
            "networkmanager",
            "ping",
            "virtual-ssh",
        ),
        supported_selinux_features=("inspect", "restore-context", "set-mode"),
        supported_firewall_features=(
            "inspect",
            "runtime-port",
            "permanent-port",
            "reload",
        ),
        supported_maps=tuple(sorted(template.component_id for template in MAP_TEMPLATES)),
        supported_map_interactions=tuple(sorted({
            interaction.capability_id
            for template in MAP_TEMPLATES for interaction in template.snapshot.interactions
        })),
        difficulty_constraints=tuple(
            DifficultyCapability(
                difficulty=level,
                min_hosts=(profile := get_difficulty_profile(level)).min_hosts,
                max_hosts=profile.max_hosts,
                min_faults=profile.min_faults,
                max_faults=profile.max_faults,
                hint_limit=profile.hint_limit,
            )
            for level in DifficultyLevel
        ),
    )


def convert_draft_to_definition(
    draft: GeneratedIncidentDraft,
    *,
    scenario_id: UUID | None = None,
    created_at: AwareDatetime | None = None,
) -> IncidentDefinition:
    return IncidentDefinition(
        scenario_id=scenario_id or uuid4(),
        schema_version=draft.schema_version,
        difficulty=draft.difficulty,
        created_at=created_at or datetime.now(UTC),
        generation=GenerationMetadata(
            generator_id=draft.generator_id,
            generator_version=draft.generator_version,
            seed=draft.seed,
            components=draft.components,
            generation_source=draft.generation_source,
            model=draft.model,
        ),
        presentation=draft.presentation,
        initial_world_state=draft.initial_world_state,
        faults=draft.faults,
        fault_relation=draft.fault_relation,
        symptoms=draft.symptoms,
        objectives=draft.objectives,
        capabilities=draft.capabilities,
        scoring=draft.scoring,
        hints=draft.hints,
        solution=draft.solution,
        service_dependencies=draft.service_dependencies,
        package_requirements=draft.package_requirements,
        configuration_requirements=draft.configuration_requirements,
        symptom_propagation=draft.symptom_propagation,
        post_incident=draft.post_incident,
    )


class DraftValidationError(ValueError):
    def __init__(self, message, *, category="capability"):
        super().__init__(message)
        self.category = category


def parse_generated_draft(payload) -> GeneratedIncidentDraft:
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Powtórzony klucz JSON.")
            result[key] = value
        return result

    def check_fields(value):
        if isinstance(value, dict):
            for child in value.values():
                check_fields(child)
        elif isinstance(value, list):
            if value and all(isinstance(item, dict) and set(item) == {"key", "value"} for item in value):
                keys = [item["key"] for item in value]
                if len(keys) != len(set(keys)):
                    raise ValueError("Powtórzone pole danych.")
            for child in value:
                check_fields(child)

    try:
        if isinstance(payload, GeneratedIncidentDraft):
            payload = payload.model_dump_json()
        if isinstance(payload, (str, bytes)):
            if len(payload) > 512_000:
                raise ValueError("Zbyt duży draft.")
            payload = json.loads(payload, object_pairs_hook=unique_object)
        check_fields(payload)
        return GeneratedIncidentDraft.model_validate_json(
            json.dumps(payload, allow_nan=False), strict=True,
        )
    except (ValueError, TypeError, RecursionError):
        pass
    raise DraftValidationError("Draft nie przeszedł walidacji schematu.", category="schema")


def validate_and_convert_draft(
    payload,
    *,
    scenario_id: UUID | None = None,
    created_at: AwareDatetime | None = None,
) -> IncidentDefinition:
    from app.admin_duty.validators import IncidentValidationError, IncidentValidator
    from app.admin_duty.validators.incident import IncidentReplayError

    draft = parse_generated_draft(payload)

    catalog = get_ai_capability_catalog()
    supported_commands = set(catalog.supported_commands)
    if not set(draft.capabilities.command_capability_ids) <= supported_commands:
        raise DraftValidationError("Draft zawiera nieznane capability.")
    fault_categories = set(catalog.supported_fault_categories)
    declared_fault_categories = {
        field.value
        for fault in draft.faults
        for field in fault.parameters
        if field.key == "component_id"
    }
    if any(
        not any(field.key == "component_id" for field in fault.parameters)
        for fault in draft.faults
    ):
        raise DraftValidationError("Draft nie deklaruje kategorii faultu.")
    if not declared_fault_categories <= fault_categories:
        raise DraftValidationError("Draft zawiera nieznaną kategorię faultu.")
    if not {
        dependency.dependency_type.value
        for dependency in draft.service_dependencies
    } <= set(catalog.supported_dependency_types):
        raise DraftValidationError("Draft zawiera nieznany typ dependency.")
    if not {
        requirement.package_name for requirement in draft.package_requirements
    } <= set(catalog.supported_packages):
        raise DraftValidationError("Draft zawiera nieznany pakiet.")
    if draft.initial_world_state.map.map_id not in set(catalog.supported_maps):
        raise DraftValidationError("Draft zawiera nieznaną mapę.")
    if not {
        interaction.capability_id for interaction in draft.initial_world_state.map.interactions
    } <= set(catalog.supported_map_interactions):
        raise DraftValidationError("Draft zawiera nieznaną interakcję mapy.")
    supported_services = set(catalog.supported_services)
    if any(fault.fault_type not in catalog.supported_fault_types for fault in draft.faults):
        raise DraftValidationError("Draft zawiera nieznany typ faultu.")
    for resource in draft.initial_world_state.resources:
        attributes = {field.key: field.value for field in resource.attributes}
        if not set(attributes) <= set(catalog.supported_resource_attributes):
            raise DraftValidationError("Draft zawiera nieznaną właściwość zasobu.")
        packages = attributes.get("installed_packages", ())
        if not isinstance(packages, tuple) or not set(packages) <= set(catalog.supported_packages):
            raise DraftValidationError("Draft zawiera nieznany pakiet hosta.")
        if attributes.get("required_package") not in {None, *catalog.supported_packages}:
            raise DraftValidationError("Draft wymaga nieznanego pakietu usługi.")
        if resource.resource_type is not ResourceType.SERVICE:
            continue
        if attributes.get("service_kind") not in supported_services:
            raise DraftValidationError("Draft zawiera nieznany rodzaj usługi.")

    try:
        definition = convert_draft_to_definition(
            draft,
            scenario_id=scenario_id,
            created_at=created_at,
        )
        return IncidentValidator().validate(definition)
    except IncidentReplayError:
        category = "replay"
    except (IncidentValidationError, ValueError):
        category = "semantic"
    raise DraftValidationError(
        "Draft nie przeszedł walidacji semantycznej." if category == "semantic"
        else "Draft nie przeszedł replay reference solution.",
        category=category,
    )


async def generate_validated_incident(
    provider: IncidentAIProvider,
    request: IncidentGenerationRequest,
    *,
    scenario_id: UUID | None = None,
    created_at: AwareDatetime | None = None,
) -> IncidentDefinition:
    from app.admin_duty.domain.public_generation import protect_public_narrative

    draft = parse_generated_draft(await provider.generate_incident(request))
    if draft.difficulty is not request.difficulty:
        raise DraftValidationError("Draft nie odpowiada żądanemu poziomowi trudności.")
    if draft.generation_source is not request.generation_source:
        raise DraftValidationError("Draft ma niezgodne źródło generowania.")
    if request.seed is not None and draft.seed != request.seed:
        raise DraftValidationError("Draft nie odpowiada żądanemu ziarnu losowania.")
    if request.map_id is not None and draft.initial_world_state.map.map_id != request.map_id:
        raise DraftValidationError("Draft nie odpowiada żądanej mapie.")
    if request.allowed_fault_categories:
        allowed_categories = set(request.allowed_fault_categories)
        draft_categories = {
            field.value
            for fault in draft.faults
            for field in fault.parameters
            if field.key == "component_id"
        }
        if not draft_categories <= allowed_categories:
            raise DraftValidationError("Draft zawiera kategorię faultu spoza żądania.")
    draft = protect_public_narrative(draft)
    return validate_and_convert_draft(
        draft,
        scenario_id=scenario_id,
        created_at=created_at,
    )
