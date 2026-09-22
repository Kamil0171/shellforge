import re
from html import unescape
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlmodel import Session, select

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
from app.models import Flashcard, LearningModule, Lesson, Quiz, QuizAnswer, QuizQuestion
from app.routers.lessons import get_adjacent_lessons
from app.seed import LESSONS, seed_database

create_db_and_tables()
seed_database()

client = TestClient(app)


def get_ordered_lessons():
    with Session(engine) as session:
        return session.exec(select(Lesson).order_by(Lesson.id)).all()


def test_home_page_returns_200():
    response = client.get("/")

    assert response.status_code == 200
    assert "ShellForge" in response.text
    assert "Rozwiąż incydent" in response.text
    assert "Sprawdź się w praktyce" in response.text
    assert "Dynamic Incident" in response.text
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


def test_lessons_page_contains_local_progress_ui():
    lessons = get_ordered_lessons()
    response = client.get("/lessons")

    assert response.status_code == 200
    assert 'id="lesson-completed-count"' in response.text
    assert 'id="lesson-total-count"' in response.text
    assert "Postęp jest zapisywany lokalnie w tej przeglądarce." in response.text
    assert 'src="http://testserver/static/js/lesson_progress.js"' in response.text
    assert response.text.count("data-lesson-completed-status") == len(lessons)

    for lesson in lessons:
        assert f'data-lesson-id="{lesson.id}"' in response.text


def test_lesson_detail_page_contains_local_progress_control():
    lesson = get_ordered_lessons()[0]
    response = client.get(f"/lessons/{lesson.id}")

    assert response.status_code == 200
    assert "data-lesson-progress-detail" in response.text
    assert f'data-lesson-id="{lesson.id}"' in response.text
    assert "data-lesson-completion-toggle" in response.text
    assert 'aria-pressed="false"' in response.text
    assert "Oznacz jako ukończoną" in response.text
    assert 'src="http://testserver/static/js/lesson_progress.js"' in response.text


def test_lessons_page_groups_lessons_into_described_module_sections():
    response = client.get("/lessons")

    assert response.status_code == 200
    assert response.text.count("data-module-section") == 6

    section_markers = [
        'id="lesson-module-1-heading"',
        'id="lesson-module-2-heading"',
        'id="lesson-module-3-heading"',
        'id="lesson-module-4-heading"',
        'id="lesson-module-5-heading"',
        'id="lesson-module-6-heading"',
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
        lesson_bundle["lesson"]["title"] for lesson_bundle in LESSONS
    ]

    assert positions == sorted(positions)
    assert rendered_lesson_titles == expected_lesson_titles
    assert all(f"MODUŁ {number}" in response.text for number in range(1, 7))
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
        "diagnozować typowe problemy występujące w systemie Linux." in response.text
    )
    assert (
        "Poznaj podstawy konfiguracji sieci, DNS, SSH, firewalla i SELinux "
        "oraz naucz się diagnozować problemy z łącznością i dostępem do usług."
        in response.text
    )
    assert (
        "Przejdź przez proces przygotowania i wdrożenia aplikacji na serwer "
        "Linux — od środowiska Python i Uvicorna po systemd, Nginx, DNS, "
        "HTTPS, aktualizacje i diagnostykę po wdrożeniu." in response.text
    )
    assert (
        "Poznaj kontenery i budowanie obrazów aplikacji, połącz usługę z PostgreSQL "
        "oraz zautomatyzuj testy i przygotowanie zmian przez GitHub Actions."
        in response.text
    )
    assert (
        "Sprawdzaj stan aplikacji, analizuj logi i metryki, reaguj na alerty oraz "
        "ćwicz bezpieczne kopie i odtwarzanie danych."
        in response.text
    )


DEVOPS_TITLES = [
    "Podstawy konteneryzacji",
    "Cykl życia kontenera i diagnostyka",
    "Dane, porty i sieć kontenerów",
    "Dockerfile dla aplikacji webowej",
    "Budowanie obrazów: kontekst, .dockerignore i cache",
    "Bezpieczny obraz aplikacji",
    "PostgreSQL w środowisku aplikacji",
    "Aplikacja i baza w Docker Compose",
    "Trwałość danych, migracje i podstawowy backup PostgreSQL",
    "CI/CD z GitHub Actions: pierwszy workflow",
    "Automatyczne testy i budowanie w pipeline",
    "Dostarczanie zmian i diagnostyka pipeline",
]

