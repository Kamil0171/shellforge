from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from pydantic import Field

from app.admin_duty.domain.definition import (
    FrozenDomainModel,
    Identifier,
    IncidentDefinition,
    InterfaceCapability,
)
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.progress import SessionProgress, get_session_progress
from app.admin_duty.domain.runtime import (
    create_session_runtime,
    end_session_runtime,
)
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.dynamic_commands import CommandExecutionResult
from app.admin_duty.repositories.protocols import (
    ScenarioRepository,
    SessionRepository,
)


class IncidentGenerator(Protocol):
    def generate(
        self,
        difficulty: DifficultyLevel,
        *,
        seed: int | None = None,
        now: datetime | None = None,
    ) -> IncidentDefinition: ...


class DynamicIncidentPublicInfo(FrozenDomainModel):
    scenario_id: UUID
    title: str = Field(min_length=1, max_length=120)
    organization: str = Field(min_length=1, max_length=120)
    environment_label: str = Field(min_length=1, max_length=80)
    briefing: str = Field(min_length=1, max_length=4000)
    difficulty: DifficultyLevel
    main_objective: str = Field(min_length=1, max_length=600)
    interfaces: tuple[InterfaceCapability, ...]
    command_capabilities: tuple[Identifier, ...]


class DynamicSessionStartResult(FrozenDomainModel):
    scenario_id: UUID
    session_id: UUID
    difficulty: DifficultyLevel
    incident: DynamicIncidentPublicInfo
    progress: SessionProgress


class DynamicSessionView(FrozenDomainModel):
    incident: DynamicIncidentPublicInfo
    progress: SessionProgress


class DynamicSessionEndResult(FrozenDomainModel):
    ended: bool
    progress: SessionProgress


def utc_now() -> datetime:
    return datetime.now(UTC)


def _resolve_now(now: datetime | None) -> datetime:
    current_time = now if now is not None else utc_now()

    if current_time.tzinfo is None or current_time.utcoffset() is None:
        raise ValueError("Czas operacji musi zawierać strefę czasową.")

    return current_time


def _get_public_info(
    definition: IncidentDefinition,
) -> DynamicIncidentPublicInfo:
    return DynamicIncidentPublicInfo(
        scenario_id=definition.scenario_id,
        title=definition.presentation.title,
        organization=definition.presentation.organization,
        environment_label=definition.presentation.environment_label,
        briefing=definition.presentation.briefing,
        difficulty=definition.difficulty,
        main_objective=definition.presentation.main_objective,
        interfaces=definition.capabilities.interfaces,
        command_capabilities=(definition.capabilities.command_capability_ids),
    )


class DynamicIncidentService:
    def __init__(
        self,
        *,
        generator: IncidentGenerator,
        scenario_repository: ScenarioRepository,
        session_repository: SessionRepository,
        command_service: DynamicCommandService | None = None,
    ) -> None:
        self._generator = generator
        self._scenarios = scenario_repository
        self._sessions = session_repository
        self._commands = (
            command_service if command_service is not None else DynamicCommandService()
        )

    def _cleanup(self, now: datetime) -> None:
        expired_states = self._sessions.cleanup_expired(now=now)
        expired_scenario_ids = {state.scenario_id for state in expired_states}

        for scenario_id in expired_scenario_ids:
            if not self._sessions.has_scenario(scenario_id, now=now):
                self._scenarios.delete(scenario_id)

    def start_session(
        self,
        difficulty: DifficultyLevel,
        *,
        seed: int | None = None,
        now: datetime | None = None,
    ) -> DynamicSessionStartResult:
        current_time = _resolve_now(now)
        self._cleanup(current_time)
        definition = self._generator.generate(
            difficulty,
            seed=seed,
            now=current_time,
        )
        self._scenarios.save(definition)
        state = create_session_runtime(definition, now=current_time)

        try:
            self._sessions.save(state, now=current_time)
        except Exception:
            self._scenarios.delete(definition.scenario_id)
            raise

        progress = get_session_progress(definition, state)
        return DynamicSessionStartResult(
            scenario_id=definition.scenario_id,
            session_id=state.session_id,
            difficulty=definition.difficulty,
            incident=_get_public_info(definition),
            progress=progress,
        )

    def execute_command(
        self,
        session_id: UUID,
        command: str,
        *,
        now: datetime | None = None,
    ) -> CommandExecutionResult:
        current_time = _resolve_now(now)
        self._cleanup(current_time)
        state = self._sessions.get(session_id, now=current_time)
        expected_revision = state.revision
        definition = self._scenarios.get(state.scenario_id)
        result = self._commands.execute(
            definition,
            state,
            command,
            now=current_time,
        )
        self._sessions.update(
            state,
            expected_revision=expected_revision,
            now=current_time,
        )
        return result

    def get_progress(
        self,
        session_id: UUID,
        *,
        now: datetime | None = None,
    ) -> DynamicSessionView:
        current_time = _resolve_now(now)
        self._cleanup(current_time)
        state = self._sessions.get(session_id, now=current_time)
        definition = self._scenarios.get(state.scenario_id)
        return DynamicSessionView(
            incident=_get_public_info(definition),
            progress=get_session_progress(definition, state),
        )

    def end_session(
        self,
        session_id: UUID,
        *,
        now: datetime | None = None,
    ) -> DynamicSessionEndResult:
        current_time = _resolve_now(now)
        self._cleanup(current_time)
        state = self._sessions.get(session_id, now=current_time)
        expected_revision = state.revision
        definition = self._scenarios.get(state.scenario_id)
        end_session_runtime(state, now=current_time)
        self._sessions.update(
            state,
            expected_revision=expected_revision,
            now=current_time,
        )
        return DynamicSessionEndResult(
            ended=True,
            progress=get_session_progress(definition, state),
        )
