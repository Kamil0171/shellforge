from datetime import datetime

from pydantic import Field

from app.admin_duty.domain.definition import (
    FrozenDomainModel,
    Identifier,
    IncidentDefinition,
    ResourceType,
)
from app.admin_duty.domain.engine import (
    DynamicIncidentEngine,
    ResourceAttributeUpdate,
    ResourceStateUpdate,
)
from app.admin_duty.domain.progress import SessionProgress
from app.admin_duty.domain.runtime import RuntimeResource, SessionRuntimeState

SYSTEMD_RESTART_CAPABILITY = "systemd.restart"
SYSTEMD_STATUS_CAPABILITY = "systemd.status"
SYSTEMD_MANAGER = "systemd"
RUNNING_STATE = "running"
SERVICE_STATUS_FACT_PREFIX = "service-status-inspected:"
SERVICE_CONFIG_FACT_PREFIX = "service-config-inspected:"
SERVICE_ENV_FACT_PREFIX = "service-environment-inspected:"
FILE_STATUS_FACT_PREFIX = "file-status-inspected:"


class CommandExecutionError(ValueError):
    pass


class CommandExecutionResult(FrozenDomainModel):
    output: str = Field(max_length=1000)
    success: bool
    current_working_directory: str = Field(default="/home/operator", min_length=1, max_length=1024)
    prompt: str = Field(default="operator@incident:~$", min_length=1, max_length=1200)
    progress: SessionProgress


def _get_systemd_service(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    capability_id: Identifier,
) -> RuntimeResource:
    if definition.scenario_id != state.scenario_id:
        raise CommandExecutionError(
            "Definicja incydentu i sesja mają różne scenario_id."
        )

    if capability_id not in definition.capabilities.command_capability_ids:
        raise CommandExecutionError(
            f"Scenariusz nie udostępnia capability {capability_id}."
        )

    resource = state.world_state.resources.get(resource_id)

    if resource is None:
        normalized = resource_id.removesuffix(".service")
        resource = next(
            (
                candidate
                for candidate in state.world_state.resources.values()
                if candidate.resource_type is ResourceType.SERVICE
                and isinstance(candidate.attributes.get("service_name"), str)
                and candidate.attributes["service_name"].removesuffix(".service")
                == normalized
            ),
            None,
        )

    if resource is None:
        raise CommandExecutionError(f"Zasób runtime nie istnieje: {resource_id}.")

    if resource.resource_type is not ResourceType.SERVICE:
        raise CommandExecutionError(f"Zasób {resource_id} nie jest usługą.")

    if resource.attributes.get("manager") != SYSTEMD_MANAGER:
        raise CommandExecutionError(
            f"Usługa {resource_id} nie jest zarządzana przez systemd."
        )

    return resource


def _get_controlled_file(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    capability_id: Identifier,
) -> RuntimeResource:
    if definition.scenario_id != state.scenario_id:
        raise CommandExecutionError(
            "Definicja incydentu i sesja mają różne scenario_id."
        )

    if capability_id not in definition.capabilities.command_capability_ids:
        raise CommandExecutionError(
            f"Scenariusz nie udostępnia capability {capability_id}."
        )

    resource = state.world_state.resources.get(resource_id)

    if resource is None:
        raise CommandExecutionError(f"Zasób runtime nie istnieje: {resource_id}.")

    if resource.resource_type is not ResourceType.FILE:
        raise CommandExecutionError(f"Zasób {resource_id} nie jest plikiem.")

    return resource


def _require_argument_count(
    arguments: tuple[Identifier, ...],
    expected: int,
) -> None:
    if len(arguments) != expected:
        raise CommandExecutionError("Komenda ma nieprawidłową liczbę argumentów.")


def _account_read_only_command(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    fact_id: Identifier,
    engine: DynamicIncidentEngine | None,
    now: datetime | None,
) -> SessionProgress:
    dynamic_engine = engine if engine is not None else DynamicIncidentEngine()
    return dynamic_engine.execute_command(
        definition,
        state,
        action=None,
        command_cost=definition.scoring.command_cost,
        discovered_fact_ids=(fact_id,),
        now=now,
    )


def _restart_prerequisites_met(
    state: SessionRuntimeState,
    service: RuntimeResource,
) -> bool:
    configured = service.attributes.get("configured_exec_start")
    expected = service.attributes.get("expected_exec_start")

    if isinstance(expected, str) and configured != expected:
        return False

    variable = service.attributes.get("required_environment_variable")
    expected_value = service.attributes.get("expected_environment_value")

    if isinstance(variable, str):
        if service.attributes.get(f"environment.{variable}") != expected_value:
            return False

    executable_id = service.attributes.get("executable_resource_id")

    if isinstance(executable_id, str):
        executable = state.world_state.resources.get(executable_id)

        if executable is None:
            return False

        expected_mode = executable.attributes.get("expected_mode")

        if executable.attributes.get("current_mode") != expected_mode:
            return False

    return True


