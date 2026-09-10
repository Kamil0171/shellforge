from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from pydantic import Field

from app.admin_duty.domain.definition import (
    DependencyType,
    FrozenDomainModel,
    Hint,
    Identifier,
    IncidentDefinition,
    InterfaceCapability,
    ResourceType,
)
from app.admin_duty.domain.difficulty import (
    DifficultyLevel,
    get_difficulty_profile,
)
from app.admin_duty.domain.generation import IncidentGenerationRequest
from app.admin_duty.domain.progress import SessionProgress, get_session_progress
from app.admin_duty.domain.runtime import (
    InactiveSessionError,
    SessionRuntimeState,
    SessionStatus,
    create_session_runtime,
    end_session_runtime,
    register_hint,
)
from app.admin_duty.dynamic_command_service import DynamicCommandService
from app.admin_duty.dynamic_commands import CommandExecutionResult
from app.admin_duty.repositories.protocols import (
    ScenarioRepository,
    SessionRepository,
)
from app.admin_duty.services.public_gameplay import (
    PublicGameMap,
    PublicMonitoring,
    project_public_game_map,
    project_public_monitoring,
)
from app.admin_duty.services.support_center import (
    PublicSupportCenter,
    project_public_support_center,
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


class PublicInfrastructureNode(FrozenDomainModel):
    id: Identifier
    label: str = Field(min_length=1, max_length=160)
    type: ResourceType
    status: Identifier
    role: str = Field(min_length=1, max_length=120)
    parent_id: Identifier | None = None
    health: Identifier | None = None


class PublicInfrastructureLink(FrozenDomainModel):
    source: Identifier
    target: Identifier
    label: str | None = Field(default=None, min_length=1, max_length=120)
    dependency_type: DependencyType | None = None
    protocol: str | None = Field(default=None, min_length=1, max_length=16)
    port: int | None = Field(default=None, ge=1, le=65535)


class PublicInfrastructure(FrozenDomainModel):
    nodes: tuple[PublicInfrastructureNode, ...]
    links: tuple[PublicInfrastructureLink, ...]


class PublicHint(FrozenDomainModel):
    order: int = Field(ge=1, le=100)
    text: str = Field(min_length=1, max_length=1000)
    cost: int = Field(ge=0, le=100_000)


class PublicShellState(FrozenDomainModel):
    user: str = Field(min_length=1, max_length=64)
    hostname: str = Field(min_length=1, max_length=253)
    current_working_directory: str = Field(min_length=1, max_length=1024)
    prompt: str = Field(min_length=1, max_length=1200)


class PublicPostIncidentReport(FrozenDomainModel):
    root_cause: str = Field(min_length=1, max_length=1000)
    affected_services: tuple[str, ...] = Field(min_length=1, max_length=64)
    diagnostic_milestones: tuple[Identifier, ...] = Field(default=(), max_length=512)
    repair_actions: tuple[str, ...] = Field(default=(), max_length=512)
    final_state: tuple[PublicInfrastructureNode, ...]
    commands_used: tuple[str, ...] = Field(default=(), max_length=512)
    hints_used: int = Field(ge=0)
    score: int = Field(ge=0, le=1_000_000)


class DynamicSessionStartResult(FrozenDomainModel):
    scenario_id: UUID
    session_id: UUID
    difficulty: DifficultyLevel
    incident: DynamicIncidentPublicInfo
    infrastructure: PublicInfrastructure
    game_map: PublicGameMap
    monitoring: PublicMonitoring
    shell: PublicShellState
    support_center: PublicSupportCenter
    revealed_hints: tuple[PublicHint, ...]
    hint_limit: int = Field(ge=0)
    progress: SessionProgress
    post_incident: PublicPostIncidentReport | None = None


class DynamicSessionView(FrozenDomainModel):
    incident: DynamicIncidentPublicInfo
    infrastructure: PublicInfrastructure
    game_map: PublicGameMap
    monitoring: PublicMonitoring
    shell: PublicShellState
    support_center: PublicSupportCenter
    revealed_hints: tuple[PublicHint, ...]
    hint_limit: int = Field(ge=0)
    progress: SessionProgress
    post_incident: PublicPostIncidentReport | None = None


class DynamicSessionEndResult(FrozenDomainModel):
    ended: bool
    progress: SessionProgress
    post_incident: PublicPostIncidentReport | None = None


class DynamicHintResult(FrozenDomainModel):
    hint: PublicHint
    revealed_hints: tuple[PublicHint, ...]
    hint_limit: int = Field(ge=0)
    progress: SessionProgress


class HintUnavailableError(ValueError):
    pass


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
    )


