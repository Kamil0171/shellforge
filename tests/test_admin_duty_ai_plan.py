import asyncio
from itertools import product

import pytest

from app.admin_duty.components.scenarios import HARD_COMBINATIONS
from app.admin_duty.domain.ai_plan import (
    EASY_ENVIRONMENTS,
    EASY_FAULTS,
    MEDIUM_FAULTS,
    MEDIUM_REVERSE_PROXY_FAULTS,
    SYMPTOMS,
    AIIncidentPlan,
    get_plan_capability_catalog,
    parse_ai_plan,
)
from app.admin_duty.domain.definition import GenerationSource
from app.admin_duty.domain.generation import (
    DraftValidationError,
    GeneratedIncidentDraft,
    IncidentGenerationRequest,
    generate_validated_incident,
    parse_generated_draft,
    validate_and_convert_draft,
)
from app.admin_duty.domain.public_generation import protect_public_narrative
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.providers.gemma import INSTRUCTION, build_generation_prompt
from app.admin_duty.repositories import (
    InMemoryScenarioRepository,
    InMemorySessionRepository,
)
from app.admin_duty.services import DynamicIncidentService
from app.admin_duty.services.ai_materializer import (
    AIIncidentMaterializer,
    MaterializingIncidentAIProvider,
)
from app.admin_duty.services.incident_generation import IncidentGenerationService


def make_plan(
    level="easy", fault="systemd-service-failed", environment="web-application", seed=51
):
    return AIIncidentPlan(
        difficulty=level,
        environment_archetype=environment,
        fault_category=fault,
        affected_service_archetype=EASY_ENVIRONMENTS[environment][0]
        if level == "easy"
        else ("reverse-proxy" if fault in MEDIUM_REVERSE_PROXY_FAULTS else "web-api"),
        dependency_archetype="direct-service"
        if level == "easy"
        else "proxy-api-database",
        symptom_archetype=SYMPTOMS[fault],
        seed=seed,
    )


def incoming(plan):
    return IncidentGenerationRequest(
        difficulty=plan.difficulty, generation_source="ai", seed=plan.seed
    )


def make_hard_plan(combination, *, seed=51):
    return AIIncidentPlan(
        difficulty="hard",
        environment_archetype="hard-web-stack",
        fault_category=None,
        primary_fault_category=combination.primary_fault_category,
        secondary_fault_category=combination.secondary_fault_category,
        affected_service_archetype=combination.affected_service_archetype,
        dependency_archetype=combination.dependency_archetype,
        symptom_archetype="progressive_service_degradation",
        skill_tags=combination.skill_tags[:3],
        seed=seed,
    )


class Plans:
    def __init__(self, *plans):
        self.plans = plans
        self.requests = []

    async def generate_plan(self, request):
        self.requests.append(request)
        return self.plans[len(self.requests) - 1]


@pytest.mark.parametrize(
    "environment,fault", list(product(EASY_ENVIRONMENTS, EASY_FAULTS))
)
def test_all_easy_materializations_validate_replay_and_keep_private_data(
    environment, fault
):
    plan = make_plan(environment=environment, fault=fault)
    draft = AIIncidentMaterializer().materialize(plan)
    assert isinstance(draft, GeneratedIncidentDraft)
    assert parse_generated_draft(draft) == draft
    assert len(draft.faults) == 1
    assert len(draft.service_dependencies) == 1
    assert (
        len(
            [
                r
                for r in draft.initial_world_state.resources
                if r.resource_type.value == "host"
            ]
        )
        == 2
    )
    definition = validate_and_convert_draft(protect_public_narrative(draft))
    assert definition.generation.generation_source is GenerationSource.AI
    assert definition.schema_version == "3.0"
    assert (
        definition.post_incident.root_cause
        not in definition.presentation.model_dump_json()
    )
    assert definition.hints and definition.solution


@pytest.mark.parametrize("fault", MEDIUM_FAULTS)
def test_all_medium_materializations_reuse_fixtures_and_replay(fault):
    plan = make_plan("medium", fault, "web-stack")
    materializer = AIIncidentMaterializer()
    draft = materializer.materialize(plan)
    definition = validate_and_convert_draft(protect_public_narrative(draft))
    assert len(definition.service_dependencies) >= 2
    assert (
        len(
            [
                r
                for r in draft.initial_world_state.resources
                if r.resource_type.value == "host"
            ]
        )
        >= 3
    )
    assert len(definition.faults) == 1
    assert draft == materializer.materialize(plan)