def restart_systemd_service(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    arguments: tuple[Identifier, ...] = (),
    engine: DynamicIncidentEngine | None = None,
    now: datetime | None = None,
) -> CommandExecutionResult:
    resource = _get_systemd_service(
        definition,
        state,
        resource_id=resource_id,
        capability_id=SYSTEMD_RESTART_CAPABILITY,
    )
    _require_argument_count(arguments, 0)
    dynamic_engine = engine if engine is not None else DynamicIncidentEngine()

    if not _restart_prerequisites_met(state, resource):
        progress = dynamic_engine.execute_command(
            definition,
            state,
            action=None,
            command_cost=definition.scoring.command_cost,
            now=now,
        )
        return CommandExecutionResult(
            output=(
                f"Job for {resource.attributes.get('service_name', resource_id)} "
                "failed. See 'systemctl status' and 'journalctl -u' for details."
            ),
            success=False,
            progress=progress,
        )

    progress = dynamic_engine.execute_command(
        definition,
        state,
        ResourceStateUpdate(
            resource_id=resource.resource_id,
            new_state=RUNNING_STATE,
        ),
        command_cost=definition.scoring.command_cost,
        now=now,
    )
    return CommandExecutionResult(
        output="",
        success=True,
        progress=progress,
    )


def get_systemd_service_status(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    arguments: tuple[Identifier, ...] = (),
    engine: DynamicIncidentEngine | None = None,
    now: datetime | None = None,
) -> CommandExecutionResult:
    resource = _get_systemd_service(
        definition,
        state,
        resource_id=resource_id,
        capability_id=SYSTEMD_STATUS_CAPABILITY,
    )
    _require_argument_count(arguments, 0)
    configured_name = resource.attributes.get("service_name")
    display_name = (
        configured_name.strip()
        if isinstance(configured_name, str) and configured_name.strip()
        else resource_id
    )
    active_label = "active (running)" if resource.current_state == "running" else "failed (Result: exit-code)"
    output = (
        f"● {display_name} - Virtual Rocky service\n"
        f"     Loaded: loaded (/etc/systemd/system/{display_name}; enabled; preset: disabled)\n"
        f"     Active: {active_label}\n"
        "       Docs: man:systemd.service(5)"
    )

    if len(output) > 1000:
        raise CommandExecutionError("Nazwa usługi jest zbyt długa.")

    fact_id = f"{SERVICE_STATUS_FACT_PREFIX}{resource_id}"
    progress = _account_read_only_command(
        definition,
        state,
        fact_id=fact_id,
        engine=engine,
        now=now,
    )

    return CommandExecutionResult(
        output=output,
        success=True,
        progress=progress,
    )


def get_systemd_service_configuration(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    arguments: tuple[Identifier, ...] = (),
    engine: DynamicIncidentEngine | None = None,
    now: datetime | None = None,
) -> CommandExecutionResult:
    resource = _get_systemd_service(
        definition,
        state,
        resource_id=resource_id,
        capability_id="systemd.cat",
    )
    _require_argument_count(arguments, 0)
    configured = resource.attributes.get("configured_exec_start", "<brak>")
    service_name = str(resource.attributes.get("service_name", resource_id))
    app_name = service_name.removesuffix(".service")
    output = (
        "[Unit]\n"
        f"Description={app_name} application service\n"
        "After=network-online.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        f"ExecStart=/opt/{app_name}/{configured}\n"
        "User=app\n"
        "Restart=on-failure\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target"
    )
    progress = _account_read_only_command(
        definition,
        state,
        fact_id=f"{SERVICE_CONFIG_FACT_PREFIX}{resource_id}",
        engine=engine,
        now=now,
    )
    return CommandExecutionResult(output=output, success=True, progress=progress)


def set_systemd_exec_start(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    arguments: tuple[Identifier, ...] = (),
    engine: DynamicIncidentEngine | None = None,
    now: datetime | None = None,
) -> CommandExecutionResult:
    resource = _get_systemd_service(
        definition,
        state,
        resource_id=resource_id,
        capability_id="systemd.set-exec-start",
    )
    _require_argument_count(arguments, 1)
    target = arguments[0]
    expected = resource.attributes.get("expected_exec_start")

    if not isinstance(expected, str) or target != expected:
        raise CommandExecutionError(
            f"Cel {target} nie jest dozwolony dla usługi {resource_id}."
        )

    dynamic_engine = engine if engine is not None else DynamicIncidentEngine()
    progress = dynamic_engine.execute_command(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id=resource.resource_id,
            attribute="configured_exec_start",
            value=target,
        ),
        command_cost=definition.scoring.command_cost,
        now=now,
    )
    service_name = str(resource.attributes.get("service_name", resource_id))
    app_name = service_name.removesuffix(".service")
    unit_path = f"/etc/systemd/system/{service_name}"
    unit = state.virtual_rocky.filesystem.get(unit_path)
    if unit is not None:
        trailing_newline = "\n" if unit.content.endswith("\n") else ""
        unit.content = "\n".join(
            f"ExecStart=/opt/{app_name}/{target}"
            if line.startswith("ExecStart=")
            else line
            for line in unit.content.splitlines()
        ) + trailing_newline
    return CommandExecutionResult(
        output=f"Ustawiono kontrolowany cel startowy usługi {resource_id}: {target}.",
        success=True,
        progress=progress,
    )


