from datetime import datetime
from types import MappingProxyType

from app.admin_duty.domain.definition import (
    FrozenDomainModel,
    Identifier,
    IncidentDefinition,
)
from app.admin_duty.domain.engine import DynamicIncidentEngine
from app.admin_duty.domain.runtime import SessionRuntimeState
from app.admin_duty.dynamic_commands import (
    CommandExecutionError,
    CommandExecutionResult,
    get_controlled_file_status,
    get_systemd_environment,
    get_systemd_service_configuration,
    get_systemd_service_status,
    restart_systemd_service,
    restore_controlled_file_permissions,
    restore_systemd_environment,
    set_systemd_exec_start,
)


class DynamicCommandRequest(FrozenDomainModel):
    command_id: Identifier
    resource_id: Identifier
    arguments: tuple[Identifier, ...] = ()


class CommandDispatchError(CommandExecutionError):
    pass


COMMAND_HANDLERS = MappingProxyType(
    {
        "systemd.status": get_systemd_service_status,
        "systemd.restart": restart_systemd_service,
        "systemd.cat": get_systemd_service_configuration,
        "systemd.set-exec-start": set_systemd_exec_start,
        "environment.inspect": get_systemd_environment,
        "environment.restore": restore_systemd_environment,
        "filesystem.stat": get_controlled_file_status,
        "filesystem.restore-permissions": restore_controlled_file_permissions,
    }
)


class DynamicCommandDispatcher:
    def dispatch(
        self,
        definition: IncidentDefinition,
        state: SessionRuntimeState,
        request: DynamicCommandRequest,
        *,
        engine: DynamicIncidentEngine | None = None,
        now: datetime | None = None,
    ) -> CommandExecutionResult:
        handler = COMMAND_HANDLERS.get(request.command_id)

        if handler is None:
            raise CommandDispatchError(
                f"Nieznana komenda dynamiczna: {request.command_id}."
            )

        if request.command_id not in definition.capabilities.command_capability_ids:
            raise CommandDispatchError(
                f"Komenda {request.command_id} nie jest dostępna w scenariuszu."
            )

        return handler(
            definition,
            state,
            resource_id=request.resource_id,
            arguments=request.arguments,
            engine=engine,
            now=now,
        )
