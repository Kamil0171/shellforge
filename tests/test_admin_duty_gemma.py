import asyncio
import json
import logging
import traceback
from datetime import UTC, datetime

import httpx
import pytest
from pydantic import SecretStr

from app.admin_duty.components.scenarios import build_medium_draft
from app.admin_duty.domain.ai_plan import AIIncidentPlan
from app.admin_duty.domain.definition import GenerationSource
from app.admin_duty.domain.generation import (
    DraftValidationError,
    FakeIncidentAIProvider,
    IncidentGenerationRequest,
    generate_validated_incident,
    parse_generated_draft,
)
from app.admin_duty.generators import (
    DeterministicIncidentGenerator,
    UnsupportedDifficultyError,
)
from app.admin_duty.providers import GemmaProvider, IncidentProviderError
from app.admin_duty.repositories import (
    InMemoryScenarioRepository,
    InMemorySessionRepository,
)
from app.admin_duty.services import DynamicIncidentService
from app.admin_duty.services.ai_materializer import MaterializingIncidentAIProvider
from app.admin_duty.services.incident_generation import (
    IncidentGenerationService,
    configured_generation_service,
    validated_scenario_metadata,
)
from app.config import IncidentAISettings

NOW = datetime(2026, 9, 9, 12, tzinfo=UTC)
TEST_SECRET = "test-only-secret-do-not-log"


def settings(**kwargs):
    return IncidentAISettings(
        enabled=True, provider="gemma", model="gemma-4-31b-it",
        api_key=SecretStr(TEST_SECRET), **kwargs,
    )


def draft(difficulty="medium", seed=51):
    payload = build_medium_draft("dependency-firewall-blocked", seed=seed).model_dump(mode="json")
    payload.update(difficulty=difficulty, generation_source="ai", model="fake-model")
    return parse_generated_draft(payload)


def request(difficulty="medium", **kwargs):
    return IncidentGenerationRequest(difficulty=difficulty, generation_source="ai", seed=51, **kwargs)


def plan(difficulty="medium", seed=51):
    easy = difficulty == "easy"
    return AIIncidentPlan(
        difficulty=difficulty, environment_archetype="web-application" if easy else "web-stack",
        fault_category="systemd-service-failed" if easy else "dependency-firewall-blocked",
        affected_service_archetype="web-api", dependency_archetype="direct-service" if easy else "proxy-api-database",
        symptom_archetype="service_unavailable" if easy else "public_service_degraded", seed=seed,
    )


def response(payload=None, **candidate):
    return httpx.Response(200, json={"candidates": [{
        "content": {"role": "model", "parts": [{"text": plan().model_dump_json() if payload is None else payload}]},
        "finishReason": "STOP", **candidate,
    }]})


def test_sdk_request_schema_timeout_and_success(caplog):
    calls = []

    def handler(outgoing):
        calls.append(outgoing)
        return response()

    provider = GemmaProvider(settings(), transport=httpx.MockTransport(handler))
    with caplog.at_level(logging.DEBUG):
        result = asyncio.run(provider.generate_plan(request(
            lesson_id=23, lesson_topic="firewalld", skill_tags=("security",),
        )))
    outgoing = calls[0]
    body = json.loads(outgoing.content)
    assert len(calls) == 1
    assert outgoing.url.host == "generativelanguage.googleapis.com"
    assert outgoing.url.path.endswith("/gemma-4-31b-it:generateContent")
    assert not outgoing.url.query
    assert outgoing.headers["x-goog-api-key"] == TEST_SECRET
    assert outgoing.extensions["timeout"]["read"] == 20
    config = body["generationConfig"]
    assert not set(config) & {"responseMimeType", "responseSchema", "responseJsonSchema", "responseFormat"}
    assert config["thinkingConfig"] == {"thinking_level": "MINIMAL"}
    assert "tools" not in body
    prompt = json.loads(body["contents"][0]["parts"][0]["text"])
    assert prompt["request"]["lesson_id"] == 23
    assert len(outgoing.content) < 4096
    assert "supported_commands" not in prompt["catalog"]
    assert "schema" not in prompt and "example" not in prompt
    assert "HARD" in body["systemInstruction"]["parts"][0]["text"]
    assert isinstance(result, AIIncidentPlan)
    assert TEST_SECRET not in caplog.text + repr(settings()) + repr(provider)


