SYSTEM_SERVICES = {
    "module": {
        "title": "Podstawy terminala",
        "description": "Pierwszy moduł poświęcony pracy w terminalu Linux.",
    },
    "lesson": {
        "title": "Usługi systemowe: systemctl i systemd",
        "level": "Podstawowy",
        "duration": "35 min",
        "description": (
            "Poznasz podstawy pracy z usługami systemowymi w Linuxie: sprawdzanie statusu, "
            "uruchamianie, zatrzymywanie, restartowanie oraz włączanie usług przy starcie systemu."
        ),
        "theory": (
            "W systemie Linux wiele programów działa jako usługi systemowe. Usługa może działać "
            "w tle i wykonywać określone zadanie, na przykład obsługiwać serwer WWW, połączenia SSH, "
            "zadania cykliczne albo aplikację webową. W wielu współczesnych dystrybucjach Linuxa "
            "zarządzaniem usługami zajmuje się systemd. Podstawowym narzędziem do pracy z usługami "
            "jest komenda systemctl. Dzięki niej można sprawdzić, czy usługa działa, uruchomić ją, "
            "zatrzymać, zrestartować, włączyć automatyczne uruchamianie po starcie systemu albo je "
            "wyłączyć. Zrozumienie systemctl jest bardzo ważne w administracji systemem, ponieważ "
            "większość usług serwerowych jest kontrolowana właśnie w ten sposób."
        ),
        "commands": [
            {
                "command": "systemctl status sshd",
                "description": "Sprawdza aktualny status usługi sshd.",
                "example": "$ systemctl status sshd\n● sshd.service - OpenSSH server daemon\n   Active: active (running)",
            },
            {
                "command": "systemctl start nginx",
                "description": "Uruchamia wskazaną usługę.",
                "example": "$ systemctl start nginx",
            },
            {
                "command": "systemctl stop nginx",
                "description": "Zatrzymuje wskazaną usługę.",
                "example": "$ systemctl stop nginx",
            },
            {
                "command": "systemctl restart nginx",
                "description": "Restartuje usługę, czyli zatrzymuje ją i uruchamia ponownie.",
                "example": "$ systemctl restart nginx",
            },
            {
                "command": "systemctl reload nginx",
                "description": "Przeładowuje konfigurację usługi bez pełnego restartu, jeśli usługa to obsługuje.",
                "example": "$ systemctl reload nginx",
            },
            {
                "command": "systemctl enable nginx",
                "description": "Włącza automatyczne uruchamianie usługi przy starcie systemu.",
                "example": "$ systemctl enable nginx",
            },
            {
                "command": "systemctl disable nginx",
                "description": "Wyłącza automatyczne uruchamianie usługi przy starcie systemu.",
                "example": "$ systemctl disable nginx",
            },
            {
                "command": "systemctl is-active nginx",
                "description": "Sprawdza, czy usługa jest aktualnie aktywna.",
                "example": "$ systemctl is-active nginx\nactive",
            },
            {
                "command": "systemctl is-enabled nginx",
                "description": "Sprawdza, czy usługa jest włączona do automatycznego startu.",
                "example": "$ systemctl is-enabled nginx\nenabled",
            },
            {
                "command": "systemctl list-units --type=service",
                "description": "Wyświetla listę aktywnych jednostek typu service.",
                "example": "$ systemctl list-units --type=service",
            },
        ],
        "practice_task": (
            "Sprawdź status przykładowej usługi poleceniem <code>systemctl status sshd</code>. "
            "Następnie sprawdź, czy jest aktywna przez <code>systemctl is-active sshd</code> oraz "
            "czy uruchamia się automatycznie przez <code>systemctl is-enabled sshd</code>. "
            "Wyświetl listę aktywnych usług komendą <code>systemctl list-units --type=service</code>. "
            "Jeżeli pracujesz w środowisku testowym, możesz przećwiczyć komendy "
            "<code>start</code>, <code>stop</code>, <code>restart</code> i <code>reload</code> "
            "na usłudze, której zatrzymanie nie przerwie Twojego połączenia z systemem."
        ),
        "common_mistakes": [
            "Restartowanie usługi bez wcześniejszego sprawdzenia jej statusu.",
            "Mylenie <code>restart</code> z <code>reload</code>.",
            "Zakładanie, że <code>enable</code> od razu uruchamia usługę.",
            "Zakładanie, że <code>start</code> włącza usługę na stałe po restarcie systemu.",
            "Zatrzymywanie usługi SSH podczas pracy przez zdalne połączenie bez świadomości skutków.",
            "Ignorowanie komunikatów błędów wyświetlanych przez <code>systemctl status</code>.",
            "Mylenie aktywności usługi z jej automatycznym uruchamianiem przy starcie systemu.",
        ],
        "summary": (
            "systemd odpowiada za zarządzanie wieloma usługami w systemie Linux, a "
            "<code>systemctl</code> jest podstawowym narzędziem do ich obsługi. "
            "Komenda <code>status</code> pokazuje stan usługi, <code>start</code> ją uruchamia, "
            "<code>stop</code> zatrzymuje, <code>restart</code> uruchamia ponownie, a "
            "<code>reload</code> przeładowuje konfigurację bez pełnego restartu, jeśli usługa to wspiera. "
            "<code>enable</code> i <code>disable</code> decydują o tym, czy usługa ma startować "
            "automatycznie razem z systemem."
        ),
    },
    "quiz": {
        "title": "Quiz: usługi systemowe",
        "description": "Sprawdź, czy rozumiesz podstawy pracy z usługami, systemd i systemctl.",
        "questions": [
            {
                "text": "Do czego służy systemctl?",
                "answers": [
                    ("a", "Do zarządzania usługami systemowymi", True),
                    ("b", "Do edycji obrazów", False),
                    ("c", "Do tworzenia plików tekstowych", False),
                    ("d", "Do zmiany rozdzielczości monitora", False),
                ],
            },
            {
                "text": "Co pokazuje systemctl status nginx?",
                "answers": [
                    ("a", "Aktualny stan usługi nginx", True),
                    ("b", "Zawartość katalogu domowego", False),
                    ("c", "Listę wszystkich użytkowników", False),
                    ("d", "Rozmiar dysku", False),
                ],
            },
            {
                "text": "Która komenda uruchamia usługę nginx?",
                "answers": [
                    ("a", "systemctl start nginx", True),
                    ("b", "systemctl enable nginx", False),
                    ("c", "systemctl list nginx", False),
                    ("d", "systemctl chmod nginx", False),
                ],
            },
            {
                "text": "Która komenda zatrzymuje usługę nginx?",
                "answers": [
                    ("a", "systemctl stop nginx", True),
                    ("b", "systemctl status nginx", False),
                    ("c", "systemctl grep nginx", False),
                    ("d", "systemctl pwd nginx", False),
                ],
            },
            {
                "text": "Co robi systemctl restart nginx?",
                "answers": [
                    ("a", "Zatrzymuje i ponownie uruchamia usługę nginx", True),
                    ("b", "Usuwa pakiet nginx", False),
                    ("c", "Zmienia nazwę usługi", False),
                    ("d", "Tworzy nowy katalog nginx", False),
                ],
            },
            {
                "text": "Co robi systemctl enable nginx?",
                "answers": [
                    ("a", "Włącza automatyczne uruchamianie usługi przy starcie systemu", True),
                    ("b", "Natychmiast usuwa usługę", False),
                    ("c", "Zawsze restartuje usługę", False),
                    ("d", "Wyświetla tylko pliki CSS", False),
                ],
            },
            {
                "text": "Co robi systemctl disable nginx?",
                "answers": [
                    ("a", "Wyłącza automatyczne uruchamianie usługi przy starcie systemu", True),
                    ("b", "Usuwa wszystkie logi", False),
                    ("c", "Instaluje nową wersję systemu", False),
                    ("d", "Zmienia hasło administratora", False),
                ],
            },
            {
                "text": "Co sprawdza systemctl is-active nginx?",
                "answers": [
                    ("a", "Czy usługa jest aktualnie aktywna", True),
                    ("b", "Czy plik jest wykonywalny", False),
                    ("c", "Czy użytkownik należy do grupy", False),
                    ("d", "Czy katalog jest pusty", False),
                ],
            },
            {
                "text": "Co sprawdza systemctl is-enabled nginx?",
                "answers": [
                    ("a", "Czy usługa ma startować automatycznie przy uruchomieniu systemu", True),
                    ("b", "Czy domena działa", False),
                    ("c", "Czy port jest zaszyfrowany", False),
                    ("d", "Czy plik jest ukryty", False),
                ],
            },
            {
                "text": "Jaka jest różnica między start i enable?",
                "answers": [
                    ("a", "start uruchamia usługę teraz, a enable włącza jej start przy uruchomieniu systemu", True),
                    ("b", "Nie ma żadnej różnicy", False),
                    ("c", "start usuwa usługę, a enable ją instaluje", False),
                    ("d", "start działa tylko na plikach, a enable tylko na katalogach", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Do czego służy systemctl?",
            "answer": "Do zarządzania usługami systemowymi w systemie Linux.",
        },
        {
            "question": "Czym jest systemd?",
            "answer": "Systemem inicjalizacji i zarządzania usługami w wielu dystrybucjach Linuxa.",
        },
        {
            "question": "Co robi systemctl status?",
            "answer": "Pokazuje aktualny stan usługi.",
        },
        {
            "question": "Jak sprawdzić status usługi nginx?",
            "answer": "Komendą systemctl status nginx.",
        },
        {
            "question": "Jak uruchomić usługę nginx?",
            "answer": "Komendą systemctl start nginx.",
        },
        {
            "question": "Jak zatrzymać usługę nginx?",
            "answer": "Komendą systemctl stop nginx.",
        },
        {
            "question": "Jak zrestartować usługę nginx?",
            "answer": "Komendą systemctl restart nginx.",
        },
        {
            "question": "Do czego służy systemctl reload?",
            "answer": "Do przeładowania konfiguracji usługi bez pełnego restartu, jeśli usługa to obsługuje.",
        },
        {
            "question": "Co robi systemctl enable?",
            "answer": "Włącza automatyczne uruchamianie usługi przy starcie systemu.",
        },
        {
            "question": "Co robi systemctl disable?",
            "answer": "Wyłącza automatyczne uruchamianie usługi przy starcie systemu.",
        },
        {
            "question": "Czy systemctl enable od razu uruchamia usługę?",
            "answer": "Nie. Enable ustawia automatyczny start przy uruchomieniu systemu.",
        },
        {
            "question": "Czy systemctl start włącza usługę na stałe po restarcie systemu?",
            "answer": "Nie. Start uruchamia usługę tylko teraz.",
        },
        {
            "question": "Co sprawdza systemctl is-active?",
            "answer": "Czy usługa jest aktualnie aktywna.",
        },
        {
            "question": "Co sprawdza systemctl is-enabled?",
            "answer": "Czy usługa jest włączona do automatycznego startu.",
        },
        {
            "question": "Jaka komenda pokazuje aktywne usługi?",
            "answer": "systemctl list-units --type=service.",
        },
        {
            "question": "Dlaczego przed restartem usługi warto sprawdzić jej status?",
            "answer": "Żeby zobaczyć, czy działa poprawnie i czy są widoczne błędy.",
        },
        {
            "question": "Czym różni się restart od reload?",
            "answer": "Restart uruchamia usługę ponownie, a reload zwykle tylko przeładowuje konfigurację.",
        },
        {
            "question": "Dlaczego trzeba uważać przy zatrzymywaniu sshd?",
            "answer": "Bo można przerwać możliwość zdalnego logowania na serwer.",
        },
        {
            "question": "Jak sprawdzić, czy nginx jest aktywny?",
            "answer": "Komendą systemctl is-active nginx.",
        },
        {
            "question": "Jak sprawdzić, czy nginx startuje automatycznie?",
            "answer": "Komendą systemctl is-enabled nginx.",
        },
    ],
}