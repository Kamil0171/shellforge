# Dynamic Incident — IncidentDefinition V3 i wielohostowy Virtual Rocky

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

## Virtual Rocky wielu hostów

```text
Polecenie / zapis edytora
  -> parser i allowlista capabilities
  -> głęboka kopia runtime sesji
  -> handler należący do aplikacji
  -> accounting, cele i walidacja
  -> atomowy commit / kontrola rewizji
  -> bezpieczna projekcja publiczna
```

Każdy `VirtualRockyRuntime` przechowuje własny filesystem, cwd, procesy, zasoby, cache jednostek, pakiety, sieć, DNS, SELinux, firewalld i NetworkManager. `SessionRuntimeState` utrzymuje słownik runtime'ów hostów oraz aktywny kontekst. Moduły `rocky/filesystem.py`, `system.py`, `network.py`, `packages.py`, `security.py` i `access.py` pracują wyłącznie na tym modelu. Nie są adapterami systemu hosta.

Obsługiwany jest kontrolowany podzbiór składni:

- filesystem: `pwd`, `cd`, `ls`, `cat`, `head`, `tail`, `grep`, `find`, `stat`, `du`, `mkdir`, `touch`, `cp`, `mv`, `rm`, `rmdir`, `chmod`, `chown`;
- edycja: `nano <plik>` oraz zapis przez `/admin-duty/dynamic/api/file`;
- system: `hostname`, `hostnamectl`, `uname`, `uptime`, `whoami`, `id`, `date`, `ps`, `free`, `df`;
- systemd: `status`, `start`, `stop`, `restart`, `cat`, `enable`, `disable`, `is-active`, `is-enabled`, `list-units`, `daemon-reload`;
- journal: wszystkie wpisy lub filtry `-u`, `-xe`, `-n`, `--since`;
- sieć: `ip addr|link|route`, `ss`, `ping`, `curl`, `getent hosts`, `dig`;
- pakiety: `dnf` i `yum` — lista, informacje, repozytoria, instalacja, usuwanie i aktualizacja; `rpm` — odczyt zainstalowanych pakietów;
- bezpieczeństwo: `getenforce`, `sestatus`, `setenforce`, `restorecon`, odczyt `semanage fcontext -l`, `firewall-cmd`;
- NetworkManager: `nmcli device status`, `connection show|up|down` oraz `connection modify <nazwa> ipv4.dns <adres>`.
- dostęp: `ssh <identyfikator-hosta|hostname>` przełącza aktywny kontekst w bieżącej sesji.

Nie jest to pełny bash ani pełna emulacja Rocky Linux. Parser odrzuca skrypty, potoki, przekierowania i łączenie poleceń. `grep` filtruje tekst literalnie, nie realizuje pełnego regex. Edytor zapisuje istniejące pliki wirtualne, z limitem 32 KiB UTF-8; nowy plik można wcześniej utworzyć przez `touch`. Hosty zachowują oddzielne katalogi robocze i cały swój stan podczas przełączania. Historia wykonanych poleceń należy do sesji i zasila podsumowanie po incydencie.

`ssh` nie korzysta z klienta systemowego, `subprocess`, gniazda ani sieci. Nie uwierzytelnia użytkownika i nie symuluje transportu SSH — jest kontrolowaną nawigacją po zdefiniowanych hostach laboratorium. Nieznany host kończy się bezpiecznym błędem bez zmiany kontekstu.

## IncidentDefinition V3 i zależności

Rdzeń `ServiceDependency` pozostaje mały i typowany: host i usługa źródłowa, host i usługa docelowa, rodzaj zależności, protokół oraz port. Pakiety, konfiguracje i reguły propagacji symptomów są osobnymi modelami. Validator sprawdza referencje, zgodność hostów, porty, adresy IP, cykle grafu, możliwości komend i odtwarza rozwiązanie przez ten sam parser, registry, handler i runtime co sesja gracza.

Poziom MEDIUM zawiera pięć kategorii scenariuszy:

- blokada połączenia do zależności przez firewalld;
- brak pakietu wymaganego przez usługę;
- nieprawidłowy kontekst SELinux;
- błędna konfiguracja DNS zarządzana przez NetworkManager;
- niezgodność zewnętrznej reguły firewalla dla portu usługi.

