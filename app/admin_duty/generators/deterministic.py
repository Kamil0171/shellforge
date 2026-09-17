import random
import secrets
from datetime import UTC, datetime
from uuid import uuid4

from app.admin_duty.components import (
    ENVIRONMENT_TEMPLATES,
    FAULT_TEMPLATES,
    EnvironmentTemplate,
    FaultTemplate,
    ResourceRole,
    get_map_template,
)
from app.admin_duty.components.maps import instantiate_map_snapshot
from app.admin_duty.components.models import AttributeMutationTemplate
from app.admin_duty.components.scenarios import (
    HARD_COMBINATIONS,
    HARD_ENVIRONMENT_ARCHETYPE,
    MEDIUM_SCENARIO_CATEGORIES,
    build_hard_draft,
    build_medium_draft,
)
from app.admin_duty.domain.definition import (
    CapabilitySet,
    CompletionCondition,
    ComponentReference,
    ComponentType,
    DataField,
    FaultInstance,
    GenerationMetadata,
    GenerationSource,
    IncidentDefinition,
    IncidentPresentation,
    InitialWorldState,
    InterfaceCapability,
    Objective,
    PostIncidentDefinition,
    ScoringRules,
    SolutionStep,
    Symptom,
    WorldResource,
)
from app.admin_duty.domain.difficulty import DifficultyLevel, get_difficulty_profile
from app.admin_duty.domain.generation import (
    IncidentGenerationRequest,
    convert_draft_to_definition,
)
from app.admin_duty.domain.reporting import get_fault_report_profile
from app.admin_duty.rocky.registry import HANDLERS
from app.admin_duty.validators import IncidentValidationError, IncidentValidator

GENERATOR_ID = "shellforge.deterministic"
GENERATOR_VERSION = "2.0"
MAX_GENERATION_ATTEMPTS = 10


class UnsupportedDifficultyError(ValueError):
    pass


class GenerationError(ValueError):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


def _field_map(fields: tuple[DataField, ...]) -> dict[str, object]:
    return {field.key: field.value for field in fields}


def _bindings(environment: EnvironmentTemplate) -> dict[str, str]:
    return {binding.role.value: binding.resource_id for binding in environment.bindings}


def _context(environment: EnvironmentTemplate) -> dict[str, str]:
    values = _bindings(environment)
    for field in environment.context:
        if not isinstance(field.value, str):
            raise GenerationError(
                f"Context środowiska zawiera nieobsługiwaną wartość: {field.key}."
            )
        values[field.key] = field.value
    service = next(
        item for item in environment.resources if item.resource_type.value == "service"
    )
    attrs = _field_map(service.attributes)
    name = str(attrs["service_name"])
    values["service_name"] = name
    values["unit_path"] = f"/etc/systemd/system/{name}"
    values["executable_path"] = (
        f"/opt/{name.removesuffix('.service')}/{values['expected_exec_target']}"
    )
    values["healthy_unit"] = (
        f"[Unit]\nDescription=Usługa aplikacyjna\nAfter=network-online.target\n\n"
        f"[Service]\nType=simple\nExecStart={values['executable_path']}\n"
        f'Environment="{values["environment_variable"]}={values["environment_value"]}"\n'
        "User=app\nRestart=on-failure\n\n[Install]\nWantedBy=multi-user.target\n"
    )
    return values


def _solution(fault, context):
    result = []
    for step in fault.solution:
        result.append(
            SolutionStep(
                order=len(result) + 1,
                capability_id=step.capability_id,
                input=step.input_template.format_map(context),
                purpose=step.purpose,
                parameters=(
                    DataField(
                        key="content", value=step.content_template.format_map(context)
                    ),
                )
                if step.content_template
                else (),
            )
        )
        if step.content_template:
            result.append(
                SolutionStep(
                    order=len(result) + 1,
                    capability_id="systemd.daemon-reload",
                    input="systemctl daemon-reload",
                    purpose="Przeładuj definicje jednostek.",
                )
            )
    return tuple(result)


def _resource_for_role(
    environment: EnvironmentTemplate,
    role: ResourceRole,
) -> WorldResource:
    resource_id = _bindings(environment)[role.value]
    return next(
        resource
        for resource in environment.resources
        if resource.resource_id == resource_id
    )


