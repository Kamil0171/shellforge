CONTAINER_LIFECYCLE = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "Cykl życia kontenera i diagnostyka",
        "level": "Średnio zaawansowany",
        "duration": "55 min",
        "description": "Uruchomisz usługę w tle, sprawdzisz jej stan i logi oraz bezpiecznie zakończysz pracę kontenera.",
        "theory": (
            "<code>docker run</code> tworzy nowy kontener i uruchamia jego główny proces. Flaga <code>-d</code> "
            "oddaje terminal i pozostawia proces w tle. Nazwa nadana przez <code>--name</code> ułatwia dalsze "
            "polecenia. <code>docker ps</code> pokazuje działające kontenery, a <code>docker ps -a</code> "
            "również zatrzymane. <code>docker stop</code> wysyła sygnał zakończenia i po czasie może wymusić "
            "zatrzymanie; <code>docker start</code> uruchamia ponownie ten sam kontener, natomiast kolejne "
            "<code>docker run</code> tworzy nowy. Kontener zakończy działanie, gdy skończy się jego główny "
            "proces. Gdy usługa nie odpowiada, najpierw porównaj stan, kod zakończenia i logi. "
            "<code>docker logs</code> czyta standardowe wyjście procesu, <code>docker inspect</code> pokazuje "
            "szczegółowy stan, a <code>docker exec</code> uruchamia pomocnicze polecenie tylko w działającym "
            "kontenerze. Po ćwiczeniu usuń zatrzymany kontener przez <code>docker rm</code>. Nie używaj "
            "<code>docker rm -f</code> jako pierwszej reakcji na awarię, bo stracisz okazję do odczytania logów."
        ),
        "commands": [
            {"command": "docker run -d --name orders-web nginx:1.28", "description": "Tworzy kontener i uruchamia usługę w tle.", "example": "$ docker run -d --name orders-web nginx:1.28"},
            {"command": "docker ps -a", "description": "Pokazuje kontenery działające i zatrzymane.", "example": "$ docker ps -a"},
            {"command": "docker logs --tail 50 orders-web", "description": "Czyta ostatnie 50 linii standardowych logów kontenera.", "example": "$ docker logs --tail 50 orders-web"},
            {"command": "docker inspect --format '{{.State.Status}} {{.State.ExitCode}}' orders-web", "description": "Odczytuje stan i kod zakończenia procesu.", "example": "$ docker inspect --format '{{.State.Status}} {{.State.ExitCode}}' orders-web"},
            {"command": "docker exec orders-web nginx -t", "description": "Sprawdza konfigurację Nginxa wewnątrz działającego kontenera.", "example": "$ docker exec orders-web nginx -t"},
            {"command": "docker stop orders-web", "description": "Kończy pracę kontenera sygnałem zatrzymania.", "example": "$ docker stop orders-web"},
            {"command": "docker start orders-web", "description": "Ponownie uruchamia istniejący kontener.", "example": "$ docker start orders-web"},
            {"command": "docker stop orders-web && docker rm orders-web", "description": "Zatrzymuje i usuwa instancję po ćwiczeniu.", "example": "$ docker stop orders-web\n$ docker rm orders-web"},
        ],
        "practice_task": (
            "Uruchom <code>orders-web</code> w tle. Odczytaj stan, ostatnie logi i wynik <code>nginx -t</code>. "
            "Zatrzymaj kontener, porównaj <code>docker ps</code> z <code>docker ps -a</code>, a następnie "
            "uruchom tę samą instancję przez <code>docker start</code>. Zapisz, czy jej identyfikator się "
            "zmienił. Na końcu zatrzymaj i usuń kontener."
        ),
        "common_mistakes": [
            "Mylenie docker start z docker run i nieświadome tworzenie kolejnych instancji.",
            "Wykonywanie docker exec na zatrzymanym kontenerze.",
            "Usuwanie kontenera przed odczytem stanu i logów awarii.",
            "Zakładanie, że działający kontener automatycznie oznacza działającą aplikację.",
        ],
        "summary": (
            "Cykl pracy obejmuje utworzenie, uruchomienie, zatrzymanie, ponowne uruchomienie i usunięcie "
            "kontenera. Podczas awarii sprawdzaj stan i logi przed zmianami; <code>exec</code> służy do "
            "kontrolowanego sprawdzenia działającej instancji."
        ),
    },
    "quiz": {
        "title": "Quiz: cykl życia kontenera i diagnostyka",
        "description": "Przećwicz wybór poleceń do diagnozowania i zatrzymywania kontenerów.",
        "questions": [
            {"text": "Kontener zniknął z docker ps. Jak sprawdzić, czy zakończył pracę?", "answers": [("a", "Uruchomić docker ps -a i odczytać jego stan", True), ("b", "Od razu usunąć obraz", False), ("c", "Uruchomić docker build", False), ("d", "Zmienić nazwę registry", False)]},
            {"text": "Chcesz uruchomić ponownie tę samą zatrzymaną instancję. Które polecenie wybierzesz?", "answers": [("a", "docker start orders-web", True), ("b", "docker run --name orders-web nginx:1.28", False), ("c", "docker pull nginx:1.28", False), ("d", "docker rm orders-web", False)]},
            {"text": "Gdzie najpierw sprawdzisz komunikaty procesu, który zakończył pracę?", "answers": [("a", "W docker logs orders-web", True), ("b", "W docker images", False), ("c", "W docker network ls", False), ("d", "W docker volume ls", False)]},
            {"text": "Dlaczego docker exec nie działa po zatrzymaniu kontenera?", "answers": [("a", "Wymaga działającej instancji", True), ("b", "Usuwa obraz przed wykonaniem", False), ("c", "Działa wyłącznie w registry", False), ("d", "Zawsze wymaga opublikowanego portu", False)]},
            {"text": "Jak odczytać kod zakończenia kontenera bez zgadywania z samych logów?", "answers": [("a", "Przez docker inspect i pole State.ExitCode", True), ("b", "Przez docker image history", False), ("c", "Przez zmianę tagu obrazu", False), ("d", "Przez docker volume create", False)]},
            {"text": "Co należy zrobić przed docker rm dla działającego kontenera w ćwiczeniu?", "answers": [("a", "Zatrzymać go przez docker stop", True), ("b", "Usunąć wszystkie obrazy", False), ("c", "Skasować registry", False), ("d", "Zmienić główny proces w Dockerfile", False)]},
        ],
    },
    "flashcards": [
        {"question": "Jak docker run wpływa na liczbę instancji?", "answer": "Za każdym wywołaniem tworzy nowy kontener."},
        {"question": "Co zmienia flaga -d?", "answer": "Uruchamia kontener w tle i oddaje terminal."},
        {"question": "Po co używać --name?", "answer": "Aby odwoływać się do kontenera czytelną nazwą."},
        {"question": "Co pokazuje docker ps?", "answer": "Działające kontenery."},
        {"question": "Co dodaje docker ps -a?", "answer": "Również kontenery zatrzymane."},
        {"question": "Co oznacza exited w stanie kontenera?", "answer": "Jego główny proces zakończył działanie."},
        {"question": "Co robi docker stop?", "answer": "Wysyła sygnał zakończenia i zatrzymuje kontener."},
        {"question": "Co robi docker start?", "answer": "Ponownie uruchamia istniejącą instancję."},
        {"question": "Jak powstaje druga instancja obrazu?", "answer": "Przez kolejne docker run z inną nazwą."},
        {"question": "Co robi docker rm?", "answer": "Usuwa istniejący, zatrzymany kontener."},
        {"question": "Kiedy kończy się działanie kontenera?", "answer": "Gdy kończy się jego główny proces."},
        {"question": "Co pokazuje docker logs?", "answer": "Standardowe wyjście i standardowe błędy procesu kontenera."},
        {"question": "Po co opcja --tail przy logach?", "answer": "Ogranicza wynik do ostatnich linii."},
        {"question": "Do czego służy docker inspect?", "answer": "Do odczytu szczegółowych metadanych i stanu kontenera."},
        {"question": "Gdzie znaleźć kod zakończenia?", "answer": "W polu State.ExitCode wyniku docker inspect."},
        {"question": "Co robi docker exec?", "answer": "Uruchamia dodatkowe polecenie w działającym kontenerze."},
        {"question": "Czy docker exec zadziała na exited?", "answer": "Nie, kontener musi działać."},
        {"question": "Jak sprawdzić konfigurację Nginxa w kontenerze?", "answer": "Poleceniem docker exec orders-web nginx -t."},
        {"question": "Czy docker start zmienia ID kontenera?", "answer": "Nie, uruchamia ponownie tę samą instancję."},
        {"question": "Czy docker run użyje starego ID?", "answer": "Nie, tworzy nową instancję."},
        {"question": "Od czego zacząć diagnozę awarii?", "answer": "Od stanu, kodu zakończenia i logów kontenera."},
        {"question": "Dlaczego nie usuwać kontenera od razu po awarii?", "answer": "Można utracić dane potrzebne do diagnozy."},
        {"question": "Czy stan running gwarantuje zdrową aplikację?", "answer": "Nie, trzeba sprawdzić działanie usługi."},
        {"question": "Po co docker stop przed docker rm?", "answer": "Aby zakończyć proces przed usunięciem instancji."},
        {"question": "Kiedy użyć docker rm -f?", "answer": "Tylko świadomie, gdy zwykłe zatrzymanie nie wystarcza i zabezpieczono diagnostykę."},
    ],
}