MONITORING_TITLES = [
    "Health checki i gotowość aplikacji",
    "Obserwowalność: logi, metryki i ślady",
    "Logi usług i aplikacji",
    "Monitoring aplikacji i zależności",
    "Metryki i percentyle w praktyce",
    "Alerty i eskalacja",
    "SLI, SLO, SLA i budżet błędów",
    "Diagnoza incydentu: od alertu do weryfikacji",
    "Strategia backupu aplikacji",
    "Backup PostgreSQL w kontenerze",
    "Odtworzenie PostgreSQL i test kopii",
    "Runbook i utrzymanie po wdrożeniu",
]


def test_devops_content_order_structure_and_placeholder_audit():
    assert len(LESSONS) == 66
    assert [bundle["lesson"]["title"] for bundle in LESSONS[42:54]] == DEVOPS_TITLES

    all_question_texts = []
    all_flashcard_questions = []
    for bundle in LESSONS[42:54]:
        lesson = bundle["lesson"]
        assert bundle["module"]["title"] == "DevOps i automatyzacja"
        assert lesson["level"] == "Średnio zaawansowany"
        assert all(lesson[key] for key in (
            "title", "duration", "description", "theory", "commands",
            "practice_task", "common_mistakes", "summary",
        ))
        assert all(all(command[key] for key in ("command", "description", "example"))
                   for command in lesson["commands"])
        assert len(bundle["quiz"]["questions"]) == 6
        assert len(bundle["flashcards"]) == 25
        assert len({card["question"] for card in bundle["flashcards"]}) == 25
        assert len({card["answer"] for card in bundle["flashcards"]}) == 25

        visible_text = [
            bundle["module"]["title"], bundle["module"]["description"],
            *(lesson[key] for key in (
                "title", "level", "duration", "description", "theory",
                "practice_task", "summary",
            )),
            *lesson["common_mistakes"],
            *(value for command in lesson["commands"] for value in command.values()),
            bundle["quiz"]["title"], bundle["quiz"]["description"],
        ]

        for question in bundle["quiz"]["questions"]:
            all_question_texts.append(question["text"])
            visible_text.append(question["text"])
            assert [answer[0] for answer in question["answers"]] == ["a", "b", "c", "d"]
            assert len({answer[1] for answer in question["answers"]}) == 4
            assert sum(answer[2] for answer in question["answers"]) == 1
            visible_text.extend(answer[1] for answer in question["answers"])

        for card in bundle["flashcards"]:
            assert card["question"] and card["answer"]
            all_flashcard_questions.append(card["question"])
            visible_text.extend((card["question"], card["answer"]))

        assert not re.search(r"\b(?:example|sample|demo)\b", " ".join(visible_text), re.I)

    assert len(set(all_question_texts)) == 72
    assert len(set(all_flashcard_questions)) == 300


def test_devops_seed_is_idempotent_and_ids_are_continuous():
    before = get_ordered_lessons()
    assert [(lesson.id, lesson.title) for lesson in before[42:54]] == list(
        zip(range(43, 55), DEVOPS_TITLES, strict=True)
    )
    seed_database()
    after = get_ordered_lessons()
    assert [(lesson.id, lesson.title) for lesson in after] == [
        (lesson.id, lesson.title) for lesson in before
    ]

    with Session(engine) as session:
        modules = session.exec(select(LearningModule)).all()
        devops_module = next(module for module in modules if module.title == "DevOps i automatyzacja")
        assert all(lesson.module_id == devops_module.id for lesson in after[42:54])
        assert len({lesson.id for lesson in after}) == 66

        for lesson in after[42:54]:
            quiz = session.exec(select(Quiz).where(Quiz.lesson_id == lesson.id)).one()
            questions = session.exec(select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id)).all()
            cards = session.exec(select(Flashcard).where(Flashcard.lesson_id == lesson.id)).all()
            assert len(questions) == 6
            assert {question.position for question in questions} == set(range(1, 7))
            assert len(cards) == 25
            assert {card.position for card in cards} == set(range(1, 26))
            for question in questions:
                answers = session.exec(select(QuizAnswer).where(QuizAnswer.question_id == question.id)).all()
                assert len(answers) == 4
                assert sum(answer.is_correct for answer in answers) == 1


