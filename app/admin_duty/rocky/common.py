import posixpath
from datetime import datetime

from app.admin_duty.domain.definition import IncidentDefinition
from app.admin_duty.domain.engine import DynamicIncidentEngine
from app.admin_duty.domain.runtime import SessionRuntimeState, VirtualFileEntry
from app.admin_duty.dynamic_commands import (
    CommandExecutionResult,
    VirtualEditorAction,
)


def _engine(engine: DynamicIncidentEngine | None) -> DynamicIncidentEngine:
    return engine if engine is not None else DynamicIncidentEngine()


def _account(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    fact_id: str,
    engine: DynamicIncidentEngine | None,
    now: datetime | None,
):
    return _engine(engine).execute_command(
        definition,
        state,
        action=None,
        command_cost=definition.scoring.command_cost,
        discovered_fact_ids=(fact_id,) if fact_id else (),
        now=now,
    )


def _result(
    output: str,
    success: bool,
    progress,
    *,
    editor: VirtualEditorAction | None = None,
) -> CommandExecutionResult:
    return CommandExecutionResult(
        output=output[:1000],
        success=success,
        editor=editor,
        progress=progress,
    )


def _resolve_path(state: SessionRuntimeState, path: str) -> str:
    home = state.virtual_rocky.home_directory
    if path == "~":
        return home
    if path.startswith("~/"):
        path = f"{home}/{path[2:]}"
    if not path.startswith("/"):
        path = posixpath.join(state.current_working_directory, path)
    return "/" + posixpath.normpath(path).lstrip("/")


def _is_denied(path: str) -> bool:
    return path == "/root" or path.startswith("/root/")


def _entry(state: SessionRuntimeState, path: str) -> VirtualFileEntry | None:
    return state.virtual_rocky.filesystem.get(path)


def _mode_string(entry: VirtualFileEntry) -> str:
    permissions = entry.mode[-3:]
    pieces = []
    for value in permissions:
        digit = int(value)
        pieces.append("r" if digit & 4 else "-")
        pieces.append("w" if digit & 2 else "-")
        pieces.append("x" if digit & 1 else "-")
    return ("d" if entry.kind == "directory" else "-") + "".join(pieces)


def _children(state: SessionRuntimeState, directory: str) -> list[VirtualFileEntry]:
    prefix = "/" if directory == "/" else f"{directory}/"
    return sorted(
        (
            entry
            for path, entry in state.virtual_rocky.filesystem.items()
            if path.startswith(prefix) and "/" not in path[len(prefix) :]
        ),
        key=lambda item: (item.kind != "directory", item.path),
    )


def _path_error(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    *,
    program: str,
    path: str,
    reason: str,
    engine: DynamicIncidentEngine | None,
    now: datetime | None,
) -> CommandExecutionResult:
    progress = _account(
        definition,
        state,
        fact_id=f"shell-error:{program}",
        engine=engine,
        now=now,
    )
    return _result(f"{program}: {path}: {reason}", False, progress)
