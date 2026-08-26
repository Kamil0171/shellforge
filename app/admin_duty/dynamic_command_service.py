from datetime import datetime

from app.admin_duty.domain.definition import IncidentDefinition
from app.admin_duty.domain.engine import DynamicIncidentEngine
from app.admin_duty.domain.runtime import SessionRuntimeState
from app.admin_duty.dynamic_command_parser import parse_dynamic_command
from app.admin_duty.dynamic_command_registry import DynamicCommandDispatcher
from app.admin_duty.dynamic_commands import CommandExecutionResult


class DynamicCommandService:
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

        return DynamicCommandDispatcher().dispatch(
            definition,
            state,
            request,
            engine=engine,
            now=now,
        )
