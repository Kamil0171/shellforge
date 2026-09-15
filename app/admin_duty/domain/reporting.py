from collections.abc import Iterable
from enum import StrEnum
from types import MappingProxyType
from urllib.parse import urlsplit

from pydantic import Field

from app.admin_duty.domain.definition import (
    FrozenDomainModel,
    Identifier,
    IncidentDefinition,
    IncidentRecoveryState,
    PostIncidentDefinition,
    ResourceType,
)
from app.admin_duty.domain.difficulty import DifficultyLevel
from app.admin_duty.domain.runtime import CommandRecord, SessionRuntimeState


class CommandClassification(StrEnum):
    DIAGNOSTIC = "diagnostic"
    REPAIR = "repair"
    VERIFICATION = "verification"
    NAVIGATION = "navigation"
    UNNECESSARY = "unnecessary"


class CommandRelevance(StrEnum):
    DIRECT = "direct"
    SUPPORTING = "supporting"
    UNRELATED = "unrelated"


class CommandPhase(StrEnum):
    DIAGNOSIS = "diagnosis"
    REPAIR = "repair"
    PARTIAL_RECOVERY = "partial_recovery"
    VERIFICATION = "verification"


class KeySignalPhase(StrEnum):
    INITIAL = "initial"
    PARTIAL_RECOVERY = "partial_recovery"
    RESOLVED = "resolved"


class FaultReportProfile(FrozenDomainModel):
    category_id: Identifier
    fault_type: Identifier
    root_cause: str | None = Field(default=None, min_length=1, max_length=1000)
    diagnostic_capability_ids: tuple[Identifier, ...] = Field(default=(), max_length=32)
    repair_capability_ids: tuple[Identifier, ...] = Field(default=(), max_length=32)
    verification_capability_ids: tuple[Identifier, ...] = Field(
        default=(), max_length=32
    )
    key_signals: tuple[str, ...] = Field(min_length=2, max_length=6)
    learning_points: tuple[str, ...] = Field(min_length=2, max_length=5)
    real_world_takeaways: tuple[str, ...] = Field(min_length=2, max_length=4)


class PostIncidentCommandReview(FrozenDomainModel):
    order: int = Field(ge=1)
    command: str = Field(min_length=1, max_length=1024)
    host: str = Field(min_length=1, max_length=253)
    classification: CommandClassification
    relevance: CommandRelevance
    explanation: str = Field(min_length=1, max_length=500)
    phase: CommandPhase
    success: bool


class PostIncidentEfficiency(FrozenDomainModel):
    commands_total: int = Field(ge=0)
    diagnostic_commands: int = Field(ge=0)
    repair_commands: int = Field(ge=0)
    verification_commands: int = Field(ge=0)
    navigation_commands: int = Field(ge=0)
    unnecessary_commands: int = Field(ge=0)
    useful_commands: int = Field(ge=0)
    diagnostic_efficiency: float | None = Field(default=None, ge=0, le=1)
    hints_used: int = Field(ge=0)
    time_to_resolve_seconds: int | None = Field(default=None, ge=0)


class PostIncidentKeySignal(FrozenDomainModel):
    phase: KeySignalPhase
    signal: str = Field(min_length=1, max_length=500)


class PostIncidentRepairStep(FrozenDomainModel):
    order: int = Field(ge=1)
    description: str = Field(min_length=1, max_length=600)
    phase: CommandPhase


class PostIncidentAnalysis(FrozenDomainModel):
    incident_summary: str = Field(min_length=1, max_length=1200)
    impact_path: tuple[str, ...] = Field(min_length=1, max_length=16)
    command_review: tuple[PostIncidentCommandReview, ...] = Field(max_length=512)
    efficiency: PostIncidentEfficiency
    key_signals: tuple[PostIncidentKeySignal, ...] = Field(min_length=2, max_length=8)
    repair_sequence: tuple[PostIncidentRepairStep, ...] = Field(max_length=32)
    repair_commands: tuple[str, ...] = Field(max_length=512)
    partial_recovery_seen: bool
    partial_recovery_explanation: str | None = Field(
        default=None, min_length=1, max_length=1000
    )
    learning_points: tuple[str, ...] = Field(min_length=2, max_length=5)
    real_world_takeaways: tuple[str, ...] = Field(min_length=2, max_length=4)


def _profile(
    category_id,
    *,
    root_cause=None,
    diagnostic=(),
    repair=(),
    verification=(),
    signals,
    learning,
    real_world,
):
    return FaultReportProfile(
        category_id=category_id,
        fault_type=category_id.replace("-", "_"),
        root_cause=root_cause,
        diagnostic_capability_ids=diagnostic,
        repair_capability_ids=repair,
        verification_capability_ids=verification,
        key_signals=signals,
        learning_points=learning,
        real_world_takeaways=real_world,
    )


_SYSTEMD_DIAGNOSTIC = ("systemd.status", "systemd.cat", "journal.read")
_SYSTEMD_VERIFICATION = ("systemd.status", "systemd.is-active", "journal.read")
_NETWORK_DIAGNOSTIC = (
    "network.curl",
    "network.ping",
    "network.getent",
    "network.dig",
    "network.listeners",
)


