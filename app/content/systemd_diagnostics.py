SYSTEMD_DIAGNOSTICS = {
    "module": {
        "title": "Administracja systemem",
        "description": "Moduł poświęcony podstawowej administracji systemem Linux.",
    },
    "lesson": {
        "title": "Diagnostyka usług systemd: systemctl status, restart, enable i journalctl -u",
        "level": "Podstawowy+",
        "duration": "45 min",
        "description": (
            "Nauczysz się metodycznie sprawdzać stan usług systemd, analizować ich logi "
            "oraz rozróżniać uruchomienie usługi od włączenia jej przy starcie systemu."
        ),
        "theory": (
            "Usługa zarządzana przez systemd jest opisana jednostką, zwykle z końcówką "
            "<code>.service</code>. Pierwszym krokiem diagnostyki powinno być "
            "<code>systemctl status nazwa</code>, które pokazuje stan jednostki, ostatni wynik "
            "uruchomienia, PID procesu i kilka najnowszych komunikatów. Stan "
            "<code>active (running)</code> oznacza działającą usługę, a "
            "<code>failed</code> wskazuje, że próba działania zakończyła się błędem. "
            "<code>systemctl is-active</code> pozwala szybko sprawdzić bieżący stan, natomiast "
            "<code>systemctl is-enabled</code> odpowiada na inne pytanie: czy jednostka ma "
            "uruchamiać się automatycznie podczas startu systemu. Polecenia "
            "<code>start</code> i <code>restart</code> wpływają na stan bieżący, a "
            "<code>enable</code> zmienia konfigurację kolejnych uruchomień systemu. "
            "Po nieudanym starcie trzeba sprawdzić pełniejsze logi przez "
            "<code>journalctl -u nazwa</code>. Warto ograniczyć je do bieżącego uruchomienia "
            "systemu, ostatnich wpisów albo konkretnego czasu. Restart nie jest metodą diagnozy "
            "samą w sobie: przed nim należy przeczytać status i logi, a po nim ponownie "
            "zweryfikować usługę. Jeśli zmieniono plik jednostki systemd, należy wykonać "
            "<code>systemctl daemon-reload</code>; nie jest to potrzebne po każdej zmianie "
            "konfiguracji samej aplikacji."
        ),
        "commands": [
            {
                "command": "systemctl status sshd",
                "description": "Pokazuje szczegółowy stan usługi sshd i ostatnie komunikaty.",
                "example": "$ systemctl status sshd",
            },
            {
                "command": "systemctl is-active sshd",
                "description": "Zwraca bieżący stan aktywności usługi.",
                "example": "$ systemctl is-active sshd\nactive",
            },
            {
                "command": "systemctl is-enabled sshd",
                "description": "Sprawdza, czy usługa ma uruchamiać się przy starcie systemu.",
                "example": "$ systemctl is-enabled sshd\nenabled",
            },
            {
                "command": "sudo systemctl restart crond",
                "description": "Restartuje usługę crond; należy używać po świadomej weryfikacji.",
                "example": "$ sudo systemctl restart crond",
            },
            {
                "command": "sudo systemctl enable crond",
                "description": "Włącza automatyczne uruchamianie crond przy starcie systemu.",
                "example": "$ sudo systemctl enable crond",
            },
            {
                "command": "sudo systemctl enable --now crond",
                "description": "Jednocześnie włącza autostart i uruchamia usługę teraz.",
                "example": "$ sudo systemctl enable --now crond",
            },
            {
                "command": "journalctl -u sshd -n 50 --no-pager",
                "description": "Pokazuje 50 ostatnich wpisów usługi sshd bez stronicowania.",
                "example": "$ journalctl -u sshd -n 50 --no-pager",
            },
            {
                "command": "journalctl -u sshd -b",
                "description": "Pokazuje logi usługi sshd z bieżącego uruchomienia systemu.",
                "example": "$ journalctl -u sshd -b",
            },
            {
                "command": "sudo systemctl daemon-reload",
                "description": "Wczytuje ponownie definicje jednostek po zmianie pliku unit.",
                "example": "$ sudo systemctl daemon-reload",
            },
        ],
        "practice_task": (
            "W środowisku laboratoryjnym sprawdź usługę <code>crond</code> poleceniami "
            "<code>systemctl status crond</code>, <code>systemctl is-active crond</code> i "
            "<code>systemctl is-enabled crond</code>. Następnie wyświetl 30 ostatnich wpisów "
            "przez <code>journalctl -u crond -n 30 --no-pager</code>. Zapisz osobno odpowiedzi "
            "na pytania: „czy usługa działa teraz?” i „czy uruchomi się po restarcie systemu?”. "
            "Jeśli pracujesz na maszynie przeznaczonej do ćwiczeń i możesz bezpiecznie przerwać "
            "działanie crond, wykonaj <code>sudo systemctl restart crond</code>, po czym ponownie "
            "sprawdź status i logi. Nie restartuj zdalnie usługi SSH używanej do bieżącego połączenia."
        ),
        "common_mistakes": [
            "Mylenie stanu active ze stanem enabled.",
            "Restartowanie usługi przed przeczytaniem statusu i zachowaniem informacji o błędzie.",
            "Zakładanie, że enable natychmiast uruchamia zatrzymaną usługę.",
            "Sprawdzanie tylko krótkiego fragmentu logów widocznego w systemctl status.",
            "Pomijanie nazwy jednostki przy filtrowaniu dziennika przez journalctl -u.",
            "Wykonywanie daemon-reload po każdej zmianie konfiguracji aplikacji.",
            "Restartowanie sshd podczas zdalnej pracy bez sprawdzenia konfiguracji i dostępu awaryjnego.",
        ],
        "summary": (
            "Diagnostykę usługi zacznij od <code>systemctl status</code>, następnie rozdziel "
            "sprawdzenie bieżącej aktywności przez <code>is-active</code> od autostartu przez "
            "<code>is-enabled</code>. Pełniejsze komunikaty znajdziesz w "
            "<code>journalctl -u</code>. Restart wykonuj świadomie i zawsze sprawdzaj jego wynik. "
            "<code>enable --now</code> łączy włączenie autostartu z natychmiastowym uruchomieniem."
        ),
    },
    "quiz": {
        "title": "Quiz: diagnostyka usług systemd",
        "description": "Sprawdź praktyczne rozumienie statusu, autostartu, restartu i logów usług.",
        "questions": [
            {
                "text": "Usługa nie działa. Od którego polecenia najlepiej zacząć diagnostykę?",
                "answers": [
                    ("a", "systemctl status nazwa-usługi", True),
                    ("b", "systemctl enable nazwa-usługi", False),
                    ("c", "rm -rf /var/log", False),
                    ("d", "hostnamectl", False),
                ],
            },
            {
                "text": "Co sprawdza systemctl is-enabled crond?",
                "answers": [
                    ("a", "Czy crond ma uruchamiać się przy starcie systemu", True),
                    ("b", "Czy crond aktualnie zużywa procesor", False),
                    ("c", "Czy istnieje katalog /var/log", False),
                    ("d", "Czy użytkownik ma hasło", False),
                ],
            },
            {
                "text": "Usługa jest enabled, ale inactive. Co to oznacza?",
                "answers": [
                    ("a", "Ma skonfigurowany autostart, lecz obecnie nie działa", True),
                    ("b", "Działa poprawnie i nie ma autostartu", False),
                    ("c", "Jej logi zostały usunięte", False),
                    ("d", "Systemd nie zna tej jednostki", False),
                ],
            },
            {
                "text": "Które polecenie pokaże logi sshd z bieżącego uruchomienia systemu?",
                "answers": [
                    ("a", "journalctl -u sshd -b", True),
                    ("b", "systemctl enable sshd", False),
                    ("c", "du -sh sshd", False),
                    ("d", "crontab -l sshd", False),
                ],
            },
            {
                "text": "Kiedy potrzebne jest systemctl daemon-reload?",
                "answers": [
                    ("a", "Po zmianie definicji jednostki systemd", True),
                    ("b", "Po każdym odczytaniu statusu usługi", False),
                    ("c", "Przed każdym użyciem journalctl", False),
                    ("d", "Po zmianie katalogu roboczego w terminalu", False),
                ],
            },
            {
                "text": "Co robi systemctl enable --now crond?",
                "answers": [
                    ("a", "Włącza autostart i uruchamia crond w bieżącej sesji", True),
                    ("b", "Tylko wyświetla status crond", False),
                    ("c", "Usuwa jednostkę crond", False),
                    ("d", "Czyści wszystkie logi crond", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest jednostka service?", "answer": "To definicja usługi zarządzanej przez systemd."},
        {"question": "Od czego zacząć diagnostykę usługi?", "answer": "Od systemctl status nazwa-usługi."},
        {"question": "Co pokazuje systemctl status?", "answer": "Stan jednostki, wynik uruchomienia, PID i ostatnie komunikaty."},
        {"question": "Co oznacza active (running)?", "answer": "Usługa jest obecnie uruchomiona."},
        {"question": "Co oznacza failed?", "answer": "Uruchomienie lub działanie jednostki zakończyło się błędem."},
        {"question": "Co robi systemctl is-active?", "answer": "Sprawdza bieżący stan aktywności jednostki."},
        {"question": "Co robi systemctl is-enabled?", "answer": "Sprawdza konfigurację automatycznego startu jednostki."},
        {"question": "Czy enabled oznacza active?", "answer": "Nie. Autostart i bieżące działanie to dwa różne stany."},
        {"question": "Co robi systemctl start?", "answer": "Uruchamia usługę teraz, bez koniecznego włączania autostartu."},
        {"question": "Co robi systemctl restart?", "answer": "Zatrzymuje usługę i uruchamia ją ponownie."},
        {"question": "Co robi systemctl enable?", "answer": "Konfiguruje uruchamianie jednostki przy starcie systemu."},
        {"question": "Co robi systemctl enable --now?", "answer": "Włącza autostart i od razu uruchamia jednostkę."},
        {"question": "Co robi journalctl -u sshd?", "answer": "Pokazuje wpisy dziennika przypisane do jednostki sshd."},
        {"question": "Po co używać opcji -n w journalctl?", "answer": "Aby ograniczyć wynik do określonej liczby ostatnich wpisów."},
        {"question": "Co oznacza -b w journalctl?", "answer": "Ogranicza wynik do bieżącego uruchomienia systemu."},
        {"question": "Po co używać --no-pager?", "answer": "Aby wyświetlić wynik bez otwierania programu stronicującego."},
        {"question": "Czy restart zawsze naprawia usługę?", "answer": "Nie. Może tylko chwilowo ukryć problem lub ponownie wywołać błąd."},
        {"question": "Co zrobić przed restartem?", "answer": "Sprawdzić status, logi i możliwą przyczynę problemu."},
        {"question": "Co zrobić po restarcie?", "answer": "Ponownie sprawdzić status i najnowsze logi."},
        {"question": "Kiedy wykonać daemon-reload?", "answer": "Po utworzeniu lub zmianie pliku jednostki systemd."},
        {"question": "Czy daemon-reload restartuje usługę?", "answer": "Nie. Wczytuje definicje jednostek, ale sam nie restartuje usługi."},
        {"question": "Dlaczego restart sshd wymaga ostrożności?", "answer": "Błąd może odciąć bieżący lub przyszły dostęp zdalny."},
        {"question": "Jak sprawdzić crond bez zmieniania jego stanu?", "answer": "Użyć systemctl status, is-active i is-enabled."},
        {"question": "Jaka jest różnica między start i enable?", "answer": "Start działa teraz, a enable konfiguruje przyszły start systemu."},
        {"question": "Jaki jest podstawowy schemat diagnostyki usługi?", "answer": "Status, pełne logi, analiza przyczyny, świadoma akcja i ponowna weryfikacja."},
    ],
}