@pytest.mark.parametrize("combination", HARD_COMBINATIONS)
def test_all_hard_plans_materialize_two_faults_and_replay(combination):
    plan = make_hard_plan(combination)
    materializer = AIIncidentMaterializer()
    draft = materializer.materialize(plan)
    definition = validate_and_convert_draft(protect_public_narrative(draft))

    assert definition.schema_version == "4.0"
    assert len(definition.faults) == 2
    assert definition.fault_relation.primary_fault_id == "fault-primary"
    assert draft == materializer.materialize(plan)


@pytest.mark.parametrize("level", ["easy", "medium"])
def test_easy_and_medium_reject_secondary_fault(level):
    plan = make_plan(
        level,
        "systemd-service-failed" if level == "easy" else "dependency-firewall-blocked",
        "web-application" if level == "easy" else "web-stack",
    )
    payload = plan.model_dump(mode="json")
    payload["secondary_fault_category"] = "selinux-context-invalid"

    with pytest.raises(DraftValidationError, match="Plan AI"):
        parse_ai_plan(payload)


def test_hard_requires_secondary_and_rejects_unsupported_pair():
    payload = make_hard_plan(HARD_COMBINATIONS[0]).model_dump(mode="json")
    payload["secondary_fault_category"] = None
    with pytest.raises(DraftValidationError, match="Plan AI"):
        parse_ai_plan(payload)

    payload["secondary_fault_category"] = "dependency-package-missing"
    with pytest.raises(DraftValidationError, match="Plan AI"):
        parse_ai_plan(payload)


def test_hard_catalog_is_small_and_contains_only_approved_pairs():
    request = IncidentGenerationRequest(
        difficulty="hard",
        generation_source="ai",
        seed=51,
    )
    catalog = get_plan_capability_catalog(request)

    assert len(catalog["hard_pairs"]) == 10
    assert catalog["fault_count"] == 2
    assert catalog["hosts"] == [5, 5]
    assert len((INSTRUCTION + build_generation_prompt(request)).encode()) < 6144


def test_mocked_hard_plan_is_materialized_as_ai():
    plan = make_hard_plan(HARD_COMBINATIONS[0])
    provider = Plans(plan)
    service = IncidentGenerationService(
        fallback=DeterministicIncidentGenerator(),
        provider=MaterializingIncidentAIProvider(provider, model="fake-model"),
    )

    definition = asyncio.run(service.generate(incoming(plan)))

    assert definition.difficulty.value == "hard"
    assert definition.generation.generation_source is GenerationSource.AI
    assert definition.generation.generator_id == "shellforge.gemma"


def test_invalid_hard_plan_falls_back_to_deterministic_hard():
    plan = make_hard_plan(HARD_COMBINATIONS[0])
    provider = Plans({}, {})
    service = IncidentGenerationService(
        fallback=DeterministicIncidentGenerator(),
        provider=MaterializingIncidentAIProvider(provider, model="fake-model"),
    )

    definition = asyncio.run(service.generate(incoming(plan)))

    assert len(provider.requests) == 2
    assert definition.difficulty.value == "hard"
    assert definition.generation.generation_source is GenerationSource.DETERMINISTIC


@pytest.mark.parametrize(
    "level,fault,environment",
    [
        ("easy", "systemd-service-failed", "web-application"),
        ("medium", "networkmanager-dns-invalid", "web-stack"),
    ],
)
def test_seed_changes_allowed_host_variant_with_working_replay(
    level, fault, environment
):
    materializer = AIIncidentMaterializer()
    first = materializer.materialize(make_plan(level, fault, environment, seed=51))
    second = materializer.materialize(make_plan(level, fault, environment, seed=52))
    assert first == materializer.materialize(
        make_plan(level, fault, environment, seed=51)
    )
    assert first.initial_world_state != second.initial_world_state
    assert first.faults == second.faults
    validate_and_convert_draft(protect_public_narrative(second))


@pytest.mark.parametrize(
    "mutation",
    [
        {"difficulty": "hard"},
        {"difficulty": "medium"},
        {"fault_category": "unknown"},
        {"environment_archetype": "arbitrary-host"},
        {"affected_service_archetype": "postgres-custom"},
        {"dependency_archetype": "proxy-api-database"},
        {"symptom_archetype": "public_service_degraded"},
        {"skill_tags": ["arbitrary-code"]},
        {"skill_tags": ["systemd", "systemd"]},
        {"seed": "51"},
        {"seed": True},
        {"lesson_id": "23"},
        {"filesystem": []},
        {"logs": []},
        {"solution": []},
        {"handler": "exec"},
    ],
)
def test_plan_rejects_unknown_fields_and_invalid_or_incompatible_values(mutation):
    payload = make_plan().model_dump(mode="json") | mutation
    with pytest.raises(DraftValidationError, match="Plan AI"):
        parse_ai_plan(payload)


