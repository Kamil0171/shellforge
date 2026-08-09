# Wdrożenie ShellForge na VPS

Ten dokument opisuje referencyjne, ręczne wdrożenie aplikacji FastAPI na VPS z Rocky Linux 9. Pokazuje model używany przez ShellForge: Uvicorn uruchamiany jako usługa systemd, Nginx jako reverse proxy oraz HTTPS obsługiwany przez Let's Encrypt i Certbota.

Repozytorium nie zawiera rzeczywistych plików konfiguracyjnych serwera. Poniższe przykłady nie są audytem działającego VPS-a i przed użyciem wymagają dopasowania do konkretnego środowiska.

Wdrożenie jest opisane bez Dockera, Podmana i PostgreSQL, ponieważ technologie te nie są częścią aktualnej implementacji aplikacji.

## Założenia referencyjne

```text
system: Rocky Linux 9
adres publiczny: <SERVER_IP_OR_DOMAIN>
domena: <DOMAIN>
port SSH: <SSH_PORT>
użytkownik aplikacji: <APP_USER>
grupa aplikacji: <APP_GROUP>
katalog repozytorium: /opt/example-app/app
katalog venv: /opt/example-app/venv
plik env: /opt/example-app/.env
serwer aplikacji: Uvicorn
nasłuch aplikacji: 127.0.0.1:8000
reverse proxy: Nginx
publiczny HTTP: 80
publiczny HTTPS: 443
HTTPS: Let's Encrypt / Certbot
endpoint kontrolny: /health
SELinux: Enforcing
zapora sieciowa: firewalld
```

Projekt i konfiguracja Ruff są przygotowane dla Pythona 3.12. Wersję interpretera dostępną na serwerze należy potwierdzić przed utworzeniem środowiska wirtualnego.

## Architektura uruchomienia

```text
Internet
  ↓ HTTPS
Nginx
  ↓ reverse proxy
127.0.0.1:8000
  ↓
Uvicorn
  ↓
FastAPI
```

Nginx jest jedyną warstwą wystawioną publicznie. Uvicorn nasłuchuje na interfejsie lokalnym, a proces aplikacji jest zarządzany przez systemd.

Aktualny kod FastAPI montuje zasoby pod `/static`. Bez rzeczywistej konfiguracji Nginx nie należy zakładać, że serwer proxy obsługuje te pliki bezpośrednio.

Szczegółowy opis komponentów znajduje się w [dokumentacji architektury](architecture.md).

## Dane wrażliwe i konfiguracja środowiska

Plik `.env` powinien znajdować się poza repozytorium i mieć ograniczone uprawnienia. Nie należy umieszczać w dokumentacji ani w Git:

- haseł i tokenów;
- kluczy API;
- prywatnych kluczy SSH;
- zawartości produkcyjnego `.env`;
- produkcyjnej bazy SQLite;
- prywatnego adresu VPS lub niestandardowego portu SSH.

Przykładowe ustawienie uprawnień pozwalające usłudze odczytać plik bez przyznawania prawa zapisu:

```bash
chown root:<APP_GROUP> /opt/example-app/.env
chmod 640 /opt/example-app/.env
```

Użytkownik aplikacyjny musi mieć prawo zapisu do katalogu używanego przez SQLite. Przy domyślnej konfiguracji projektu jest to katalog `app/data` wewnątrz repozytorium aplikacji. Nie należy ręcznie edytować pliku bazy.

## Przygotowanie aplikacji

Kod aplikacji i środowisko wirtualne powinny być własnością dedykowanego użytkownika aplikacyjnego. Przykładowy układ:

```text
/opt/example-app/
├── app/       # checkout repozytorium
├── venv/      # środowisko Python
└── .env       # konfiguracja serwera poza repozytorium
```

Po pobraniu kodu należy utworzyć środowisko wirtualne i zainstalować zależności:

```bash
python3 -m venv /opt/example-app/venv
/opt/example-app/venv/bin/python -m pip install --upgrade pip
/opt/example-app/venv/bin/python -m pip install -r /opt/example-app/app/requirements.txt
```

## Tryb lokalny i produkcyjny

Plik `run.py` służy do lokalnego uruchamiania aplikacji i korzysta z automatycznego przeładowania.

Na VPS-ie aplikację należy uruchamiać bez `reload`, bezpośrednio przez Uvicorna zarządzanego przez systemd:

```bash
/opt/example-app/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Polecenie wymaga katalogu roboczego ustawionego na `/opt/example-app/app`.

## Usługa systemd

Przykładowa jednostka `/etc/systemd/system/example-app.service`:

```ini
[Unit]
Description=Example FastAPI application
After=network.target

[Service]
Type=simple
User=<APP_USER>
Group=<APP_GROUP>
WorkingDirectory=/opt/example-app/app
EnvironmentFile=/opt/example-app/.env
ExecStart=/opt/example-app/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Po utworzeniu lub zmianie jednostki:

```bash
systemctl daemon-reload
systemctl enable --now example-app
systemctl status example-app --no-pager
```

Jeżeli usługa nie startuje, pierwszym źródłem diagnostycznym powinien być dziennik:

```bash
journalctl -u example-app -n 100 --no-pager
```

## Nginx

Nginx przekazuje żądania do aplikacji działającej na `127.0.0.1:8000`. Minimalny przykład serwera HTTP:

