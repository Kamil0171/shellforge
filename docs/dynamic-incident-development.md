# Dynamic Incident — notatki developerskie

## Podział odpowiedzialności

Backend pozostaje źródłem prawdy dla sesji, mapy, stanu zasobów, punktacji i podpowiedzi. `MapSnapshot` jest modelem wewnętrznym generatora. Klient otrzymuje niezależny, allowlistowany `PublicGameMap`, który zawiera wyłącznie renderowalne wymiary, geometrię kolizji, obiekty dekoracyjne i bezpieczne interakcje.

Lista `revealed_hints` jest zawsze dokładnym prefiksem `definition.hints[:state.hints_used]`. Przyszłe podpowiedzi nie są serializowane do publicznego DTO.

Frontend jest podzielony na:

- `game.js` — scena Phaser, renderer mapy, ruch, kolizje, kamera i interakcje;
- `terminal.js` — focus, Enter, historia, ESC i cykl requestu terminala; `clear`/`cls` są obsługiwane lokalnie i nie mutują sesji;
- `scenario.js` — API, publiczne projekcje, HUD, overlaye, desktop gate i lifecycle sesji;
- `index.js` — lobby i generowanie nowej sesji.

## Virtual Rocky Linux v1

Terminal Dynamic Incident nie uruchamia poleceń systemu operacyjnego. Każde polecenie przechodzi przez trzy kontrolowane warstwy:

```text
Shell Parser -> Command Registry -> Virtual Rocky Runtime
```

Parser rozpoznaje tylko wspieraną składnię, registry mapuje capability na kod należący do ShellForge, a runtime przechowuje odrębny stan każdej sesji. Definicja incydentu może wskazać wymagane capabilities i dane wejściowe, ale nie może dostarczyć handlera ani kodu wykonywalnego. Dzięki temu przyszły generator AI może tworzyć walidowany `IncidentDefinition`, lecz nie otrzymuje dostępu do shella ani hosta.

`VirtualRockyRuntime` zawiera wirtualną nazwę hosta, użytkownika, katalog domowy i kontrolowany filesystem. Stan sesji przechowuje bieżący katalog roboczy. Obsługiwane są ścieżki absolutne i względne, `.`, `..` oraz `~`; wejście do `/root` zwraca błąd uprawnień. Bazowe drzewo obejmuje `/etc`, `/var`, `/home`, `/opt`, `/srv` i `/tmp`, a generator dodaje pliki jednostek systemd, logi oraz katalogi aplikacji wynikające z definicji incydentu.

Pierwszy katalog realnych składniowo poleceń obejmuje:

- pliki i nawigację: `pwd`, `cd`, `ls`, `ls -l`, `ls -la`, `cat`, `head`, `tail`, `grep`, `stat`;
- system: `hostname`, `uname`, `uptime`, `whoami`, `id`;
- systemd i logi: `systemctl status|start|stop|restart|cat`, `journalctl -u`, `journalctl -xe`;
- zasoby: `free -h`, `df -h`;
- sieć: `ip addr`, `ip route`, `ss -lntp`.

Outputy są deterministycznie składane ze stanu runtime i stylizowane na Rocky Linux/RHEL. `clear` pozostaje lokalnym poleceniem UI bez kosztu. Pozostałe rozpoznane polecenia, w tym błędy ścieżek i niepoprawna składnia, przechodzą przez istniejący command accounting; nieobsługiwane dane nie zmieniają świata. Prompt zwracany przez API odzwierciedla cwd, na przykład `operator@incident:~$` i `operator@incident:/etc/systemd/system$`.

Warstwa wykonawcza nie korzysta z `subprocess`, `shell=True`, `os.system`, hostowego filesystemu ani prawdziwych `systemctl`, `journalctl` czy `chmod`. Dane wyjściowe pochodzą wyłącznie z kontrolowanego runtime sesji.

Diagnostyka korzysta już z naturalnych poleceń. Kontrolowane naprawy pozostają tymczasowo dostępne dla istniejących fault flows: `systemctl set-exec-start`, `env inspect`, `env restore` i `chmod restore`. Powinny być zastępowane przez przyszłe, bezpieczne mechanizmy edycji wirtualnej konfiguracji.

## Modern NOC i Centrum wsparcia

Modern NOC jest pierwszą mapą produkcyjną. Jej role przestrzenne rozdzielają monitoring symptomów, racki infrastruktury, stanowisko terminalowe i Support Bay. Publiczny katalog map pozwala później dodawać kolejne kompozycje niezależne od konkretnego faultu.

Centrum wsparcia udostępnia kontrolowany katalog runbooków, bezpłatne wskazówki operacyjne oraz atomowy Hint Service. Runbooki są dobierane po bezpiecznych tagach scenariusza i uczą procesu diagnostycznego bez ujawniania rozwiązania. Podpowiedzi pobierane są pojedynczo z backendu, kosztują punkty, a klient widzi wyłącznie ujawniony prefiks.

Nowa mapa wymaga komponentu w katalogu map oraz publicznej kompozycji renderowalnych obiektów. Scena nie zawiera identyfikatorów konkretnego incydentu.

Workspace sesji zajmuje pozostałą część `100dvh` pod navbarem i blokuje scroll dokumentu. Briefing oraz podpowiedzi korzystają z wewnętrznego drawera, a terminal i szczegóły węzłów z overlayów. Przejście lobby → sesja używa `location.replace()`, dzięki czemu Back wraca do menu trybów zamiast do ekranu generowania.

## Walidacja

Pełny lokalny gate:

```powershell
python scripts/check.py
```

Kontrola składni automatycznie wykrywa wszystkie pliki `*.js` w `app/static/admin_duty/dynamic/`. Smoke test uruchomionej aplikacji sprawdza start sesji, publiczną projekcję Modern NOC, Support Bay, podstawowe polecenia Virtual Rocky i zakończenie:

```powershell
python scripts/smoke_test.py --base-url http://127.0.0.1:8000
```

## Audit legacy INC-001

INC-001 nadal działa i w tym milestone nie jest usuwany. Po podjęciu osobnej decyzji o wyłączeniu klasycznego scenariusza dokładna lista plików do usunięcia to:

- `app/admin_duty/scenarios/incident_001.py`;
- `app/admin_duty/scenarios/__init__.py`;
- `app/admin_duty/commands.py`;
- `app/admin_duty/engine.py`;
- `app/templates/admin_duty/scenario.html`;
- `app/static/admin_duty/js/scenario.js`.

Usunięcie wymaga też punktowych zmian, ale nie kasowania całych plików: oczyszczenia klasycznych endpointów i importów w `app/admin_duty/router.py`, usunięcia testów INC-001 z `tests/test_basic.py`, aktualizacji karty w `app/templates/admin_duty/index.html`, wzmianki na stronie głównej oraz dokumentacji. `app/static/admin_duty/css/admin_duty.css` i `app/static/admin_duty/js/admin_duty.js` pozostają potrzebne lobby Symulatora.
