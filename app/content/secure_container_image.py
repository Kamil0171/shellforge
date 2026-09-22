SECURE_CONTAINER_IMAGE = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "Bezpieczny obraz aplikacji",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": "Ograniczysz zawartość obrazu i uprawnienia procesu, zachowując działający punkt wejścia aplikacji.",
        "theory": (
            "Prosty obraz aplikacji może zawierać kompilatory, cache pakietów i pliki budowy, których nie "
            "potrzeba podczas działania. Multi-stage build używa osobnego etapu do przygotowania zależności "
            "oraz mniejszego etapu runtime; <code>COPY --from=build</code> przenosi tylko wybrany wynik. "
            "W Pythonie można zbudować środowisko wirtualne w etapie build i skopiować je do etapu "
            "runtime o zgodnej wersji Pythona i systemu. Obraz <code>slim</code> zmniejsza liczbę zbędnych "
            "pakietów, lecz nadal trzeba regularnie aktualizować jego bazę. Instrukcja <code>USER</code> "
            "uruchamia aplikację bez uprawnień roota; katalogi potrzebne do zapisu muszą należeć do "
            "właściwego użytkownika. Nie ustawiaj <code>USER</code> dopiero w poleceniu uruchomieniowym, "
            "jeżeli obraz ma być bezpieczny domyślnie. Dla wydania wybierz kontrolowane wersje pakietów "
            "i obrazu bazowego, a przy wymaganej pełnej odtwarzalności użyj digestu. Hasła, tokeny i pliki "
            "<code>.env</code> pozostają poza obrazem. Test końcowy musi potwierdzić zarówno działanie "
            "endpointu, jak i UID procesu."
        ),
        "commands": [
            {"command": "FROM python:3.12-slim AS build", "description": "Rozpoczyna etap przygotowania zależności.", "example": "FROM python:3.12-slim AS build\nWORKDIR /srv/orders-api\nRUN python -m venv /opt/venv"},
            {"command": "RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt", "description": "Instaluje pakiety do środowiska przenoszonego między etapami.", "example": "COPY requirements.txt .\nRUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt"},
            {"command": "COPY --from=build /opt/venv /opt/venv", "description": "Przenosi gotowe zależności do etapu runtime.", "example": "FROM python:3.12-slim\nCOPY --from=build /opt/venv /opt/venv"},
            {"command": "RUN useradd --system --uid 10001 --no-create-home orders", "description": "Tworzy konto o ograniczonych uprawnieniach w obrazie.", "example": "RUN useradd --system --uid 10001 --no-create-home orders"},
            {"command": "USER orders", "description": "Ustawia użytkownika domyślnego procesu kontenera.", "example": "USER orders"},
            {"command": "docker run --rm orders-api:secure id", "description": "Sprawdza UID uruchomionego procesu.", "example": "$ docker run --rm orders-api:secure id"},
            {"command": "docker image inspect --format '{{.Config.User}}' orders-api:secure", "description": "Odczytuje domyślnego użytkownika z metadanych obrazu.", "example": "$ docker image inspect --format '{{.Config.User}}' orders-api:secure"},
        ],
        "practice_task": (
            "Przebuduj Dockerfile <code>orders-api</code> na dwa etapy: build z instalacją zależności "
            "do <code>/opt/venv</code> i runtime z tym samym obrazem bazowym bez narzędzi budowania. "
            "Utwórz konto <code>orders</code>, nadaj mu dostęp do plików aplikacji i ustaw <code>USER</code>. "
            "Uruchom <code>id</code> w kontenerze oraz żądanie do endpointu; jeśli aplikacja zapisuje "
            "pliki, sprawdź uprawnienia wyłącznie potrzebnego katalogu."
        ),
        "common_mistakes": [
            "Kopiowanie całego etapu build do runtime zamiast wybranych artefaktów.",
            "Ustawianie USER bez dostępu do plików potrzebnych aplikacji.",
            "Traktowanie slim jako gwarancji braku podatności.",
            "Przekazywanie tokenów przez ARG, ENV lub COPY do obrazu.",
            "Łączenie etapów o niezgodnej wersji Pythona lub bibliotek systemowych.",
        ],
        "summary": (
            "Oddziel etap build od runtime, przenoś tylko potrzebne pliki i uruchamiaj proces jako "
            "użytkownik bez uprawnień roota. Mniejszy obraz i kontrola wersji ograniczają ryzyko, "
            "a test UID i endpointu potwierdza działanie po zmianach."
        ),
    },
    "quiz": {
        "title": "Quiz: bezpieczny obraz aplikacji",
        "description": "Sprawdź praktyczne decyzje dotyczące wieloetapowej budowy i uprawnień.",
        "questions": [
            {"text": "Po co drugi etap FROM w obrazie aplikacji Python?", "answers": [("a", "Aby runtime zawierał tylko potrzebne pliki i zależności", True), ("b", "Aby każdy kontener miał dwa jądra", False), ("c", "Aby automatycznie uruchomić PostgreSQL", False), ("d", "Aby ukryć port przed hostem", False)]},
            {"text": "Co należy skopiować z etapu build do runtime?", "answers": [("a", "Wybrane artefakty, na przykład zgodne środowisko venv", True), ("b", "Wszystkie tymczasowe pliki i cache", False), ("c", "Historię .git i lokalne sekrety", False), ("d", "Cały system hosta", False)]},
            {"text": "Proces ma działać bez roota domyślnie. Co ustawisz?", "answers": [("a", "USER orders w Dockerfile", True), ("b", "EXPOSE root", False), ("c", "TAG non-root", False), ("d", "docker images -a", False)]},
            {"text": "Aplikacja po zmianie USER nie może zapisywać pliku. Jaka poprawka jest właściwa?", "answers": [("a", "Nadać temu użytkownikowi dostęp do potrzebnego katalogu", True), ("b", "Przywrócić root bez diagnozy", False), ("c", "Zapisać hasło w ENV", False), ("d", "Usunąć drugi etap budowy", False)]},
            {"text": "Gdzie powinien być token aplikacji?", "answers": [("a", "Poza obrazem, w kontrolowanym mechanizmie sekretów", True), ("b", "W instrukcji ARG obrazu", False), ("c", "W COPY .env", False), ("d", "W tagu obrazu", False)]},
            {"text": "Co oprócz testu endpointu potwierdzi użytkownika procesu?", "answers": [("a", "docker run --rm orders-api:secure id", True), ("b", "docker volume ls", False), ("c", "docker history nginx", False), ("d", "docker network create", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest multi-stage build?", "answer": "Budową obrazu z co najmniej dwóch etapów FROM."},
        {"question": "Po co oddzielać build od runtime?", "answer": "Aby końcowy obraz zawierał tylko elementy potrzebne do działania."},
        {"question": "Co robi COPY --from=build?", "answer": "Kopiuje wybrane pliki z wcześniejszego etapu."},
        {"question": "Co może być artefaktem etapu build Pythona?", "answer": "Środowisko venv z zainstalowanymi zależnościami."},
        {"question": "Jaki warunek dotyczy kopiowanego venv?", "answer": "Etapy powinny mieć zgodnego Pythona i biblioteki systemowe."},
        {"question": "Po co obraz slim?", "answer": "Ogranicza zbędne pakiety w obrazie bazowym."},
        {"question": "Czy slim eliminuje potrzebę aktualizacji?", "answer": "Nie, bazę nadal trzeba utrzymywać."},
        {"question": "Co ustawia USER w Dockerfile?", "answer": "Domyślne konto procesu w kontenerze."},
        {"question": "Dlaczego proces nie powinien działać jako root?", "answer": "Ogranicza skutki błędu lub przejęcia aplikacji."},
        {"question": "Co sprawdzić po zmianie USER?", "answer": "UID procesu, dostęp do plików i działanie endpointu."},
        {"question": "Jak odczytać UID w kontenerze?", "answer": "Uruchomić id przez docker run lub docker exec."},
        {"question": "Co jeśli aplikacja musi zapisywać pliki?", "answer": "Nadać dostęp tylko do potrzebnego katalogu."},
        {"question": "Czy kopiować .env do obrazu?", "answer": "Nie, sekrety powinny pozostać poza obrazem."},
        {"question": "Czy ARG nadaje się na sekret?", "answer": "Nie, może pozostać w historii lub metadanych budowy."},
        {"question": "Czy ENV nadaje się na hasło?", "answer": "Nie, wartość może być odczytana z obrazu."},
        {"question": "Co daje przypięcie digestu bazy?", "answer": "Wskazuje dokładną zawartość obrazu bazowego."},
        {"question": "Po co kontrolować wersje zależności?", "answer": "Aby ograniczyć nieplanowane zmiany przy kolejnej budowie."},
        {"question": "Czego nie przenosić z build?", "answer": "Kompilatorów, cache i tymczasowych plików bez potrzeby."},
        {"question": "Czy mniejszy obraz jest automatycznie bezpieczny?", "answer": "Nie, nadal wymaga poprawnych uprawnień i aktualizacji."},
        {"question": "Co sprawdza Config.User obrazu?", "answer": "Domyślnego użytkownika ustawionego w metadanych."},
        {"question": "Po co nadać plikom właściwego właściciela?", "answer": "Aby aplikacja działała jako użytkownik bez roota."},
        {"question": "Czy root jest konieczny dla Uvicorna na porcie 8000?", "answer": "Nie, port 8000 nie wymaga uprawnień roota."},
        {"question": "Co ogranicza powierzchnię obrazu?", "answer": "Usunięcie zbędnych narzędzi i plików z runtime."},
        {"question": "Po co testować endpoint po zmianie obrazu?", "answer": "Aby wykryć brak zależności lub uprawnień w runtime."},
        {"question": "Co utrzymuje obraz w dobrym stanie po wydaniu?", "answer": "Regularna aktualizacja bazy, zależności i ponowne testy."},
    ],
}
