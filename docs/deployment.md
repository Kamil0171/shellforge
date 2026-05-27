# Deployment ShellForge na VPS

Ten dokument opisuje przykładowy ręczny deployment aplikacji ShellForge na VPS z systemem Rocky Linux 9.

Deployment został wykonany klasycznie, bez Dockera, Podmana i PostgreSQL. Celem jest pokazanie ogólnego procesu wdrożenia aplikacji FastAPI z wykorzystaniem użytkownika aplikacyjnego, Python virtual environment, systemd, Nginx reverse proxy, firewalld, SELinux, domeny oraz HTTPS.

## Założenia deploymentu

```text
system: Rocky Linux 9
provider: VPS provider
public address: <SERVER_IP_OR_DOMAIN>
domain: <DOMAIN>
SSH port: <SSH_PORT>
app user: <APP_USER>
app directory: /opt/<app-name>/app
venv directory: /opt/<app-name>/venv
env file: /opt/<app-name>/.env
Python: 3.12
app server: Uvicorn
app bind: 127.0.0.1:8000
reverse proxy: Nginx
public HTTP: 80
public HTTPS: 443
HTTPS: Let's Encrypt / Certbot
health check: /health
SELinux: Enforcing
firewall: firewalld
```

## Ogólny przebieg deploymentu

Pierwszy deployment aplikacji zakłada ręczne przygotowanie VPS-a, instalację wymaganych pakietów, utworzenie osobnego użytkownika systemowego dla aplikacji oraz pobranie kodu z repozytorium Git.

Aplikacja jest uruchamiana przez Uvicorn wewnętrznie na adresie `127.0.0.1:8000`, a publiczny ruch HTTP/HTTPS jest obsługiwany przez Nginx działający jako reverse proxy.

Plik środowiskowy `.env` znajduje się poza repozytorium, ponieważ może zawierać konfigurację specyficzną dla danego serwera.

## Architektura uruchomienia

```text
Internet
  ↓
Domena
  ↓
Nginx
  ↓
127.0.0.1:8000
  ↓
Uvicorn
  ↓
FastAPI / aplikacja
```

## Tryb lokalny i produkcyjny

Plik `run.py` służy wyłącznie do lokalnego uruchamiania aplikacji w środowisku developerskim.

W środowisku lokalnym dopuszczalne jest użycie trybu automatycznego przeładowania aplikacji, ponieważ ułatwia on pracę nad kodem i szybkie sprawdzanie zmian.

Na VPS-ie aplikacja nie powinna być uruchamiana przez `run.py`, jeżeli używa on trybu `reload=True`.

W środowisku produkcyjnym aplikacja powinna być uruchamiana przez `systemd` oraz Uvicorna bez trybu `reload`.

Przykładowa komenda produkcyjna:

```bash
/opt/<app-name>/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Uvicorn powinien nasłuchiwać lokalnie na `127.0.0.1`, a publiczny ruch HTTP/HTTPS powinien przechodzić przez Nginx jako reverse proxy.

## Usługa systemd

Aplikacja działa jako usługa systemowa zarządzana przez `systemd`.

Przykładowa ścieżka usługi:

```text
/etc/systemd/system/<app-name>.service
```

Usługa korzysta z osobnego użytkownika aplikacyjnego, katalogu aplikacji oraz pliku środowiskowego.

## Nginx

Nginx pełni rolę reverse proxy. Publicznie dostępny jest ruch HTTP/HTTPS, natomiast aplikacja FastAPI nie jest wystawiona bezpośrednio na zewnątrz.

Przykładowa ścieżka konfiguracji Nginx dla aplikacji:

```text
/etc/nginx/conf.d/<app-name>.conf
```

W konfiguracji Nginx należy ustawić domenę główną oraz wariant `www`.

Przykład:

```nginx
server_name <DOMAIN> www.<DOMAIN>;
```

Po każdej zmianie konfiguracji Nginx należy sprawdzić poprawność konfiguracji i przeładować usługę:

```bash
nginx -t
systemctl reload nginx
```

## Domena i DNS

Domena powinna wskazywać na VPS przez rekordy DNS typu `A`.

Przykładowe rekordy:

```text
<DOMAIN>        A        <SERVER_IP>
www.<DOMAIN>    A        <SERVER_IP>
```

Po zmianie rekordów DNS należy poczekać na propagację. Może to potrwać od kilku minut do kilkunastu godzin, w zależności od konfiguracji DNS.

Poprawność rekordów DNS można sprawdzić lokalnie:

```powershell
nslookup <DOMAIN>
nslookup www.<DOMAIN>
```

Oczekiwany wynik to adres IP serwera VPS.

## HTTPS

HTTPS można skonfigurować za pomocą Let's Encrypt oraz Certbota.

Po poprawnym ustawieniu DNS oraz konfiguracji Nginx certyfikat można wygenerować dla domeny głównej i wariantu `www`.

Przykład:

```bash
certbot --nginx -d <DOMAIN> -d www.<DOMAIN>
```

Po poprawnej konfiguracji oczekiwany efekt jest następujący:

```text
http://<DOMAIN>       → przekierowanie na HTTPS
https://<DOMAIN>      → aplikacja działa poprawnie
https://www.<DOMAIN>  → aplikacja działa poprawnie
```

Poprawność działania HTTPS można sprawdzić:

```bash
curl -I http://<DOMAIN>
curl https://<DOMAIN>/health
curl https://www.<DOMAIN>/health
```

Endpoint `/health` powinien zwrócić odpowiedź aplikacji.

## Odnawianie certyfikatu

Certyfikat Let's Encrypt jest ważny czasowo, dlatego musi być odnawiany automatycznie.

Poprawność odnawiania można sprawdzić poleceniem:

```bash
certbot renew --dry-run
```

Jeżeli system używa timera `systemd`, można sprawdzić jego status:

```bash
systemctl status certbot-renew.timer --no-pager
systemctl list-timers --all | grep -i cert
```

Timer powinien być aktywny i mieć zaplanowane kolejne uruchomienie.

## SELinux

Na Rocky Linux SELinux działa w trybie `Enforcing`. Przy konfiguracji Nginx jako reverse proxy może być wymagane dopuszczenie połączeń Nginx do backendu aplikacji.

Jeżeli Nginx zwraca błąd `502 Bad Gateway`, mimo że aplikacja działa poprawnie na `127.0.0.1:8000`, jedną z możliwych przyczyn jest blokada SELinux.

W takim przypadku należy sprawdzić ustawienie:

```bash
getsebool httpd_can_network_connect
```

Włączenie połączeń Nginx do backendu aplikacji:

```bash
setsebool -P httpd_can_network_connect 1
```

## Aktualizacja aplikacji

Po zmergowaniu zmian do brancha `main` aktualizacja aplikacji na VPS polega na pobraniu najnowszej wersji kodu z repozytorium oraz restarcie usługi aplikacji.

Ogólny schemat:

```bash
cd /opt/<app-name>/app
runuser -u <APP_USER> -- git pull origin main
systemctl restart <app-name>
systemctl status <app-name> --no-pager
curl https://<DOMAIN>/health
```

Jeżeli zmieniana była wyłącznie dokumentacja, restart aplikacji nie jest konieczny.

## Podstawowe komendy kontrolne

Status aplikacji:

```bash
systemctl status <app-name> --no-pager
```

Status Nginx:

```bash
systemctl status nginx --no-pager
```

Sprawdzenie konfiguracji Nginx:

```bash
nginx -t
```

Sprawdzenie firewalla:

```bash
firewall-cmd --list-all
```

Sprawdzenie nasłuchujących portów:

```bash
ss -tulpn
```

Sprawdzenie endpointu aplikacji:

```bash
curl https://<DOMAIN>/health
```

## Następne kroki

Do wykonania w kolejnych etapach:

- logowanie SSH za pomocą klucza,
- rozważenie fail2ban,
- konteneryzacja przez Docker albo Podman,
- CI/CD,
- monitoring.