def get_systemd_environment(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    arguments: tuple[Identifier, ...] = (),
    engine: DynamicIncidentEngine | None = None,
    now: datetime | None = None,
) -> CommandExecutionResult:
    resource = _get_systemd_service(
        definition,
        state,
        resource_id=resource_id,
        capability_id="environment.inspect",
    )
    _require_argument_count(arguments, 0)
    variable = resource.attributes.get("required_environment_variable")

    if not isinstance(variable, str):
        raise CommandExecutionError("Usługa nie definiuje wymaganego środowiska.")

    value = resource.attributes.get(f"environment.{variable}", "<brak>")
    progress = _account_read_only_command(
        definition,
        state,
        fact_id=f"{SERVICE_ENV_FACT_PREFIX}{resource_id}",
        engine=engine,
        now=now,
    )
    return CommandExecutionResult(
        output=f"Wymagane środowisko:\n{variable}={value}",
        success=True,
        progress=progress,
    )


def restore_systemd_environment(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    arguments: tuple[Identifier, ...] = (),
    engine: DynamicIncidentEngine | None = None,
    now: datetime | None = None,
) -> CommandExecutionResult:
    resource = _get_systemd_service(
        definition,
        state,
        resource_id=resource_id,
        capability_id="environment.restore",
    )
    _require_argument_count(arguments, 1)
    variable = arguments[0]
    required_variable = resource.attributes.get("required_environment_variable")
    expected_value = resource.attributes.get("expected_environment_value")

    if variable != required_variable or not isinstance(expected_value, str):
        raise CommandExecutionError(
            f"Zmienna {variable} nie jest dostępna do przywrócenia."
        )

    dynamic_engine = engine if engine is not None else DynamicIncidentEngine()
    progress = dynamic_engine.execute_command(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id=resource.resource_id,
            attribute=f"environment.{variable}",
            value=expected_value,
        ),
        command_cost=definition.scoring.command_cost,
        now=now,
    )
    return CommandExecutionResult(
        output=f"Przywrócono kontrolowaną zmienną {variable} dla {resource_id}.",
        success=True,
        progress=progress,
    )


def get_controlled_file_status(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    arguments: tuple[Identifier, ...] = (),
    engine: DynamicIncidentEngine | None = None,
    now: datetime | None = None,
) -> CommandExecutionResult:
    resource = _get_controlled_file(
        definition,
        state,
        resource_id=resource_id,
        capability_id="filesystem.stat",
    )
    _require_argument_count(arguments, 0)
    mode = resource.attributes.get("current_mode", "<brak>")
    owner = resource.attributes.get("owner", "<brak>")
    progress = _account_read_only_command(
        definition,
        state,
        fact_id=f"{FILE_STATUS_FACT_PREFIX}{resource_id}",
        engine=engine,
        now=now,
    )
    return CommandExecutionResult(
        output=f"Zasób: {resource_id}\nTryb: {mode}\nWłaściciel: {owner}",
        success=True,
        progress=progress,
    )


def restore_controlled_file_permissions(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    resource_id: Identifier,
    arguments: tuple[Identifier, ...] = (),
    engine: DynamicIncidentEngine | None = None,
    now: datetime | None = None,
) -> CommandExecutionResult:
    resource = _get_controlled_file(
        definition,
        state,
        resource_id=resource_id,
        capability_id="filesystem.restore-permissions",
    )
    _require_argument_count(arguments, 0)
    expected_mode = resource.attributes.get("expected_mode")

    if not isinstance(expected_mode, str):
        raise CommandExecutionError("Plik nie ma kontrolowanego oczekiwanego trybu.")

    dynamic_engine = engine if engine is not None else DynamicIncidentEngine()
    progress = dynamic_engine.execute_command(
        definition,
        state,
        ResourceAttributeUpdate(
            resource_id=resource_id,
            attribute="current_mode",
            value=expected_mode,
        ),
        command_cost=definition.scoring.command_cost,
        now=now,
    )
    service = next(
        (
            candidate
            for candidate in state.world_state.resources.values()
            if candidate.resource_type is ResourceType.SERVICE
            and candidate.attributes.get("executable_resource_id") == resource.resource_id
        ),
        None,
    )
    if service is not None:
        service_name = str(service.attributes.get("service_name", service.resource_id))
        app_name = service_name.removesuffix(".service")
        exec_target = str(service.attributes.get("expected_exec_start", app_name))
        executable = state.virtual_rocky.filesystem.get(
            f"/opt/{app_name}/{exec_target}"
        )
        if executable is not None:
            executable.mode = expected_mode
    return CommandExecutionResult(
        output=f"Przywrócono kontrolowany tryb {expected_mode} dla {resource_id}.",
        success=True,
        progress=progress,
    )