def test_devops_pages_navigation_and_learning_path():
    for lesson_id, title in enumerate(DEVOPS_TITLES, start=43):
        lesson_response = client.get(f"/lessons/{lesson_id}")
        assert lesson_response.status_code == 200
        assert title in unescape(lesson_response.text)
        assert client.get(f"/quiz/{lesson_id}").status_code == 200
        assert client.get(f"/flashcards/{lesson_id}").status_code == 200

    last_deployment = client.get("/lessons/42")
    first_devops = client.get("/lessons/43")
    last_devops = client.get("/lessons/54")
    assert 'href="/lessons/43"' in last_deployment.text
    assert 'href="/lessons/42"' in first_devops.text
    assert 'href="/lessons/44"' in first_devops.text
    assert 'href="/lessons/53"' in last_devops.text
    assert 'href="/lessons/55"' in last_devops.text

    roadmap = client.get("/roadmap/")
    assert roadmap.status_code == 200
    level_five = roadmap.text.split("Poziom 5", 1)[1].split("Poziom 6", 1)[0]
    assert "DevOps i automatyzacja" in level_five
    assert "Dostępne" in level_five
    assert "Planowane" not in level_five
    assert 'href="/lessons"' in level_five
    assert all(unescape(title) in unescape(level_five) for title in DEVOPS_TITLES)
    assert "Dostępne" in roadmap.text.split("Poziom 6", 1)[1]


def test_monitoring_content_order_structure_uniqueness_and_placeholder_audit():
    assert len(LESSONS) == 66
    assert [bundle["lesson"]["title"] for bundle in LESSONS[54:]] == MONITORING_TITLES

    all_question_texts = []
    all_flashcard_questions = []
    all_flashcard_answers = []
    for bundle in LESSONS[54:]:
        lesson = bundle["lesson"]
        assert bundle["module"]["title"] == "Monitoring i utrzymanie"
        assert lesson["level"] == "Średnio zaawansowany"
        assert all(
            lesson[key]
            for key in (
                "title",
                "duration",
                "description",
                "theory",
                "commands",
                "practice_task",
                "common_mistakes",
                "summary",
            )
        )
        assert all(
            all(command[key] for key in ("command", "description", "example"))
            for command in lesson["commands"]
        )
        assert len(bundle["quiz"]["questions"]) == 6
        assert len(bundle["flashcards"]) == 25
        assert len({card["question"] for card in bundle["flashcards"]}) == 25
        assert len({card["answer"] for card in bundle["flashcards"]}) == 25

        visible_text = [
            bundle["module"]["title"],
            bundle["module"]["description"],
            *(
                lesson[key]
                for key in (
                    "title",
                    "level",
                    "duration",
                    "description",
                    "theory",
                    "practice_task",
                    "summary",
                )
            ),
            *lesson["common_mistakes"],
            *(value for command in lesson["commands"] for value in command.values()),
            bundle["quiz"]["title"],
            bundle["quiz"]["description"],
        ]

        for question in bundle["quiz"]["questions"]:
            all_question_texts.append(question["text"])
            visible_text.append(question["text"])
            assert [answer[0] for answer in question["answers"]] == ["a", "b", "c", "d"]
            assert len({answer[1] for answer in question["answers"]}) == 4
            assert sum(answer[2] for answer in question["answers"]) == 1
            visible_text.extend(answer[1] for answer in question["answers"])

        for card in bundle["flashcards"]:
            all_flashcard_questions.append(card["question"])
            all_flashcard_answers.append(card["answer"])
            visible_text.extend((card["question"], card["answer"]))

        assert not re.search(r"\b(?:example|sample|demo)\b", " ".join(visible_text), re.I)

    assert len(set(all_question_texts)) == 72
    assert len(set(all_flashcard_questions)) == 300
    assert len(set(all_flashcard_answers)) == 300


