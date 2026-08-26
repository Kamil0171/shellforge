from datetime import UTC, datetime, timedelta
from threading import RLock
from uuid import UUID

from app.admin_duty.domain.definition import IncidentDefinition
from app.admin_duty.domain.runtime import SessionRuntimeState
from app.admin_duty.repositories.protocols import (
    ScenarioConflictError,
    ScenarioNotFoundError,
    SessionConflictError,
    SessionLimitError,
    SessionNotFoundError,
)

SESSION_TTL = timedelta(minutes=45)
MAX_ACTIVE_SESSIONS = 500


def utc_now() -> datetime:
    return datetime.now(UTC)


def _resolve_now(now: datetime | None) -> datetime:
    current_time = now if now is not None else utc_now()

    if current_time.tzinfo is None or current_time.utcoffset() is None:
        raise ValueError("Czas repository musi zawierać strefę czasową.")

    return current_time


def _copy_state(state: SessionRuntimeState) -> SessionRuntimeState:
    return state.model_copy(deep=True)


class InMemoryScenarioRepository:
    def __init__(self) -> None:
        self._definitions: dict[UUID, IncidentDefinition] = {}
        self._lock = RLock()

    def save(self, definition: IncidentDefinition) -> None:
        with self._lock:
            existing = self._definitions.get(definition.scenario_id)

            if existing is None:
                self._definitions[definition.scenario_id] = definition
                return

            if existing != definition:
                raise ScenarioConflictError(
                    "Scenario ID jest już przypisane do innej definicji."
                )

    def get(self, scenario_id: UUID) -> IncidentDefinition:
        with self._lock:
            try:
                return self._definitions[scenario_id]
            except KeyError as error:
                raise ScenarioNotFoundError(
                    "Definicja incydentu nie istnieje."
                ) from error

    def exists(self, scenario_id: UUID) -> bool:
        with self._lock:
            return scenario_id in self._definitions

    def delete(self, scenario_id: UUID) -> bool:
        with self._lock:
            return self._definitions.pop(scenario_id, None) is not None


class InMemorySessionRepository:
    def __init__(
        self,
        *,
        ttl: timedelta = SESSION_TTL,
        max_sessions: int = MAX_ACTIVE_SESSIONS,
    ) -> None:
        if ttl <= timedelta(0):
            raise ValueError("TTL sesji musi być dodatni.")

        if max_sessions < 1:
            raise ValueError("Limit sesji musi być dodatni.")

        self._ttl = ttl
        self._max_sessions = max_sessions
        self._sessions: dict[UUID, SessionRuntimeState] = {}
        self._lock = RLock()

    @property
    def ttl(self) -> timedelta:
        return self._ttl

    @property
    def max_sessions(self) -> int:
        return self._max_sessions

    def _cleanup_expired_locked(
        self,
        now: datetime,
    ) -> tuple[SessionRuntimeState, ...]:
        expired_ids = tuple(
            session_id
            for session_id, state in self._sessions.items()
            if now - state.last_activity >= self._ttl
        )
        expired_states = tuple(
            self._sessions.pop(session_id) for session_id in expired_ids
        )
        return tuple(_copy_state(state) for state in expired_states)

    def save(
        self,
        state: SessionRuntimeState,
        *,
        now: datetime | None = None,
    ) -> None:
        current_time = _resolve_now(now)

        with self._lock:
            self._cleanup_expired_locked(current_time)

            if state.session_id in self._sessions:
                raise SessionConflictError("Sesja już istnieje.")

            if len(self._sessions) >= self._max_sessions:
                raise SessionLimitError("Limit aktywnych sesji został osiągnięty.")

            self._sessions[state.session_id] = _copy_state(state)

    def get(
        self,
        session_id: UUID,
        *,
        now: datetime | None = None,
    ) -> SessionRuntimeState:
        current_time = _resolve_now(now)

        with self._lock:
            self._cleanup_expired_locked(current_time)

            try:
                return _copy_state(self._sessions[session_id])
            except KeyError as error:
                raise SessionNotFoundError("Sesja nie istnieje.") from error

    def update(
        self,
        state: SessionRuntimeState,
        *,
        expected_revision: int,
        now: datetime | None = None,
    ) -> None:
        current_time = _resolve_now(now)

        with self._lock:
            self._cleanup_expired_locked(current_time)
            existing = self._sessions.get(state.session_id)

            if existing is None:
                raise SessionNotFoundError("Sesja nie istnieje.")

            if existing.revision != expected_revision:
                raise SessionConflictError("Sesja została równocześnie zmodyfikowana.")

            if state.scenario_id != existing.scenario_id:
                raise SessionConflictError(
                    "Nie można zmienić scenario_id istniejącej sesji."
                )

            if state.revision <= expected_revision:
                raise SessionConflictError(
                    "Aktualizacja sesji wymaga nowszej revision."
                )

            self._sessions[state.session_id] = _copy_state(state)

    def delete(
        self,
        session_id: UUID,
        *,
        now: datetime | None = None,
    ) -> SessionRuntimeState:
        current_time = _resolve_now(now)

        with self._lock:
            self._cleanup_expired_locked(current_time)

            try:
                return _copy_state(self._sessions.pop(session_id))
            except KeyError as error:
                raise SessionNotFoundError("Sesja nie istnieje.") from error

    def cleanup_expired(
        self,
        *,
        now: datetime | None = None,
    ) -> tuple[SessionRuntimeState, ...]:
        current_time = _resolve_now(now)

        with self._lock:
            return self._cleanup_expired_locked(current_time)

    def has_scenario(
        self,
        scenario_id: UUID,
        *,
        now: datetime | None = None,
    ) -> bool:
        current_time = _resolve_now(now)

        with self._lock:
            self._cleanup_expired_locked(current_time)
            return any(
                state.scenario_id == scenario_id for state in self._sessions.values()
            )
