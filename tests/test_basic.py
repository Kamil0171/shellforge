import re
from datetime import timedelta
from html import unescape
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

import app.admin_duty.router as admin_duty_router_module
from app.admin_duty.router import sessions as admin_duty_sessions
from app.admin_duty.scenarios.incident_001 import (
    BROKEN_EXEC_START,
    CORRECT_EXEC_START,
    SERVICE_FILE,
)
from app.content.application_dns import APPLICATION_DNS
from app.content.certbot_https import CERTBOT_HTTPS
from app.content.deployment_backup_rollback import DEPLOYMENT_BACKUP_ROLLBACK
from app.content.deployment_checklist import DEPLOYMENT_CHECKLIST
from app.content.deployment_preparation import DEPLOYMENT_PREPARATION
from app.content.disk_space_cleanup import DISK_SPACE_CLEANUP
from app.content.dns_practice import DNS_PRACTICE
from app.content.environment_secrets import ENVIRONMENT_SECRETS
from app.content.firewall_basics import FIREWALL_BASICS
from app.content.firewalld_zones_services_ports import FIREWALLD_ZONES_SERVICES_PORTS
from app.content.git_application_update import GIT_APPLICATION_UPDATE
from app.content.ip_addressing import IP_ADDRESSING
from app.content.log_analysis import LOG_ANALYSIS
from app.content.network_dns_routing_connections import NETWORK_DNS_ROUTING_CONNECTIONS
from app.content.network_ports_services import NETWORK_PORTS_SERVICES
from app.content.nginx_reverse_proxy import NGINX_REVERSE_PROXY
from app.content.post_deployment_diagnostics import POST_DEPLOYMENT_DIAGNOSTICS
from app.content.python_server_environment import PYTHON_SERVER_ENVIRONMENT
from app.content.scheduled_tasks import SCHEDULED_TASKS
from app.content.selinux_basics import SELINUX_BASICS
from app.content.selinux_troubleshooting import SELINUX_TROUBLESHOOTING
from app.content.ssh_administration import SSH_ADMINISTRATION
from app.content.ssh_keys_practice import SSH_KEYS_PRACTICE
from app.content.ssh_secure_configuration import SSH_SECURE_CONFIGURATION
from app.content.systemd_diagnostics import SYSTEMD_DIAGNOSTICS
from app.content.systemd_web_service import SYSTEMD_WEB_SERVICE
from app.content.tls_https_basics import TLS_HTTPS_BASICS
from app.content.uvicorn_application import UVICORN_APPLICATION
from app.database import create_db_and_tables, engine
from app.main import app
from app.models import Lesson
from app.routers.lessons import get_adjacent_lessons
from app.seed import LESSONS, seed_database

create_db_and_tables()
seed_database()

client = TestClient(app)


def start_admin_duty_session():
    response = client.post(
        "/admin-duty/api/start",
        json={"scenario_id": "INC-001"},
    )

    assert response.status_code == 200

    return response.json()


def run_admin_duty_command(session_id, command):
    response = client.post(
        "/admin-duty/api/command",
        json={
            "session_id": session_id,
            "command": command,
        },
    )

    assert response.status_code == 200

    return response.json()


@pytest.fixture
def admin_duty_session():
    admin_duty_sessions.clear()
    session = start_admin_duty_session()

    yield session

    admin_duty_sessions.clear()


def get_ordered_lessons():
    with Session(engine) as session:
        return session.exec(select(Lesson).order_by(Lesson.id)).all()


def test_home_page_returns_200():
    response = client.get("/")

    assert response.status_code == 200
    assert "ShellForge" in response.text
    assert "Rozwiąż incydent" in response.text
    assert "Sprawdź się w praktyce" in response.text
    assert "502 po wdrożeniu" in response.text
    assert "Linux · systemd · diagnostyka" in response.text
    assert "Uvicorn" not in response.text
    assert 'href="/admin-duty/"' in response.text


def test_shared_navigation_uses_simulator_module_name():
    response = client.get("/nieistniejaca-strona")

    assert response.status_code == 404
    assert 'href="/admin-duty/"' in response.text
    assert "Symulator" in response.text
    assert "Dyżur administratora" not in response.text


def test_lessons_page_returns_200():
    response = client.get("/lessons")

    assert response.status_code == 200
    assert "Lekcje ShellForge" in response.text
    assert "Gotowy na praktykę?" in response.text
    assert "Przejdź do Symulatora" in response.text


def test_lesson_detail_page_returns_200():
    response = client.get("/lessons/1")

    assert response.status_code == 200
    assert "Gdzie jestem? Komendy pwd, ls i cd" in response.text


def test_first_lesson_navigation():
    lessons = get_ordered_lessons()
    first_lesson, next_lesson = lessons[:2]

    response = client.get(f"/lessons/{first_lesson.id}")

    assert response.status_code == 200
    assert "Poprzednia lekcja" not in response.text
    assert "Następna lekcja" in response.text
    assert f'href="/lessons/{next_lesson.id}"' in response.text


def test_middle_lesson_navigation():
    lessons = get_ordered_lessons()
    middle_index = len(lessons) // 2
    previous_lesson = lessons[middle_index - 1]
    lesson = lessons[middle_index]
    next_lesson = lessons[middle_index + 1]

    response = client.get(f"/lessons/{lesson.id}")

    assert response.status_code == 200
    assert "Poprzednia lekcja" in response.text
    assert "Następna lekcja" in response.text
    assert f'href="/lessons/{previous_lesson.id}"' in response.text
    assert f'href="/lessons/{next_lesson.id}"' in response.text


def test_last_lesson_navigation():
    lessons = get_ordered_lessons()
    previous_lesson, last_lesson = lessons[-2:]

    response = client.get(f"/lessons/{last_lesson.id}")

    assert response.status_code == 200
    assert "Poprzednia lekcja" in response.text
    assert "Następna lekcja" not in response.text
    assert f'href="/lessons/{previous_lesson.id}"' in response.text


def test_lesson_navigation_uses_ordered_collection_with_non_contiguous_ids():
    lessons = [
        SimpleNamespace(id=3),
        SimpleNamespace(id=11),
        SimpleNamespace(id=27),
    ]

    previous_lesson, next_lesson = get_adjacent_lessons(lessons, 11)

    assert previous_lesson is lessons[0]
    assert next_lesson is lessons[2]


def test_quiz_page_returns_200():
    response = client.get("/quiz/1")

    assert response.status_code == 200
    assert "Quiz: pwd, ls i cd" in response.text


def test_missing_lesson_returns_404():
    response = client.get("/lessons/999")

    assert response.status_code == 404


def test_missing_quiz_returns_404():
    response = client.get("/quiz/999")

    assert response.status_code == 404


def test_quiz_submit_returns_result():
    response = client.post(
        "/quiz/1",
        data={
            "question_1": "b",
            "question_2": "a",
            "question_3": "c",
            "question_4": "c",
        },
    )

    assert response.status_code == 200
    assert "Wynik quizu" in response.text
    assert "100%" in response.text