FAULT_REPORT_PROFILES = (
    _profile(
        "systemd-service-failed",
        root_cause="Proces usługi zakończył się błędem; jednostka wymagała ponownego uruchomienia.",
        diagnostic=("systemd.status", "journal.read", "processes.list"),
        repair=("systemd.restart", "systemd.start"),
        verification=_SYSTEMD_VERIFICATION,
        signals=(
            "Stan jednostki systemd wskazywał awarię procesu.",
            "Dziennik usługi pozwalał odróżnić problem procesu od problemu sieciowego.",
            "Po ponownym uruchomieniu jednostka wróciła do stanu aktywnego.",
        ),
        learning=(
            "Stan failed w systemd jest punktem wyjścia do dalszej diagnostyki, a nie pełną przyczyną awarii.",
            "Po restarcie warto ponownie sprawdzić stan jednostki i dostępność usługi.",
        ),
        real_world=(
            "Zacznij od systemctl status, a następnie sprawdź journalctl -u dla tej samej jednostki.",
            "Po restarcie potwierdź zarówno stan procesu, jak i działanie punktu końcowego.",
        ),
    ),
    _profile(
        "systemd-wrong-exec-start",
        root_cause="ExecStart jednostki systemd wskazywał nieprawidłowy plik wykonywalny.",
        diagnostic=(*_SYSTEMD_DIAGNOSTIC, "filesystem.read"),
        repair=("filesystem.edit", "systemd.daemon-reload", "systemd.restart"),
        verification=_SYSTEMD_VERIFICATION,
        signals=(
            "Jednostka nie mogła uruchomić procesu wskazanego przez ExecStart.",
            "Zawartość unit file różniła się od oczekiwanej konfiguracji startowej.",
            "Po zmianie pliku konieczne było przeładowanie konfiguracji systemd.",
        ),
        learning=(
            "Zmiana unit file na dysku nie aktualizuje automatycznie konfiguracji używanej przez systemd.",
            "systemctl cat i journalctl pomagają połączyć konfigurację ExecStart z błędem uruchomienia.",
        ),
        real_world=(
            "Porównaj systemctl cat z komunikatem startowym w journalctl -u.",
            "Po edycji wykonaj systemctl daemon-reload, restart i ponowną weryfikację.",
        ),
    ),
    _profile(
        "systemd-missing-environment-variable",
        root_cause="W konfiguracji jednostki systemd brakowało wymaganej zmiennej środowiskowej.",
        diagnostic=_SYSTEMD_DIAGNOSTIC,
        repair=("filesystem.edit", "systemd.daemon-reload", "systemd.restart"),
        verification=_SYSTEMD_VERIFICATION,
        signals=(
            "Proces kończył pracę na etapie inicjalizacji.",
            "Konfiguracja jednostki nie przekazywała kompletnego środowiska procesu.",
            "Usługa uruchomiła się po poprawieniu konfiguracji i jej przeładowaniu.",
        ),
        learning=(
            "Środowisko procesu systemd wynika z konfiguracji jednostki, a nie z interaktywnej powłoki administratora.",
            "Log startowy często wskazuje brak ustawienia szybciej niż analiza kodu aplikacji.",
        ),
        real_world=(
            "Sprawdź status, journalctl -u oraz efektywną konfigurację przez systemctl cat.",
            "Po korekcie wykonaj daemon-reload i zweryfikuj proces bez ujawniania wartości sekretów.",
        ),
    ),
    _profile(
        "systemd-permission-denied",
        root_cause="Plik wykonywalny usługi nie miał wymaganego uprawnienia do wykonania.",
        diagnostic=("systemd.status", "journal.read", "filesystem.path-stat"),
        repair=("filesystem.chmod", "systemd.restart"),
        verification=("filesystem.path-stat", *_SYSTEMD_VERIFICATION),
        signals=(
            "Dziennik systemd wskazywał odmowę uruchomienia pliku wykonywalnego.",
            "Tryb pliku nie zawierał wymaganego prawa wykonania.",
            "Po korekcie uprawnień proces mógł zostać uruchomiony.",
        ),
        learning=(
            "Poprawna ścieżka ExecStart nie wystarcza, jeśli plik nie ma właściwych praw dostępu.",
            "stat pozwala potwierdzić tryb pliku przed zmianą i po niej.",
        ),
        real_world=(
            "Po komunikacie Permission denied sprawdź właściciela, tryb i kontekst SELinux pliku.",
            "Zmieniaj tylko wymagane uprawnienia, a następnie ponownie uruchom i sprawdź usługę.",
        ),
    ),
    _profile(
        "dependency-firewall-blocked",
        diagnostic=(*_NETWORK_DIAGNOSTIC, "firewalld.command"),
        repair=("firewalld.command",),
        verification=("network.curl", "network.ping", "firewalld.command"),
        signals=(
            "Proces zależności działał, lecz połączenie do wymaganego portu nie dochodziło do celu.",
            "Aktywna strefa firewalld nie udostępniała wymaganego ruchu.",
            "Po aktywacji reguły połączenie między usługami zaczęło działać.",
        ),
        learning=(
            "Stan running usługi nie oznacza jeszcze, że jest ona osiągalna przez sieć.",
            "Konfigurację runtime i permanent firewalld trzeba rozpatrywać oddzielnie.",
        ),
        real_world=(
            "Potwierdź listener i łączność, a potem sprawdź aktywną strefę przez firewall-cmd.",
            "Po trwałej zmianie przeładuj reguły i ponownie wykonaj test z hosta źródłowego.",
        ),
    ),
    _profile(
        "dependency-package-missing",
        diagnostic=("packages.rpm", "packages.command", *_SYSTEMD_DIAGNOSTIC),
        repair=("packages.command", "systemd.restart"),
        verification=("packages.rpm", "systemd.status", "network.curl"),
        signals=(
            "Usługa nie mogła załadować wymaganej zależności pakietowej.",
            "Baza RPM nie zawierała pakietu wymaganego przez proces.",
            "Po instalacji zależności usługa mogła zostać uruchomiona.",
        ),
        learning=(
            "Awaria po wdrożeniu może wynikać z zależności systemowej, mimo że konfiguracja aplikacji jest poprawna.",
            "rpm i dnf pokazują inne perspektywy: stan instalacji oraz dostępność pakietu w repozytorium.",
        ),
        real_world=(
            "Po błędzie biblioteki sprawdź pakiet przez rpm -q oraz jego dostępność przez dnf info.",
            "Po instalacji uruchom usługę ponownie i wykonaj test funkcjonalny.",
        ),
    ),
    _profile(
        "selinux-context-invalid",
        diagnostic=(
            "selinux.getenforce",
            "selinux.sestatus",
            "selinux.semanage",
            *_SYSTEMD_DIAGNOSTIC,
        ),
        repair=("selinux.restorecon", "systemd.restart"),
        verification=("systemd.status", "network.curl", "selinux.getenforce"),
        signals=(
            "Lokalny proces był blokowany mimo poprawnych klasycznych uprawnień pliku.",
            "Dziennik wskazywał odmowę wynikającą z polityki SELinux.",
            "Przywrócenie oczekiwanego kontekstu umożliwiło start usługi.",
        ),
        learning=(
            "Poprawne chmod i właściciel nie wykluczają blokady przez politykę SELinux.",
            "Przywrócenie właściwego kontekstu jest bezpieczniejsze niż trwałe wyłączanie ochrony.",
        ),
        real_world=(
            "Sprawdź tryb SELinux oraz wpisy AVC, zanim zmienisz politykę lub uprawnienia.",
            "Użyj restorecon dla znanej ścieżki i ponownie zweryfikuj usługę.",
        ),
    ),
    _profile(
        "networkmanager-dns-invalid",
        diagnostic=(
            *_NETWORK_DIAGNOSTIC,
            "networkmanager.command",
            "network.addr",
            "network.route",
        ),
        repair=("networkmanager.command",),
        verification=(
            "network.dig",
            "network.getent",
            "network.curl",
            "networkmanager.command",
        ),
        signals=(
            "Host miał łączność IP, ale nie potrafił rozwiązać nazwy zależności.",
            "Aktywny profil NetworkManager nie zawierał oczekiwanego serwera DNS.",
            "Po aktywacji poprawionego profilu rozwiązywanie nazw wróciło.",
        ),
        learning=(
            "Działający interfejs i trasa nie gwarantują poprawnego DNS.",
            "Zmiana profilu NetworkManager wymaga ponownej aktywacji, aby wpłynęła na bieżące połączenie.",
        ),
        real_world=(
            "Oddziel test łączności po IP od testu rozwiązywania nazwy przez dig lub getent.",
            "Sprawdź aktywny profil nmcli, popraw DNS, aktywuj profil i powtórz test aplikacyjny.",
        ),
    ),
    _profile(
        "external-firewall-mismatch",
        diagnostic=(
            "network.curl",
            "network.listeners",
            "firewalld.command",
            "systemd.status",
        ),
        repair=("firewalld.command",),
        verification=("network.curl", "firewalld.command"),
        signals=(
            "Usługa brzegowa działała lokalnie, lecz publiczny port pozostawał nieosiągalny.",
            "Reguły firewalld nie odpowiadały portowi używanemu przez punkt wejścia.",
            "Po korekcie reguły publiczny test HTTP zakończył się powodzeniem.",
        ),
        learning=(
            "Healthy service i publiczna dostępność są osobnymi warstwami diagnostycznymi.",
            "Port listenera, adres testu i reguła firewalld muszą opisywać tę samą ścieżkę.",
        ),
        real_world=(
            "Porównaj ss -lntp, lokalny curl i test z zewnętrznego hosta.",
            "Sprawdź aktywną strefę oraz usługi i porty firewalld przed zmianą reguł.",
        ),
    ),
    _profile(
        "service-config-invalid",
        diagnostic=(
            *_SYSTEMD_DIAGNOSTIC,
            "filesystem.read",
            "filesystem.grep",
            "network.curl",
        ),
        repair=("filesystem.edit", "systemd.restart"),
        verification=("systemd.status", "network.curl"),
        signals=(
            "Proces odczytywał niespójną konfigurację zależności.",
            "Wartość w kontrolowanym pliku nie odpowiadała oczekiwanemu środowisku.",
            "Po zapisie poprawnej konfiguracji stan zależności wrócił do normy.",
        ),
        learning=(
            "Błąd konfiguracji może pozostawić proces uruchomiony, ale funkcjonalnie niezdrowy.",
            "Weryfikacja powinna objąć zarówno plik, jak i zachowanie usługi po restarcie.",
        ),
        real_world=(
            "Porównaj aktywną konfigurację z wymaganiami zależności i logami aplikacji.",
            "Po zmianie wykonaj kontrolowany restart oraz test end-to-end.",
        ),
    ),
    _profile(
        "dependency-port-mismatch",
        diagnostic=(
            "network.curl",
            "network.listeners",
            "filesystem.read",
            "filesystem.grep",
            "systemd.status",
        ),
        repair=("filesystem.edit", "systemd.restart"),
        verification=("network.curl", "network.listeners", "systemd.status"),
        signals=(
            "Usługa docelowa nasłuchiwała, ale klient kierował ruch na inny port.",
            "Konfiguracja upstream nie odpowiadała faktycznemu listenerowi zależności.",
            "Po ujednoliceniu portu cała ścieżka żądania zaczęła działać.",
        ),
        learning=(
            "Działające procesy mogą nadal tworzyć zerwaną ścieżkę przez rozbieżność portów.",
            "Listener po stronie celu trzeba porównać z konfiguracją klienta lub proxy.",
        ),
        real_world=(
            "Sprawdź ss -lntp na hoście docelowym i konfigurację upstream po stronie klienta.",
            "Po korekcie wykonaj restart wymaganej usługi i test end-to-end.",
        ),
    ),
    _profile(
        "networkmanager-connection-inactive",
        diagnostic=(
            "networkmanager.command",
            "network.addr",
            "network.link",
            "network.route",
            "network.curl",
            "network.ping",
        ),
        repair=("networkmanager.command",),
        verification=(
            "networkmanager.command",
            "network.addr",
            "network.ping",
            "network.curl",
        ),
        signals=(
            "Interfejs hosta nie miał aktywnego połączenia NetworkManager.",
            "Brak aktywnego profilu odcinał kolejne zależności sieciowe.",
            "Po aktywacji połączenia host odzyskał łączność z siecią.",
        ),
        learning=(
            "Stan procesu aplikacji nie opisuje stanu interfejsu i profilu sieciowego.",
            "Odzyskanie linku może ujawnić kolejny niezależny problem w dalszej części ścieżki.",
        ),
        real_world=(
            "Sprawdź nmcli device status, adresy i trasę przed analizą wyższych warstw.",
            "Po aktywacji profilu powtórz testy DNS, portu i aplikacji.",
        ),
    ),
    _profile(
        "service-config-permission-denied",
        diagnostic=(
            "systemd.status",
            "journal.read",
            "filesystem.path-stat",
            "filesystem.read",
        ),
        repair=("filesystem.chmod", "filesystem.chown", "systemd.restart"),
        verification=("filesystem.path-stat", "systemd.status", "network.curl"),
        signals=(
            "Proces działał, ale nie miał dostępu do wymaganego pliku konfiguracji.",
            "Tryb i właściciel pliku nie odpowiadały użytkownikowi usługi.",
            "Po przywróceniu dostępu zależność aplikacyjna odzyskała zdrowie.",
        ),
        learning=(
            "Poprawna treść pliku nie wystarcza, jeśli proces nie może go odczytać.",
            "Tryb, właściciel i użytkownik jednostki trzeba analizować razem.",
        ),
        real_world=(
            "Porównaj systemctl status i journalctl -u z wynikiem stat dla wskazanego pliku.",
            "Przywróć najmniejszy wymagany dostęp i ponownie wykonaj test funkcjonalny.",
        ),
    ),
    _profile(
        "systemd-stale-unit-config",
        diagnostic=(*_SYSTEMD_DIAGNOSTIC, "filesystem.read"),
        repair=("filesystem.edit", "systemd.daemon-reload", "systemd.restart"),
        verification=_SYSTEMD_VERIFICATION,
        signals=(
            "Jednostka wskazywała nieaktualny cel uruchomieniowy.",
            "Zmiana pliku na dysku wymagała przeładowania cache systemd.",
            "Po daemon-reload i restarcie proces uruchomił właściwy plik.",
        ),
        learning=(
            "systemd używa załadowanej definicji jednostki, a nie każdej niezapisanej zmiany operatora.",
            "Edycja unit file, daemon-reload i restart pełnią trzy różne role.",
        ),
        real_world=(
            "Porównaj status, journal oraz systemctl cat przed zmianą jednostki.",
            "Po zapisie wykonaj daemon-reload, restart i niezależny test usługi.",
        ),
    ),
    _profile(
        "dependency-dns-name-mismatch",
        diagnostic=(*_NETWORK_DIAGNOSTIC, "filesystem.read", "systemd.status"),
        repair=("filesystem.edit", "systemd.restart"),
        verification=("network.dig", "network.ping", "network.curl", "systemd.status"),
        signals=(
            "Host zależności odpowiadał po adresie IP.",
            "Nazwa zapisana w konfiguracji nie miała rekordu DNS.",
            "Po wskazaniu prawidłowej nazwy aplikacja odzyskała połączenie.",
        ),
        learning=(
            "Osiągalność IP i rozwiązywanie nazwy są osobnymi etapami diagnostyki.",
            "Błędna nazwa usługi może wyglądać jak awaria sieci lub procesu downstream.",
        ),
        real_world=(
            "Porównaj ping lub curl po IP z dig i getent dla nazwy używanej przez aplikację.",
            "Po zmianie konfiguracji powtórz test DNS oraz test end-to-end.",
        ),
    ),
    _profile(
        "selinux-proxy-context-invalid",
        diagnostic=(
            "systemd.status",
            "journal.read",
            "selinux.getenforce",
            "selinux.semanage",
        ),
        repair=("selinux.restorecon", "systemd.restart"),
        verification=("systemd.status", "journal.read", "network.curl"),
        signals=(
            "Reverse proxy kończył start mimo poprawnych tradycyjnych uprawnień.",
            "Dziennik wskazywał odmowę wykonania przez SELinux.",
            "Przywrócenie oczekiwanego kontekstu umożliwiło uruchomienie proxy.",
        ),
        learning=(
            "Kontekst SELinux jest niezależny od właściciela i bitów trybu pliku.",
            "restorecon przywraca etykietę wynikającą z polityki bez wyłączania ochrony.",
        ),
        real_world=(
            "Sprawdź journal i tryb SELinux przed zmianą tradycyjnych uprawnień.",
            "Po restorecon uruchom usługę ponownie i sprawdź publiczny endpoint.",
        ),
    ),
)

