from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/roadmap", tags=["roadmap"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def roadmap_page(request: Request):
    stages = [
        {
            "title": "Etap 1 — MVP lokalne",
            "status": "W trakcie",
            "items": [
                "FastAPI",
                "SQLite",
                "Jinja2",
                "lekcje",
                "quizy",
                "fiszki",
                "dashboard",
                "testy pytest",
                "GitHub Actions",
            ],
            "active": True,
        },
        {
            "title": "Etap 2 — Deployment na VPS",
            "status": "Planowane",
            "items": [
                "Rocky Linux 9 VPS",
                "SSH",
                "użytkownik systemowy",
                "systemd service",
                "Nginx reverse proxy",
                "domena",
                "HTTPS",
                "firewalld",
            ],
            "active": False,
        },
        {
            "title": "Etap 3 — Konteneryzacja",
            "status": "Planowane",
            "items": [
                "Docker albo Podman",
                "compose",
                "wolumeny",
                "sieć kontenerów",
                "PostgreSQL",
            ],
            "active": False,
        },
        {
            "title": "Etap 4 — CI/CD",
            "status": "Planowane",
            "items": [
                "rozbudowa GitHub Actions",
                "automatyczne testy",
                "automatyczny deployment",
                "kontrola jakości kodu",
            ],
            "active": False,
        },
        {
            "title": "Etap 5 — Monitoring",
            "status": "Planowane",
            "items": [
                "logi aplikacji",
                "Prometheus",
                "Grafana",
                "metryki",
                "alerty",
            ],
            "active": False,
        },
        {
            "title": "Etap 6 — Funkcje zaawansowane",
            "status": "Planowane",
            "items": [
                "symulator terminala",
                "sandbox Linux",
                "WebSockety",
                "dynamiczne zadania",
                "AI tutor",
            ],
            "active": False,
        },
    ]

    return templates.TemplateResponse(
        request=request,
        name="roadmap.html",
        context={
            "stages": stages,
        },
    )