def test_monitoring_seed_is_idempotent_and_preserves_existing_ids():
    before = get_ordered_lessons()
    assert [(lesson.id, lesson.title) for lesson in before[:54]] == list(
        zip(
            range(1, 55),
            [bundle["lesson"]["title"] for bundle in LESSONS[:54]],
            strict=True,
        )
    )
    assert [(lesson.id, lesson.title) for lesson in before[54:]] == list(
        zip(range(55, 67), MONITORING_TITLES, strict=True)
    )

    seed_database()
    after = get_ordered_lessons()
    assert [(lesson.id, lesson.title) for lesson in after] == [
        (lesson.id, lesson.title) for lesson in before
    ]

    with Session(engine) as session:
        modules = session.exec(select(LearningModule)).all()
        monitoring_module = next(
            module for module in modules if module.title == "Monitoring i utrzymanie"
        )
        assert all(lesson.module_id == monitoring_module.id for lesson in after[54:])
        assert len(after) == 66
        assert len({lesson.id for lesson in after}) == 66

        for lesson in after[54:]:
            quizzes = session.exec(select(Quiz).where(Quiz.lesson_id == lesson.id)).all()
            cards = session.exec(
                select(Flashcard).where(Flashcard.lesson_id == lesson.id)
            ).all()
            assert len(quizzes) == 1
            questions = session.exec(
                select(QuizQuestion).where(QuizQuestion.quiz_id == quizzes[0].id)
            ).all()
            assert len(questions) == 6
            assert {question.position for question in questions} == set(range(1, 7))
            assert len(cards) == 25
            assert {card.position for card in cards} == set(range(1, 26))
            for question in questions:
                answers = session.exec(
                    select(QuizAnswer).where(QuizAnswer.question_id == question.id)
                ).all()
                assert len(answers) == 4
                assert sum(answer.is_correct for answer in answers) == 1


def test_monitoring_pages_navigation_and_all_roadmap_levels_available():
    for lesson_id, title in enumerate(MONITORING_TITLES, start=55):
        lesson_response = client.get(f"/lessons/{lesson_id}")
        assert lesson_response.status_code == 200
        assert title in unescape(lesson_response.text)
        assert client.get(f"/quiz/{lesson_id}").status_code == 200
        assert client.get(f"/flashcards/{lesson_id}").status_code == 200

    lesson_54 = client.get("/lessons/54")
    lesson_55 = client.get("/lessons/55")
    lesson_66 = client.get("/lessons/66")
    assert 'href="/lessons/55"' in lesson_54.text
    assert 'href="/lessons/54"' in lesson_55.text
    assert 'href="/lessons/56"' in lesson_55.text
    assert 'href="/lessons/65"' in lesson_66.text
    assert "Następna lekcja" not in lesson_66.text

    roadmap = client.get("/roadmap/")
    assert roadmap.status_code == 200
    rendered = unescape(roadmap.text)
    for level in range(1, 7):
        start = rendered.index(f"Poziom {level}")
        end = rendered.find(f"Poziom {level + 1}", start)
        stage = rendered[start:] if end == -1 else rendered[start:end]
        assert "Dostępne" in stage
        assert "Planowane" not in stage
    level_six = rendered.split("Poziom 6", 1)[1]
    assert 'href="/lessons/55"' in level_six
    assert all(title in level_six for title in MONITORING_TITLES)


def test_admin_duty_page_returns_200():
    response = client.get("/admin-duty/")

    assert response.status_code == 200
    assert "Symulator" in response.text
    assert "Dyżur administratora" in response.text
    assert "Polecenia wykonywane w Symulatorze działają wyłącznie" in response.text
    assert "wykonywane na rzeczywistym serwerze" in response.text
    assert "Poziom podstawowy" in response.text
    assert "10–15 min" not in response.text
    assert "Od objawów do rozwiązania" in response.text
    assert "Punktacja i samodzielność" in response.text
    assert "Podpowiedzi i rozwiązanie" in response.text
    assert "Symulowane środowisko" in response.text
    assert "Kolejne scenariusze" not in response.text
    assert "Uvicorn" not in response.text