FAULT_REPORT_PROFILES_BY_TYPE = MappingProxyType(
    {profile.fault_type: profile for profile in FAULT_REPORT_PROFILES}
)
FAULT_REPORT_PROFILES_BY_CATEGORY = MappingProxyType(
    {profile.category_id: profile for profile in FAULT_REPORT_PROFILES}
)


def get_fault_report_profile(fault_type: str) -> FaultReportProfile | None:
    return FAULT_REPORT_PROFILES_BY_TYPE.get(fault_type)


def get_fault_root_cause(category_id: str) -> str:
    profile = FAULT_REPORT_PROFILES_BY_CATEGORY.get(category_id)
    if profile is None or profile.root_cause is None:
        raise ValueError(f"Brak deterministycznej przyczyny dla faultu {category_id}.")
    return profile.root_cause


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if value))


def _resource_label(definition: IncidentDefinition, resource_id: str) -> str:
    resource = next(
        (
            item
            for item in definition.initial_world_state.resources
            if item.resource_id == resource_id
        ),
        None,
    )
    if resource is None:
        return resource_id
    fields = {field.key: field.value for field in resource.attributes}
    for key in ("hostname", "service_name", "name"):
        value = fields.get(key)
        if isinstance(value, str):
            return value
    return resource_id


def _host_label(state: SessionRuntimeState, host_id: str) -> str:
    runtime = state.host_runtimes.get(host_id)
    return runtime.hostname if runtime is not None else host_id