def test_dashboard_page_returns_200():
    response = client.get("/dashboard/")

    assert response.status_code == 200
    assert "Twoje miejsce startowe w ShellForge" in response.text


def test_flashcards_page_returns_200():
    response = client.get("/flashcards/1")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_missing_flashcards_lesson_returns_404():
    response = client.get("/flashcards/999")

    assert response.status_code == 404


def test_second_lesson_detail_page_returns_200():
    response = client.get("/lessons/2")

    assert response.status_code == 200
    assert "Pliki i katalogi" in response.text


def test_second_quiz_page_returns_200():
    response = client.get("/quiz/2")

    assert response.status_code == 200
    assert "Quiz: pliki i katalogi" in response.text


def test_second_flashcards_page_returns_200():
    response = client.get("/flashcards/2")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_health_check_returns_200():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ShellForge"
    assert response.json()["version"] == "0.1.0"
    assert response.json()["environment"] == "development"


def test_roadmap_page_returns_200():
    response = client.get("/roadmap/")

    assert response.status_code == 200
    assert "Ścieżka nauki" in response.text
    assert "Praktyka poza ścieżką" in response.text
    assert "Przejdź do Symulatora" in response.text


def test_custom_404_page_returns_404():
    response = client.get("/nieistniejaca-strona")

    assert response.status_code == 404
    assert "Nie znaleziono strony" in response.text


def test_about_page_returns_200():
    response = client.get("/about/")

    assert response.status_code == 200
    assert "Czym jest ShellForge?" in response.text
    assert "Trzy filary ShellForge" in response.text
    assert ">Nauka<" in response.text
    assert ">Utrwalanie<" in response.text
    assert ">Praktyka<" in response.text
    assert "Polecenia wykonywane w Symulatorze działają wyłącznie" in response.text
    assert "nie są wykonywane na rzeczywistym serwerze" in response.text
    assert "rzeczywistym serwerze ShellForge" not in response.text


def test_third_lesson_detail_page_returns_200():
    response = client.get("/lessons/3")

    assert response.status_code == 200
    assert "Uprawnienia plików" in response.text


def test_third_quiz_page_returns_200():
    response = client.get("/quiz/3")

    assert response.status_code == 200
    assert "Quiz: uprawnienia plików" in response.text


def test_third_flashcards_page_returns_200():
    response = client.get("/flashcards/3")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_fourth_lesson_detail_page_returns_200():
    response = client.get("/lessons/4")

    assert response.status_code == 200
    assert "Użytkownicy i grupy" in response.text


def test_fourth_quiz_page_returns_200():
    response = client.get("/quiz/4")

    assert response.status_code == 200
    assert "Quiz: użytkownicy i grupy" in response.text


def test_fourth_flashcards_page_returns_200():
    response = client.get("/flashcards/4")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_fifth_lesson_detail_page_returns_200():
    response = client.get("/lessons/5")

    assert response.status_code == 200
    assert "Procesy w Linuxie" in response.text


def test_fifth_quiz_page_returns_200():
    response = client.get("/quiz/5")

    assert response.status_code == 200
    assert "Quiz: procesy w Linuxie" in response.text


def test_fifth_flashcards_page_returns_200():
    response = client.get("/flashcards/5")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_sixth_lesson_detail_page_returns_200():
    response = client.get("/lessons/6")

    assert response.status_code == 200
    assert "Praca z plikami tekstowymi" in response.text


def test_sixth_quiz_page_returns_200():
    response = client.get("/quiz/6")

    assert response.status_code == 200
    assert "Quiz: praca z plikami tekstowymi" in response.text


def test_sixth_flashcards_page_returns_200():
    response = client.get("/flashcards/6")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_seventh_lesson_detail_page_returns_200():
    response = client.get("/lessons/7")

    assert response.status_code == 200
    assert "Pakiety i aktualizacje" in response.text


def test_seventh_quiz_page_returns_200():
    response = client.get("/quiz/7")

    assert response.status_code == 200
    assert "Quiz: pakiety i aktualizacje" in response.text


def test_seventh_flashcards_page_returns_200():
    response = client.get("/flashcards/7")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_eighth_lesson_detail_page_returns_200():
    response = client.get("/lessons/8")

    assert response.status_code == 200
    assert "Usługi systemowe" in response.text


def test_eighth_quiz_page_returns_200():
    response = client.get("/quiz/8")

    assert response.status_code == 200
    assert "Quiz: usługi systemowe" in response.text


def test_eighth_flashcards_page_returns_200():
    response = client.get("/flashcards/8")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_ninth_lesson_detail_page_returns_200():
    response = client.get("/lessons/9")

    assert response.status_code == 200
    assert "Sieć i diagnostyka" in response.text


def test_ninth_quiz_page_returns_200():
    response = client.get("/quiz/9")

    assert response.status_code == 200
    assert "Quiz: sieć i diagnostyka" in response.text


def test_ninth_flashcards_page_returns_200():
    response = client.get("/flashcards/9")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_tenth_lesson_detail_page_returns_200():
    response = client.get("/lessons/10")

    assert response.status_code == 200
    assert "Logi systemowe" in response.text


def test_tenth_quiz_page_returns_200():
    response = client.get("/quiz/10")

    assert response.status_code == 200
    assert "Quiz: logi systemowe" in response.text


def test_tenth_flashcards_page_returns_200():
    response = client.get("/flashcards/10")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_eleventh_lesson_detail_page_returns_200():
    response = client.get("/lessons/11")

    assert response.status_code == 200
    assert "Struktura katalogów administracyjnych" in response.text


def test_eleventh_quiz_page_returns_200():
    response = client.get("/quiz/11")

    assert response.status_code == 200
    assert "Quiz: katalogi administracyjne" in response.text


def test_eleventh_flashcards_page_returns_200():
    response = client.get("/flashcards/11")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twelfth_lesson_detail_page_returns_200():
    response = client.get("/lessons/12")

    assert response.status_code == 200
    assert "Podstawowa diagnostyka systemu" in response.text


def test_twelfth_quiz_page_returns_200():
    response = client.get("/quiz/12")

    assert response.status_code == 200
    assert "Quiz: podstawowa diagnostyka systemu" in response.text


def test_twelfth_flashcards_page_returns_200():
    response = client.get("/flashcards/12")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_thirteenth_lesson_detail_page_returns_200():
    response = client.get("/lessons/13")

    assert response.status_code == 200
    assert "Sudo i praca administratora" in response.text
    assert "Podstawowy+" in response.text
    assert "<code>sudo</code>" in response.text
    assert "&lt;code&gt;sudo&lt;/code&gt;" not in response.text


def test_thirteenth_quiz_page_returns_200():
    response = client.get("/quiz/13")

    assert response.status_code == 200
    assert "Quiz: sudo i praca administratora" in response.text


def test_thirteenth_flashcards_page_returns_200():
    response = client.get("/flashcards/13")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_fourteenth_lesson_detail_page_returns_200():
    response = client.get("/lessons/14")

    assert response.status_code == 200
    assert "Zarządzanie użytkownikami i grupami" in response.text
    assert "Podstawowy+" in response.text


