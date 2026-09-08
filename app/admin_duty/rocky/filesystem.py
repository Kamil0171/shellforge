import posixpath
from copy import deepcopy
from fnmatch import fnmatch

from app.admin_duty.domain.definition import ResourceType
from app.admin_duty.domain.runtime import SessionRuntimeState, VirtualFileEntry
from app.admin_duty.dynamic_commands import VirtualEditorAction
from app.admin_duty.rocky.common import (
    _account,
    _children,
    _entry,
    _is_denied,
    _mode_string,
    _path_error,
    _resolve_path,
    _result,
)


def shell_pwd(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    progress = _account(definition, state, fact_id="shell:pwd", engine=engine, now=now)
    return _result(state.current_working_directory, True, progress)


def shell_cd(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    if _is_denied(target):
        return _path_error(
            definition,
            state,
            program="cd",
            path=resource_id,
            reason="Permission denied",
            engine=engine,
            now=now,
        )
    entry = _entry(state, target)
    if entry is None:
        return _path_error(
            definition,
            state,
            program="cd",
            path=resource_id,
            reason="No such file or directory",
            engine=engine,
            now=now,
        )
    if entry.kind != "directory":
        return _path_error(
            definition,
            state,
            program="cd",
            path=resource_id,
            reason="Not a directory",
            engine=engine,
            now=now,
        )
    previous = state.current_working_directory
    state.current_working_directory = target
    try:
        progress = _account(
            definition, state, fact_id="shell:cd", engine=engine, now=now
        )
    except Exception:
        state.current_working_directory = previous
        raise
    return _result("", True, progress)


def shell_ls(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    if _is_denied(target):
        return _path_error(
            definition,
            state,
            program="ls",
            path=resource_id,
            reason="Permission denied",
            engine=engine,
            now=now,
        )
    entry = _entry(state, target)
    if entry is None:
        return _path_error(
            definition,
            state,
            program="ls",
            path=resource_id,
            reason="No such file or directory",
            engine=engine,
            now=now,
        )
    long_format = "-l" in arguments or "-la" in arguments or "-al" in arguments
    entries = _children(state, target) if entry.kind == "directory" else [entry]
    if not any("a" in flag for flag in arguments):
        entries = [
            item
            for item in entries
            if not posixpath.basename(item.path).startswith(".")
        ]
    if long_format:
        lines = [f"total {len(entries) * 4}"]
        if "-a" in arguments or "-la" in arguments or "-al" in arguments:
            lines.extend(
                (
                    "drwxr-xr-x  2 operator operator 4096 .",
                    "drwxr-xr-x  3 root root 4096 ..",
                )
            )
        for item in entries:
            size = (
                4096 if item.kind == "directory" else len(item.content.encode("utf-8"))
            )
            lines.append(
                f"{_mode_string(item)}  1 {item.owner:<8} {item.group:<8} {size:>5} {posixpath.basename(item.path)}"
            )
        output = "\n".join(lines)
    else:
        output = "  ".join(posixpath.basename(item.path) for item in entries)
    progress = _account(
        definition, state, fact_id="filesystem:list", engine=engine, now=now
    )
    return _result(output, True, progress)


def _read_file(definition, state, *, program, resource_id, engine, now):
    target = _resolve_path(state, resource_id)
    if _is_denied(target):
        return None, _path_error(
            definition,
            state,
            program=program,
            path=resource_id,
            reason="Permission denied",
            engine=engine,
            now=now,
        )
    entry = _entry(state, target)
    if entry is None:
        return None, _path_error(
            definition,
            state,
            program=program,
            path=resource_id,
            reason="No such file or directory",
            engine=engine,
            now=now,
        )
    if entry.kind != "file":
        return None, _path_error(
            definition,
            state,
            program=program,
            path=resource_id,
            reason="Is a directory",
            engine=engine,
            now=now,
        )
    return entry, None


def shell_cat(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    entry, error = _read_file(
        definition,
        state,
        program="cat",
        resource_id=resource_id,
        engine=engine,
        now=now,
    )
    if error:
        return error
    progress = _account(
        definition, state, fact_id="filesystem:read", engine=engine, now=now
    )
    return _result(entry.content.rstrip(), True, progress)


def _head_tail(definition, state, *, resource_id, arguments, engine, now, tail):
    program = "tail" if tail else "head"
    entry, error = _read_file(
        definition,
        state,
        program=program,
        resource_id=resource_id,
        engine=engine,
        now=now,
    )
    if error:
        return error
    count = int(arguments[0]) if arguments else 10
    lines = entry.content.splitlines()
    selected = lines[-count:] if tail else lines[:count]
    progress = _account(
        definition, state, fact_id=f"filesystem:{program}", engine=engine, now=now
    )
    return _result("\n".join(selected), True, progress)


def shell_head(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    return _head_tail(
        definition,
        state,
        resource_id=resource_id,
        arguments=arguments,
        engine=engine,
        now=now,
        tail=False,
    )


def shell_tail(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    return _head_tail(
        definition,
        state,
        resource_id=resource_id,
        arguments=arguments,
        engine=engine,
        now=now,
        tail=True,
    )


def shell_grep(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    pattern = arguments[0]
    entry, error = _read_file(
        definition,
        state,
        program="grep",
        resource_id=resource_id,
        engine=engine,
        now=now,
    )
    if error:
        return error
    matches = [line for line in entry.content.splitlines() if pattern in line]
    progress = _account(
        definition, state, fact_id="filesystem:grep", engine=engine, now=now
    )
    return _result("\n".join(matches) or "grep: no matches", bool(matches), progress)


def shell_path_stat(
    definition, state, *, resource_id, arguments=(), engine=None, now=None
):
    target = _resolve_path(state, resource_id)
    entry = _entry(state, target)
    if entry is None or _is_denied(target):
        reason = (
            "Permission denied" if _is_denied(target) else "No such file or directory"
        )
        return _path_error(
            definition,
            state,
            program="stat",
            path=resource_id,
            reason=reason,
            engine=engine,
            now=now,
        )
    size = 4096 if entry.kind == "directory" else len(entry.content.encode("utf-8"))
    output = f"  File: {target}\n  Size: {size}\tType: {entry.kind}\nAccess: ({entry.mode}/{_mode_string(entry)})  Uid: {entry.owner}  Gid: {entry.group}"
    progress = _account(
        definition, state, fact_id="filesystem:path-stat", engine=engine, now=now
    )
    return _result(output, True, progress)


def _mutation_result(definition, state, *, fact_id, output="", engine=None, now=None):
    progress = _account(definition, state, fact_id=fact_id, engine=engine, now=now)
    return _result(output, True, progress)


def shell_find(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    entry = _entry(state, target)
    if entry is None or _is_denied(target):
        reason = (
            "Permission denied" if _is_denied(target) else "No such file or directory"
        )
        return _path_error(
            definition,
            state,
            program="find",
            path=resource_id,
            reason=reason,
            engine=engine,
            now=now,
        )
    pattern = arguments[0] if arguments else "*"
    prefix = target if target == "/" else f"{target}/"
    matches = [
        path
        for path in sorted(state.virtual_rocky.filesystem)
        if (path == target or path.startswith(prefix))
        and fnmatch(posixpath.basename(path), pattern)
    ]
    progress = _account(
        definition, state, fact_id="filesystem:find", engine=engine, now=now
    )
    return _result("\n".join(matches), True, progress)


def _require_parent_directory(state: SessionRuntimeState, path: str) -> bool:
    parent = posixpath.dirname(path) or "/"
    entry = _entry(state, parent)
    return entry is not None and entry.kind == "directory" and not _is_denied(parent)


def shell_mkdir(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    if _entry(state, target) is not None:
        if "-p" in arguments and _entry(state, target).kind == "directory":
            return _mutation_result(
                definition, state, fact_id="filesystem:mkdir", engine=engine, now=now
            )
        return _path_error(
            definition,
            state,
            program="mkdir",
            path=resource_id,
            reason="File exists",
            engine=engine,
            now=now,
        )
    create_parents = "-p" in arguments
    missing = []
    candidate = target
    while _entry(state, candidate) is None and candidate != "/":
        missing.append(candidate)
        candidate = posixpath.dirname(candidate)
    if (
        _is_denied(target)
        or _entry(state, candidate).kind != "directory"
        or (not create_parents and not _require_parent_directory(state, target))
    ):
        return _path_error(
            definition,
            state,
            program="mkdir",
            path=resource_id,
            reason="No such file or directory",
            engine=engine,
            now=now,
        )
    for path in reversed(missing):
        state.virtual_rocky.filesystem[path] = VirtualFileEntry(
            path=path,
            kind="directory",
            mode="0755",
            owner=state.virtual_rocky.user,
            group=state.virtual_rocky.user,
        )
    return _mutation_result(
        definition, state, fact_id="filesystem:mkdir", engine=engine, now=now
    )


def shell_touch(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    existing = _entry(state, target)
    if existing is not None and existing.kind == "directory":
        return _path_error(
            definition,
            state,
            program="touch",
            path=resource_id,
            reason="Is a directory",
            engine=engine,
            now=now,
        )
    if _is_denied(target) or not _require_parent_directory(state, target):
        return _path_error(
            definition,
            state,
            program="touch",
            path=resource_id,
            reason="Permission denied",
            engine=engine,
            now=now,
        )
    if existing is None:
        state.virtual_rocky.filesystem[target] = VirtualFileEntry(
            path=target,
            kind="file",
            content="",
            mode="0644",
            owner=state.virtual_rocky.user,
            group=state.virtual_rocky.user,
        )
    return _mutation_result(
        definition, state, fact_id="filesystem:touch", engine=engine, now=now
    )


def shell_copy(
    definition, state, *, resource_id, arguments=(), engine=None, now=None, move=False
):
    source = _resolve_path(state, resource_id)
    destination = _resolve_path(state, arguments[0])
    entry = _entry(state, source)
    destination_entry = _entry(state, destination)
    if destination_entry and destination_entry.kind == "directory":
        destination = posixpath.join(destination, posixpath.basename(source))
    if _entry(state, destination) and _entry(state, destination).kind == "directory":
        return _path_error(
            definition,
            state,
            program="mv" if move else "cp",
            path=destination,
            reason="Is a directory",
            engine=engine,
            now=now,
        )
    if (
        entry is None
        or entry.kind != "file"
        or _is_denied(source)
        or _is_denied(destination)
        or source == destination
        or not _require_parent_directory(state, destination)
    ):
        return _path_error(
            definition,
            state,
            program="cp",
            path=resource_id,
            reason="Invalid source or destination",
            engine=engine,
            now=now,
        )
    state.virtual_rocky.filesystem[destination] = entry.model_copy(
        update={"path": destination}, deep=True
    )
    if any(
        path.startswith("/etc/systemd/system/") and path.endswith(".service")
        for path in (source, destination)
    ):
        state.virtual_rocky.daemon_reload_required = True
    if move:
        state.virtual_rocky.filesystem.pop(source)
    return _mutation_result(
        definition, state, fact_id="filesystem:copy", engine=engine, now=now
    )


def shell_move(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    return shell_copy(
        definition,
        state,
        resource_id=resource_id,
        arguments=arguments,
        engine=engine,
        now=now,
        move=True,
    )


def shell_remove(
    definition, state, *, resource_id, arguments=(), engine=None, now=None
):
    target = _resolve_path(state, resource_id)
    entry = _entry(state, target)
    recursive = "-r" in arguments or "-R" in arguments
    if (
        entry is None
        or _is_denied(target)
        or target in {"/", state.virtual_rocky.home_directory}
    ):
        return _path_error(
            definition,
            state,
            program="rm",
            path=resource_id,
            reason="Operation not permitted",
            engine=engine,
            now=now,
        )
    children = [
        path for path in state.virtual_rocky.filesystem if path.startswith(f"{target}/")
    ]
    if (
        state.current_working_directory == target
        or state.current_working_directory.startswith(target + "/")
    ):
        return _path_error(
            definition,
            state,
            program="rm",
            path=resource_id,
            reason="Katalog roboczy jest używany",
            engine=engine,
            now=now,
        )
    if entry.kind == "directory" and not recursive:
        return _path_error(
            definition,
            state,
            program="rm",
            path=resource_id,
            reason="Is a directory",
            engine=engine,
            now=now,
        )
    for path in (*children, target):
        state.virtual_rocky.filesystem.pop(path, None)
        if path.startswith("/etc/systemd/system/") and path.endswith(".service"):
            state.virtual_rocky.daemon_reload_required = True
    return _mutation_result(
        definition, state, fact_id="filesystem:remove", engine=engine, now=now
    )


def shell_rmdir(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    entry = _entry(state, target)
    if entry is None or entry.kind != "directory":
        return _path_error(
            definition,
            state,
            program="rmdir",
            path=resource_id,
            reason="Not a directory",
            engine=engine,
            now=now,
        )
    if any(path.startswith(f"{target}/") for path in state.virtual_rocky.filesystem):
        return _path_error(
            definition,
            state,
            program="rmdir",
            path=resource_id,
            reason="Directory not empty",
            engine=engine,
            now=now,
        )
    return shell_remove(
        definition,
        state,
        resource_id=resource_id,
        arguments=("-r",),
        engine=engine,
        now=now,
    )


def _sync_file_resource(
    state: SessionRuntimeState, path: str, *, mode=None, owner=None, group=None
) -> None:
    for resource in state.world_state.resources.values():
        if resource.resource_type is not ResourceType.FILE:
            continue
        service = next(
            (
                item
                for item in state.world_state.resources.values()
                if item.resource_type is ResourceType.SERVICE
                and item.attributes.get("executable_resource_id")
                == resource.resource_id
            ),
            None,
        )
        if service is None:
            continue
        app_name = str(
            service.attributes.get("service_name", "app.service")
        ).removesuffix(".service")
        expected = str(service.attributes.get("expected_exec_start", "app"))
        if path == f"/opt/{app_name}/{expected}":
            if mode is not None:
                resource.attributes["current_mode"] = mode
            if owner is not None:
                resource.attributes["owner"] = owner
            if group is not None:
                resource.attributes["group"] = group


def shell_chmod(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    entry = _entry(state, target)
    mode = arguments[0]
    if entry is None or _is_denied(target):
        return _path_error(
            definition,
            state,
            program="chmod",
            path=resource_id,
            reason="No such file or directory",
            engine=engine,
            now=now,
        )
    entry.mode = mode
    _sync_file_resource(state, target, mode=mode)
    return _mutation_result(
        definition, state, fact_id="filesystem:chmod", engine=engine, now=now
    )


def shell_chown(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    entry = _entry(state, target)
    if entry is None or _is_denied(target):
        return _path_error(
            definition,
            state,
            program="chown",
            path=resource_id,
            reason="No such file or directory",
            engine=engine,
            now=now,
        )
    owner, _, group = arguments[0].partition(":")
    entry.owner = owner
    entry.group = group or entry.group
    _sync_file_resource(state, target, owner=entry.owner, group=entry.group)
    return _mutation_result(
        definition, state, fact_id="filesystem:chown", engine=engine, now=now
    )


def shell_du(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    entry = _entry(state, target)
    if entry is None or _is_denied(target):
        return _path_error(
            definition,
            state,
            program="du",
            path=resource_id,
            reason="No such file or directory",
            engine=engine,
            now=now,
        )
    prefix = target if target == "/" else f"{target}/"
    size = sum(
        4096 if item.kind == "directory" else len(item.content.encode("utf-8"))
        for path, item in state.virtual_rocky.filesystem.items()
        if path == target or path.startswith(prefix)
    )
    display = (
        f"{max(4, (size + 1023) // 1024)}K"
        if "-h" in arguments
        else str((size + 1023) // 1024)
    )
    progress = _account(
        definition, state, fact_id="filesystem:du", engine=engine, now=now
    )
    return _result(f"{display}\t{target}", True, progress)


def shell_nano(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target = _resolve_path(state, resource_id)
    entry, error = _read_file(
        definition,
        state,
        program="nano",
        resource_id=resource_id,
        engine=engine,
        now=now,
    )
    if error:
        return error
    progress = _account(
        definition, state, fact_id="filesystem:edit-open", engine=engine, now=now
    )
    return _result(
        f"Otwarto {target} w bezpiecznym edytorze.",
        True,
        progress,
        editor=VirtualEditorAction(path=target, content=entry.content),
    )


def save_virtual_file(
    definition, state, *, path: str, content: str, engine=None, now=None
):
    target = _resolve_path(state, path)
    entry = _entry(state, target)
    if entry is None or entry.kind != "file" or _is_denied(target):
        return _path_error(
            definition,
            state,
            program="nano",
            path=path,
            reason="File is not editable",
            engine=engine,
            now=now,
        )
    if len(content.encode("utf-8")) > 32768:
        return _path_error(
            definition,
            state,
            program="nano",
            path=path,
            reason="File is too large",
            engine=engine,
            now=now,
        )
    previous = deepcopy(entry)
    entry.content = content
    if target.startswith("/etc/systemd/system/") and target.endswith(".service"):
        state.virtual_rocky.daemon_reload_required = True
    try:
        return _mutation_result(
            definition,
            state,
            fact_id="filesystem:edit-save",
            output=f"Zapisano {target}.",
            engine=engine,
            now=now,
        )
    except Exception:
        state.virtual_rocky.filesystem[target] = previous
        raise
