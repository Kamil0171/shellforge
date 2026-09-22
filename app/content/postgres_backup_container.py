POSTGRES_BACKUP_CONTAINER = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Backup PostgreSQL w kontenerze",
        "level": "Średnio zaawansowany",
        "duration": "65 min",
        "description": "Wykonasz i zweryfikujesz logiczny zrzut ćwiczeniowej bazy PostgreSQL uruchomionej przez Compose.",
        "theory": (
            "W ćwiczeniowym Compose usługa <code>app-db</code> przechowuje dane na nazwanym volume. "
            "<code>pg_dump</code> tworzy osobny logiczny zrzut jednej bazy; format custom <code>-Fc</code> "
            "można później odtworzyć przez <code>pg_restore</code>. Wykonaj polecenie z katalogu "
            "z plikiem Compose. Opcja <code>exec -T</code> wyłącza TTY, co jest ważne dla strumienia "
            "binarnego kierowanego do pliku na hoście. W powłoce Linux przekierowanie <code>&gt;</code> "
            "zapisuje plik po stronie hosta, nie wewnątrz kontenera. Użyj katalogu poza repozytorium, "
            "z ograniczonym dostępem. Przed zadaniem sprawdź dostępną przestrzeń oraz uprawnienia. "
            "Najpierw utwórz wyłącznie testowe rekordy w bazie <code>orders</code>. Po zrzucie sprawdź "
            "kod wyjścia polecenia, rozmiar i listę obiektów przez <code>pg_restore --list</code>. "
            "Sama lista nie potwierdza poprawnego odtworzenia; to osobna lekcja. "
            "W automatyzacji zapewnij log wyniku, alarm po błędzie, retencję i test odtwarzania. "
            "Nie wpisuj hasła do polecenia ani do pliku lekcji: korzystaj z bezpiecznego mechanizmu "
            "przekazywania danych uwierzytelniających. <code>pg_dump</code> jednej bazy nie obejmuje "
            "automatycznie wszystkich ról ani innych baz klastra."
        ),
        "commands": [
            {"command": "docker compose ps app-db", "description": "Potwierdza, że ćwiczeniowa baza działa przed zrzutem.", "example": "$ docker compose ps app-db"},
            {"command": "mkdir -p ../backups", "description": "Przygotowuje lokalizację testowej kopii poza katalogiem repozytorium.", "example": "$ mkdir -p ../backups"},
            {"command": "df -h ../backups", "description": "Sprawdza miejsce w lokalizacji docelowej.", "example": "$ df -h ../backups"},
            {"command": "docker compose exec -T app-db pg_dump -U orders -d orders -Fc > ../backups/orders-test.backup", "description": "Zapisuje zrzut ćwiczeniowej bazy w formacie custom na hoście Linux.", "example": "$ docker compose exec -T app-db pg_dump -U orders -d orders -Fc > ../backups/orders-test.backup"},
            {"command": "test -s ../backups/orders-test.backup", "description": "Sprawdza, że wynikowy plik nie jest pusty.", "example": "$ test -s ../backups/orders-test.backup"},
            {"command": "docker compose exec -T app-db pg_restore --list < ../backups/orders-test.backup", "description": "Czyta katalog obiektów zrzutu bez zmiany bazy.", "example": "$ docker compose exec -T app-db pg_restore --list < ../backups/orders-test.backup"},
            {"command": "sha256sum ../backups/orders-test.backup", "description": "Zapisuje sumę kontrolną pliku do porównania po przeniesieniu.", "example": "$ sha256sum ../backups/orders-test.backup"},
        ],
        "practice_task": (
            "Na izolowanym środowisku Compose przygotuj w bazie <code>orders</code> tabelę "
            "<code>backup_probe</code> z dwoma fikcyjnymi wierszami i zanotuj ich liczbę. "
            "Sprawdź miejsce w <code>../backups</code>, wykonaj <code>pg_dump -Fc</code> i sprawdź "
            "kod zakończenia, niepusty plik, spis obiektów oraz sumę kontrolną. Ustal, gdzie "
            "przechowywać kopię poza hostem, jak długo ją zachować i jaki alert wysłać po błędzie. "
            "Nie używaj danych produkcyjnych ani nie commituj pliku kopii."
        ),
        "common_mistakes": [
            "Zapis pliku wewnątrz nietrwałej warstwy kontenera zamiast na chronionym hoście.",
            "Użycie interaktywnego TTY przy przekierowaniu binarnego formatu custom.",
            "Brak kontroli kodu zakończenia pg_dump przed uznaniem pliku za kopię.",
            "Przechowywanie zrzutu w repozytorium albo bez ograniczenia dostępu.",
            "Założenie, że zrzut jednej bazy obejmuje role i wszystkie bazy klastra.",
        ],
        "summary": (
            "Zrzut pg_dump w formacie custom jest oddzielny od volume. Po zapisaniu na hoście "
            "sprawdź wynik polecenia, plik i katalog obiektów, a następnie bezpieczne przechowywanie. "
            "Pełna weryfikacja wymaga jeszcze odtworzenia na danych testowych."
        ),
    },
    "quiz": {
        "title": "Quiz: backup PostgreSQL w kontenerze",
        "description": "Wybierz poprawne kroki tworzenia i wstępnej kontroli zrzutu.",
        "questions": [
            {"text": "Dlaczego przy pg_dump -Fc kierowanym do pliku użyto docker compose exec -T?", "answers": [("a", "Aby wyłączyć TTY i zachować poprawny strumień binarny", True), ("b", "Aby automatycznie zaszyfrować zrzut", False), ("c", "Aby skasować volume po zrzucie", False), ("d", "Aby objąć wszystkie bazy klastra", False)]},
            {"text": "Gdzie powstaje plik przy przekierowaniu > ../backups/orders-test.backup w powłoce hosta?", "answers": [("a", "Na hoście uruchamiającym polecenie", True), ("b", "W obrazie PostgreSQL", False), ("c", "W registry obrazów", False), ("d", "W katalogu danych każdej bazy", False)]},
            {"text": "Zadanie pg_dump zakończyło się błędem, ale plik ma kilka bajtów. Co zrobisz?", "answers": [("a", "Oznaczę kopię jako nieudaną, zbadam błąd i ponowię zadanie", True), ("b", "Uznaję ją za gotową, bo plik istnieje", False), ("c", "Wyłączę monitoring zadania", False), ("d", "Zmienię nazwę pliku na .sql", False)]},
            {"text": "Czego dowodzi pg_restore --list na zrzucie custom?", "answers": [("a", "Że można odczytać spis obiektów archiwum, ale nie pełnej odtwarzalności", True), ("b", "Że aplikacja po odtworzeniu działa", False), ("c", "Że wszystkie sekrety są zapisane", False), ("d", "Że kopia jest poza hostem", False)]},
            {"text": "Czy pg_dump -d orders zachowuje automatycznie wszystkie role i inne bazy klastra?", "answers": [("a", "Nie, dotyczy wskazanej bazy; globalne obiekty wymagają osobnego planu", True), ("b", "Tak, zawsze obejmuje cały klaster", False), ("c", "Tak, jeśli plik ma rozszerzenie .backup", False), ("d", "Tylko gdy baza działa na volume", False)]},
            {"text": "Co powinien zgłosić automatyczny backup, gdy zadanie nie tworzy poprawnego zrzutu?", "answers": [("a", "Błąd zadania z czasem i przyczyną do osoby odpowiedzialnej", True), ("b", "Sukces, bo harmonogram się uruchomił", False), ("c", "Wyłącznie liczbę kontenerów", False), ("d", "Nowy tag obrazu aplikacji", False)]},
        ],
    },
    "flashcards": [
        {"question": "Co tworzy pg_dump?", "answer": "Logiczny zrzut wskazanej bazy PostgreSQL."},
        {"question": "Co oznacza format -Fc?", "answer": "Archiwum custom obsługiwane przez pg_restore."},
        {"question": "Po co uruchamiać pg_dump przez compose exec?", "answer": "Aby użyć narzędzia PostgreSQL w kontenerze usługi bazy."},
        {"question": "Dlaczego exec -T jest ważne dla zrzutu?", "answer": "Wyłącza TTY, który może zakłócić strumień binarny."},
        {"question": "Dokąd zapisuje > w powłoce hosta?", "answer": "Do pliku na hoście uruchamiającym polecenie."},
        {"question": "Co sprawdzić przed zrzutem?", "answer": "Stan bazy, miejsce i uprawnienia lokalizacji docelowej."},
        {"question": "Co oznacza niezerowy kod pg_dump?", "answer": "Zadanie zakończyło się błędem i pliku nie wolno uznać za sprawdzoną kopię."},
        {"question": "Co sprawdza test -s po zrzucie?", "answer": "Istnienie i niezerowy rozmiar pliku."},
        {"question": "Co pokazuje pg_restore --list?", "answer": "Katalog obiektów zapisanych w archiwum custom."},
        {"question": "Czy --list zmienia bazę?", "answer": "Nie, odczytuje archiwum bez odtwarzania."},
        {"question": "Po co zapisać sumę zrzutu?", "answer": "Aby wykryć zmianę pliku podczas późniejszego przenoszenia."},
        {"question": "Co jest lepszym dowodem niż spis obiektów?", "answer": "Odtworzenie do osobnej bazy i kontrola danych."},
        {"question": "Czy pojedynczy pg_dump obejmuje cały klaster?", "answer": "Nie, dotyczy wskazanej bazy."},
        {"question": "Jak zabezpieczyć role klastra w planie?", "answer": "Zaplanować osobną kopię obiektów globalnych, jeśli są potrzebne do odtworzenia."},
        {"question": "Dlaczego nie wpisywać hasła w polecenie?", "answer": "Może trafić do historii powłoki lub logów procesu."},
        {"question": "Gdzie trzymać plik zrzutu?", "answer": "W chronionej lokalizacji poza repozytorium, z kopią poza hostem."},
        {"question": "Co oznacza nazwa orders-test.backup?", "answer": "Plik zrzutu ćwiczeniowej bazy, a nie danych produkcyjnych."},
        {"question": "Czy volume zastępuje pg_dump?", "answer": "Nie, volume przechowuje działające dane, a pg_dump tworzy osobny zrzut."},
        {"question": "Jakie dane użyć w ćwiczeniu?", "answer": "Fikcyjne rekordy w odizolowanej bazie testowej."},
        {"question": "Co powinien rejestrować harmonogram?", "answer": "Czas startu, wynik, rozmiar i lokalizację kopii."},
        {"question": "Kiedy wysłać alert backupu?", "answer": "Po błędzie zadania lub gdy ostatnia udana kopia przekracza dopuszczalny wiek."},
        {"question": "Dlaczego sprawdzać retencję?", "answer": "Aby utrzymywać wymagane punkty odzyskiwania bez zapełnienia miejsca."},
        {"question": "Czy pg_dump -Fc jest plikiem SQL dla psql?", "answer": "Nie, format custom odtwarza się przez pg_restore."},
        {"question": "Co zrobić po błędzie kopii?", "answer": "Ustalić przyczynę i wykonać nową, sprawdzoną kopię."},
        {"question": "Jaki krok następuje po utworzeniu zrzutu?", "answer": "Test odtworzenia w odizolowanej bazie."},
    ],
}
