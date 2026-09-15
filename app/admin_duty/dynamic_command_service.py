from datetime import datetime

from app.admin_duty.domain.definition import IncidentDefinition
from app.admin_duty.domain.engine import DynamicIncidentEngine
from app.admin_duty.domain.recovery import resolved_fault_ids
from app.admin_duty.domain.runtime import CommandRecord, SessionRuntimeState
from app.admin_duty.dynamic_command_parser import parse_dynamic_command
from app.admin_duty.dynamic_command_registry import DynamicCommandDispatcher
from app.admin_duty.dynamic_commands import (
    CommandExecutionError,
    CommandExecutionResult,
)


class DynamicCommandService:
    @staticmethod
    def _record_command(
        definition,
        state,
        *,
        command,
        capability_id,
        resource_id,
        arguments,
        host_id,
        success,
        environment_changed,
        now,
    ):
        state.command_history.append(
            CommandRecord(
                order=len(state.command_history) + 1,
                command=command,
                capability_id=capability_id,
                resource_id=resource_id,
                arguments=tuple(arguments),
                host_id=host_id,
                success=success,
                environment_changed=environment_changed,
                resolved_fault_ids=tuple(sorted(resolved_fault_ids(definition, state))),
                occurred_at=now or state.last_activity,
            )
        )

    def save_file(self, definition, state, *, path, content, engine=None, now=None):
        from app.admin_duty.domain.engine import _commit_candidate, _validate_candidate
        from app.admin_duty.rocky.filesystem import save_virtual_file

        if "filesystem.edit" not in definition.capabilities.command_capability_ids:
            raise CommandExecutionError("Edytor nie jest dostępny w tym incydencie.")
        candidate = state.model_copy(deep=True)
        command_host_id = candidate.active_host_id
        world_before = candidate.world_state.model_copy(deep=True)
        hosts_before = {
            host_id: runtime.model_copy(deep=True)
            for host_id, runtime in candidate.host_runtimes.items()
        }
        result = save_virtual_file(
            definition, candidate, path=path, content=content, engine=engine, now=now
        )
        self._record_command(
            definition,
            candidate,
            command=f"zapis pliku {path}",
            capability_id="filesystem.edit",
            resource_id=path,
            arguments=(path,),
            host_id=command_host_id,
            success=result.success,
            environment_changed=(
                candidate.world_state != world_before
                or candidate.host_runtimes != hosts_before
            ),
            now=now,
        )
        _commit_candidate(state, _validate_candidate(candidate))
        return result

    def execute(
        self,
        definition: IncidentDefinition,
        state: SessionRuntimeState,
        command: str,
        *,
        engine: DynamicIncidentEngine | None = None,
        now: datetime | None = None,
    ) -> CommandExecutionResult:
        request = parse_dynamic_command(command)

        from app.admin_duty.domain.engine import _commit_candidate, _validate_candidate

        candidate = state.model_copy(deep=True)
        command_host_id = candidate.active_host_id
        world_before = candidate.world_state.model_copy(deep=True)
        hosts_before = {
            host_id: runtime.model_copy(deep=True)
            for host_id, runtime in candidate.host_runtimes.items()
        }
        result = DynamicCommandDispatcher().dispatch(
            definition,
            candidate,
            request,
            engine=engine,
            now=now,
        )
        self._record_command(
            definition,
            candidate,
            command=command,
            capability_id=request.command_id,
            resource_id=request.resource_id,
            arguments=request.arguments,
            host_id=command_host_id,
            success=result.success,
            environment_changed=(
                candidate.world_state != world_before
                or candidate.host_runtimes != hosts_before
            ),
            now=now,
        )
        _commit_candidate(state, _validate_candidate(candidate))
        cwd = candidate.current_working_directory
        home = candidate.virtual_rocky.home_directory
        display_cwd = "~" if cwd == home else cwd
        if cwd.startswith(f"{home}/"):
            display_cwd = f"~/{cwd.removeprefix(f'{home}/')}"
        return result.model_copy(
            update={
                "current_working_directory": cwd,
                "prompt": (
                    f"{candidate.virtual_rocky.user}@"
                    f"{candidate.virtual_rocky.hostname}:{display_cwd}$"
                ),
            }
        )
