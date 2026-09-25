import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from app.admin_duty.domain.definition import IncidentDefinition
from app.admin_duty.domain.progress import get_session_progress
from app.admin_duty.domain.runtime import SessionRuntimeState, SessionStatus

SESSION_SNAPSHOT_SCHEMA_VERSION = 1


class SessionSnapshotError(ValueError):
    pass


class UnsupportedSessionSnapshotVersionError(SessionSnapshotError):
    pass


class CorruptSessionSnapshotError(SessionSnapshotError):
    pass


class DynamicIncidentSnapshotV1(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = SESSION_SNAPSHOT_SCHEMA_VERSION
    incident_definition: IncidentDefinition
    runtime_state: SessionRuntimeState

    @model_validator(mode="after")
    def validate_aggregate(self):
        if self.incident_definition.scenario_id != self.runtime_state.scenario_id:
            raise ValueError("Definicja i runtime mają różne scenario_id.")

        progress = get_session_progress(
            self.incident_definition,
            self.runtime_state,
        )
        if (
            self.runtime_state.status is SessionStatus.ACTIVE
            and progress.mission_complete
        ):
            raise ValueError("Aktywna sesja nie może mieć ukończonej misji.")
        if (
            self.runtime_state.status is SessionStatus.COMPLETED
            and not progress.mission_complete
        ):
            raise ValueError("Ukończona sesja musi mieć ukończoną misję.")
        return self


def serialize_session_snapshot(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> str:
    try:
        snapshot = DynamicIncidentSnapshotV1.model_validate(
            {
                "schema_version": SESSION_SNAPSHOT_SCHEMA_VERSION,
                "incident_definition": definition.model_dump(
                    mode="python",
                    round_trip=True,
                ),
                "runtime_state": state.model_dump(
                    mode="python",
                    round_trip=True,
                ),
            }
        )
    except ValidationError as error:
        raise CorruptSessionSnapshotError(
            "Stan sesji nie przeszedł walidacji przed zapisem."
        ) from error
    return snapshot.model_dump_json()


def deserialize_session_snapshot(payload: str) -> DynamicIncidentSnapshotV1:
    try:
        decoded = json.loads(payload)
    except (json.JSONDecodeError, TypeError) as error:
        raise CorruptSessionSnapshotError(
            "Snapshot sesji nie jest poprawnym JSON-em."
        ) from error

    if not isinstance(decoded, dict):
        raise CorruptSessionSnapshotError("Snapshot sesji nie jest obiektem JSON.")
    if "schema_version" not in decoded:
        raise CorruptSessionSnapshotError("Snapshot sesji nie ma schema_version.")
    if decoded["schema_version"] != SESSION_SNAPSHOT_SCHEMA_VERSION:
        raise UnsupportedSessionSnapshotVersionError(
            "Wersja snapshotu sesji nie jest obsługiwana."
        )

    try:
        return DynamicIncidentSnapshotV1.model_validate(decoded)
    except ValidationError as error:
        raise CorruptSessionSnapshotError(
            "Snapshot sesji nie przeszedł walidacji."
        ) from error
