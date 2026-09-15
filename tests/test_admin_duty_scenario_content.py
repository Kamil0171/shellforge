import json
from datetime import UTC, datetime, timedelta

from app.admin_duty.components.scenarios import (
    HARD_COMBINATIONS,
    MEDIUM_SCENARIO_CATEGORIES,
    build_hard_draft,
    build_medium_draft,
)
from app.admin_duty.domain.ai_plan import AIIncidentPlan
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.generation import validate_and_convert_draft
from app.admin_duty.domain.runtime import create_session_runtime
from app.admin_duty.generators import DeterministicIncidentGenerator
from app.admin_duty.repositories import (
    InMemoryScenarioRepository,
    InMemorySessionRepository,
)
from app.admin_duty.services import DynamicIncidentService
from app.admin_duty.services.ai_materializer import AIIncidentMaterializer

NOW = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)
PLACEHOLDERS = ("example", "sample", "demo")


def _serialized(value) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json", exclude_none=True)
    return json.dumps(value, ensure_ascii=False, sort_keys=True).casefold()


def _assert_no_placeholders(label: str, *values) -> None:
    content = "\n".join(_serialized(value) for value in values)
    for placeholder in PLACEHOLDERS:
        assert placeholder not in content, (
            f"{label} zawiera placeholder {placeholder!r}"
        )


def _scenario_service() -> DynamicIncidentService:
    return DynamicIncidentService(
        generator=DeterministicIncidentGenerator(),
        scenario_repository=InMemoryScenarioRepository(),
        session_repository=InMemorySessionRepository(),
    )


def _curated_definitions():
    generator = DeterministicIncidentGenerator()
    easy = tuple(
        generator.generate(DifficultyLevel.EASY, seed=seed, now=NOW)
        for seed in range(50)
    )
    medium = tuple(
        validate_and_convert_draft(
            build_medium_draft(category, seed=100 + index),
            created_at=NOW,
        )
        for index, category in enumerate(MEDIUM_SCENARIO_CATEGORIES)
    )
    hard = tuple(
        validate_and_convert_draft(
            build_hard_draft(combination.combination_id, seed=200 + index),
            created_at=NOW,
        )
        for index, combination in enumerate(HARD_COMBINATIONS)
    )
    return easy, medium, hard


def _complete_with_reference_solution(definition):
    service = _scenario_service()
    started = service._start_definition(definition, NOW)
    current = NOW
    for step in definition.solution:
        current += timedelta(seconds=2)
        result = service.execute_command(started.session_id, step.input, now=current)
        if step.capability_id == "filesystem.edit":
            content = {field.key: field.value for field in step.parameters}["content"]
            current += timedelta(seconds=1)
            service.save_file(
                started.session_id,
                path=result.editor.path,
                content=content,
                now=current,
            )
    view = service.get_progress(started.session_id, now=current)
    assert view.progress.mission_complete
    assert view.post_incident is not None
    return view.post_incident


def test_generated_scenario_runtime_and_public_data_have_no_placeholder_names():
    suites = zip(("EASY", "MEDIUM", "HARD"), _curated_definitions(), strict=True)

    for difficulty, definitions in suites:
        for definition in definitions:
            runtime = create_session_runtime(definition, now=NOW)
            started = _scenario_service()._start_definition(definition, NOW)
            _assert_no_placeholders(difficulty, definition, runtime, started)
            public_payload = _serialized(started)
            for hidden in (
                "root_cause",
                "resolution_condition",
                "expected_content",
                "forbidden_public_terms",
                "generator_id",
                "post_incident",
            ):
                assert hidden not in public_payload


def test_ai_materializer_uses_clean_catalog_names_without_live_provider_calls():
    plans = (
        AIIncidentPlan(
            difficulty="easy",
            environment_archetype="web-application",
            fault_category="systemd-service-failed",
            affected_service_archetype="web-api",
            dependency_archetype="direct-service",
            symptom_archetype="service_unavailable",
            seed=301,
        ),
        AIIncidentPlan(
            difficulty="medium",
            environment_archetype="web-stack",
            fault_category="dependency-firewall-blocked",
            affected_service_archetype="web-api",
            dependency_archetype="proxy-api-database",
            symptom_archetype="public_service_degraded",
            seed=302,
        ),
        AIIncidentPlan(
            difficulty="hard",
            environment_archetype="hard-web-stack",
            primary_fault_category="dependency-firewall-blocked",
            secondary_fault_category="selinux-context-invalid",
            affected_service_archetype="web-api",
            dependency_archetype="proxy-api-database",
            symptom_archetype="progressive_service_degradation",
            seed=303,
        ),
    )

    materializer = AIIncidentMaterializer()
    for plan in plans:
        _assert_no_placeholders(plan.difficulty, materializer.materialize(plan))


def test_all_medium_and_hard_reports_have_complete_v2_content():
    definitions = (
        *(
            validate_and_convert_draft(
                build_medium_draft(category, seed=400 + index),
                created_at=NOW,
            )
            for index, category in enumerate(MEDIUM_SCENARIO_CATEGORIES)
        ),
        *(
            validate_and_convert_draft(
                build_hard_draft(combination.combination_id, seed=500 + index),
                created_at=NOW,
            )
            for index, combination in enumerate(HARD_COMBINATIONS)
        ),
    )

    for definition in definitions:
        report = _complete_with_reference_solution(definition)
        _assert_no_placeholders(definition.difficulty.value, report)
        assert report.version == "2.0"
        assert report.root_cause
        assert report.key_signals
        assert report.learning_points
        assert report.real_world_takeaways
        if definition.difficulty is DifficultyLevel.HARD:
            assert len(report.root_cause_chain) == 2
            assert report.partial_recovery_explanation
