POSTGRES_CONTAINER = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "PostgreSQL w środowisku aplikacji",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": "Uruchomisz osobny kontener bazy, sprawdzisz gotowość i wykonasz pierwsze zapytanie bez wystawiania portu publicznie.",
        "theory": (
            "Aplikacja i baza mają odrębne cykle życia. Obraz aplikacji nie powinien zawierać plików "
            "PostgreSQL ani hasła bazy. Oficjalny obraz <code>postgres:17</code> przy pierwszym uruchomieniu "
            "inicjalizuje bazę z wartości <code>POSTGRES_USER</code>, <code>POSTGRES_DB</code> i "
            "<code>POSTGRES_PASSWORD</code>. W tym ćwiczeniu wartości pochodzą z lokalnego pliku "
            "<code>orders-db.env</code>, który nie jest śledzony przez Git i ma ograniczony dostęp. "
            "Przekazywanie zmiennych przez env ułatwia konfigurację, ale nie stanowi pełnej ochrony sekretów; "
            "w środowisku produkcyjnym trzeba użyć odpowiedniego mechanizmu sekretów. PostgreSQL nasłuchuje "
            "zwykle na porcie 5432 wewnątrz kontenera. Aplikacja w tej samej sieci może łączyć się po nazwie "
            "<code>app-db</code>, bez publikowania portu bazy na hoście. Łańcuch połączenia opisuje schemat, "
            "użytkownika, hasło, host, port i nazwę bazy; znaki specjalne w haśle wymagają poprawnego "
            "kodowania albo parametrów sterownika. Nazwany volume chroni pliki danych przed usunięciem "
            "kontenera. <code>pg_isready</code> sprawdza gotowość serwera, a <code>psql</code> wykonuje "
            "zapytania SQL. Gotowość serwera nie dowodzi jeszcze, że schemat aplikacji jest aktualny."
        ),
        "commands": [
            {"command": "docker volume create app-db-data", "description": "Tworzy trwałe miejsce na pliki bazy.", "example": "$ docker volume create app-db-data"},
            {"command": "docker network create orders-net", "description": "Tworzy prywatną sieć aplikacji i bazy.", "example": "$ docker network create orders-net"},
            {"command": "docker run -d --name app-db --network orders-net --env-file ./orders-db.env -v app-db-data:/var/lib/postgresql/data postgres:17", "description": "Uruchamia PostgreSQL z lokalną konfiguracją i volume, bez publikacji portu.", "example": "$ docker run -d --name app-db --network orders-net --env-file ./orders-db.env -v app-db-data:/var/lib/postgresql/data postgres:17"},
            {"command": "docker exec app-db pg_isready -U orders -d orders", "description": "Sprawdza gotowość bazy dla wskazanego użytkownika i nazwy.", "example": "$ docker exec app-db pg_isready -U orders -d orders"},
            {"command": "docker exec app-db psql -U orders -d orders -c 'SELECT 1;'", "description": "Wykonuje proste zapytanie w działającym kontenerze.", "example": "$ docker exec app-db psql -U orders -d orders -c 'SELECT 1;'"},
            {"command": "docker logs --tail 50 app-db", "description": "Sprawdza komunikaty startowe i błędy PostgreSQL.", "example": "$ docker logs --tail 50 app-db"},
        ],
        "practice_task": (
            "Utwórz w katalogu ćwiczenia nieśledzony plik <code>orders-db.env</code> zawierający testowe wartości "
            "<code>POSTGRES_USER=orders</code>, <code>POSTGRES_DB=orders</code> i własne hasło testowe "
            "w <code>POSTGRES_PASSWORD</code>. Uruchom <code>app-db</code> z volume, bez <code>-p</code>. "
            "Sprawdź <code>pg_isready</code>, wykonaj <code>SELECT 1</code> i zapisz elementy adresu "
            "<code>postgresql://orders:…@app-db:5432/orders</code>. Nie zapisuj hasła w notatce."
        ),
        "common_mistakes": [
            "Publikowanie portu 5432, choć korzysta z niego tylko aplikacja w prywatnej sieci.",
            "Commitowanie pliku z hasłem do repozytorium.",
            "Przechowywanie plików bazy wyłącznie w warstwie kontenera.",
            "Zakładanie, że zmiana POSTGRES_PASSWORD po inicjalizacji automatycznie zmieni hasło istniejącego użytkownika.",
            "Uznawanie pg_isready za test poprawności schematu aplikacji.",
        ],
        "summary": (
            "PostgreSQL uruchamiaj jako osobną usługę z volume i kontrolowaną konfiguracją. "
            "Port 5432 może pozostać wyłącznie w prywatnej sieci. Gotowość sprawdza pg_isready, "
            "a podstawowe połączenie i zapytanie psql."
        ),
    },
    "quiz": {
        "title": "Quiz: PostgreSQL w środowisku aplikacji",
        "description": "Sprawdź konfigurację i diagnostykę bazy w kontenerze.",
        "questions": [
            {"text": "Aplikacja i baza są w jednej sieci Docker. Jakiego hosta użyje aplikacja?", "answers": [("a", "Nazwy kontenera app-db", True), ("b", "Zawsze 127.0.0.1 aplikacji", False), ("c", "Tagu postgres:17", False), ("d", "Nazwy volume", False)]},
            {"text": "Co zachowa dane po usunięciu kontenera app-db?", "answers": [("a", "Nazwany volume pod katalogiem danych", True), ("b", "Samo docker logs", False), ("c", "Port 5432", False), ("d", "Tag obrazu", False)]},
            {"text": "Czy aplikacja w prywatnej sieci wymaga -p 5432:5432 dla bazy?", "answers": [("a", "Nie, może użyć wewnętrznego portu kontenera", True), ("b", "Tak, DNS nie działa bez publikacji", False), ("c", "Tak, inaczej nie działa volume", False), ("d", "Tak, inaczej pg_isready usuwa kontener", False)]},
            {"text": "Które narzędzie sprawdza, czy serwer PostgreSQL przyjmuje połączenia?", "answers": [("a", "pg_isready", True), ("b", "docker images", False), ("c", "ruff check", False), ("d", "docker history", False)]},
            {"text": "Gdzie przechować hasło bazy dla ćwiczenia?", "answers": [("a", "W lokalnym pliku env poza repozytorium z ograniczonym dostępem", True), ("b", "W Dockerfile jako ENV", False), ("c", "W nazwie kontenera", False), ("d", "W publicznym README", False)]},
            {"text": "Zmieniono POSTGRES_PASSWORD dla już zainicjalizowanego volume. Czego nie należy zakładać?", "answers": [("a", "Że hasło istniejącej roli automatycznie się zmieni", True), ("b", "Że pliki bazy nadal są na volume", False), ("c", "Że kontener można zatrzymać", False), ("d", "Że psql może wykonać SQL", False)]},
        ],
    },
    "flashcards": [
        {"question": "Dlaczego baza jest osobną usługą?", "answer": "Ma własny cykl życia, dane i wymagania operacyjne."},
        {"question": "Jaki obraz uruchamia bazę w ćwiczeniu?", "answer": "postgres:17."},
        {"question": "Do czego służy POSTGRES_USER?", "answer": "Ustala użytkownika tworzonego przy inicjalizacji obrazu."},
        {"question": "Do czego służy POSTGRES_DB?", "answer": "Ustala bazę tworzoną przy inicjalizacji."},
        {"question": "Do czego służy POSTGRES_PASSWORD?", "answer": "Podaje hasło użytkownika podczas pierwszej inicjalizacji."},
        {"question": "Czy zmiana env zmienia hasło już utworzonej roli?", "answer": "Nie, wymaga osobnej operacji w bazie."},
        {"question": "Jaki jest domyślny port PostgreSQL?", "answer": "5432/TCP."},
        {"question": "Czy port bazy trzeba publikować na hoście?", "answer": "Nie, jeśli klient jest w tej samej sieci kontenerowej."},
        {"question": "Jaki host wpisuje klient w sieci Docker?", "answer": "Nazwę usługi lub kontenera, na przykład app-db."},
        {"question": "Czym jest connection string?", "answer": "Adresem opisującym połączenie klienta z bazą."},
        {"question": "Jakie części ma adres PostgreSQL?", "answer": "Schemat, dane użytkownika, host, port i nazwę bazy."},
        {"question": "Co z hasłem zawierającym znaki specjalne w URL?", "answer": "Wymaga poprawnego kodowania albo parametrów sterownika."},
        {"question": "Jak chronić plik orders-db.env?", "answer": "Nie śledzić go przez Git i ograniczyć dostęp do pliku."},
        {"question": "Czy env jest pełnym sejfem na hasło?", "answer": "Nie, do produkcji trzeba dobrać mechanizm sekretów."},
        {"question": "Po co volume bazy?", "answer": "Aby dane przetrwały wymianę kontenera."},
        {"question": "Gdzie PostgreSQL 17 zapisuje dane w kontenerze?", "answer": "W /var/lib/postgresql/data."},
        {"question": "Co sprawdza pg_isready?", "answer": "Czy serwer PostgreSQL przyjmuje połączenia."},
        {"question": "Czy pg_isready weryfikuje schemat aplikacji?", "answer": "Nie, sprawdza gotowość serwera."},
        {"question": "Do czego służy psql?", "answer": "Do łączenia się z PostgreSQL i wykonywania SQL."},
        {"question": "Co potwierdza SELECT 1?", "answer": "Że proste zapytanie SQL może zostać wykonane."},
        {"question": "Jak odczytać logi bazy?", "answer": "Poleceniem docker logs app-db."},
        {"question": "Czy baza powinna być w obrazie aplikacji?", "answer": "Nie, jest odrębną usługą z własnymi danymi."},
        {"question": "Po co prywatna sieć dla app-db?", "answer": "Pozwala aplikacji łączyć się bez wystawiania bazy publicznie."},
        {"question": "Kiedy POSTGRES_DB jest stosowane?", "answer": "Przy inicjalizacji pustego katalogu danych."},
        {"question": "Co jest następnym krokiem po pojedynczej bazie?", "answer": "Połączenie aplikacji i bazy w jednym opisie usług."},
    ],
}
