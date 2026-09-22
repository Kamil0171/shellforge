OPERATIONS_RUNBOOK = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Runbook i utrzymanie po wdrożeniu",
        "level": "Średnio zaawansowany",
        "duration": "65 min",
        "description": "Złożysz powtarzalną procedurę kontroli wdrożenia, reagowania i przekazania dyżuru.",
        "theory": (
            "Runbook to krótka instrukcja dla operatora, który musi działać pod presją i może nie znać "
            "historii usługi. Zapisz cel procedury, warunki uruchomienia, właściciela, wymagany dostęp, "
            "ryzyka, konkretne polecenia, oczekiwane wyniki oraz punkt decyzji o eskalacji. Po wdrożeniu "
            "sprawdź wersję aplikacji, <code>/health</code>, ważny endpoint, błędy, opóźnienia i stan "
            "zależności. Obserwuj ustalone okno, bo pierwszy udany request nie wyklucza późnej regresji. "
            "Dla zmiany zaplanuj okno serwisowe, komunikację i warunki cofnięcia. Rollback kodu nie zawsze "
            "cofa migrację danych; przed działaniem sprawdź zgodność schematu i dostępność kopii. "
            "W części incydentowej ułóż sekwencję: potwierdź objaw, określ wpływ, zbierz logi i metryki, "
            "zweryfikuj zależności, postaw i sprawdź hipotezę, wykonaj bezpieczną naprawę, a potem "
            "potwierdź zdrowie usługi. Dodaj kontakty i sposób przekazania dyżuru bez ujawniania "
            "sekretów w dokumencie. Po incydencie zanotuj oś czasu, przyczynę, działania, wpływ, "
            "wynik i zadania zapobiegawcze; opisuj mechanizmy, nie przypisuj winy. Procedura jest "
            "aktualna tylko wtedy, gdy zespół ćwiczy ją na danych testowych i poprawia po zmianach systemu."
        ),
        "commands": [
            {"command": "systemctl status orders-api --no-pager", "description": "Weryfikuje proces aplikacji po wdrożeniu.", "example": "$ systemctl status orders-api --no-pager"},
            {"command": "curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' http://127.0.0.1:8000/health", "description": "Sprawdza kod i czas odpowiedzi endpointu health.", "example": "$ curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' http://127.0.0.1:8000/health"},
            {"command": "journalctl -u orders-api --since '10 minutes ago' --no-pager", "description": "Czyta logi z okna po zmianie.", "example": "$ journalctl -u orders-api --since '10 minutes ago' --no-pager"},
            {"command": "docker compose ps app-db", "description": "Sprawdza stan zależnej bazy w ćwiczeniowym środowisku.", "example": "$ docker compose ps app-db"},
            {"command": "df -h /var", "description": "Sprawdza wolne miejsce dla logów i danych.", "example": "$ df -h /var"},
            {"command": "date --iso-8601=seconds", "description": "Zapisuje czas obserwacji albo przekazania dyżuru.", "example": "$ date --iso-8601=seconds"},
        ],
        "practice_task": (
            "Napisz jednostronicowy runbook dla fikcyjnego wdrożenia <code>orders-api</code>. Uwzględnij "
            "warunki startu, właściciela, okno zmiany, kontrolę wersji i health, dwa sygnały aplikacji, "
            "sprawdzenie <code>app-db</code>, próg decyzji o cofnięciu, zgodność schematu, komunikację "
            "oraz końcowy zapis wyniku. Przećwicz na danych testowych wariant alertu 5xx po zmianie: "
            "zapisz oś czasu i hipotezy, wybierz test, opisz działanie i warunki zamknięcia. Dodaj "
            "krótką notatkę przekazania dyżuru i jedno zadanie zapobiegawcze."
        ),
        "common_mistakes": [
            "Lista poleceń bez oczekiwanych wyników i punktów decyzji.",
            "Brak właściciela incydentu lub kontaktu do eskalacji.",
            "Założenie, że rollback obrazu automatycznie cofa migrację bazy.",
            "Zakończenie wdrożenia po jednym HTTP 200 bez obserwacji trendu błędów.",
            "Wpisanie sekretów do runbooka lub notatki z incydentu.",
        ],
        "summary": (
            "Dobry runbook prowadzi od warunków startu przez kontrole i decyzje do weryfikacji oraz "
            "przekazania wyniku. Łączy wiedzę o health, logach, metrykach, zależnościach, backupie "
            "i odtwarzaniu. Regularne ćwiczenie utrzymuje procedurę użyteczną."
        ),
    },
    "quiz": {
        "title": "Quiz: runbook i utrzymanie po wdrożeniu",
        "description": "Podejmij praktyczne decyzje podczas kontroli zmiany i incydentu.",
        "questions": [
            {"text": "Runbook mówi tylko «sprawdź logi». Czego brakuje operatorowi?", "answers": [("a", "Zakresu czasu, polecenia, oczekiwanego wyniku i dalszej decyzji", True), ("b", "Koloru terminala", False), ("c", "Liczby plików CSS", False), ("d", "Nazwy przeglądarki autora", False)]},
            {"text": "Po wdrożeniu /health zwraca 200, ale rośnie odsetek 5xx na endpointach biznesowych. Co zrobisz?", "answers": [("a", "Uznaję zmianę za podejrzaną, badam wpływ i stosuję warunek cofnięcia", True), ("b", "Zamykam kontrolę, bo health wystarcza", False), ("c", "Usuwam logi", False), ("d", "Ignoruję metrykę do jutra", False)]},
            {"text": "Kiedy sam rollback obrazu może nie wystarczyć?", "answers": [("a", "Gdy wdrożenie zmieniło schemat bazy niezgodnie ze starą wersją", True), ("b", "Gdy kod ma numer wersji", False), ("c", "Gdy działa Nginx", False), ("d", "Gdy zapisano godzinę zmiany", False)]},
            {"text": "Co powinno znaleźć się w przekazaniu dyżuru po incydencie?", "answers": [("a", "Stan usługi, wykonane działania, ryzyka i następne kroki", True), ("b", "Prywatne hasła operatora", False), ("c", "Wyłącznie nazwa hosta", False), ("d", "Tylko zrzut ekranu alertu", False)]},
            {"text": "Po naprawie alert ucichł. Jaki warunek zamknięcia jest rozsądny?", "answers": [("a", "Potwierdzone działanie ważnej funkcji oraz stabilne błędy i opóźnienia w ustalonym oknie", True), ("b", "Samo zniknięcie powiadomienia", False), ("c", "Restart komputera operatora", False), ("d", "Usunięcie historycznych metryk", False)]},
            {"text": "Jak ulepszyć runbook po ćwiczeniu, w którym operator nie znał celu jednej komendy?", "answers": [("a", "Dopisać znaczenie, oczekiwany wynik i decyzję po wyniku", True), ("b", "Dopisać hasło produkcyjne", False), ("c", "Usunąć wszystkie kroki", False), ("d", "Zastąpić procedurę losowym restartem", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest runbook?", "answer": "Powtarzalną instrukcją operacyjną z testami, wynikami i decyzjami."},
        {"question": "Kiedy uruchomić procedurę?", "answer": "Gdy spełniony jest zapisany warunek, na przykład alert lub wdrożenie."},
        {"question": "Po co właściciel w runbooku?", "answer": "Wiadomo, kto prowadzi działanie i podejmuje decyzje."},
        {"question": "Co zapisać przy poleceniu?", "answer": "Cel, oczekiwany wynik i następny krok dla wyniku poprawnego lub błędu."},
        {"question": "Po co okno zmiany?", "answer": "Ustala czas wdrożenia, obserwacji i komunikacji."},
        {"question": "Co sprawdzić przed wdrożeniem?", "answer": "Stan wyjściowy, kopię danych, zgodność schematu i plan cofnięcia."},
        {"question": "Co sprawdzić zaraz po wdrożeniu?", "answer": "Wersję, health, kluczowy endpoint i stan zależności."},
        {"question": "Dlaczego obserwować nowe okno metryk?", "answer": "Późne błędy mogą ujawnić się po pierwszym udanym żądaniu."},
        {"question": "Co oznacza warunek rollbacku?", "answer": "Zapisany próg objawu lub wpływu, po którym rozważa się cofnięcie zmiany."},
        {"question": "Czy rollback kodu cofa migrację?", "answer": "Nie, zgodność starej wersji ze schematem trzeba sprawdzić osobno."},
        {"question": "Po co plan komunikacji?", "answer": "Użytkownicy i dyżur wiedzą o wpływie, decyzjach i stanie usługi."},
        {"question": "Co zapisać w osi czasu incydentu?", "answer": "Czas alertu, testów, zmian, naprawy i weryfikacji."},
        {"question": "Co odróżnia objaw od przyczyny?", "answer": "Objaw jest skutkiem widocznym w usłudze, przyczyna wyjaśnia mechanizm awarii."},
        {"question": "Po co w runbooku punkt eskalacji?", "answer": "Określa, kiedy i komu przekazać problem przekraczający kompetencje lub czas."},
        {"question": "Co sprawdzić przy awarii zależności?", "answer": "Jej stan, logi, gotowość i połączenie z aplikacji."},
        {"question": "Czy HTTP 200 z /health kończy diagnozę?", "answer": "Nie, trzeba sprawdzić ważną funkcję i trend błędów."},
        {"question": "Co przekazać następnej zmianie?", "answer": "Bieżący stan, wykonane testy, ryzyka i następne działania."},
        {"question": "Gdzie trzymać hasła do procedury?", "answer": "W chronionym mechanizmie sekretów, nie w treści runbooka."},
        {"question": "Po co notatka po incydencie?", "answer": "Pozwala odtworzyć przebieg i zaplanować usprawnienia."},
        {"question": "Jak pisać o przyczynie po incydencie?", "answer": "Opisywać mechanizm i dowody bez przypisywania winy osobom."},
        {"question": "Co daje ćwiczenie runbooka?", "answer": "Wykrywa brakujące kroki, uprawnienia i błędne założenia."},
        {"question": "Kiedy aktualizować runbook?", "answer": "Po zmianie systemu, incydencie lub nieudanym ćwiczeniu."},
        {"question": "Jak sprawdzić skuteczność naprawy?", "answer": "Porównać health, funkcję użytkownika, błędy i opóźnienia po zmianie."},
        {"question": "Co powinno być wynikiem procedury?", "answer": "Jednoznaczny stan usługi, zapis decyzji i odpowiedzialność za dalsze kroki."},
        {"question": "Jaki jest ostatni krok ścieżki nauki?", "answer": "Połączenie monitoringu, diagnozy i ochrony danych w sprawdzony runbook."},
    ],
}
