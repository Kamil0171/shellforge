from app.admin_duty.components.maps import get_map_template
from app.admin_duty.domain.definition import (
    CapabilitySet,
    CompletionCondition,
    ComponentReference,
    ComponentType,
    ConditionOperator,
    ConfigurationRequirement,
    DataField,
    DependencyType,
    FaultInstance,
    FaultSeverity,
    GenerationSource,
    Hint,
    IncidentPresentation,
    InitialWorldState,
    InterfaceCapability,
    NetworkProtocol,
    Objective,
    ObjectiveType,
    PackageRequirement,
    PostIncidentDefinition,
    ResourceType,
    ScoringRules,
    ServiceDependency,
    SolutionStep,
    Symptom,
    SymptomPropagationRule,
    SymptomVisibility,
    WorldResource,
)
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.generation import GeneratedIncidentDraft
from app.admin_duty.rocky.registry import HANDLERS

LEGACY_MEDIUM_SCENARIO_CATEGORIES = (
    "dependency-firewall-blocked",
    "dependency-package-missing",
    "selinux-context-invalid",
    "networkmanager-dns-invalid",
    "external-firewall-mismatch",
)

EXPANDED_MEDIUM_SCENARIO_CATEGORIES = (
    "service-config-permission-denied",
    "systemd-stale-unit-config",
    "service-config-invalid",
    "dependency-dns-name-mismatch",
    "dependency-port-mismatch",
    "selinux-proxy-context-invalid",
    "networkmanager-connection-inactive",
)

MEDIUM_SCENARIO_CATEGORIES = (
    *LEGACY_MEDIUM_SCENARIO_CATEGORIES,
    *EXPANDED_MEDIUM_SCENARIO_CATEGORIES,
)


def _fields(**values) -> tuple[DataField, ...]:
    return tuple(DataField(key=key, value=value) for key, value in values.items())


def _host(
    resource_id,
    hostname,
    address,
    role,
    *,
    installed_packages=(),
    firewall_services=("ssh",),
    firewall_ports=(),
    dns_servers=("10.24.8.53",),
):
    return WorldResource(
        resource_id=resource_id,
        resource_type=ResourceType.HOST,
        state="running",
        attributes=_fields(
            hostname=hostname,
            address=address,
            role=role,
            connection="System-ens192",
            installed_packages=tuple(installed_packages),
            firewall_runtime_services=tuple(firewall_services),
            firewall_permanent_services=tuple(firewall_services),
            firewall_runtime_ports=tuple(firewall_ports),
            firewall_permanent_ports=tuple(firewall_ports),
            dns_servers=tuple(dns_servers),
            expected_dns_servers=("10.24.8.53",),
        ),
    )


def _service(
    resource_id,
    host_id,
    service_name,
    port,
    *,
    state="running",
    unhealthy_status_code=503,
    required_package=None,
    required_dns_name=None,
    current_selinux_context=None,
):
    app_name = service_name.removesuffix(".service")
    service_kind = {
        "edge-proxy.service": "reverse-proxy",
        "orders-api.service": "web-api",
        "database.service": "database",
    }.get(service_name, "systemd-service")
    executable_id = f"file-{resource_id.removeprefix('service-')}-binary"
    attributes = {
        "manager": "systemd",
        "service_name": service_name,
        "port": port,
        "configured_exec_start": app_name,
        "expected_exec_start": app_name,
        "executable_resource_id": executable_id,
        "unhealthy_status_code": unhealthy_status_code,
        "service_kind": service_kind,
    }
    if required_package:
        attributes["required_package"] = required_package
    if required_dns_name:
        attributes["required_dns_name"] = required_dns_name
    if current_selinux_context:
        attributes["current_selinux_context"] = current_selinux_context
        attributes["expected_selinux_context"] = "system_u:object_r:bin_t:s0"
    service = WorldResource(
        resource_id=resource_id,
        resource_type=ResourceType.SERVICE,
        state=state,
        parent_id=host_id,
        dependencies=(executable_id,),
        attributes=_fields(**attributes),
    )
    executable = WorldResource(
        resource_id=executable_id,
        resource_type=ResourceType.FILE,
        state="present",
        parent_id=host_id,
        attributes=_fields(current_mode="0755", expected_mode="0755", owner="app"),
    )
    return service, executable


def _dependency(
    dependency_id,
    source_host,
    source,
    target,
    host,
    protocol,
    port,
    dependency_type=DependencyType.SERVICE,
):
    return ServiceDependency(
        dependency_id=dependency_id,
        source_host_id=source_host,
        source_service_id=source,
        target_service_id=target,
        target_host_id=host,
        dependency_type=dependency_type,
        protocol=protocol,
        port=port,
    )


def _step(order, capability, command, purpose, *, expected_success=True):
    return SolutionStep(
        order=order,
        capability_id=capability,
        input=command,
        purpose=purpose,
        expected_success=expected_success,
    )