def test_fourteenth_quiz_page_returns_200():
    response = client.get("/quiz/14")

    assert response.status_code == 200
    assert "Quiz: zarządzanie użytkownikami i grupami" in response.text


def test_fourteenth_flashcards_page_returns_200():
    response = client.get("/flashcards/14")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_fifteenth_lesson_detail_page_returns_200():
    response = client.get("/lessons/15")

    assert response.status_code == 200
    assert "Diagnostyka usług systemd" in response.text
    assert "Podstawowy+" in response.text


def test_fifteenth_quiz_page_returns_200():
    response = client.get("/quiz/15")

    assert response.status_code == 200
    assert "Quiz: diagnostyka usług systemd" in response.text


def test_fifteenth_flashcards_page_returns_200():
    response = client.get("/flashcards/15")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_sixteenth_lesson_detail_page_returns_200():
    response = client.get("/lessons/16")

    assert response.status_code == 200
    assert "Analiza logów w praktyce" in response.text
    assert "Podstawowy+" in response.text


def test_sixteenth_quiz_page_returns_200():
    response = client.get("/quiz/16")

    assert response.status_code == 200
    assert "Quiz: analiza logów w praktyce" in response.text


def test_sixteenth_flashcards_page_returns_200():
    response = client.get("/flashcards/16")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_seventeenth_lesson_detail_page_returns_200():
    response = client.get("/lessons/17")

    assert response.status_code == 200
    assert "Miejsce na dysku i porządkowanie systemu" in response.text
    assert "Podstawowy+" in response.text


def test_seventeenth_quiz_page_returns_200():
    response = client.get("/quiz/17")

    assert response.status_code == 200
    assert "Quiz: miejsce na dysku i porządkowanie systemu" in response.text


def test_seventeenth_flashcards_page_returns_200():
    response = client.get("/flashcards/17")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_eighteenth_lesson_detail_page_returns_200():
    response = client.get("/lessons/18")

    assert response.status_code == 200
    assert "Zadania cykliczne" in response.text
    assert "Podstawowy+" in response.text


def test_eighteenth_quiz_page_returns_200():
    response = client.get("/quiz/18")

    assert response.status_code == 200
    assert "Quiz: cron i podstawy systemd timers" in response.text


def test_eighteenth_flashcards_page_returns_200():
    response = client.get("/flashcards/18")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_nineteenth_lesson_detail_page_returns_200():
    response = client.get("/lessons/19")

    assert response.status_code == 200
    assert "Podstawy adresacji IP" in response.text
    assert "Podstawowy+" in response.text


def test_nineteenth_quiz_page_returns_200():
    response = client.get("/quiz/19")

    assert response.status_code == 200
    assert "Quiz: podstawy adresacji IP" in response.text


def test_nineteenth_flashcards_page_returns_200():
    response = client.get("/flashcards/19")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twentieth_lesson_detail_page_returns_200():
    response = client.get("/lessons/20")

    assert response.status_code == 200
    assert "DNS w praktyce" in response.text
    assert "Podstawowy+" in response.text


def test_twentieth_quiz_page_returns_200():
    response = client.get("/quiz/20")

    assert response.status_code == 200
    assert "Quiz: DNS w praktyce" in response.text


def test_twentieth_flashcards_page_returns_200():
    response = client.get("/flashcards/20")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twenty_first_lesson_detail_page_returns_200():
    response = client.get("/lessons/21")

    assert response.status_code == 200
    assert "Porty" in response.text
    assert "sieciowe" in response.text
    assert "Podstawowy+" in response.text


def test_twenty_first_quiz_page_returns_200():
    response = client.get("/quiz/21")

    assert response.status_code == 200
    assert "Quiz:" in response.text
    assert "porty" in response.text


def test_twenty_first_flashcards_page_returns_200():
    response = client.get("/flashcards/21")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twenty_second_lesson_detail_page_returns_200():
    response = client.get("/lessons/22")

    assert response.status_code == 200
    assert "SSH w administracji systemem" in response.text
    assert "Podstawowy+" in response.text


def test_twenty_second_quiz_page_returns_200():
    response = client.get("/quiz/22")

    assert response.status_code == 200
    assert "Quiz: SSH w administracji systemem" in response.text


def test_twenty_second_flashcards_page_returns_200():
    response = client.get("/flashcards/22")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twenty_third_lesson_detail_page_returns_200():
    response = client.get("/lessons/23")

    assert response.status_code == 200
    assert "Firewall" in response.text
    assert "Podstawowy+" in response.text


def test_twenty_third_quiz_page_returns_200():
    response = client.get("/quiz/23")

    assert response.status_code == 200
    assert "Quiz:" in response.text
    assert "firewall" in response.text


def test_twenty_third_flashcards_page_returns_200():
    response = client.get("/flashcards/23")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twenty_fourth_lesson_detail_page_returns_200():
    response = client.get("/lessons/24")

    assert response.status_code == 200
    assert "SELinux" in response.text
    assert "Podstawowy+" in response.text


def test_twenty_fourth_quiz_page_returns_200():
    response = client.get("/quiz/24")

    assert response.status_code == 200
    assert "Quiz:" in response.text
    assert "SELinux" in response.text


def test_twenty_fourth_flashcards_page_returns_200():
    response = client.get("/flashcards/24")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twenty_fifth_lesson_detail_page_returns_200():
    response = client.get("/lessons/25")

    assert response.status_code == 200
    assert "Bezpieczna konfiguracja SSH" in response.text
    assert "Podstawowy+" in response.text


def test_twenty_fifth_quiz_page_returns_200():
    response = client.get("/quiz/25")

    assert response.status_code == 200
    assert "Quiz: bezpieczna konfiguracja SSH" in response.text


def test_twenty_fifth_flashcards_page_returns_200():
    response = client.get("/flashcards/25")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twenty_sixth_lesson_detail_page_returns_200():
    response = client.get("/lessons/26")

    assert response.status_code == 200
    assert "Klucze SSH w praktyce" in response.text
    assert "Podstawowy+" in response.text


def test_twenty_sixth_quiz_page_returns_200():
    response = client.get("/quiz/26")

    assert response.status_code == 200
    assert "Quiz: klucze SSH w praktyce" in response.text


def test_twenty_sixth_flashcards_page_returns_200():
    response = client.get("/flashcards/26")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twenty_seventh_lesson_detail_page_returns_200():
    response = client.get("/lessons/27")

    assert response.status_code == 200
    assert "Firewalld" in response.text
    assert "strefy" in response.text
    assert "Podstawowy+" in response.text


def test_twenty_seventh_quiz_page_returns_200():
    response = client.get("/quiz/27")

    assert response.status_code == 200
    assert "Quiz:" in response.text
    assert "firewalld" in response.text


def test_twenty_seventh_flashcards_page_returns_200():
    response = client.get("/flashcards/27")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twenty_eighth_lesson_detail_page_returns_200():
    response = client.get("/lessons/28")

    assert response.status_code == 200
    assert "SELinux" in response.text
    assert "diagnostyka problemów" in response.text
    assert "Podstawowy+" in response.text


