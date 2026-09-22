POSTGRES_RESTORE_TEST = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Odtworzenie PostgreSQL i test kopii",
        "level": "Średnio zaawansowany",
        "duration": "70 min",
        "description": "Odtworzysz zrzut do osobnej bazy testowej i sprawdzisz dane bez naruszania źródła.",
        "theory": (
            "Test odtwarzania ma odpowiedzieć na pytanie, czy kopia pozwala odzyskać użyteczne dane w "
            "założonym czasie. Pracuj wyłącznie na fikcyjnych rekordach i w odizolowanym środowisku "
            "Compose. Nie kieruj <code>pg_restore</code> do działającej bazy <code>orders</code>. Utwórz "
            "nową, pustą bazę <code>orders_restore</code> z szablonu <code>template0</code>; nazwa "
            "jednoznacznie odróżnia cel od źródła. Przed odtworzeniem odczytaj spis archiwum "
            "<code>pg_restore --list</code>. Format custom z poprzedniej lekcji wymaga "
            "<code>pg_restore</code>, a nie <code>psql</code>. Opcja <code>--exit-on-error</code> "
            "zatrzymuje proces po błędzie SQL, a <code>--no-owner</code> pomija odtwarzanie właściciela "
            "obiektów w teście z innymi rolami. Uprawnienia i rozszerzenia mogą wymagać osobnej kontroli "
            "w prawdziwym planie odzyskiwania. Po odtworzeniu sprawdź listę tabel, liczbę i treść "
            "przygotowanych wcześniej rekordów <code>backup_probe</code> oraz prosty odczyt aplikacji "
            "skierowanej na bazę testową. Zanotuj czas od rozpoczęcia do potwierdzenia działania i porównaj "
            "go z RTO. Jeżeli zapisane dwa rekordy nie wracają, test jest nieudany nawet przy kodzie 0 "
            "procesu. Ćwiczenie nie obejmuje nadpisania produkcji; taki krok wymaga osobnego runbooka, "
            "kontroli uprawnień i decyzji podczas rzeczywistego incydentu."
        ),
        "commands": [
            {"command": "test -s ../backups/orders-test.backup", "description": "Potwierdza dostępność przygotowanego pliku testowego.", "example": "$ test -s ../backups/orders-test.backup"},
            {"command": "docker compose exec -T app-db pg_restore --list < ../backups/orders-test.backup", "description": "Sprawdza spis obiektów przed odtworzeniem.", "example": "$ docker compose exec -T app-db pg_restore --list < ../backups/orders-test.backup"},
            {"command": "docker compose exec -T app-db createdb -U orders -T template0 orders_restore", "description": "Tworzy osobną pustą bazę testową bez dotykania orders.", "example": "$ docker compose exec -T app-db createdb -U orders -T template0 orders_restore"},
            {"command": "docker compose exec -T app-db pg_restore --exit-on-error --no-owner -U orders -d orders_restore < ../backups/orders-test.backup", "description": "Odtwarza archiwum custom wyłącznie do nowej bazy testowej.", "example": "$ docker compose exec -T app-db pg_restore --exit-on-error --no-owner -U orders -d orders_restore < ../backups/orders-test.backup"},
            {"command": "docker compose exec -T app-db psql -U orders -d orders_restore -c '\\dt'", "description": "Pokazuje tabele utworzone w bazie testowej.", "example": "$ docker compose exec -T app-db psql -U orders -d orders_restore -c '\\dt'"},
            {"command": "docker compose exec -T app-db psql -U orders -d orders_restore -c 'SELECT count(*) FROM backup_probe;'", "description": "Porównuje liczbę fikcyjnych rekordów z liczbą przed zrzutem.", "example": "$ docker compose exec -T app-db psql -U orders -d orders_restore -c 'SELECT count(*) FROM backup_probe;'"},
            {"command": "docker compose exec -T app-db psql -U orders -d orders_restore -c 'SELECT id, label FROM backup_probe ORDER BY id;'", "description": "Potwierdza treść dwóch przygotowanych rekordów testowych.", "example": "$ docker compose exec -T app-db psql -U orders -d orders_restore -c 'SELECT id, label FROM backup_probe ORDER BY id;'"},
        ],
        "practice_task": (
            "W lekcji o backupie przygotowano tabelę <code>backup_probe(id, label)</code> z dwoma "
            "fikcyjnymi wierszami. Odczytaj archiwum, utwórz wyłącznie nową bazę "
            "<code>orders_restore</code> i odtwórz do niej zrzut. Porównaj liczbę oraz treść rekordów "
            "z notatką sprzed kopii. Skieruj osobną instancję ćwiczeniowej aplikacji na bazę testową "
            "i sprawdź jeden odczyt; nie zmieniaj połączenia działającej instancji. Zapisz czas testu, "
            "wynik i ewentualne błędy. Jeśli baza docelowa już istnieje, przerwij ćwiczenie i użyj "
            "innej nowej nazwy zamiast czyścić lub nadpisywać dane."
        ),
        "common_mistakes": [
            "Odtwarzanie do tej samej bazy, z której wykonano kopię.",
            "Użycie psql do archiwum custom zamiast pg_restore.",
            "Ignorowanie błędów pg_restore i ocenianie tylko obecności tabel.",
            "Sprawdzenie liczby rekordów bez porównania ich treści.",
            "Testowanie aplikacji przez zmianę połączenia działającej instancji.",
        ],
        "summary": (
            "Sprawdzony backup da się odtworzyć do pustej, odizolowanej bazy. Wynik ocenia się "
            "przez błędy procesu, schemat, oczekiwane rekordy, odczyt aplikacji i czas potrzebny "
            "na cały test. Źródłowa baza pozostaje nietknięta."
        ),
    },
    "quiz": {
        "title": "Quiz: odtworzenie PostgreSQL i test kopii",
        "description": "Rozpoznaj bezpieczny cel odtwarzania i właściwe kryterium sukcesu.",
        "questions": [
            {"text": "Masz zrzut testowej bazy orders. Dokąd należy go odtworzyć w ćwiczeniu?", "answers": [("a", "Do nowej pustej bazy orders_restore w izolowanym środowisku", True), ("b", "Do działającej bazy orders", False), ("c", "Do katalogu kodu aplikacji", False), ("d", "Do obrazu kontenera bez bazy", False)]},
            {"text": "Archiwum utworzono przez pg_dump -Fc. Jakiego narzędzia użyjesz do odtworzenia?", "answers": [("a", "pg_restore", True), ("b", "psql -f bez konwersji", False), ("c", "docker logs", False), ("d", "curl", False)]},
            {"text": "Po odtworzeniu są tabele, ale backup_probe ma tylko jeden z dwóch zapisanych rekordów. Jak oceniasz test?", "answers": [("a", "Nieudany; trzeba wyjaśnić brak danych", True), ("b", "Udany, bo tabela istnieje", False), ("c", "Udany, bo baza odpowiada na ping", False), ("d", "Nie trzeba porównywać danych", False)]},
            {"text": "Po co utworzyć orders_restore z template0?", "answers": [("a", "Aby odtwarzać do pustej bazy bez dodatkowych obiektów z template1", True), ("b", "Aby automatycznie nadpisać orders", False), ("c", "Aby pominąć kontrolę zrzutu", False), ("d", "Aby zaszyfrować plik", False)]},
            {"text": "Co oznacza --exit-on-error podczas testu?", "answers": [("a", "Zatrzymuje odtwarzanie po błędzie SQL zamiast kontynuować", True), ("b", "Usuwa bazę źródłową", False), ("c", "Wyłącza serwer PostgreSQL", False), ("d", "Sprawdza tylko sumę pliku", False)]},
            {"text": "Nowa baza testowa już istnieje i ma nieznane dane. Co zrobisz?", "answers": [("a", "Przerwę test i wybiorę inną nową nazwę bez czyszczenia istniejącej bazy", True), ("b", "Wykonam --clean bez sprawdzenia", False), ("c", "Nadpiszę produkcyjne orders", False), ("d", "Pominę odtworzenie i zgłoszę sukces", False)]},
        ],
    },
    "flashcards": [
        {"question": "Jaki jest cel testu odtwarzania?", "answer": "Potwierdzenie, że kopia przywraca użyteczne dane i działanie usługi."},
        {"question": "Dlaczego użyć osobnej bazy?", "answer": "Aby test nie zmienił danych źródłowych."},
        {"question": "Jaką bazę tworzy createdb -T template0?", "answer": "Nową pustą bazę bez lokalnych dodatków template1."},
        {"question": "Co oznacza orders_restore?", "answer": "Jednoznaczny cel odtworzenia ćwiczeniowej kopii."},
        {"question": "Czym odtworzyć archiwum -Fc?", "answer": "Narzędziem pg_restore."},
        {"question": "Czy psql czyta bezpośrednio format custom?", "answer": "Nie, do tego formatu służy pg_restore."},
        {"question": "Co daje --exit-on-error?", "answer": "Kończy pg_restore po pierwszym błędzie SQL."},
        {"question": "Co daje --no-owner?", "answer": "Pomija odtwarzanie własności obiektów w celu testowym."},
        {"question": "Dlaczego nadal sprawdzać uprawnienia?", "answer": "Pomijanie właściciela nie gwarantuje zgodności uprawnień aplikacji."},
        {"question": "Co sprawdzić przed pg_restore?", "answer": "Plik kopii, spis obiektów i nazwę pustej bazy docelowej."},
        {"question": "Czy pg_restore --list odtwarza dane?", "answer": "Nie, wyświetla tylko spis archiwum."},
        {"question": "Jak sprawdzić schemat po odtworzeniu?", "answer": "Odczytać listę oczekiwanych tabel w bazie testowej."},
        {"question": "Jak sprawdzić kompletność testowych rekordów?", "answer": "Porównać ich liczbę i treść z notatką sprzed kopii."},
        {"question": "Dlaczego sama liczba rekordów nie wystarcza?", "answer": "Taka sama liczba może ukrywać niepoprawną treść."},
        {"question": "Co zrobić, gdy baza docelowa istnieje?", "answer": "Przerwać i wybrać nową nazwę bez czyszczenia nieznanych danych."},
        {"question": "Jak testować aplikację po odtworzeniu?", "answer": "Uruchomić osobną instancję na bazie testowej i sprawdzić ważny odczyt."},
        {"question": "Dlaczego nie przełączać działającej aplikacji?", "answer": "Test nie powinien zmieniać ruchu ani danych użytkowników."},
        {"question": "Co oznacza brak jednego z dwóch rekordów?", "answer": "Nieudany test wymagający wyjaśnienia zakresu zrzutu lub odtworzenia."},
        {"question": "Jak mierzyć czas odtworzenia?", "answer": "Od startu procedury do potwierdzenia danych i działania aplikacji."},
        {"question": "Z czym porównać czas testu?", "answer": "Z wymaganiem RTO dla usługi."},
        {"question": "Co zapisać w raporcie testu?", "answer": "Źródło kopii, cel, czas, wyniki kontroli i błędy."},
        {"question": "Czy kod 0 zawsze dowodzi kompletności danych?", "answer": "Nie, trzeba jeszcze porównać oczekiwane rekordy i funkcję aplikacji."},
        {"question": "Jaka jest rola izolacji testu?", "answer": "Chroni źródło i pozwala bezpiecznie wykryć problem procedury."},
        {"question": "Co zrobić po nieudanym teście kopii?", "answer": "Zbadać przyczynę, poprawić procedurę i powtórzyć odtworzenie."},
        {"question": "Kiedy kopia jest praktycznie sprawdzona?", "answer": "Gdy odtworzone dane i kluczowy odczyt aplikacji zgadzają się z oczekiwaniem."},
    ],
}
