from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.admin_duty.domain.definition import (
    CompletionCondition,
    ConditionOperator,
    Objective,
)
from app.admin_duty.domain.objectives import (
    ObjectiveEvaluationError,
    evaluate_condition,
    evaluate_objective,
    evaluate_objectives,
)
from app.admin_duty.domain.runtime import create_session_runtime
from tests.test_admin_duty_incident_definition import build_incident_definition

FIXED_NOW = datetime(2026, 8, 24, 18, 0, tzinfo=UTC)


def build_context():
    definition = build_incident_definition()
    state = create_session_runtime(definition, now=FIXED_NOW)
    return definition, state


def build_condition(
    *,
    field: str,
    operator: ConditionOperator,
    expected=None,
    resource_id: str = "service-api",
) -> CompletionCondition:
    return CompletionCondition(
        resource_id=resource_id,
        field=field,
        operator=operator,
        expected=expected,
    )


def build_objective(
    objective_id: str,
    condition: CompletionCondition,
    *,
    required: bool = True,
) -> Objective:
    return Objective(
        objective_id=objective_id,
        label=f"Cel {objective_id}",
        required=required,
        completion_condition=condition,
        order=1,
    )


@pytest.mark.parametrize(
    ("operator", "expected", "result"),
    [
        (ConditionOperator.EQUALS, "failed", True),
        (ConditionOperator.EQUALS, "active", False),
        (ConditionOperator.NOT_EQUALS, "active", True),
        (ConditionOperator.NOT_EQUALS, "failed", False),
    ],
)
def test_current_state_comparison(operator, expected, result):
    _, state = build_context()
    condition = build_condition(
        field="current_state",
        operator=operator,
        expected=expected,
    )

    assert evaluate_condition(condition, state.world_state) is result


@pytest.mark.parametrize(
    ("resource_id", "operator", "result"),
    [
        ("service-api", ConditionOperator.EXISTS, True),
        ("missing-service", ConditionOperator.EXISTS, False),
        ("service-api", ConditionOperator.NOT_EXISTS, False),
        ("missing-service", ConditionOperator.NOT_EXISTS, True),
    ],
)
def test_resource_existence(resource_id, operator, result):
    _, state = build_context()
    condition = build_condition(
        resource_id=resource_id,
        field="resource",
        operator=operator,
    )

    assert evaluate_condition(condition, state.world_state) is result


@pytest.mark.parametrize(
    "operator",
    [
        ConditionOperator.EQUALS,
        ConditionOperator.NOT_EQUALS,
        ConditionOperator.CONTAINS,
    ],
)
def test_missing_resource_is_false_for_value_operators(operator):
    _, state = build_context()
    condition = build_condition(
        resource_id="missing-service",
        field="current_state",
        operator=operator,
        expected="failed",
    )

    assert evaluate_condition(condition, state.world_state) is False


def test_parent_resource_id_can_be_compared():
    _, state = build_context()
    condition = build_condition(
        field="parent_resource_id",
        operator=ConditionOperator.EQUALS,
        expected="host-app",
    )

    assert evaluate_condition(condition, state.world_state) is True


@pytest.mark.parametrize(
    ("operator", "expected", "result"),
    [
        (ConditionOperator.EQUALS, 8100, True),
        (ConditionOperator.NOT_EQUALS, 8200, True),
    ],
)
def test_attribute_value_can_be_compared(operator, expected, result):
    _, state = build_context()
    condition = build_condition(
        field="attributes.port",
        operator=operator,
        expected=expected,
    )

    assert evaluate_condition(condition, state.world_state) is result


@pytest.mark.parametrize(
    ("operator", "result"),
    [
        (ConditionOperator.EQUALS, False),
        (ConditionOperator.NOT_EQUALS, True),
        (ConditionOperator.CONTAINS, False),
    ],
)
def test_missing_attribute_has_defined_comparison_semantics(operator, result):
    _, state = build_context()
    condition = build_condition(
        field="attributes.missing",
        operator=operator,
        expected="value",
    )

    assert evaluate_condition(condition, state.world_state) is result


def test_contains_supports_string_substring():
    _, state = build_context()
    condition = build_condition(
        field="attributes.manager",
        operator=ConditionOperator.CONTAINS,
        expected="stem",
    )

    assert evaluate_condition(condition, state.world_state) is True


def test_contains_string_requires_string_expected_value():
    _, state = build_context()
    condition = build_condition(
        field="attributes.manager",
        operator=ConditionOperator.CONTAINS,
        expected=1,
    )

    assert evaluate_condition(condition, state.world_state) is False