@pytest.mark.parametrize("status,category", [(400, "rejected"), (401, "rejected"), (403, "rejected"), (429, "rate_limit"), (500, "api_error"), (503, "api_error")])
def test_sdk_errors_do_not_retry_or_expose_response(status, category, caplog):
    calls = []

    def handler(outgoing):
        calls.append(outgoing)
        return httpx.Response(status, json={"error": {"code": status, "message": TEST_SECRET}})

    with caplog.at_level(logging.DEBUG), pytest.raises(IncidentProviderError) as caught:
        asyncio.run(GemmaProvider(settings(), transport=httpx.MockTransport(handler)).generate_plan(request()))
    assert len(calls) == 1
    assert caught.value.category == category
    assert caught.value.__context__ is None
    assert caught.value.__cause__ is None
    assert TEST_SECRET not in caplog.text + "".join(traceback.format_exception(caught.value))


@pytest.mark.parametrize("payload", ["```json\n{}\n```", "not-json", "{}", '{"a": 1, "a": 2}', TEST_SECRET, "x" * 512_001], ids=["markdown", "text", "schema", "duplicate", "secret", "oversized"])
def test_invalid_output_is_rejected_without_repairs(payload):
    provider = GemmaProvider(settings(), transport=httpx.MockTransport(lambda _: response(payload)))
    with pytest.raises(IncidentProviderError):
        asyncio.run(provider.generate_plan(request()))


@pytest.mark.parametrize("payload,category", [
    ("```json\n{}\n```", "invalid_json"), (" ", "invalid_json"),
    ('{"a":1,"a":2}', "invalid_json"), ("{}", "plan"),
    ("null", "plan"), ("[]", "plan"),
])
def test_plain_json_failure_category(payload, category, caplog):
    provider = GemmaProvider(settings(), transport=httpx.MockTransport(lambda _: response(payload)))
    with caplog.at_level(logging.DEBUG), pytest.raises(IncidentProviderError) as caught:
        asyncio.run(provider.generate_plan(request()))
    assert caught.value.category == category
    assert caught.value.__context__ is None
    assert TEST_SECRET not in caplog.text


def test_plain_json_strict_schema_does_not_coerce_seed():
    payload = plan().model_dump(mode="json")
    payload["seed"] = "51"
    provider = GemmaProvider(settings(), transport=httpx.MockTransport(lambda _: response(json.dumps(payload))))
    with pytest.raises(IncidentProviderError) as caught:
        asyncio.run(provider.generate_plan(request()))
    assert caught.value.category == "plan"


@pytest.mark.parametrize("mutation,category", [
    (lambda p: p["capabilities"]["command_capability_ids"].append("python.execute"), "capability"),
    (lambda p: p["service_dependencies"][0].update(target_service_id="unknown-service"), "semantic"),
    (lambda p: p.update(solution=p["solution"][:1]), "replay"),
])
def test_validation_stages_have_distinct_safe_feedback(mutation, category, caplog):
    payload = draft().model_dump(mode="json")
    mutation(payload)
    provider = SequenceProvider(payload, payload)
    with caplog.at_level(logging.INFO):
        result = asyncio.run(pipeline(provider).generate(request(), now=NOW))
    assert result.generation.generation_source is GenerationSource.DETERMINISTIC
    assert provider.requests[1].validation_feedback == (category,)
    assert f"result={category}" in caplog.text
    assert TEST_SECRET not in caplog.text


@pytest.mark.parametrize("body", [
    {}, {"candidates": []},
    {"candidates": [{"finishReason": "MAX_TOKENS", "content": {"parts": [{"text": "{}"}]}}]},
    {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "private thoughts", "thought": True}]}}]},
    {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"functionCall": {"name": "shell", "args": {}}}]}}]},
])
def test_empty_truncated_or_non_data_response_fails(body):
    provider = GemmaProvider(settings(), transport=httpx.MockTransport(lambda _: httpx.Response(200, json=body)))
    with pytest.raises(IncidentProviderError):
        asyncio.run(provider.generate_plan(request()))


