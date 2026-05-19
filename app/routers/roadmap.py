from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/roadmap", tags=["roadmap"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def roadmap_page(request: Request):
    stages = [
        {
            "title": "Etap 1 — Fundamenty platformy",
            "subtitle": "Pierwsza działająca wersja aplikacji edukacyjnej",
            "status": "Ukończone",
            "status_type": "done",
            "description": (
                "Ten etap obejmował przygotowanie podstawowej struktury aplikacji, "
                "widoków publicznych, lekcji, quizów, fiszek, dashboardu, roadmapy "
                "oraz automatycznych testów."
            ),
            "items": [
                "strona główna",
                "lista lekcji",
                "widok szczegółowy lekcji",
                "quizy",
                "fiszki",
                "dashboard",
                "roadmapa",
                "testy pytest",
                "GitHub Actions",
            ],
        },
        {
            "title": "Etap 2 — Publiczne uruchomienie",
            "subtitle": "Aplikacja dostępna przez domenę i HTTPS",
            "status": "Ukończone",
            "status_type": "done",
            "description": (
                "Ten etap obejmował przygotowanie serwera VPS, uruchomienie aplikacji "
                "jako usługi systemowej, konfigurację Nginx, podpięcie domeny, "
                "włączenie HTTPS oraz podstawowe uporządkowanie konfiguracji serwera."
            ),
            "items": [
                "deployment na VPS",
                "użytkownik aplikacyjny",
                "Python virtual environment",
                "systemd service",
                "Nginx reverse proxy",
                "domena",
                "HTTPS",
                "automatyczne odnawianie certyfikatu",
                "podstawowy hardening Nginx",
            ],
        },
        {
            "title": "Etap 3 — Rozbudowa lekcji podstawowych",
            "subtitle": "Solidne fundamenty pracy z Linuxem",
            "status": "W trakcie",
            "status_type": "active",
            "description": (
                "Aktualny etap skupia się na domknięciu pierwszego bloku lekcji "
                "podstawowych. Celem jest przygotowanie spójnej ścieżki dla osób, "
                "które zaczynają naukę terminala, plików, procesów, pakietów, usług, "
                "sieci i logów."
            ),
            "items": [
                "nawigacja po systemie plików",
                "pliki i katalogi",
                "uprawnienia",
                "użytkownicy i grupy",
                "procesy",
                "praca z plikami tekstowymi",
                "pakiety i aktualizacje",
                "usługi systemowe",
                "sieć i diagnostyka",
                "logi systemowe",
            ],
        },
        {
            "title": "Etap 4 — Administracja systemem",
            "subtitle": "Codzienna praca z serwerem Linux",
            "status": "Planowane",
            "status_type": "planned",
            "description": (
                "Ten etap będzie rozwijał tematy związane z administracją systemem: "
                "usługami, logami, SSH, firewallem, SELinux, diagnostyką i podstawowym "
                "bezpieczeństwem serwera."
            ),
            "items": [
                "SSH i zdalne logowanie",
                "podstawowe zabezpieczenie SSH",
                "firewalld",
                "SELinux",
                "diagnostyka usług",
                "analiza logów",
                "podstawy bezpieczeństwa",
            ],
        },
        {
            "title": "Etap 5 — Deployment i DevOps",
            "subtitle": "Od aplikacji lokalnej do utrzymywanego wdrożenia",
            "status": "Planowane",
            "status_type": "planned",
            "description": (
                "Ten etap będzie pokazywał, jak uruchamiać i utrzymywać aplikacje "
                "webowe na serwerze: przez systemd, Nginx, domenę, HTTPS, Git oraz "
                "powtarzalne procedury aktualizacji."
            ),
            "items": [
                "systemd service dla aplikacji",
                "zmienne środowiskowe",
                "Nginx reverse proxy",
                "DNS",
                "HTTPS",
                "aktualizacja aplikacji przez Git",
                "procedury utrzymaniowe",
            ],
        },
        {
            "title": "Etap 6 — Automatyzacja i monitoring",
            "subtitle": "Kontenery, CI/CD, metryki i dalszy rozwój",
            "status": "Planowane",
            "status_type": "planned",
            "description": (
                "Ostatni etap będzie dotyczył bardziej zaawansowanych tematów: "
                "konteneryzacji, automatyzacji testów i wdrożeń, monitoringu, "
                "metryk, alertów oraz funkcji interaktywnych."
            ),
            "items": [
                "Docker albo Podman",
                "PostgreSQL",
                "GitHub Actions",
                "CI/CD",
                "automatyczny deployment",
                "Prometheus",
                "Grafana",
                "interaktywne zadania",
            ],
        },
    ]

    return templates.TemplateResponse(
        request=request,
        name="roadmap.html",
        context={
            "stages": stages,
        },
    )