DEPLOYMENT_CHECKLIST = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Procedura deploymentu i lista kontrolna",
        "level": "Średnio zaawansowany",
        "duration": "70 min",
        "description": (
            "Połączysz przygotowanie, backup, aktualizację, restart i weryfikację w jedną powtarzalną procedurę "
            "ręcznego deploymentu aplikacji."
        ),
        "theory": (
            "Procedura deploymentu zmienia zbiór pojedynczych poleceń w powtarzalny proces z punktami kontroli. "
            "Przed wdrożeniem należy przejrzeć zakres zmian, potwierdzić branch i czyste working tree, uruchomić "
            "lokalnie <code>ruff check .</code> oraz <code>pytest</code>, a następnie doprowadzić zatwierdzoną "
            "wersję do <code>main</code> zgodnie z workflow zespołu. Trzeba znać wymagane zmiany konfiguracji, "
            "zależności i bazy oraz przygotować kryteria sukcesu i plan rollbacku. Na serwerze najpierw zapisuje "
            "się <code>git rev-parse HEAD</code>, tworzy sprawdzony backup danych i konfiguracji, a dopiero potem "
            "pobiera kod przez <code>git pull --ff-only origin main</code>. Zależności aktualizuje się tylko, "
            "gdy zmienił się odpowiedni plik lub wymaga tego wydanie. Po restarcie kontrola przebiega od "
            "najbliższej warstwy: status i journal usługi, bezpośredni endpoint Uvicorna na "
            "<code>127.0.0.1:8000</code>, test i stan Nginxa, a następnie publiczna domena i HTTPS. Smoke test "
            "powinien sprawdzić nie tylko kod 200 strony głównej, lecz także najważniejsze funkcje właściwe dla "
            "aplikacji, bez modyfikowania produkcyjnych danych w niekontrolowany sposób. Wynik wdrożenia, commit, "
            "czas, operator, backup i anomalie należy zapisać. Jeśli kryteria sukcesu nie są spełnione, nie "
            "improwizuje się: zatrzymuje dalsze zmiany, zbiera logi i wykonuje przygotowany rollback kodu lub "
            "danych zależnie od diagnozy. Checklista powinna mieć trzy fazy. Przed: zakres, review, testy, branch, "
            "konfiguracja, backup i plan powrotu. W trakcie: zapis commita, pull --ff-only, zależności, restart i "
            "obserwacja logów. Po: Uvicorn, Nginx, domena, HTTPS, funkcje, monitoring i dokumentacja. Ręczny "
            "deployment daje operatorowi kontrolę, ale zależy od konsekwencji i jest podatny na pominięcia. CI/CD "
            "automatyzuje powtarzalne kroki i bramki jakości; zostanie rozwinięte w module DevOps, po zrozumieniu "
            "procesu ręcznego."
        ),
        "commands": [
            {
                "command": "ruff check . && pytest",
                "description": "Uruchamia lokalny lint i testy przed dopuszczeniem zmiany do wdrożenia.",
                "example": "$ ruff check .\n$ pytest",
            },
            {
                "command": "git status --short && git rev-parse HEAD",
                "description": "Potwierdza czyste repozytorium i zapisuje wersję wyjściową.",
                "example": "$ git status --short\n$ git rev-parse HEAD",
            },
            {
                "command": "git pull --ff-only origin main",
                "description": "Pobiera zatwierdzoną wersję main bez tworzenia merge commita na serwerze.",
                "example": "$ git pull --ff-only origin main",
            },
            {
                "command": "sudo systemctl restart example-app && sudo systemctl status example-app --no-pager -l",
                "description": "Uruchamia nową wersję procesu i sprawdza stan jednostki.",
                "example": "$ sudo systemctl restart example-app\n$ sudo systemctl status example-app --no-pager -l",
            },
            {
                "command": "journalctl -u example-app -n 100 --no-pager",
                "description": "Kontroluje logi nowego uruchomienia pod kątem błędów.",
                "example": "$ journalctl -u example-app -n 100 --no-pager",
            },
            {
                "command": "curl -sS -o /dev/null -w \"%{http_code}\\n\" http://127.0.0.1:8000/",
                "description": "Sprawdza bezpośrednio lokalny endpoint Uvicorna.",
                "example": "$ curl -sS -o /dev/null -w \"%{http_code}\\n\" http://127.0.0.1:8000/\n200",
            },
            {
                "command": "curl -sS -o /dev/null -w \"%{http_code}\\n\" https://app.example.com/",
                "description": "Sprawdza publiczną ścieżkę przez DNS, TLS i Nginx.",
                "example": "$ curl -sS -o /dev/null -w \"%{http_code}\\n\" https://app.example.com/\n200",
            },
        ],
        "practice_task": (
            "Przygotuj notatkę wdrożeniową dla <code>example-app.service</code> z trzema checklistami. "
            "<strong>Przed:</strong> zakres i review zmian, branch main, czyste working tree, ruff, pytest, zmiany "
            "konfiguracji, plan backupu i rollbacku. <strong>W trakcie:</strong> zapis commita, backup SQLite i "
            ".env, pull --ff-only, opcjonalna aktualizacja zależności, restart, status i logi. "
            "<strong>Po:</strong> lokalny curl do 127.0.0.1:8000, test Nginxa, publiczny HTTPS, kluczowe funkcje "
            "i dokumentacja wyniku. Dla każdego punktu dodaj oczekiwany wynik oraz decyzję STOP przy błędzie."
        ),
        "common_mistakes": [
            "Wdrażanie zmian, które nie przeszły lokalnych testów i lintowania.",
            "Pobieranie kodu przed zapisaniem commita i wykonaniem backupu.",
            "Aktualizowanie zależności bez użycia venv lub bez potrzeby.",
            "Uznanie aktywnego statusu systemd za pełne potwierdzenie działania.",
            "Pomijanie bezpośredniego testu Uvicorna albo publicznego testu HTTPS.",
            "Brak przygotowanego kryterium rollbacku i sprawdzonej kopii danych.",
            "Niedokumentowanie wersji, czasu, wyników oraz problemów wdrożenia.",
        ],
        "summary": (
            "Kompletna procedura obejmuje przygotowanie i lokalne testy, zapis stanu serwera, backup, bezpieczne "
            "pobranie kodu, zależności, restart i weryfikację każdej warstwy. Checklista przed, w trakcie i po "
            "wdrożeniu ogranicza pominięcia, a plan rollbacku wyznacza reakcję na błąd. Ręczny proces stanowi "
            "podstawę do późniejszej automatyzacji CI/CD w module DevOps."
        ),
    },
    "quiz": {
        "title": "Quiz: procedura deploymentu i lista kontrolna",
        "description": "Sprawdź znajomość pełnej, kontrolowanej procedury wdrożenia.",
        "questions": [
            {
                "text": "Co powinno wydarzyć się przed połączeniem z serwerem?",
                "answers": [
                    ("a", "Review zmian, kontrola repozytorium oraz lokalne ruff i pytest", True),
                    ("b", "Usunięcie poprzedniej bazy", False),
                    ("c", "Restart Nginxa bez zmian", False),
                    ("d", "Pomijanie planu rollbacku", False),
                ],
            },
            {
                "text": "Jaka jest właściwa kolejność na serwerze przed pull?",
                "answers": [
                    ("a", "Zapisać commit, wykonać i sprawdzić backup, potem pobrać kod", True),
                    ("b", "Najpierw pull, potem ustalać poprzednią wersję", False),
                    ("c", "Usunąć logi i backup", False),
                    ("d", "Wyłączyć firewall", False),
                ],
            },
            {
                "text": "Kiedy aktualizować zależności?",
                "answers": [
                    ("a", "Gdy zmienił się właściwy plik lub wymaga tego wydanie", True),
                    ("b", "Zawsze globalnie przed git pull", False),
                    ("c", "Dopiero po rollbacku", False),
                    ("d", "Nigdy", False),
                ],
            },
            {
                "text": "Jaka kolejność weryfikacji najlepiej lokalizuje problem?",
                "answers": [
                    ("a", "Systemd i logi, Uvicorn, Nginx, publiczna domena HTTPS", True),
                    ("b", "Domena, usunięcie bazy, restart systemu", False),
                    ("c", "Tylko strona główna w przeglądarce", False),
                    ("d", "Wyłącznie git log", False),
                ],
            },
            {
                "text": "Co zrobić, gdy kryteria sukcesu nie są spełnione?",
                "answers": [
                    ("a", "Zatrzymać dalsze zmiany, zebrać dane i użyć planu rollbacku", True),
                    ("b", "Kontynuować kolejne wdrożenia", False),
                    ("c", "Usunąć wszystkie logi", False),
                    ("d", "Ukryć problem restartami", False),
                ],
            },
            {
                "text": "Jaka jest relacja ręcznego deploymentu do CI/CD?",
                "answers": [
                    ("a", "Ręczny proces uczy kroków, które później można bezpiecznie automatyzować", True),
                    ("b", "Są identyczne i nie wymagają testów", False),
                    ("c", "CI/CD oznacza ręczne kopiowanie plików", False),
                    ("d", "Ręczny deployment nie potrzebuje checklisty", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Po co procedura deploymentu?", "answer": "Aby wdrożenie było powtarzalne, sprawdzalne i mniej podatne na pominięcia."},
        {"question": "Jakie są trzy fazy checklisty?", "answer": "Przed wdrożeniem, w trakcie i po wdrożeniu."},
        {"question": "Co sprawdzić lokalnie przed wdrożeniem?", "answer": "Zakres zmian, branch, working tree, review, ruff i pytest."},
        {"question": "Po co uruchamiać ruff check .?", "answer": "Aby wykryć problemy jakości i stylu kodu przed wdrożeniem."},
        {"question": "Po co uruchamiać pytest?", "answer": "Aby sprawdzić automatyczne scenariusze działania aplikacji."},
        {"question": "Co powinno trafić do main?", "answer": "Przejrzana i zatwierdzona wersja gotowa do wdrożenia."},
        {"question": "Co zapisać przed pobraniem kodu?", "answer": "Bieżący commit oraz lokalizację sprawdzonego backupu."},
        {"question": "Co obejmuje backup przed wdrożeniem?", "answer": "Dane i konfigurację potrzebne do odtworzenia usługi."},
        {"question": "Dlaczego używać pull --ff-only?", "answer": "Aby nie tworzyć nieplanowanego scalenia na serwerze."},
        {"question": "Kiedy aktualizować requirements.txt?", "answer": "Zależności instaluje się, gdy plik się zmienił lub wymaga tego wydanie."},
        {"question": "Co zrobić po restarcie?", "answer": "Sprawdzić status i logi nowego uruchomienia."},
        {"question": "Po co testować Uvicorna bezpośrednio?", "answer": "Aby potwierdzić warstwę aplikacji bez Nginxa i TLS."},
        {"question": "Po co uruchamiać nginx -t?", "answer": "Aby potwierdzić poprawność konfiguracji reverse proxy."},
        {"question": "Co sprawdza publiczny curl HTTPS?", "answer": "Łańcuch DNS, TLS, Nginx i aplikacji."},
        {"question": "Czym jest smoke test?", "answer": "Krótką kontrolą najważniejszych funkcji po zmianie."},
        {"question": "Czy sam kod HTTP 200 wystarcza?", "answer": "Nie zawsze; trzeba sprawdzić kluczowe funkcje aplikacji."},
        {"question": "Czym jest kryterium sukcesu?", "answer": "Mierzalnym warunkiem uznania wdrożenia za poprawne."},
        {"question": "Czym jest kryterium rollbacku?", "answer": "Warunkiem, po którego wystąpieniu należy rozpocząć kontrolowany powrót."},
        {"question": "Co zrobić przy błędzie w trakcie?", "answer": "Zatrzymać proces, zachować dane diagnostyczne i użyć przygotowanego planu."},
        {"question": "Co dokumentować po wdrożeniu?", "answer": "Czas, commit, operatora, backup, kroki, testy i anomalie."},
        {"question": "Dlaczego checklista ma kolejność?", "answer": "Każdy krok tworzy bezpieczny punkt kontrolny dla następnego."},
        {"question": "Czym jest ręczny deployment?", "answer": "Procesem wykonywanym i zatwierdzanym krok po kroku przez operatora."},
        {"question": "Czym jest CI/CD?", "answer": "Automatyzacją integracji, testów i dostarczania zmian według zdefiniowanego procesu."},
        {"question": "Gdzie rozwijane będzie CI/CD?", "answer": "W module DevOps i automatyzacja."},
        {"question": "Jaki jest końcowy cel deploymentu?", "answer": "Bezpiecznie uruchomić właściwą wersję i potwierdzić jej działanie."},
    ],
}