def test_sdk_text_metadata_is_not_plan_content_or_persisted():
    body = {
        "candidates": [{
            "finishReason": "STOP", "content": {"parts": [{
                "text": plan().model_dump_json(), "thoughtSignature": "c2lnbmF0dXJl",
            }]},
        }],
    }
    provider = GemmaProvider(settings(), transport=httpx.MockTransport(lambda _: httpx.Response(200, json=body)))
    result = asyncio.run(provider.generate_plan(request()))
    assert result == plan()
    assert "signature" not in result.model_dump_json()


def test_sdk_empty_signature_part_does_not_hide_plan_text():
    body = {
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "parts": [
                        {"text": "", "thoughtSignature": "c2lnbmF0dXJl"},
                        {"text": plan().model_dump_json()},
                    ]
                },
            }
        ],
    }
    provider = GemmaProvider(
        settings(),
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json=body)),
    )
    assert asyncio.run(provider.generate_plan(request())) == plan()


@pytest.mark.parametrize("error,category", [(httpx.ReadTimeout(TEST_SECRET), "timeout"), (httpx.ConnectError(TEST_SECRET), "transport")])
def test_network_failure_is_sanitized(error, category):
    def handler(_):
        raise error

    with pytest.raises(IncidentProviderError) as caught:
        asyncio.run(GemmaProvider(settings(), transport=httpx.MockTransport(handler)).generate_plan(request()))
    assert caught.value.category == category
    assert TEST_SECRET not in str(caught.value)
    assert caught.value.__context__ is None


def test_sdk_wall_clock_timeout():
    async def handler(_):
        await asyncio.sleep(1)
        return response()

    provider = GemmaProvider(settings(timeout_seconds=0.01), transport=httpx.MockTransport(handler))
    with pytest.raises(IncidentProviderError, match="timeout"):
        asyncio.run(provider.generate_plan(request()))


@pytest.mark.parametrize("mutation", [
    lambda p: p.update(unknown="python"),
    lambda p: p.update(seed="51"),
    lambda p: p["initial_world_state"]["resources"][0]["attributes"].append(p["initial_world_state"]["resources"][0]["attributes"][0]),
])
def test_strict_schema_revalidates_untrusted_data(mutation):
    payload = draft().model_dump(mode="json")
    mutation(payload)
    with pytest.raises(DraftValidationError):
        parse_generated_draft(payload)


