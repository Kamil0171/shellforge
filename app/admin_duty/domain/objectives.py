from app.admin_duty.domain.definition import (
    CompletionCondition,
    ConditionOperator,
    Identifier,
    IncidentDefinition,
    JsonValue,
    Objective,
)
from app.admin_duty.domain.runtime import (
    RuntimeResource,
    RuntimeWorldState,
    SessionRuntimeState,
)

type ResolvedConditionValue = JsonValue | list[Identifier]


class ObjectiveEvaluationError(ValueError):
    pass


def _parse_condition_field(field: str) -> tuple[str, str | None]:
    if field == "resource":
        return field, None

    if field in {"current_state", "parent_resource_id", "dependencies"}:
        return field, None

    attribute_prefix = "attributes."
    if field.startswith(attribute_prefix):
        attribute_key = field.removeprefix(attribute_prefix)
        if attribute_key and not attribute_key.startswith("_"):
            return "attributes", attribute_key

    raise ObjectiveEvaluationError(f"Nieobsługiwane pole warunku ukończenia: {field}.")


def _validate_operator_for_field(
    operator: ConditionOperator,
    field_type: str,
) -> None:
    resource_operators = {
        ConditionOperator.EXISTS,
        ConditionOperator.NOT_EXISTS,
    }

    if field_type == "resource" and operator not in resource_operators:
        raise ObjectiveEvaluationError(
            "Pole resource obsługuje wyłącznie operatory exists i not_exists."
        )

    if field_type != "resource" and operator in resource_operators:
        raise ObjectiveEvaluationError(
            "Operatory exists i not_exists wymagają pola resource."
        )


def _resolve_field_value(
    resource: RuntimeResource,
    field_type: str,
    attribute_key: str | None,
) -> tuple[bool, ResolvedConditionValue]:
    if field_type == "current_state":
        return True, resource.current_state

    if field_type == "parent_resource_id":
        return True, resource.parent_resource_id

    if field_type == "dependencies":
        return True, resource.dependencies

    if attribute_key not in resource.attributes:
        return False, None

    return True, resource.attributes[attribute_key]


def _contains(
    value: ResolvedConditionValue,
    expected: JsonValue,
) -> bool:
    if isinstance(value, str):
        return isinstance(expected, str) and expected in value

    if isinstance(value, (tuple, list)):
        return expected in value

    return False


def evaluate_condition(
    condition: CompletionCondition,
    world: RuntimeWorldState,
) -> bool:
    field_type, attribute_key = _parse_condition_field(condition.field)
    _validate_operator_for_field(condition.operator, field_type)
    resource = world.resources.get(condition.resource_id)

    if field_type == "resource":
        if condition.operator is ConditionOperator.EXISTS:
            return resource is not None
        return resource is None

    if resource is None:
        return False

    field_exists, value = _resolve_field_value(
        resource,
        field_type,
        attribute_key,
    )

    if not field_exists:
        return condition.operator is ConditionOperator.NOT_EQUALS

    if condition.operator is ConditionOperator.EQUALS:
        return value == condition.expected

    if condition.operator is ConditionOperator.NOT_EQUALS:
        return value != condition.expected

    if condition.operator is ConditionOperator.CONTAINS:
        return _contains(value, condition.expected)

    raise ObjectiveEvaluationError(
        f"Nieobsługiwany operator warunku: {condition.operator.value}."
    )


def evaluate_objective(
    objective: Objective,
    world: RuntimeWorldState,
) -> bool:
    if objective.completion_condition is None:
        return True
    return evaluate_condition(objective.completion_condition, world)


def evaluate_objectives(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> frozenset[Identifier]:
    if definition.scenario_id != state.scenario_id:
        raise ObjectiveEvaluationError(
            "Definicja incydentu i sesja mają różne scenario_id."
        )

    return frozenset(
        objective.objective_id
        for objective in definition.objectives
        if evaluate_objective(objective, state.world_state)
        and set(objective.completion_fact_ids) <= state.discovered_fact_ids
    )
