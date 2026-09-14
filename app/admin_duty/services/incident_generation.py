import asyncio
import logging
from time import monotonic

from app.admin_duty.domain.definition import (
    GenerationSource,
    ScenarioPoolMetadata,
    ValidationStatus,
)
from app.admin_duty.domain.generation import (
    DraftValidationError,
    IncidentAIProvider,
    generate_validated_incident,
)
from app.admin_duty.providers import GemmaProvider, IncidentProviderError
from app.admin_duty.services.ai_materializer import MaterializingIncidentAIProvider
from app.config import IncidentAISettings

logger = logging.getLogger(__name__)
MAX_AI_ATTEMPTS = 2


def validated_scenario_metadata(definition):
    return ScenarioPoolMetadata(
        scenario_id=definition.scenario_id,
        generation_source=definition.generation.generation_source,
        provider=definition.generation.generator_id,
        model=definition.generation.model,
        created_at=definition.created_at,
        difficulty=definition.difficulty,
        validation_status=ValidationStatus.VALID,
        schema_version=definition.schema_version,
        quality_version="1.0",
    )


class IncidentGenerationService:
    def __init__(self, *, fallback, provider: IncidentAIProvider | None = None, timeout_seconds=20):
        self._fallback = fallback
        self._provider = provider
        self._timeout = timeout_seconds

    async def generate(self, request, *, now=None):
        if self._provider is not None and request.generation_source is GenerationSource.AI:
            attempt_request = request
            for attempt in range(1, MAX_AI_ATTEMPTS + 1):
                started = monotonic()
                try:
                    async with asyncio.timeout(self._timeout):
                        definition = await generate_validated_incident(
                            self._provider, attempt_request, created_at=now,
                        )
                    logger.info("incident_ai attempt=%d result=accepted latency_ms=%d", attempt, (monotonic() - started) * 1000)
                    return definition
                except TimeoutError:
                    category = "timeout"
                except (DraftValidationError, IncidentProviderError) as error:
                    category = error.category
                except Exception:
                    category = "unavailable"
                if category not in {
                    "schema", "plan", "materialization", "capability", "semantic", "replay", "request_mismatch",
                    "timeout", "transport", "api_error", "rate_limit", "unavailable",
                    "rejected", "invalid_response", "invalid_json",
                }:
                    category = "unavailable"
                logger.info("incident_ai attempt=%d result=%s latency_ms=%d", attempt, category, (monotonic() - started) * 1000)
                attempt_request = request.model_copy(update={"validation_feedback": (category,)})
                if category == "rejected":
                    break
        logger.info("incident_generation fallback=deterministic")
        fallback_request = request.model_copy(update={
            "generation_source": GenerationSource.DETERMINISTIC, "validation_feedback": (),
        })
        return self._fallback.generate_from_request(fallback_request, now=now)


def configured_generation_service(fallback):
    settings = IncidentAISettings.from_environment()
    return IncidentGenerationService(
        fallback=fallback,
        provider=MaterializingIncidentAIProvider(GemmaProvider(settings), model=settings.model) if settings.enabled else None,
        timeout_seconds=settings.timeout_seconds,
    )
