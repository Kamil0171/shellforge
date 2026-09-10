from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field

from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.runtime import InactiveSessionError
from app.admin_duty.dynamic_command_parser import (
    MAX_DYNAMIC_COMMAND_LENGTH,
    CommandParseError,
)
from app.admin_duty.dynamic_command_registry import CommandDispatchError
from app.admin_duty.dynamic_commands import (
    CommandExecutionError,
    CommandExecutionResult,
)
from app.admin_duty.generators import (
    DeterministicIncidentGenerator,
    GenerationError,
    UnsupportedDifficultyError,
)
from app.admin_duty.repositories import (
    InMemoryScenarioRepository,
    InMemorySessionRepository,
    ScenarioConflictError,
    ScenarioNotFoundError,
    SessionConflictError,
    SessionLimitError,
    SessionNotFoundError,
)
from app.admin_duty.services import (
    DynamicHintResult,
    DynamicIncidentService,
    DynamicSessionEndResult,
    DynamicSessionStartResult,
    DynamicSessionView,
    HintUnavailableError,
)
from app.admin_duty.services.incident_generation import configured_generation_service

router = APIRouter(
    prefix="/admin-duty/dynamic",
    tags=["admin-duty-dynamic"],
)

templates = Jinja2Templates(directory="app/templates")


class StrictRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DynamicStartRequest(StrictRequestModel):
    difficulty: DifficultyLevel
    seed: int | None = Field(default=None, ge=0, le=2**63 - 1)


class DynamicCommandRequest(StrictRequestModel):
    session_id: UUID
    command: str = Field(max_length=MAX_DYNAMIC_COMMAND_LENGTH)


class DynamicEndRequest(StrictRequestModel):
    session_id: UUID


class DynamicFileRequest(StrictRequestModel):
    session_id: UUID
    path: str = Field(min_length=1, max_length=1024)
    content: str = Field(max_length=32768)


class DynamicHintRequest(StrictRequestModel):
    session_id: UUID


_scenario_repository = InMemoryScenarioRepository()
_session_repository = InMemorySessionRepository()
_deterministic_generator = DeterministicIncidentGenerator()
_dynamic_incident_service = DynamicIncidentService(
    generator=_deterministic_generator,
    generation_service=configured_generation_service(_deterministic_generator),
    scenario_repository=_scenario_repository,
    session_repository=_session_repository,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


def get_dynamic_incident_service() -> DynamicIncidentService:
    return _dynamic_incident_service


@router.get("/", response_class=HTMLResponse)
def dynamic_incident_lobby(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin_duty/dynamic/index.html",
        context={},
    )


@router.get(
    "/sessions/{session_id}",
    response_class=HTMLResponse,
)
def dynamic_incident_workspace(
    request: Request,
    session_id: UUID,
):
    return templates.TemplateResponse(
        request=request,
        name="admin_duty/dynamic/scenario.html",
        context={"session_id": str(session_id)},
    )


def _error_response(error: Exception) -> JSONResponse:
    if isinstance(error, SessionNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": "Sesja nie istnieje lub wygasła."},
        )

    if isinstance(error, InactiveSessionError):
        return JSONResponse(
            status_code=409,
            content={"detail": str(error)},
        )

    if isinstance(error, HintUnavailableError):
        return JSONResponse(
            status_code=409,
            content={"detail": str(error)},
        )

    if isinstance(error, SessionConflictError):
        return JSONResponse(
            status_code=409,
            content={"detail": "Sesja została równocześnie zmodyfikowana."},
        )

    if isinstance(error, SessionLimitError):
        return JSONResponse(
            status_code=503,
            content={"detail": "Limit aktywnych sesji został osiągnięty."},
        )

    if isinstance(error, GenerationError):
        return JSONResponse(
            status_code=503,
            content={"detail": "Nie udało się przygotować poprawnego incydentu."},
        )

    if isinstance(
        error,
        (
            UnsupportedDifficultyError,
            CommandParseError,
            CommandDispatchError,
            CommandExecutionError,
        ),
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": str(error)},
        )

    if isinstance(error, (ScenarioConflictError, ScenarioNotFoundError)):
        return JSONResponse(
            status_code=409,
            content={"detail": "Dane incydentu są niespójne."},
        )

    raise error


@router.post(
    "/api/start",
    response_model=DynamicSessionStartResult,
    response_model_exclude_none=True,
)
async def start_dynamic_session(
    payload: DynamicStartRequest,
    service: DynamicIncidentService = Depends(get_dynamic_incident_service),
):
    try:
        return await service.start_session_async(
            payload.difficulty,
            seed=payload.seed,
            now=utc_now(),
        )
    except Exception as error:
        return _error_response(error)


@router.get(
    "/api/sessions/{session_id}",
    response_model=DynamicSessionView,
    response_model_exclude_none=True,
)
def get_dynamic_session(
    session_id: UUID,
    service: DynamicIncidentService = Depends(get_dynamic_incident_service),
):
    try:
        return service.get_progress(session_id, now=utc_now())
    except Exception as error:
        return _error_response(error)


@router.post(
    "/api/command",
    response_model=CommandExecutionResult,
)
def execute_dynamic_command(
    payload: DynamicCommandRequest,
    service: DynamicIncidentService = Depends(get_dynamic_incident_service),
):
    try:
        return service.execute_command(
            payload.session_id,
            payload.command,
            now=utc_now(),
        )
    except Exception as error:
        return _error_response(error)


@router.post(
    "/api/hint",
    response_model=DynamicHintResult,
)
def request_dynamic_hint(
    payload: DynamicHintRequest,
    service: DynamicIncidentService = Depends(get_dynamic_incident_service),
):
    try:
        return service.request_hint(payload.session_id, now=utc_now())
    except Exception as error:
        return _error_response(error)


@router.post("/api/file", response_model=CommandExecutionResult)
def save_dynamic_file(
    payload: DynamicFileRequest,
    service: DynamicIncidentService = Depends(get_dynamic_incident_service),
):
    try:
        return service.save_file(
            payload.session_id,
            path=payload.path,
            content=payload.content,
            now=utc_now(),
        )
    except Exception as error:
        return _error_response(error)


@router.post(
    "/api/end",
    response_model=DynamicSessionEndResult,
    response_model_exclude_none=True,
)
def end_dynamic_session(
    payload: DynamicEndRequest,
    service: DynamicIncidentService = Depends(get_dynamic_incident_service),
):
    try:
        return service.end_session(payload.session_id, now=utc_now())
    except Exception as error:
        return _error_response(error)