def test_contains_supports_tuple_membership():
    _, state = build_context()
    service = state.world_state.resources["service-api"]
    service.attributes["roles"] = ("api", "worker")
    condition = build_condition(
        field="attributes.roles",
        operator=ConditionOperator.CONTAINS,
        expected="worker",
    )

    assert evaluate_condition(condition, state.world_state) is True


def test_contains_supports_dependencies_list_membership():
    _, state = build_context()
    service = state.world_state.resources["service-api"]
    service.dependencies.extend(("database", "dns"))
    condition = build_condition(
        field="dependencies",
        operator=ConditionOperator.CONTAINS,
        expected="dns",
    )

    assert evaluate_condition(condition, state.world_state) is True


def test_contains_does_not_convert_unsupported_value_to_string():
    _, state = build_context()
    condition = build_condition(
        field="attributes.port",
        operator=ConditionOperator.CONTAINS,
        expected="81",
    )

    assert evaluate_condition(condition, state.world_state) is False


@pytest.mark.parametrize(
    "field",
    ["internal_secret", "model_dump", "attributes.__class__"],
)
def test_unsupported_field_is_rejected(field):
    _, state = build_context()
    condition = build_condition(
        field=field,
        operator=ConditionOperator.EQUALS,
        expected="value",
    )

    with pytest.raises(ObjectiveEvaluationError, match="Nieobsługiwane pole"):
        evaluate_condition(condition, state.world_state)


def test_dunder_field_is_rejected_even_for_unvalidated_condition():
    _, state = build_context()
    condition = CompletionCondition.model_construct(
        resource_id="service-api",
        field="__class__",
        operator=ConditionOperator.EQUALS,
        expected=None,
    )

    with pytest.raises(ObjectiveEvaluationError, match="Nieobsługiwane pole"):
        evaluate_condition(condition, state.world_state)


@pytest.mark.parametrize(
    ("field", "operator"),
    [
        ("resource", ConditionOperator.EQUALS),
        ("current_state", ConditionOperator.EXISTS),
        ("attributes.manager", ConditionOperator.NOT_EXISTS),
    ],
)
def test_invalid_operator_and_field_combination_is_rejected(field, operator):
    _, state = build_context()
    condition = build_condition(
        field=field,
        operator=operator,
        expected="failed",
    )

    with pytest.raises(ObjectiveEvaluationError):
        evaluate_condition(condition, state.world_state)


def test_evaluate_objective_delegates_to_its_completion_condition():
    _, state = build_context()
    objective = build_objective(
        "restore-service",
        build_condition(
            field="current_state",
            operator=ConditionOperator.EQUALS,
            expected="failed",
        ),
    )

    assert evaluate_objective(objective, state.world_state) is True


def test_evaluate_objectives_includes_required_and_optional_matches():
    definition, state = build_context()
    definition = definition.model_copy(
        update={
            "objectives": (
                build_objective(
                    "restore-service",
                    build_condition(
                        field="current_state",
                        operator=ConditionOperator.EQUALS,
                        expected="failed",
                    ),
                ),
                build_objective(
                    "document-incident",
                    build_condition(
                        field="attributes.manager",
                        operator=ConditionOperator.EQUALS,
                        expected="systemd",
                    ),
                    required=False,
                ),
                build_objective(
                    "activate-service",
                    build_condition(
                        field="current_state",
                        operator=ConditionOperator.EQUALS,
                        expected="active",
                    ),
                ),
            )
        }
    )

    result = evaluate_objectives(definition, state)

    assert result == frozenset({"restore-service", "document-incident"})
    assert isinstance(result, frozenset)


def test_evaluate_objectives_rejects_scenario_mismatch():
    definition, state = build_context()
    state.scenario_id = uuid4()

    with pytest.raises(ObjectiveEvaluationError, match="różne scenario_id"):
        evaluate_objectives(definition, state)


def test_evaluation_is_deterministic_and_does_not_mutate_inputs():
    definition, state = build_context()
    definition = definition.model_copy(
        update={
            "objectives": (
                build_objective(
                    "service-failed",
                    build_condition(
                        field="current_state",
                        operator=ConditionOperator.EQUALS,
                        expected="failed",
                    ),
                ),
            )
        }
    )
    state.completed_objective_ids.add("previous-result")
    definition_before = definition.model_dump_json()
    state_before = state.model_dump_json()
    revision_before = state.revision
    last_activity_before = state.last_activity
    completed_before = state.completed_objective_ids.copy()

    first_result = evaluate_objectives(definition, state)
    second_result = evaluate_objectives(definition, state)

    assert first_result == second_result == frozenset({"service-failed"})
    assert definition.model_dump_json() == definition_before
    assert state.model_dump_json() == state_before
    assert state.revision == revision_before
    assert state.last_activity == last_activity_before
    assert state.completed_objective_ids == completed_before
