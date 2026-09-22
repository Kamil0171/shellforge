POSTGRES_PERSISTENCE = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "Trwałość danych, migracje i podstawowy backup PostgreSQL",
        "level": "Średnio zaawansowany",
        "duration": "65 min",
        "description": "Odróżnisz volume od kopii zapasowej, sprawdzisz schemat i zapiszesz podstawowy zrzut bazy.",
        "theory": (
            "Nazwany volume utrzymuje pliki PostgreSQL przy wymianie kontenera, lecz nie jest kopią "
            "zapasową. Błąd operatora, uszkodzenie danych albo utrata hosta mogą dotknąć także volume. "
            "<code>pg_dump</code> tworzy logiczny zrzut wybranej bazy; format <code>-Fc</code> pozwala "
            "obejrzeć zawartość przez <code>pg_restore --list</code>. Przekierowanie <code>></code> zapisuje "
            "plik na hoście, z którego uruchomiono polecenie. Zrzut może zawierać dane poufne, więc "
            "potrzebuje ograniczonego dostępu, miejsca na dysku i przechowywania poza repozytorium. "
            "Sam fakt powstania pliku nie dowodzi, że da się go odtworzyć; procedury odtwarzania i DR "
            "należą do kolejnego poziomu. Migracja to kontrolowana, wersjonowana zmiana schematu "
            "związana z wersją aplikacji. Przed wdrożeniem należy wiedzieć, czy zmiana wymaga migracji "
            "i czy stara oraz nowa wersja aplikacji mogą pracować z danym schematem. Skrypt SQL można "
            "wykonać przez <code>psql</code>, ale w realnym projekcie potrzebny jest rejestr zastosowanych "
            "migracji i narzędzie dopasowane do aplikacji. Wykonuj migrację tylko w kontrolowanym "
            "środowisku ćwiczeniowym, po zrobieniu kopii danych."
        ),
        "commands": [
            {"command": "docker volume ls", "description": "Potwierdza obecność nazwanego volume bazy.", "example": "$ docker volume ls"},
            {"command": "docker compose exec app-db psql -U orders -d orders -c '\\dt'", "description": "Wyświetla tabele bieżącej bazy.", "example": "$ docker compose exec app-db psql -U orders -d orders -c '\\dt'"},
            {"command": "mkdir -p ../backups", "description": "Tworzy katalog kopii poza katalogiem repozytorium ćwiczeniowego.", "example": "$ mkdir -p ../backups"},
            {"command": "docker compose exec -T app-db pg_dump -U orders -d orders -Fc > ../backups/orders.backup", "description": "Zapisuje logiczny zrzut bazy na hoście w formacie custom.", "example": "$ docker compose exec -T app-db pg_dump -U orders -d orders -Fc > ../backups/orders.backup"},
            {"command": "test -s ../backups/orders.backup", "description": "Sprawdza, że plik zrzutu istnieje i nie jest pusty.", "example": "$ test -s ../backups/orders.backup"},
            {"command": "docker compose exec -T app-db pg_restore --list < ../backups/orders.backup", "description": "Odczytuje spis obiektów zrzutu bez odtwarzania danych.", "example": "$ docker compose exec -T app-db pg_restore --list < ../backups/orders.backup"},
            {"command": "docker compose exec -T app-db psql -U orders -d orders < migrations/001_create_orders.sql", "description": "Wykonuje przygotowany skrypt zmiany schematu w środowisku ćwiczeniowym.", "example": "$ docker compose exec -T app-db psql -U orders -d orders < migrations/001_create_orders.sql"},
        ],
        "practice_task": (
            "Na ćwiczeniowej bazie <code>orders</code> odczytaj listę tabel. Przygotuj lokalny plik "
            "<code>migrations/001_create_orders.sql</code> z jedną świadomą zmianą schematu i opisz, "
            "jak odnotujesz jej wykonanie. Najpierw utwórz <code>../backups</code> i wykonaj "
            "<code>pg_dump -Fc</code> do tego katalogu, sprawdź rozmiar pliku i spis obiektów. "
            "Dopiero potem uruchom skrypt i "
            "ponownie odczytaj tabele. Nie traktuj tego jako kompletnej procedury odtwarzania."
        ),
        "common_mistakes": [
            "Uznawanie volume za niezależną kopię zapasową.",
            "Commitowanie zrzutu danych do repozytorium.",
            "Wykonywanie migracji bez informacji, która wersja schematu już obowiązuje.",
            "Zakładanie, że niepusty plik gwarantuje możliwość odtworzenia.",
            "Pomijanie kontroli wolnego miejsca przed utworzeniem kopii.",
        ],
        "summary": (
            "Volume utrzymuje dane przy wymianie kontenera, a pg_dump tworzy odrębny logiczny zrzut. "
            "Migracje pozwalają kontrolować zmiany schematu. Sprawdzenie pliku i listy obiektów to "
            "pierwsza kontrola kopii, nie pełny test odtwarzania."
        ),
    },
    "quiz": {
        "title": "Quiz: trwałość danych i podstawowy backup PostgreSQL",
        "description": "Odróżnij persistence, migrację i logiczną kopię bazy.",
        "questions": [
            {"text": "Baza działa na nazwanym volume. Dlaczego nadal potrzebna jest kopia?", "answers": [("a", "Volume może ulec uszkodzeniu lub zostać utracony razem z hostem", True), ("b", "Volume usuwa dane przy każdym restarcie", False), ("c", "pg_dump jest potrzebny do działania DNS", False), ("d", "Bez kopii Compose nie tworzy sieci", False)]},
            {"text": "Co tworzy pg_dump -Fc?", "answers": [("a", "Logiczny zrzut w formacie custom", True), ("b", "Nowy volume Docker", False), ("c", "Gotowy plan DR", False), ("d", "Uruchomiony serwer HTTP", False)]},
            {"text": "Dokąd trafia plik przy > orders.backup?", "answers": [("a", "Na host uruchamiający powłokę", True), ("b", "Zawsze do katalogu danych wewnątrz bazy", False), ("c", "Automatycznie do registry", False), ("d", "Do obrazu orders-api", False)]},
            {"text": "Jak bez odtwarzania podejrzeć zawartość zrzutu custom?", "answers": [("a", "Użyć pg_restore --list", True), ("b", "Użyć docker ps", False), ("c", "Zmienić tag obrazu", False), ("d", "Uruchomić EXPOSE", False)]},
            {"text": "Co opisuje migracja bazy?", "answers": [("a", "Kontrolowaną, wersjonowaną zmianę schematu", True), ("b", "Przeniesienie kontenera do registry", False), ("c", "Wyłącznie restart procesu", False), ("d", "Automatyczne ustawienie portu hosta", False)]},
            {"text": "Czy niepusty orders.backup dowodzi pełnej odtwarzalności?", "answers": [("a", "Nie, potrzebny jest osobny test odtworzenia", True), ("b", "Tak, rozmiar zawsze wystarcza", False), ("c", "Tak, jeśli volume ma nazwę", False), ("d", "Tak, jeśli aplikacja odpowiada HTTP 200", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czy volume jest backupem?", "answer": "Nie, to trwałe miejsce danych w środowisku Dockera."},
        {"question": "Co może uszkodzić dane na volume?", "answer": "Błąd operatora, awaria nośnika lub utrata hosta."},
        {"question": "Do czego służy pg_dump?", "answer": "Tworzy logiczny zrzut bazy PostgreSQL."},
        {"question": "Co oznacza -Fc przy pg_dump?", "answer": "Format custom obsługiwany przez pg_restore."},
        {"question": "Gdzie zapisuje przekierowanie > ../backups/orders.backup?", "answer": "W katalogu kopii na hoście, na którym działa powłoka."},
        {"question": "Po co -T przy compose exec?", "answer": "Wyłącza terminal TTY dla strumieniowego wejścia lub wyjścia."},
        {"question": "Co sprawdza test -s?", "answer": "Czy plik istnieje i ma niezerowy rozmiar."},
        {"question": "Co robi pg_restore --list?", "answer": "Pokazuje spis obiektów w zrzucie custom."},
        {"question": "Czy pg_restore --list odtwarza bazę?", "answer": "Nie, tylko czyta spis zrzutu."},
        {"question": "Czy niepusty zrzut dowodzi poprawnego odtworzenia?", "answer": "Nie, konieczny jest osobny test odtwarzania."},
        {"question": "Czy zrzut może zawierać dane poufne?", "answer": "Tak, trzeba ograniczyć do niego dostęp."},
        {"question": "Gdzie nie umieszczać zrzutu bazy?", "answer": "W repozytorium kodu."},
        {"question": "Co sprawdzić przed pg_dump?", "answer": "Dostępne miejsce i docelową lokalizację pliku."},
        {"question": "Czym jest migracja?", "answer": "Wersjonowaną zmianą schematu danych."},
        {"question": "Po co rejestrować zastosowane migracje?", "answer": "Aby wiedzieć, jaki schemat obowiązuje w danym środowisku."},
        {"question": "Co sprawdzić przed zmianą schematu?", "answer": "Kopię danych i zgodność wersji aplikacji."},
        {"question": "Co pokazuje psql z \\dt?", "answer": "Listę tabel dostępnych w bieżącej bazie."},
        {"question": "Czy restart bazy wykonuje migracje?", "answer": "Nie, migracje wymagają osobnego kroku."},
        {"question": "Co grozi przy niekontrolowanym skrypcie SQL?", "answer": "Nieoczekiwana zmiana lub utrata danych."},
        {"question": "Po co testować migrację poza produkcją?", "answer": "Aby wykryć błędy schematu i zgodności wcześniej."},
        {"question": "Czy pg_dump zastępuje plan DR?", "answer": "Nie, jest jednym z elementów ochrony danych."},
        {"question": "Kiedy volume pozostaje po compose down?", "answer": "Gdy nie użyto opcji -v usuwającej volume."},
        {"question": "Co sprawdzić po ćwiczeniowej migracji?", "answer": "Stan tabel i działanie zapytań aplikacji."},
        {"question": "Po co oddzielić kopię od hosta bazy?", "answer": "Aby awaria jednego hosta nie usuwała obu egzemplarzy danych."},
        {"question": "Co powinno być opisane przy pliku kopii?", "answer": "Baza źródłowa, czas wykonania i miejsce bezpiecznego przechowywania."},
    ],
}
