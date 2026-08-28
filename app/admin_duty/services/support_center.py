from types import MappingProxyType

from pydantic import Field

from app.admin_duty.domain.definition import FrozenDomainModel, IncidentDefinition


class PublicRunbook(FrozenDomainModel):
    id: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=160)
    summary: str = Field(min_length=1, max_length=400)
    steps: tuple[str, ...] = Field(min_length=2, max_length=12)
    topics: tuple[str, ...] = Field(default=(), max_length=12)


class PublicSupportCenter(FrozenDomainModel):
    runbooks: tuple[PublicRunbook, ...] = Field(min_length=1, max_length=12)
    operational_guidance: tuple[str, ...] = Field(min_length=1, max_length=12)


RUNBOOK_CATALOG = MappingProxyType(
    {
        "systemd-service": PublicRunbook(
            id="systemd-service",
            title="Diagnostyka niedziałającej usługi systemd",
            summary="Bezpieczna sekwencja potwierdzenia symptomu, analizy statusu i logów jednostki.",
            steps=(
                "Potwierdź nazwę jednostki i jej bieżący stan przez systemctl status.",
                "Przeczytaj ostatnie wpisy journalctl dla tej samej jednostki.",
                "Sprawdź deklarację jednostki przez systemctl cat, bez zakładania przyczyny.",
                "Po kontrolowanej korekcie uruchom usługę i ponownie potwierdź status.",
            ),
            topics=("systemd", "journal", "service"),
        ),
        "linux-logs": PublicRunbook(
            id="linux-logs",
            title="Podstawowa analiza logów systemowych",
            summary="Jak przejść od alertu do osi czasu zdarzeń bez zgadywania rozwiązania.",
            steps=(
                "Zacznij od logów komponentu bezpośrednio związanego z symptomem.",
                "Zwróć uwagę na pierwszy błąd, a nie tylko późniejsze komunikaty wtórne.",
                "Porównaj czas błędu z wdrożeniem, restartem lub zmianą konfiguracji.",
                "Oddziel obserwację od hipotezy i potwierdź ją drugim źródłem danych.",
            ),
            topics=("journal", "logs", "diagnostics"),
        ),
        "network-basics": PublicRunbook(
            id="network-basics",
            title="Podstawowa diagnostyka sieci",
            summary="Kontrola adresacji, routingu i portów nasłuchujących w Rocky Linux.",
            steps=(
                "Sprawdź adresy interfejsów poleceniem ip addr.",
                "Potwierdź trasę domyślną oraz sieci lokalne przez ip route.",
                "Zweryfikuj porty nasłuchujące przez ss -lntp.",
                "Dopiero potem łącz wyniki z alertem aplikacyjnym.",
            ),
            topics=("network", "iproute2", "ports"),
        ),
        "resource-basics": PublicRunbook(
            id="resource-basics",
            title="Pamięć i miejsce na dysku",
            summary="Szybka ocena presji zasobów bez wykonywania zmian w systemie.",
            steps=(
                "Sprawdź dostępną pamięć przez free -h.",
                "Sprawdź zajętość filesystemów przez df -h.",
                "Szukaj wartości odstających i koreluj je z czasem alertu.",
                "Nie usuwaj danych bez ustalenia właściciela i skutków operacji.",
            ),
            topics=("memory", "disk", "resources"),
        ),
    }
)


def project_public_support_center(
    definition: IncidentDefinition,
) -> PublicSupportCenter:
    topics = set(definition.presentation.tags)
    selected = [RUNBOOK_CATALOG["systemd-service"], RUNBOOK_CATALOG["linux-logs"]]
    if "network" in topics:
        selected.append(RUNBOOK_CATALOG["network-basics"])
    else:
        selected.append(RUNBOOK_CATALOG["resource-basics"])
    return PublicSupportCenter(
        runbooks=tuple(selected),
        operational_guidance=(
            "Najpierw potwierdź symptom, później zbierz status i logi.",
            "Jedna obserwacja to za mało — potwierdź hipotezę drugim poleceniem.",
            "Przed restartem sprawdź konfigurację i zależności usługi.",
        ),
    )
