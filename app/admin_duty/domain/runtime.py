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
    mode: str = Field(pattern=r"^[0-7]{3,4}$")
    owner: str = Field(min_length=1, max_length=64)
    group: str = Field(min_length=1, max_length=64)

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("Ścieżka wirtualnego filesystemu musi być bezwzględna.")
        return "/" + posixpath.normpath(value).lstrip("/")


class VirtualProcess(MutableDomainModel):
    pid: int = Field(ge=1, le=999_999)
    user: str = Field(min_length=1, max_length=64)
    command: str = Field(min_length=1, max_length=1024)
    service_resource_id: Identifier | None = None


class VirtualPackage(MutableDomainModel):
    name: Identifier
    version: str = Field(min_length=1, max_length=128)
    repository: Identifier
    summary: str = Field(min_length=1, max_length=240)


class PackageManagerState(MutableDomainModel):
    installed_packages: dict[Identifier, VirtualPackage] = Field(default_factory=dict)
    available_packages: dict[Identifier, VirtualPackage] = Field(default_factory=dict)
    repositories: tuple[Identifier, ...] = ("baseos", "appstream", "extras")
    enabled_repositories: set[Identifier] = Field(
        default_factory=lambda: {"baseos", "appstream", "extras"}
    )
    cache_clean: bool = False


class VirtualNetworkInterface(MutableDomainModel):
    name: Identifier
    address: str = Field(min_length=1, max_length=128)
    state: Literal["up", "down"]
    connection: Identifier


class VirtualNetworkState(MutableDomainModel):
    interfaces: dict[Identifier, VirtualNetworkInterface] = Field(default_factory=dict)
    routes: list[str] = Field(default_factory=list, max_length=64)
    dns_records: dict[str, str] = Field(default_factory=dict, max_length=128)
    connections: dict[Identifier, bool] = Field(default_factory=dict, max_length=64)
    connection_dns_servers: dict[Identifier, tuple[str, ...]] = Field(
        default_factory=dict, max_length=64
    )
    expected_dns_servers: dict[Identifier, tuple[str, ...]] = Field(
        default_factory=dict, max_length=64
    )


class VirtualSelinuxState(MutableDomainModel):
    mode: Literal["Enforcing", "Permissive", "Disabled"] = "Enforcing"
    file_contexts: dict[str, str] = Field(default_factory=dict, max_length=512)
    expected_file_contexts: dict[str, str] = Field(default_factory=dict, max_length=512)


class VirtualFirewallState(MutableDomainModel):
    running: bool = True
    active_zone: Identifier = "public"
    runtime_services: set[Identifier] = Field(default_factory=lambda: {"ssh"})
    permanent_services: set[Identifier] = Field(default_factory=lambda: {"ssh"})
    runtime_ports: set[str] = Field(default_factory=set)
    permanent_ports: set[str] = Field(default_factory=set)


class VirtualRockyRuntime(MutableDomainModel):
    host_resource_id: Identifier = "host-primary"
    hostname: str = Field(default="incident-host", min_length=1, max_length=253)
    user: str = Field(default="operator", min_length=1, max_length=64)
    home_directory: str = Field(default="/home/operator", min_length=1, max_length=1024)
    filesystem: dict[str, VirtualFileEntry] = Field(
        default_factory=dict, max_length=2048
    )
    processes: dict[int, VirtualProcess] = Field(default_factory=dict, max_length=1024)
    packages: PackageManagerState = Field(default_factory=PackageManagerState)
    network: VirtualNetworkState = Field(default_factory=VirtualNetworkState)
    selinux: VirtualSelinuxState = Field(default_factory=VirtualSelinuxState)
    firewall: VirtualFirewallState = Field(default_factory=VirtualFirewallState)
    journal_entries: list[str] = Field(default_factory=list, max_length=2048)
    systemd_unit_cache: dict[str, str] = Field(default_factory=dict, max_length=256)
    systemd_enabled_units: set[str] = Field(default_factory=set, max_length=256)
    daemon_reload_required: bool = False
    memory_total_kib: int = Field(default=8_000_000, ge=1)
    memory_used_kib: int = Field(default=2_000_000, ge=0)
    disk_total_kib: int = Field(default=40_000_000, ge=1)
    disk_used_kib: int = Field(default=13_000_000, ge=0)
    uptime_seconds: int = Field(default=1234567, ge=0)

    @model_validator(mode="after")
    def validate_filesystem_keys(self):
        if any(path != entry.path for path, entry in self.filesystem.items()):
            raise ValueError("Klucz filesystemu musi odpowiadać ścieżce wpisu.")
        return self