def test_twenty_eighth_quiz_page_returns_200():
    response = client.get("/quiz/28")

    assert response.status_code == 200
    assert "Quiz:" in response.text
    assert "SELinux" in response.text


def test_twenty_eighth_flashcards_page_returns_200():
    response = client.get("/flashcards/28")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_twenty_ninth_lesson_detail_page_returns_200():
    response = client.get("/lessons/29")

    assert response.status_code == 200
    assert "Diagnostyka DNS, routingu i połączeń" in response.text
    assert "Podstawowy+" in response.text


def test_twenty_ninth_quiz_page_returns_200():
    response = client.get("/quiz/29")

    assert response.status_code == 200
    assert "Quiz: diagnostyka DNS, routingu i połączeń" in response.text


def test_twenty_ninth_flashcards_page_returns_200():
    response = client.get("/flashcards/29")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_thirtieth_lesson_detail_page_returns_200():
    response = client.get("/lessons/30")

    assert response.status_code == 200
    assert "Podstawy TLS i HTTPS" in response.text
    assert "Podstawowy+" in response.text


def test_thirtieth_quiz_page_returns_200():
    response = client.get("/quiz/30")

    assert response.status_code == 200
    assert "Quiz: podstawy TLS i HTTPS" in response.text


def test_thirtieth_flashcards_page_returns_200():
    response = client.get("/flashcards/30")

    assert response.status_code == 200
    assert "Fiszki do lekcji" in response.text


def test_deployment_lesson_pages_return_200():
    lesson_titles = {
        31: "Przygotowanie aplikacji do wdrożenia",
        32: "Środowisko Python na serwerze",
        33: "Uruchamianie aplikacji przez Uvicorn",
        34: "Aplikacja jako usługa systemd",
        35: "Nginx jako reverse proxy",
        36: "Domena i rekordy DNS dla aplikacji",
        37: "HTTPS z Let&#39;s Encrypt i Certbot",
        38: "Zmienne środowiskowe i sekrety aplikacji",
        39: "Aktualizacja aplikacji przez Git",
        40: "Backup przed wdrożeniem i podstawowy rollback",
        41: "Logi i diagnostyka problemów po wdrożeniu",
        42: "Procedura deploymentu i lista kontrolna",
    }

    for lesson_id, title in lesson_titles.items():
        response = client.get(f"/lessons/{lesson_id}")

        assert response.status_code == 200
        assert title in response.text
        assert "Średnio zaawansowany" in response.text


def test_deployment_quiz_pages_return_200():
    quiz_titles = {
        31: "Quiz: przygotowanie aplikacji do wdrożenia",
        32: "Quiz: środowisko Python na serwerze",
        33: "Quiz: uruchamianie aplikacji przez Uvicorn",
        34: "Quiz: aplikacja jako usługa systemd",
        35: "Quiz: Nginx jako reverse proxy",
        36: "Quiz: domena i rekordy DNS dla aplikacji",
        37: "Quiz: HTTPS z Let&#39;s Encrypt i Certbot",
        38: "Quiz: zmienne środowiskowe i sekrety aplikacji",
        39: "Quiz: aktualizacja aplikacji przez Git",
        40: "Quiz: backup przed wdrożeniem i podstawowy rollback",
        41: "Quiz: logi i diagnostyka problemów po wdrożeniu",
        42: "Quiz: procedura deploymentu i lista kontrolna",
    }

    for quiz_id, title in quiz_titles.items():
        response = client.get(f"/quiz/{quiz_id}")

        assert response.status_code == 200
        assert title in response.text


def test_deployment_flashcard_pages_return_200():
    for lesson_id in range(31, 43):
        response = client.get(f"/flashcards/{lesson_id}")

        assert response.status_code == 200
        assert "Fiszki do lekcji" in response.text


def test_new_administration_lessons_have_required_structure():
    lessons = [
        SYSTEMD_DIAGNOSTICS,
        LOG_ANALYSIS,
        DISK_SPACE_CLEANUP,
        SCHEDULED_TASKS,
    ]

    for lesson_bundle in lessons:
        assert lesson_bundle["module"]["title"] == "Administracja systemem"
        assert lesson_bundle["lesson"]["level"] == "Podstawowy+"
        assert lesson_bundle["lesson"]["practice_task"]
        assert lesson_bundle["lesson"]["common_mistakes"]
        assert len(lesson_bundle["quiz"]["questions"]) == 6
        assert len(lesson_bundle["flashcards"]) == 25

        for question in lesson_bundle["quiz"]["questions"]:
            assert len(question["answers"]) == 4
            assert sum(answer[2] for answer in question["answers"]) == 1


def test_network_security_lessons_have_required_structure():
    lessons = [
        IP_ADDRESSING,
        DNS_PRACTICE,
        NETWORK_PORTS_SERVICES,
        SSH_ADMINISTRATION,
        FIREWALL_BASICS,
        SELINUX_BASICS,
        SSH_SECURE_CONFIGURATION,
        SSH_KEYS_PRACTICE,
        FIREWALLD_ZONES_SERVICES_PORTS,
        SELINUX_TROUBLESHOOTING,
        NETWORK_DNS_ROUTING_CONNECTIONS,
        TLS_HTTPS_BASICS,
    ]

    for lesson_bundle in lessons:
        assert lesson_bundle["module"]["title"] == "Sieć i bezpieczeństwo"
        assert lesson_bundle["lesson"]["level"] == "Podstawowy+"
        assert lesson_bundle["lesson"]["practice_task"]
        assert lesson_bundle["lesson"]["common_mistakes"]
        assert len(lesson_bundle["quiz"]["questions"]) == 6
        assert len(lesson_bundle["flashcards"]) == 25

        for question in lesson_bundle["quiz"]["questions"]:
            assert len(question["answers"]) == 4
            assert sum(answer[2] for answer in question["answers"]) == 1


def test_deployment_lessons_have_required_structure():
    lessons = [
        DEPLOYMENT_PREPARATION,
        PYTHON_SERVER_ENVIRONMENT,
        UVICORN_APPLICATION,
        SYSTEMD_WEB_SERVICE,
        NGINX_REVERSE_PROXY,
        APPLICATION_DNS,
        CERTBOT_HTTPS,
        ENVIRONMENT_SECRETS,
        GIT_APPLICATION_UPDATE,
        DEPLOYMENT_BACKUP_ROLLBACK,
        POST_DEPLOYMENT_DIAGNOSTICS,
        DEPLOYMENT_CHECKLIST,
    ]

    for lesson_bundle in lessons:
        lesson = lesson_bundle["lesson"]

        assert lesson_bundle["module"]["title"] == "Deployment aplikacji"
        assert lesson["level"] == "Średnio zaawansowany"
        assert lesson["description"]
        assert lesson["theory"]
        assert lesson["commands"]
        assert lesson["practice_task"]
        assert lesson["common_mistakes"]
        assert lesson["summary"]
        assert len(lesson_bundle["quiz"]["questions"]) == 6
        assert len(lesson_bundle["flashcards"]) == 25

        for question in lesson_bundle["quiz"]["questions"]:
            assert len(question["answers"]) == 4
            assert sum(answer[2] for answer in question["answers"]) == 1
            assert [answer[0] for answer in question["answers"]] == ["a", "b", "c", "d"]