def _base_classification(record: CommandRecord) -> CommandClassification:
    capability = record.capability_id
    if capability in {"shell.pwd", "shell.cd", "remote.ssh", "filesystem.list"}:
        return CommandClassification.NAVIGATION
    if capability == "firewalld.command":
        option = next(
            (argument for argument in record.arguments if argument != "--permanent"),
            "",
        )
        return (
            CommandClassification.REPAIR
            if option == "--reload" or option.startswith(("--add-", "--remove-"))
            else CommandClassification.DIAGNOSTIC
        )
    if capability == "networkmanager.command":
        return (
            CommandClassification.DIAGNOSTIC
            if record.arguments[:2] in {("device", "status"), ("connection", "show")}
            else CommandClassification.REPAIR
        )
    if capability == "packages.command":
        return (
            CommandClassification.REPAIR
            if record.arguments
            and record.arguments[0] in {"install", "remove", "update", "clean"}
            else CommandClassification.DIAGNOSTIC
        )
    if capability.startswith("selinux."):
        return (
            CommandClassification.REPAIR
            if capability in {"selinux.setenforce", "selinux.restorecon"}
            else CommandClassification.DIAGNOSTIC
        )
    if capability in {
        "systemd.start",
        "systemd.stop",
        "systemd.restart",
        "systemd.enable",
        "systemd.disable",
        "systemd.daemon-reload",
        "filesystem.mkdir",
        "filesystem.touch",
        "filesystem.copy",
        "filesystem.move",
        "filesystem.remove",
        "filesystem.rmdir",
        "filesystem.chmod",
        "filesystem.chown",
        "filesystem.edit",
    }:
        return CommandClassification.REPAIR
    return CommandClassification.DIAGNOSTIC