class CommandRecord(MutableDomainModel):
    order: int = Field(ge=1)
    command: str = Field(min_length=1, max_length=1024)
    capability_id: Identifier
    host_id: Identifier
    success: bool
    occurred_at: AwareDatetime


class SessionRuntimeState(MutableDomainModel):
    scenario_id: UUID
    session_id: UUID
    created_at: AwareDatetime
    last_activity: AwareDatetime
    status: SessionStatus
    current_working_directory: str = Field(min_length=1, max_length=1024)
    active_host_id: Identifier
    host_runtimes: dict[Identifier, VirtualRockyRuntime] = Field(
        default_factory=dict, min_length=1, max_length=16
    )
    host_working_directories: dict[Identifier, str] = Field(
        default_factory=dict, max_length=16
    )
    world_state: RuntimeWorldState
    score: int = Field(ge=0, le=1_000_000)
    commands_used: int = Field(default=0, ge=0)
    hints_used: int = Field(default=0, ge=0)
    solution_viewed: bool = False
    completed_objective_ids: set[Identifier] = Field(default_factory=set)
    discovered_fact_ids: set[Identifier] = Field(default_factory=set)
    command_history: list[CommandRecord] = Field(default_factory=list, max_length=512)
    revision: int = Field(default=0, ge=0)

    @property
    def virtual_rocky(self) -> VirtualRockyRuntime:
        return self.host_runtimes[self.active_host_id]

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

        if self.active_host_id not in self.host_runtimes:
            raise ValueError("Aktywny host nie ma runtime Virtual Rocky.")
        if any(
            host_id != runtime.host_resource_id
            for host_id, runtime in self.host_runtimes.items()
        ):
            raise ValueError("Klucz runtime hosta musi odpowiadać host_resource_id.")
        if any(host_id not in self.host_runtimes for host_id in self.host_working_directories):
            raise ValueError("Katalog roboczy wskazuje nieznany host.")
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


def _virtual_directory(
    path: str, mode: str = "0755", owner: str = "root"
) -> VirtualFileEntry:
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


def _field_map(fields) -> dict[str, JsonValue]:
    return {field.key: field.value for field in fields}


