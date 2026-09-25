from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, func, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session, select

from app.admin_duty.domain.definition import IncidentDefinition
from app.admin_duty.domain.persistence import (
    SESSION_SNAPSHOT_SCHEMA_VERSION,
    CorruptSessionSnapshotError,
    UnsupportedSessionSnapshotVersionError,
    deserialize_session_snapshot,
    serialize_session_snapshot,
)
from app.admin_duty.domain.runtime import SessionRuntimeState, SessionStatus
from app.admin_duty.repositories.aggregate import StoredIncidentSession
from app.admin_duty.repositories.memory import MAX_ACTIVE_SESSIONS, SESSION_TTL
from app.admin_duty.repositories.protocols import (
    RepositoryUnavailableError,
    SessionConflictError,
    SessionLimitError,
    SessionNotFoundError,
)
from app.models import DynamicIncidentSession


def utc_now() -> datetime:
    return datetime.now(UTC)


def _resolve_now(now: datetime | None) -> datetime:
    current_time = now if now is not None else utc_now()
    if current_time.tzinfo is None or current_time.utcoffset() is None:
        raise ValueError("Czas repository musi zawierać strefę czasową.")
    return current_time.astimezone(UTC)


def _database_time(value: datetime) -> datetime:
    return value.astimezone(UTC).replace(tzinfo=None)


def _aware_database_time(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC)