def _relevant_host_ids(
    definition: IncidentDefinition, post_incident: PostIncidentDefinition
) -> set[str]:
    resource_by_id = {
        resource.resource_id: resource
        for resource in definition.initial_world_state.resources
    }
    resource_ids = {
        *(fault.target_resource_id for fault in definition.faults),
        *post_incident.affected_service_ids,
    }
    for dependency in definition.service_dependencies:
        resource_ids.update(
            {
                dependency.source_service_id,
                dependency.target_service_id,
                dependency.source_host_id,
                dependency.target_host_id,
            }
        )
    hosts = set()
    for resource_id in resource_ids:
        resource = resource_by_id.get(resource_id)
        if resource is None:
            continue
        if resource.resource_type is ResourceType.HOST:
            hosts.add(resource.resource_id)
        elif resource.parent_id is not None:
            hosts.add(resource.parent_id)
    return hosts


def _relevant_resource_ids(
    definition: IncidentDefinition,
    post_incident: PostIncidentDefinition,
) -> set[str]:
    resource_ids = {
        *(fault.target_resource_id for fault in definition.faults),
        *post_incident.affected_service_ids,
    }
    for dependency in definition.service_dependencies:
        resource_ids.update(
            {
                dependency.source_service_id,
                dependency.target_service_id,
                dependency.source_host_id,
                dependency.target_host_id,
            }
        )
    for requirement in definition.configuration_requirements:
        resource_ids.update(
            {
                requirement.file_resource_id,
                requirement.service_id,
                requirement.host_id,
            }
        )
    for requirement in definition.package_requirements:
        resource_ids.update({requirement.service_id, requirement.host_id})
    resource_by_id = {
        resource.resource_id: resource
        for resource in definition.initial_world_state.resources
    }
    pending = list(resource_ids)
    while pending:
        resource = resource_by_id.get(pending.pop())
        if resource is None:
            continue
        for dependency_id in resource.dependencies:
            if dependency_id not in resource_ids:
                resource_ids.add(dependency_id)
                pending.append(dependency_id)
    resource_ids.update(
        resource.resource_id
        for resource in definition.initial_world_state.resources
        if resource.resource_type in {ResourceType.DOMAIN, ResourceType.ENDPOINT}
    )
    return resource_ids


def _relevant_aliases(
    definition: IncidentDefinition,
    post_incident: PostIncidentDefinition,
) -> set[str]:
    resource_ids = _relevant_resource_ids(definition, post_incident)
    aliases = set(resource_ids)
    for resource in definition.initial_world_state.resources:
        if resource.resource_id not in resource_ids:
            continue
        for field in resource.attributes:
            if isinstance(field.value, str):
                aliases.add(field.value)
                aliases.add(field.value.removesuffix(".service"))
    return aliases


def _network_target(resource_id: str) -> str:
    if "://" in resource_id:
        return urlsplit(resource_id).hostname or resource_id
    return resource_id.rsplit(":", 1)[0] if resource_id.count(":") == 1 else resource_id


