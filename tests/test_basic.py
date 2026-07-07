from fastapi.testclient import TestClient

from app.content.disk_space_cleanup import DISK_SPACE_CLEANUP
from app.content.dns_practice import DNS_PRACTICE
from app.content.firewall_basics import FIREWALL_BASICS
from app.content.firewalld_zones_services_ports import FIREWALLD_ZONES_SERVICES_PORTS
from app.content.ip_addressing import IP_ADDRESSING
from app.content.log_analysis import LOG_ANALYSIS
from app.content.network_dns_routing_connections import NETWORK_DNS_ROUTING_CONNECTIONS
from app.content.network_ports_services import NETWORK_PORTS_SERVICES
from app.content.scheduled_tasks import SCHEDULED_TASKS
from app.content.selinux_basics import SELINUX_BASICS
from app.content.selinux_troubleshooting import SELINUX_TROUBLESHOOTING
from app.content.ssh_administration import SSH_ADMINISTRATION
from app.content.ssh_keys_practice import SSH_KEYS_PRACTICE
from app.content.ssh_secure_configuration import SSH_SECURE_CONFIGURATION
from app.content.systemd_diagnostics import SYSTEMD_DIAGNOSTICS
from app.content.tls_https_basics import TLS_HTTPS_BASICS
from app.database import create_db_and_tables
from app.main import app
from app.seed import seed_database

create_db_and_tables()
seed_database()

client = TestClient(app)


def test_home_page_returns_200():
    response = client.get("/")

    assert response.status_code == 200
    assert "ShellForge" in response.text


def test_lessons_page_returns_200():
    response = client.get("/lessons")

    assert response.status_code == 200
    assert "Lekcje ShellForge" in response.text


def test_lesson_detail_page_returns_200():
    response = client.get("/lessons/1")

    assert response.status_code == 200
    assert "Gdzie jestem? Komendy pwd, ls i cd" in response.text


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


def test_custom_404_page_returns_404():
    response = client.get("/nieistniejaca-strona")

    assert response.status_code == 404
    assert "Nie znaleziono strony" in response.text


def test_about_page_returns_200():
    response = client.get("/about/")

    assert response.status_code == 200
    assert "Czym jest ShellForge?" in response.text


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


def test_lessons_page_contains_learning_block_summary():
    response = client.get("/lessons")

    assert response.status_code == 200
    assert "Podstawy Linuxa i terminala" in response.text
    assert "Pierwszy blok obejmuje podstawy Linuxa" in response.text