def test_deployment_lessons_contain_required_topics():
    required_topics = {
        DEPLOYMENT_PREPARATION["lesson"]["title"]: [
            "app.main:app",
            "requirements.txt",
            "/opt/example-app",
            "python3 --version",
            "git --version",
            "df -h",
            "ss -lntp",
            "dedykowany użytkownik",
        ],
        PYTHON_SERVER_ENVIRONMENT["lesson"]["title"]: [
            "systemowy python",
            "venv",
            "globalnym",
            "which python",
            "python -m pip",
            "pip check",
            "requirements.txt",
            "odtwarzal",
        ],
        UVICORN_APPLICATION["lesson"]["title"]: [
            "asgi",
            "uvicorn",
            "app.main:app",
            "--host",
            "--port",
            "127.0.0.1:8000",
            "curl",
            "ss -lntp",
            "--reload",
            "zajęty",
        ],
        SYSTEMD_WEB_SERVICE["lesson"]["title"]: [
            "[unit]",
            "[service]",
            "[install]",
            "user",
            "group",
            "workingdirectory",
            "environmentfile",
            "execstart",
            "restart",
            "daemon-reload",
            "enable",
            "start",
            "status",
            "journalctl",
        ],
        NGINX_REVERSE_PROXY["lesson"]["title"]: [
            "reverse proxy",
            "listen 80",
            "server_name",
            "location /",
            "proxy_pass",
            "proxy_set_header",
            "host",
            "x-real-ip",
            "x-forwarded-for",
            "x-forwarded-proto",
            "nginx -t",
            "reload nginx",
            "502 bad gateway",
        ],
        APPLICATION_DNS["lesson"]["title"]: [
            "domena główna",
            "subdomen",
            "rekord a",
            "aaaa",
            "cname",
            "server_name",
            "ttl",
            "cache dns",
            "/etc/hosts",
            "dig",
            "host",
            "getent hosts",
            "resolver",
        ],
        CERTBOT_HTTPS["lesson"]["title"]: [
            "http",
            "https",
            "tls",
            "let's encrypt",
            "certbot --nginx",
            "renew --dry-run",
            "list-timers",
            "nginx -t",
            "porty 80 i 443",
            "firewall",
            "/etc/letsencrypt",
        ],
        ENVIRONMENT_SECRETS["lesson"]["title"]: [
            "zmienne środowiskowe",
            "sekret",
            ".env.example",
            ".gitignore",
            "environmentfile",
            "execstart",
            "grep -q",
            "600",
            "restart",
            "rotacja",
        ],
        GIT_APPLICATION_UPDATE["lesson"]["title"]: [
            "branch",
            "working tree",
            "git fetch",
            "pull --ff-only",
            "main",
            "requirements.txt",
            "git log -1",
            "systemctl status",
            "127.0.0.1:8000",
            "reset --hard",
        ],
        DEPLOYMENT_BACKUP_ROLLBACK["lesson"]["title"]: [
            "backup",
            "sqlite",
            ".backup",
            "git rev-parse head",
            "--preserve=mode,ownership",
            "git switch --detach",
            "rollback kodu",
            "rollback danych",
            "migracji",
        ],
        POST_DEPLOYMENT_DIAGNOSTICS["lesson"]["title"]: [
            "journalctl",
            "--since",
            "127.0.0.1:8000",
            "error.log",
            "ss -tlnp",
            "dig",
            "404",
            "502",
            "503",
            "500",
            "df -h",
            "free -h",
            "uptime",
        ],
        DEPLOYMENT_CHECKLIST["lesson"]["title"]: [
            "ruff check .",
            "pytest",
            "git status --short",
            "git rev-parse head",
            "pull --ff-only",
            "backup",
            "journalctl",
            "127.0.0.1:8000",
            "https://app.example.com",
            "smoke test",
            "rollback",
            "ci/cd",
        ],
    }
    lesson_bundles = [
        DEPLOYMENT_PREPARATION,
        PYTHON_SERVER_ENVIRONMENT,
        UVICORN_APPLICATION,
        SYSTEMD_WEB_SERVICE,
        NGINX_REVERSE_PROXY,
        APPLICATION_DNS,
        CERTBOT_HTTPS,
        ENVIRONMENT_SECRETS,
        GIT_APPLICATION_UPDATE,
        DEPLOYMENT_BACKUP_ROLLBACK,
        POST_DEPLOYMENT_DIAGNOSTICS,
        DEPLOYMENT_CHECKLIST,
    ]

    for lesson_bundle in lesson_bundles:
        lesson = lesson_bundle["lesson"]
        searchable_content = " ".join(
            [
                lesson["description"],
                lesson["theory"],
                str(lesson["commands"]),
                lesson["practice_task"],
                str(lesson["common_mistakes"]),
                lesson["summary"],
            ]
        ).lower()

        for topic in required_topics[lesson["title"]]:
            assert topic in searchable_content


def test_lessons_page_contains_deployment_module_in_correct_order():
    response = client.get("/lessons")

    assert response.status_code == 200
    module_options = [
        'value="Podstawy terminala"',
        'value="Administracja systemem"',
        'value="Sieć i bezpieczeństwo"',
        'value="Deployment aplikacji"',
    ]
    positions = [response.text.index(option) for option in module_options]

    assert positions == sorted(positions)


def test_roadmap_shows_complete_deployment_stage_as_available():
    response = client.get("/roadmap/")

    assert response.status_code == 200
    assert "Deployment aplikacji" in response.text
    assert "Dostępne" in response.text
    assert "Przygotowanie aplikacji do wdrożenia" in response.text
    assert "Środowisko Python na serwerze" in response.text
    assert "Uruchamianie aplikacji przez Uvicorn" in response.text
    assert "Aplikacja jako usługa systemd" in response.text
    assert "Nginx jako reverse proxy" in response.text
    assert "Domena i rekordy DNS dla aplikacji" in response.text
    assert "HTTPS z Let&#39;s Encrypt i Certbot" in response.text
    assert "Zmienne środowiskowe i sekrety aplikacji" in response.text
    assert "Aktualizacja aplikacji przez Git" in response.text
    assert "Backup przed wdrożeniem i podstawowy rollback" in response.text
    assert "Logi i diagnostyka problemów po wdrożeniu" in response.text
    assert "Procedura deploymentu i lista kontrolna" in response.text
    assert 'href="/lessons"' in response.text


