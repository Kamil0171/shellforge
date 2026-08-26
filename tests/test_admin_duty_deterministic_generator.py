from datetime import UTC, datetime

import pytest

from app.admin_duty.domain.definition import ComponentType, ResourceType
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.generators import (
    DeterministicIncidentGenerator,
    GenerationError,
    UnsupportedDifficultyError,
)
from app.admin_duty.validators import IncidentValidationError

FIXED_NOW = datetime(2026, 8, 25, 20, 0, tzinfo=UTC)


def test_easy_generator_builds_valid_component_incident():
    definition = DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY, seed=123, now=FIXED_NOW
    )
    resources = definition.initial_world_state.resources
    hosts = [r for r in resources if r.resource_type is ResourceType.HOST]
    services = [r for r in resources if r.resource_type is ResourceType.SERVICE]

    assert definition.difficulty is DifficultyLevel.EASY
    assert definition.created_at == FIXED_NOW
    assert definition.generation.seed == 123
    assert len(hosts) == 2
    assert len(services) == 1
    assert services[0].state == "failed"
    assert len(definition.faults) == 1
    assert len(definition.symptoms) == 1
    assert len(definition.objectives) == 1
    assert len(definition.hints) == 3
    assert definition.solution
    assert definition.initial_world_state.map.interactions


def test_same_seed_is_deterministic_outside_identity_and_timestamp():
    generator = DeterministicIncidentGenerator()
    first = generator.generate(DifficultyLevel.EASY, seed=987, now=FIXED_NOW)
    second = generator.generate(
        DifficultyLevel.EASY, seed=987, now=FIXED_NOW.replace(hour=21)
    )
    excluded = {"scenario_id", "created_at"}

    assert first.scenario_id != second.scenario_id
    assert first.model_dump(exclude=excluded) == second.model_dump(exclude=excluded)


def test_seed_none_creates_and_persists_safe_effective_seed():
    definition = DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY, now=FIXED_NOW
    )

    assert definition.generation.seed is not None
    assert 0 <= definition.generation.seed <= 2**63 - 1


def test_generated_provenance_contains_all_required_component_types():
    definition = DeterministicIncidentGenerator().generate(
        DifficultyLevel.EASY, seed=8, now=FIXED_NOW
    )
    component_types = {item.component_type for item in definition.generation.components}

    assert component_types == {
        ComponentType.MAP,
        ComponentType.ENVIRONMENT,
        ComponentType.FAULT,
        ComponentType.SYMPTOM,
        ComponentType.OBJECTIVE,
        ComponentType.CAPABILITY,
        ComponentType.SCORING_POLICY,
    }


def test_known_seed_range_covers_entire_catalog_and_many_combinations():
    generator = DeterministicIncidentGenerator()
    definitions = [
        generator.generate(DifficultyLevel.EASY, seed=seed, now=FIXED_NOW)
        for seed in range(50)
    ]
    environments = {d.initial_world_state.environment_id for d in definitions}
    faults = {d.faults[0].fault_type for d in definitions}
    combinations = {
        (d.initial_world_state.environment_id, d.faults[0].fault_type)
        for d in definitions
    }

    assert environments == {
        "web-application",
        "internal-business-service",
        "reverse-proxy-stack",
    }
    assert faults == {
        "systemd_service_failed",
        "systemd_wrong_exec_start",
        "systemd_missing_environment_variable",
        "systemd_permission_denied",
    }
    assert len(combinations) == 12


def test_generator_retries_validation_at_most_ten_times():
    class RejectingValidator:
        def __init__(self):
            self.calls = 0

        def validate(self, definition):
            self.calls += 1
            raise IncidentValidationError("reject")

    validator = RejectingValidator()
    generator = DeterministicIncidentGenerator(validator=validator)

    with pytest.raises(GenerationError):
        generator.generate(DifficultyLevel.EASY, seed=10, now=FIXED_NOW)

    assert validator.calls == 10


@pytest.mark.parametrize("difficulty", [DifficultyLevel.MEDIUM, DifficultyLevel.HARD])
def test_generator_rejects_unimplemented_difficulties(difficulty):
    with pytest.raises(UnsupportedDifficultyError):
        DeterministicIncidentGenerator().generate(difficulty, now=FIXED_NOW)
