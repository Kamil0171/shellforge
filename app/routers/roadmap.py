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
            "skills": [
                "poruszanie się po systemie plików",
                "tworzenie i usuwanie plików oraz katalogów",
                "rozumienie uprawnień",
                "sprawdzanie użytkowników i grup",
                "analiza procesów",
                "praca z plikami tekstowymi",
                "zarządzanie pakietami",
            ],
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
            "skills": [
                "zarządzanie usługami przez systemd",
                "sprawdzanie statusu usług",
                "restartowanie i włączanie usług",
                "czytanie logów systemowych",
                "rozumienie podstawowej struktury systemu",
                "diagnozowanie problemów z usługami",
                "bezpieczna praca z sudo i kontem root",
                "zarządzanie użytkownikami i grupami",
                "analiza zajętości dysku i bezpieczne porządkowanie systemu",
                "planowanie zadań przez cron i systemd timers",
            ],
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
            "status": "Planowane",
            "status_type": "planned",
            "description": (
                "Ten etap skupia się na podstawach komunikacji sieciowej, zdalnym "
                "logowaniu oraz zabezpieczaniu serwera Linux z użyciem standardowych "
                "narzędzi administracyjnych."
            ),
            "skills": [
                "korzystanie z SSH",
                "sprawdzanie portów i połączeń",
                "testowanie dostępności usług",
                "podstawy DNS",
                "podstawy firewalld",
                "podstawy SELinux",
                "bezpieczniejsza konfiguracja dostępu do serwera",
            ],
            "lessons": [
                "SSH i zdalne logowanie",
                "Sieć i diagnostyka: ping, curl, ss i DNS",
                "Firewall: podstawy firewalld",
                "SELinux w praktyce administracyjnej",
            ],
            "cta_label": "Planowane",
            "cta_url": None,
        },
        {
            "level": "Poziom 4",
            "title": "Deployment aplikacji",
            "status": "Planowane",
            "status_type": "planned",
            "description": (
                "Ten etap pokazuje, jak uruchomić aplikację webową na serwerze. "
                "Użytkownik poznaje praktyczny proces przejścia od aplikacji lokalnej "
                "do publicznego wdrożenia dostępnego przez domenę i HTTPS."
            ),
            "skills": [
                "przygotowanie katalogów aplikacji",
                "konfiguracja środowiska Python",
                "uruchamianie aplikacji przez systemd",
                "konfiguracja Nginx jako reverse proxy",
                "podpięcie domeny",
                "konfiguracja HTTPS",
                "aktualizacja aplikacji przez Git",
            ],
            "lessons": [
                "Aplikacja jako usługa systemowa",
                "Nginx jako reverse proxy",
                "Domena i rekordy DNS",
                "HTTPS z Let's Encrypt i Certbot",
                "Aktualizacja aplikacji na serwerze",
            ],
            "cta_label": "Planowane",
            "cta_url": None,
        },
        {
            "level": "Poziom 5",
            "title": "DevOps i automatyzacja",
            "status": "Planowane",
            "status_type": "planned",
            "description": (
                "Po opanowaniu ręcznego deploymentu kolejnym krokiem jest automatyzacja. "
                "Ten etap prowadzi przez konteneryzację, automatyczne testy, CI/CD "
                "i bardziej powtarzalne wdrożenia."
            ),
            "skills": [
                "podstawy kontenerów",
                "Docker albo Podman",
                "przygotowanie Dockerfile",
                "praca z bazą PostgreSQL",
                "GitHub Actions",
                "automatyzacja testów",
                "automatyzacja wdrożeń",
            ],
            "lessons": [
                "Podstawy konteneryzacji",
                "Dockerfile dla aplikacji webowej",
                "PostgreSQL w środowisku aplikacji",
                "CI/CD z GitHub Actions",
            ],
            "cta_label": "Planowane",
            "cta_url": None,
        },
        {
            "level": "Poziom 6",
            "title": "Monitoring i utrzymanie",
            "status": "Planowane",
            "status_type": "planned",
            "description": (
                "Ostatni etap koncentruje się na utrzymaniu aplikacji po wdrożeniu. "
                "Użytkownik poznaje podstawy monitorowania, health checków, logów, "
                "metryk, alertów i procedur operacyjnych."
            ),
            "skills": [
                "health checki",
                "analiza logów aplikacji i serwera",
                "podstawy metryk",
                "monitoring dostępności",
                "Prometheus",
                "Grafana",
                "alerty",
                "backup i odtwarzanie",
            ],
            "lessons": [
                "Health checki i podstawy obserwowalności",
                "Monitoring aplikacji",
                "Metryki i alerty",
                "Backup i procedury odtworzeniowe",
            ],
            "cta_label": "Planowane",
            "cta_url": None,
        },
    ]

    return templates.TemplateResponse(
        request=request,
        name="roadmap.html",
        context={
            "learning_path": learning_path,
        },
    )