def _is_compatible(
    environment: EnvironmentTemplate,
    fault: FaultTemplate,
    difficulty: DifficultyLevel,
) -> bool:
    if difficulty not in environment.compatible_difficulties:
        return False
    if difficulty not in fault.compatible_difficulties:
        return False

    bindings = _bindings(environment)
    context = _field_map(environment.context)
    if fault.target_role.value not in bindings:
        return False
    if any(key not in context for key in fault.required_context_keys):
        return False

    target = _resource_for_role(environment, fault.target_role)
    return target.resource_type in fault.required_resource_types


def _resolve_attribute_name(
    mutation: AttributeMutationTemplate,
    context: dict[str, str],
) -> str:
    if mutation.attribute is not None:
        return mutation.attribute
    if mutation.attribute_context_key is None:
        raise GenerationError("Mutacja nie definiuje nazwy pola.")
    return f"{mutation.attribute_prefix}{context[mutation.attribute_context_key]}"


def _apply_fault(
    environment: EnvironmentTemplate,
    fault: FaultTemplate,
) -> tuple[WorldResource, ...]:
    bindings = _bindings(environment)
    context = _context(environment)
    state_updates = {
        bindings[mutation.resource_role.value]: mutation.new_state
        for mutation in fault.state_mutations
    }
    attribute_updates: dict[str, list[tuple[str, object, bool]]] = {}

    for mutation in fault.attribute_mutations:
        resource_id = bindings[mutation.resource_role.value]
        attribute = _resolve_attribute_name(mutation, context)
        value = (
            context[mutation.value_context_key]
            if mutation.value_context_key is not None
            else mutation.value
        )
        attribute_updates.setdefault(resource_id, []).append(
            (attribute, value, mutation.remove)
        )

    resources = []
    for resource in environment.resources:
        attributes = _field_map(resource.attributes)
        for attribute, value, remove in attribute_updates.get(resource.resource_id, ()):
            if remove:
                attributes.pop(attribute, None)
            else:
                attributes[attribute] = value

        resources.append(
            resource.model_copy(
                update={
                    "state": state_updates.get(resource.resource_id, resource.state),
                    "attributes": tuple(
                        DataField(key=key, value=value)
                        for key, value in attributes.items()
                    ),
                }
            )
        )
    return tuple(resources)


