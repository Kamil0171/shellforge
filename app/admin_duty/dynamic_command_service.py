from datetime import datetime

from app.admin_duty.domain.definition import IncidentDefinition
from app.admin_duty.domain.engine import DynamicIncidentEngine
from app.admin_duty.domain.runtime import SessionRuntimeState
from app.admin_duty.dynamic_command_parser import parse_dynamic_command
from app.admin_duty.dynamic_command_registry import DynamicCommandDispatcher
from app.admin_duty.dynamic_commands import (
    CommandExecutionError,
    CommandExecutionResult,
)


class DynamicCommandService:
    def save_file(self, definition, state, *, path, content, engine=None, now=None):
        from app.admin_duty.domain.engine import _commit_candidate, _validate_candidate
        from app.admin_duty.rocky.filesystem import save_virtual_file

        if "filesystem.edit" not in definition.capabilities.command_capability_ids:
            raise CommandExecutionError("Edytor nie jest dostępny w tym incydencie.")
        candidate = state.model_copy(deep=True)
        result = save_virtual_file(
            definition, candidate, path=path, content=content, engine=engine, now=now
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

        result = DynamicCommandDispatcher().dispatch(
            definition,
            state,
            request,
            engine=engine,
            now=now,
        )
        cwd = state.current_working_directory
        home = state.virtual_rocky.home_directory
        display_cwd = "~" if cwd == home else cwd
        if cwd.startswith(f"{home}/"):
            display_cwd = f"~/{cwd.removeprefix(f'{home}/')}"
        return result.model_copy(
            update={
                "current_working_directory": cwd,
                "prompt": f"operator@incident:{display_cwd}$",
            }
        )