Scenariusze używają trzech lub czterech hostów i kilku usług. Awaria zależności może pozostawić proces usługi w stanie `running`, a jednocześnie oznaczyć publiczne zdrowie usługi jako `unhealthy` oraz propagować błąd do endpointu. Monitoring i publiczna topologia pokazują tylko dozwolone węzły, zdrowie oraz jawne krawędzie zależności.

## Realistyczne naprawy

Diagnostyka zaczyna się od `systemctl status`, `journalctl -u`, `systemctl cat` i plików aplikacji. Wirtualny `/opt/<aplikacja>/README.md` zawiera wymagania uruchomieniowe, aby rozwiązanie można było ustalić bez ukrytej definicji.

- Błędny ExecStart: edycja jednostki przez `nano`, poprawienie ścieżki, zapis, `systemctl daemon-reload`, restart.
- Brak zmiennej: edycja `Environment` w jednostce, zapis, przeładowanie definicji, restart.
- Odmowa wykonania: `ls -l` / `stat`, zwykłe `chmod`, w razie potrzeby `chown`, restart.
- Zatrzymana usługa: diagnostyka i zwykłe `systemctl start` / `restart`.

Zapis jednostki zmienia plik, ale nie załadowany cache. Dopiero `daemon-reload` aktualizuje definicje używane przez restart. Restart sprawdza wirtualny executable, uprawnienia, wymagane środowisko, pakiety i SELinux; aktualizuje procesy, logi i zasób.

Usunięto sztuczne `systemctl set-exec-start`, `env inspect`, `env restore` i `chmod restore`. Rozwiązania generatora i validator wykonują normalne polecenia oraz ten sam bezpieczny zapis pliku co UI. Nie ma uprzywilejowanego skrótu naprawy.

DNF i YUM delegują do tego samego handlera i `PackageManagerState`. Instalacja nginx tworzy wirtualny executable, jednostkę i usługę; RPM widzi katalog pakietów konkretnego hosta. Brak pobierania pakietów. `curl` odpowiada na podstawie usług, zależności, portów, połączeń i firewalla; DNS jest tabelą runtime hosta. Firewalld ma osobny stan runtime/permanent oraz reload. NetworkManager aktualizuje interfejsy, serwery DNS i dostępność tras. Jest to kontrolowana symulacja wielu maszyn, a nie pełny emulator sieci lub dystrybucji.

## Bezpieczeństwo i spójność

W ścieżce poleceń nie ma `subprocess`, `os.system`, `shell=True`, `eval`, `exec`, odczytu hostowego filesystemu ani rzeczywistych klientów sieciowych. Zaufany loader mapy odczytuje plik repozytorium podczas inicjalizacji; nie przyjmuje ścieżki od gracza. HTTP przeglądarki do aplikacji i ładowanie bibliotek strony nie są ruchem wirtualnych poleceń.

Błędna operacja nie pozostawia częściowej mutacji świata. Obsłużony błąd może naliczyć komendę i jej koszt zgodnie z regułami sesji. Zapis używa kontroli rewizji, a sesje mają niezależne kopie danych. Testy blokują funkcje systemowe, plikowe i sieciowe podczas reprezentatywnych poleceń oraz zapisu edytora.

Architektura przygotowuje przyszły generator AI zwracający wyłącznie ścisły draft danych. `IncidentGenerationRequest`, `GeneratedIncidentDraft`, asynchroniczny protokół providera, fake provider i katalog możliwości prowadzą do tego samego validatora strukturalnego, semantycznego i replay co generator deterministyczny. Nie ma integracji Gemma, klucza, klienta HTTP, kont, generowania kodu ani shella. Sesje pozostają w pamięci procesu, z TTL; nie przeżywają restartu aplikacji.

Po ukończeniu wymaganych celów API może ujawnić raport po incydencie: przyczynę źródłową, dotknięte usługi, odkryte kamienie milowe, skuteczne działania naprawcze, końcowy stan infrastruktury, historię komend, liczbę podpowiedzi i wynik. Raport nie jest dostępny przed ukończeniem misji.

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