def _build_candidate(
    *,
    difficulty: DifficultyLevel,
    effective_seed: int,
    created_at: datetime,
    environment: EnvironmentTemplate,
    fault: FaultTemplate,
) -> IncidentDefinition:
    profile = get_difficulty_profile(difficulty)
    context = _context(environment)
    bindings = _bindings(environment)
    map_template = get_map_template(environment.map_component_id)
    target_resource_id = bindings[fault.target_role.value]
    service_resource_id = bindings[ResourceRole.PRIMARY_SERVICE.value]
    objective_id = fault.objective.objective_id_template.format_map(context)
    objective_label = fault.objective.label_template.format_map(context)
    components = (
        ComponentReference(
            component_type=ComponentType.MAP,
            component_id=map_template.component_id,
            version=map_template.version,
        ),
        ComponentReference(
            component_type=ComponentType.ENVIRONMENT,
            component_id=environment.component_id,
            version=environment.version,
        ),
        ComponentReference(
            component_type=ComponentType.FAULT,
            component_id=fault.component_id,
            version=fault.version,
        ),
        ComponentReference(
            component_type=ComponentType.SYMPTOM,
            component_id=fault.symptom.component_id,
            version=fault.symptom.version,
        ),
        ComponentReference(
            component_type=ComponentType.OBJECTIVE,
            component_id=fault.objective.component_id,
            version=fault.objective.version,
        ),
        ComponentReference(
            component_type=ComponentType.CAPABILITY,
            component_id=f"capabilities.{fault.component_id}",
            version=fault.version,
        ),
        ComponentReference(
            component_type=ComponentType.SCORING_POLICY,
            component_id=f"scoring.{profile.scoring_severity.value}",
            version="1.0",
        ),
    )

    report_profile = get_fault_report_profile(fault.fault_type)
    if report_profile is None or report_profile.root_cause is None:
        raise GenerationError("Fault EASY nie ma profilu raportowania.")

    return IncidentDefinition(
        scenario_id=uuid4(),
        schema_version="1.0",
        difficulty=difficulty,
        created_at=created_at,
        generation=GenerationMetadata(
            generator_id=GENERATOR_ID,
            generator_version=GENERATOR_VERSION,
            seed=effective_seed,
            components=components,
        ),
        presentation=IncidentPresentation(
            title=environment.title,
            organization=environment.organization,
            environment_label=environment.environment_label,
            briefing=f"{environment.briefing} {fault.briefing_addition}",
            main_objective=environment.main_objective,
            ticket_reference=f"{environment.ticket_prefix}-{effective_seed % 100000:05d}",
            tags=environment.tags,
            estimated_time_minutes=10,
        ),
        initial_world_state=InitialWorldState(
            environment_id=environment.component_id,
            environment_version=environment.version,
            map=instantiate_map_snapshot(
                map_template.component_id,
                seed=effective_seed,
            ),
            resources=_apply_fault(environment, fault),
        ),
        faults=(
            FaultInstance(
                fault_id=f"fault-{target_resource_id}",
                fault_type=fault.fault_type,
                version=fault.version,
                target_resource_id=target_resource_id,
                severity=fault.severity,
                parameters=(
                    DataField(key="component_id", value=fault.component_id),
                    DataField(key="primary_service_id", value=service_resource_id),
                    DataField(
                        key="forbidden_public_terms",
                        value=fault.forbidden_public_terms,
                    ),
                ),
            ),
        ),
        symptoms=(
            Symptom(
                symptom_id=fault.symptom.symptom_id,
                symptom_type=fault.symptom.symptom_type,
                source_resource_id=(
                    bindings[fault.symptom.source_role.value]
                    if fault.symptom.source_role is not None
                    else None
                ),
                visibility=fault.symptom.visibility,
                data=fault.symptom.data,
            ),
        ),
        objectives=(
            Objective(
                objective_id=objective_id,
                label=objective_label,
                required=fault.objective.required,
                completion_condition=CompletionCondition(
                    resource_id=service_resource_id,
                    field=fault.objective.condition.field,
                    operator=fault.objective.condition.operator,
                    expected=fault.objective.condition.expected,
                ),
                order=fault.objective.order,
                weight=fault.objective.weight,
            ),
        ),
        capabilities=CapabilitySet(
            interfaces=(
                InterfaceCapability.TERMINAL,
                InterfaceCapability.FILE_EDITOR,
                InterfaceCapability.MONITORING,
            ),
            command_capability_ids=tuple(
                dict.fromkeys((*fault.required_capabilities, *HANDLERS))
            ),
        ),
        scoring=ScoringRules(
            policy_id=f"scoring.{profile.scoring_severity.value}",
            initial_score=1000,
            command_cost=5,
            solution_penalty=300,
            solution_score_cap=500,
        ),
        hints=fault.hints[: profile.hint_limit],
        solution=_solution(fault, context),
        post_incident=PostIncidentDefinition(
            root_cause=report_profile.root_cause,
            affected_service_ids=(service_resource_id,),
            repair_capability_ids=report_profile.repair_capability_ids,
        ),
    )


