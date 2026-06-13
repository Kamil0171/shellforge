ADMIN_DIRECTORIES = {
    "module": {
        "title": "Administracja systemem",
        "description": "Moduł poświęcony podstawowej administracji systemem Linux.",
    },
    "lesson": {
        "title": "Struktura katalogów administracyjnych: /etc, /var, /opt, /usr i /tmp",
        "level": "Podstawowy",
        "duration": "35 min",
        "description": (
            "Poznasz najważniejsze katalogi używane w administracji Linuxem oraz nauczysz się "
            "bezpiecznie przeglądać ich zawartość bez modyfikowania konfiguracji systemu."
        ),
        "theory": (
            "Katalog domowy użytkownika, na przykład <code>/home/anna</code>, służy głównie do "
            "przechowywania prywatnych plików, konfiguracji użytkownika i codziennej pracy. "
            "Katalogi systemowe mają inną rolę: zawierają konfigurację, logi, programy, dane usług "
            "oraz pliki tymczasowe. Administrator powinien umieć je rozpoznać, ale na początku "
            "najważniejsze jest bezpieczne przeglądanie, a nie edycja. Katalog <code>/etc</code> "
            "zawiera konfigurację systemu i usług. Katalog <code>/var</code> przechowuje dane, "
            "które zmieniają się podczas działania systemu, a <code>/var/log</code> jest typowym "
            "miejscem logów. Katalog <code>/opt</code> bywa używany dla dodatkowego oprogramowania "
            "instalowanego poza standardowym menedżerem pakietów. W <code>/usr</code> znajdują się "
            "programy, biblioteki i współdzielone zasoby systemowe. Katalog <code>/tmp</code> służy "
            "do plików tymczasowych. Bezpieczne poznawanie tych miejsc polega na używaniu komend "
            "odczytujących dane, takich jak <code>ls</code>, <code>du</code> i <code>file</code>, "
            "oraz unikaniu przypadkowego usuwania lub edycji plików systemowych."
        ),
        "commands": [
            {
                "command": "ls /etc",
                "description": "Wyświetla pliki i katalogi konfiguracyjne systemu.",
                "example": "$ ls /etc",
            },
            {
                "command": "ls /var",
                "description": "Pokazuje katalogi z danymi zmiennymi systemu i usług.",
                "example": "$ ls /var",
            },
            {
                "command": "ls /var/log",
                "description": "Wyświetla katalogi i pliki z logami systemowymi.",
                "example": "$ ls /var/log",
            },
            {
                "command": "ls /opt",
                "description": "Pokazuje dodatkowe oprogramowanie instalowane w /opt, jeśli istnieje.",
                "example": "$ ls /opt",
            },
            {
                "command": "ls /usr",
                "description": "Wyświetla główne katalogi z programami i zasobami systemowymi.",
                "example": "$ ls /usr",
            },
            {
                "command": "ls /tmp",
                "description": "Pokazuje pliki tymczasowe dostępne w katalogu /tmp.",
                "example": "$ ls /tmp",
            },
            {
                "command": "du -sh /var/log",
                "description": "Pokazuje łączny rozmiar katalogu z logami w czytelnej formie.",
                "example": "$ du -sh /var/log",
            },
            {
                "command": "file /etc/passwd",
                "description": "Sprawdza typ pliku /etc/passwd bez otwierania go do edycji.",
                "example": "$ file /etc/passwd",
            },
        ],
        "practice_task": (
            "Przejrzyj wybrane katalogi systemowe tylko komendami odczytującymi dane. Wykonaj "
            "<code>ls /etc</code>, <code>ls /var</code>, <code>ls /var/log</code>, "
            "<code>ls /opt</code>, <code>ls /usr</code> i <code>ls /tmp</code>. Następnie sprawdź "
            "rozmiar logów przez <code>du -sh /var/log</code> oraz typ pliku "
            "<code>/etc/passwd</code> komendą <code>file /etc/passwd</code>. Zapisz, które katalogi "
            "są związane z konfiguracją, które z logami, a które z programami lub plikami "
            "tymczasowymi."
        ),
        "common_mistakes": [
            "Mylenie katalogu domowego użytkownika z katalogami systemowymi.",
            "Edytowanie plików w <code>/etc</code> bez kopii zapasowej i zrozumienia skutków.",
            "Usuwanie plików z <code>/var/log</code> zamiast najpierw sprawdzić ich rozmiar i rotację logów.",
            "Zakładanie, że katalog <code>/tmp</code> jest dobrym miejscem na trwałe dane.",
            "Instalowanie własnych plików w przypadkowych katalogach systemowych.",
            "Używanie komend usuwających w katalogach systemowych bez sprawdzenia aktualnej ścieżki.",
            "Ignorowanie komunikatów o braku uprawnień zamiast rozumienia, że część danych jest chroniona.",
        ],
        "summary": (
            "Katalogi administracyjne mają konkretne role. <code>/etc</code> przechowuje "
            "konfigurację, <code>/var</code> dane zmienne, <code>/var/log</code> logi, "
            "<code>/opt</code> dodatkowe oprogramowanie, <code>/usr</code> programy i zasoby "
            "systemowe, a <code>/tmp</code> pliki tymczasowe. Na początku najbezpieczniej jest "
            "poznawać je przez komendy odczytu, takie jak <code>ls</code>, <code>du -sh</code> "
            "i <code>file</code>."
        ),
    },
    "quiz": {
        "title": "Quiz: katalogi administracyjne",
        "description": "Sprawdź, czy rozumiesz role katalogów /etc, /var, /opt, /usr i /tmp.",
        "questions": [
            {
                "text": "Do czego najczęściej służy katalog /etc?",
                "answers": [
                    ("a", "Do przechowywania konfiguracji systemu i usług", True),
                    ("b", "Do zapisywania prywatnych zdjęć użytkownika", False),
                    ("c", "Do montowania nośników USB", False),
                    ("d", "Do przechowywania wyłącznie plików tymczasowych", False),
                ],
            },
            {
                "text": "Który katalog zwykle zawiera logi systemowe?",
                "answers": [
                    ("a", "/var/log", True),
                    ("b", "/home/log", False),
                    ("c", "/usr/tmp", False),
                    ("d", "/etc/bin", False),
                ],
            },
            {
                "text": "Co pokazuje komenda du -sh /var/log?",
                "answers": [
                    ("a", "Łączny rozmiar katalogu /var/log w czytelnej formie", True),
                    ("b", "Listę wszystkich użytkowników systemu", False),
                    ("c", "Zawartość pliku /etc/passwd", False),
                    ("d", "Aktualny load average", False),
                ],
            },
            {
                "text": "Do czego służy katalog /tmp?",
                "answers": [
                    ("a", "Do plików tymczasowych", True),
                    ("b", "Do stałego przechowywania konfiguracji usług", False),
                    ("c", "Do plików jądra systemu", False),
                    ("d", "Do domowych katalogów użytkowników", False),
                ],
            },
            {
                "text": "Co robi komenda file /etc/passwd?",
                "answers": [
                    ("a", "Sprawdza typ pliku /etc/passwd", True),
                    ("b", "Zmienia hasło użytkownika root", False),
                    ("c", "Usuwa plik /etc/passwd", False),
                    ("d", "Przenosi plik do /tmp", False),
                ],
            },
            {
                "text": "Które podejście jest najbezpieczniejsze podczas pierwszego poznawania katalogów systemowych?",
                "answers": [
                    ("a", "Używanie komend odczytujących dane, takich jak ls, du i file", True),
                    ("b", "Usuwanie nieznanych plików, żeby zwolnić miejsce", False),
                    ("c", "Edytowanie konfiguracji bez kopii zapasowej", False),
                    ("d", "Przenoszenie katalogów systemowych do katalogu domowego", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Czym różni się katalog domowy od katalogów systemowych?",
            "answer": "Katalog domowy przechowuje pliki użytkownika, a katalogi systemowe konfigurację, programy, logi i dane usług.",
        },
        {
            "question": "Do czego służy /etc?",
            "answer": "Do przechowywania konfiguracji systemu i usług.",
        },
        {
            "question": "Jaka komenda pokazuje zawartość /etc?",
            "answer": "ls /etc.",
        },
        {
            "question": "Do czego służy /var?",
            "answer": "Do danych zmieniających się podczas pracy systemu i usług.",
        },
        {
            "question": "Jaka komenda pokazuje zawartość /var?",
            "answer": "ls /var.",
        },
        {
            "question": "Do czego służy /var/log?",
            "answer": "Do przechowywania logów systemowych i logów usług.",
        },
        {
            "question": "Jaka komenda pokazuje zawartość /var/log?",
            "answer": "ls /var/log.",
        },
        {
            "question": "Co robi du -sh /var/log?",
            "answer": "Pokazuje łączny rozmiar katalogu /var/log w czytelnej formie.",
        },
        {
            "question": "Do czego służy /opt?",
            "answer": "Często do dodatkowego oprogramowania instalowanego poza standardowym układem systemu.",
        },
        {
            "question": "Jaka komenda pokazuje zawartość /opt?",
            "answer": "ls /opt.",
        },
        {
            "question": "Do czego służy /usr?",
            "answer": "Do programów, bibliotek i współdzielonych zasobów systemowych.",
        },
        {
            "question": "Jaka komenda pokazuje zawartość /usr?",
            "answer": "ls /usr.",
        },
        {
            "question": "Do czego służy /tmp?",
            "answer": "Do plików tymczasowych.",
        },
        {
            "question": "Jaka komenda pokazuje zawartość /tmp?",
            "answer": "ls /tmp.",
        },
        {
            "question": "Czy /tmp jest dobrym miejscem na trwałe dane?",
            "answer": "Nie. To katalog na pliki tymczasowe.",
        },
        {
            "question": "Co robi file /etc/passwd?",
            "answer": "Sprawdza typ pliku /etc/passwd.",
        },
        {
            "question": "Czy ls modyfikuje katalog systemowy?",
            "answer": "Nie. ls tylko wyświetla zawartość.",
        },
        {
            "question": "Dlaczego trzeba uważać w /etc?",
            "answer": "Bo znajdują się tam ważne pliki konfiguracyjne systemu i usług.",
        },
        {
            "question": "Dlaczego trzeba uważać w /var/log?",
            "answer": "Bo logi mogą być potrzebne do diagnostyki problemów.",
        },
        {
            "question": "Co warto zrobić przed użyciem komend usuwających w katalogach systemowych?",
            "answer": "Sprawdzić aktualną ścieżkę i upewnić się, co dokładnie zostanie usunięte.",
        },
        {
            "question": "Czy brak uprawnień w katalogu systemowym zawsze oznacza błąd?",
            "answer": "Nie. Część plików jest celowo chroniona przed zwykłym użytkownikiem.",
        },
        {
            "question": "Co oznacza bezpieczne przeglądanie katalogów systemowych?",
            "answer": "Używanie komend odczytu i unikanie przypadkowej edycji lub usuwania plików.",
        },
        {
            "question": "Które komendy z tej lekcji są komendami odczytu?",
            "answer": "ls, du -sh i file.",
        },
        {
            "question": "Gdzie administrator zwykle szuka konfiguracji usług?",
            "answer": "W katalogu /etc.",
        },
        {
            "question": "Gdzie administrator zwykle zaczyna szukać klasycznych plików logów?",
            "answer": "W katalogu /var/log.",
        },
    ],
}