class SequenceProvider:
    def __init__(self, *outcomes):
        self.outcomes = outcomes
        self.requests = []

    async def generate_incident(self, incoming):
        self.requests.append(incoming)
        outcome = self.outcomes[len(self.requests) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def pipeline(provider):
    return IncidentGenerationService(fallback=DeterministicIncidentGenerator(), provider=provider, timeout_seconds=0.2)


def test_retry_feedback_is_controlled_and_second_draft_is_validated():
    invalid = draft().model_copy(update={"solution": (draft().solution[0],)})
    provider = SequenceProvider(invalid, draft())
    result = asyncio.run(pipeline(provider).generate(request(), now=NOW))
    assert result.generation.generation_source is GenerationSource.AI
    assert len(provider.requests) == 2
    assert provider.requests[0].validation_feedback == ()
    assert provider.requests[1].validation_feedback == ("replay",)


@pytest.mark.parametrize("difficulty", ["easy", "medium"])
def test_two_failures_fall_back_with_original_seed(difficulty, caplog):
    provider = SequenceProvider(RuntimeError(TEST_SECRET), RuntimeError(TEST_SECRET))
    with caplog.at_level(logging.INFO):
        result = asyncio.run(pipeline(provider).generate(request(difficulty), now=NOW))
    assert result.generation.generation_source is GenerationSource.DETERMINISTIC
    assert result.difficulty.value == difficulty
    assert result.generation.seed == 51
    assert len(provider.requests) == 2
    assert TEST_SECRET not in caplog.text


def test_pipeline_timeout_and_cancellation():
    class SlowProvider:
        calls = 0

        async def generate_incident(self, incoming):
            self.calls += 1
            await asyncio.sleep(10)

    provider = SlowProvider()
    service = pipeline(provider)
    service._timeout = 0.01
    result = asyncio.run(service.generate(request(), now=NOW))
    assert provider.calls == 2
    assert result.generation.generation_source is GenerationSource.DETERMINISTIC

    async def cancel():
        task = asyncio.create_task(service.generate(request(), now=NOW))
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(cancel())


def test_hard_never_calls_provider():
    provider = SequenceProvider()
    with pytest.raises(UnsupportedDifficultyError):
        asyncio.run(pipeline(provider).generate(request("hard")))
    assert provider.requests == []


@pytest.mark.parametrize("environment", [
    {}, {"SHELLFORGE_AI_GENERATION_ENABLED": "false"},
    {"SHELLFORGE_AI_PROVIDER": "unknown"}, {"GEMMA_API_KEY": ""},
    {"GEMMA_MODEL": "../../invalid"}, {"SHELLFORGE_AI_TIMEOUT_SECONDS": "nan"},
    {"SHELLFORGE_AI_TIMEOUT_SECONDS": "invalid"}, {"SHELLFORGE_AI_TIMEOUT_SECONDS": "0"},
])
def test_invalid_configuration_starts_without_sdk_client(monkeypatch, environment):
    defaults = {
        "SHELLFORGE_AI_GENERATION_ENABLED": "true", "SHELLFORGE_AI_PROVIDER": "gemma",
        "GEMMA_API_KEY": TEST_SECRET, "GEMMA_MODEL": "gemma-4-31b-it",
        "SHELLFORGE_AI_TIMEOUT_SECONDS": "30",
    }
    for key in defaults:
        monkeypatch.delenv(key, raising=False)
    if environment:
        for key, value in (defaults | environment).items():
            monkeypatch.setenv(key, value)
    service = configured_generation_service(DeterministicIncidentGenerator())
    assert service._provider is None
    result = asyncio.run(service.generate(request(), now=NOW))
    assert result.generation.generation_source is GenerationSource.DETERMINISTIC


def test_public_narrative_cannot_repeat_or_paraphrase_private_root_cause():
    original = draft()
    unsafe = original.model_copy(update={
        "presentation": original.presentation.model_copy(update={"briefing": "Usunięto regułę zapory i ruch do bazy nie dociera."}),
        "objectives": tuple(o.model_copy(update={"label": original.post_incident.root_cause}) for o in original.objectives),
        "faults": tuple(f.model_copy(update={"parameters": tuple(p for p in f.parameters if p.key != "forbidden_public_terms")}) for f in original.faults),
    })
    definition = asyncio.run(generate_validated_incident(FakeIncidentAIProvider(unsafe), request()))
    public_text = definition.presentation.model_dump_json() + str([o.label for o in definition.objectives])
    assert "Usunięto regułę" not in public_text
    assert original.post_incident.root_cause not in public_text


def test_public_host_cannot_expose_root_cause_when_model_omits_forbidden_terms():
    payload = draft().model_dump(mode="json")
    for field in payload["initial_world_state"]["resources"][0]["attributes"]:
        if field["key"] == "hostname":
            field["value"] = "python3-psycopg2"
    payload["faults"][0]["parameters"] = [p for p in payload["faults"][0]["parameters"] if p["key"] != "forbidden_public_terms"]
    with pytest.raises(DraftValidationError):
        asyncio.run(generate_validated_incident(FakeIncidentAIProvider(parse_generated_draft(payload)), request()))


def test_concurrent_sessions_have_isolated_definitions_and_runtime():
    scenarios = InMemoryScenarioRepository()
    sessions = InMemorySessionRepository()
    service = DynamicIncidentService(
        generator=DeterministicIncidentGenerator(), scenario_repository=scenarios,
        session_repository=sessions, generation_service=pipeline(FakeIncidentAIProvider(draft())),
    )

    async def start():
        return await asyncio.gather(*(service.start_session_async(request().difficulty, seed=51, now=NOW) for _ in range(3)))

    results = asyncio.run(start())
    assert len({r.scenario_id for r in results}) == 3
    assert len({r.session_id for r in results}) == 3
    first, second, _ = results
    service.execute_command(first.session_id, "pwd", now=NOW)
    assert service.get_progress(first.session_id, now=NOW).progress.commands_used == 1
    assert service.get_progress(second.session_id, now=NOW).progress.commands_used == 0
    public = first.model_dump_json()
    for hidden in ("root_cause", "solution", "validation_feedback", "raw_response", TEST_SECRET, "fake-model"):
        assert f'"{hidden}"' not in public


@pytest.mark.parametrize("difficulty", ["easy", "medium"])
def test_sdk_retry_success_and_full_api_projection(difficulty, caplog):
    from fastapi.testclient import TestClient

    import app.admin_duty.dynamic_router as router
    from app.main import app

    calls = []

    def handler(outgoing):
        calls.append(outgoing)
        if len(calls) == 1:
            return httpx.Response(429, json={"error": {"code": 429, "message": TEST_SECRET}})
        return response(plan(difficulty).model_dump_json())

    scenarios = InMemoryScenarioRepository()
    service = DynamicIncidentService(
        generator=DeterministicIncidentGenerator(), scenario_repository=scenarios,
        session_repository=InMemorySessionRepository(),
        generation_service=IncidentGenerationService(
            fallback=DeterministicIncidentGenerator(),
            provider=MaterializingIncidentAIProvider(GemmaProvider(settings(), transport=httpx.MockTransport(handler)), model=settings().model),
        ),
    )
    app.dependency_overrides[router.get_dynamic_incident_service] = lambda: service
    try:
        with caplog.at_level(logging.DEBUG):
            result = TestClient(app).post("/admin-duty/dynamic/api/start", json={"difficulty": difficulty, "seed": 51})
        assert result.status_code == 200
        assert len(calls) == 2
        prompt = json.loads(json.loads(calls[1].content)["contents"][0]["parts"][0]["text"])
        assert prompt["request"]["validation_feedback"] == ["rate_limit"]
        assert TEST_SECRET not in result.text + caplog.text
        assert "root_cause" not in result.text
        assert "reference_solution" not in result.text
        assert "generation_source" not in result.text
        from uuid import UUID

        definition = scenarios.get(UUID(result.json()["scenario_id"]))
        metadata = validated_scenario_metadata(definition)
        assert metadata.generation_source is GenerationSource.AI
        assert metadata.provider == "shellforge.gemma"
        assert metadata.schema_version == "3.0"
        assert metadata.validation_status.value == "valid"
    finally:
        app.dependency_overrides.clear()


def test_enabled_configuration_does_not_construct_sdk_at_startup(monkeypatch):
    from google import genai

    def forbidden(*args, **kwargs):
        pytest.fail("SDK nie może być inicjalizowane przy starcie aplikacji.")

    for key, value in {
        "SHELLFORGE_AI_GENERATION_ENABLED": "true", "SHELLFORGE_AI_PROVIDER": "gemma",
        "GEMMA_API_KEY": TEST_SECRET, "GEMMA_MODEL": "gemma-4-31b-it",
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(genai, "Client", forbidden)
    service = configured_generation_service(DeterministicIncidentGenerator())
    assert isinstance(service._provider, MaterializingIncidentAIProvider)
    assert isinstance(service._provider.provider, GemmaProvider)


@pytest.mark.parametrize("mutation", [
    lambda p: p["capabilities"]["command_capability_ids"].append("python.execute"),
    lambda p: p["faults"][0].update(fault_type="unknown_fault"),
    lambda p: p["initial_world_state"]["map"]["interactions"][0].update(capability_id="python.execute"),
    lambda p: p["initial_world_state"]["resources"][0]["attributes"].append({"key": "handler", "value": "arbitrary"}),
    lambda p: p["service_dependencies"][0].update(target_service_id="unknown-service"),
    lambda p: p["solution"][0].update(input="python evil.py"),
])
def test_untrusted_provider_fails_validation_then_falls_back(mutation):
    payload = draft().model_dump(mode="json")
    mutation(payload)
    provider = SequenceProvider(payload, payload)
    definition = asyncio.run(pipeline(provider).generate(request(), now=NOW))
    assert len(provider.requests) == 2
    assert definition.generation.generation_source is GenerationSource.DETERMINISTIC


def test_fallback_respects_easy_fault_and_map_constraints():
    incoming = request("easy", allowed_fault_categories=("systemd-wrong-exec-start",), map_id="web-operations-room")
    definition = asyncio.run(pipeline(None).generate(incoming, now=NOW))
    categories = {p.value for f in definition.faults for p in f.parameters if p.key == "component_id"}
    assert categories == {"systemd-wrong-exec-start"}
    assert definition.initial_world_state.map.map_id == "web-operations-room"


def test_overlapping_sdk_requests_do_not_share_feedback_seed_or_runtime():
    async def exercise():
        both_started = asyncio.Event()
        incoming_requests = []

        async def handler(outgoing):
            prompt = json.loads(json.loads(outgoing.content)["contents"][0]["parts"][0]["text"])
            incoming = prompt["request"]
            incoming_requests.append(incoming)
            if len(incoming_requests) == 2:
                both_started.set()
            await asyncio.wait_for(both_started.wait(), 2)
            return response(plan(seed=incoming["seed"]).model_dump_json())

        scenarios = InMemoryScenarioRepository()
        service = DynamicIncidentService(
            generator=DeterministicIncidentGenerator(), scenario_repository=scenarios,
            session_repository=InMemorySessionRepository(),
            generation_service=IncidentGenerationService(
                fallback=DeterministicIncidentGenerator(),
                provider=MaterializingIncidentAIProvider(GemmaProvider(settings(), transport=httpx.MockTransport(handler)), model=settings().model),
            ),
        )
        first, second = await asyncio.gather(*(
            service.start_session_async(request().difficulty, seed=seed, now=NOW)
            for seed in (51, 52)
        ))
        assert len(incoming_requests) == 2
        assert all(item["validation_feedback"] == [] for item in incoming_requests)
        assert first.session_id != second.session_id
        assert first.scenario_id != second.scenario_id
        assert scenarios.get(first.scenario_id).generation.seed == 51
        assert scenarios.get(second.scenario_id).generation.seed == 52
        assert scenarios.get(first.scenario_id).generation.generation_source is GenerationSource.AI
        service.execute_command(first.session_id, "pwd", now=NOW)
        assert service.get_progress(second.session_id, now=NOW).progress.commands_used == 0

    asyncio.run(exercise())


def test_ai_root_cause_is_available_only_after_completion():
    scenarios = InMemoryScenarioRepository()
    service = DynamicIncidentService(
        generator=DeterministicIncidentGenerator(), scenario_repository=scenarios,
        session_repository=InMemorySessionRepository(),
        generation_service=pipeline(FakeIncidentAIProvider(draft())),
    )
    started = asyncio.run(service.start_session_async(request().difficulty, seed=51, now=NOW))
    definition = scenarios.get(started.scenario_id)
    assert started.post_incident is None
    assert service.get_progress(started.session_id, now=NOW).post_incident is None
    for step in definition.solution:
        service.execute_command(started.session_id, step.input, now=NOW)
    finished = service.get_progress(started.session_id, now=NOW)
    assert finished.progress.mission_complete
    assert finished.post_incident.root_cause == definition.post_incident.root_cause


def test_unknown_installed_package_is_rejected():
    payload = draft().model_dump(mode="json")
    fields = payload["initial_world_state"]["resources"][0]["attributes"]
    for field in fields:
        if field["key"] == "installed_packages":
            field["value"] = ["unknown-package"]
    provider = SequenceProvider(payload, payload)
    result = asyncio.run(pipeline(provider).generate(request(), now=NOW))
    assert provider.requests[1].validation_feedback == ("capability",)
    assert result.generation.generation_source is GenerationSource.DETERMINISTIC
