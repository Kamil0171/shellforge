from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.admin_duty.domain.definition import IncidentDefinition
from app.admin_duty.domain.runtime import SessionRuntimeState


class RepositoryError(ValueError):
    pass


class ScenarioNotFoundError(RepositoryError):
    pass


class ScenarioConflictError(RepositoryError):
    pass


class SessionNotFoundError(RepositoryError):
    pass


class SessionConflictError(RepositoryError):
    pass


class SessionLimitError(RepositoryError):
    pass


class ScenarioRepository(Protocol):
    def save(self, definition: IncidentDefinition) -> None: ...

    def get(self, scenario_id: UUID) -> IncidentDefinition: ...

    def exists(self, scenario_id: UUID) -> bool: ...

    def delete(self, scenario_id: UUID) -> bool: ...


class SessionRepository(Protocol):
    def save(
        self,
        state: SessionRuntimeState,
        *,
        now: datetime | None = None,
    ) -> None: ...

    def get(
        self,
        session_id: UUID,
        *,
        now: datetime | None = None,
    ) -> SessionRuntimeState: ...

    def update(
        self,
        state: SessionRuntimeState,
        *,
        expected_revision: int,
        now: datetime | None = None,
    ) -> None: ...

    def delete(
        self,
        session_id: UUID,
        *,
        now: datetime | None = None,
    ) -> SessionRuntimeState: ...

    def cleanup_expired(
        self,
        *,
        now: datetime | None = None,
    ) -> tuple[SessionRuntimeState, ...]: ...

    def has_scenario(
        self,
        scenario_id: UUID,
        *,
        now: datetime | None = None,
    ) -> bool: ...
