# Dynamic Incident — World Engine V2 i Virtual Rocky V2

## Granice odpowiedzialności

Backend jest źródłem prawdy dla definicji, sesji, zasobów, celów, punktacji i podpowiedzi. Frontend steruje prezentacją, ruchem, kamerą i odkrywaniem mapy. Publiczne DTO nie zawiera filesystemu, rozwiązania, ukrytych atrybutów ani przyszłych podpowiedzi. `revealed_hints` jest prefiksem faktycznie odkrytym przez daną sesję.

## World Engine V2

- `components/maps/modern_noc.json` — jedna kompozycja Modern NOC, pięć sektorów i 34 obiekty; geometria, warianty, kolizje i interakcje.
- `definition.py` — walidowany `MapDefinition` / `PublicGameMap`: wymiary, spawn, sektory, obiekty i interakcje; sprawdza unikalność identyfikatorów, granice i dostępność interakcji.
- `loader.py` — odczyt zaufanego pliku mapy przy inicjalizacji, nie z polecenia użytkownika.
- `world-core.js` — MapLoader, RuntimeBridge, CameraController, DiscoveryState i wybór najbliższej interakcji.
- `world-renderers.js` — proceduralne tekstury podłóg, ścian, drzwi, biurek, racków, tablic i dekoracji.
- `world-systems.js` — animacja gracza, wspólny zegar otoczenia, światło, gradientowa maska odkrywania i interakcje.
- `game.js` — składanie sceny Phaser, fizyka, kolizje, kamera i lifecycle.
- `scenario.js` — API, HUD, overlaye, wsparcie, desktop gate i zakończenie.
- `terminal.js` — komendy, historia, prompt, focus, Escape i edytor; `clear` / `cls` działają lokalnie.
- `index.js` — lobby i start sesji.

Geometria nie zależy od identyfikatora incydentu. Powiązania racków i monitoringu pochodzą z publicznej projekcji backendu. Sześć wariantów racków, cztery materiały podłogi, szklane przegrody i drzwi rozdzielają strefę operacyjną, monitoring, serwerownię, wsparcie i wejście. Triage jest stanowiskiem wizualnym, bez osobnej interakcji.

Kamera używa płynnego śledzenia i granic świata. Kolizje pochodzą z tej samej definicji co obiekty. Depth wynika z położenia podstawy obiektu; gracz ma cień, cztery kierunki, idle i chód. Odkrywanie zachowuje odsłoniętą maskę podczas eksploracji sceny. Po przeładowaniu strony maska i pozycja zaczynają się od nowa — nie są zapisywane w sesji backendowej.

Format oddziela dane od renderowania i pozwala później napisać adapter Tiled. Nie ma obecnie importera TMX ani natywnego JSON Tiled. Oświetlenie jest stylizowanym efektem Canvas, nie fizycznym modelem światła. Animacje racków i monitorów korzystają ze wspólnej aktualizacji, bez timera dla każdego obiektu.

## Virtual Rocky V2

```text
Polecenie / zapis edytora
  -> parser i allowlista capabilities
  -> głęboka kopia runtime sesji
  -> handler należący do aplikacji
  -> accounting, cele i walidacja
  -> atomowy commit / kontrola rewizji
  -> bezpieczna projekcja publiczna
```

`VirtualRockyRuntime` przechowuje filesystem, cwd, procesy, zasoby, cache jednostek, pakiety, sieć, DNS, SELinux i firewalld. Moduły `rocky/filesystem.py`, `system.py`, `network.py`, `packages.py` i `security.py` współdzielą ten model. Nie są adapterami systemu hosta.

Obsługiwany jest kontrolowany podzbiór składni:

- filesystem: `pwd`, `cd`, `ls`, `cat`, `head`, `tail`, `grep`, `find`, `stat`, `du`, `mkdir`, `touch`, `cp`, `mv`, `rm`, `rmdir`, `chmod`, `chown`;
- edycja: `nano <plik>` oraz zapis przez `/admin-duty/dynamic/api/file`;
- system: `hostname`, `hostnamectl`, `uname`, `uptime`, `whoami`, `id`, `date`, `ps`, `free`, `df`;
- systemd: `status`, `start`, `stop`, `restart`, `cat`, `enable`, `disable`, `is-active`, `is-enabled`, `list-units`, `daemon-reload`;
- journal: wszystkie wpisy lub filtry `-u`, `-xe`, `-n`, `--since`;
- sieć: `ip addr|link|route`, `ss`, `ping`, `curl`, `getent hosts`, `dig`;
- pakiety: `dnf` i `yum` — lista, informacje, repozytoria, instalacja, usuwanie i aktualizacja; `rpm` — odczyt zainstalowanych pakietów;
- bezpieczeństwo: `getenforce`, `sestatus`, `setenforce`, `restorecon`, odczyt `semanage fcontext -l`, `firewall-cmd`;
- NetworkManager: `nmcli device status`, `connection show|up|down`.

