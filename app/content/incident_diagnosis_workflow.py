INCIDENT_DIAGNOSIS_WORKFLOW = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Diagnoza incydentu: od alertu do weryfikacji",
        "level": "Średnio zaawansowany",
        "duration": "70 min",
        "description": "Przejdziesz od alertu 5xx do potwierdzenia przyczyny, naprawy i testu końcowego.",
        "theory": (
            "Incydent zaczyna się od objawu, nie od zgadywania komendy naprawczej. Po alertcie "
            "potwierdź aktualny wynik <code>/health</code> oraz zakres wpływu: wszystkie żądania "
            "czy tylko jedno API, jeden host czy wiele instancji. Zapisz czas początku i ostatnią "
            "zmianę. Potem czytaj logi <code>orders-api</code> z tego okna oraz metryki błędów, "
            "opóźnień i zasobów. Komunikat o połączeniu z bazą wymaga weryfikacji <code>app-db</code>, "
            "jej logów, sieci i puli połączeń. Nie zakładaj, że restart aplikacji naprawi awarię "
            "zależności. Oddziel hipotezę od potwierdzonej przyczyny i zapisuj wyniki kolejnych testów. "
            "Naprawę wybierz zgodnie z runbookiem: może nią być korekta konfiguracji, przywrócenie "
            "zależności lub rollback ostatniej zmiany. Po działaniu sprawdź health, ważny endpoint, "
            "błędy i opóźnienia w nowym oknie oraz stabilność przez ustalony czas. Zamknięcie alertu "
            "bez weryfikacji użytkownika nie kończy incydentu. Ten schemat jest zgodny z praktyką "
            "Symulatora Dynamic Incident: objaw → zakres → dowody → przyczyna → naprawa → kontrola."
        ),
        "commands": [
            {"command": "date --iso-8601=seconds", "description": "Zapisuje czas rozpoczęcia diagnozy.", "example": "$ date --iso-8601=seconds"},
            {"command": "curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' http://127.0.0.1:8000/health", "description": "Potwierdza aktualny objaw i czas odpowiedzi.", "example": "$ curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' http://127.0.0.1:8000/health"},
            {"command": "journalctl -u orders-api --since '15 minutes ago' --no-pager", "description": "Czyta logi aplikacji z czasu incydentu.", "example": "$ journalctl -u orders-api --since '15 minutes ago' --no-pager"},
            {"command": "systemctl status orders-api --no-pager", "description": "Sprawdza stan procesu osobno od stanu aplikacji.", "example": "$ systemctl status orders-api --no-pager"},
            {"command": "docker compose ps app-db", "description": "Sprawdza stan zależnej bazy uruchomionej w ćwiczeniowym Compose.", "example": "$ docker compose ps app-db"},
            {"command": "docker compose exec app-db pg_isready -U orders -d orders", "description": "Weryfikuje gotowość bazy po hipotezie o zależności.", "example": "$ docker compose exec app-db pg_isready -U orders -d orders"},
            {"command": "df -h /var", "description": "Sprawdza miejsce, gdy logi sugerują błąd zapisu.", "example": "$ df -h /var"},
        ],
        "practice_task": (
            "Załóż alert 5xx dla <code>orders-api</code>, odpowiedź 503 z <code>/health</code> i log "
            "połączenia z <code>app-db</code>. Poprowadź notatkę w ośmiu krokach: alert, health, "
            "zakres, logi, metryki, zależności, naprawa, weryfikacja. Dla każdej hipotezy podaj "
            "jeden test. Zanim zaproponujesz restart albo rollback, zapisz dowód przyczyny. "
            "Po ćwiczeniowej naprawie sprawdź ważny endpoint oraz trend 5xx w kolejnym oknie."
        ),
        "common_mistakes": [
            "Restartowanie usługi bez ustalenia, czy awaria dotyczy zależnej bazy.",
            "Czytanie logów z innej godziny niż czas alertu.",
            "Uznawanie jednej hipotezy za przyczynę bez testu potwierdzającego.",
            "Naprawianie tylko jednego hosta przy problemie obejmującym cały ruch.",
            "Zamykanie incydentu bez testu funkcji i obserwacji błędów po zmianie.",
        ],
        "summary": (
            "Skuteczna diagnoza przechodzi od wpływu na użytkownika do zawężania przyczyny. "
            "Łącz health, logi, metryki, systemd, sieć i zależności, a naprawę wykonuj po teście "
            "hipotezy. Zakończ dopiero po weryfikacji działania i stabilności."
        ),
    },
    "quiz": {
        "title": "Quiz: diagnoza incydentu od alertu do weryfikacji",
        "description": "Wybierz następny test i warunek zamknięcia incydentu.",
        "questions": [
            {"text": "Otrzymujesz alert 5xx dla orders-api. Co sprawdzisz jako pierwsze?", "answers": [("a", "Aktualny health i zakres wpływu na żądania", True), ("b", "Losowo zrestartujesz bazę", False), ("c", "Usuniesz stare logi", False), ("d", "Zmienisz tag obrazu bez diagnozy", False)]},
            {"text": "Log aplikacji wskazuje błąd połączenia z app-db. Co jest następnym testem?", "answers": [("a", "Stan i gotowość bazy oraz łączność z nią", True), ("b", "Kolor alertu", False), ("c", "Wersja edytora", False), ("d", "Liczba fiszek w aplikacji", False)]},
            {"text": "Tylko jedno API zwraca błędy, reszta działa. Co to mówi o zakresie?", "answers": [("a", "Problem może być ograniczony do tej funkcji lub jej zależności", True), ("b", "Cała infrastruktura musi być wyłączona", False), ("c", "Nie ma incydentu", False), ("d", "Nie trzeba sprawdzać logów", False)]},
            {"text": "Dlaczego restart bez potwierdzonej przyczyny jest ryzykowny?", "answers": [("a", "Może ukryć objaw, nie usuwając źródła awarii", True), ("b", "Zawsze odtwarza backup", False), ("c", "Automatycznie aktualizuje SLO", False), ("d", "Zmienia wszystkie rekordy DNS", False)]},
            {"text": "Po naprawie /health ma 200. Czy incydent można zamknąć natychmiast?", "answers": [("a", "Nie, sprawdź ważną funkcję, błędy i stabilność w nowym oknie", True), ("b", "Tak, żadne inne testy nie mają znaczenia", False), ("c", "Tak, jeśli skasowano logi", False), ("d", "Tak, gdy host ma niski CPU", False)]},
            {"text": "Co odróżnia hipotezę od potwierdzonej przyczyny?", "answers": [("a", "Wynik testu zgodny z objawem i mechanizmem awarii", True), ("b", "Przekonanie operatora bez danych", False), ("c", "Sama nazwa alertu", False), ("d", "Liczba wykonanych restartów", False)]},
        ],
    },
    "flashcards": [
        {"question": "Od czego zaczyna się diagnoza incydentu?", "answer": "Od potwierdzenia objawu i wpływu na użytkownika."},
        {"question": "Po co określać scope incydentu?", "answer": "Aby wiedzieć, które funkcje, hosty i użytkownicy są dotknięci."},
        {"question": "Co zapisać na początku?", "answer": "Czas alertu, obserwowany objaw i ostatnie zmiany."},
        {"question": "Co daje test /health?", "answer": "Bieżącą ocenę stanu według kontraktu aplikacji."},
        {"question": "Czy aktywny systemd wyklucza incydent?", "answer": "Nie, proces może działać, gdy API zwraca błędy."},
        {"question": "Po co czytać logi w oknie alertu?", "answer": "Łączy zdarzenia z właściwym czasem awarii."},
        {"question": "Która metryka pokazuje skalę błędów?", "answer": "Odsetek lub tempo odpowiedzi 5xx."},
        {"question": "Która metryka pokazuje wolne żądania?", "answer": "Rozkład czasu odpowiedzi, na przykład p95."},
        {"question": "Co sprawdzić przy błędzie app-db?", "answer": "Gotowość bazy, logi, połączenia i sieć."},
        {"question": "Czy hipoteza jest przyczyną?", "answer": "Nie, wymaga testu potwierdzającego."},
        {"question": "Po co zapisywać wynik testu?", "answer": "Ułatwia odrzucenie błędnych hipotez i przekazanie dyżuru."},
        {"question": "Kiedy rozważyć rollback?", "answer": "Gdy dowody łączą incydent z ostatnią zmianą i plan go przewiduje."},
        {"question": "Czy restart bazy jest pierwszym krokiem?", "answer": "Nie, najpierw trzeba potwierdzić przyczynę i wpływ."},
        {"question": "Co jeśli tylko jeden endpoint zawodzi?", "answer": "Zawęzić diagnozę do jego kodu i zależności."},
        {"question": "Co jeśli wiele usług zawodzi jednocześnie?", "answer": "Sprawdzić wspólną zależność lub warstwę sieciową."},
        {"question": "Po co df -h przy błędzie zapisu?", "answer": "Pozwala potwierdzić brak miejsca na systemie plików."},
        {"question": "Co oznacza repair w procedurze?", "answer": "Kontrolowane działanie usuwające potwierdzoną przyczynę."},
        {"question": "Co sprawdzić po naprawie?", "answer": "Health, kluczową funkcję, błędy i opóźnienia."},
        {"question": "Po co obserwować nowe okno po naprawie?", "answer": "Aby potwierdzić trwałość rozwiązania."},
        {"question": "Czy zamknięcie alertu kończy incydent?", "answer": "Nie, potrzebna jest weryfikacja usługi."},
        {"question": "Co powinny zawierać notatki incydentu?", "answer": "Czas, zakres, hipotezy, testy, działania i wynik."},
        {"question": "Po co sprawdzać ostatnie wdrożenie?", "answer": "Regresja mogła pojawić się po zmianie kodu lub konfiguracji."},
        {"question": "Jak łączyć logi i metryki?", "answer": "Wspólnym oknem czasu, usługą i objawem."},
        {"question": "Co zrobić przed ryzykowną naprawą?", "answer": "Ocenić skutki, przygotować cofnięcie i powiadomić właściwe osoby."},
        {"question": "Jaki jest ostatni krok workflow?", "answer": "Weryfikacja działania i udokumentowanie wyniku."},
    ],
}
