import posixpath
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.admin_duty.domain.definition import (
    Identifier,
    IncidentDefinition,
    JsonValue,
    ResourceType,
    WorldResource,
)


class MutableDomainModel(BaseModel):
    model_config = ConfigDict(
        allow_inf_nan=False,
        extra="forbid",
        validate_assignment=True,
    )


class SessionStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ENDED = "ended"


class InactiveSessionError(ValueError):
    pass


class RuntimeResource(MutableDomainModel):
    resource_id: Identifier
    resource_type: ResourceType
    current_state: Identifier
    parent_resource_id: Identifier | None = None
    dependencies: list[Identifier] = Field(default_factory=list, max_length=32)
    attributes: dict[Identifier, JsonValue] = Field(
        default_factory=dict,
        max_length=64,
    )


class RuntimeWorldState(MutableDomainModel):
    resources: dict[Identifier, RuntimeResource] = Field(
        default_factory=dict,
        max_length=1024,
    )

    @model_validator(mode="after")
    def validate_resource_keys(self):
        if any(
            resource_id != resource.resource_id
            for resource_id, resource in self.resources.items()
        ):
            raise ValueError("Klucz zasobu runtime musi odpowiadać jego resource_id.")

        return self


class VirtualFileEntry(MutableDomainModel):
    path: str = Field(min_length=1, max_length=1024)
    kind: Literal["directory", "file"]
    content: str = Field(default="", max_length=32768)
    mode: str = Field(min_length=3, max_length=10)
    owner: str = Field(min_length=1, max_length=64)
    group: str = Field(min_length=1, max_length=64)

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("Ścieżka wirtualnego filesystemu musi być bezwzględna.")
        return "/" + posixpath.normpath(value).lstrip("/")


class VirtualRockyRuntime(MutableDomainModel):
    hostname: str = Field(default="incident-host", min_length=1, max_length=253)
    user: str = Field(default="operator", min_length=1, max_length=64)
    home_directory: str = Field(default="/home/operator", min_length=1, max_length=1024)
    filesystem: dict[str, VirtualFileEntry] = Field(default_factory=dict, max_length=2048)

    @model_validator(mode="after")
    def validate_filesystem_keys(self):
        if any(path != entry.path for path, entry in self.filesystem.items()):
            raise ValueError("Klucz filesystemu musi odpowiadać ścieżce wpisu.")
        return self


