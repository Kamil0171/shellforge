from uuid import UUID

from pydantic import Field

from app.admin_duty.domain.definition import (
    FrozenDomainModel,
    Identifier,
    IncidentDefinition,
)
from app.admin_duty.domain.recovery import recovery_allows_completion
from app.admin_duty.domain.runtime import SessionRuntimeState, SessionStatus


class SessionProgressConsistencyError(ValueError):
    pass


class ObjectiveProgress(FrozenDomainModel):
    objective_id: Identifier
    label: str = Field(min_length=1, max_length=240)
    required: bool
    completed: bool
    order: int = Field(ge=1, le=100)


class SessionProgress(FrozenDomainModel):
    scenario_id: UUID
    session_id: UUID
    status: SessionStatus
    score: int = Field(ge=0, le=1_000_000)
    commands_used: int = Field(ge=0)
    hints_used: int = Field(ge=0)
    solution_viewed: bool
    completed_objectives: int = Field(ge=0)
    total_objectives: int = Field(ge=0)
    mission_complete: bool
    objectives: tuple[ObjectiveProgress, ...]
    revision: int = Field(ge=0)


def get_session_progress(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> SessionProgress:
    if definition.scenario_id != state.scenario_id:
        raise SessionProgressConsistencyError(
            "Definicja incydentu i sesja mają różne scenario_id."
        )

    completed_objective_ids = frozenset(state.completed_objective_ids)
    definition_objective_ids = {
        objective.objective_id for objective in definition.objectives
    }
    unknown_objective_ids = completed_objective_ids - definition_objective_ids

    if unknown_objective_ids:
        unknown_ids = ", ".join(sorted(unknown_objective_ids))
        raise SessionProgressConsistencyError(
            "Sesja zawiera nieznane ukończone cele: " + unknown_ids
        )

    sorted_objectives = sorted(
        definition.objectives,
        key=lambda objective: (objective.order, objective.objective_id),
    )
    objectives = tuple(
        ObjectiveProgress(
            objective_id=objective.objective_id,
            label=objective.label,
            required=objective.required,
            completed=objective.objective_id in completed_objective_ids,
            order=objective.order,
        )
        for objective in sorted_objectives
    )
    required_objective_ids = {
        objective.objective_id
        for objective in definition.objectives
        if objective.required
    }

    return SessionProgress(
        scenario_id=definition.scenario_id,
        session_id=state.session_id,
        status=state.status,
        score=state.score,
        commands_used=state.commands_used,
        hints_used=state.hints_used,
        solution_viewed=state.solution_viewed,
        completed_objectives=len(completed_objective_ids),
        total_objectives=len(definition.objectives),
        mission_complete=(
            required_objective_ids <= completed_objective_ids
            and recovery_allows_completion(definition, state)
        ),
        objectives=objectives,
        revision=state.revision,
    )
