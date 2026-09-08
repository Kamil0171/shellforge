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
)
from app.admin_duty.rocky.registry import HANDLERS


class DynamicCommandRequest(FrozenDomainModel):
    command_id: Identifier
    resource_id: str = Field(min_length=1, max_length=1024)
    arguments: tuple[str, ...] = Field(default=(), max_length=32)


class CommandDispatchError(CommandExecutionError):
    pass


COMMAND_HANDLERS = MappingProxyType(HANDLERS)


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

        candidate = state.model_copy(deep=True)
        result = handler(
            definition,
            candidate,
            resource_id=request.resource_id,
            arguments=request.arguments,
            engine=engine,
            now=now,
        )
        from app.admin_duty.domain.engine import _commit_candidate, _validate_candidate

        _commit_candidate(state, _validate_candidate(candidate))
        return result