def _string_tuple(value: JsonValue, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    if isinstance(value, tuple) and all(isinstance(item, str) for item in value):
        return value
    return default


def _package_catalog() -> dict[Identifier, VirtualPackage]:
    packages = (
        VirtualPackage(
            name="bash",
            version="5.1.8-9.el9",
            repository="baseos",
            summary="Powłoka GNU Bourne Again",
        ),
        VirtualPackage(
            name="systemd",
            version="252-51.el9",
            repository="baseos",
            summary="Menedżer systemu i usług",
        ),
        VirtualPackage(
            name="rocky-release",
            version="9.6-1.2.el9",
            repository="baseos",
            summary="Pliki wydania Rocky Linux",
        ),
        VirtualPackage(
            name="nginx",
            version="1.20.1-22.el9",
            repository="appstream",
            summary="Serwer HTTP i reverse proxy",
        ),
        VirtualPackage(
            name="bind-utils",
            version="9.16.23-31.el9",
            repository="appstream",
            summary="Narzędzia diagnostyczne DNS",
        ),
        VirtualPackage(
            name="policycoreutils-python-utils",
            version="3.6-2.1.el9",
            repository="baseos",
            summary="Narzędzia zarządzania SELinux",
        ),
        VirtualPackage(
            name="python3-psycopg2",
            version="2.9.6-1.el9",
            repository="appstream",
            summary="Sterownik PostgreSQL dla Pythona",
        ),
    )
    return {package.name: package for package in packages}


def _service_unit(service, attributes: dict[str, JsonValue]) -> tuple[str, str, str]:
    service_name = str(
        attributes.get("service_name", f"{service.resource_id}.service")
    )
    app_name = service_name.removesuffix(".service")
    app_directory = str(attributes.get("app_directory", f"/opt/{app_name}"))
    configured_exec_target = str(attributes.get("configured_exec_start", app_name))
    environment_variable = attributes.get("required_environment_variable")
    environment_value = attributes.get(
        f"environment.{environment_variable}"
        if isinstance(environment_variable, str)
        else ""
    )
    environment_line = (
        f'Environment="{environment_variable}={environment_value}"\n'
        if isinstance(environment_variable, str) and isinstance(environment_value, str)
        else ""
    )
    unit_content = (
        "[Unit]\n"
        f"Description=ShellForge incident service {app_name}\n"
        "After=network-online.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        f"ExecStart={app_directory}/{configured_exec_target}\n"
        f"{environment_line}"
        "User=app\n"
        "Restart=on-failure\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n"
    )
    return service_name, app_directory, unit_content


def _base_filesystem(hostname: str) -> dict[str, VirtualFileEntry]:
    entries = (
        _virtual_directory("/"),
        _virtual_directory("/etc"),
        _virtual_directory("/etc/systemd"),
        _virtual_directory("/etc/systemd/system"),
        _virtual_directory("/etc/NetworkManager"),
        _virtual_directory("/etc/NetworkManager/system-connections", mode="0700"),
        _virtual_directory("/var"),
        _virtual_directory("/var/log", mode="0750"),
        _virtual_directory("/home"),
        _virtual_directory("/home/operator", owner="operator"),
        _virtual_file(
            "/home/operator/README.txt",
            f"Środowisko szkoleniowe ShellForge. Host: {hostname}.\n",
            owner="operator",
        ),
        _virtual_directory("/opt"),
        _virtual_directory("/srv"),
        _virtual_directory("/tmp", mode="1777"),
        _virtual_directory("/root", mode="0700"),
        _virtual_file(
            "/etc/os-release",
            'NAME="Rocky Linux"\nVERSION="9.6 (Blue Onyx)"\nID="rocky"\nVERSION_ID="9.6"\n',
        ),
    )
    return {entry.path: entry for entry in entries}


def _create_host_runtime(
    definition: IncidentDefinition,
    host,
    *,
    host_index: int,
    dns_records: dict[str, str],
) -> VirtualRockyRuntime:
    resources = definition.initial_world_state.resources
    host_attributes = _field_map(host.attributes)
    hostname = str(host_attributes.get("hostname", host.resource_id))
    address = str(host_attributes.get("address", f"10.24.8.{17 + host_index}/24"))
    plain_address = address.split("/")[0]
    filesystem = _base_filesystem(hostname)
    unit_cache: dict[str, str] = {}
    enabled_units: set[str] = set()
    file_contexts: dict[str, str] = {}
    expected_file_contexts: dict[str, str] = {}

    services = [
        resource
        for resource in resources
        if resource.resource_type is ResourceType.SERVICE
        and resource.parent_id == host.resource_id
    ]
    resource_by_id = {resource.resource_id: resource for resource in resources}
    for service in services:
        attributes = _field_map(service.attributes)
        service_name, app_directory, unit_content = _service_unit(service, attributes)
        app_name = service_name.removesuffix(".service")
        expected_exec_target = str(
            attributes.get(
                "expected_exec_start",
                attributes.get("configured_exec_start", app_name),
            )
        )
        executable = resource_by_id.get(str(attributes.get("executable_resource_id")))
        executable_attributes = _field_map(executable.attributes) if executable else {}
        executable_path = f"{app_directory}/{expected_exec_target}"
        filesystem.setdefault(
            app_directory,
            _virtual_directory(app_directory, mode="0755", owner="app"),
        )
        filesystem[f"{app_directory}/README.md"] = _virtual_file(
            f"{app_directory}/README.md",
            f"# Dokumentacja wdrożenia {app_name}\n"
            f"Jednostka: {service_name}\n"
            f"Plik wykonywalny: {executable_path}\n"
            "Użytkownik usługi: app. Plik wykonywalny wymaga prawa wykonania.\n"
            + (
                "Wymagane środowisko: "
                f"{attributes['required_environment_variable']}="
                f"{attributes.get('expected_environment_value')}\n"
                if attributes.get("required_environment_variable")
                else ""
            )
            + "Po zmianie jednostki wykonaj systemctl daemon-reload, a następnie restart usługi.\n",
        )
        filesystem[executable_path] = _virtual_file(
            executable_path,
            "ELF virtual executable\n",
            mode=str(executable_attributes.get("current_mode", "0755")),
            owner=str(executable_attributes.get("owner", "app")),
        )
        unit_path = f"/etc/systemd/system/{service_name}"
        filesystem[unit_path] = _virtual_file(unit_path, unit_content)
        filesystem[f"/var/log/{app_name}.log"] = _virtual_file(
            f"/var/log/{app_name}.log",
            f"{app_name}: oczekiwanie na diagnostykę operatora\n",
            mode="0640",
            owner="app",
            group="app",
        )
        unit_cache[service_name] = unit_content
        enabled_units.add(service_name)
        expected_context = str(
            attributes.get("expected_selinux_context", "system_u:object_r:usr_t:s0")
        )
        current_context = str(attributes.get("current_selinux_context", expected_context))
        expected_file_contexts[app_directory] = expected_context
        file_contexts[app_directory] = current_context

    for resource in resources:
        if resource.resource_type is not ResourceType.FILE or resource.parent_id != host.resource_id:
            continue
        attributes = _field_map(resource.attributes)
        path = attributes.get("path")
        if not isinstance(path, str) or path in filesystem:
            continue
        filesystem[path] = _virtual_file(
            path,
            str(attributes.get("content", "")),
            mode=str(attributes.get("current_mode", "0644")),
            owner=str(attributes.get("owner", "root")),
        )

    catalog = _package_catalog()
    installed_names = {
        "bash",
        "systemd",
        "rocky-release",
        *_string_tuple(host_attributes.get("installed_packages")),
    }
    installed = {
        name: catalog[name].model_copy(deep=True)
        for name in installed_names
        if name in catalog
    }
    connection_name = str(host_attributes.get("connection", "System-ens192"))
    dns_servers = _string_tuple(
        host_attributes.get("dns_servers"),
        ("10.24.8.53",),
    )
    expected_dns_servers = _string_tuple(
        host_attributes.get("expected_dns_servers"),
        ("10.24.8.53",),
    )
    connection = VirtualNetworkInterface(
        name="ens192",
        address=address,
        state="up" if host.state in {"running", "healthy"} else "down",
        connection=connection_name,
    )
    return VirtualRockyRuntime(
        host_resource_id=host.resource_id,
        hostname=hostname,
        filesystem=filesystem,
        processes={
            1: VirtualProcess(pid=1, user="root", command="/usr/lib/systemd/systemd"),
            812: VirtualProcess(
                pid=812, user="root", command="sshd: /usr/sbin/sshd -D"
            ),
        },
        packages=PackageManagerState(
            installed_packages=installed,
            available_packages={
                name: package.model_copy(deep=True) for name, package in catalog.items()
            },
        ),
        network=VirtualNetworkState(
            interfaces={connection.name: connection},
            routes=[
                "default via 10.24.8.1 dev ens192 proto static metric 100",
                f"10.24.8.0/24 dev ens192 proto kernel scope link src {plain_address} metric 100",
            ],
            dns_records=dns_records,
            connections={connection.connection: True},
            connection_dns_servers={connection.connection: dns_servers},
            expected_dns_servers={connection.connection: expected_dns_servers},
        ),
        selinux=VirtualSelinuxState(
            file_contexts=file_contexts,
            expected_file_contexts=expected_file_contexts,
        ),
        firewall=VirtualFirewallState(
            running=bool(host_attributes.get("firewall_running", True)),
            runtime_services=set(
                _string_tuple(host_attributes.get("firewall_runtime_services"), ("ssh",))
            ),
            permanent_services=set(
                _string_tuple(host_attributes.get("firewall_permanent_services"), ("ssh",))
            ),
            runtime_ports=set(_string_tuple(host_attributes.get("firewall_runtime_ports"))),
            permanent_ports=set(
                _string_tuple(host_attributes.get("firewall_permanent_ports"))
            ),
        ),
        journal_entries=[f"systemd[1]: Utworzono wirtualną sesję hosta {hostname}."],
        systemd_unit_cache=unit_cache,
        systemd_enabled_units=enabled_units,
    )


def _primary_host_id(definition: IncidentDefinition) -> Identifier:
    terminal_host = next(
        (
            interaction.target_resource_id
            for interaction in definition.initial_world_state.map.interactions
            if interaction.capability_id == "terminal" and interaction.target_resource_id
        ),
        None,
    )
    if terminal_host is not None:
        return terminal_host
    return next(
        resource.resource_id
        for resource in definition.initial_world_state.resources
        if resource.resource_type is ResourceType.HOST
    )


def create_virtual_rocky_hosts(
    definition: IncidentDefinition,
) -> dict[Identifier, VirtualRockyRuntime]:
    hosts = [
        resource
        for resource in definition.initial_world_state.resources
        if resource.resource_type is ResourceType.HOST
    ]
    dns_records = {
        str(_field_map(host.attributes).get("hostname", host.resource_id)): str(
            _field_map(host.attributes).get("address", f"10.24.8.{17 + index}/24")
        ).split("/")[0]
        for index, host in enumerate(hosts)
    }
    dns_records.update(
        {
            "repo.rockylinux.org": "151.101.2.132",
            "example.internal": "10.24.8.40",
        }
    )
    for resource in definition.initial_world_state.resources:
        if resource.resource_type is not ResourceType.DOMAIN:
            continue
        attributes = _field_map(resource.attributes)
        name = attributes.get("name")
        address = attributes.get("address")
        if isinstance(name, str) and isinstance(address, str):
            dns_records[name] = address
    return {
        host.resource_id: _create_host_runtime(
            definition,
            host,
            host_index=index,
            dns_records=dns_records,
        )
        for index, host in enumerate(hosts)
    }


def create_virtual_rocky_runtime(definition: IncidentDefinition) -> VirtualRockyRuntime:
    return create_virtual_rocky_hosts(definition)[_primary_host_id(definition)]


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

    host_runtimes = create_virtual_rocky_hosts(definition)
    primary_host_id = _primary_host_id(definition)
    state = SessionRuntimeState(
        scenario_id=definition.scenario_id,
        session_id=session_id if session_id is not None else uuid4(),
        created_at=current_time,
        last_activity=current_time,
        status=SessionStatus.ACTIVE,
        current_working_directory=current_working_directory,
        active_host_id=primary_host_id,
        host_runtimes=host_runtimes,
        host_working_directories={
            host_id: current_working_directory for host_id in host_runtimes
        },
        world_state=RuntimeWorldState(resources=runtime_resources),
        score=definition.scoring.initial_score,
    )
    from app.admin_duty.rocky.system import service_failure

    for host_id in host_runtimes:
        state.active_host_id = host_id
        for resource in state.world_state.resources.values():
            if (
                resource.resource_type is not ResourceType.SERVICE
                or resource.parent_resource_id != host_id
            ):
                continue
            name = str(
                resource.attributes.get(
                    "service_name", f"{resource.resource_id}.service"
                )
            )
            detail = (
                service_failure(state, resource, synchronize=False)
                if resource.current_state != "running"
                else None
            )
            state.virtual_rocky.journal_entries.append(
                f"{current_time.isoformat()} {state.virtual_rocky.hostname} "
                f"systemd[1]: {name}: "
                + (
                    detail
                    or (
                        "Started"
                        if resource.current_state == "running"
                        else "Main process exited, status=1/FAILURE"
                    )
                )
            )
            if resource.current_state == "running":
                pid = 1421 + len(state.virtual_rocky.processes)
                state.virtual_rocky.processes[pid] = VirtualProcess(
                    pid=pid,
                    user="app",
                    command=name,
                    service_resource_id=resource.resource_id,
                )
    state.active_host_id = primary_host_id
    from app.admin_duty.domain.dependencies import reconcile_dependencies

    reconcile_dependencies(definition, state)
    return state


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