def _target_is_relevant(
    definition: IncidentDefinition,
    record: CommandRecord,
    aliases: set[str],
) -> bool:
    capability = record.capability_id
    if capability == "packages.command":
        package_names = {
            requirement.package_name for requirement in definition.package_requirements
        }
        requested = set(record.arguments[1:]) - {"installed", "all"}
        return not requested or bool(requested & package_names)
    if capability == "packages.rpm":
        package_names = {
            requirement.package_name for requirement in definition.package_requirements
        }
        return record.resource_id == "." or record.resource_id in package_names
    if capability == "firewalld.command":
        option = next(
            (argument for argument in record.arguments if argument != "--permanent"),
            "",
        )
        if not option.startswith(("--add-", "--remove-")):
            return True
        _, _, value = option.partition("=")
        relevant_ports = {
            f"{dependency.port}/tcp" for dependency in definition.service_dependencies
        }
        relevant_services = {
            service
            for dependency in definition.service_dependencies
            for service, port in (("http", 80), ("https", 443))
            if dependency.port == port
        }
        return value in relevant_ports | relevant_services
    if capability.startswith("network.") and capability not in {
        "network.addr",
        "network.link",
        "network.route",
        "network.listeners",
    }:
        return _network_target(record.resource_id) in aliases
    if capability.startswith(("systemd.", "journal.")):
        return (
            record.resource_id == "."
            or record.resource_id.removesuffix(".service") in aliases
        )
    if capability.startswith("filesystem."):
        return record.resource_id == "." or any(
            record.resource_id == alias
            or record.resource_id.startswith(alias.rstrip("/") + "/")
            for alias in aliases
            if alias.startswith("/")
        )
    return True


def _command_explanation(
    classification: CommandClassification,
    relevance: CommandRelevance,
    record: CommandRecord,
) -> str:
    if classification is CommandClassification.NAVIGATION:
        return "Polecenie zmieniało lub potwierdzało kontekst pracy w wirtualnym środowisku."
    if classification is CommandClassification.UNNECESSARY:
        return (
            "Polecenie nie dostarczało sygnału ani zmiany istotnej dla tego incydentu."
        )
    subsystem = record.capability_id.split(".", 1)[0]
    labels = {
        "filesystem": "plików i konfiguracji",
        "firewalld": "reguł zapory sieciowej",
        "journal": "dziennika usługi",
        "network": "ścieżki sieciowej",
        "networkmanager": "połączenia NetworkManager",
        "packages": "zależności pakietowych",
        "selinux": "polityki SELinux",
        "systemd": "stanu usługi systemd",
    }
    subject = labels.get(subsystem, "stanu środowiska")
    if classification is CommandClassification.DIAGNOSTIC:
        text = f"Polecenie dostarczało danych diagnostycznych dotyczących {subject}."
    elif classification is CommandClassification.VERIFICATION:
        text = (
            f"Polecenie weryfikowało efekt wcześniejszej naprawy w obszarze {subject}."
        )
    else:
        text = f"Polecenie wykonywało zmianę naprawczą w obszarze {subject}."
    if relevance is CommandRelevance.SUPPORTING:
        text += " Był to sygnał wspierający, wykonany poza głównym hostem problemu."
    if not record.success:
        text += " Polecenie nie zakończyło się powodzeniem, ale pozostało elementem ścieżki diagnostycznej."
    return text


def _phase_for(classification: CommandClassification, partial: bool) -> CommandPhase:
    if classification is CommandClassification.REPAIR:
        return CommandPhase.REPAIR
    if classification is CommandClassification.VERIFICATION:
        return CommandPhase.VERIFICATION
    if partial:
        return CommandPhase.PARTIAL_RECOVERY
    return CommandPhase.DIAGNOSIS


def _record_recovery_state(
    definition: IncidentDefinition,
    record: CommandRecord,
) -> IncidentRecoveryState:
    resolved_count = len(record.resolved_fault_ids)
    if resolved_count == 0:
        return IncidentRecoveryState.BROKEN
    if resolved_count < len(definition.faults):
        return IncidentRecoveryState.PARTIALLY_RECOVERED
    return IncidentRecoveryState.HEALTHY


def _review_commands(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    post_incident: PostIncidentDefinition,
    profiles: tuple[FaultReportProfile, ...],
) -> tuple[PostIncidentCommandReview, ...]:
    diagnostic = set(
        capability
        for profile in profiles
        for capability in profile.diagnostic_capability_ids
    )
    repair = set(post_incident.repair_capability_ids) | {
        capability
        for profile in profiles
        for capability in profile.repair_capability_ids
    }
    verification = {
        capability
        for profile in profiles
        for capability in profile.verification_capability_ids
    }
    relevant_capabilities = diagnostic | repair | verification
    relevant_hosts = _relevant_host_ids(definition, post_incident)
    relevant_aliases = _relevant_aliases(definition, post_incident)
    repair_seen = False
    previous_recovery = IncidentRecoveryState.BROKEN
    review = []
    for record in state.command_history:
        base = _base_classification(record)
        if base is CommandClassification.NAVIGATION:
            relevance = CommandRelevance.SUPPORTING
            classification = base
        elif (
            record.capability_id not in relevant_capabilities
            or not _target_is_relevant(definition, record, relevant_aliases)
        ):
            relevance = CommandRelevance.UNRELATED
            classification = CommandClassification.UNNECESSARY
        else:
            relevance = (
                CommandRelevance.DIRECT
                if record.host_id in relevant_hosts
                else CommandRelevance.SUPPORTING
            )
            if (
                base is CommandClassification.DIAGNOSTIC
                and record.capability_id in verification
                and repair_seen
            ):
                classification = CommandClassification.VERIFICATION
            else:
                classification = base
        partial = previous_recovery is IncidentRecoveryState.PARTIALLY_RECOVERED
        review.append(
            PostIncidentCommandReview(
                order=record.order,
                command=record.command,
                host=_host_label(state, record.host_id),
                classification=classification,
                relevance=relevance,
                explanation=_command_explanation(classification, relevance, record),
                phase=_phase_for(classification, partial),
                success=record.success,
            )
        )
        if (
            classification is CommandClassification.REPAIR
            and relevance is not CommandRelevance.UNRELATED
            and record.success
            and record.environment_changed
        ):
            repair_seen = True
        previous_recovery = _record_recovery_state(definition, record)
    return tuple(review)


