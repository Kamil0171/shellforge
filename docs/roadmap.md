# Roadmapa projektu ShellForge

ShellForge jest edukacyjną aplikacją webową do praktycznej nauki Linuxa, administracji systemami i podstaw DevOps.

Projekt rozwijany jest etapami, bez overengineeringu. Najpierw powstaje proste MVP, a później kolejne funkcje związane z bazą danych, deploymentem, konteneryzacją, CI/CD i monitoringiem.

## Etap 1 — MVP lokalnie

Cel: uruchomić lokalną aplikację edukacyjną z podstawowymi lekcjami i quizami.

Zakres:

- FastAPI
- Jinja2
- Bootstrap
- SQLite
- SQLModel
- prosta strona główna
- lista lekcji
- widok lekcji
- prosty quiz
- podstawowe testy pytest

Pierwszy milestone:

- działająca strona główna
- jedna lekcja
- jeden quiz
- zapis danych w SQLite

## Etap 2 — Baza danych i treści edukacyjne

Cel: przenieść lekcje i quizy z tymczasowych struktur danych do SQLite.

Zakres:

- modele `Module`, `Lesson`, `QuizQuestion`, `QuizAnswer`
- seed danych
- podstawowa obsługa bazy
- testy modeli i tras
- pierwsze lekcje Linux

## Etap 3 — Deployment na Rocky Linux 9 VPS

Cel: uruchomić aplikację na serwerze VPS jako usługę.

Zakres:

- SSH
- użytkownik deploy
- Python virtualenv
- systemd service
- Nginx reverse proxy
- firewalld
- domena
- HTTPS przez Certbot

## Etap 4 — Docker/Podman

Cel: uruchomić ShellForge w kontenerze.

Zakres:

- Dockerfile
- docker-compose albo podman-compose
- wolumeny
- sieci kontenerowe
- podstawy image build
- różnice Docker vs Podman

## Etap 5 — CI/CD

Cel: zautomatyzować testy i deployment.

Zakres:

- GitHub Actions
- uruchamianie testów
- linting
- automatyczny deployment na VPS

## Etap 6 — Monitoring

Cel: nauczyć się podstaw obserwowalności aplikacji i systemu.

Zakres:

- logi aplikacji
- logi systemd
- Prometheus
- Grafana
- Loki
- alerty

## Etap 7 — Funkcje zaawansowane

Cel: rozbudować ShellForge o praktyczne środowisko ćwiczeń.

Zakres:

- symulator terminala
- WebSockety
- sandboxy Linux
- izolowane kontenery
- zadania praktyczne sprawdzane automatycznie