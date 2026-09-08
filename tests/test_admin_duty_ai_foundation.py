import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.admin_duty.components.scenarios import build_medium_draft
from app.admin_duty.domain.definition import GenerationSource
from app.admin_duty.domain.generation import (
    DraftValidationError,
    FakeIncidentAIProvider,
    GeneratedIncidentDraft,
    IncidentGenerationRequest,
    generate_validated_incident,
    get_ai_capability_catalog,
    validate_and_convert_draft,
)

NOW = datetime(2026, 9, 8, 12, 0, tzinfo=UTC)


def ai_draft():
    return build_medium_draft("dependency-firewall-blocked", seed=51).model_copy(
        update={
            "generation_source": GenerationSource.AI,
            "model": "fake-provider-v1",
        }
    )


def test_generation_request_supports_lesson_linkage_and_strict_round_trip():
    request = IncidentGenerationRequest(
        difficulty="medium",
        environment_preferences=("multi-service",),
        allowed_fault_categories=("dependency-firewall-blocked",),
        map_id="web-operations-room",
        lesson_id=23,
        lesson_topic="firewalld",
        skill_tags=("network", "security"),
        seed=7,
        generation_source="ai",
    )

    restored = IncidentGenerationRequest.model_validate_json(request.model_dump_json())
    assert restored == request
    with pytest.raises(ValidationError):
        IncidentGenerationRequest.model_validate(
            {**request.model_dump(), "unexpected": True}
        )


def test_generated_draft_is_strict_data_only_and_rejects_invalid_schema():
    payload = ai_draft().model_dump(mode="json")
    payload["schema_version"] = "4.0"

    with pytest.raises(ValidationError):
        GeneratedIncidentDraft.model_validate(payload)


def test_capability_catalog_is_frozen_and_contains_controlled_allowlists():
    catalog = get_ai_capability_catalog()

    assert "remote.ssh" in catalog.supported_commands
    assert "network" in catalog.supported_dependency_types
    assert "python3-psycopg2" in catalog.supported_packages
    assert "web-operations-room" in catalog.supported_maps
    with pytest.raises(ValidationError):
        catalog.supported_commands = ("arbitrary-code",)


def test_unknown_capability_is_rejected_before_semantic_conversion():
    draft = ai_draft()
    capabilities = draft.capabilities.model_copy(
        update={
            "command_capability_ids": (
                *draft.capabilities.command_capability_ids,
                "python.execute",
            )
        }
    )

    with pytest.raises(DraftValidationError, match="capability"):
        validate_and_convert_draft(
            draft.model_copy(update={"capabilities": capabilities}),
            created_at=NOW,
        )


def test_unknown_service_reference_is_rejected_semantically():
    draft = ai_draft()
    dependency = draft.service_dependencies[0].model_copy(
        update={"target_service_id": "unknown-service"}
    )

    with pytest.raises(DraftValidationError, match="semantycznej"):
        validate_and_convert_draft(
            draft.model_copy(
                update={
                    "service_dependencies": (
                        dependency,
                        *draft.service_dependencies[1:],
                    )
                }
            ),
            created_at=NOW,
        )


def test_unknown_service_kind_is_rejected_by_capability_catalog():
    draft = ai_draft()
    resources = list(draft.initial_world_state.resources)
    service_index = next(
        index
        for index, resource in enumerate(resources)
        if resource.resource_id == "service-api"
    )
    service = resources[service_index]
    attributes = tuple(
        field.model_copy(update={"value": "arbitrary-service"})
        if field.key == "service_kind"
        else field
        for field in service.attributes
    )
    resources[service_index] = service.model_copy(update={"attributes": attributes})
    world = draft.initial_world_state.model_copy(update={"resources": tuple(resources)})

    with pytest.raises(DraftValidationError, match="rodzaj usługi"):
        validate_and_convert_draft(
            draft.model_copy(update={"initial_world_state": world}),
            created_at=NOW,
        )


def test_invalid_reference_solution_is_rejected_by_replay():
    draft = ai_draft()
    first = draft.solution[0].model_copy(update={"input": "unknown-command"})

    with pytest.raises(DraftValidationError, match="semantycznej"):
        validate_and_convert_draft(
            draft.model_copy(update={"solution": (first, *draft.solution[1:])}),
            created_at=NOW,
        )


def test_fake_provider_runs_full_validated_draft_pipeline():
    provider = FakeIncidentAIProvider(ai_draft())
    request = IncidentGenerationRequest(
        difficulty="medium",
        generation_source="ai",
        seed=51,
    )

    definition = asyncio.run(
        generate_validated_incident(
            provider,
            request,
            scenario_id=uuid4(),
            created_at=NOW,
        )
    )

    assert definition.generation.generation_source is GenerationSource.AI
    assert definition.generation.model == "fake-provider-v1"
    assert definition.schema_version == "3.0"


def test_provider_draft_must_match_generation_request():
    provider = FakeIncidentAIProvider(ai_draft())
    request = IncidentGenerationRequest(
        difficulty="medium",
        generation_source="ai",
        seed=999,
    )

    with pytest.raises(DraftValidationError, match="ziarnu"):
        asyncio.run(generate_validated_incident(provider, request, created_at=NOW))
