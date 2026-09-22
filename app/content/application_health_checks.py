APPLICATION_HEALTH_CHECKS = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Health checki i gotowość aplikacji",
        "level": "Średnio zaawansowany",
        "duration": "55 min",
        "description": "Odróżnisz działający proces od gotowej usługi i sprawdzisz endpoint /health z limitem czasu.",
        "theory": (
            "Aktywny proces systemd nie gwarantuje, że aplikacja odpowiada na żądania. Health check "
            "wykonuje konkretne sprawdzenie, na przykład żądanie do <code>/health</code>, i ocenia kod HTTP "
            "oraz czas odpowiedzi. Liveness odpowiada na pytanie, czy proces nadal działa poprawnie i "
            "wymaga ewentualnego restartu. Readiness mówi, czy instancja może przyjmować ruch; może "
            "uwzględniać połączenie z bazą, ale nie powinna wykonywać kosztownych operacji. Brak gotowości "
            "nie zawsze oznacza konieczność restartu. Zależności mogą być chwilowo niedostępne, dlatego "
            "wynik trzeba interpretować razem z logami i stanem bazy. Kod 200 zwykle oznacza pozytywny "
            "wynik, a 503 brak gotowości. Sama strona główna 200 nie dowodzi działania ważnych funkcji. "
            "Ustaw krótki timeout, aby zawieszony endpoint nie blokował sprawdzania. Ograniczona liczba "
            "ponowień zmniejsza wpływ pojedynczego błędu sieci, lecz nie może ukrywać długiej awarii. "
            "Endpoint nie powinien ujawniać sekretów ani szczegółów infrastruktury."
        ),
        "commands": [
            {"command": "systemctl status orders-api --no-pager", "description": "Sprawdza stan procesu, ale nie zastępuje testu HTTP.", "example": "$ systemctl status orders-api --no-pager"},
            {"command": "curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/health", "description": "Odczytuje kod odpowiedzi endpointu zdrowia.", "example": "$ curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/health\n200"},
            {"command": "curl --fail --max-time 2 http://127.0.0.1:8000/health", "description": "Zwraca błąd dla niepowodzenia HTTP i ogranicza czas oczekiwania.", "example": "$ curl --fail --max-time 2 http://127.0.0.1:8000/health"},
            {"command": "curl --fail --max-time 2 --retry 2 --retry-delay 1 http://127.0.0.1:8000/health", "description": "Ponawia krótkotrwały błąd najwyżej dwa razy.", "example": "$ curl --fail --max-time 2 --retry 2 --retry-delay 1 http://127.0.0.1:8000/health"},
            {"command": "journalctl -u orders-api -n 30 --no-pager", "description": "Łączy wynik health checku z ostatnimi logami usługi.", "example": "$ journalctl -u orders-api -n 30 --no-pager"},
            {"command": "ss -lntp | grep ':8000'", "description": "Sprawdza nasłuch portu aplikacji.", "example": "$ ss -lntp | grep ':8000'"},
        ],
        "practice_task": (
            "Dla ćwiczeniowego <code>orders-api</code> przygotuj kontrakt <code>/health</code>: kod 200, "
            "gdy instancja może obsługiwać ruch, i 503 przy braku krytycznej zależności. Opisz osobno "
            "prosty test liveness i readiness. Sprawdź proces, port oraz żądanie HTTP z timeoutem. "
            "Zasymuluj niedostępność testowej bazy i zapisz, dlaczego aktywny systemd nie wystarcza "
            "do uznania usługi za gotową."
        ),
        "common_mistakes": [
            "Traktowanie systemctl active jako dowodu poprawnej odpowiedzi aplikacji.",
            "Łączenie liveness z każdą chwilową awarią zależności i wywoływanie pętli restartów.",
            "Brak timeoutu, przez co sprawdzenie może się zawiesić.",
            "Nieograniczone ponawianie, które opóźnia wykrycie trwałej awarii.",
            "Zwracanie haseł lub szczegółów połączenia w publicznym endpointcie.",
        ],
        "summary": (
            "Health check ocenia zachowanie aplikacji, a nie tylko jej proces. Liveness pomaga wykryć "
            "instancję wymagającą restartu, readiness określa gotowość do ruchu. Kod HTTP, timeout "
            "i ograniczone ponowienia tworzą użyteczny sygnał do monitoringu."
        ),
    },
    "quiz": {
        "title": "Quiz: health checki i gotowość aplikacji",
        "description": "Sprawdź decyzje dotyczące stanu procesu, gotowości i zależności.",
        "questions": [
            {"text": "systemctl pokazuje active, ale /health zwraca 503. Co to oznacza?", "answers": [("a", "Proces działa, lecz aplikacja nie jest gotowa do obsługi ruchu", True), ("b", "Usługa jest na pewno zdrowa", False), ("c", "Port 8000 musi być zamknięty", False), ("d", "Każdy klient otrzymuje 200", False)]},
            {"text": "Baza chwilowo nie odpowiada. Który sygnał powinien przede wszystkim zmienić stan?", "answers": [("a", "Readiness zależne od bazy", True), ("b", "Liveness wymuszające stałe restarty", False), ("c", "Wersja obrazu", False), ("d", "Nazwa jednostki systemd", False)]},
            {"text": "Dlaczego health check potrzebuje timeoutu?", "answers": [("a", "Aby zawieszona odpowiedź nie blokowała oceny stanu bez końca", True), ("b", "Aby wyłączyć logi", False), ("c", "Aby usunąć bazę", False), ("d", "Aby zawsze zwrócić 200", False)]},
            {"text": "Co najlepiej potwierdza gotowość HTTP na porcie lokalnym?", "answers": [("a", "Żądanie curl do /health i kontrola kodu", True), ("b", "Samo docker images", False), ("c", "Sam odczyt PID", False), ("d", "Wyłącznie uptime hosta", False)]},
            {"text": "Po co ograniczyć liczbę retry?", "answers": [("a", "Aby odfiltrować krótką usterkę bez ukrycia dłuższej awarii", True), ("b", "Aby zastąpić diagnozę logów", False), ("c", "Aby zmienić adres usługi", False), ("d", "Aby ominąć każdy błąd HTTP", False)]},
            {"text": "Jaka odpowiedź endpointu zdrowia jest niewłaściwa?", "answers": [("a", "Treść ujawniająca hasło do bazy", True), ("b", "Kod 503 przy braku gotowości", False), ("c", "Zwięzła odpowiedź bez sekretów", False), ("d", "Kod 200 dla gotowej instancji", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest health check?", "answer": "Konkretnym testem stanu usługi lub aplikacji."},
        {"question": "Co sprawdza liveness?", "answer": "Czy instancja działa na tyle poprawnie, by nie wymagać restartu."},
        {"question": "Co sprawdza readiness?", "answer": "Czy instancja może teraz przyjmować ruch."},
        {"question": "Czy brak gotowości zawsze oznacza restart?", "answer": "Nie, przyczyną może być chwilowa awaria zależności."},
        {"question": "Czy aktywny systemd dowodzi zdrowia aplikacji?", "answer": "Nie, potwierdza głównie stan procesu."},
        {"question": "Co sprawdza endpoint /health?", "answer": "Stan określony kontraktem aplikacji, oceniany po kodzie HTTP."},
        {"question": "Jaki kod może oznaczać gotowość?", "answer": "200, gdy kontrakt endpointu tak stanowi."},
        {"question": "Jaki kod może oznaczać brak gotowości?", "answer": "503 Service Unavailable."},
        {"question": "Czy 200 ze strony głównej wystarcza?", "answer": "Nie, ważne funkcje i zależności mogą nadal nie działać."},
        {"question": "Po co timeout w health checku?", "answer": "Ogranicza czas oczekiwania na zawieszoną usługę."},
        {"question": "Po co ograniczone retry?", "answer": "Zmniejsza wpływ pojedynczego błędu bez ukrywania awarii."},
        {"question": "Co robi curl --fail?", "answer": "Zwraca błąd procesu przy odpowiedzi HTTP 4xx lub 5xx."},
        {"question": "Co robi curl --max-time 2?", "answer": "Ogranicza całe żądanie do około dwóch sekund."},
        {"question": "Co pokazuje format %{http_code}?", "answer": "Kod odpowiedzi HTTP."},
        {"question": "Co sprawdza ss -lntp?", "answer": "Procesy nasłuchujące na portach TCP."},
        {"question": "Co dodać do oceny po błędzie /health?", "answer": "Logi aplikacji, zależności i stan portu."},
        {"question": "Czy liveness powinien zależeć od każdej bazy?", "answer": "Nie, chwilowy brak bazy nie powinien wywoływać pętli restartów."},
        {"question": "Czy readiness może sprawdzać krytyczną zależność?", "answer": "Tak, gdy bez niej aplikacja nie obsłuży ruchu."},
        {"question": "Dlaczego health check ma być lekki?", "answer": "Jest wykonywany często i nie powinien obciążać usługi."},
        {"question": "Czego nie ujawniać przez /health?", "answer": "Sekretów i szczegółów prywatnej infrastruktury."},
        {"question": "Co oznacza nasłuch portu bez odpowiedzi HTTP?", "answer": "Proces może działać, lecz ścieżka aplikacyjna nadal zawodzić."},
        {"question": "Jak sprawdzić ostatnie logi jednostki?", "answer": "journalctl -u orders-api -n 30 --no-pager."},
        {"question": "Co odróżnia proces running od gotowości?", "answer": "Gotowość wymaga rzeczywistej zdolności obsługi żądań."},
        {"question": "Kiedy wynik zależności ma znaczenie?", "answer": "Gdy aplikacja nie może bez niej obsłużyć ważnej funkcji."},
        {"question": "Co zapisać w kontrakcie health checku?", "answer": "Zakres testu, kody odpowiedzi i limit czasu."},
    ],
}
