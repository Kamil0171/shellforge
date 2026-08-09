from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Literal, TypedDict
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.admin_duty.commands import (
    execute_command,
    save_service_file,
)
from app.admin_duty.engine import (
    create_scenario_state,
    get_progress,
    reveal_next_hint,
    reveal_solution,
)
from app.admin_duty.scenarios.incident_001 import SCENARIO

router = APIRouter(
    prefix="/admin-duty",
    tags=["admin-duty"],
)

templates = Jinja2Templates(
    directory="app/templates",
)

SESSION_TTL = timedelta(minutes=45)
MAX_ACTIVE_SESSIONS = 500
MAX_COMMAND_LENGTH = 1024
MAX_SERVICE_FILE_BYTES = 32 * 1024


class ScenarioSession(TypedDict):
    state: dict
    created_at: datetime
    last_activity: datetime


sessions: dict[str, ScenarioSession] = {}
_sessions_lock = Lock()


class StrictRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StartScenarioRequest(StrictRequestModel):
    scenario_id: Literal["INC-001"]


class SessionRequest(StrictRequestModel):
    session_id: UUID


class CommandRequest(SessionRequest):
    command: str = Field(max_length=MAX_COMMAND_LENGTH)


class ServiceFileRequest(SessionRequest):
    content: str = Field(max_length=MAX_SERVICE_FILE_BYTES)

    @field_validator("content")
    @classmethod
    def validate_content_size(cls, content: str) -> str:
        if len(content.encode("utf-8")) > MAX_SERVICE_FILE_BYTES:
            raise ValueError("Treść pliku przekracza limit 32 KiB.")

        return content


def utc_now() -> datetime:
    return datetime.now(UTC)


def _cleanup_expired_sessions_locked(now: datetime) -> int:
    expired_session_ids = [
        session_id
        for session_id, session in sessions.items()
        if now - session["last_activity"] >= SESSION_TTL
    ]

    for session_id in expired_session_ids:
        sessions.pop(session_id, None)

    return len(expired_session_ids)


def cleanup_expired_sessions(now: datetime | None = None) -> int:
    current_time = now or utc_now()

    with _sessions_lock:
        return _cleanup_expired_sessions_locked(current_time)


def _get_active_session(session_id: UUID) -> dict | None:
    current_time = utc_now()
    session_key = str(session_id)

    with _sessions_lock:
        _cleanup_expired_sessions_locked(current_time)
        session = sessions.get(session_key)

        if session is None:
            return None

        session["last_activity"] = current_time

        return session["state"]


def get_session(session_id: UUID) -> dict:
    state = _get_active_session(session_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Sesja gry nie istnieje.",
        )

    return state


@router.get(
    "/",
    response_class=HTMLResponse,
)
def admin_duty(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin_duty/index.html",
        context={
            "scenarios": [SCENARIO],
        },
    )


@router.post("/api/start")
def start_scenario(
    payload: StartScenarioRequest,
):
    current_time = utc_now()

    with _sessions_lock:
        _cleanup_expired_sessions_locked(current_time)

        if len(sessions) >= MAX_ACTIVE_SESSIONS:
            raise HTTPException(
                status_code=503,
                detail="Limit aktywnych sesji został osiągnięty.",
            )

        session_id = str(uuid4())
        sessions[session_id] = {
            "state": create_scenario_state(),
            "created_at": current_time,
            "last_activity": current_time,
        }

    return {
        "session_id": session_id,
        "redirect_url": (
            "/admin-duty/scenarios/"
            f"{SCENARIO['slug']}/"
            f"?session_id={session_id}"
        ),
    }


@router.get(
    "/scenarios/inc-001/",
    response_class=HTMLResponse,
)
def scenario_inc_001(
    request: Request,
    session_id: UUID | None = None,
):
    state = None if session_id is None else _get_active_session(session_id)

    if state is None:
        return RedirectResponse(
            url="/admin-duty/?view=scenarios",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin_duty/scenario.html",
        context={
            "scenario": SCENARIO,
            "session_id": str(session_id),
            "progress": get_progress(state),
        },
    )


@router.post("/api/command")
def run_command(
    payload: CommandRequest,
):
    state = get_session(
        payload.session_id,
    )

    return execute_command(
        payload.command,
        state,
    )


@router.post("/api/service-file")
def update_service_file(
    payload: ServiceFileRequest,
):
    state = get_session(
        payload.session_id,
    )

    return save_service_file(
        payload.content,
        state,
    )


@router.post("/api/hint")
def get_hint(
    payload: SessionRequest,
):
    state = get_session(
        payload.session_id,
    )

    return reveal_next_hint(state)


@router.post("/api/solution")
def get_solution(
    payload: SessionRequest,
):
    state = get_session(
        payload.session_id,
    )

    return reveal_solution(state)


@router.post("/api/end")
def end_scenario(
    payload: SessionRequest,
):
    current_time = utc_now()

    with _sessions_lock:
        _cleanup_expired_sessions_locked(current_time)
        sessions.pop(
            str(payload.session_id),
            None,
        )

    return {
        "ended": True,
    }
