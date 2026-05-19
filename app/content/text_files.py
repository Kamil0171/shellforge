TEXT_FILES = {
    "module": {
        "title": "Podstawy terminala",
        "description": "Pierwszy moduł poświęcony pracy w terminalu Linux.",
    },
    "lesson": {
        "title": "Praca z plikami tekstowymi: cat, less, tail, grep i nano",
        "level": "Podstawowy",
        "duration": "35 min",
        "description": (
            "Poznasz podstawowe narzędzia do czytania, przeglądania, wyszukiwania i prostej edycji "
            "plików tekstowych w terminalu Linux."
        ),
        "theory": (
            "W Linuxie wiele ważnych informacji znajduje się w plikach tekstowych. Plikami tekstowymi "
            "są między innymi pliki konfiguracyjne, listy użytkowników, ustawienia usług oraz logi. "
            "Dlatego administrator systemu powinien umieć szybko podejrzeć zawartość pliku, wygodnie "
            "przewijać dłuższy tekst, sprawdzić ostatnie linie logu, wyszukać konkretny fragment oraz "
            "bezpiecznie wykonać prostą edycję. Do podstawowych narzędzi należą cat, less, head, tail, "
            "grep oraz nano. Te komendy są fundamentem późniejszej pracy z konfiguracją usług, "
            "diagnostyką błędów i analizą logów."
        ),
        "commands": [
            {
                "command": "cat /etc/os-release",
                "description": "Wyświetla całą zawartość krótkiego pliku tekstowego.",
                "example": "$ cat /etc/os-release\nNAME=\"Rocky Linux\"\nVERSION=\"9\"",
            },
            {
                "command": "less /etc/ssh/sshd_config",
                "description": "Otwiera plik w wygodnym podglądzie z możliwością przewijania.",
                "example": "$ less /etc/ssh/sshd_config",
            },
            {
                "command": "head /var/log/messages",
                "description": "Wyświetla początkowe linie pliku.",
                "example": "$ head /var/log/messages",
            },
            {
                "command": "tail /var/log/messages",
                "description": "Wyświetla końcowe linie pliku.",
                "example": "$ tail /var/log/messages",
            },
            {
                "command": "tail -f /var/log/messages",
                "description": "Obserwuje dopisywane na bieżąco linie pliku, co jest przydatne przy logach.",
                "example": "$ tail -f /var/log/messages",
            },
            {
                "command": "grep PermitRootLogin /etc/ssh/sshd_config",
                "description": "Wyszukuje w pliku linie zawierające podany tekst.",
                "example": "$ grep PermitRootLogin /etc/ssh/sshd_config",
            },
            {
                "command": "grep -i error /var/log/messages",
                "description": "Wyszukuje tekst bez rozróżniania wielkości liter.",
                "example": "$ grep -i error /var/log/messages",
            },
            {
                "command": "grep -n server_name /etc/nginx/nginx.conf",
                "description": "Wyszukuje tekst i pokazuje numery pasujących linii.",
                "example": "$ grep -n server_name /etc/nginx/nginx.conf",
            },
            {
                "command": "nano /opt/example-app/.env",
                "description": "Otwiera plik do prostej edycji w terminalu.",
                "example": "$ nano /opt/example-app/.env",
            },
        ],
        "practice_task": (
            "Wykonaj kolejno: <code>cat /etc/os-release</code>, <code>less /etc/os-release</code>, "
            "<code>head /etc/os-release</code> oraz <code>tail /etc/os-release</code>. W programie "
            "<code>less</code> wyjdź klawiszem <code>q</code>. Następnie użyj <code>grep</code>, aby "
            "wyszukać wybrany tekst w pliku, na przykład <code>grep NAME /etc/os-release</code>. "
            "Na końcu otwórz testowy plik w <code>nano</code>, zapisz zmianę skrótem "
            "<code>Ctrl + O</code>, zatwierdź klawiszem Enter i wyjdź skrótem <code>Ctrl + X</code>."
        ),
        "common_mistakes": [
            "Używanie <code>cat</code> do bardzo długich plików zamiast <code>less</code>.",
            "Zapominanie, że z programu <code>less</code> wychodzi się klawiszem <code>q</code>.",
            "Mylenie <code>head</code> i <code>tail</code>.",
            "Używanie <code>tail -f</code> bez wiedzy, że działanie można przerwać skrótem <code>Ctrl + C</code>.",
            "Wyszukiwanie tekstu komendą <code>grep</code> bez sprawdzenia wielkości liter.",
            "Edycja ważnych plików konfiguracyjnych bez wcześniejszego sprawdzenia ich zawartości.",
            "Zapominanie o zapisaniu zmian w <code>nano</code> przed wyjściem.",
        ],
        "summary": (
            "Pliki tekstowe są bardzo ważne w codziennej pracy z Linuxem. Komenda <code>cat</code> "
            "pozwala szybko wyświetlić krótki plik, <code>less</code> ułatwia przeglądanie dłuższych "
            "plików, <code>head</code> i <code>tail</code> pokazują początek oraz koniec pliku, "
            "<code>tail -f</code> pozwala obserwować logi, <code>grep</code> wyszukuje tekst, a "
            "<code>nano</code> umożliwia prostą edycję plików w terminalu."
        ),
    },
    "quiz": {
        "title": "Quiz: praca z plikami tekstowymi",
        "description": "Sprawdź, czy rozumiesz podstawowe komendy do pracy z plikami tekstowymi.",
        "questions": [
            {
                "text": "Do czego służy komenda cat?",
                "answers": [
                    ("a", "Do szybkiego wyświetlania zawartości pliku", True),
                    ("b", "Do zmiany właściciela pliku", False),
                    ("c", "Do tworzenia użytkowników", False),
                    ("d", "Do restartowania usług", False),
                ],
            },
            {
                "text": "Która komenda jest wygodniejsza do przeglądania długiego pliku?",
                "answers": [
                    ("a", "rm", False),
                    ("b", "less", True),
                    ("c", "mkdir", False),
                    ("d", "id", False),
                ],
            },
            {
                "text": "Jak wyjść z programu less?",
                "answers": [
                    ("a", "Klawiszem q", True),
                    ("b", "Komendą rm", False),
                    ("c", "Klawiszem F1", False),
                    ("d", "Komendą chmod", False),
                ],
            },
            {
                "text": "Co robi komenda tail?",
                "answers": [
                    ("a", "Pokazuje końcowe linie pliku", True),
                    ("b", "Pokazuje tylko katalogi", False),
                    ("c", "Usuwa końcówkę pliku", False),
                    ("d", "Zmienia uprawnienia", False),
                ],
            },
            {
                "text": "Do czego służy tail -f?",
                "answers": [
                    ("a", "Do obserwowania dopisywanych na bieżąco linii pliku", True),
                    ("b", "Do formatowania dysku", False),
                    ("c", "Do instalowania pakietów", False),
                    ("d", "Do tworzenia grup", False),
                ],
            },
            {
                "text": "Do czego służy grep?",
                "answers": [
                    ("a", "Do wyszukiwania tekstu w plikach lub wyniku komendy", True),
                    ("b", "Do kopiowania katalogów", False),
                    ("c", "Do zatrzymywania procesów", False),
                    ("d", "Do zmiany hasła", False),
                ],
            },
            {
                "text": "Co oznacza opcja -i w grep?",
                "answers": [
                    ("a", "Wyszukiwanie bez rozróżniania wielkości liter", True),
                    ("b", "Usunięcie pliku po wyszukaniu", False),
                    ("c", "Pokazanie tylko pierwszej linii", False),
                    ("d", "Uruchomienie trybu graficznego", False),
                ],
            },
            {
                "text": "Co oznacza opcja -n w grep?",
                "answers": [
                    ("a", "Pokazanie numerów pasujących linii", True),
                    ("b", "Utworzenie nowego użytkownika", False),
                    ("c", "Ukrycie wszystkich wyników", False),
                    ("d", "Zamknięcie terminala", False),
                ],
            },
            {
                "text": "Do czego służy nano?",
                "answers": [
                    ("a", "Do prostej edycji plików tekstowych w terminalu", True),
                    ("b", "Do monitorowania procesów", False),
                    ("c", "Do sprawdzania adresu IP", False),
                    ("d", "Do kompresowania pakietów", False),
                ],
            },
            {
                "text": "Jak w nano zapisać plik?",
                "answers": [
                    ("a", "Ctrl + O, a następnie Enter", True),
                    ("b", "Ctrl + Q bez potwierdzenia", False),
                    ("c", "Komendą ps", False),
                    ("d", "Klawiszem q", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Do czego służy cat?",
            "answer": "Do szybkiego wyświetlania zawartości pliku tekstowego.",
        },
        {
            "question": "Kiedy lepiej użyć less zamiast cat?",
            "answer": "Gdy plik jest długi i chcemy go wygodnie przewijać.",
        },
        {
            "question": "Jak wyjść z less?",
            "answer": "Klawiszem q.",
        },
        {
            "question": "Co robi head?",
            "answer": "Wyświetla początkowe linie pliku.",
        },
        {
            "question": "Co robi tail?",
            "answer": "Wyświetla końcowe linie pliku.",
        },
        {
            "question": "Co robi tail -f?",
            "answer": "Obserwuje dopisywane na bieżąco linie pliku, na przykład logu.",
        },
        {
            "question": "Jak przerwać tail -f?",
            "answer": "Skrótem Ctrl + C.",
        },
        {
            "question": "Do czego służy grep?",
            "answer": "Do wyszukiwania tekstu w plikach lub wyniku komendy.",
        },
        {
            "question": "Co robi grep -i?",
            "answer": "Wyszukuje tekst bez rozróżniania wielkości liter.",
        },
        {
            "question": "Co robi grep -n?",
            "answer": "Pokazuje numery linii, w których znaleziono dopasowanie.",
        },
        {
            "question": "Do czego służy nano?",
            "answer": "Do prostej edycji plików tekstowych w terminalu.",
        },
        {
            "question": "Jak zapisać plik w nano?",
            "answer": "Skrótem Ctrl + O, a potem klawiszem Enter.",
        },
        {
            "question": "Jak wyjść z nano?",
            "answer": "Skrótem Ctrl + X.",
        },
        {
            "question": "Dlaczego pliki tekstowe są ważne w Linuxie?",
            "answer": "Bo wiele konfiguracji, ustawień i logów ma formę plików tekstowych.",
        },
        {
            "question": "Jaki plik pokazuje informacje o systemie?",
            "answer": "Na wielu dystrybucjach jest to /etc/os-release.",
        },
        {
            "question": "Jaki przykład pliku konfiguracyjnego można przeglądać w less?",
            "answer": "Na przykład /etc/ssh/sshd_config.",
        },
        {
            "question": "Jaki przykład logu można obserwować przez tail -f?",
            "answer": "Na przykład /var/log/messages.",
        },
        {
            "question": "Czy cat jest dobry do bardzo długich plików?",
            "answer": "Nie. Do długich plików wygodniejszy jest less.",
        },
        {
            "question": "Co warto zrobić przed edycją ważnego pliku?",
            "answer": "Najpierw przeczytać jego zawartość i upewnić się, co chcemy zmienić.",
        },
        {
            "question": "Która komenda pomaga znaleźć konkretną linijkę konfiguracji?",
            "answer": "grep.",
        },
    ],
}