def _public_resource_label(resource) -> str:
    hostname = resource.attributes.get("hostname")

    if resource.resource_type is ResourceType.HOST and isinstance(hostname, str):
        return hostname

    service_name = resource.attributes.get("service_name")
    if resource.resource_type is ResourceType.SERVICE and isinstance(service_name, str):
        return service_name
    return resource.resource_id


def _public_resource_role(resource) -> str:
    role = resource.attributes.get("role")

    if resource.resource_type is ResourceType.HOST and isinstance(role, str):
        return role

    return "usługa systemd"


def _public_resource_health(resource) -> str | None:
    health = resource.attributes.get("public_health")
    return health if resource.resource_type is ResourceType.SERVICE and isinstance(health, str) else None


def _get_public_infrastructure(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> PublicInfrastructure:
    public_types = {ResourceType.HOST, ResourceType.SERVICE}
    resources = tuple(
        resource
        for resource in state.world_state.resources.values()
        if resource.resource_type in public_types
    )
    public_ids = {resource.resource_id for resource in resources}
    nodes = tuple(
        PublicInfrastructureNode(
            id=resource.resource_id,
            label=_public_resource_label(resource),
            type=resource.resource_type,
            status=resource.current_state,
            role=_public_resource_role(resource),
            parent_id=(
                resource.parent_resource_id
                if resource.parent_resource_id in public_ids
                else None
            ),
            health=_public_resource_health(resource),
        )
        for resource in resources
    )
    ownership_links = tuple(
        PublicInfrastructureLink(
            source=resource.parent_resource_id,
            target=resource.resource_id,
            label="uruchamia",
        )
        for resource in resources
        if resource.parent_resource_id in public_ids
    )
    dependency_links = tuple(
        PublicInfrastructureLink(
            source=dependency.source_service_id,
            target=dependency.target_service_id,
            label="zależy od",
            dependency_type=dependency.dependency_type,
            protocol=dependency.protocol.value,
            port=dependency.port,
        )
        for dependency in definition.service_dependencies
        if dependency.publicly_visible
        and dependency.source_service_id in public_ids
        and dependency.target_service_id in public_ids
    )
    return PublicInfrastructure(nodes=nodes, links=(*ownership_links, *dependency_links))


def _get_post_incident_report(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> PublicPostIncidentReport | None:
    post_incident = definition.post_incident
    progress = get_session_progress(definition, state)
    if post_incident is None or not progress.mission_complete:
        return None
    affected_ids = set(post_incident.affected_service_ids)
    affected_services = tuple(
        _public_resource_label(resource)
        for resource in state.world_state.resources.values()
        if resource.resource_id in affected_ids
    )
    repair_capabilities = set(post_incident.repair_capability_ids)
    return PublicPostIncidentReport(
        root_cause=post_incident.root_cause,
        affected_services=affected_services,
        diagnostic_milestones=tuple(sorted(state.discovered_fact_ids)),
        repair_actions=tuple(
            record.command
            for record in state.command_history
            if record.capability_id in repair_capabilities and record.success
        ),
        final_state=_get_public_infrastructure(definition, state).nodes,
        commands_used=tuple(record.command for record in state.command_history),
        hints_used=state.hints_used,
        score=state.score,
    )


def _to_public_hint(hint: Hint) -> PublicHint:
    return PublicHint(order=hint.order, text=hint.text, cost=hint.cost)


def _get_revealed_hints(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> tuple[PublicHint, ...]:
    return tuple(_to_public_hint(hint) for hint in definition.hints[: state.hints_used])


def _get_hint_limit(definition: IncidentDefinition) -> int:
    return get_difficulty_profile(definition.difficulty).hint_limit


def _get_public_shell(state: SessionRuntimeState) -> PublicShellState:
    cwd = state.current_working_directory
    home = state.virtual_rocky.home_directory
    display_cwd = "~" if cwd == home else cwd
    if cwd.startswith(f"{home}/"):
        display_cwd = f"~/{cwd.removeprefix(f'{home}/')}"
    return PublicShellState(
        user=state.virtual_rocky.user,
        hostname=state.virtual_rocky.hostname,
        current_working_directory=cwd,
        prompt=f"{state.virtual_rocky.user}@{state.virtual_rocky.hostname}:{display_cwd}$",
    )


class DynamicIncidentService:
    def __init__(
        self,
        *,
        generator: IncidentGenerator,
        scenario_repository: ScenarioRepository,
        session_repository: SessionRepository,
        command_service: DynamicCommandService | None = None,
        generation_service=None,
    ) -> None:
        self._generator = generator
        self._generation_service = generation_service
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
        return self._start_definition(definition, current_time)

    async def start_session_async(self, difficulty, *, seed=None, now=None):
        if self._generation_service is None:
            return self.start_session(difficulty, seed=seed, now=now)
        current_time = _resolve_now(now)
        definition = await self._generation_service.generate(
            IncidentGenerationRequest(difficulty=difficulty, seed=seed, generation_source="ai"),
            now=current_time,
        )
        return self._start_definition(definition, _resolve_now(now))

    def _start_definition(self, definition, current_time):
        self._cleanup(current_time)
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
            infrastructure=_get_public_infrastructure(definition, state),
            game_map=project_public_game_map(definition.initial_world_state.map, state),
            monitoring=project_public_monitoring(definition, state),
            shell=_get_public_shell(state),
            support_center=project_public_support_center(definition),
            revealed_hints=_get_revealed_hints(definition, state),
            hint_limit=_get_hint_limit(definition),
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

    def save_file(self, session_id, *, path, content, now=None):
        current_time = _resolve_now(now)
        self._cleanup(current_time)
        state = self._sessions.get(session_id, now=current_time)
        expected_revision = state.revision
        definition = self._scenarios.get(state.scenario_id)
        result = self._commands.save_file(
            definition, state, path=path, content=content, now=current_time
        )
        self._sessions.update(
            state, expected_revision=expected_revision, now=current_time
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
            infrastructure=_get_public_infrastructure(definition, state),
            game_map=project_public_game_map(definition.initial_world_state.map, state),
            monitoring=project_public_monitoring(definition, state),
            shell=_get_public_shell(state),
            support_center=project_public_support_center(definition),
            revealed_hints=_get_revealed_hints(definition, state),
            hint_limit=_get_hint_limit(definition),
            progress=get_session_progress(definition, state),
            post_incident=_get_post_incident_report(definition, state),
        )

    def request_hint(
        self,
        session_id: UUID,
        *,
        now: datetime | None = None,
    ) -> DynamicHintResult:
        current_time = _resolve_now(now)
        self._cleanup(current_time)
        state = self._sessions.get(session_id, now=current_time)
        expected_revision = state.revision
        definition = self._scenarios.get(state.scenario_id)
        hint_limit = _get_hint_limit(definition)
        available_count = min(hint_limit, len(definition.hints))

        if state.status is not SessionStatus.ACTIVE:
            raise InactiveSessionError(
                "Operacja jest dostępna wyłącznie dla aktywnej sesji."
            )

        if state.hints_used >= available_count:
            raise HintUnavailableError("Wykorzystano wszystkie dostępne podpowiedzi.")

        hint = definition.hints[state.hints_used]
        register_hint(state, penalty=hint.cost, now=current_time)
        self._sessions.update(
            state,
            expected_revision=expected_revision,
            now=current_time,
        )
        revealed_hints = _get_revealed_hints(definition, state)
        return DynamicHintResult(
            hint=_to_public_hint(hint),
            revealed_hints=revealed_hints,
            hint_limit=hint_limit,
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
            post_incident=_get_post_incident_report(definition, state),
        )
