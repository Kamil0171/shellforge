from types import MappingProxyType
from typing import Final

from pydantic import Field, model_validator

from app.admin_duty.components.scenarios.medium import (
    _dependency,
    _fields,
    _host,
    _map_snapshot,
    _service,
    _step,
)
from app.admin_duty.domain.definition import (
    CapabilitySet,
    CompletionCondition,
    ComponentReference,
    ComponentType,
    ConditionOperator,
    ConfigurationRequirement,
    FaultInstance,
    FaultRelation,
    FaultRelationType,
    FaultSeverity,
    FrozenDomainModel,
    GenerationSource,
    Hint,
    Identifier,
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

HARD_ENVIRONMENT_ARCHETYPE = "hard-web-stack"
HARD_DEPENDENCY_ARCHETYPE = "proxy-api-database"
HARD_SYMPTOM_ARCHETYPE = "progressive_service_degradation"


class HardSymptomStage(FrozenDomainModel):
    state: Identifier
    summary: str = Field(min_length=1, max_length=300)


class HardFaultCombination(FrozenDomainModel):
    combination_id: Identifier
    primary_fault_category: Identifier
    secondary_fault_category: Identifier
    compatible_environment_archetypes: tuple[Identifier, ...] = Field(min_length=1)
    required_host_roles: tuple[str, ...] = Field(min_length=2)
    affected_service_archetype: Identifier
    dependency_archetype: Identifier
    relation_type: FaultRelationType
    symptom_progression: tuple[HardSymptomStage, ...] = Field(min_length=3, max_length=3)
    reference_repair_order: tuple[Identifier, Identifier]
    required_capabilities: tuple[Identifier, ...] = Field(min_length=1)
    skill_tags: tuple[Identifier, ...] = Field(min_length=1, max_length=5)
    constraints: tuple[str, ...] = Field(default=(), max_length=8)

    @model_validator(mode="after")
    def validate_pair(self):
        if self.primary_fault_category == self.secondary_fault_category:
            raise ValueError("Kombinacja HARD wymaga dwóch różnych faultów.")
        if self.reference_repair_order != (
            self.primary_fault_category,
            self.secondary_fault_category,
        ):
            raise ValueError("Kolejność napraw nie odpowiada faultom kombinacji.")
        if tuple(stage.state for stage in self.symptom_progression) != (
            "broken",
            "partially_recovered",
            "healthy",
        ):
            raise ValueError("Kombinacja HARD wymaga pełnej progresji symptomów.")
        return self


def _progression(partial_summary: str) -> tuple[HardSymptomStage, ...]:
    return (
        HardSymptomStage(
            state="broken",
            summary="Usługa publiczna i zależności wewnętrzne są niedostępne.",
        ),
        HardSymptomStage(state="partially_recovered", summary=partial_summary),
        HardSymptomStage(
            state="healthy",
            summary="Pełna ścieżka żądania wróciła do stanu nominalnego.",
        ),
    )


HARD_COMBINATIONS: Final = (
    HardFaultCombination(
        combination_id="H-01",
        primary_fault_category="dependency-firewall-blocked",
        secondary_fault_category="selinux-context-invalid",
        compatible_environment_archetypes=(HARD_ENVIRONMENT_ARCHETYPE,),
        required_host_roles=("warstwa brzegowa", "aplikacja", "baza danych", "DNS", "sonda zewnętrzna"),
        affected_service_archetype="web-api",
        dependency_archetype=HARD_DEPENDENCY_ARCHETYPE,
        relation_type=FaultRelationType.DEPENDENCY_CHAIN,
        symptom_progression=_progression(
            "Łączność z bazą wróciła, ale proces API nadal nie działa prawidłowo."
        ),
        reference_repair_order=(
            "dependency-firewall-blocked",
            "selinux-context-invalid",
        ),
        required_capabilities=(
            "firewalld.command",
            "selinux.restorecon",
            "systemd.restart",
        ),
        skill_tags=("firewall", "selinux", "systemd", "network"),
    ),
    HardFaultCombination(
        combination_id="H-02",
        primary_fault_category="networkmanager-dns-invalid",
        secondary_fault_category="external-firewall-mismatch",
        compatible_environment_archetypes=(HARD_ENVIRONMENT_ARCHETYPE,),
        required_host_roles=("warstwa brzegowa", "aplikacja", "baza danych", "DNS", "sonda zewnętrzna"),
        affected_service_archetype="reverse-proxy",
        dependency_archetype=HARD_DEPENDENCY_ARCHETYPE,
        relation_type=FaultRelationType.DEPENDENCY_CHAIN,
        symptom_progression=_progression(
            "Rozwiązywanie nazw działa, lecz publiczny punkt wejścia pozostaje nieosiągalny."
        ),
        reference_repair_order=(
            "networkmanager-dns-invalid",
            "external-firewall-mismatch",
        ),
        required_capabilities=("networkmanager.command", "firewalld.command"),
        skill_tags=("dns", "network", "firewall"),
    ),
    HardFaultCombination(
        combination_id="H-03",
        primary_fault_category="dependency-package-missing",
        secondary_fault_category="systemd-wrong-exec-start",
        compatible_environment_archetypes=(HARD_ENVIRONMENT_ARCHETYPE,),
        required_host_roles=("warstwa brzegowa", "aplikacja", "baza danych", "DNS", "sonda zewnętrzna"),
        affected_service_archetype="web-api",
        dependency_archetype=HARD_DEPENDENCY_ARCHETYPE,
        relation_type=FaultRelationType.DEPENDENCY_CHAIN,
        symptom_progression=_progression(
            "API odpowiada bezpośrednio, ale warstwa proxy nadal nie uruchamia się poprawnie."
        ),
        reference_repair_order=(
            "dependency-package-missing",
            "systemd-wrong-exec-start",
        ),
        required_capabilities=(
            "packages.command",
            "filesystem.edit",
            "systemd.daemon-reload",
            "systemd.restart",
        ),
        skill_tags=("packages", "systemd", "filesystem"),
    ),
    HardFaultCombination(
        combination_id="H-04",
        primary_fault_category="service-config-invalid",
        secondary_fault_category="dependency-port-mismatch",
        compatible_environment_archetypes=(HARD_ENVIRONMENT_ARCHETYPE,),
        required_host_roles=("warstwa brzegowa", "aplikacja", "baza danych", "DNS", "sonda zewnętrzna"),
        affected_service_archetype="web-api",
        dependency_archetype=HARD_DEPENDENCY_ARCHETYPE,
        relation_type=FaultRelationType.DEPENDENCY_CHAIN,
        symptom_progression=_progression(
            "Konfiguracja API jest poprawna, lecz proxy nadal kieruje ruch na niewłaściwy port."
        ),
        reference_repair_order=(
            "service-config-invalid",
            "dependency-port-mismatch",
        ),
        required_capabilities=("filesystem.edit", "systemd.restart"),
        skill_tags=("filesystem", "systemd", "network"),
        constraints=("Obie zmiany dotyczą różnych plików i różnych usług.",),
    ),
    HardFaultCombination(
        combination_id="H-05",
        primary_fault_category="networkmanager-connection-inactive",
        secondary_fault_category="dependency-firewall-blocked",
        compatible_environment_archetypes=(HARD_ENVIRONMENT_ARCHETYPE,),
        required_host_roles=("warstwa brzegowa", "aplikacja", "baza danych", "DNS", "sonda zewnętrzna"),
        affected_service_archetype="web-api",
        dependency_archetype=HARD_DEPENDENCY_ARCHETYPE,
        relation_type=FaultRelationType.DEPENDENCY_CHAIN,
        symptom_progression=_progression(
            "Interfejs aplikacyjny wrócił, ale komunikacja z usługą danych nadal jest blokowana."
        ),
        reference_repair_order=(
            "networkmanager-connection-inactive",
            "dependency-firewall-blocked",
        ),
        required_capabilities=("networkmanager.command", "firewalld.command"),
        skill_tags=("network", "firewall"),
    ),
)

HARD_COMBINATIONS_BY_ID: Final = MappingProxyType(
    {item.combination_id: item for item in HARD_COMBINATIONS}
)
HARD_COMBINATIONS_BY_PAIR: Final = MappingProxyType(
    {
        (item.primary_fault_category, item.secondary_fault_category): item
        for item in HARD_COMBINATIONS
    }
)


def get_hard_combination(combination_id: str) -> HardFaultCombination:
    try:
        return HARD_COMBINATIONS_BY_ID[combination_id]
    except KeyError as error:
        raise ValueError(f"Nieznana kombinacja HARD: {combination_id}.") from error


def get_hard_combination_for_pair(
    primary_fault_category: str,
    secondary_fault_category: str,
) -> HardFaultCombination:
    try:
        return HARD_COMBINATIONS_BY_PAIR[
            (primary_fault_category, secondary_fault_category)
        ]
    except KeyError as error:
        raise ValueError("Nieobsługiwana para faultów HARD.") from error


def _with_attributes(resource: WorldResource, **updates) -> WorldResource:
    attributes = {field.key: field.value for field in resource.attributes}
    attributes.update(updates)
    return resource.model_copy(update={"attributes": _fields(**attributes)})


def _healthy_unit(service_name: str) -> str:
    app_name = service_name.removesuffix(".service")
    return (
        "[Unit]\nDescription=Usługa aplikacyjna\nAfter=network-online.target\n\n"
        "[Service]\nType=simple\n"
        f"ExecStart=/opt/{app_name}/{app_name}\n"
        "User=app\nRestart=on-failure\n\n"
        "[Install]\nWantedBy=multi-user.target\n"
    )


def _editor_step(order: int, command: str, content: str, purpose: str) -> SolutionStep:
    return SolutionStep(
        order=order,
        capability_id="filesystem.edit",
        input=command,
        purpose=purpose,
        parameters=_fields(content=content),
    )


def _renumber(steps) -> tuple[SolutionStep, ...]:
    return tuple(step.model_copy(update={"order": index}) for index, step in enumerate(steps, 1))


def _components(combination: HardFaultCombination) -> tuple[ComponentReference, ...]:
    return (
        ComponentReference(
            component_type=ComponentType.MAP,
            component_id="web-operations-room",
            version="1.0",
        ),
        ComponentReference(
            component_type=ComponentType.ENVIRONMENT,
            component_id=HARD_ENVIRONMENT_ARCHETYPE,
            version="4.0",
        ),
        *(
            ComponentReference(
                component_type=ComponentType.FAULT,
                component_id=category,
                version="4.0",
            )
            for category in (
                combination.primary_fault_category,
                combination.secondary_fault_category,
            )
        ),
        ComponentReference(
            component_type=ComponentType.SYMPTOM,
            component_id=HARD_SYMPTOM_ARCHETYPE,
            version="4.0",
        ),
        ComponentReference(
            component_type=ComponentType.OBJECTIVE,
            component_id="objectives-hard-service-chain",
            version="4.0",
        ),
        ComponentReference(
            component_type=ComponentType.CAPABILITY,
            component_id="capabilities-virtual-rocky-v4",
            version="4.0",
        ),
        ComponentReference(
            component_type=ComponentType.SCORING_POLICY,
            component_id="scoring-strict",
            version="4.0",
        ),
    )


def build_hard_draft(combination_id: str, *, seed: int) -> GeneratedIncidentDraft:
    combination = get_hard_combination(combination_id)
    suffix = seed % 10000
    names = {
        "edge": f"edge-{suffix:04d}",
        "app": f"app-{suffix:04d}",
        "data": f"data-{suffix:04d}",
        "dns": f"dns-{suffix:04d}",
        "client": f"client-{suffix:04d}",
    }
    edge_services = ("ssh", "http")
    app_packages = ("python3-psycopg2",)
    app_dns = ("10.24.8.53",)
    app_connection_active = True
    database_ports = ("5432/tcp",)
    api_state = "running"
    api_context = None
    proxy_state = "running"
    proxy_exec = "edge-proxy"
    api_config = "DATABASE_HOST=database.internal\n"
    proxy_config = "UPSTREAM_PORT=8080\n"

    if combination_id == "H-01":
        database_ports = ()
        api_state = "failed"
        api_context = "unconfined_u:object_r:default_t:s0"
    elif combination_id == "H-02":
        app_dns = ()
        edge_services = ("ssh",)
    elif combination_id == "H-03":
        app_packages = ()
        api_state = "failed"
        proxy_state = "failed"
        proxy_exec = "edge-proxy-missing"
    elif combination_id == "H-04":
        api_config = "DATABASE_HOST=database-wrong.internal\n"
        proxy_config = "UPSTREAM_PORT=8081\n"
    elif combination_id == "H-05":
        app_connection_active = False
        database_ports = ()

    hosts = [
        _with_attributes(
            _host(
                "host-edge-01",
                names["edge"],
                "10.24.8.10/24",
                "warstwa brzegowa",
                firewall_services=edge_services,
            ),
            expected_firewall_services=("ssh", "http"),
            expected_firewall_ports=(),
            connection_active=True,
        ),
        _with_attributes(
            _host(
                "host-app-01",
                names["app"],
                "10.24.8.20/24",
                "aplikacja",
                installed_packages=app_packages,
                firewall_ports=("8080/tcp",),
                dns_servers=app_dns,
            ),
            expected_firewall_services=("ssh",),
            expected_firewall_ports=("8080/tcp",),
            connection_active=app_connection_active,
        ),
        _with_attributes(
            _host(
                "host-data-01",
                names["data"],
                "10.24.8.30/24",
                "baza danych",
                firewall_ports=database_ports,
            ),
            expected_firewall_services=("ssh",),
            expected_firewall_ports=("5432/tcp",),
            connection_active=True,
        ),
        _with_attributes(
            _host(
                "host-dns-01",
                names["dns"],
                "10.24.8.53/24",
                "DNS",
                firewall_services=("ssh", "dns"),
            ),
            expected_firewall_services=("ssh", "dns"),
            expected_firewall_ports=(),
            connection_active=True,
        ),
        _with_attributes(
            _host(
                "host-client-01",
                names["client"],
                "10.24.8.40/24",
                "sonda zewnętrzna",
            ),
            expected_firewall_services=("ssh",),
            expected_firewall_ports=(),
            connection_active=True,
        ),
    ]
    proxy = _service(
        "service-proxy",
        "host-edge-01",
        "edge-proxy.service",
        80,
        state=proxy_state,
        unhealthy_status_code=502,
    )
    proxy = (_with_attributes(proxy[0], configured_exec_start=proxy_exec), proxy[1])
    api = _service(
        "service-api",
        "host-app-01",
        "orders-api.service",
        8080,
        state=api_state,
        required_package="python3-psycopg2",
        required_dns_name="database.internal",
        current_selinux_context=api_context,
    )
    database = _service(
        "service-database", "host-data-01", "database.service", 5432
    )
    dns = _service("service-dns", "host-dns-01", "named.service", 53)
    external = _service(
        "service-external-check",
        "host-client-01",
        "external-check.service",
        9090,
    )
    resources = [*hosts, *proxy, *api, *database, *dns, *external]
    dependencies: list[ServiceDependency] = [
        _dependency(
            "dep-external-proxy",
            "host-client-01",
            "service-external-check",
            "service-proxy",
            "host-edge-01",
            NetworkProtocol.HTTP,
            80,
        ),
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
        ),
        _dependency(
            "dep-api-dns",
            "host-app-01",
            "service-api",
            "service-dns",
            "host-dns-01",
            NetworkProtocol.UDP,
            53,
        ),
    ]
    api_file = WorldResource(
        resource_id="file-api-config",
        resource_type=ResourceType.FILE,
        state="present",
        parent_id="host-app-01",
        attributes=_fields(
            path="/opt/orders-api/app.conf",
            content=api_config,
            expected_content="DATABASE_HOST=database.internal\n",
            current_mode="0640",
            owner="app",
        ),
    )
    proxy_file = WorldResource(
        resource_id="file-proxy-config",
        resource_type=ResourceType.FILE,
        state="present",
        parent_id="host-edge-01",
        attributes=_fields(
            path="/opt/edge-proxy/upstream.conf",
            content=proxy_config,
            expected_content="UPSTREAM_PORT=8080\n",
            current_mode="0640",
            owner="app",
        ),
    )
    endpoint_primary = WorldResource(
        resource_id="endpoint-primary-path",
        resource_type=ResourceType.ENDPOINT,
        state="unhealthy",
        attributes=_fields(label="Wewnętrzna ścieżka zależności"),
    )
    endpoint_portal = WorldResource(
        resource_id="endpoint-portal",
        resource_type=ResourceType.ENDPOINT,
        state="unreachable",
        dependencies=("service-proxy",),
        attributes=_fields(
            url="http://portal.internal",
            label="Publiczna aplikacja",
        ),
    )
    resources.extend(
        (
            api_file,
            proxy_file,
            endpoint_primary,
            endpoint_portal,
            WorldResource(
                resource_id="domain-portal",
                resource_type=ResourceType.DOMAIN,
                state="present",
                attributes=_fields(name="portal.internal", address="10.24.8.10"),
            ),
            WorldResource(
                resource_id="domain-api",
                resource_type=ResourceType.DOMAIN,
                state="present",
                attributes=_fields(name="api.internal", address="10.24.8.20"),
            ),
            WorldResource(
                resource_id="domain-database",
                resource_type=ResourceType.DOMAIN,
                state="present",
                attributes=_fields(name="database.internal", address="10.24.8.30"),
            ),
        )
    )

    primary_dependency = {
        "H-01": "dep-api-database",
        "H-02": "dep-api-dns",
        "H-03": "dep-proxy-api",
        "H-04": "dep-proxy-api",
        "H-05": "dep-api-dns",
    }[combination_id]
    resolution_conditions = {
        "H-01": (
            CompletionCondition(
                resource_id="host-data-01",
                field="attributes.firewall_health",
                operator=ConditionOperator.EQUALS,
                expected="healthy",
            ),
            CompletionCondition(
                resource_id="service-api",
                field="current_state",
                operator=ConditionOperator.EQUALS,
                expected="running",
            ),
        ),
        "H-02": (
            CompletionCondition(
                resource_id="host-app-01",
                field="attributes.dns_health",
                operator=ConditionOperator.EQUALS,
                expected="healthy",
            ),
            CompletionCondition(
                resource_id="host-edge-01",
                field="attributes.firewall_health",
                operator=ConditionOperator.EQUALS,
                expected="healthy",
            ),
        ),
        "H-03": (
            CompletionCondition(
                resource_id="service-api",
                field="current_state",
                operator=ConditionOperator.EQUALS,
                expected="running",
            ),
            CompletionCondition(
                resource_id="service-proxy",
                field="current_state",
                operator=ConditionOperator.EQUALS,
                expected="running",
            ),
        ),
        "H-04": (
            CompletionCondition(
                resource_id="service-api",
                field="attributes.configuration_health",
                operator=ConditionOperator.EQUALS,
                expected="healthy",
            ),
            CompletionCondition(
                resource_id="service-proxy",
                field="attributes.configuration_health",
                operator=ConditionOperator.EQUALS,
                expected="healthy",
            ),
        ),
        "H-05": (
            CompletionCondition(
                resource_id="host-app-01",
                field="attributes.network_health",
                operator=ConditionOperator.EQUALS,
                expected="healthy",
            ),
            CompletionCondition(
                resource_id="host-data-01",
                field="attributes.firewall_health",
                operator=ConditionOperator.EQUALS,
                expected="healthy",
            ),
        ),
    }[combination_id]
    faults = tuple(
        FaultInstance(
            fault_id=f"fault-{position}",
            fault_type=category.replace("-", "_"),
            version="4.0",
            target_resource_id=(
                resolution_conditions[index].resource_id
            ),
            severity=FaultSeverity.HIGH,
            parameters=_fields(
                component_id=category,
                combination_id=combination.combination_id,
                position=position,
                forbidden_public_terms=(
                    "restorecon",
                    "python3-psycopg2",
                    "ipv4.dns",
                    "5432/tcp",
                    "UPSTREAM_PORT",
                    "ExecStart",
                ),
            ),
            resolution_condition=resolution_conditions[index],
        )
        for index, (position, category) in enumerate(
            (
                ("primary", combination.primary_fault_category),
                ("secondary", combination.secondary_fault_category),
            )
        )
    )

    edge = names["edge"]
    app = names["app"]
    data = names["data"]
    client = names["client"]
    if combination_id == "H-01":
        steps = (
            _step(1, "network.curl", "curl http://portal.internal", "Potwierdź awarię."),
            _step(2, "remote.ssh", f"ssh {data}", "Przejdź na host danych."),
            _step(3, "firewalld.command", "firewall-cmd --list-all", "Sprawdź reguły."),
            _step(4, "firewalld.command", "firewall-cmd --permanent --add-port=5432/tcp", "Przywróć port zależności."),
            _step(5, "firewalld.command", "firewall-cmd --reload", "Aktywuj regułę."),
            _step(6, "network.curl", "curl http://database.internal:5432", "Zweryfikuj częściową poprawę."),
            _step(7, "remote.ssh", f"ssh {app}", "Przejdź na host aplikacji."),
            _step(8, "selinux.getenforce", "getenforce", "Sprawdź tryb SELinux."),
            _step(9, "selinux.restorecon", "restorecon -R /opt/orders-api", "Przywróć kontekst."),
            _step(10, "systemd.restart", "systemctl restart orders-api", "Uruchom API."),
            _step(11, "remote.ssh", f"ssh {client}", "Wróć do sondy."),
            _step(12, "network.curl", "curl http://portal.internal", "Zweryfikuj pełną ścieżkę."),
        )
    elif combination_id == "H-02":
        steps = (
            _step(1, "network.curl", "curl http://portal.internal", "Potwierdź awarię.", expected_success=False),
            _step(2, "remote.ssh", f"ssh {app}", "Przejdź na host aplikacji."),
            _step(3, "network.dig", "dig database.internal", "Sprawdź DNS.", expected_success=False),
            _step(4, "networkmanager.command", "nmcli connection modify System-ens192 ipv4.dns 10.24.8.53", "Przywróć DNS."),
            _step(5, "network.dig", "dig database.internal", "Zweryfikuj częściową poprawę."),
            _step(6, "remote.ssh", f"ssh {edge}", "Przejdź na host brzegowy."),
            _step(7, "firewalld.command", "firewall-cmd --list-all", "Sprawdź dostęp publiczny."),
            _step(8, "firewalld.command", "firewall-cmd --permanent --add-service=http", "Dodaj usługę HTTP."),
            _step(9, "firewalld.command", "firewall-cmd --reload", "Aktywuj regułę."),
            _step(10, "remote.ssh", f"ssh {client}", "Wróć do sondy."),
            _step(11, "network.curl", "curl http://portal.internal", "Zweryfikuj pełną ścieżkę."),
        )
    elif combination_id == "H-03":
        steps = (
            _step(1, "network.curl", "curl http://portal.internal", "Potwierdź awarię.", expected_success=False),
            _step(2, "remote.ssh", f"ssh {app}", "Przejdź na host aplikacji."),
            _step(3, "packages.rpm", "rpm -q python3-psycopg2", "Sprawdź pakiet.", expected_success=False),
            _step(4, "packages.command", "dnf install -y python3-psycopg2", "Zainstaluj zależność."),
            _step(5, "systemd.restart", "systemctl restart orders-api", "Uruchom API."),
            _step(6, "remote.ssh", f"ssh {edge}", "Zweryfikuj częściową poprawę."),
            _step(7, "network.curl", "curl http://api.internal:8080", "Sprawdź API."),
            _step(8, "systemd.status", "systemctl status edge-proxy", "Sprawdź proxy."),
            _editor_step(9, "nano /etc/systemd/system/edge-proxy.service", _healthy_unit("edge-proxy.service"), "Popraw jednostkę proxy."),
            _step(10, "systemd.daemon-reload", "systemctl daemon-reload", "Przeładuj jednostki."),
            _step(11, "systemd.restart", "systemctl restart edge-proxy", "Uruchom proxy."),
            _step(12, "remote.ssh", f"ssh {client}", "Wróć do sondy."),
            _step(13, "network.curl", "curl http://portal.internal", "Zweryfikuj pełną ścieżkę."),
        )
    elif combination_id == "H-04":
        steps = (
            _step(1, "network.curl", "curl http://portal.internal", "Potwierdź awarię."),
            _step(2, "remote.ssh", f"ssh {app}", "Przejdź na host aplikacji."),
            _editor_step(3, "nano /opt/orders-api/app.conf", "DATABASE_HOST=database.internal\n", "Popraw konfigurację API."),
            _step(4, "systemd.restart", "systemctl restart orders-api", "Przeładuj API."),
            _step(5, "remote.ssh", f"ssh {edge}", "Zweryfikuj częściową poprawę."),
            _step(6, "network.curl", "curl http://api.internal:8080", "Sprawdź API."),
            _editor_step(7, "nano /opt/edge-proxy/upstream.conf", "UPSTREAM_PORT=8080\n", "Popraw port upstream."),
            _step(8, "systemd.restart", "systemctl restart edge-proxy", "Przeładuj proxy."),
            _step(9, "remote.ssh", f"ssh {client}", "Wróć do sondy."),
            _step(10, "network.curl", "curl http://portal.internal", "Zweryfikuj pełną ścieżkę."),
        )
    else:
        steps = (
            _step(1, "network.curl", "curl http://portal.internal", "Potwierdź awarię."),
            _step(2, "remote.ssh", f"ssh {app}", "Przejdź na host aplikacji."),
            _step(3, "networkmanager.command", "nmcli device status", "Sprawdź połączenie."),
            _step(4, "networkmanager.command", "nmcli connection up System-ens192", "Aktywuj połączenie."),
            _step(5, "network.dig", "dig database.internal", "Zweryfikuj częściową poprawę."),
            _step(6, "remote.ssh", f"ssh {data}", "Przejdź na host danych."),
            _step(7, "firewalld.command", "firewall-cmd --list-all", "Sprawdź reguły."),
            _step(8, "firewalld.command", "firewall-cmd --permanent --add-port=5432/tcp", "Przywróć port zależności."),
            _step(9, "firewalld.command", "firewall-cmd --reload", "Aktywuj regułę."),
            _step(10, "remote.ssh", f"ssh {client}", "Wróć do sondy."),
            _step(11, "network.curl", "curl http://portal.internal", "Zweryfikuj pełną ścieżkę."),
        )

    repair_labels = {
        "dependency-firewall-blocked": "blokada ruchu przez firewalld",
        "selinux-context-invalid": "nieprawidłowy kontekst SELinux",
        "networkmanager-dns-invalid": "błędna konfiguracja DNS w NetworkManager",
        "external-firewall-mismatch": "brak reguły dostępu na warstwie brzegowej",
        "dependency-package-missing": "brak pakietu wymaganego przez API",
        "systemd-wrong-exec-start": "błędna ścieżka ExecStart jednostki systemd",
        "service-config-invalid": "błędna konfiguracja usługi API",
        "dependency-port-mismatch": "niezgodny port zależności proxy",
        "networkmanager-connection-inactive": "nieaktywne połączenie NetworkManager",
    }
    return GeneratedIncidentDraft(
        draft_id=f"hard-{combination.combination_id.lower()}-{seed}",
        schema_version="4.0",
        difficulty=DifficultyLevel.HARD,
        generator_id="shellforge.deterministic",
        generator_version="4.0",
        generation_source=GenerationSource.DETERMINISTIC,
        seed=seed,
        components=_components(combination),
        presentation=IncidentPresentation(
            title="Wielowarstwowy incydent produkcyjny",
            organization="Northstar Commerce",
            environment_label="Krytyczny stos usług",
            briefing=(
                "Publiczna aplikacja jest niedostępna, a monitoring wskazuje problemy "
                "na kilku odcinkach ścieżki żądania. Ustal zależności i przywróć stan nominalny."
            ),
            main_objective="Przywróć dostępność aplikacji i prawidłową komunikację całej ścieżki zależności.",
            ticket_reference=f"HARD-{seed % 100000:05d}",
            tags=("hard", "dependencies", "diagnostyka"),
            estimated_time_minutes=45,
        ),
        initial_world_state=InitialWorldState(
            environment_id=HARD_ENVIRONMENT_ARCHETYPE,
            environment_version="4.0",
            map=_map_snapshot("host-client-01", "host-data-01"),
            resources=tuple(resources),
        ),
        faults=faults,
        fault_relation=FaultRelation(
            relation_type=combination.relation_type,
            primary_fault_id="fault-primary",
            secondary_fault_id="fault-secondary",
        ),
        symptoms=(
            Symptom(
                symptom_id="symptom-public-path",
                symptom_type=HARD_SYMPTOM_ARCHETYPE,
                source_resource_id="endpoint-portal",
                visibility=SymptomVisibility.MONITORING,
                data=_fields(observed_state="unreachable"),
            ),
            Symptom(
                symptom_id="symptom-internal-path",
                symptom_type="dependency_path_degraded",
                source_resource_id="endpoint-primary-path",
                visibility=SymptomVisibility.MONITORING,
                data=_fields(observed_state="unhealthy"),
            ),
        ),
        objectives=(
            Objective(
                objective_id="restore-internal-communication",
                label="Przywróć prawidłową komunikację między zależnościami",
                order=1,
                objective_type=ObjectiveType.RESTORE_DEPENDENCY,
                completion_condition=CompletionCondition(
                    resource_id="endpoint-primary-path",
                    field="current_state",
                    operator=ConditionOperator.EQUALS,
                    expected="healthy",
                ),
            ),
            Objective(
                objective_id="restore-nominal-environment",
                label="Doprowadź środowisko do pełnego stanu nominalnego",
                order=2,
                objective_type=ObjectiveType.VERIFY_END_TO_END,
                completion_condition=CompletionCondition(
                    resource_id="endpoint-portal",
                    field="current_state",
                    operator=ConditionOperator.EQUALS,
                    expected="healthy",
                ),
                completion_fact_ids=("endpoint-healthy:host-edge-01:80",),
            ),
        ),
        capabilities=CapabilitySet(
            interfaces=(
                InterfaceCapability.TERMINAL,
                InterfaceCapability.FILE_EDITOR,
                InterfaceCapability.MONITORING,
            ),
            command_capability_ids=tuple(HANDLERS),
        ),
        scoring=ScoringRules(
            policy_id="scoring.strict",
            initial_score=1800,
            command_cost=12,
            solution_penalty=700,
            solution_score_cap=750,
        ),
        hints=(
            Hint(
                order=1,
                text="Porównaj stan kolejnych odcinków ścieżki i zweryfikuj ponownie symptomy po każdej zmianie.",
                cost=100,
            ),
        ),
        solution=_renumber(steps),
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
            ConfigurationRequirement(
                requirement_id="config-proxy-upstream",
                service_id="service-proxy",
                host_id="host-edge-01",
                file_resource_id="file-proxy-config",
            ),
        ),
        symptom_propagation=(
            SymptomPropagationRule(
                rule_id="propagate-primary-recovery",
                dependency_id=primary_dependency,
                affected_resource_id="endpoint-primary-path",
                unhealthy_state="unhealthy",
                healthy_state="healthy",
            ),
            SymptomPropagationRule(
                rule_id="propagate-public-recovery",
                dependency_id="dep-external-proxy",
                affected_resource_id="endpoint-portal",
                unhealthy_state="unreachable",
                healthy_state="healthy",
            ),
        ),
        post_incident=PostIncidentDefinition(
            root_cause=(
                f"Łańcuch dwóch powiązanych problemów: {repair_labels[combination.primary_fault_category]} "
                f"oraz {repair_labels[combination.secondary_fault_category]}."
            ),
            affected_service_ids=("service-proxy", "service-api", "service-database"),
            repair_capability_ids=combination.required_capabilities,
            root_cause_chain=(
                repair_labels[combination.primary_fault_category],
                repair_labels[combination.secondary_fault_category],
            ),
            primary_fault=repair_labels[combination.primary_fault_category],
            secondary_fault=repair_labels[combination.secondary_fault_category],
            impact_path=("sonda zewnętrzna", "reverse proxy", "API", "usługa danych"),
            repair_sequence=tuple(
                repair_labels[category] for category in combination.reference_repair_order
            ),
            partial_recovery_explanation=combination.symptom_progression[1].summary,
            learning_summary=(
                "Po każdej naprawie ponownie sprawdzaj całą ścieżkę. Zmiana symptomu nie oznacza jeszcze pełnego usunięcia incydentu."
            ),
        ),
    )
