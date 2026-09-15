from datetime import UTC, datetime

from app.admin_duty.components import ENVIRONMENT_TEMPLATES, FAULT_TEMPLATES
from app.admin_duty.components.scenarios import (
    build_hard_draft,
    build_medium_draft,
    get_hard_combination_for_pair,
)
from app.admin_duty.domain.ai_plan import get_plan_capability_catalog, parse_ai_plan
from app.admin_duty.domain.definition import (
    DataField,
    GenerationSource,
    ResourceType,
    ServiceDependency,
    WorldResource,
)
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.generation import (
    DraftValidationError,
    GeneratedIncidentDraft,
    parse_generated_draft,
)
from app.admin_duty.generators.deterministic import _build_candidate


class AIIncidentMaterializer:
    def materialize(self, plan) -> GeneratedIncidentDraft:
        plan = parse_ai_plan(plan)
        if plan.difficulty == "hard":
            combination = get_hard_combination_for_pair(
                plan.primary_fault_category,
                plan.secondary_fault_category,
            )
            draft = build_hard_draft(combination.combination_id, seed=plan.seed)
        elif plan.difficulty == "medium":
            draft = build_medium_draft(plan.fault_category, seed=plan.seed)
        else:
            environment = next(
                e
                for e in ENVIRONMENT_TEMPLATES
                if e.component_id == plan.environment_archetype
            )
            fault = next(
                f for f in FAULT_TEMPLATES if f.component_id == plan.fault_category
            )
            definition = _build_candidate(
                difficulty=DifficultyLevel.EASY,
                effective_seed=plan.seed,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
                environment=environment,
                fault=fault,
            )
            primary = next(
                r
                for r in definition.initial_world_state.resources
                if r.resource_type is ResourceType.SERVICE
            )
            observer_host = next(
                r
                for r in definition.initial_world_state.resources
                if r.resource_type is ResourceType.HOST
                and r.resource_id != primary.parent_id
            )
            resources = tuple(
                resource.model_copy(
                    update={
                        "attributes": (
                            *resource.attributes,
                            DataField(key="service_kind", value="systemd-service"),
                            DataField(key="port", value=8080),
                        )
                    }
                )
                if resource is primary
                else resource
                for resource in definition.initial_world_state.resources
            )
            observer = WorldResource(
                resource_id="service-observer",
                resource_type=ResourceType.SERVICE,
                parent_id=observer_host.resource_id,
                state="running",
                attributes=(
                    DataField(key="service_name", value="observer.service"),
                    DataField(key="service_kind", value="reverse-proxy"),
                    DataField(key="port", value=80),
                ),
            )
            fields = {
                name: getattr(definition, name)
                for name in GeneratedIncidentDraft.model_fields
                if hasattr(definition, name)
            }
            fields.update(
                draft_id=f"easy-{plan.environment_archetype}-{plan.fault_category}-{plan.seed}",
                schema_version="3.0",
                generator_id="shellforge.materializer",
                generator_version="1.0",
                generation_source=GenerationSource.AI,
                seed=plan.seed,
                components=definition.generation.components,
                initial_world_state=definition.initial_world_state.model_copy(
                    update={"resources": (*resources, observer)}
                ),
                service_dependencies=(
                    ServiceDependency(
                        dependency_id="observer-primary",
                        source_host_id=observer_host.resource_id,
                        source_service_id=observer.resource_id,
                        target_host_id=primary.parent_id,
                        target_service_id=primary.resource_id,
                        dependency_type="service",
                        protocol="tcp",
                        port=8080,
                    ),
                ),
                post_incident=definition.post_incident,
            )
            draft = GeneratedIncidentDraft(**fields)
        world = draft.initial_world_state
        hostnames = {} if plan.difficulty == "hard" else {
            field.value: f"{field.value}-{plan.seed % 10000:04d}"
            for resource in world.resources
            if resource.resource_type is ResourceType.HOST
            for field in resource.attributes
            if field.key == "hostname"
        }

        def rename_text(text):
            for original, renamed in hostnames.items():
                text = text.replace(original, renamed)
            return text

        resources = world.resources if plan.difficulty == "hard" else tuple(
            resource.model_copy(
                update={
                    "attributes": tuple(
                        field.model_copy(
                            update={"value": f"{field.value}-{plan.seed % 10000:04d}"}
                        )
                        if field.key == "hostname"
                        else field
                        for field in resource.attributes
                    ),
                }
            )
            if resource.resource_type is ResourceType.HOST
            else resource
            for resource in world.resources
        )
        return parse_generated_draft(
            draft.model_copy(
                update={
                    "generation_source": GenerationSource.AI,
                    "generator_id": "shellforge.materializer",
                    "model": "materialized-plan",
                    "initial_world_state": world.model_copy(
                        update={"resources": resources}
                    ),
                    "solution": tuple(
                        step.model_copy(update={"input": rename_text(step.input)})
                        for step in draft.solution
                    ),
                    "hints": tuple(
                        hint.model_copy(update={"text": rename_text(hint.text)})
                        for hint in draft.hints
                    ),
                    "post_incident": draft.post_incident.model_copy(
                        update={
                            "root_cause": rename_text(draft.post_incident.root_cause)
                        }
                    ),
                }
            )
        )


class MaterializingIncidentAIProvider:
    def __init__(self, provider, *, model, materializer=None):
        self.provider = provider
        self.model = model
        self.materializer = materializer or AIIncidentMaterializer()

    async def generate_incident(self, request):
        plan = parse_ai_plan(await self.provider.generate_plan(request))
        catalog = get_plan_capability_catalog(request)
        hard_plan = plan.difficulty == "hard"
        fault_matches = hard_plan or plan.fault_category in catalog.get(
            "faults_and_symptoms", {}
        )
        pair_matches = not hard_plan or any(
            pair["primary"] == plan.primary_fault_category
            and pair["secondary"] == plan.secondary_fault_category
            and pair["service"] == plan.affected_service_archetype
            for pair in catalog.get("hard_pairs", ())
        )
        if (
            plan.difficulty != request.difficulty.value
            or request.seed is not None
            and plan.seed != request.seed
            or plan.lesson_id != request.lesson_id
            or plan.environment_archetype not in catalog["environments_and_services"]
            or not fault_matches
            or not pair_matches
            or request.map_id not in {None, "web-operations-room"}
            and plan.difficulty in {"medium", "hard"}
        ):
            raise DraftValidationError(
                "Plan nie odpowiada żądaniu.", category="request_mismatch"
            )
        try:
            draft = self.materializer.materialize(plan)
        except DraftValidationError:
            raise
        except Exception:
            draft = None
        if draft is None:
            raise DraftValidationError(
                "Materializacja planu nie powiodła się.", category="materialization"
            )
        return parse_generated_draft(draft).model_copy(
            update={
                "model": self.model,
                "generator_id": "shellforge.gemma",
                "generator_version": "2.0",
            }
        )