def _map_snapshot(initial_host_id, secondary_host_id):
    template = get_map_template("web-operations-room")
    interactions = tuple(
        interaction.model_copy(
            update={
                "interaction_id": f"{interaction.capability_id}-{initial_host_id}",
                "target_resource_id": (
                    initial_host_id
                    if interaction.capability_id in {"terminal", "monitoring"}
                    else secondary_host_id
                ),
            }
        )
        for interaction in template.snapshot.interactions
    )
    return template.snapshot.model_copy(update={"interactions": interactions})


def _components(category, *, version="3.0"):
    return (
        ComponentReference(
            component_type=ComponentType.MAP,
            component_id="web-operations-room",
            version="1.0",
        ),
        ComponentReference(
            component_type=ComponentType.ENVIRONMENT,
            component_id=f"medium-{category}",
            version=version,
        ),
        ComponentReference(
            component_type=ComponentType.FAULT,
            component_id=category,
            version=version,
        ),
        ComponentReference(
            component_type=ComponentType.SYMPTOM,
            component_id=f"symptom-{category}",
            version=version,
        ),
        ComponentReference(
            component_type=ComponentType.OBJECTIVE,
            component_id="objectives-medium-service-chain",
            version="3.0",
        ),
        ComponentReference(
            component_type=ComponentType.CAPABILITY,
            component_id="capabilities-virtual-rocky-v3",
            version="3.0",
        ),
        ComponentReference(
            component_type=ComponentType.SCORING_POLICY,
            component_id="scoring-standard",
            version="3.0",
        ),
    )


