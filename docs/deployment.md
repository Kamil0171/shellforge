# Deployment ShellForge na VPS

Ten dokument opisuje plan pierwszego wdrożenia aplikacji ShellForge na VPS z systemem Rocky Linux 9.

Celem pierwszego deploymentu jest uruchomienie aplikacji w prosty, klasyczny sposób:

- Rocky Linux 9
- Python virtual environment
- Git
- systemd
- Uvicorn
- Nginx jako reverse proxy
- HTTPS
- firewalld
- health check `/health`

Na pierwszym etapie nie używamy jeszcze Dockera, Podmana ani PostgreSQL. Najpierw aplikacja zostanie wdrożona ręcznie, aby dobrze zrozumieć działanie procesu deploymentu.

## Założenia

Docelowo aplikacja będzie działała jako usługa systemowa na VPS.

Przykładowe założenia:

```text
system: Rocky Linux 9
app user: shellforge
app directory: /opt/shellforge
python version: Python 3.12+
app port: 8000
reverse proxy: Nginx
public access: HTTPS
health check: /health