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
    output: str = Field(min_length=1, max_length=1000)
    success: bool
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
                f"Nie udało się uruchomić usługi {resource_id}. "
                "Sprawdź jej konfigurację i zależności."
            ),
            success=False,
            progress=progress,
        )

    already_running = resource.current_state == RUNNING_STATE
    progress = dynamic_engine.execute_command(
        definition,
        state,
        ResourceStateUpdate(
            resource_id=resource_id,
            new_state=RUNNING_STATE,
        ),
        command_cost=definition.scoring.command_cost,
        now=now,
    )
    output = (
        f"Usługa {resource_id} już działa."
        if already_running
        else f"Usługa {resource_id} została ponownie uruchomiona."
    )

    return CommandExecutionResult(
        output=output,
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
    output = f"● {display_name}\n   Loaded: loaded\n   Active: {resource.current_state}"

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
    expected = resource.attributes.get("expected_exec_start", "<brak>")
    output = f"[Service]\nExecStart={configured}\nDozwolony cel: {expected}"
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
            resource_id=resource_id,
            attribute="configured_exec_start",
            value=target,
        ),
        command_cost=definition.scoring.command_cost,
        now=now,
    )
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
            resource_id=resource_id,
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
    return CommandExecutionResult(
        output=f"Przywrócono kontrolowany tryb {expected_mode} dla {resource_id}.",
        success=True,
        progress=progress,
    )
