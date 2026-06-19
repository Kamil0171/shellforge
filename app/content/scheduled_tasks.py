SCHEDULED_TASKS = {
    "module": {
        "title": "Administracja systemem",
        "description": "Moduł poświęcony podstawowej administracji systemem Linux.",
    },
    "lesson": {
        "title": "Zadania cykliczne: cron i podstawy systemd timers",
        "level": "Podstawowy+",
        "duration": "50 min",
        "description": (
            "Nauczysz się planować proste zadania przez cron, sprawdzać usługę crond "
            "oraz rozpoznawać i diagnozować podstawowe timery systemd."
        ),
        "theory": (
            "Automatyzacja zadań cyklicznych pozwala regularnie wykonywać kopie, raporty i prace "
            "porządkowe. Użytkownik zarządza swoim harmonogramem przez <code>crontab -e</code>, "
            "a listę wpisów sprawdza przez <code>crontab -l</code>. Typowy wpis ma pięć pól czasu: "
            "minutę, godzinę, dzień miesiąca, miesiąc i dzień tygodnia, po których następuje "
            "polecenie. Gwiazdka oznacza każdą wartość, przecinek listę, myślnik zakres, a zapis "
            "z ukośnikiem krok. Cron uruchamia polecenia w ograniczonym środowisku, dlatego warto "
            "używać pełnych ścieżek do programów i plików, ustalać katalog roboczy oraz kierować "
            "standardowe wyjście i błędy do kontrolowanego logu. W Rocky Linux za wykonywanie "
            "zadań odpowiada usługa <code>crond</code>, a jej zdarzenia można sprawdzać w journalu. "
            "Systemd timers stanowią nowocześniejszy mechanizm powiązany z jednostkami service. "
            "Timer opisuje termin, a odpowiadająca mu usługa wykonuje pracę. "
            "<code>systemctl list-timers</code> pokazuje poprzednie i następne uruchomienie, "
            "a status oraz journal pomagają w diagnozie. Timery mogą korzystać z zależności "
            "systemd, czytelnych logów i opcji uruchomienia pominiętego zadania po wyłączeniu "
            "maszyny. Niezależnie od mechanizmu należy najpierw przetestować polecenie ręcznie "
            "i unikać zadań, których kolejne uruchomienia nakładają się lub niszczą dane."
        ),
        "commands": [
            {
                "command": "crontab -l",
                "description": "Wyświetla wpisy crona aktualnego użytkownika.",
                "example": "$ crontab -l",
            },
            {
                "command": "crontab -e",
                "description": "Otwiera harmonogram aktualnego użytkownika do bezpiecznej edycji.",
                "example": "$ crontab -e",
            },
            {
                "command": "*/5 * * * * /usr/bin/date >> /tmp/cron-date.log 2>&1",
                "description": "Uruchamia date co pięć minut i zapisuje wyjście oraz błędy.",
                "example": "*/5 * * * * /usr/bin/date >> /tmp/cron-date.log 2>&1",
            },
            {
                "command": "systemctl status crond",
                "description": "Sprawdza stan usługi wykonującej zadania cron.",
                "example": "$ systemctl status crond",
            },
            {
                "command": "journalctl -u crond --since \"1 hour ago\"",
                "description": "Pokazuje zdarzenia crond z ostatniej godziny.",
                "example": "$ journalctl -u crond --since \"1 hour ago\"",
            },
            {
                "command": "systemctl list-timers --all",
                "description": "Wyświetla aktywne i nieaktywne timery wraz z terminami.",
                "example": "$ systemctl list-timers --all",
            },
            {
                "command": "systemctl status dnf-makecache.timer",
                "description": "Pokazuje stan przykładowego timera systemd.",
                "example": "$ systemctl status dnf-makecache.timer",
            },
            {
                "command": "systemctl cat dnf-makecache.timer",
                "description": "Wyświetla definicję timera i jego ustawienia czasu.",
                "example": "$ systemctl cat dnf-makecache.timer",
            },
            {
                "command": "journalctl -u dnf-makecache.service -n 30",
                "description": "Pokazuje logi usługi uruchamianej przez przykładowy timer.",
                "example": "$ journalctl -u dnf-makecache.service -n 30",
            },
        ],
        "practice_task": (
            "Najpierw wykonaj ręcznie <code>/usr/bin/date</code>. Następnie dodaj przez "
            "<code>crontab -e</code> wpis uruchamiający to polecenie co pięć minut i zapisujący "
            "wynik do <code>/tmp/cron-date.log</code>. Sprawdź wpis przez <code>crontab -l</code>, "
            "stan <code>crond</code> oraz po kilku minutach zawartość pliku wynikowego. Jeśli zadanie "
            "nie działa, przeanalizuj <code>journalctl -u crond --since \"15 minutes ago\"</code>. "
            "Potem wyświetl <code>systemctl list-timers --all</code>, znajdź "
            "<code>dnf-makecache.timer</code> i sprawdź jego status, definicję oraz logi powiązanej "
            "usługi. Po ćwiczeniu usuń wyłącznie dodany przez siebie wpis z crontaba."
        ),
        "common_mistakes": [
            "Niepoprawna kolejność pięciu pól czasu w crontabie użytkownika.",
            "Używanie względnych ścieżek i zakładanie takiego samego środowiska jak w terminalu.",
            "Brak przekierowania wyjścia i błędów, przez co zadanie trudno diagnozować.",
            "Dodawanie zadania bez wcześniejszego ręcznego przetestowania polecenia.",
            "Mylenie crontaba użytkownika z /etc/crontab, który zawiera dodatkowe pole użytkownika.",
            "Sprawdzanie tylko timera systemd bez logów uruchamianej jednostki service.",
            "Planowanie częstych zadań bez uwzględnienia nakładania się kolejnych uruchomień.",
        ],
        "summary": (
            "<code>crontab -e</code> edytuje harmonogram użytkownika, a pięć pól określa czas "
            "wykonania. Zadania cron powinny używać pełnych ścieżek i zapisywać błędy. Stan "
            "<code>crond</code> oraz jego journal pomagają w diagnozie. Systemd timer określa "
            "harmonogram, a powiązana jednostka service wykonuje pracę; oba elementy trzeba "
            "sprawdzać osobno."
        ),
    },
    "quiz": {
        "title": "Quiz: cron i podstawy systemd timers",
        "description": "Sprawdź praktyczne rozumienie harmonogramów i diagnostyki zadań.",
        "questions": [
            {
                "text": "Co robi crontab -l?",
                "answers": [
                    ("a", "Wyświetla zadania cron aktualnego użytkownika", True),
                    ("b", "Usuwa wszystkie timery systemd", False),
                    ("c", "Restartuje crond", False),
                    ("d", "Pokazuje zajętość dysku", False),
                ],
            },
            {
                "text": "Co oznacza */5 w polu minut crona?",
                "answers": [
                    ("a", "Wykonanie co pięć minut", True),
                    ("b", "Wykonanie tylko piątego dnia miesiąca", False),
                    ("c", "Pięć wykonań jednocześnie", False),
                    ("d", "Opóźnienie o pięć godzin", False),
                ],
            },
            {
                "text": "Dlaczego w zadaniu cron warto użyć /usr/bin/date zamiast samego date?",
                "answers": [
                    ("a", "Cron może mieć ograniczoną zmienną PATH", True),
                    ("b", "Cron nie obsługuje krótkich nazw plików", False),
                    ("c", "Pełna ścieżka zawsze nadaje uprawnienia root", False),
                    ("d", "Samo date usuwa crontab", False),
                ],
            },
            {
                "text": "Zadanie cron nie uruchomiło się. Co należy sprawdzić?",
                "answers": [
                    ("a", "Stan crond, składnię wpisu, ścieżki i logi", True),
                    ("b", "Wyłącznie ilość pamięci RAM", False),
                    ("c", "Kolor terminala", False),
                    ("d", "Tylko nazwę użytkownika root", False),
                ],
            },
            {
                "text": "Jaka jest rola jednostki timer w systemd?",
                "answers": [
                    ("a", "Określa, kiedy uruchomić powiązaną jednostkę service", True),
                    ("b", "Przechowuje wszystkie pliki aplikacji", False),
                    ("c", "Zastępuje system plików", False),
                    ("d", "Nadaje użytkownikom hasła", False),
                ],
            },
            {
                "text": "Gdzie szukać szczegółów wykonania zadania uruchomionego przez timer?",
                "answers": [
                    ("a", "W statusie i journalu powiązanej jednostki service", True),
                    ("b", "Wyłącznie w definicji timera", False),
                    ("c", "W /etc/hostname", False),
                    ("d", "W wyniku df -i", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Do czego służy cron?", "answer": "Do uruchamiania poleceń według harmonogramu."},
        {"question": "Co robi crontab -l?", "answer": "Wyświetla crontab aktualnego użytkownika."},
        {"question": "Co robi crontab -e?", "answer": "Edytuje crontab aktualnego użytkownika."},
        {"question": "Ile pól czasu ma wpis w crontabie użytkownika?", "answer": "Pięć, a po nich znajduje się polecenie."},
        {"question": "Jakie jest pierwsze pole crona?", "answer": "Minuta."},
        {"question": "Jakie jest drugie pole crona?", "answer": "Godzina."},
        {"question": "Jakie jest trzecie pole crona?", "answer": "Dzień miesiąca."},
        {"question": "Jakie jest czwarte pole crona?", "answer": "Miesiąc."},
        {"question": "Jakie jest piąte pole crona?", "answer": "Dzień tygodnia."},
        {"question": "Co oznacza gwiazdka w polu crona?", "answer": "Każdą dozwoloną wartość tego pola."},
        {"question": "Co oznacza */5 w polu minut?", "answer": "Uruchomienie co pięć minut."},
        {"question": "Po co używać pełnych ścieżek w cron?", "answer": "Cron może działać z inną i ograniczoną zmienną PATH."},
        {"question": "Co oznacza >> w zadaniu cron?", "answer": "Dopisanie standardowego wyjścia do pliku."},
        {"question": "Co oznacza 2>&1?", "answer": "Skierowanie standardowych błędów w to samo miejsce co standardowe wyjście."},
        {"question": "Dlaczego najpierw uruchomić polecenie ręcznie?", "answer": "Aby oddzielić błąd polecenia od błędu harmonogramu."},
        {"question": "Jaka usługa wykonuje zadania cron w Rocky Linux?", "answer": "crond."},
        {"question": "Jak sprawdzić stan crond?", "answer": "Poleceniem systemctl status crond."},
        {"question": "Jak sprawdzić logi crond?", "answer": "Poleceniem journalctl -u crond."},
        {"question": "Czym różni się /etc/crontab od crontaba użytkownika?", "answer": "/etc/crontab zawiera dodatkowe pole określające użytkownika wykonującego zadanie."},
        {"question": "Czym jest systemd timer?", "answer": "Jednostką planującą uruchomienie innej jednostki, zwykle service."},
        {"question": "Co pokazuje systemctl list-timers?", "answer": "Poprzednie i następne uruchomienia aktywnych timerów."},
        {"question": "Po co użyć list-timers --all?", "answer": "Aby uwzględnić także nieaktywne timery."},
        {"question": "Co robi systemctl cat nazwa.timer?", "answer": "Wyświetla definicję i źródłowe pliki jednostki timer."},
        {"question": "Gdzie sprawdzić wynik timera?", "answer": "W statusie i journalu uruchamianej jednostki service."},
        {"question": "Dlaczego zadania nie powinny się nakładać?", "answer": "Równoczesne wykonania mogą obciążyć system lub uszkodzić współdzielone dane."},
    ],
}