class SessionRuntimeState(MutableDomainModel):
    scenario_id: UUID
    session_id: UUID
    created_at: AwareDatetime
    last_activity: AwareDatetime
    status: SessionStatus
    current_working_directory: str = Field(min_length=1, max_length=1024)
    virtual_rocky: VirtualRockyRuntime = Field(default_factory=VirtualRockyRuntime)
    world_state: RuntimeWorldState
    score: int = Field(ge=0, le=1_000_000)
    commands_used: int = Field(default=0, ge=0)
    hints_used: int = Field(default=0, ge=0)
    solution_viewed: bool = False
    completed_objective_ids: set[Identifier] = Field(default_factory=set)
    discovered_fact_ids: set[Identifier] = Field(default_factory=set)
    revision: int = Field(default=0, ge=0)

    @field_validator("current_working_directory")
    @classmethod
    def validate_current_working_directory(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("Katalog roboczy musi być bezwzględną ścieżką POSIX.")

        return "/" + posixpath.normpath(value).lstrip("/")

    @model_validator(mode="after")
    def validate_timestamps(self):
        if self.last_activity < self.created_at:
            raise ValueError(
                "Ostatnia aktywność nie może być wcześniejsza niż utworzenie sesji."
            )

        return self


def utc_now() -> datetime:
    return datetime.now(UTC)


def create_runtime_resource(resource: WorldResource) -> RuntimeResource:
    return RuntimeResource(
        resource_id=resource.resource_id,
        resource_type=resource.resource_type,
        current_state=resource.state,
        parent_resource_id=resource.parent_id,
        dependencies=list(resource.dependencies),
        attributes={
            attribute.key: attribute.value for attribute in resource.attributes
        },
    )


def _virtual_directory(path: str, mode: str = "0755", owner: str = "root") -> VirtualFileEntry:
    return VirtualFileEntry(
        path=path,
        kind="directory",
        mode=mode,
        owner=owner,
        group=owner,
    )


def _virtual_file(
    path: str,
    content: str,
    *,
    mode: str = "0644",
    owner: str = "root",
    group: str | None = None,
) -> VirtualFileEntry:
    return VirtualFileEntry(
        path=path,
        kind="file",
        content=content,
        mode=mode,
        owner=owner,
        group=group or owner,
    )


def create_virtual_rocky_runtime(definition: IncidentDefinition) -> VirtualRockyRuntime:
    resources = definition.initial_world_state.resources
    service = next(
        resource for resource in resources if resource.resource_type is ResourceType.SERVICE
    )
    attributes = {field.key: field.value for field in service.attributes}
    host = next(
        resource
        for resource in resources
        if resource.resource_id == service.parent_id
    )
    host_attributes = {field.key: field.value for field in host.attributes}
    hostname = str(host_attributes.get("hostname", "incident-host"))
    service_name = str(attributes.get("service_name", f"{service.resource_id}.service"))
    app_name = service_name.removesuffix(".service")
    configured_exec_target = str(attributes.get("configured_exec_start", app_name))
    expected_exec_target = str(
        attributes.get("expected_exec_start", configured_exec_target)
    )
    executable = next(
        (
            resource
            for resource in resources
            if resource.resource_id == attributes.get("executable_resource_id")
        ),
        None,
    )
    executable_attributes = (
        {field.key: field.value for field in executable.attributes}
        if executable is not None
        else {}
    )
    app_directory = f"/opt/{app_name}"
    service_path = f"/etc/systemd/system/{service_name}"
    log_path = f"/var/log/{app_name}.log"
    unit_content = (
        "[Unit]\n"
        f"Description=ShellForge incident service {app_name}\n"
        "After=network-online.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        f"ExecStart={app_directory}/{configured_exec_target}\n"
        "User=app\n"
        "Restart=on-failure\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n"
    )
    entries = (
        _virtual_directory("/"),
        _virtual_directory("/etc"),
        _virtual_directory("/etc/systemd"),
        _virtual_directory("/etc/systemd/system"),
        _virtual_directory("/var"),
        _virtual_directory("/var/log", mode="0750"),
        _virtual_directory("/home"),
        _virtual_directory("/home/operator", owner="operator"),
        _virtual_file("/home/operator/README.txt", "Środowisko szkoleniowe ShellForge.\n", owner="operator"),
        _virtual_directory("/opt"),
        _virtual_directory(app_directory, mode="0755", owner="app"),
        _virtual_file(
            f"{app_directory}/{expected_exec_target}",
            "ELF virtual executable\n",
            mode=str(executable_attributes.get("current_mode", "0755")),
            owner=str(executable_attributes.get("owner", "app")),
        ),
        _virtual_directory("/srv"),
        _virtual_directory(f"/srv/{app_name}", owner="app"),
        _virtual_directory("/tmp", mode="1777"),
        _virtual_directory("/root", mode="0700"),
        _virtual_file(service_path, unit_content),
        _virtual_file(log_path, f"{app_name}: oczekiwanie na diagnostykę operatora\n", mode="0640", owner="app", group="app"),
        _virtual_file(
            "/etc/os-release",
            'NAME="Rocky Linux"\nVERSION="9.6 (Blue Onyx)"\nID="rocky"\nVERSION_ID="9.6"\n',
        ),
    )
    return VirtualRockyRuntime(
        hostname=hostname,
        filesystem={entry.path: entry for entry in entries},
    )


def create_session_runtime(
    definition: IncidentDefinition,
    *,
    session_id: UUID | None = None,
    now: datetime | None = None,
    current_working_directory: str = "/home/operator",
) -> SessionRuntimeState:
    current_time = now if now is not None else utc_now()
    runtime_resources = {
        resource.resource_id: create_runtime_resource(resource)
        for resource in definition.initial_world_state.resources
    }

    return SessionRuntimeState(
        scenario_id=definition.scenario_id,
        session_id=session_id if session_id is not None else uuid4(),
        created_at=current_time,
        last_activity=current_time,
        status=SessionStatus.ACTIVE,
        current_working_directory=current_working_directory,
        virtual_rocky=create_virtual_rocky_runtime(definition),
        world_state=RuntimeWorldState(resources=runtime_resources),
        score=definition.scoring.initial_score,
    )


def _require_active_session(state: SessionRuntimeState) -> None:
    if state.status is not SessionStatus.ACTIVE:
        raise InactiveSessionError(
            "Operacja jest dostępna wyłącznie dla aktywnej sesji."
        )


def _validate_penalty(penalty: int) -> None:
    if penalty < 0:
        raise ValueError("Kara punktowa nie może być ujemna.")


def _resolve_operation_time(
    state: SessionRuntimeState,
    now: datetime | None,
) -> datetime:
    current_time = now if now is not None else utc_now()

    if current_time.tzinfo is None or current_time.utcoffset() is None:
        raise ValueError("Czas operacji musi zawierać strefę czasową.")

    if current_time < state.created_at or current_time < state.last_activity:
        raise ValueError("Czas operacji nie może cofać aktywności sesji.")

    return current_time


def _apply_runtime_mutation(
    state: SessionRuntimeState,
    *,
    current_time: datetime,
    score_penalty: int = 0,
    commands_delta: int = 0,
    hints_delta: int = 0,
    solution_viewed: bool = False,
) -> None:
    if score_penalty:
        state.score = max(0, state.score - score_penalty)

    if commands_delta:
        state.commands_used += commands_delta

    if hints_delta:
        state.hints_used += hints_delta

    if solution_viewed:
        state.solution_viewed = True

    state.last_activity = current_time
    state.revision += 1


def touch_session(
    state: SessionRuntimeState,
    *,
    now: datetime | None = None,
) -> None:
    _require_active_session(state)
    current_time = _resolve_operation_time(state, now)
    _apply_runtime_mutation(state, current_time=current_time)


def apply_score_penalty(
    state: SessionRuntimeState,
    penalty: int,
    *,
    now: datetime | None = None,
) -> None:
    _require_active_session(state)
    _validate_penalty(penalty)
    current_time = _resolve_operation_time(state, now)
    _apply_runtime_mutation(
        state,
        current_time=current_time,
        score_penalty=penalty,
    )


def register_command(
    state: SessionRuntimeState,
    *,
    cost: int = 0,
    now: datetime | None = None,
) -> None:
    _require_active_session(state)
    _validate_penalty(cost)
    current_time = _resolve_operation_time(state, now)
    _apply_runtime_mutation(
        state,
        current_time=current_time,
        score_penalty=cost,
        commands_delta=1,
    )


def register_hint(
    state: SessionRuntimeState,
    *,
    penalty: int = 0,
    now: datetime | None = None,
) -> None:
    _require_active_session(state)
    _validate_penalty(penalty)
    current_time = _resolve_operation_time(state, now)
    _apply_runtime_mutation(
        state,
        current_time=current_time,
        score_penalty=penalty,
        hints_delta=1,
    )


def mark_solution_viewed(
    state: SessionRuntimeState,
    *,
    penalty: int = 0,
    now: datetime | None = None,
) -> None:
    _require_active_session(state)

    if state.solution_viewed:
        return

    _validate_penalty(penalty)
    current_time = _resolve_operation_time(state, now)
    _apply_runtime_mutation(
        state,
        current_time=current_time,
        score_penalty=penalty,
        solution_viewed=True,
    )


def end_session_runtime(
    state: SessionRuntimeState,
    *,
    now: datetime | None = None,
) -> None:
    if state.status is SessionStatus.ENDED:
        raise InactiveSessionError("Sesja została już zakończona.")

    current_time = _resolve_operation_time(state, now)
    state.status = SessionStatus.ENDED
    state.last_activity = current_time
    state.revision += 1
