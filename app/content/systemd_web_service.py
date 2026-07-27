SYSTEMD_WEB_SERVICE = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Aplikacja jako usługa systemd",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": (
            "Zbudujesz jednostkę systemd dla aplikacji webowej, ustawisz użytkownika, katalog roboczy, "
            "konfigurację środowiskową i polecenie Uvicorna oraz sprawdzisz uruchomienie i logi usługi."
        ),
        "theory": (
            "Plik jednostki <code>example-app.service</code> opisuje, jak systemd ma zarządzać procesem "
            "aplikacji. Sekcja <code>[Unit]</code> zawiera opis i zależności kolejności uruchamiania. "
            "<code>[Service]</code> określa proces: <code>User</code> i <code>Group</code> ograniczają jego "
            "uprawnienia, <code>WorkingDirectory</code> ustawia katalog potrzebny do importu kodu, a "
            "<code>EnvironmentFile</code> wskazuje plik konfiguracji środowiskowej. <code>ExecStart</code> "
            "powinien używać bezpośredniej ścieżki do Uvicorna w venv i uruchamiać "
            "<code>app.main:app</code> na <code>127.0.0.1:8000</code>. <code>Restart=on-failure</code> pozwala "
            "ponowić uruchomienie po nieoczekiwanym błędzie, ale nie naprawia złej konfiguracji. Sekcja "
            "<code>[Install]</code> z <code>WantedBy=multi-user.target</code> pozwala włączyć autostart. Po "
            "utworzeniu lub zmianie jednostki wykonuje się <code>systemctl daemon-reload</code>. Następnie "
            "można ją włączyć, uruchomić i kontrolować przez <code>status</code> oraz "
            "<code>journalctl -u</code>. Ta konfiguracja dotyczy aplikacji webowej; wcześniejsze ogólne zasady "
            "diagnostyki systemd nadal obowiązują."
        ),
        "commands": [
            {
                "command": "/etc/systemd/system/example-app.service",
                "description": "Przykładowa jednostka uruchamiająca aplikację przez Uvicorn z venv.",
                "example": (
                    "[Unit]\n"
                    "Description=Example ASGI application\n"
                    "After=network.target\n"
                    "\n"
                    "[Service]\n"
                    "User=example-app\n"
                    "Group=example-app\n"
                    "WorkingDirectory=/opt/example-app\n"
                    "EnvironmentFile=/opt/example-app/.env\n"
                    "ExecStart=/opt/example-app/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000\n"
                    "Restart=on-failure\n"
                    "\n"
                    "[Install]\n"
                    "WantedBy=multi-user.target"
                ),
            },
            {
                "command": "sudo systemctl daemon-reload",
                "description": "Wczytuje definicję nowej lub zmienionej jednostki.",
                "example": "$ sudo systemctl daemon-reload",
            },
            {
                "command": "sudo systemctl enable example-app.service",
                "description": "Włącza automatyczne uruchamianie aplikacji podczas startu systemu.",
                "example": "$ sudo systemctl enable example-app.service",
            },
            {
                "command": "sudo systemctl start example-app.service",
                "description": "Uruchamia usługę aplikacji w bieżącej sesji systemu.",
                "example": "$ sudo systemctl start example-app.service",
            },
            {
                "command": "sudo systemctl restart example-app.service",
                "description": "Restartuje usługę po świadomej zmianie kodu lub konfiguracji.",
                "example": "$ sudo systemctl restart example-app.service",
            },
            {
                "command": "systemctl status example-app.service",
                "description": "Pokazuje stan usługi, PID procesu i ostatnie komunikaty.",
                "example": "$ systemctl status example-app.service",
            },
            {
                "command": "journalctl -u example-app.service -n 50 --no-pager",
                "description": "Wyświetla 50 ostatnich wpisów dziennika aplikacji.",
                "example": "$ journalctl -u example-app.service -n 50 --no-pager",
            },
        ],
        "practice_task": (
            "W środowisku laboratoryjnym przygotuj plik <code>example-app.service</code> z trzema sekcjami. "
            "W <code>[Service]</code> ustaw <code>User=example-app</code>, <code>Group=example-app</code>, "
            "<code>WorkingDirectory=/opt/example-app</code>, "
            "<code>EnvironmentFile=/opt/example-app/.env</code>, "
            "<code>ExecStart=/opt/example-app/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000</code> "
            "oraz <code>Restart=on-failure</code>. Dodaj <code>WantedBy=multi-user.target</code>, wykonaj "
            "<code>daemon-reload</code>, włącz i uruchom usługę. Sprawdź <code>status</code>, logi oraz lokalną "
            "odpowiedź przez curl. Użyj wyłącznie aplikacji laboratoryjnej."
        ),
        "common_mistakes": [
            "Wskazanie globalnego Uvicorna zamiast programu z venv w ExecStart.",
            "Ustawienie katalogu roboczego, z którego nie można zaimportować modułu aplikacji.",
            "Uruchamianie usługi jako root mimo braku takiej potrzeby.",
            "Pominięcie daemon-reload po zmianie pliku jednostki.",
            "Założenie, że enable natychmiast uruchamia usługę.",
            "Restartowanie usługi bez przeczytania statusu i logów po błędzie.",
            "Nadanie użytkownikowi usługi braku dostępu do kodu lub pliku środowiskowego.",
        ],
        "summary": (
            "Jednostka systemd zamienia ręczne polecenie Uvicorna w zarządzaną usługę. Kluczowe pola to "
            "<code>User</code>, <code>Group</code>, <code>WorkingDirectory</code>, "
            "<code>EnvironmentFile</code> i <code>ExecStart</code>. Po zmianie jednostki trzeba wykonać "
            "<code>daemon-reload</code>, a autostart i bieżące uruchomienie kontroluje się oddzielnie. "
            "Stan procesu pokazuje <code>systemctl status</code>, a pełniejszą przyczynę problemu zwykle "
            "<code>journalctl -u</code>."
        ),
    },
    "quiz": {
        "title": "Quiz: aplikacja jako usługa systemd",
        "description": "Sprawdź konfigurację jednostki aplikacji webowej i jej diagnostykę.",
        "questions": [
            {
                "text": "W której sekcji jednostki umieszcza się ExecStart?",
                "answers": [
                    ("a", "[Service]", True),
                    ("b", "[Unit]", False),
                    ("c", "[Install]", False),
                    ("d", "[Network]", False),
                ],
            },
            {
                "text": "Po co ustawia się WorkingDirectory=/opt/example-app?",
                "answers": [
                    ("a", "Aby proces startował w katalogu, z którego może zaimportować aplikację", True),
                    ("b", "Aby utworzyć rekord DNS", False),
                    ("c", "Aby Nginx zaczął nasłuchiwać na porcie 80", False),
                    ("d", "Aby zmienić właściciela wszystkich plików systemu", False),
                ],
            },
            {
                "text": "Co powinien wskazywać ExecStart w tej konfiguracji?",
                "answers": [
                    ("a", "Uvicorna z venv wraz z punktem wejścia i adresem nasłuchu", True),
                    ("b", "Wyłącznie katalog /opt/example-app", False),
                    ("c", "Publiczny resolver DNS", False),
                    ("d", "Plik konfiguracji Nginxa bez polecenia", False),
                ],
            },
            {
                "text": "Kiedy wykonać systemctl daemon-reload?",
                "answers": [
                    ("a", "Po utworzeniu lub zmianie pliku jednostki", True),
                    ("b", "Po każdym żądaniu HTTP", False),
                    ("c", "Przed każdą komendą curl", False),
                    ("d", "Po zmianie rekordu A u operatora DNS", False),
                ],
            },
            {
                "text": "Jaka jest różnica między enable i start?",
                "answers": [
                    ("a", "Enable konfiguruje autostart, a start uruchamia usługę teraz", True),
                    ("b", "Enable czyta logi, a start tworzy venv", False),
                    ("c", "Enable testuje Nginx, a start ustawia DNS", False),
                    ("d", "Nie ma między nimi różnicy", False),
                ],
            },
            {
                "text": "Gdzie szukać pełniejszych logów example-app.service?",
                "answers": [
                    ("a", "W journalctl -u example-app.service", True),
                    ("b", "W pliku requirements.txt", False),
                    ("c", "W wyniku dig", False),
                    ("d", "W which python", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest jednostka service?", "answer": "Definicją sposobu zarządzania procesem usługi przez systemd."},
        {"question": "Gdzie zwykle umieszcza się własną jednostkę?", "answer": "W /etc/systemd/system, na przykład jako example-app.service."},
        {"question": "Do czego służy sekcja [Unit]?", "answer": "Opisuje jednostkę i jej relacje lub kolejność względem innych jednostek."},
        {"question": "Do czego służy sekcja [Service]?", "answer": "Określa użytkownika, środowisko i sposób uruchamiania procesu."},
        {"question": "Do czego służy sekcja [Install]?", "answer": "Opisuje między innymi sposób podłączenia jednostki do autostartu."},
        {"question": "Co ustawia User?", "answer": "Konto systemowe, jako które działa proces aplikacji."},
        {"question": "Co ustawia Group?", "answer": "Grupę systemową procesu aplikacji."},
        {"question": "Co ustawia WorkingDirectory?", "answer": "Katalog roboczy procesu przed wykonaniem ExecStart."},
        {"question": "Co wskazuje EnvironmentFile?", "answer": "Plik zawierający zmienne środowiskowe ładowane dla usługi."},
        {"question": "Co definiuje ExecStart?", "answer": "Dokładne polecenie uruchamiające główny proces usługi."},
        {"question": "Jak wskazać Uvicorn z venv?", "answer": "Pełną ścieżką /opt/example-app/venv/bin/uvicorn."},
        {"question": "Co daje Restart=on-failure?", "answer": "Pozwala systemd ponownie uruchomić proces po nieoczekiwanym błędzie."},
        {"question": "Czy Restart naprawia błędny kod?", "answer": "Nie, może jedynie ponawiać uruchomienie wadliwego procesu."},
        {"question": "Co robi daemon-reload?", "answer": "Wczytuje ponownie definicje jednostek systemd."},
        {"question": "Co robi systemctl enable?", "answer": "Konfiguruje uruchamianie jednostki przy starcie systemu."},
        {"question": "Co robi systemctl start?", "answer": "Uruchamia jednostkę teraz."},
        {"question": "Co robi systemctl restart?", "answer": "Zatrzymuje i ponownie uruchamia jednostkę."},
        {"question": "Co pokazuje systemctl status?", "answer": "Bieżący stan, PID i ostatnie komunikaty jednostki."},
        {"question": "Jak wyświetlić logi jednej usługi?", "answer": "Poleceniem journalctl -u nazwa.service."},
        {"question": "Co oznacza WantedBy=multi-user.target?", "answer": "Pozwala powiązać usługę z typowym wieloużytkownikowym startem systemu."},
        {"question": "Czy enable uruchamia usługę od razu?", "answer": "Nie, chyba że użyto wariantu enable --now."},
        {"question": "Dlaczego nie uruchamiać aplikacji jako root?", "answer": "Ograniczone konto zmniejsza skutki błędu lub przejęcia procesu."},
        {"question": "Co sprawdzić po starcie usługi?", "answer": "Status, logi, nasłuch portu i odpowiedź HTTP."},
        {"question": "Co może powodować błąd importu modułu?", "answer": "Niewłaściwy WorkingDirectory lub błędny zapis punktu wejścia."},
        {"question": "Co może powodować błąd odczytu .env?", "answer": "Nieistniejący plik albo nieprawidłowe uprawnienia użytkownika usługi."},
    ],
}
