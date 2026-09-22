from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/roadmap", tags=["roadmap"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def roadmap_page(request: Request):
    learning_path = [
        {
            "level": "Poziom 1",
            "title": "Podstawy Linuxa",
            "status": "Dostępne",
            "status_type": "active",
            "description": (
                "Pierwszy etap uczy swobodnej pracy w terminalu. To fundament, "
                "bez którego trudno przejść do administracji systemem, sieci, "
                "deploymentu i automatyzacji."
            ),
            "lessons": [
                "Gdzie jestem? Komendy pwd, ls i cd",
                "Pliki i katalogi: mkdir, touch, cp, mv i rm",
                "Uprawnienia plików: chmod, rwx, 755 i 644",
                "Użytkownicy i grupy: whoami, id i groups",
                "Procesy w Linuxie: ps, top, kill i PID",
                "Praca z plikami tekstowymi: cat, less, tail, grep i nano",
                "Pakiety i aktualizacje: yum, rpm i repozytoria",
            ],
            "cta_label": "Przejdź do lekcji",
            "cta_url": "/lessons",
        },
        {
            "level": "Poziom 2",
            "title": "Administracja systemem",
            "status": "Dostępne",
            "status_type": "active",
            "description": (
                "Kompletny etap rozwijający podstawy w kierunku codziennej pracy administratora. "
                "Użytkownik uczy się zarządzania usługami, logami, kontami, miejscem na dysku "
                "oraz zadaniami cyklicznymi."
            ),
            "lessons": [
                "Usługi systemowe: systemctl i systemd",
                "Logi systemowe: journalctl i katalog /var/log",
                "Struktura katalogów administracyjnych: /etc, /var, /opt, /usr i /tmp",
                "Podstawowa diagnostyka systemu: uptime, free, df, du i hostnamectl",
                "Sudo i praca administratora: sudo, su, root i dobre praktyki",
                "Zarządzanie użytkownikami i grupami: useradd, passwd, usermod i userdel",
                "Diagnostyka usług systemd: systemctl status, restart, enable i journalctl -u",
                "Analiza logów w praktyce: journalctl, /var/log i filtrowanie zdarzeń",
                "Miejsce na dysku i porządkowanie systemu: df, du, cache i logi",
                "Zadania cykliczne: cron i podstawy systemd timers",
            ],
            "cta_label": "Przejdź do lekcji",
            "cta_url": "/lessons",
        },
        {
            "level": "Poziom 3",
            "title": "Sieć i bezpieczeństwo",
            "status": "Dostępne",
            "status_type": "active",
            "description": (
                "Kompletny etap skupia się na podstawach komunikacji sieciowej, "
                "DNS, portach, zdalnym logowaniu, firewallu, SELinux oraz HTTPS "
                "w codziennej administracji serwerem Linux."
            ),
            "lessons": [
                "Podstawy adresacji IP",
                "DNS w praktyce",
                "Porty i usługi sieciowe",
                "SSH w administracji systemem",
                "Firewall — podstawy",
                "SELinux — podstawowe pojęcia",
                "Bezpieczna konfiguracja SSH",
                "Klucze SSH w praktyce",
                "Firewalld — strefy, usługi i porty",
                "SELinux — diagnostyka problemów",
                "Diagnostyka DNS, routingu i połączeń",
                "Podstawy TLS i HTTPS",
            ],
            "cta_label": "Przejdź do lekcji",
            "cta_url": "/lessons",
        },
        {
            "level": "Poziom 4",
            "title": "Deployment aplikacji",
            "status": "Dostępne",
            "status_type": "active",
            "description": (
                "Kompletny etap pokazuje, jak przygotować aplikację Python, uruchomić ją jako usługę, "
                "udostępnić przez Nginx i HTTPS oraz bezpiecznie aktualizować i diagnozować wdrożenie."
            ),
            "lessons": [
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
            ],
            "cta_label": "Przejdź do lekcji",
            "cta_url": "/lessons",
        },
        {
            "level": "Poziom 5",
            "title": "DevOps i automatyzacja",
            "status": "Dostępne",
            "status_type": "active",
            "description": (
                "Kompletny etap prowadzi od kontenerów i obrazów aplikacji przez "
                "PostgreSQL po automatyczne testy, budowanie i kontrolowane "
                "dostarczanie zmian w GitHub Actions."
            ),
            "lessons": [
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
            ],
            "cta_label": "Przejdź do lekcji",
            "cta_url": "/lessons",
        },
        {
            "level": "Poziom 6",
            "title": "Monitoring i utrzymanie",
            "status": "Dostępne",
            "status_type": "active",
            "description": (
                "Kompletny etap prowadzi od health checków, logów i metryk przez alerty, "
                "SLO oraz diagnozę incydentów do bezpiecznych kopii, odtwarzania i runbooka."
            ),
            "lessons": [
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
            ],
            "cta_label": "Przejdź do lekcji",
            "cta_url": "/lessons/55",
        },
    ]

    return templates.TemplateResponse(
        request=request,
        name="roadmap.html",
        context={
            "learning_path": learning_path,
        },
    )
