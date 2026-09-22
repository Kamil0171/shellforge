SERVICE_APPLICATION_LOGS = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Logi usług i aplikacji",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": "Wyfiltrujesz zdarzenia z journalu i logów aplikacji, zachowując czas, kontekst i prywatność.",
        "theory": (
            "Log usługi powinien odpowiadać na pytania: kiedy, w którym komponencie, na jakim poziomie "
            "i co się stało. <code>journalctl -u orders-api</code> filtruje jednostkę systemd, "
            "<code>-n</code> ogranicza liczbę wpisów, <code>--since</code> wybiera okno czasu, a "
            "<code>-p</code> filtruje priorytet. Poziom warning nie oznacza automatycznie awarii, a "
            "brak error nie dowodzi poprawności działania. Znacznik czasu ma znaczenie przy łączeniu "
            "logów aplikacji, Nginxa i kontenera bazy. Aplikacja może pisać na stdout, który przejmuje "
            "systemd lub runtime kontenera. Ustrukturyzowany log to zestaw pól, na przykład time, "
            "level, service i request_id; ułatwia filtrowanie, ale nie wymaga wdrożenia nowej platformy "
            "logowej. Identyfikator żądania pomaga skleić zdarzenia z kilku komponentów. "
            "<code>tail</code> i <code>grep</code> przydają się dla zwykłych plików. Logi mogą zawierać "
            "dane wrażliwe; nie zapisuj haseł i pełnych tokenów. Retencja i rotacja ograniczają "
            "rozmiar magazynu, a usuwanie logów podczas incydentu bez kopii utrudnia dochodzenie."
        ),
        "commands": [
            {"command": "journalctl -u orders-api -n 50 --no-pager", "description": "Czyta ostatnie wpisy jednostki.", "example": "$ journalctl -u orders-api -n 50 --no-pager"},
            {"command": "journalctl -u orders-api --since '2026-09-18 14:00:00' --until '2026-09-18 14:15:00' --no-pager", "description": "Zawęża logi do czasu incydentu.", "example": "$ journalctl -u orders-api --since '2026-09-18 14:00:00' --until '2026-09-18 14:15:00' --no-pager"},
            {"command": "journalctl -u orders-api -p warning --since '1 hour ago' --no-pager", "description": "Pokazuje wpisy od poziomu warning wzwyż w ostatniej godzinie.", "example": "$ journalctl -u orders-api -p warning --since '1 hour ago' --no-pager"},
            {"command": "journalctl -u orders-api -o json --since '10 minutes ago' --no-pager", "description": "Wyświetla wpisy journalu jako rekordy JSON.", "example": "$ journalctl -u orders-api -o json --since '10 minutes ago' --no-pager"},
            {"command": "tail -n 50 /var/log/nginx/error.log", "description": "Czyta końcówkę logu błędów proxy.", "example": "$ tail -n 50 /var/log/nginx/error.log"},
            {"command": "grep 'request_id=ord-42' /var/log/orders-api/app.log", "description": "Wyszukuje zdarzenia jednego żądania, jeśli aplikacja zapisuje to pole.", "example": "$ grep 'request_id=ord-42' /var/log/orders-api/app.log"},
            {"command": "journalctl --disk-usage", "description": "Sprawdza miejsce zajmowane przez journal przed zmianą retencji.", "example": "$ journalctl --disk-usage"},
        ],
        "practice_task": (
            "Dla incydentu <code>orders-api</code> w przedziale 14:00–14:15 zbierz wpisy jednostki "
            "oraz końcówkę logu Nginxa. Oddziel ostrzeżenia od błędów, sprawdź strefę czasu i "
            "wyszukaj ćwiczeniowy <code>request_id=ord-42</code>, jeśli jest zapisywany. Zaprojektuj "
            "jedną krótką linię logu z polami time, level, service, request_id i message bez "
            "sekretów. Sprawdź rozmiar journalu i zaproponuj rozsądną retencję bez kasowania dowodów."
        ),
        "common_mistakes": [
            "Czytanie wszystkich logów bez ograniczenia czasu i usługi.",
            "Zakładanie, że każdy warning oznacza awarię użytkownika.",
            "Mieszanie czasów z różnych stref podczas budowania osi incydentu.",
            "Logowanie haseł, tokenów i pełnych danych klientów.",
            "Usuwanie logów przed zapisaniem materiału potrzebnego do diagnozy.",
        ],
        "summary": (
            "Filtruj logi po usłudze, czasie i priorytecie, a zdarzenia łącz przez request ID. "
            "Ustrukturyzowane pola ułatwiają diagnostykę. Retencję dobieraj świadomie, chroniąc "
            "zarówno przestrzeń dyskową, jak i dane wrażliwe."
        ),
    },
    "quiz": {
        "title": "Quiz: logi usług i aplikacji",
        "description": "Sprawdź filtrowanie zdarzeń i interpretację poziomów logu.",
        "questions": [
            {"text": "Awaria trwała od 14:00 do 14:15. Jak najczytelniej ograniczyć journal?", "answers": [("a", "Po jednostce oraz --since i --until", True), ("b", "Wyświetlić cały journal od startu hosta", False), ("c", "Sprawdzić tylko docker images", False), ("d", "Usunąć stare logi przed odczytem", False)]},
            {"text": "Chcesz zobaczyć ostatnie 50 wpisów orders-api. Które polecenie pasuje?", "answers": [("a", "journalctl -u orders-api -n 50", True), ("b", "journalctl --disk-usage", False), ("c", "docker volume ls", False), ("d", "pg_dump -Fc", False)]},
            {"text": "Po co pole request_id w logu aplikacji?", "answers": [("a", "Aby powiązać wpisy dotyczące jednego żądania", True), ("b", "Aby zastąpić kopię bazy", False), ("c", "Aby automatycznie zwiększyć pamięć", False), ("d", "Aby ukryć wszystkie błędy", False)]},
            {"text": "W logu widzisz warning, ale ruch działa. Jaki wniosek jest poprawny?", "answers": [("a", "Trzeba ocenić kontekst i wpływ, sam poziom nie dowodzi awarii", True), ("b", "Każdy warning wymaga rollbacku", False), ("c", "Należy natychmiast usunąć log", False), ("d", "Health check nie ma znaczenia", False)]},
            {"text": "Co grozi przy logowaniu pełnego tokenu dostępu?", "answers": [("a", "Ujawnienie poświadczenia osobom mającym dostęp do logów", True), ("b", "Automatyczne szyfrowanie tokenu", False), ("c", "Zmiana portu usługi", False), ("d", "Zniknięcie wpisów z journalu", False)]},
            {"text": "Dlaczego przed zmianą retencji warto sprawdzić journalctl --disk-usage?", "answers": [("a", "Aby znać rzeczywiste zużycie miejsca przez journal", True), ("b", "Aby odtworzyć bazę", False), ("c", "Aby nadać uprawnienia root każdej usłudze", False), ("d", "Aby wymusić restart Nginxa", False)]},
        ],
    },
    "flashcards": [
        {"question": "Co filtruje journalctl -u?", "answer": "Wpisy wskazanej jednostki systemd."},
        {"question": "Co ogranicza journalctl -n 50?", "answer": "Wynik do ostatnich 50 wpisów."},
        {"question": "Do czego służy --since?", "answer": "Ustawia początek okna czasu logów."},
        {"question": "Do czego służy --until?", "answer": "Ustawia koniec okna czasu logów."},
        {"question": "Co filtruje journalctl -p?", "answer": "Priorytet wpisów journalu."},
        {"question": "Co oznacza poziom warning?", "answer": "Zdarzenie wymagające uwagi, niekoniecznie awarię."},
        {"question": "Co oznacza poziom error?", "answer": "Błąd operacji, który trzeba ocenić w kontekście."},
        {"question": "Po co znacznik czasu w logu?", "answer": "Pozwala ustalić kolejność i korelację zdarzeń."},
        {"question": "Co daje journalctl -o json?", "answer": "Ustrukturyzowany wynik wpisów journalu."},
        {"question": "Czym jest structured logging?", "answer": "Zapisem zdarzeń w polach zamiast w niejednolitym tekście."},
        {"question": "Jakie pola są użyteczne w logu?", "answer": "Czas, poziom, usługa, request ID i komunikat."},
        {"question": "Co robi tail -n 50?", "answer": "Czyta 50 ostatnich linii pliku."},
        {"question": "Co robi grep request_id?", "answer": "Wyszukuje wpisy powiązane z jednym żądaniem."},
        {"question": "Czy brak error dowodzi zdrowia aplikacji?", "answer": "Nie, trzeba sprawdzić zachowanie i metryki."},
        {"question": "Po co porównywać strefy czasu?", "answer": "Bez tego oś incydentu może być błędna."},
        {"question": "Gdzie może trafić stdout usługi systemd?", "answer": "Do journalu, zależnie od konfiguracji jednostki."},
        {"question": "Gdzie czytać log błędów Nginxa?", "answer": "Zwykle w /var/log/nginx/error.log."},
        {"question": "Czym jest rotacja logów?", "answer": "Okresową wymianą i usuwaniem starych plików według polityki."},
        {"question": "Po co retencja logów?", "answer": "Ogranicza czas przechowywania i zużycie miejsca."},
        {"question": "Co pokazuje journalctl --disk-usage?", "answer": "Rozmiar danych zajmowanych przez journal."},
        {"question": "Dlaczego nie usuwać logów w trakcie incydentu?", "answer": "Można utracić materiał potrzebny do ustalenia przyczyny."},
        {"question": "Czego nie zapisywać w logach?", "answer": "Haseł, pełnych tokenów i zbędnych danych klientów."},
        {"question": "Kto powinien czytać logi produkcyjne?", "answer": "Osoby z uzasadnionym dostępem operacyjnym."},
        {"question": "Co daje correlation ID między usługami?", "answer": "Pozwala powiązać wpisy dotyczące tego samego żądania."},
        {"question": "Od czego zacząć analizę logów awarii?", "answer": "Od usługi, czasu zdarzenia i objawu użytkownika."},
    ],
}