def test_duplicate_json_and_forged_model_are_rejected():
    with pytest.raises(DraftValidationError):
        parse_ai_plan('{"seed":1,"seed":2}')
    forged = make_plan().model_copy(update={"dependency_archetype": "arbitrary"})
    with pytest.raises(DraftValidationError):
        AIIncidentMaterializer().materialize(forged)


def test_small_catalog_filters_request_and_preserves_metadata():
    request = IncidentGenerationRequest(
        difficulty="easy",
        map_id="business-service-room",
        seed=51,
        generation_source="ai",
        allowed_fault_categories=("systemd-wrong-exec-start",),
        lesson_id=23,
        skill_tags=("systemd",),
    )
    catalog = get_plan_capability_catalog(request)
    assert catalog["environments_and_services"] == {
        "internal-business-service": "worker"
    }
    assert set(catalog["faults_and_symptoms"]) == {"systemd-wrong-exec-start"}
    assert len((INSTRUCTION + build_generation_prompt(request)).encode()) < 4096
    assert "GeneratedIncidentDraft" not in build_generation_prompt(request)


def test_invalid_plan_retries_and_success_is_ai():
    plan = make_plan()
    provider = Plans(plan.model_dump(mode="json") | {"command": "evil"}, plan)
    service = IncidentGenerationService(
        fallback=DeterministicIncidentGenerator(),
        provider=MaterializingIncidentAIProvider(provider, model="fake-model"),
    )
    definition = asyncio.run(service.generate(incoming(plan)))
    assert provider.requests[1].validation_feedback == ("plan",)
    assert definition.generation.generation_source is GenerationSource.AI


@pytest.mark.parametrize("failure", ["materialization", "replay"])
def test_materializer_and_replay_failures_retry_then_succeed(failure):
    plan = make_plan()
    provider = Plans(plan, plan)

    class FirstBadMaterializer(AIIncidentMaterializer):
        calls = 0

        def materialize(self, plan):
            self.calls += 1
            if self.calls == 1 and failure == "materialization":
                raise ValueError("private internal failure")
            draft = super().materialize(plan)
            if self.calls == 1:
                return draft.model_copy(update={"solution": draft.solution[:1]})
            return draft

    service = IncidentGenerationService(
        fallback=DeterministicIncidentGenerator(),
        provider=MaterializingIncidentAIProvider(
            provider,
            model="fake-model",
            materializer=FirstBadMaterializer(),
        ),
    )
    definition = asyncio.run(service.generate(incoming(plan)))
    assert provider.requests[1].validation_feedback == (failure,)
    assert definition.generation.generation_source is GenerationSource.AI


def test_two_invalid_plans_fall_back_without_changing_request():
    plan = make_plan()
    provider = Plans({}, {})
    service = IncidentGenerationService(
        fallback=DeterministicIncidentGenerator(),
        provider=MaterializingIncidentAIProvider(provider, model="fake"),
    )
    definition = asyncio.run(service.generate(incoming(plan)))
    assert len(provider.requests) == 2
    assert definition.generation.seed == plan.seed
    assert definition.generation.generation_source is GenerationSource.DETERMINISTIC


def test_plan_metadata_mismatch_is_rejected():
    plan = make_plan().model_copy(update={"lesson_id": 23})
    with pytest.raises(DraftValidationError) as caught:
        asyncio.run(
            generate_validated_incident(
                MaterializingIncidentAIProvider(Plans(plan), model="fake"),
                incoming(plan),
            )
        )
    assert caught.value.category == "request_mismatch"


def test_active_session_never_exposes_plan_and_post_incident_is_available_after_repair():
    plan = make_plan()
    scenarios = InMemoryScenarioRepository()
    service = DynamicIncidentService(
        generator=DeterministicIncidentGenerator(),
        scenario_repository=scenarios,
        session_repository=InMemorySessionRepository(),
        generation_service=IncidentGenerationService(
            fallback=DeterministicIncidentGenerator(),
            provider=MaterializingIncidentAIProvider(Plans(plan), model="fake-model"),
        ),
    )
    session = asyncio.run(
        service.start_session_async(incoming(plan).difficulty, seed=51)
    )
    public = session.model_dump_json()
    for hidden in (
        "AIIncidentPlan",
        "fault_category",
        "root_cause",
        "solution",
        "validation_feedback",
        "fake-model",
    ):
        assert f'"{hidden}"' not in public
    definition = scenarios.get(session.scenario_id)
    for step in definition.solution:
        service.execute_command(session.session_id, step.input)
    finished = service.get_progress(session.session_id)
    assert finished.progress.mission_complete
    assert finished.post_incident.root_cause == definition.post_incident.root_cause