def _efficiency(
    state: SessionRuntimeState,
    review: tuple[PostIncidentCommandReview, ...],
) -> PostIncidentEfficiency:
    counts = {
        classification: sum(item.classification is classification for item in review)
        for classification in CommandClassification
    }
    total = len(review)
    useful = (
        counts[CommandClassification.DIAGNOSTIC]
        + counts[CommandClassification.REPAIR]
        + counts[CommandClassification.VERIFICATION]
    )
    duration = None
    if state.command_history:
        duration = max(
            0,
            int(
                (
                    state.command_history[-1].occurred_at - state.created_at
                ).total_seconds()
            ),
        )
    return PostIncidentEfficiency(
        commands_total=total,
        diagnostic_commands=counts[CommandClassification.DIAGNOSTIC],
        repair_commands=counts[CommandClassification.REPAIR],
        verification_commands=counts[CommandClassification.VERIFICATION],
        navigation_commands=counts[CommandClassification.NAVIGATION],
        unnecessary_commands=counts[CommandClassification.UNNECESSARY],
        useful_commands=useful,
        diagnostic_efficiency=round(useful / total, 3) if total else None,
        hints_used=state.hints_used,
        time_to_resolve_seconds=duration,
    )


def _repair_description(record: CommandRecord, host: str) -> str:
    capability = record.capability_id
    arguments = record.arguments
    if capability == "filesystem.edit":
        return f"Zapisano poprawioną konfigurację na hoście {host}."
    if capability == "filesystem.chmod":
        return f"Przywrócono wymagane uprawnienia pliku na hoście {host}."
    if capability == "filesystem.chown":
        return f"Przywrócono właściwego właściciela pliku na hoście {host}."
    if capability == "systemd.daemon-reload":
        return f"Przeładowano konfigurację systemd na hoście {host}."
    if capability in {"systemd.restart", "systemd.start"}:
        return f"Uruchomiono ponownie właściwą usługę na hoście {host}."
    if capability == "selinux.restorecon":
        return f"Przywrócono oczekiwany kontekst SELinux na hoście {host}."
    if capability == "packages.command":
        action = arguments[0] if arguments else "zmianę"
        labels = {
            "install": "Zainstalowano",
            "remove": "Usunięto",
            "update": "Zaktualizowano",
        }
        return f"{labels.get(action, 'Wykonano zmianę pakietową dla')} wymaganą zależność na hoście {host}."
    if capability == "networkmanager.command":
        if arguments[:2] == ("connection", "modify"):
            return f"Poprawiono profil NetworkManager na hoście {host}."
        return f"Aktywowano poprawną konfigurację sieciową na hoście {host}."
    if capability == "firewalld.command":
        option = next((item for item in arguments if item != "--permanent"), "")
        if option == "--reload":
            return f"Przeładowano aktywne reguły firewalld na hoście {host}."
        return f"Skorygowano regułę firewalld na hoście {host}."
    return f"Wykonano skuteczną zmianę naprawczą na hoście {host}."


def _verification_description(item: PostIncidentCommandReview) -> str:
    return (
        f"Potwierdzono efekt naprawy poleceniem „{item.command}” na hoście {item.host}."
    )


def _repair_sequence(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
    review: tuple[PostIncidentCommandReview, ...],
    post_incident: PostIncidentDefinition,
) -> tuple[
    tuple[PostIncidentRepairStep, ...],
    tuple[str, ...],
    str | None,
]:
    review_by_order = {item.order: item for item in review}
    descriptions = []
    repair_commands = []
    partial_explanation = None
    previous_recovery = IncidentRecoveryState.BROKEN
    for record in state.command_history:
        item = review_by_order[record.order]
        if (
            item.classification is CommandClassification.REPAIR
            and item.relevance is not CommandRelevance.UNRELATED
            and record.success
            and record.environment_changed
        ):
            description = _repair_description(record, item.host)
            if not descriptions or descriptions[-1][0] != description:
                descriptions.append((description, CommandPhase.REPAIR))
            repair_commands.append(record.command)
        recovery_state = _record_recovery_state(definition, record)
        if (
            recovery_state is IncidentRecoveryState.PARTIALLY_RECOVERED
            and previous_recovery is not IncidentRecoveryState.PARTIALLY_RECOVERED
        ):
            resolved_id = record.resolved_fault_ids[0]
            relation = definition.fault_relation
            if (
                relation is not None
                and resolved_id == relation.primary_fault_id
                and post_incident.partial_recovery_explanation
            ):
                partial_explanation = post_incident.partial_recovery_explanation
            else:
                resolved_label = (
                    post_incident.primary_fault
                    if relation is not None and resolved_id == relation.primary_fault_id
                    else post_incident.secondary_fault
                )
                remaining_label = (
                    post_incident.secondary_fault
                    if relation is not None and resolved_id == relation.primary_fault_id
                    else post_incident.primary_fault
                )
                partial_explanation = (
                    f"Naprawiono pierwszy z faktycznie rozwiązanych problemów: {resolved_label}. "
                    f"Środowisko nadal wymagało usunięcia problemu: {remaining_label}."
                )
            descriptions.append(
                (
                    partial_explanation,
                    CommandPhase.PARTIAL_RECOVERY,
                )
            )
        previous_recovery = recovery_state
    verification = next(
        (
            item
            for item in reversed(review)
            if item.classification is CommandClassification.VERIFICATION
            and item.relevance is not CommandRelevance.UNRELATED
            and item.success
        ),
        None,
    )
    if descriptions and verification is not None:
        descriptions.append(
            (_verification_description(verification), CommandPhase.VERIFICATION)
        )
    return (
        tuple(
            PostIncidentRepairStep(order=index, description=text, phase=phase)
            for index, (text, phase) in enumerate(descriptions, 1)
        ),
        tuple(repair_commands),
        partial_explanation,
    )


