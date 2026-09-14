from enum import StrEnum

from app.admin_duty.domain.definition import Identifier, IncidentDefinition
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.objectives import evaluate_condition
from app.admin_duty.domain.runtime import SessionRuntimeState


class IncidentRecoveryState(StrEnum):
    BROKEN = "broken"
    PARTIALLY_RECOVERED = "partially_recovered"
    HEALTHY = "healthy"


def resolved_fault_ids(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> frozenset[Identifier]:
    return frozenset(
        fault.fault_id
        for fault in definition.faults
        if fault.resolution_condition is not None
        and evaluate_condition(fault.resolution_condition, state.world_state)
    )


def get_incident_recovery_state(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> IncidentRecoveryState:
    resolved = resolved_fault_ids(definition, state)
    if not resolved:
        return IncidentRecoveryState.BROKEN
    if len(resolved) < len(definition.faults):
        return IncidentRecoveryState.PARTIALLY_RECOVERED
    return IncidentRecoveryState.HEALTHY


def recovery_allows_completion(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> bool:
    if definition.difficulty is not DifficultyLevel.HARD:
        return True
    return get_incident_recovery_state(definition, state) is IncidentRecoveryState.HEALTHY