class SQLIncidentSessionRepository:
    def __init__(
        self,
        engine,
        *,
        ttl: timedelta = SESSION_TTL,
        max_sessions: int = MAX_ACTIVE_SESSIONS,
    ) -> None:
        if ttl <= timedelta(0):
            raise ValueError("TTL sesji musi być dodatni.")
        if max_sessions < 1:
            raise ValueError("Limit sesji musi być dodatni.")
        self._engine = engine
        self._ttl = ttl
        self._max_sessions = max_sessions

    @property
    def ttl(self) -> timedelta:
        return self._ttl

    @property
    def max_sessions(self) -> int:
        return self._max_sessions

    def _expires_at(self, state: SessionRuntimeState) -> datetime:
        return state.last_activity + self._ttl

    def _delete_expired(self, session: Session, current_time: datetime):
        expired_ids = tuple(
            session.exec(
                select(DynamicIncidentSession.session_id).where(
                    DynamicIncidentSession.expires_at
                    <= _database_time(current_time)
                )
            ).all()
        )
        if expired_ids:
            session.exec(
                delete(DynamicIncidentSession).where(
                    DynamicIncidentSession.session_id.in_(expired_ids)
                )
            )
        return expired_ids

    def _validate_record(
        self,
        record: DynamicIncidentSession,
    ) -> StoredIncidentSession:
        if record.schema_version != SESSION_SNAPSHOT_SCHEMA_VERSION:
            raise UnsupportedSessionSnapshotVersionError(
                "Wersja rekordu sesji nie jest obsługiwana."
            )
        snapshot = deserialize_session_snapshot(record.snapshot_json)
        definition = snapshot.incident_definition
        state = snapshot.runtime_state

        if str(state.session_id) != record.session_id:
            raise CorruptSessionSnapshotError(
                "Session ID rekordu nie odpowiada snapshotowi."
            )
        if str(definition.scenario_id) != record.scenario_id:
            raise CorruptSessionSnapshotError(
                "Scenario ID rekordu nie odpowiada snapshotowi."
            )
        if state.revision != record.revision:
            raise CorruptSessionSnapshotError(
                "Revision rekordu nie odpowiada snapshotowi."
            )
        if state.status.value != record.status:
            raise CorruptSessionSnapshotError(
                "Status rekordu nie odpowiada snapshotowi."
            )
        if _aware_database_time(record.created_at) != state.created_at.astimezone(UTC):
            raise CorruptSessionSnapshotError(
                "Czas utworzenia rekordu nie odpowiada snapshotowi."
            )
        if _aware_database_time(record.updated_at) != state.last_activity.astimezone(UTC):
            raise CorruptSessionSnapshotError(
                "Czas aktualizacji rekordu nie odpowiada snapshotowi."
            )
        if _aware_database_time(record.expires_at) != self._expires_at(state):
            raise CorruptSessionSnapshotError(
                "Czas wygaśnięcia rekordu nie odpowiada snapshotowi."
            )
        return StoredIncidentSession(definition=definition, state=state)

    def create(
        self,
        definition: IncidentDefinition,
        state: SessionRuntimeState,
        *,
        now: datetime | None = None,
    ) -> None:
        current_time = _resolve_now(now)
        snapshot_json = serialize_session_snapshot(definition, state)
        record = DynamicIncidentSession(
            session_id=str(state.session_id),
            scenario_id=str(definition.scenario_id),
            status=state.status.value,
            revision=state.revision,
            schema_version=SESSION_SNAPSHOT_SCHEMA_VERSION,
            snapshot_json=snapshot_json,
            created_at=_database_time(state.created_at),
            updated_at=_database_time(state.last_activity),
            completed_at=None,
            expires_at=_database_time(self._expires_at(state)),
        )
        try:
            with Session(self._engine) as session:
                self._delete_expired(session, current_time)
                count = session.exec(
                    select(func.count()).select_from(DynamicIncidentSession)
                ).one()
                if count >= self._max_sessions:
                    session.rollback()
                    raise SessionLimitError(
                        "Limit aktywnych sesji został osiągnięty."
                    )
                session.add(record)
                session.commit()
        except SessionLimitError:
            raise
        except IntegrityError as error:
            raise SessionConflictError("Sesja już istnieje.") from error
        except SQLAlchemyError as error:
            raise RepositoryUnavailableError(
                "Nie udało się zapisać sesji."
            ) from error

    def get(
        self,
        session_id: UUID,
        *,
        now: datetime | None = None,
    ) -> StoredIncidentSession:
        current_time = _resolve_now(now)
        try:
            with Session(self._engine) as session:
                record = session.get(DynamicIncidentSession, str(session_id))
                if record is None:
                    raise SessionNotFoundError("Sesja nie istnieje.")
                if record.expires_at <= _database_time(current_time):
                    session.delete(record)
                    session.commit()
                    raise SessionNotFoundError("Sesja nie istnieje.")
                return self._validate_record(record)
        except SessionNotFoundError:
            raise
        except SQLAlchemyError as error:
            raise RepositoryUnavailableError(
                "Nie udało się odczytać sesji."
            ) from error

    def update(
        self,
        definition: IncidentDefinition,
        state: SessionRuntimeState,
        *,
        expected_revision: int,
        now: datetime | None = None,
    ) -> None:
        current_time = _resolve_now(now)
        snapshot_json = serialize_session_snapshot(definition, state)
        try:
            with Session(self._engine) as session:
                existing = session.get(DynamicIncidentSession, str(state.session_id))
                if existing is None or existing.expires_at <= _database_time(current_time):
                    if existing is not None:
                        session.delete(existing)
                        session.commit()
                    raise SessionNotFoundError("Sesja nie istnieje.")
                if existing.scenario_id != str(definition.scenario_id):
                    raise SessionConflictError(
                        "Nie można zmienić scenario_id istniejącej sesji."
                    )
                stored = self._validate_record(existing)
                if stored.definition != definition:
                    raise SessionConflictError(
                        "Nie można zmienić definicji istniejącej sesji."
                    )
                if state.revision <= expected_revision:
                    raise SessionConflictError(
                        "Aktualizacja sesji wymaga nowszej revision."
                    )

                completed_at = existing.completed_at
                if completed_at is None and state.status is SessionStatus.COMPLETED:
                    completed_at = _database_time(state.last_activity)

                result = session.exec(
                    update(DynamicIncidentSession)
                    .where(
                        DynamicIncidentSession.session_id == str(state.session_id),
                        DynamicIncidentSession.revision == expected_revision,
                    )
                    .values(
                        status=state.status.value,
                        revision=state.revision,
                        schema_version=SESSION_SNAPSHOT_SCHEMA_VERSION,
                        snapshot_json=snapshot_json,
                        updated_at=_database_time(state.last_activity),
                        completed_at=completed_at,
                        expires_at=_database_time(self._expires_at(state)),
                    )
                )
                if result.rowcount != 1:
                    session.rollback()
                    raise SessionConflictError(
                        "Sesja została równocześnie zmodyfikowana."
                    )
                session.commit()
        except (SessionConflictError, SessionNotFoundError):
            raise
        except SQLAlchemyError as error:
            raise RepositoryUnavailableError(
                "Nie udało się zaktualizować sesji."
            ) from error

    def cleanup_expired(
        self,
        *,
        now: datetime | None = None,
    ) -> tuple[UUID, ...]:
        current_time = _resolve_now(now)
        try:
            with Session(self._engine) as session:
                expired_ids = self._delete_expired(session, current_time)
                if expired_ids:
                    session.commit()
                return tuple(UUID(value) for value in expired_ids)
        except SQLAlchemyError as error:
            raise RepositoryUnavailableError(
                "Nie udało się usunąć wygasłych sesji."
            ) from error
