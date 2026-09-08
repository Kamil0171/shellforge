from app.admin_duty.domain.definition import ResourceType
from app.admin_duty.domain.runtime import RuntimeResource, VirtualFileEntry
from app.admin_duty.rocky.system import finish


def package_command(
    definition, state, *, resource_id, arguments=(), engine=None, now=None
):
    packages = state.virtual_rocky.packages
    action = arguments[0]
    names = arguments[1:]
    if action in {"install", "remove", "update"}:
        targets = names or tuple(packages.installed_packages)
        for name in targets:
            if action == "remove" and name not in packages.installed_packages:
                return finish(
                    definition,
                    state,
                    f"Pakiet {name} nie jest zainstalowany.",
                    False,
                    engine=engine,
                    now=now,
                )
            if action == "update" and name not in packages.installed_packages:
                return finish(
                    definition,
                    state,
                    f"Pakiet {name} nie jest zainstalowany.",
                    False,
                    engine=engine,
                    now=now,
                )
            if action != "remove" and (
                name not in packages.available_packages
                or packages.available_packages[name].repository
                not in packages.enabled_repositories
            ):
                return finish(
                    definition,
                    state,
                    f"Nieznany pakiet: {name}. Brak pasującego pakietu w aktywnych repozytoriach.",
                    False,
                    engine=engine,
                    now=now,
                )
        lines = []
        for name in targets:
            package = (
                packages.installed_packages.get(name)
                if action == "remove"
                else packages.available_packages[name]
            )
            if action == "remove":
                packages.installed_packages.pop(name, None)
                if name == "nginx":
                    state.world_state.resources.pop("service-nginx", None)
                    state.virtual_rocky.filesystem.pop(
                        "/etc/systemd/system/nginx.service", None
                    )
                    state.virtual_rocky.filesystem.pop("/usr/sbin/nginx", None)
                    state.virtual_rocky.systemd_unit_cache.pop("nginx.service", None)
                    state.virtual_rocky.systemd_enabled_units.discard("nginx.service")
                    state.virtual_rocky.processes = {
                        pid: item
                        for pid, item in state.virtual_rocky.processes.items()
                        if item.service_resource_id != "service-nginx"
                    }
            else:
                packages.installed_packages[name] = packages.available_packages[
                    name
                ].model_copy(deep=True)
                if name == "nginx":
                    rocky = state.virtual_rocky
                    for path in ("/usr", "/usr/sbin"):
                        rocky.filesystem.setdefault(
                            path,
                            VirtualFileEntry(
                                path=path,
                                kind="directory",
                                mode="0755",
                                owner="root",
                                group="root",
                            ),
                        )
                    rocky.filesystem.setdefault(
                        "/usr/sbin/nginx",
                        VirtualFileEntry(
                            path="/usr/sbin/nginx",
                            kind="file",
                            content="ELF virtual executable",
                            mode="0755",
                            owner="root",
                            group="root",
                        ),
                    )
                    unit = "[Service]\nExecStart=/usr/sbin/nginx\n"
                    rocky.filesystem.setdefault(
                        "/etc/systemd/system/nginx.service",
                        VirtualFileEntry(
                            path="/etc/systemd/system/nginx.service",
                            kind="file",
                            content=unit,
                            mode="0644",
                            owner="root",
                            group="root",
                        ),
                    )
                    rocky.systemd_unit_cache.setdefault("nginx.service", unit)
                    state.world_state.resources.setdefault(
                        "service-nginx",
                        RuntimeResource(
                            resource_id="service-nginx",
                            resource_type=ResourceType.SERVICE,
                            current_state="stopped",
                            attributes={
                                "manager": "systemd",
                                "service_name": "nginx.service",
                                "port": 80,
                                "required_package": "nginx",
                            },
                        ),
                    )
            lines.append(f"{name}.x86_64 {package.version}")
        packages.cache_clean = False
        return finish(
            definition,
            state,
            f"Transakcja {action}:\n" + "\n".join(lines) + "\nUkończono!",
            engine=engine,
            now=now,
        )
    if action == "repolist":
        output = "repo id         repo name\n" + "\n".join(
            f"{name:16} Rocky Linux 9 - {name}"
            for name in sorted(packages.enabled_repositories)
        )
    elif action == "clean":
        packages.cache_clean = True
        output = "Usunięto wirtualną pamięć podręczną metadanych."
    else:
        catalog = (
            packages.installed_packages
            if names == ("installed",)
            else packages.available_packages
        )
        if action == "info":
            package = catalog.get(names[0])
            if package is None:
                return finish(
                    definition,
                    state,
                    "Nie znaleziono pakietu.",
                    False,
                    engine=engine,
                    now=now,
                )
            output = f"Name : {package.name}\nVersion : {package.version}\nRepository : {package.repository}\nSummary : {package.summary}"
        else:
            output = "\n".join(
                f"{p.name}.x86_64 {p.version} {p.repository}" for p in catalog.values()
            )
    return finish(definition, state, output, engine=engine, now=now)


def rpm(definition, state, *, resource_id, arguments=(), engine=None, now=None):
    packages = state.virtual_rocky.packages.installed_packages
    selected = (
        list(packages.values())
        if arguments[0] == "-qa"
        else [packages.get(resource_id)]
    )
    if not all(selected):
        return finish(
            definition,
            state,
            f"package {resource_id} is not installed",
            False,
            engine=engine,
            now=now,
        )
    output = "\n".join(
        f"{p.name}-{p.version}.x86_64"
        if arguments[0] != "-qi"
        else f"Name : {p.name}\nVersion : {p.version}\nSummary : {p.summary}"
        for p in selected
    )
    return finish(definition, state, output, engine=engine, now=now)


HANDLERS = {"packages.command": package_command, "packages.rpm": rpm}
