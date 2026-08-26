from collections.abc import Iterable
from datetime import datetime

from pydantic import TypeAdapter, ValidationError

from app.admin_duty.domain.definition import (
    FrozenDomainModel,
    Identifier,
    IncidentDefinition,
    JsonValue,
)
from app.admin_duty.domain.objectives import evaluate_objectives
from app.admin_duty.domain.progress import SessionProgress, get_session_progress
from app.admin_duty.domain.runtime import (
    RuntimeResource,
    SessionRuntimeState,
    SessionStatus,
    _require_active_session,
    _resolve_operation_time,
)


class DynamicIncidentEngineError(ValueError):
    pass


class ResourceStateUpdate(FrozenDomainModel):
    resource_id: Identifier
    new_state: Identifier


class ResourceAttributeUpdate(FrozenDomainModel):
    resource_id: Identifier
    attribute: Identifier
    value: JsonValue


type IncidentAction = ResourceStateUpdate | ResourceAttributeUpdate


def _get_action_resource_id(action: IncidentAction) -> Identifier:
    if isinstance(action, (ResourceStateUpdate, ResourceAttributeUpdate)):
        return action.resource_id

    raise DynamicIncidentEngineError("Nieobsługiwany typ akcji incydentu.")


def _is_no_op(
    resource: RuntimeResource,
    action: IncidentAction,
) -> bool:
    if isinstance(action, ResourceStateUpdate):
        return resource.current_state == action.new_state

    if isinstance(action, ResourceAttributeUpdate):
        return (
            action.attribute in resource.attributes
            and resource.attributes[action.attribute] == action.value
        )

    raise DynamicIncidentEngineError("Nieobsługiwany typ akcji incydentu.")


def _apply_action(
    resource: RuntimeResource,
    action: IncidentAction,
) -> None:
    if isinstance(action, ResourceStateUpdate):
        resource.current_state = action.new_state
        return

    if isinstance(action, ResourceAttributeUpdate):
        attributes = resource.attributes.copy()
        attributes[action.attribute] = action.value
        resource.attributes = attributes
        return

    raise DynamicIncidentEngineError("Nieobsługiwany typ akcji incydentu.")


def _mission_is_complete(
    definition: IncidentDefinition,
    completed_objective_ids: frozenset[Identifier],
) -> bool:
    required_objective_ids = {
        objective.objective_id
        for objective in definition.objectives
        if objective.required
    }
    return required_objective_ids <= completed_objective_ids


def _validate_candidate(
    candidate: SessionRuntimeState,
) -> SessionRuntimeState:
    return SessionRuntimeState.model_validate(
        candidate.model_dump(mode="python", round_trip=True)
    )


def _commit_candidate(
    state: SessionRuntimeState,
    candidate: SessionRuntimeState,
) -> None:
    object.__setattr__(state, "__dict__", dict(candidate.__dict__))


def _validate_command_cost(command_cost: int | None) -> None:
    if command_cost is None:
        return

    if isinstance(command_cost, bool) or not isinstance(command_cost, int):
        raise DynamicIncidentEngineError("Koszt komendy musi być liczbą całkowitą.")

    if command_cost < 0:
        raise DynamicIncidentEngineError("Koszt komendy nie może być ujemny.")


def _validate_discovered_fact_ids(
    discovered_fact_ids: Iterable[Identifier],
) -> tuple[Identifier, ...]:
    if isinstance(discovered_fact_ids, (str, bytes)):
        raise DynamicIncidentEngineError(
            "Identyfikatory faktów muszą być przekazane jako kolekcja."
        )

    try:
        return TypeAdapter(tuple[Identifier, ...]).validate_python(discovered_fact_ids)
    except ValidationError as error:
        raise DynamicIncidentEngineError(
            "Komenda zawiera nieprawidłowy identyfikator faktu."
        ) from error


class DynamicIncidentEngine:
    def execute(
        self,
        definition: IncidentDefinition,
        state: SessionRuntimeState,
        action: IncidentAction,
        *,
        now: datetime | None = None,
    ) -> SessionProgress:
        return self._execute(
            definition,
            state,
            action,
            command_cost=None,
            discovered_fact_ids=(),
            now=now,
        )

    def execute_command(
        self,
        definition: IncidentDefinition,
        state: SessionRuntimeState,
        action: IncidentAction | None = None,
        *,
        command_cost: int,
        discovered_fact_ids: Iterable[Identifier] = (),
        now: datetime | None = None,
    ) -> SessionProgress:
        return self._execute(
            definition,
            state,
            action,
            command_cost=command_cost,
            discovered_fact_ids=discovered_fact_ids,
            now=now,
        )

    def _execute(
        self,
        definition: IncidentDefinition,
        state: SessionRuntimeState,
        action: IncidentAction | None,
        *,
        command_cost: int | None,
        discovered_fact_ids: Iterable[Identifier],
        now: datetime | None,
    ) -> SessionProgress:
        if definition.scenario_id != state.scenario_id:
            raise DynamicIncidentEngineError(
                "Definicja incydentu i sesja mają różne scenario_id."
            )

        _require_active_session(state)
        operation_time = _resolve_operation_time(state, now)

        if action is None and command_cost is None:
            raise DynamicIncidentEngineError(
                "Czysta operacja domenowa wymaga akcji incydentu."
            )

        resource_id = None
        resource = None
        world_is_no_op = action is None

        if action is not None:
            resource_id = _get_action_resource_id(action)
            resource = state.world_state.resources.get(resource_id)

            if resource is None:
                raise DynamicIncidentEngineError(
                    f"Zasób runtime nie istnieje: {resource_id}."
                )

            world_is_no_op = _is_no_op(resource, action)

        _validate_command_cost(command_cost)
        validated_fact_ids = _validate_discovered_fact_ids(discovered_fact_ids)

        if world_is_no_op and command_cost is None:
            return get_session_progress(definition, state)

        candidate = state.model_copy(deep=True)

        if action is not None and not world_is_no_op:
            candidate_resource = candidate.world_state.resources[resource_id]
            _apply_action(candidate_resource, action)

        if command_cost is not None:
            candidate.commands_used += 1
            candidate.score = max(0, candidate.score - command_cost)
            candidate.discovered_fact_ids.update(validated_fact_ids)

        completed_objective_ids = evaluate_objectives(definition, candidate)
        candidate.completed_objective_ids = set(completed_objective_ids)
        candidate.status = (
            SessionStatus.COMPLETED
            if _mission_is_complete(definition, completed_objective_ids)
            else SessionStatus.ACTIVE
        )
        candidate.last_activity = operation_time
        candidate.revision = state.revision + 1
        candidate = _validate_candidate(candidate)
        get_session_progress(definition, candidate)

        original_fields = state.__dict__
        _commit_candidate(state, candidate)
        try:
            return get_session_progress(definition, state)
        except Exception:
            object.__setattr__(state, "__dict__", original_fields)
            raise
