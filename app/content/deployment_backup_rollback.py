DEPLOYMENT_BACKUP_ROLLBACK = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Backup przed wdrożeniem i podstawowy rollback",
        "level": "Średnio zaawansowany",
        "duration": "65 min",
        "description": (
            "Przygotujesz backup danych i konfiguracji przed wdrożeniem oraz przećwiczysz kontrolowany powrót "
            "do zapisanej wersji kodu i bazy."
        ),
        "theory": (
            "Backup przed wdrożeniem ogranicza skutki błędu, ale tylko wtedy, gdy obejmuje właściwe zasoby i "
            "da się go odtworzyć. Kod, konfiguracja i dane wymagają różnych metod. Kod ma historię Git, dlatego "
            "przed zmianą zapisuje się identyfikator z <code>git rev-parse HEAD</code>. Plik .env i konfigurację "
            "usługi należy kopiować z zachowaniem uprawnień do chronionego katalogu. Dane SQLite wymagają "
            "spójnej kopii. Najlepiej użyć polecenia <code>.backup</code> klienta sqlite3, które korzysta z API "
            "backupu. Przy prostym kopiowaniu pliku bazę powinna wcześniej przestać modyfikować aplikacja, "
            "zwykle przez kontrolowane zatrzymanie usługi; samo cp aktywnej bazy może dać niespójny wynik, "
            "szczególnie przy dodatkowych plikach WAL. Katalog <code>/opt/example-app/backups</code> powinien "
            "mieć ograniczone uprawnienia. Znacznik czasu w nazwie pozwala powiązać pliki z wdrożeniem, lecz "
            "trzeba też sprawdzić kod wyjścia, istnienie i rozmiar kopii. Backup bez testu odtworzenia daje "
            "fałszywe poczucie bezpieczeństwa. Rollback kodu i rollback danych to osobne decyzje. Do awaryjnego "
            "uruchomienia zapisanej wersji można w kontrolowany sposób użyć "
            "<code>git switch --detach &lt;commit&gt;</code>, po wcześniejszym sprawdzeniu working tree i historii. "
            "Docelowo warto mieć udokumentowaną metodę powrotu brancha lub wydania, aby nie pozostawić serwera "
            "bez nazwanego brancha. Przywrócenie bazy wymaga zatrzymania aplikacji, zabezpieczenia bieżącego "
            "pliku, odtworzenia sprawdzonej kopii, ustawienia właściciela i restartu. Cofnięcie kodu nie zawsze "
            "wymaga cofnięcia danych. Nowy kod mógł jednak zmienić schemat lub zapisać dane niezgodne ze starą "
            "wersją. Bardziej złożone systemy potrzebują wersjonowanych migracji oraz osobnych procedur rollbacku "
            "danych. Każdy krok, commit, plik backupu i wynik weryfikacji należy udokumentować."
        ),
        "commands": [
            {
                "command": "sudo install -d -o example-app -g example-app -m 700 /opt/example-app/backups",
                "description": "Tworzy chroniony katalog backupów dla użytkownika aplikacji.",
                "example": "$ sudo install -d -o example-app -g example-app -m 700 /opt/example-app/backups",
            },
            {
                "command": "date +%Y%m%d-%H%M%S && git rev-parse HEAD",
                "description": "Generuje znacznik czasu i zapisuje dokładny commit przed wdrożeniem.",
                "example": "$ date +%Y%m%d-%H%M%S\n20260806-153000\n$ git rev-parse HEAD",
            },
            {
                "command": "sqlite3 /opt/example-app/data/app.db \".backup '/opt/example-app/backups/app-20260806-153000.db'\"",
                "description": "Tworzy spójną kopię bazy SQLite przez mechanizm backupu.",
                "example": "$ sqlite3 /opt/example-app/data/app.db \".backup '/opt/example-app/backups/app-20260806-153000.db'\"",
            },
            {
                "command": "sudo cp --preserve=mode,ownership /opt/example-app/.env /opt/example-app/backups/.env-20260806-153000",
                "description": "Kopiuje konfigurację z zachowaniem właściciela i uprawnień.",
                "example": "$ sudo cp --preserve=mode,ownership /opt/example-app/.env /opt/example-app/backups/.env-20260806-153000",
            },
            {
                "command": "git log --oneline -5 && git switch --detach <commit>",
                "description": "Pozwala wybrać i tymczasowo uruchomić wcześniej zidentyfikowany commit.",
                "example": "$ git log --oneline -5\n$ git switch --detach <commit>",
            },
            {
                "command": "sudo systemctl restart example-app",
                "description": "Uruchamia usługę z wybraną wersją po wykonaniu wymaganych operacji odtworzeniowych.",
                "example": "$ sudo systemctl restart example-app",
            },
        ],
        "practice_task": (
            "Utwórz chroniony katalog <code>/opt/example-app/backups</code> i wygeneruj znacznik czasu. Zapisz "
            "commit przez <code>git rev-parse HEAD</code>, wykonaj backup bazy przez <code>sqlite3 .backup</code> "
            "oraz kopię .env z zachowaniem uprawnień. Sprawdź, że pliki istnieją, mają niezerowy rozmiar i "
            "właściwego właściciela. Następnie opisz kontrolowany rollback: zatrzymanie zmian, wybór zapisanego "
            "commita, decyzję czy cofać dane, bezpieczne odtworzenie bazy, restart, status, logi i smoke test. "
            "Ćwiczenie wykonaj na danych laboratoryjnych."
        ),
        "common_mistakes": [
            "Kopiowanie aktywnej bazy SQLite bez .backup lub zatrzymania zapisującej aplikacji.",
            "Tworzenie backupu bez sprawdzenia jego istnienia, rozmiaru i możliwości odtworzenia.",
            "Przechowywanie kopii .env z uprawnieniami umożliwiającymi odczyt innym użytkownikom.",
            "Rozpoczynanie rollbacku bez zapisanego commita i backupu danych.",
            "Automatyczne cofanie bazy razem z kodem bez analizy zgodności danych.",
            "Używanie git reset --hard jako podstawowej metody bez oceny utraty zmian.",
            "Brak dokumentacji wskazującej użyty commit, backup i wynik weryfikacji.",
        ],
        "summary": (
            "Przed wdrożeniem należy osobno zabezpieczyć dane, konfigurację i punkt odniesienia kodu. SQLite "
            "najbezpieczniej kopiować przez .backup, a pliki konfiguracyjne przechowywać z ograniczonymi "
            "uprawnieniami. Rollback kodu nie oznacza automatycznie rollbacku danych; zgodność wersji i "
            "migracji trzeba ocenić przed odtworzeniem. Procedura kończy się restartem i weryfikacją."
        ),
    },
    "quiz": {
        "title": "Quiz: backup przed wdrożeniem i podstawowy rollback",
        "description": "Sprawdź przygotowanie kopii i kontrolowane odtwarzanie aplikacji.",
        "questions": [
            {
                "text": "Dlaczego kod, konfigurację i dane backupuje się inaczej?",
                "answers": [
                    ("a", "Mają inne właściwości, ryzyka i mechanizmy odtworzenia", True),
                    ("b", "Każdy z nich jest rekordem DNS", False),
                    ("c", "Git przechowuje automatycznie bazę i sekrety", False),
                    ("d", "Nie można kopiować plików konfiguracji", False),
                ],
            },
            {
                "text": "Jak utworzyć spójną kopię aktywnej bazy SQLite?",
                "answers": [
                    ("a", "Użyć mechanizmu .backup albo zatrzymać zapisy przed prostym kopiowaniem", True),
                    ("b", "Skopiować wyłącznie plik WAL podczas zapisu", False),
                    ("c", "Wykonać git pull", False),
                    ("d", "Zrestartować Nginx bez kopii", False),
                ],
            },
            {
                "text": "Po co zapisywać git rev-parse HEAD?",
                "answers": [
                    ("a", "Aby znać dokładny commit działający przed wdrożeniem", True),
                    ("b", "Aby wydrukować zawartość .env", False),
                    ("c", "Aby utworzyć certyfikat", False),
                    ("d", "Aby sprawdzić wolną pamięć", False),
                ],
            },
            {
                "text": "Co trzeba sprawdzić po utworzeniu backupu?",
                "answers": [
                    ("a", "Istnienie, rozmiar, uprawnienia i możliwość odtworzenia", True),
                    ("b", "Wyłącznie nazwę katalogu", False),
                    ("c", "Czy plik jest publicznie dostępny", False),
                    ("d", "Czy usunięto poprzedni commit", False),
                ],
            },
            {
                "text": "Czy rollback kodu zawsze wymaga rollbacku bazy?",
                "answers": [
                    ("a", "Nie, to osobna decyzja zależna od zmian danych i schematu", True),
                    ("b", "Tak, bez żadnej analizy", False),
                    ("c", "Tak, ponieważ Git zarządza SQLite", False),
                    ("d", "Nie, bo bazy nigdy nie trzeba backupować", False),
                ],
            },
            {
                "text": "Co kończy kontrolowany rollback?",
                "answers": [
                    ("a", "Restart oraz weryfikacja statusu, logów i działania", True),
                    ("b", "Usunięcie wszystkich backupów", False),
                    ("c", "Wyłączenie HTTPS", False),
                    ("d", "Pozostawienie usługi bez testu", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Po co backup przed wdrożeniem?", "answer": "Aby mieć sprawdzony punkt odtworzenia po nieudanej zmianie."},
        {"question": "Jakie trzy obszary trzeba rozróżnić?", "answer": "Kod, konfigurację i dane aplikacji."},
        {"question": "Jak Git pomaga przy kodzie?", "answer": "Identyfikuje dokładne wersje przez commity."},
        {"question": "Co zapisuje git rev-parse HEAD?", "answer": "Pełny identyfikator bieżącego commita."},
        {"question": "Po co znacznik czasu w nazwie?", "answer": "Łączy kopię z konkretnym momentem i wdrożeniem."},
        {"question": "Gdzie przechowywać kopie przykładowej aplikacji?", "answer": "Na przykład w chronionym /opt/example-app/backups."},
        {"question": "Jakie uprawnienia powinien mieć katalog backupu?", "answer": "Ograniczone do kont odpowiedzialnych za aplikację i odtwarzanie."},
        {"question": "Dlaczego zwykłe cp aktywnej SQLite jest ryzykowne?", "answer": "Zapis może trwać, a dane mogą znajdować się także w WAL."},
        {"question": "Co robi sqlite3 .backup?", "answer": "Tworzy spójną kopię przez mechanizm backupu SQLite."},
        {"question": "Kiedy proste kopiowanie bazy jest bezpieczniejsze?", "answer": "Po zatrzymaniu procesu, który może do niej zapisywać."},
        {"question": "Dlaczego chronić kopię .env?", "answer": "Może zawierać te same sekrety co aktywna konfiguracja."},
        {"question": "Co zachowuje cp --preserve?", "answer": "Wskazane metadane, na przykład tryb i właściciela."},
        {"question": "Czy istnienie pliku potwierdza dobry backup?", "answer": "Nie, trzeba też sprawdzić rozmiar, spójność i odtworzenie."},
        {"question": "Czym jest rollback kodu?", "answer": "Powrotem do wcześniej zidentyfikowanej wersji aplikacji."},
        {"question": "Czym jest rollback danych?", "answer": "Odtworzeniem wcześniejszego stanu bazy lub innych danych."},
        {"question": "Czy rollback kodu i danych to jedno?", "answer": "Nie, mogą mieć różne przyczyny, skutki i procedury."},
        {"question": "Co robi git switch --detach?", "answer": "Przełącza working tree na commit bez ustawiania nazwanego brancha."},
        {"question": "Co sprawdzić przed switch --detach?", "answer": "Working tree, bieżący commit, backup i wybraną wersję."},
        {"question": "Jak bezpiecznie przywracać bazę?", "answer": "Zatrzymać aplikację, zabezpieczyć bieżący stan, odtworzyć kopię i ustawić uprawnienia."},
        {"question": "Co zrobić po odtworzeniu?", "answer": "Uruchomić usługę i sprawdzić status, logi oraz funkcje."},
        {"question": "Skąd ryzyko zgodności bazy?", "answer": "Nowy kod mógł zmienić schemat lub format zapisanych danych."},
        {"question": "Czego wymagają większe aplikacje?", "answer": "Migracji oraz osobnych, wersjonowanych procedur rollbacku."},
        {"question": "Dlaczego nie zaczynać od reset --hard?", "answer": "Może usunąć zmiany i utrudnić analizę stanu wyjściowego."},
        {"question": "Co dokumentować przy rollbacku?", "answer": "Powód, commity, kopie, wykonane kroki i wyniki testów."},
        {"question": "Kiedy backup jest użyteczny?", "answer": "Gdy jest kompletny, chroniony, sprawdzony i można go odtworzyć."},
    ],
}