def _impact_path(
    definition: IncidentDefinition,
    post_incident: PostIncidentDefinition,
) -> tuple[str, ...]:
    if post_incident.impact_path:
        return post_incident.impact_path
    dependency_resources = _unique(
        resource_id
        for dependency in definition.service_dependencies
        for resource_id in (
            dependency.source_service_id,
            dependency.target_service_id,
        )
    )
    resource_ids = dependency_resources or post_incident.affected_service_ids
    return _unique(
        _resource_label(definition, resource_id) for resource_id in resource_ids
    )


def _key_signals(
    definition: IncidentDefinition,
    profiles: tuple[FaultReportProfile, ...],
    post_incident: PostIncidentDefinition,
    partial_explanation: str | None,
) -> tuple[PostIncidentKeySignal, ...]:
    partial_seen = partial_explanation is not None
    if definition.difficulty is DifficultyLevel.EASY:
        values = [
            PostIncidentKeySignal(phase=KeySignalPhase.INITIAL, signal=signal)
            for signal in profiles[0].key_signals[:3]
        ]
    elif definition.difficulty is DifficultyLevel.MEDIUM:
        values = [
            PostIncidentKeySignal(phase=KeySignalPhase.INITIAL, signal=signal)
            for signal in profiles[0].key_signals[:3]
        ]
        values.append(
            PostIncidentKeySignal(
                phase=KeySignalPhase.RESOLVED,
                signal="Końcowa weryfikacja potwierdziła odtworzenie pełnej ścieżki zależności.",
            )
        )
    else:
        values = [
            PostIncidentKeySignal(phase=KeySignalPhase.INITIAL, signal=signal)
            for signal in profiles[0].key_signals[:2]
        ]
        if partial_seen:
            values.append(
                PostIncidentKeySignal(
                    phase=KeySignalPhase.PARTIAL_RECOVERY,
                    signal=partial_explanation,
                )
            )
        values.extend(
            PostIncidentKeySignal(
                phase=(
                    KeySignalPhase.PARTIAL_RECOVERY
                    if partial_seen
                    else KeySignalPhase.INITIAL
                ),
                signal=signal,
            )
            for signal in profiles[-1].key_signals[:2]
        )
        values.append(
            PostIncidentKeySignal(
                phase=KeySignalPhase.RESOLVED,
                signal="Dopiero końcowy test całego łańcucha potwierdził pełne odtworzenie środowiska.",
            )
        )
    return tuple(values[:8])


def _incident_summary(
    definition: IncidentDefinition,
    post_incident: PostIncidentDefinition,
) -> str:
    affected = ", ".join(
        _resource_label(definition, resource_id)
        for resource_id in post_incident.affected_service_ids
    )
    if definition.difficulty is DifficultyLevel.HARD:
        return (
            f"Incydent obejmował dwa powiązane problemy w ścieżce {affected}. "
            "Kolejne naprawy zmieniały obserwowane symptomy, aż pełna ścieżka wróciła do stanu nominalnego."
        )
    if definition.difficulty is DifficultyLevel.MEDIUM:
        return (
            f"Awaria zależności zakłóciła działanie ścieżki obejmującej {affected}. "
            "Po usunięciu przyczyny i weryfikacji end-to-end środowisko odzyskało poprawny stan."
        )
    return (
        f"Problem uniemożliwiał poprawne działanie usługi {affected}. "
        "Po rozpoznaniu przyczyny wykonane działania przywróciły jej prawidłowy stan."
    )


def build_post_incident_analysis(
    definition: IncidentDefinition,
    state: SessionRuntimeState,
) -> PostIncidentAnalysis:
    post_incident = definition.post_incident
    if post_incident is None:
        raise ValueError("Definicja nie zawiera danych post-incident.")
    profiles = tuple(
        profile
        for fault in definition.faults
        if (profile := get_fault_report_profile(fault.fault_type)) is not None
    )
    if not profiles:
        raise ValueError("Brak profilu raportowania dla faultu incydentu.")
    review = _review_commands(definition, state, post_incident, profiles)
    repair_sequence, repair_commands, partial_explanation = _repair_sequence(
        definition, state, review, post_incident
    )
    learning = _unique(
        (
            *(
                (post_incident.learning_summary,)
                if post_incident.learning_summary
                else ()
            ),
            *(point for profile in profiles for point in profile.learning_points),
        )
    )[:5]
    real_world = _unique(
        point for profile in profiles for point in profile.real_world_takeaways
    )[:4]
    return PostIncidentAnalysis(
        incident_summary=_incident_summary(definition, post_incident),
        impact_path=_impact_path(definition, post_incident),
        command_review=review,
        efficiency=_efficiency(state, review),
        key_signals=_key_signals(
            definition, profiles, post_incident, partial_explanation
        ),
        repair_sequence=repair_sequence,
        repair_commands=repair_commands,
        partial_recovery_seen=partial_explanation is not None,
        partial_recovery_explanation=partial_explanation,
        learning_points=learning,
        real_world_takeaways=real_world,
    )
