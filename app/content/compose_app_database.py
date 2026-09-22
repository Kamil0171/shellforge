COMPOSE_APP_DATABASE = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "Aplikacja i baza w Docker Compose",
        "level": "Średnio zaawansowany",
        "duration": "65 min",
        "description": "Połączysz orders-api z PostgreSQL przez nazwę usługi i poczekasz na gotowość bazy.",
        "theory": (
            "Docker Compose opisuje kilka powiązanych usług w jednym pliku YAML. Usługa "
            "<code>orders-api</code> buduje obraz aplikacji, a <code>app-db</code> uruchamia PostgreSQL. "
            "Compose tworzy wspólną sieć projektu, w której nazwa usługi <code>app-db</code> rozwiązuje się "
            "przez DNS. Wewnątrz <code>orders-api</code> adres <code>localhost</code> oznacza samą "
            "aplikację, nie bazę. Łańcuch połączenia powinien wskazywać <code>app-db:5432</code>, a nie "
            "port opublikowany na hoście. Zwykle publikuje się tylko port aplikacji; dane bazy trafiają na "
            "nazwany volume. <code>depends_on</code> w prostym wariancie ustala kolejność tworzenia usług, "
            "ale nie gwarantuje gotowości bazy. Dopiero <code>healthcheck</code> i warunek "
            "<code>service_healthy</code> opóźniają utworzenie aplikacji do czasu poprawnego testu "
            "<code>pg_isready</code>. Aplikacja i tak powinna obsługiwać późniejsze zerwania połączenia. "
            "Plik <code>orders-api.env</code> może zawierać <code>DATABASE_URL</code> wskazujący "
            "<code>app-db:5432</code>. Pliki env zawierające dane dostępowe trzymaj poza kontrolą "
            "wersji i ogranicz uprawnienia. "
            "<code>docker compose down</code> usuwa kontenery i sieć projektu, ale bez <code>-v</code> "
            "pozostawia nazwany volume."
        ),
        "commands": [
            {"command": "cat compose.yaml", "description": "Pokazuje układ dwóch usług, healthcheck i nazwany volume.", "example": "services:\n  orders-api:\n    build: .\n    ports:\n      - '127.0.0.1:8000:8000'\n    env_file: ./orders-api.env\n    depends_on:\n      app-db:\n        condition: service_healthy\n  app-db:\n    image: postgres:17\n    env_file: ./orders-db.env\n    volumes:\n      - app-db-data:/var/lib/postgresql/data\n    healthcheck:\n      test: ['CMD-SHELL', 'pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}']\n      interval: 10s\n      timeout: 5s\n      retries: 5\nvolumes:\n  app-db-data:"},
            {"command": "docker compose up -d --build", "description": "Buduje obraz aplikacji i uruchamia usługi opisane w compose.yaml.", "example": "$ docker compose up -d --build"},
            {"command": "docker compose ps", "description": "Pokazuje stan obu usług i wynik healthcheck.", "example": "$ docker compose ps"},
            {"command": "docker compose logs --tail 50 app-db", "description": "Czyta komunikaty bazy w projekcie Compose.", "example": "$ docker compose logs --tail 50 app-db"},
            {"command": "docker compose exec app-db pg_isready -U orders -d orders", "description": "Sprawdza gotowość bazy z jej kontenera.", "example": "$ docker compose exec app-db pg_isready -U orders -d orders"},
            {"command": "docker compose exec orders-api python -c \"import socket; print(socket.gethostbyname('app-db'))\"", "description": "Potwierdza rozwiązywanie nazwy usługi bazy z aplikacji.", "example": "$ docker compose exec orders-api python -c \"import socket; print(socket.gethostbyname('app-db'))\""},
            {"command": "docker compose down", "description": "Usuwa kontenery i sieć projektu, zachowując nazwany volume.", "example": "$ docker compose down"},
        ],
        "practice_task": (
            "Utwórz <code>compose.yaml</code> z usługami <code>orders-api</code> i <code>app-db</code>. "
            "Dla bazy dodaj volume <code>app-db-data</code> oraz healthcheck z "
            "<code>pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}</code>. Przy aplikacji ustaw "
            "zależność od bazy z warunkiem <code>service_healthy</code>. W nieśledzonym "
            "<code>orders-api.env</code> ustaw adres bazy z hostem <code>app-db</code>. "
            "Udostępnij na hoście tylko port aplikacji. Po uruchomieniu sprawdź "
            "stan usług, DNS z aplikacji i połączenie z bazą; po <code>docker compose down</code> "
            "potwierdź obecność volume."
        ),
        "common_mistakes": [
            "Używanie localhost w aplikacji jako adresu osobnego kontenera bazy.",
            "Zakładanie, że samo depends_on czeka na gotowość PostgreSQL.",
            "Publikowanie portu 5432 bez potrzeby.",
            "Dodawanie plików env z hasłem do repozytorium.",
            "Przekonanie, że healthcheck zastępuje obsługę utraty połączenia w aplikacji.",
        ],
        "summary": (
            "Compose opisuje aplikację i bazę jako usługi. Ich wspólna sieć zapewnia adresowanie po nazwie, "
            "healthcheck pomaga przy starcie, a volume utrzymuje dane. Aplikacja musi również reagować "
            "na awarie bazy po uruchomieniu."
        ),
    },
    "quiz": {
        "title": "Quiz: aplikacja i baza w Docker Compose",
        "description": "Sprawdź adresowanie usług, healthcheck i trwałość danych.",
        "questions": [
            {"text": "Jaki host bazy powinno użyć orders-api w sieci Compose?", "answers": [("a", "app-db", True), ("b", "localhost aplikacji", False), ("c", "Nazwa volume app-db-data", False), ("d", "Adres registry", False)]},
            {"text": "Co zapewnia depends_on bez warunku zdrowia?", "answers": [("a", "Kolejność tworzenia usług, ale nie gotowość bazy", True), ("b", "Pełną gotowość schematu i połączeń", False), ("c", "Automatyczny backup", False), ("d", "Publikację portu 5432", False)]},
            {"text": "Jak opóźnić utworzenie aplikacji do czasu gotowości PostgreSQL?", "answers": [("a", "Użyć healthcheck i depends_on z service_healthy", True), ("b", "Dodać EXPOSE 5432 do aplikacji", False), ("c", "Usunąć volume", False), ("d", "Zmienić tag obrazu aplikacji", False)]},
            {"text": "Co zwykle pozostaje po docker compose down bez -v?", "answers": [("a", "Nazwany volume z danymi", True), ("b", "Wszystkie kontenery projektu", False), ("c", "Wyłącznie działający proces bazy", False), ("d", "Opublikowany port aplikacji", False)]},
            {"text": "Dlaczego aplikacja musi radzić sobie z przerwą połączenia mimo healthcheck startowego?", "answers": [("a", "Baza może stać się niedostępna po starcie", True), ("b", "Healthcheck usuwa dane", False), ("c", "Compose nie tworzy sieci", False), ("d", "DNS działa tylko przed startem", False)]},
            {"text": "Który port wystawisz na hoście, jeśli bazę obsługuje tylko orders-api?", "answers": [("a", "Port aplikacji, bez portu bazy", True), ("b", "Zawsze 5432 bazy", False), ("c", "Wszystkie porty wszystkich usług", False), ("d", "Żaden port, nawet gdy aplikacja ma być dostępna", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest Docker Compose?", "answer": "Narzędziem do opisu i uruchamiania powiązanych usług."},
        {"question": "Gdzie zapisuje się usługi Compose?", "answer": "Zwykle w pliku compose.yaml."},
        {"question": "Co robi docker compose up?", "answer": "Tworzy i uruchamia usługi projektu."},
        {"question": "Co dodaje --build do compose up?", "answer": "Buduje obrazy usług przed uruchomieniem."},
        {"question": "Co pokazuje docker compose ps?", "answer": "Stan usług projektu."},
        {"question": "Jak odczytać logi jednej usługi?", "answer": "docker compose logs app-db."},
        {"question": "Jak uruchomić polecenie w usłudze?", "answer": "docker compose exec nazwa-usługi polecenie."},
        {"question": "Jaką sieć tworzy Compose domyślnie?", "answer": "Wspólną sieć projektu dla jego usług."},
        {"question": "Jak aplikacja odnajduje bazę?", "answer": "Przez nazwę usługi app-db w DNS sieci Compose."},
        {"question": "Co znaczy localhost w kontenerze aplikacji?", "answer": "Sam kontener aplikacji."},
        {"question": "Jaki port bazy wykorzystuje aplikacja w sieci?", "answer": "Wewnętrzny port 5432 usługi app-db."},
        {"question": "Czy bazę trzeba wystawić przez ports?", "answer": "Nie, jeśli korzysta z niej tylko aplikacja w Compose."},
        {"question": "Co robi podstawowe depends_on?", "answer": "Ustala kolejność tworzenia usług."},
        {"question": "Czy podstawowe depends_on czeka na gotowość?", "answer": "Nie, potrzebny jest healthcheck i service_healthy."},
        {"question": "Czym jest healthcheck?", "answer": "Testem informującym, czy usługa jest gotowa według przyjętego kryterium."},
        {"question": "Co sprawdza pg_isready w healthcheck?", "answer": "Gotowość serwera PostgreSQL do przyjmowania połączeń."},
        {"question": "Co oznacza service_healthy?", "answer": "Warunek oczekiwania na zdrowy stan usługi zależnej."},
        {"question": "Po co podwójny dolar w $${POSTGRES_USER}?", "answer": "Zapobiega podstawieniu zmiennej przez Compose przed uruchomieniem kontenera."},
        {"question": "Czy healthcheck usuwa potrzebę ponowienia połączenia?", "answer": "Nie, baza może przestać działać później."},
        {"question": "Gdzie trzymać dane app-db?", "answer": "W nazwanym volume, poza zapisywalną warstwą kontenera."},
        {"question": "Co robi docker compose down?", "answer": "Usuwa kontenery i sieć projektu."},
        {"question": "Czy down bez -v usuwa nazwany volume?", "answer": "Nie, volume pozostaje."},
        {"question": "Jak chronić hasło użyte przez Compose?", "answer": "Nie commitować pliku env i ograniczyć do niego dostęp."},
        {"question": "Co jest minimalnym testem po compose up?", "answer": "Stan usług, DNS app-db i połączenie aplikacji z bazą."},
        {"question": "Czy gotowa baza oznacza aktualny schemat?", "answer": "Nie, schemat wymaga osobnej kontroli i migracji."},
    ],
}
