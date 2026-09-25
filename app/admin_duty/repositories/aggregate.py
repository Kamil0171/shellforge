from dataclasses import dataclass
from uuid import UUID

from app.admin_duty.domain.definition import IncidentDefinition
from app.admin_duty.domain.runtime import SessionRuntimeState
from app.admin_duty.repositories.protocols import (
    ScenarioConflictError,
    ScenarioRepository,
    SessionRepository,
)


@dataclass(frozen=True, slots=True)
class StoredIncidentSession:
    definition: IncidentDefinition
    state: SessionRuntimeState


class SplitIncidentSessionRepository:
    def __init__(
        self,
        scenarios: ScenarioRepository,
        sessions: SessionRepository,
    ) -> None:
        self._scenarios = scenarios
        self._sessions = sessions

    def create(self, definition, state, *, now=None):
        self._scenarios.save(definition)
        try:
            self._sessions.save(state, now=now)
        except Exception:
            self._scenarios.delete(definition.scenario_id)
            raise

    def get(self, session_id, *, now=None):
        state = self._sessions.get(session_id, now=now)
        definition = self._scenarios.get(state.scenario_id)
        return StoredIncidentSession(definition=definition, state=state)

    def update(self, definition, state, *, expected_revision, now=None):
        current = self._scenarios.get(state.scenario_id)
        if current != definition:
            raise ScenarioConflictError(
                "Nie można zmienić definicji istniejącej sesji."
            )
        self._sessions.update(
            state,
            expected_revision=expected_revision,
            now=now,
        )

    def cleanup_expired(self, *, now=None) -> tuple[UUID, ...]:
        expired_states = self._sessions.cleanup_expired(now=now)
        expired_scenario_ids = {state.scenario_id for state in expired_states}
        for scenario_id in expired_scenario_ids:
            if not self._sessions.has_scenario(scenario_id, now=now):
                self._scenarios.delete(scenario_id)
        return tuple(state.session_id for state in expired_states)