def test_deployment_module_contains_twelve_lessons_in_order():
    deployment_lessons = [
        lesson_bundle["lesson"]["title"]
        for lesson_bundle in LESSONS
        if lesson_bundle["module"]["title"] == "Deployment aplikacji"
    ]

    assert deployment_lessons == [
        "Przygotowanie aplikacji do wdrożenia",
        "Środowisko Python na serwerze",
        "Uruchamianie aplikacji przez Uvicorn",
        "Aplikacja jako usługa systemd",
        "Nginx jako reverse proxy",
        "Domena i rekordy DNS dla aplikacji",
        "HTTPS z Let's Encrypt i Certbot",
        "Zmienne środowiskowe i sekrety aplikacji",
        "Aktualizacja aplikacji przez Git",
        "Backup przed wdrożeniem i podstawowy rollback",
        "Logi i diagnostyka problemów po wdrożeniu",
        "Procedura deploymentu i lista kontrolna",
    ]


def test_roadmap_shows_complete_administration_stage_as_available():
    response = client.get("/roadmap/")

    assert response.status_code == 200
    assert "Administracja systemem" in response.text
    assert "Dostępne" in response.text
    assert "Zadania cykliczne: cron i podstawy systemd timers" in response.text


def test_roadmap_shows_network_security_stage_as_available():
    response = client.get("/roadmap/")

    assert response.status_code == 200
    assert "DNS w praktyce" in response.text
    assert "SSH w administracji systemem" in response.text
    assert "SELinux" in response.text
    assert "Bezpieczna konfiguracja SSH" in response.text
    assert "Klucze SSH w praktyce" in response.text
    assert "Firewalld" in response.text
    assert "Podstawy TLS i HTTPS" in response.text


def test_lessons_page_contains_filtering_ui():
    response = client.get("/lessons")

    assert response.status_code == 200
    assert "lesson-search" in response.text
    assert "lesson-level-filter" in response.text
    assert "lesson-module-filter" in response.text
    assert "lesson-visible-count" in response.text
    assert "lesson-filters-reset" in response.text


def test_lessons_page_groups_lessons_into_described_module_sections():
    response = client.get("/lessons")

    assert response.status_code == 200
    assert response.text.count("data-module-section") == 4

    section_markers = [
        'id="lesson-module-1-heading"',
        'id="lesson-module-2-heading"',
        'id="lesson-module-3-heading"',
        'id="lesson-module-4-heading"',
    ]
    positions = [response.text.index(marker) for marker in section_markers]
    rendered_lesson_titles = [
        unescape(title)
        for title in re.findall(
            r'data-title="([^"]+)"',
            response.text,
        )
    ]
    expected_lesson_titles = [
        lesson_bundle["lesson"]["title"]
        for lesson_bundle in LESSONS
    ]

    assert positions == sorted(positions)
    assert rendered_lesson_titles == expected_lesson_titles
    assert all(f"MODUŁ {number}" in response.text for number in range(1, 5))
    assert "Podstawy Linuxa i terminala" not in response.text
    assert "Ten blok prowadzi od pierwszych komend terminala" not in response.text
    assert "Pierwszy blok obejmuje podstawy Linuxa" not in response.text
    assert "Materiały uporządkowane w praktyczne moduły tematyczne." in response.text
    assert (
        "Poznaj najważniejsze polecenia i podstawowe zasady pracy w terminalu "
        "Linux. Nauczysz się poruszać po systemie plików, zarządzać plikami "
        "i katalogami oraz wykonywać codzienne operacje w wierszu poleceń."
        in response.text
    )
    assert (
        "Naucz się zarządzać usługami, użytkownikami, procesami i logami oraz "
        "diagnozować typowe problemy występujące w systemie Linux."
        in response.text
    )
    assert (
        "Poznaj podstawy konfiguracji sieci, DNS, SSH, firewalla i SELinux "
        "oraz naucz się diagnozować problemy z łącznością i dostępem do usług."
        in response.text
    )
    assert (
        "Przejdź przez proces przygotowania i wdrożenia aplikacji na serwer "
        "Linux — od środowiska Python i Uvicorna po systemd, Nginx, DNS, "
        "HTTPS, aktualizacje i diagnostykę po wdrożeniu."
        in response.text
    )


def test_admin_duty_page_returns_200():
    response = client.get("/admin-duty/")

    assert response.status_code == 200
    assert "Symulator" in response.text
    assert "Dyżur administratora" in response.text
    assert "Polecenia wykonywane w Symulatorze działają wyłącznie" in response.text
    assert "wykonywane na rzeczywistym serwerze" in response.text
    assert "Podstawowy" in response.text
    assert "10–15 min" not in response.text
    assert "Od objawów do rozwiązania" in response.text
    assert "Punktacja i samodzielność" in response.text
    assert "Podpowiedzi i rozwiązanie" in response.text
    assert "Symulowane środowisko" in response.text
    assert "Kolejne scenariusze" not in response.text
    assert "Uvicorn" not in response.text


def test_admin_duty_start_returns_scenario_redirect():
    admin_duty_sessions.clear()
    session = start_admin_duty_session()

    try:
        assert session["session_id"]
        assert session["redirect_url"].startswith(
            "/admin-duty/scenarios/inc-001/?session_id="
        )
        assert session["session_id"] in session["redirect_url"]
    finally:
        admin_duty_sessions.clear()


def test_admin_duty_session_stores_timestamps_and_updates_last_activity():
    admin_duty_sessions.clear()
    session = start_admin_duty_session()
    session_id = session["session_id"]

    try:
        stored_session = admin_duty_sessions[session_id]
        created_at = stored_session["created_at"]
        previous_activity = admin_duty_router_module.utc_now() - timedelta(
            minutes=1,
        )
        stored_session["last_activity"] = previous_activity

        response = client.post(
            "/admin-duty/api/command",
            json={
                "session_id": session_id,
                "command": "status",
            },
        )

        assert response.status_code == 200
        assert created_at.tzinfo is not None
        assert stored_session["last_activity"] > previous_activity
    finally:
        admin_duty_sessions.clear()


def test_admin_duty_expired_session_is_rejected_and_removed():
    admin_duty_sessions.clear()
    assert admin_duty_router_module.SESSION_TTL == timedelta(minutes=45)

    session = start_admin_duty_session()
    session_id = session["session_id"]
    expired_at = (
        admin_duty_router_module.utc_now()
        - admin_duty_router_module.SESSION_TTL
    )
    admin_duty_sessions[session_id]["last_activity"] = expired_at

    try:
        response = client.post(
            "/admin-duty/api/command",
            json={
                "session_id": session_id,
                "command": "status",
            },
        )

        assert response.status_code == 404
        assert session_id not in admin_duty_sessions
    finally:
        admin_duty_sessions.clear()


def test_admin_duty_start_cleans_up_expired_sessions():
    admin_duty_sessions.clear()
    expired_session = start_admin_duty_session()
    active_session = start_admin_duty_session()
    expired_session_id = expired_session["session_id"]
    active_session_id = active_session["session_id"]
    admin_duty_sessions[expired_session_id]["last_activity"] = (
        admin_duty_router_module.utc_now()
        - admin_duty_router_module.SESSION_TTL
    )

    try:
        new_session = start_admin_duty_session()

        assert expired_session_id not in admin_duty_sessions
        assert active_session_id in admin_duty_sessions
        assert new_session["session_id"] in admin_duty_sessions
    finally:
        admin_duty_sessions.clear()