def build_medium_draft(category: str, *, seed: int) -> GeneratedIncidentDraft:
    if category not in MEDIUM_SCENARIO_CATEGORIES:
        raise ValueError(f"Nieznana kategoria MEDIUM: {category}.")
    if category in EXPANDED_MEDIUM_SCENARIO_CATEGORIES:
        return _build_expanded_medium_draft(category, seed=seed)

    api_state = "running"
    api_context = None
    api_dns_name = None
    app_packages = ("python3-psycopg2",)
    app_dns = ("10.24.8.53",)
    database_ports = ("5432/tcp",)
    edge_services = ("ssh", "http")
    edge_port = 80
    initial_host_id = "host-edge-01"
    fault_target = "service-api"
    symptom_state = "http-502"
    root_cause = "Warstwa aplikacji utraciła sprawną zależność infrastrukturalną."
    repair_capabilities = ("systemd.restart",)

    if category == "dependency-firewall-blocked":
        database_ports = ()
        fault_target = "host-data-01"
        root_cause = "Firewalld na hoście data-01 blokował wymagane połączenie TCP do portu 5432."
        repair_capabilities = ("firewalld.command",)
    elif category == "dependency-package-missing":
        api_state = "failed"
        app_packages = ()
        root_cause = "Po wdrożeniu na app-01 brakowało pakietu python3-psycopg2 wymaganego przez API."
        repair_capabilities = ("packages.command", "systemd.restart")
    elif category == "selinux-context-invalid":
        api_state = "failed"
        api_context = "unconfined_u:object_r:default_t:s0"
        root_cause = "Pliki API miały nieprawidłowy kontekst SELinux, który blokował uruchomienie procesu."
        repair_capabilities = ("selinux.restorecon", "systemd.restart")
    elif category == "networkmanager-dns-invalid":
        app_dns = ()
        api_dns_name = "database.internal"
        fault_target = "host-app-01"
        root_cause = "Aktywne połączenie NetworkManager na app-01 nie miało skonfigurowanego serwera DNS."
        repair_capabilities = ("networkmanager.command",)
    else:
        edge_services = ("ssh",)
        edge_port = 443
        initial_host_id = "host-client-01"
        fault_target = "host-edge-01"
        symptom_state = "unreachable"
        root_cause = "Publiczny ruch HTTPS blokowała rozbieżność między portem reverse proxy a usługami firewalld."
        repair_capabilities = ("firewalld.command",)

    hosts = [
        _host(
            "host-edge-01",
            "edge-01",
            "10.24.8.10/24",
            "reverse proxy",
            firewall_services=edge_services,
        ),
        _host(
            "host-app-01",
            "app-01",
            "10.24.8.20/24",
            "application",
            installed_packages=app_packages,
            firewall_ports=("8080/tcp",),
            dns_servers=app_dns,
        ),
        _host(
            "host-data-01",
            "data-01",
            "10.24.8.30/24",
            "database",
            firewall_ports=database_ports,
        ),
    ]
    if category == "networkmanager-dns-invalid":
        hosts.append(
            _host(
                "host-dns-01",
                "dns-01",
                "10.24.8.53/24",
                "dns",
                firewall_services=("ssh", "dns"),
            )
        )
    if category == "external-firewall-mismatch":
        hosts.append(
            _host(
                "host-client-01",
                "client-01",
                "10.24.8.40/24",
                "external probe",
            )
        )

    proxy = _service(
        "service-proxy",
        "host-edge-01",
        "edge-proxy.service",
        edge_port,
        unhealthy_status_code=502,
    )
    api = _service(
        "service-api",
        "host-app-01",
        "orders-api.service",
        8080,
        state=api_state,
        required_package="python3-psycopg2",
        required_dns_name=api_dns_name,
        current_selinux_context=api_context,
    )
    database = _service(
        "service-database",
        "host-data-01",
        "database.service",
        5432,
    )
    resources = [*hosts, *proxy, *api, *database]
    dependencies = [
        _dependency(
            "dep-proxy-api",
            "host-edge-01",
            "service-proxy",
            "service-api",
            "host-app-01",
            NetworkProtocol.HTTP,
            8080,
        ),
        _dependency(
            "dep-api-database",
            "host-app-01",
            "service-api",
            "service-database",
            "host-data-01",
            NetworkProtocol.TCP,
            5432,
            DependencyType.NETWORK,
        ),
    ]
    propagation_dependency = "dep-proxy-api"
    restore_resource = "service-proxy"

    if category == "networkmanager-dns-invalid":
        dns_service = _service(
            "service-dns",
            "host-dns-01",
            "named.service",
            53,
        )
        resources.extend(dns_service)
        dependencies.append(
            _dependency(
                "dep-api-dns",
                "host-app-01",
                "service-api",
                "service-dns",
                "host-dns-01",
                NetworkProtocol.UDP,
                53,
                DependencyType.NETWORK,
            )
        )
    if category == "external-firewall-mismatch":
        external = _service(
            "service-external-check",
            "host-client-01",
            "external-check.service",
            9090,
        )
        resources.extend(external)
        dependencies.append(
            _dependency(
                "dep-external-proxy",
                "host-client-01",
                "service-external-check",
                "service-proxy",
                "host-edge-01",
                NetworkProtocol.HTTPS,
                443,
                DependencyType.NETWORK,
            )
        )
        propagation_dependency = "dep-external-proxy"
        restore_resource = "service-external-check"

    config_file = WorldResource(
        resource_id="file-api-config",
        resource_type=ResourceType.FILE,
        state="present",
        parent_id="host-app-01",
        attributes=_fields(
            path="/opt/orders-api/app.conf",
            content="DATABASE_HOST=database.internal\n",
            expected_content="DATABASE_HOST=database.internal\n",
            current_mode="0640",
            owner="app",
        ),
    )
    endpoint = WorldResource(
        resource_id="endpoint-portal",
        resource_type=ResourceType.ENDPOINT,
        state="healthy",
        dependencies=("service-proxy",),
        attributes=_fields(url="https://portal.internal"),
    )
    domain = WorldResource(
        resource_id="domain-portal",
        resource_type=ResourceType.DOMAIN,
        state="present",
        attributes=_fields(name="portal.internal", address="10.24.8.10"),
    )
    api_domain = WorldResource(
        resource_id="domain-api",
        resource_type=ResourceType.DOMAIN,
        state="present",
        attributes=_fields(name="api.internal", address="10.24.8.20"),
    )
    database_domain = WorldResource(
        resource_id="domain-database",
        resource_type=ResourceType.DOMAIN,
        state="present",
        attributes=_fields(name="database.internal", address="10.24.8.30"),
    )
    resources.extend((config_file, endpoint, domain, api_domain, database_domain))

    solutions = {
        "dependency-firewall-blocked": (
            ("network.curl", "curl http://portal.internal", True),
            ("systemd.status", "systemctl status edge-proxy", True),
            ("network.curl", "curl http://api.internal:8080", True),
            ("remote.ssh", "ssh data-01", True),
            ("firewalld.command", "firewall-cmd --list-all", True),
            (
                "firewalld.command",
                "firewall-cmd --permanent --add-port=5432/tcp",
                True,
            ),
            ("firewalld.command", "firewall-cmd --reload", True),
            ("remote.ssh", "ssh edge-01", True),
            ("network.curl", "curl http://portal.internal", True),
        ),
        "dependency-package-missing": (
            ("network.curl", "curl http://portal.internal", True),
            ("remote.ssh", "ssh app-01", True),
            ("systemd.status", "systemctl status orders-api", True),
            ("journal.read", "journalctl -u orders-api", True),
            ("packages.rpm", "rpm -q python3-psycopg2", False),
            ("packages.command", "dnf install -y python3-psycopg2", True),
            ("systemd.restart", "systemctl restart orders-api", True),
            ("remote.ssh", "ssh edge-01", True),
            ("network.curl", "curl http://portal.internal", True),
        ),
        "selinux-context-invalid": (
            ("network.curl", "curl http://portal.internal", True),
            ("remote.ssh", "ssh app-01", True),
            ("systemd.status", "systemctl status orders-api", True),
            ("journal.read", "journalctl -u orders-api", True),
            ("selinux.getenforce", "getenforce", True),
            ("selinux.semanage", "semanage fcontext -l", True),
            ("selinux.restorecon", "restorecon -R /opt/orders-api", True),
            ("systemd.restart", "systemctl restart orders-api", True),
            ("remote.ssh", "ssh edge-01", True),
            ("network.curl", "curl http://portal.internal", True),
        ),
        "networkmanager-dns-invalid": (
            ("network.curl", "curl http://portal.internal", True),
            ("remote.ssh", "ssh app-01", True),
            ("networkmanager.command", "nmcli connection show", True),
            ("network.dig", "dig database.internal", False),
            (
                "networkmanager.command",
                "nmcli connection modify System-ens192 ipv4.dns 10.24.8.53",
                True,
            ),
            ("network.dig", "dig database.internal", True),
            ("remote.ssh", "ssh edge-01", True),
            ("network.curl", "curl http://portal.internal", True),
        ),
        "external-firewall-mismatch": (
            ("network.curl", "curl https://portal.internal", False),
            ("remote.ssh", "ssh edge-01", True),
            ("systemd.status", "systemctl status edge-proxy", True),
            ("network.listeners", "ss -lntp", True),
            ("firewalld.command", "firewall-cmd --list-all", True),
            (
                "firewalld.command",
                "firewall-cmd --permanent --add-service=https",
                True,
            ),
            ("firewalld.command", "firewall-cmd --reload", True),
            ("remote.ssh", "ssh client-01", True),
            ("network.curl", "curl https://portal.internal", True),
        ),
    }
    solution = tuple(
        _step(
            order,
            capability,
            command,
            "Wykonaj kontrolowany krok diagnostyki lub naprawy.",
            expected_success=expected_success,
        )
        for order, (capability, command, expected_success) in enumerate(
            solutions[category], 1
        )
    )
    root_endpoint_port = 443 if category == "external-firewall-mismatch" else 80
    objectives = (
        Objective(
            objective_id="confirm-public-symptom",
            label="Potwierdź symptom widoczny dla użytkowników",
            required=False,
            order=1,
            objective_type=ObjectiveType.CONFIRM_SYMPTOM,
            completion_fact_ids=(
                f"endpoint-checked:host-edge-01:{root_endpoint_port}",
            ),
        ),
        Objective(
            objective_id="inspect-service-chain",
            label="Sprawdź stan usług uczestniczących w obsłudze żądania",
            required=False,
            order=2,
            objective_type=ObjectiveType.INSPECT_SERVICE,
            completion_fact_ids=("service-status-inspected:service-proxy",),
        ),
        Objective(
            objective_id="restore-service-chain",
            label="Przywróć komunikację między warstwami aplikacji",
            order=3,
            objective_type=ObjectiveType.RESTORE_DEPENDENCY,
            completion_condition=CompletionCondition(
                resource_id=restore_resource,
                field="attributes.public_health",
                operator=ConditionOperator.EQUALS,
                expected="healthy",
            ),
        ),
        Objective(
            objective_id="verify-end-to-end",
            label="Potwierdź poprawne działanie usługi end-to-end",
            order=4,
            objective_type=ObjectiveType.VERIFY_END_TO_END,
            completion_condition=CompletionCondition(
                resource_id="endpoint-portal",
                field="current_state",
                operator=ConditionOperator.EQUALS,
                expected="healthy",
            ),
            completion_fact_ids=(
                f"endpoint-healthy:host-edge-01:{root_endpoint_port}",
            ),
        ),
    )
    fault = FaultInstance(
        fault_id=f"fault-{category}",
        fault_type=category.replace("-", "_"),
        version="3.0",
        target_resource_id=fault_target,
        severity=FaultSeverity.MEDIUM,
        parameters=_fields(
            component_id=category,
            forbidden_public_terms=(
                "python3-psycopg2",
                "restorecon",
                "ipv4.dns",
                "5432/tcp",
                "add-service=https",
            ),
        ),
    )
    return GeneratedIncidentDraft(
        draft_id=f"medium-{category}-{seed}",
        schema_version="3.0",
        difficulty=DifficultyLevel.MEDIUM,
        generator_id="shellforge.deterministic",
        generator_version="3.0",
        generation_source=GenerationSource.DETERMINISTIC,
        seed=seed,
        components=_components(category),
        presentation=IncidentPresentation(
            title="Incydent w wielowarstwowej aplikacji",
            organization="Northstar Commerce",
            environment_label="Środowisko wielousługowe",
            briefing=(
                "Monitoring zgłasza niedostępność lub degradację publicznej aplikacji. "
                "Warstwa brzegowa, API i usługi zaplecza działają na oddzielnych hostach."
            ),
            main_objective="Przywróć poprawne działanie całej ścieżki żądania.",
            ticket_reference=f"MED-{seed % 100000:05d}",
            tags=("medium", "dependencies", "diagnostyka"),
            estimated_time_minutes=25,
        ),
        initial_world_state=InitialWorldState(
            environment_id=f"medium-{category}",
            environment_version="3.0",
            map=_map_snapshot(initial_host_id, "host-data-01"),
            resources=tuple(resources),
        ),
        faults=(fault,),
        symptoms=(
            Symptom(
                symptom_id=f"symptom-{category}",
                symptom_type="public_service_degraded",
                source_resource_id="endpoint-portal",
                visibility=SymptomVisibility.MONITORING,
                data=_fields(observed_state=symptom_state),
            ),
        ),
        objectives=objectives,
        capabilities=CapabilitySet(
            interfaces=(
                InterfaceCapability.TERMINAL,
                InterfaceCapability.FILE_EDITOR,
                InterfaceCapability.MONITORING,
            ),
            command_capability_ids=tuple(HANDLERS),
        ),
        scoring=ScoringRules(
            policy_id="scoring.standard",
            initial_score=1400,
            command_cost=8,
            solution_penalty=450,
            solution_score_cap=650,
        ),
        hints=(
            Hint(
                order=1,
                text="Ustal, na której warstwie ścieżka żądania przestaje działać.",
                cost=45,
            ),
            Hint(
                order=2,
                text="Porównaj stan usługi z jej zależnościami sieciowymi i systemowymi.",
                cost=70,
            ),
        ),
        solution=solution,
        service_dependencies=tuple(dependencies),
        package_requirements=(
            PackageRequirement(
                requirement_id="package-api-database-driver",
                service_id="service-api",
                host_id="host-app-01",
                package_name="python3-psycopg2",
            ),
        ),
        configuration_requirements=(
            ConfigurationRequirement(
                requirement_id="config-api-database",
                service_id="service-api",
                host_id="host-app-01",
                file_resource_id="file-api-config",
            ),
        ),
        symptom_propagation=(
            SymptomPropagationRule(
                rule_id="propagate-public-health",
                dependency_id=propagation_dependency,
                affected_resource_id="endpoint-portal",
                unhealthy_state=symptom_state,
                healthy_state="healthy",
            ),
        ),
        post_incident=PostIncidentDefinition(
            root_cause=root_cause,
            affected_service_ids=("service-proxy", "service-api"),
            repair_capability_ids=repair_capabilities,
        ),
    )


