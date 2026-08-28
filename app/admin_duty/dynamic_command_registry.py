from datetime import datetime
from types import MappingProxyType

from pydantic import Field

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
from app.admin_duty.virtual_shell import (
    shell_cat,
    shell_cd,
    shell_df,
    shell_free,
    shell_grep,
    shell_head,
    shell_hostname,
    shell_id,
    shell_ip_addr,
    shell_ip_route,
    shell_journal,
    shell_journal_xe,
    shell_ls,
    shell_path_stat,
    shell_pwd,
    shell_ss,
    shell_systemd_start,
    shell_systemd_stop,
    shell_tail,
    shell_uname,
    shell_uptime,
    shell_whoami,
)


class DynamicCommandRequest(FrozenDomainModel):
    command_id: Identifier
    resource_id: str = Field(min_length=1, max_length=1024)
    arguments: tuple[str, ...] = Field(default=(), max_length=32)


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
        "shell.pwd": shell_pwd,
        "shell.cd": shell_cd,
        "filesystem.list": shell_ls,
        "filesystem.read": shell_cat,
        "filesystem.head": shell_head,
        "filesystem.tail": shell_tail,
        "filesystem.grep": shell_grep,
        "filesystem.path-stat": shell_path_stat,
        "system.hostname": shell_hostname,
        "system.uname": shell_uname,
        "system.uptime": shell_uptime,
        "system.whoami": shell_whoami,
        "system.id": shell_id,
        "journal.read": shell_journal,
        "journal.xe": shell_journal_xe,
        "resources.memory": shell_free,
        "resources.disk": shell_df,
        "network.addr": shell_ip_addr,
        "network.route": shell_ip_route,
        "network.listeners": shell_ss,
        "systemd.start": shell_systemd_start,
        "systemd.stop": shell_systemd_stop,
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