def test_admin_duty_start_returns_503_at_active_session_limit(monkeypatch):
    admin_duty_sessions.clear()
    assert admin_duty_router_module.MAX_ACTIVE_SESSIONS == 500

    monkeypatch.setattr(
        admin_duty_router_module,
        "MAX_ACTIVE_SESSIONS",
        2,
    )

    try:
        start_admin_duty_session()
        start_admin_duty_session()

        response = client.post(
            "/admin-duty/api/start",
            json={"scenario_id": "INC-001"},
        )

        assert response.status_code == 503
        assert len(admin_duty_sessions) == 2
    finally:
        admin_duty_sessions.clear()


def test_admin_duty_rejects_invalid_session_uuid():
    response = client.post(
        "/admin-duty/api/command",
        json={
            "session_id": "not-a-uuid",
            "command": "status",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Nieprawidłowe dane żądania.",
    }


def test_admin_duty_rejects_command_longer_than_1024_characters(
    admin_duty_session,
):
    response = client.post(
        "/admin-duty/api/command",
        json={
            "session_id": admin_duty_session["session_id"],
            "command": "x" * 1025,
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Nieprawidłowe dane żądania.",
    }


def test_admin_duty_rejects_service_file_larger_than_32_kib(
    admin_duty_session,
):
    response = client.post(
        "/admin-duty/api/service-file",
        json={
            "session_id": admin_duty_session["session_id"],
            "content": "ą" * 16385,
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Nieprawidłowe dane żądania.",
    }


def test_admin_duty_rejects_unknown_request_field():
    admin_duty_sessions.clear()

    try:
        response = client.post(
            "/admin-duty/api/start",
            json={
                "scenario_id": "INC-001",
                "unexpected": True,
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Nieprawidłowe dane żądania.",
        }
        assert not admin_duty_sessions
    finally:
        admin_duty_sessions.clear()


def test_admin_duty_rejects_unsupported_scenario():
    admin_duty_sessions.clear()

    try:
        response = client.post(
            "/admin-duty/api/start",
            json={"scenario_id": "INC-999"},
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Nieprawidłowe dane żądania.",
        }
        assert not admin_duty_sessions
    finally:
        admin_duty_sessions.clear()


def test_admin_duty_scenario_without_session_redirects():
    response = client.get(
        "/admin-duty/scenarios/inc-001/",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/admin-duty/?view=scenarios"


def test_admin_duty_valid_session_opens_scenario(admin_duty_session):
    response = client.get(admin_duty_session["redirect_url"])

    assert response.status_code == 200
    assert "502 po wdrożeniu" in response.text
    assert "Cele incydentu" in response.text


def test_admin_duty_command_returns_objective_progress(admin_duty_session):
    response = client.post(
        "/admin-duty/api/command",
        json={
            "session_id": admin_duty_session["session_id"],
            "command": "curl https://portal.ironvale.internal",
        },
    )

    assert response.status_code == 200
    result = response.json()
    objectives = {
        objective["key"]: objective["completed"]
        for objective in result["progress"]["objectives"]
    }

    assert result["output"] == "HTTP/2 502\nBad Gateway"
    assert objectives["check_portal"] is True
    assert objectives["verify_portal"] is False


def test_admin_duty_hints_reduce_score(admin_duty_session):
    scores = []
    costs = []

    for _ in range(3):
        response = client.post(
            "/admin-duty/api/hint",
            json={"session_id": admin_duty_session["session_id"]},
        )

        assert response.status_code == 200
        result = response.json()
        scores.append(result["progress"]["score"])
        costs.append(result["cost"])

    assert costs == [25, 50, 100]
    assert scores == [975, 925, 825]

    exhausted = client.post(
        "/admin-duty/api/hint",
        json={"session_id": admin_duty_session["session_id"]},
    ).json()

    assert exhausted["available"] is False
    assert exhausted["progress"]["score"] == 825


def test_admin_duty_solution_is_structured_and_caps_score(admin_duty_session):
    response = client.post(
        "/admin-duty/api/solution",
        json={"session_id": admin_duty_session["session_id"]},
    )

    assert response.status_code == 200
    result = response.json()

    assert result["progress"]["solution_viewed"] is True
    assert result["progress"]["score"] == 500
    assert result["steps"][0]["command"] == (
        "curl https://portal.ironvale.internal"
    )

    editor_step = next(
        step for step in result["steps"] if step["command"] == "edit-service"
    )

    assert "/opt/ironvale/venv/bin/uvicorn" in editor_step["instruction"]
    assert "/srv/ironvale/venv/bin/uvicorn" in editor_step["instruction"]

    repeated = client.post(
        "/admin-duty/api/solution",
        json={"session_id": admin_duty_session["session_id"]},
    ).json()

    assert repeated["progress"]["score"] == 500


def test_admin_duty_end_removes_session(admin_duty_session):
    session_id = admin_duty_session["session_id"]
    response = client.post(
        "/admin-duty/api/end",
        json={"session_id": session_id},
    )

    assert response.status_code == 200
    assert response.json() == {"ended": True}

    missing_session = client.post(
        "/admin-duty/api/command",
        json={
            "session_id": session_id,
            "command": "status",
        },
    )

    assert missing_session.status_code == 404


def test_admin_duty_complete_command_sequence_finishes_scenario(
    admin_duty_session,
):
    session_id = admin_duty_session["session_id"]

    diagnostic_commands = [
        "curl https://portal.ironvale.internal",
        "systemctl status ironvale-api",
        "journalctl -u ironvale-api",
    ]

    for command in diagnostic_commands:
        response = client.post(
            "/admin-duty/api/command",
            json={
                "session_id": session_id,
                "command": command,
            },
        )

        assert response.status_code == 200

    service_file = SERVICE_FILE.format(exec_start=CORRECT_EXEC_START)
    saved = client.post(
        "/admin-duty/api/service-file",
        json={
            "session_id": session_id,
            "content": service_file,
        },
    )

    assert saved.status_code == 200
    assert saved.json()["success"] is True

    repair_commands = [
        "systemctl daemon-reload",
        "systemctl restart ironvale-api",
        "curl https://portal.ironvale.internal",
    ]

    for command in repair_commands:
        response = client.post(
            "/admin-duty/api/command",
            json={
                "session_id": session_id,
                "command": command,
            },
        )

        assert response.status_code == 200

    progress = response.json()["progress"]

    assert progress["mission_complete"] is True
    assert all(objective["completed"] for objective in progress["objectives"])


def test_admin_duty_terminal_pwd_and_cd_navigation(admin_duty_session):
    session_id = admin_duty_session["session_id"]

    initial = run_admin_duty_command(session_id, "pwd")
    changed = run_admin_duty_command(
        session_id,
        "cd /etc/systemd/system",
    )
    parent = run_admin_duty_command(session_id, "cd ..")
    home_without_argument = run_admin_duty_command(session_id, "cd")
    run_admin_duty_command(session_id, "cd /srv/ironvale")
    home_with_tilde = run_admin_duty_command(session_id, "cd ~")

    assert initial["output"] == "/home/operator"
    assert changed["cwd"] == "/etc/systemd/system"
    assert parent["cwd"] == "/etc/systemd"
    assert home_without_argument["cwd"] == "/home/operator"
    assert home_with_tilde["cwd"] == "/home/operator"


def test_admin_duty_terminal_lists_virtual_filesystem(admin_duty_session):
    session_id = admin_duty_session["session_id"]

    root = run_admin_duty_command(session_id, "ls /")
    home = run_admin_duty_command(session_id, "ls -la /home/operator")
    active_bin = run_admin_duty_command(
        session_id,
        "ls -la /srv/ironvale/venv/bin",
    )
    legacy_bin = run_admin_duty_command(
        session_id,
        "ls -al /opt/ironvale/venv/bin",
    )

    assert all(directory in root["output"] for directory in ["etc", "opt", "srv"])
    assert ".profile" in home["output"]
    assert "drwxr-x" in home["output"]
    assert "uvicorn" in active_bin["output"]
    assert "-rwxr-xr-x" in active_bin["output"]
    assert "uvicorn" not in legacy_bin["output"]


def test_admin_duty_terminal_cat_supports_paths_and_multiple_files(
    admin_duty_session,
):
    session_id = admin_duty_session["session_id"]
    run_admin_duty_command(
        session_id,
        "cd /etc/systemd/system",
    )

    relative = run_admin_duty_command(
        session_id,
        "cat ironvale-api.service",
    )
    multiple = run_admin_duty_command(
        session_id,
        "cat /home/operator/.profile /srv/ironvale/venv/bin/uvicorn",
    )

    assert f"ExecStart={BROKEN_EXEC_START}" in relative["output"]
    assert "export EDITOR=vi" in multiple["output"]
    assert "from uvicorn.main import main" in multiple["output"]


def test_admin_duty_terminal_reports_path_errors(admin_duty_session):
    session_id = admin_duty_session["session_id"]

    missing_directory = run_admin_duty_command(
        session_id,
        "cd /nie-istnieje",
    )
    missing_list = run_admin_duty_command(
        session_id,
        "ls /nie-istnieje",
    )
    directory_cat = run_admin_duty_command(
        session_id,
        "cat /srv/ironvale",
    )
    missing_cat = run_admin_duty_command(
        session_id,
        "cat /srv/ironvale/brak.txt",
    )

    assert missing_directory["type"] == "error"
    assert missing_directory["cwd"] == "/home/operator"
    assert "Nie ma takiego pliku ani katalogu" in missing_list["output"]
    assert "Jest katalogiem" in directory_cat["output"]
    assert "Nie ma takiego pliku ani katalogu" in missing_cat["output"]


def test_admin_duty_help_describes_commands_without_solution_sequence(
    admin_duty_session,
):
    session_id = admin_duty_session["session_id"]

    general_help = run_admin_duty_command(session_id, "help")
    systemctl_help = run_admin_duty_command(session_id, "help systemctl")

    assert "ls [-la] [ścieżka]" in general_help["output"]
    assert "cat <plik> [plik...]" in general_help["output"]
    assert "curl https://portal.ironvale.internal" not in general_help["output"]
    assert "journalctl -u ironvale-api" not in general_help["output"]
    assert "systemctl status ironvale-api" not in general_help["output"]
    assert "systemctl status <usługa>" in systemctl_help["output"]
    assert "systemctl daemon-reload" in systemctl_help["output"]


def test_admin_duty_virtual_exploration_identifies_cause(admin_duty_session):
    session_id = admin_duty_session["session_id"]

    inspected_unit = run_admin_duty_command(
        session_id,
        "cat /etc/systemd/system/ironvale-api.service",
    )
    found_binary = run_admin_duty_command(
        session_id,
        "ls /srv/ironvale/venv/bin",
    )

    objectives = {
        objective["key"]: objective["completed"]
        for objective in found_binary["progress"]["objectives"]
    }

    assert f"ExecStart={BROKEN_EXEC_START}" in inspected_unit["output"]
    assert "uvicorn" in found_binary["output"]
    assert objectives["find_cause"] is True


def test_admin_duty_editor_save_updates_cat_content(admin_duty_session):
    session_id = admin_duty_session["session_id"]
    updated_content = SERVICE_FILE.format(exec_start=CORRECT_EXEC_START)

    saved = client.post(
        "/admin-duty/api/service-file",
        json={
            "session_id": session_id,
            "content": updated_content,
        },
    )
    read_back = run_admin_duty_command(
        session_id,
        "cat /etc/systemd/system/ironvale-api.service",
    )

    assert saved.status_code == 200
    assert saved.json()["success"] is True
    assert saved.json()["configuration_fixed"] is True
    assert "Zmiany zostały zapisane" in saved.json()["message"]
    assert read_back["output"] == updated_content.rstrip("\n")


def test_admin_duty_editor_persists_incorrect_content_with_warning(
    admin_duty_session,
):
    session_id = admin_duty_session["session_id"]
    incorrect_content = SERVICE_FILE.format(
        exec_start="/srv/ironvale/venv/bin/brak",
    )

    saved = client.post(
        "/admin-duty/api/service-file",
        json={
            "session_id": session_id,
            "content": incorrect_content,
        },
    ).json()
    read_back = run_admin_duty_command(
        session_id,
        "cat /etc/systemd/system/ironvale-api.service",
    )

    assert saved["success"] is True
    assert saved["configuration_fixed"] is False
    assert "nadal jest nieprawidłowy" in saved["message"]
    assert read_back["output"] == incorrect_content.rstrip("\n")


def test_admin_duty_virtual_files_are_isolated_between_sessions(
    admin_duty_session,
):
    first_session_id = admin_duty_session["session_id"]
    second_session = start_admin_duty_session()
    second_session_id = second_session["session_id"]
    updated_content = SERVICE_FILE.format(exec_start=CORRECT_EXEC_START)

    client.post(
        "/admin-duty/api/service-file",
        json={
            "session_id": first_session_id,
            "content": updated_content,
        },
    )

    first_content = run_admin_duty_command(
        first_session_id,
        "cat /etc/systemd/system/ironvale-api.service",
    )
    second_content = run_admin_duty_command(
        second_session_id,
        "cat /etc/systemd/system/ironvale-api.service",
    )

    assert f"ExecStart={CORRECT_EXEC_START}" in first_content["output"]
    assert f"ExecStart={BROKEN_EXEC_START}" in second_content["output"]


def test_admin_duty_editor_has_visible_save_and_cancel_actions(
    admin_duty_session,
):
    response = client.get(admin_duty_session["redirect_url"])

    assert response.status_code == 200
    assert "Zapisz zmiany" in response.text
    assert "Anuluj" in response.text
    assert 'id="editor-message"' in response.text