Nie jest to pełny bash ani pełna emulacja Rocky Linux. Parser odrzuca skrypty, potoki, przekierowania i łączenie poleceń. `grep` filtruje tekst literalnie, nie realizuje pełnego regex. Edytor zapisuje istniejące pliki wirtualne, z limitem 32 KiB UTF-8; nowy plik można wcześniej utworzyć przez `touch`. Historia terminala jest lokalna dla strony, cwd należy do sesji.

## Realistyczne naprawy

Diagnostyka zaczyna się od `systemctl status`, `journalctl -u`, `systemctl cat` i plików aplikacji. Wirtualny `/opt/<aplikacja>/README.md` zawiera wymagania uruchomieniowe, aby rozwiązanie można było ustalić bez ukrytej definicji.

- Błędny ExecStart: edycja jednostki przez `nano`, poprawienie ścieżki, zapis, `systemctl daemon-reload`, restart.
- Brak zmiennej: edycja `Environment` w jednostce, zapis, przeładowanie definicji, restart.
- Odmowa wykonania: `ls -l` / `stat`, zwykłe `chmod`, w razie potrzeby `chown`, restart.
- Zatrzymana usługa: diagnostyka i zwykłe `systemctl start` / `restart`.

Zapis jednostki zmienia plik, ale nie załadowany cache. Dopiero `daemon-reload` aktualizuje definicje używane przez restart. Restart sprawdza wirtualny executable, uprawnienia, wymagane środowisko, pakiety i SELinux; aktualizuje procesy, logi i zasób.

Usunięto sztuczne `systemctl set-exec-start`, `env inspect`, `env restore` i `chmod restore`. Rozwiązania generatora i validator wykonują normalne polecenia oraz ten sam bezpieczny zapis pliku co UI. Nie ma uprzywilejowanego skrótu naprawy.

DNF i YUM delegują do tego samego handlera i `PackageManagerState`. Instalacja nginx tworzy wirtualny executable, jednostkę i usługę; RPM widzi ten sam katalog pakietów. Brak pobierania pakietów. `curl` odpowiada na podstawie usług, portów, połączeń i firewalla; DNS jest tabelą runtime. Firewalld ma osobny stan runtime/permanent oraz reload. NetworkManager aktualizuje interfejsy i dostępność tras. Jest to ograniczona symulacja jednej maszyny, nie pełny emulator sieci wielu hostów.

## Bezpieczeństwo i spójność

W ścieżce poleceń nie ma `subprocess`, `os.system`, `shell=True`, `eval`, `exec`, odczytu hostowego filesystemu ani rzeczywistych klientów sieciowych. Zaufany loader mapy odczytuje plik repozytorium podczas inicjalizacji; nie przyjmuje ścieżki od gracza. HTTP przeglądarki do aplikacji i ładowanie bibliotek strony nie są ruchem wirtualnych poleceń.

Błędna operacja nie pozostawia częściowej mutacji świata. Obsłużony błąd może naliczyć komendę i jej koszt zgodnie z regułami sesji. Zapis używa kontroli rewizji, a sesje mają niezależne kopie danych. Testy blokują funkcje systemowe, plikowe i sieciowe podczas reprezentatywnych poleceń oraz zapisu edytora.

Architektura umożliwia przyszły generator AI zwracający dane `IncidentDefinition`, poddane walidacji i odtworzeniu rozwiązania. Nie wdraża AI, kont, generowania kodu ani shella. Sesje pozostają w pamięci procesu, z TTL; nie przeżywają restartu aplikacji.

## Interfejs i wsparcie

Workspace mieści się w `100dvh` pod navbarem. Overlaye mają wewnętrzne przewijanie treści. Desktop gate blokuje małe viewporty i urządzenia dotykowe zgodnie z kontrolą klienta. Nie ma joysticka. Zmiana rozmiaru nie kończy sesji.

Centrum wsparcia udostępnia runbooki, wskazówki operacyjne i płatne podpowiedzi. Podpowiedzi są pobierane pojedynczo, atomowo odejmują punkty i ujawniają tylko dozwolony prefiks. Monitoring i racki korzystają wyłącznie z publicznych danych. Po ukończeniu można przeglądać świat, ale terminal nie pozwala dalej zmieniać incydentu.

## Quality workflow i cleanup

```powershell
python scripts/check.py
python scripts/smoke_test.py --base-url http://127.0.0.1:8000
pre-commit run --all-files
```

`check.py` uruchamia Ruff, pełny pytest, kontrolę wszystkich Dynamic Incident JS, testy World Engine w Node i `git diff --check`. Smoke test wymaga działającej aplikacji i sprawdza publiczne strony oraz sesję API. `requirements-dev.txt` i `.pre-commit-config.yaml` pozostają aktywną częścią workflow opisanego w README; GitHub Actions uruchamia testy i JS checks.

Dedykowany stos INC-001 został usunięty: commands/engine/scenarios, osobny template i JS, endpointy, testy tej funkcji oraz nieużywane style. Wspólne lobby, jego router, template, CSS i skrypt nawigacji pozostają używane. `virtual_shell.py` został zastąpiony modułami `rocky/`. Dokumentacja utrzymuje Mermaid zamiast nieaktualnego PNG architektury. Testy Virtual Rocky zachowują historyczną nazwę pliku, ponieważ sprawdzają aktywne zachowanie, nie usunięty adapter.