class DeterministicIncidentGenerator:
    def __init__(self, validator: IncidentValidator | None = None) -> None:
        self._validator = validator if validator is not None else IncidentValidator()

    def generate(
        self,
        difficulty: DifficultyLevel,
        *,
        seed: int | None = None,
        now: datetime | None = None,
        request: IncidentGenerationRequest | None = None,
    ) -> IncidentDefinition:
        effective_seed = seed if seed is not None else secrets.randbelow(2**63)
        rng = random.Random(effective_seed)
        created_at = now if now is not None else utc_now()
        if difficulty is DifficultyLevel.HARD:
            if request is not None and request.map_id not in {
                None,
                "web-operations-room",
            }:
                raise GenerationError("HARD obsługuje mapę Modern NOC.")
            if request is not None and request.environment_preferences and (
                HARD_ENVIRONMENT_ARCHETYPE not in request.environment_preferences
            ):
                raise GenerationError("Żądanie nie zawiera środowiska HARD.")
            combinations = tuple(
                item
                for item in HARD_COMBINATIONS
                if request is None
                or not request.allowed_fault_categories
                or {
                    item.primary_fault_category,
                    item.secondary_fault_category,
                }
                <= set(request.allowed_fault_categories)
            )
            if not combinations:
                raise GenerationError("Żądanie nie zawiera obsługiwanej pary HARD.")
            combination = rng.choice(combinations)
            candidate = convert_draft_to_definition(
                build_hard_draft(combination.combination_id, seed=effective_seed),
                created_at=created_at,
            )
            return self._validator.validate(candidate)
        if difficulty is DifficultyLevel.MEDIUM:
            last_error = None
            for _ in range(MAX_GENERATION_ATTEMPTS):
                category = rng.choice(MEDIUM_SCENARIO_CATEGORIES)
                candidate = convert_draft_to_definition(
                    build_medium_draft(category, seed=effective_seed),
                    created_at=created_at,
                )
                try:
                    return self._validator.validate(candidate)
                except IncidentValidationError as error:
                    last_error = error
            raise GenerationError(
                "Nie udało się zbudować poprawnego incydentu MEDIUM po 10 próbach."
            ) from last_error

        environments = [
            environment
            for environment in ENVIRONMENT_TEMPLATES
            if difficulty in environment.compatible_difficulties
            and (request is None or request.map_id is None or environment.map_component_id == request.map_id)
        ]
        if not environments:
            raise GenerationError("Żądanie nie zawiera obsługiwanej mapy.")
        if request and request.environment_preferences:
            preferred = [environment for environment in environments if (
                environment.component_id in request.environment_preferences
                or set(environment.tags) & set(request.environment_preferences)
            )]
            environments = preferred or environments
        last_error = None

        for _ in range(MAX_GENERATION_ATTEMPTS):
            environment = rng.choice(environments)
            faults = [
                fault
                for fault in FAULT_TEMPLATES
                if _is_compatible(environment, fault, difficulty)
                and (request is None or not request.allowed_fault_categories or fault.component_id in request.allowed_fault_categories)
            ]
            if not faults:
                last_error = IncidentValidationError(
                    "Środowisko nie ma kompatybilnego faultu."
                )
                continue

            fault = rng.choice(faults)
            candidate = _build_candidate(
                difficulty=difficulty,
                effective_seed=effective_seed,
                created_at=created_at,
                environment=environment,
                fault=fault,
            )
            try:
                return self._validator.validate(candidate)
            except IncidentValidationError as error:
                last_error = error

        raise GenerationError(
            "Nie udało się zbudować poprawnego incydentu po 10 próbach."
        ) from last_error

    def generate_from_request(
        self,
        request: IncidentGenerationRequest,
        *,
        now: datetime | None = None,
    ) -> IncidentDefinition:
        if request.generation_source is not GenerationSource.DETERMINISTIC:
            raise GenerationError("Generator deterministyczny nie obsługuje źródła AI.")
        if request.map_id not in {None, "web-operations-room"} and request.difficulty in {
            DifficultyLevel.MEDIUM,
            DifficultyLevel.HARD,
        }:
            raise GenerationError("MEDIUM i HARD obsługują obecnie mapę Modern NOC.")
        if request.allowed_fault_categories and request.difficulty is DifficultyLevel.MEDIUM:
            allowed = tuple(
                category
                for category in MEDIUM_SCENARIO_CATEGORIES
                if category in request.allowed_fault_categories
            )
            if not allowed:
                raise GenerationError("Żądanie nie zawiera obsługiwanej kategorii faultu.")
            effective_seed = request.seed if request.seed is not None else secrets.randbelow(2**63)
            category = random.Random(effective_seed).choice(allowed)
            candidate = convert_draft_to_definition(
                build_medium_draft(category, seed=effective_seed),
                created_at=now or utc_now(),
            )
            return self._validator.validate(candidate)
        return self.generate(request.difficulty, seed=request.seed, now=now, request=request)
