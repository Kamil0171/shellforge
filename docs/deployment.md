# Deployment ShellForge na VPS

Ten dokument opisuje przykładowy ręczny deployment aplikacji ShellForge na VPS z systemem Rocky Linux 9.

Deployment został wykonany klasycznie, bez Dockera, Podmana i PostgreSQL. Celem jest pokazanie ogólnego procesu wdrożenia aplikacji FastAPI z wykorzystaniem użytkownika aplikacyjnego, Python virtual environment, systemd, Nginx reverse proxy, firewalld oraz SELinux.

## Założenia deploymentu

```text
system: Rocky Linux 9
provider: VPS provider
public address: <SERVER_IP_OR_DOMAIN>
SSH port: <SSH_PORT>
app user: shellforge
app directory: /opt/shellforge/app
venv directory: /opt/shellforge/venv
env file: /opt/shellforge/.env
Python: 3.12
app server: Uvicorn
app bind: 127.0.0.1:8000
reverse proxy: Nginx
public HTTP: 80
health check: /health
SELinux: Enforcing
firewall: firewalld
```

## Ogólny przebieg deploymentu

Pierwszy deployment ShellForge zakłada ręczne przygotowanie VPS-a, instalację wymaganych pakietów, utworzenie osobnego użytkownika systemowego dla aplikacji oraz pobranie kodu z repozytorium Git.

Aplikacja jest uruchamiana przez Uvicorn wewnętrznie na adresie `127.0.0.1:8000`, a publiczny ruch HTTP jest obsługiwany przez Nginx działający jako reverse proxy.

Plik środowiskowy `.env` znajduje się poza repozytorium, ponieważ może zawierać konfigurację specyficzną dla danego serwera.

## Architektura uruchomienia

```text
Internet
  ↓
Nginx
  ↓
127.0.0.1:8000
  ↓
Uvicorn
  ↓
FastAPI / ShellForge
```

## Usługa systemd

Aplikacja działa jako usługa systemowa zarządzana przez `systemd`.

Przykładowa ścieżka usługi:

```text
/etc/systemd/system/shellforge.service
```

Usługa korzysta z osobnego użytkownika aplikacyjnego, katalogu aplikacji oraz pliku środowiskowego.

## Nginx

Nginx pełni rolę reverse proxy. Publicznie dostępny jest port HTTP, natomiast aplikacja FastAPI nie jest wystawiona bezpośrednio na zewnątrz.

Docelowo po podpięciu domeny należy skonfigurować HTTPS.

## SELinux

Na Rocky Linux SELinux działa w trybie `Enforcing`. Przy konfiguracji Nginx jako reverse proxy może być wymagane dopuszczenie połączeń Nginx do backendu aplikacji.

## Aktualizacja aplikacji

Po zmergowaniu zmian do brancha `main` aktualizacja aplikacji na VPS polega na pobraniu najnowszej wersji kodu z repozytorium oraz restarcie usługi aplikacji.

Jeżeli zmieniana była wyłącznie dokumentacja, restart aplikacji nie jest konieczny.

## Następne kroki

Do wykonania w kolejnych etapach:

- podpięcie domeny,
- konfiguracja HTTPS,
- certyfikat Let's Encrypt,
- logowanie SSH za pomocą klucza,
- rozważenie fail2ban,
- dodanie favicony,
- konteneryzacja przez Docker albo Podman,
- CI/CD,
- monitoring.