def _resource_with(
    resource: WorldResource, *, state=None, **attributes
) -> WorldResource:
    values = {field.key: field.value for field in resource.attributes}
    values.update(attributes)
    updates = {"attributes": _fields(**values)}
    if state is not None:
        updates["state"] = state
    return resource.model_copy(update=updates)


def _medium_editor_step(
    order: int, command: str, content: str, purpose: str
) -> SolutionStep:
    return SolutionStep(
        order=order,
        capability_id="filesystem.edit",
        input=command,
        purpose=purpose,
        parameters=(DataField(key="content", value=content),),
    )


def _healthy_api_unit() -> str:
    return (
        "[Unit]\nDescription=Usługa aplikacyjna orders-api\n"
        "After=network-online.target\n\n[Service]\nType=simple\n"
        "ExecStart=/opt/orders-api/orders-api\nUser=app\nRestart=on-failure\n\n"
        "[Install]\nWantedBy=multi-user.target\n"
    )


def _build_expanded_medium_draft(category: str, *, seed: int) -> GeneratedIncidentDraft:
    base = build_medium_draft("dependency-firewall-blocked", seed=seed)
    resources = []
    for resource in base.initial_world_state.resources:
        if resource.resource_id == "host-data-01":
            resource = _resource_with(
                resource,
                firewall_runtime_ports=("5432/tcp",),
                firewall_permanent_ports=("5432/tcp",),
            )
        resources.append(resource)

    resource_by_id = {resource.resource_id: resource for resource in resources}

    def replace(resource_id: str, resource: WorldResource) -> None:
        resource_by_id[resource_id] = resource

    proxy_config = WorldResource(
        resource_id="file-proxy-config",
        resource_type=ResourceType.FILE,
        state="present",
        parent_id="host-edge-01",
        attributes=_fields(
            path="/opt/edge-proxy/upstream.conf",
            content="UPSTREAM_PORT=8080\n",
            expected_content="UPSTREAM_PORT=8080\n",
            current_mode="0640",
            owner="app",
        ),
    )
    configuration_requirements = base.configuration_requirements
    root_cause = "Warstwa aplikacyjna miała niespójną konfigurację operacyjną."
    repair_capabilities: tuple[str, ...] = ("filesystem.edit", "systemd.restart")
    organization = "Horyzont Danych"
    environment_label = "Platforma obsługi zamówień"
    title = "Degradacja ścieżki aplikacyjnej"
    briefing = (
        "Monitoring wykrył degradację publicznej usługi. Procesy i zależności działają "
        "na oddzielnych hostach, dlatego potrzebna jest diagnostyka całej ścieżki."
    )
    fault_target = "service-api"
    forbidden_terms: tuple[str, ...] = ()

    if category == "service-config-permission-denied":
        config = _resource_with(
            resource_by_id["file-api-config"], current_mode="0600", owner="root"
        )
        replace("file-api-config", config)
        replace(
            "service-api",
            _resource_with(
                resource_by_id["service-api"],
                journal_clue="Nie można odczytać pliku /opt/orders-api/app.conf.",
            ),
        )
        configuration_requirements = (
            base.configuration_requirements[0].model_copy(
                update={"expected_mode": "0640", "expected_owner": "app"}
            ),
        )
        solution = (
            _step(
                1,
                "network.curl",
                "curl http://portal.internal",
                "Potwierdź degradację.",
            ),
            _step(2, "remote.ssh", "ssh app-01", "Przejdź na host aplikacji."),
            _step(
                3,
                "systemd.status",
                "systemctl status orders-api",
                "Sprawdź proces API.",
            ),
            _step(
                4,
                "journal.read",
                "journalctl -u orders-api",
                "Odczytaj komunikat o konfiguracji.",
            ),
            _step(
                5,
                "filesystem.path-stat",
                "stat /opt/orders-api/app.conf",
                "Sprawdź właściciela i tryb pliku.",
            ),
            _step(
                6,
                "filesystem.chmod",
                "chmod 640 /opt/orders-api/app.conf",
                "Przywróć bezpieczny tryb pliku.",
            ),
            _step(
                7,
                "filesystem.chown",
                "chown app:app /opt/orders-api/app.conf",
                "Przywróć właściciela konfiguracji.",
            ),
            _step(
                8,
                "systemd.restart",
                "systemctl restart orders-api",
                "Uruchom ponownie API.",
            ),
            _step(9, "remote.ssh", "ssh edge-01", "Wróć na host brzegowy."),
            _step(
                10,
                "network.curl",
                "curl http://portal.internal",
                "Zweryfikuj pełną ścieżkę.",
            ),
        )
        root_cause = (
            "Plik konfiguracji API miał właściciela root i tryb 0600, więc proces działający "
            "jako app nie mógł go odczytać."
        )
        repair_capabilities = (
            "filesystem.chmod",
            "filesystem.chown",
            "systemd.restart",
        )
        organization = "Srebrny Szlak"
        environment_label = "System rozliczeń przesyłek"
        title = "API bez dostępu do konfiguracji"
        fault_target = "file-api-config"
        forbidden_terms = ("0600", "chown app:app", "chmod 640")
    elif category == "systemd-stale-unit-config":
        api = _resource_with(
            resource_by_id["service-api"],
            state="failed",
            configured_exec_start="orders-api-old",
            journal_clue="Jednostka wskazuje nieaktualny plik wykonywalny po zmianie wydania.",
        )
        replace("service-api", api)
        solution = (
            _step(
                1,
                "network.curl",
                "curl http://portal.internal",
                "Potwierdź degradację.",
            ),
            _step(2, "remote.ssh", "ssh app-01", "Przejdź na host aplikacji."),
            _step(
                3,
                "systemd.status",
                "systemctl status orders-api",
                "Sprawdź stan jednostki.",
            ),
            _step(
                4, "journal.read", "journalctl -u orders-api", "Odczytaj błąd startu."
            ),
            _step(
                5,
                "systemd.cat",
                "systemctl cat orders-api",
                "Porównaj ścieżkę uruchomieniową.",
            ),
            _medium_editor_step(
                6,
                "nano /etc/systemd/system/orders-api.service",
                _healthy_api_unit(),
                "Popraw plik jednostki.",
            ),
            _step(
                7,
                "systemd.daemon-reload",
                "systemctl daemon-reload",
                "Przeładuj cache jednostek.",
            ),
            _step(
                8,
                "systemd.restart",
                "systemctl restart orders-api",
                "Uruchom poprawioną jednostkę.",
            ),
            _step(9, "remote.ssh", "ssh edge-01", "Wróć na host brzegowy."),
            _step(
                10,
                "network.curl",
                "curl http://portal.internal",
                "Zweryfikuj pełną ścieżkę.",
            ),
        )
        root_cause = (
            "Jednostka systemd wskazywała nieaktualny plik wykonywalny, a poprawiona definicja "
            "wymagała przeładowania cache przez daemon-reload."
        )
        repair_capabilities = (
            "filesystem.edit",
            "systemd.daemon-reload",
            "systemd.restart",
        )
        organization = "Bursztynowa Chmura"
        environment_label = "Zaplecze obsługi katalogu"
        title = "Nieaktualna definicja jednostki"
        forbidden_terms = ("orders-api-old", "daemon-reload", "execstart")
    elif category in {"service-config-invalid", "dependency-dns-name-mismatch"}:
        wrong_host = (
            "database-archive.internal"
            if category == "service-config-invalid"
            else "database.service.internal"
        )
        config = _resource_with(
            resource_by_id["file-api-config"],
            content=f"DATABASE_HOST={wrong_host}\n",
        )
        replace("file-api-config", config)
        replace(
            "service-api",
            _resource_with(
                resource_by_id["service-api"],
                journal_clue="Połączenie z usługą danych nie może zostać zestawione.",
            ),
        )
        common_steps = [
            _step(
                1,
                "network.curl",
                "curl http://portal.internal",
                "Potwierdź degradację.",
            ),
            _step(2, "remote.ssh", "ssh app-01", "Przejdź na host aplikacji."),
            _step(
                3,
                "systemd.status",
                "systemctl status orders-api",
                "Potwierdź działanie procesu.",
            ),
        ]
        if category == "dependency-dns-name-mismatch":
            replace(
                "service-api",
                _resource_with(
                    resource_by_id["service-api"],
                    required_dns_name="database.internal",
                ),
            )
            common_steps.extend(
                (
                    _step(
                        4,
                        "network.ping",
                        "ping 10.24.8.30",
                        "Potwierdź osiągalność hosta po IP.",
                    ),
                    _step(
                        5,
                        "network.dig",
                        f"dig {wrong_host}",
                        "Sprawdź nazwę używaną przez usługę.",
                        expected_success=False,
                    ),
                    _step(
                        6,
                        "network.dig",
                        "dig database.internal",
                        "Zweryfikuj właściwy rekord DNS.",
                    ),
                    _step(
                        7,
                        "filesystem.read",
                        "cat /opt/orders-api/app.conf",
                        "Porównaj konfigurację z DNS.",
                    ),
                    _medium_editor_step(
                        8,
                        "nano /opt/orders-api/app.conf",
                        "DATABASE_HOST=database.internal\n",
                        "Popraw nazwę zależności.",
                    ),
                    _step(
                        9,
                        "systemd.restart",
                        "systemctl restart orders-api",
                        "Przeładuj konfigurację API.",
                    ),
                    _step(10, "remote.ssh", "ssh edge-01", "Wróć na host brzegowy."),
                    _step(
                        11,
                        "network.curl",
                        "curl http://portal.internal",
                        "Zweryfikuj pełną ścieżkę.",
                    ),
                )
            )
            root_cause = (
                "Konfiguracja API używała nieistniejącej nazwy DNS zależności, mimo że host "
                "bazy danych pozostawał osiągalny po adresie IP."
            )
            organization = "Nadwiślańskie Systemy"
            environment_label = "Platforma synchronizacji danych"
            title = "Błędna nazwa zależności"
            forbidden_terms = (wrong_host, "DATABASE_HOST")
        else:
            common_steps.extend(
                (
                    _step(
                        4,
                        "journal.read",
                        "journalctl -u orders-api",
                        "Sprawdź komunikaty aplikacji.",
                    ),
                    _step(
                        5,
                        "filesystem.read",
                        "cat /opt/orders-api/app.conf",
                        "Sprawdź konfigurację zależności.",
                    ),
                    _medium_editor_step(
                        6,
                        "nano /opt/orders-api/app.conf",
                        "DATABASE_HOST=database.internal\n",
                        "Przywróć właściwą konfigurację.",
                    ),
                    _step(
                        7,
                        "systemd.restart",
                        "systemctl restart orders-api",
                        "Przeładuj konfigurację API.",
                    ),
                    _step(8, "remote.ssh", "ssh edge-01", "Wróć na host brzegowy."),
                    _step(
                        9,
                        "network.curl",
                        "curl http://portal.internal",
                        "Zweryfikuj pełną ścieżkę.",
                    ),
                )
            )
            root_cause = "API wskazywało nieprawidłowy adres logiczny usługi danych w pliku konfiguracji."
            organization = "Zielony Port"
            environment_label = "System obsługi rezerwacji"
            title = "Niespójna konfiguracja API"
            forbidden_terms = (wrong_host, "DATABASE_HOST")
        solution = tuple(common_steps)
        fault_target = "file-api-config"
    elif category == "dependency-port-mismatch":
        proxy_config = _resource_with(proxy_config, content="UPSTREAM_PORT=8081\n")
        resource_by_id[proxy_config.resource_id] = proxy_config
        replace(
            "service-proxy",
            _resource_with(
                resource_by_id["service-proxy"],
                journal_clue="Upstream odrzuca połączenie na skonfigurowanym porcie.",
            ),
        )
        configuration_requirements = (
            *base.configuration_requirements,
            ConfigurationRequirement(
                requirement_id="config-proxy-upstream",
                service_id="service-proxy",
                host_id="host-edge-01",
                file_resource_id="file-proxy-config",
            ),
        )
        solution = (
            _step(
                1,
                "network.curl",
                "curl http://portal.internal",
                "Potwierdź degradację.",
            ),
            _step(
                2,
                "systemd.status",
                "systemctl status edge-proxy",
                "Potwierdź działanie proxy.",
            ),
            _step(3, "network.listeners", "ss -lntp", "Sprawdź lokalne listenery."),
            _step(4, "remote.ssh", "ssh app-01", "Przejdź na host API."),
            _step(5, "network.listeners", "ss -lntp", "Sprawdź port API."),
            _step(6, "remote.ssh", "ssh edge-01", "Wróć na host proxy."),
            _step(
                7,
                "filesystem.read",
                "cat /opt/edge-proxy/upstream.conf",
                "Porównaj port upstream.",
            ),
            _medium_editor_step(
                8,
                "nano /opt/edge-proxy/upstream.conf",
                "UPSTREAM_PORT=8080\n",
                "Ujednolić port zależności.",
            ),
            _step(
                9,
                "systemd.restart",
                "systemctl restart edge-proxy",
                "Przeładuj konfigurację proxy.",
            ),
            _step(
                10,
                "network.curl",
                "curl http://portal.internal",
                "Zweryfikuj pełną ścieżkę.",
            ),
        )
        root_cause = "Reverse proxy kierował żądania na port 8081, podczas gdy API nasłuchiwało na porcie 8080."
        organization = "Latarnia Operacyjna"
        environment_label = "Bramka usług wewnętrznych"
        title = "Działające procesy, zerwana ścieżka"
        fault_target = "file-proxy-config"
        forbidden_terms = ("UPSTREAM_PORT=8081", "8081")
    elif category == "selinux-proxy-context-invalid":
        proxy = _resource_with(
            resource_by_id["service-proxy"],
            state="failed",
            current_selinux_context="unconfined_u:object_r:default_t:s0",
            expected_selinux_context="system_u:object_r:bin_t:s0",
        )
        replace("service-proxy", proxy)
        solution = (
            _step(
                1,
                "network.curl",
                "curl http://portal.internal",
                "Potwierdź niedostępność.",
                expected_success=False,
            ),
            _step(
                2,
                "systemd.status",
                "systemctl status edge-proxy",
                "Sprawdź stan proxy.",
            ),
            _step(
                3,
                "journal.read",
                "journalctl -u edge-proxy",
                "Odczytaj przyczynę odmowy.",
            ),
            _step(4, "selinux.getenforce", "getenforce", "Sprawdź tryb SELinux."),
            _step(
                5,
                "selinux.semanage",
                "semanage fcontext -l",
                "Sprawdź oczekiwane konteksty.",
            ),
            _step(
                6,
                "selinux.restorecon",
                "restorecon -R /opt/edge-proxy",
                "Przywróć kontekst plików proxy.",
            ),
            _step(
                7,
                "systemd.restart",
                "systemctl restart edge-proxy",
                "Uruchom ponownie proxy.",
            ),
            _step(
                8,
                "network.curl",
                "curl http://portal.internal",
                "Zweryfikuj pełną ścieżkę.",
            ),
        )
        root_cause = "Pliki reverse proxy miały kontekst SELinux niezgodny z oczekiwaną etykietą wykonywalną."
        repair_capabilities = ("selinux.restorecon", "systemd.restart")
        organization = "Pracownia Północ"
        environment_label = "Warstwa publikacji usług"
        title = "Proxy blokowane przez politykę systemu"
        fault_target = "service-proxy"
        forbidden_terms = ("restorecon", "default_t", "bin_t")
    else:
        app_host = _resource_with(
            resource_by_id["host-app-01"], connection_active=False
        )
        replace("host-app-01", app_host)
        solution = (
            _step(
                1,
                "network.curl",
                "curl http://portal.internal",
                "Potwierdź degradację.",
            ),
            _step(2, "remote.ssh", "ssh app-01", "Przejdź do konsoli hosta aplikacji."),
            _step(
                3,
                "networkmanager.command",
                "nmcli device status",
                "Sprawdź stan interfejsu.",
            ),
            _step(4, "network.route", "ip route", "Sprawdź widoczne trasy."),
            _step(
                5,
                "networkmanager.command",
                "nmcli connection show",
                "Ustal nazwę profilu połączenia.",
            ),
            _step(
                6,
                "networkmanager.command",
                "nmcli connection up System-ens192",
                "Aktywuj istniejący profil.",
            ),
            _step(
                7,
                "network.ping",
                "ping 10.24.8.30",
                "Zweryfikuj łączność do usługi danych.",
            ),
            _step(8, "remote.ssh", "ssh edge-01", "Wróć na host brzegowy."),
            _step(
                9,
                "network.curl",
                "curl http://portal.internal",
                "Zweryfikuj pełną ścieżkę.",
            ),
        )
        root_cause = "Profil NetworkManager na hoście aplikacji był nieaktywny, odcinając API od zależności."
        repair_capabilities = ("networkmanager.command",)
        organization = "Węzeł Zachodni"
        environment_label = "Klaster integracji operacyjnej"
        title = "Odłączony host aplikacyjny"
        fault_target = "host-app-01"
        forbidden_terms = ("connection up", "System-ens192")

    fault = FaultInstance(
        fault_id=f"fault-{category}",
        fault_type=category.replace("-", "_"),
        version="5.0",
        target_resource_id=fault_target,
        severity=FaultSeverity.MEDIUM,
        parameters=_fields(
            component_id=category,
            forbidden_public_terms=forbidden_terms,
        ),
    )
    symptom = base.symptoms[0].model_copy(
        update={
            "symptom_id": f"symptom-{category}",
            "data": _fields(observed_state="http-502"),
        }
    )
    presentation = base.presentation.model_copy(
        update={
            "title": title,
            "organization": organization,
            "environment_label": environment_label,
            "briefing": briefing,
            "ticket_reference": f"MED-{seed % 100000:05d}",
            "tags": ("medium", "dependencies", "diagnostyka"),
        }
    )
    world = base.initial_world_state.model_copy(
        update={
            "environment_id": f"medium-{category}",
            "environment_version": "5.0",
            "resources": tuple(resource_by_id.values()),
        }
    )
    return base.model_copy(
        update={
            "draft_id": f"medium-{category}-{seed}",
            "generator_version": "5.0",
            "components": _components(category, version="5.0"),
            "presentation": presentation,
            "initial_world_state": world,
            "faults": (fault,),
            "symptoms": (symptom,),
            "solution": solution,
            "configuration_requirements": configuration_requirements,
            "post_incident": PostIncidentDefinition(
                root_cause=root_cause,
                affected_service_ids=("service-proxy", "service-api"),
                repair_capability_ids=repair_capabilities,
            ),
        }
    )