```nginx
server {
    listen 80;
    server_name <DOMAIN> www.<DOMAIN>;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Wariant `www` należy dodać tylko wtedy, gdy ma właściwy rekord DNS i ma być obsługiwany przez aplikację oraz certyfikat.

Po każdej zmianie konfiguracji:

```bash
nginx -t
systemctl reload nginx
```

## Firewalld

Publicznie powinny być dostępne usługi HTTP i HTTPS. Port Uvicorna pozostaje związany z `127.0.0.1` i nie wymaga publicznej reguły firewalla.

```bash
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
firewall-cmd --list-all
```

Zmian dotyczących SSH nie należy wykonywać bez potwierdzenia działającego połączenia zapasowego i reguły zgodnej z rzeczywistym portem serwera.

## Domena i DNS

Przykładowe rekordy DNS:

```text
<DOMAIN>        A        <SERVER_IP>
www.<DOMAIN>    A        <SERVER_IP>
```

Rekord `www` jest opcjonalny. Poprawność DNS można sprawdzić przed wystawieniem certyfikatu:

```bash
dig +short <DOMAIN>
dig +short www.<DOMAIN>
```

Odpowiedź powinna wskazywać publiczny adres VPS-a.

## HTTPS i Certbot

Po poprawnym ustawieniu DNS oraz sprawdzeniu konfiguracji Nginx można wygenerować certyfikat:

```bash
certbot --nginx -d <DOMAIN> -d www.<DOMAIN>
```

Jeżeli wariant `www` nie jest używany, należy pominąć go w poleceniu.

Po konfiguracji należy sprawdzić przekierowanie HTTP, odpowiedź HTTPS i endpoint aplikacji:

```bash
curl -I http://<DOMAIN>
curl -I https://<DOMAIN>
curl https://<DOMAIN>/health
```

Test mechanizmu odnawiania:

```bash
certbot renew --dry-run
```

Nazwa timera lub usługi odpowiedzialnej za odnowienie może zależeć od sposobu instalacji Certbota. Dostępne jednostki można znaleźć poleceniem:

```bash
systemctl list-timers --all | grep -i cert
```

## SELinux

Na Rocky Linux SELinux powinien pozostać w trybie `Enforcing`. Gdy Nginx zwraca `502 Bad Gateway`, mimo że backend odpowiada lokalnie, jedną z możliwych przyczyn jest blokada połączenia do Uvicorna.

Sprawdzenie ustawienia:

```bash
getsebool httpd_can_network_connect
```

Jeżeli polityka środowiska wymaga zezwolenia Nginxowi na połączenie z backendem:

```bash
setsebool -P httpd_can_network_connect 1
```

Zmiana powinna wynikać z diagnozy. Nie należy wyłączać SELinux jako sposobu naprawy konfiguracji.

## Aktualizacja aplikacji

Przed aktualizacją należy znać aktualnie wdrożoną rewizję i mieć przygotowaną możliwość powrotu do sprawdzonej wersji. Ogólny przebieg:

```bash
cd /opt/example-app/app
runuser -u <APP_USER> -- git status --short
runuser -u <APP_USER> -- git pull --ff-only origin main
/opt/example-app/venv/bin/python -m pip install -r requirements.txt
systemctl restart example-app
systemctl status example-app --no-pager
curl http://127.0.0.1:8000/health
curl https://<DOMAIN>/health
```

Instalacja zależności jest potrzebna, gdy zmienił się `requirements.txt`. Jeżeli aktualizacja dotyczy wyłącznie dokumentacji, restart aplikacji nie jest konieczny.

Po nieudanym wdrożeniu należy wrócić do wcześniej sprawdzonej rewizji lub backupu zgodnie z przyjętą procedurą, ponownie zainstalować zgodne zależności, zrestartować usługę i wykonać testy zdrowia.

## Diagnostyka po wdrożeniu

Status i logi aplikacji:

```bash
systemctl status example-app --no-pager
journalctl -u example-app -n 100 --no-pager
```

Backend lokalny:

```bash
curl http://127.0.0.1:8000/health
ss -tulpn
```

Nginx:

```bash
nginx -t
systemctl status nginx --no-pager
journalctl -u nginx -n 100 --no-pager
```

Warstwa publiczna:

```bash
curl -I https://<DOMAIN>
curl https://<DOMAIN>/health
```

Kolejność diagnozy powinna ustalić, czy problem występuje w aplikacji, procesie Uvicorna, połączeniu Nginx–backend, DNS czy warstwie HTTPS.

## Lista kontrolna wdrożenia

- kod pochodzi z zatwierdzonej rewizji;
- `.env` znajduje się poza repozytorium i ma ograniczone uprawnienia;
- użytkownik aplikacyjny ma dostęp do wymaganych katalogów;
- Uvicorn działa bez `reload` na `127.0.0.1`;
- jednostka systemd jest aktywna;
- `nginx -t` kończy się powodzeniem;
- firewalld udostępnia HTTP i HTTPS;
- SELinux pozostaje w trybie `Enforcing`;
- DNS wskazuje właściwy serwer;
- certyfikat HTTPS jest poprawny i ma działające odnawianie;
- lokalny i publiczny endpoint `/health` odpowiadają;
- logi aplikacji i Nginx nie zawierają nowych błędów.
