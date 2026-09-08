from app.admin_duty.rocky.system import finish


def ssh(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    target_id = next(
        (
            host_id
            for host_id, runtime in state.host_runtimes.items()
            if resource_id in {host_id, runtime.hostname}
        ),
        None,
    )
    if target_id is None:
        return finish(
            definition,
            state,
            f"ssh: Nieznany host {resource_id}.",
            False,
            engine=engine,
            now=now,
        )

    previous_id = state.active_host_id
    state.host_working_directories[previous_id] = state.current_working_directory
    state.active_host_id = target_id
    state.current_working_directory = state.host_working_directories.get(
        target_id,
        state.virtual_rocky.home_directory,
    )
    state.host_working_directories.setdefault(
        target_id,
        state.current_working_directory,
    )
    return finish(
        definition,
        state,
        f"Połączono z wirtualnym hostem {state.virtual_rocky.hostname}.",
        engine=engine,
        now=now,
        fact_id=f"host-accessed:{target_id}",
    )


HANDLERS = {"remote.ssh": ssh}
