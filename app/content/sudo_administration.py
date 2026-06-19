SUDO_ADMINISTRATION = {
    "module": {
        "title": "Administracja systemem",
        "description": "Moduł poświęcony podstawowej administracji systemem Linux.",
    },
    "lesson": {
        "title": "Sudo i praca administratora: sudo, su, root i dobre praktyki",
        "level": "Podstawowy+",
        "duration": "40 min",
        "description": (
            "Poznasz różnice między sudo, su i kontem root oraz nauczysz się wykonywać "
            "zadania administracyjne z możliwie najmniejszym zakresem uprawnień."
        ),
        "theory": (
            "Konto <code>root</code> ma pełne uprawnienia w systemie, dlatego błąd wykonany jako "
            "root może zmienić lub usunąć ważne dane. W codziennej pracy bezpieczniej korzystać "
            "ze zwykłego konta i podnosić uprawnienia tylko dla konkretnego polecenia przez "
            "<code>sudo</code>. Dostęp do sudo wynika z konfiguracji systemu; w Rocky Linux 9 "
            "często otrzymują go członkowie grupy <code>wheel</code>. Komenda <code>sudo -l</code> "
            "pokazuje, jakie polecenia użytkownik może uruchamiać. <code>sudo polecenie</code> "
            "wykonuje pojedynczą operację z podwyższonymi uprawnieniami, a <code>sudo -i</code> "
            "otwiera powłokę administracyjną i powinno być używane tylko wtedy, gdy jest naprawdę "
            "potrzebne. <code>su - użytkownik</code> przełącza konto i uruchamia jego środowisko "
            "logowania; <code>su -</code> zwykle oznacza próbę przejścia na konto root. "
            "Po zakończeniu pracy uprzywilejowanej należy użyć <code>exit</code>. Dobra praktyka "
            "to sprawdzanie polecenia przed uruchomieniem, unikanie długiej pracy jako root, "
            "niekopiowanie nieznanych komend z internetu oraz niewprowadzanie zmian, których "
            "skutków się nie rozumie."
        ),
        "commands": [
            {
                "command": "sudo -l",
                "description": "Pokazuje polecenia, które aktualny użytkownik może uruchamiać przez sudo.",
                "example": "$ sudo -l",
            },
            {
                "command": "sudo whoami",
                "description": "Uruchamia pojedyncze polecenie z podwyższonymi uprawnieniami.",
                "example": "$ sudo whoami\nroot",
            },
            {
                "command": "sudo cat /etc/ssh/sshd_config",
                "description": "Odczytuje chroniony plik bez otwierania stałej sesji root.",
                "example": "$ sudo cat /etc/ssh/sshd_config",
            },
            {
                "command": "sudo -i",
                "description": "Otwiera powłokę logowania root, gdy seria zadań tego wymaga.",
                "example": "$ sudo -i\n# whoami\nroot",
            },
            {
                "command": "su - anna",
                "description": "Przełącza się na konto anna wraz z jego środowiskiem logowania.",
                "example": "$ su - anna",
            },
            {
                "command": "exit",
                "description": "Kończy bieżącą powłokę i wraca do poprzedniego użytkownika.",
                "example": "# exit\n$",
            },
            {
                "command": "id",
                "description": "Pomaga sprawdzić aktualny UID, GID i przynależność do grup.",
                "example": "$ id",
            },
        ],
        "practice_task": (
            "W środowisku laboratoryjnym wykonaj <code>whoami</code> i <code>id</code>, a następnie "
            "<code>sudo -l</code>, aby sprawdzić swój zakres uprawnień. Jeśli konto ma dostęp do "
            "sudo, uruchom <code>sudo whoami</code> i porównaj wynik ze zwykłym "
            "<code>whoami</code>. Odczytaj chroniony plik poleceniem "
            "<code>sudo cat /etc/ssh/sshd_config</code>, nie modyfikując go. Na końcu wyjaśnij, "
            "dlaczego pojedyncze użycie sudo jest bezpieczniejsze niż pozostawanie w powłoce root."
        ),
        "common_mistakes": [
            "Wykonywanie całej codziennej pracy jako root zamiast używania sudo do pojedynczych poleceń.",
            "Uruchamianie skopiowanych komend przez sudo bez sprawdzenia ich działania.",
            "Mylenie hasła własnego konta używanego przez sudo z hasłem konta docelowego używanym przez su.",
            "Zakładanie, że każdy użytkownik automatycznie może korzystać z sudo.",
            "Używanie <code>sudo -i</code> do zadania, które wymaga tylko jednego polecenia.",
            "Brak sprawdzenia aktualnego użytkownika przed wykonaniem ryzykownej operacji.",
            "Pozostawianie otwartej powłoki root po zakończeniu zadania.",
        ],
        "summary": (
            "<code>root</code> ma pełną kontrolę nad systemem, dlatego uprawnienia administracyjne "
            "należy stosować oszczędnie. <code>sudo</code> najlepiej nadaje się do uruchamiania "
            "pojedynczych poleceń, <code>sudo -l</code> pokazuje dostępny zakres uprawnień, a "
            "<code>su -</code> przełącza konto i środowisko logowania. Powłoka root powinna być "
            "krótkotrwała, świadomie używana i zamykana przez <code>exit</code>."
        ),
    },
    "quiz": {
        "title": "Quiz: sudo i praca administratora",
        "description": "Sprawdź, czy bezpiecznie korzystasz z uprawnień administracyjnych.",
        "questions": [
            {
                "text": "Chcesz wykonać jedno polecenie wymagające uprawnień administratora. Co jest najlepszym wyborem?",
                "answers": [
                    ("a", "Uruchomić je przez sudo", True),
                    ("b", "Zalogować się jako root na cały dzień", False),
                    ("c", "Nadać wszystkim pełne uprawnienia", False),
                    ("d", "Wyłączyć kontrolę dostępu", False),
                ],
            },
            {
                "text": "Co pokazuje komenda sudo -l?",
                "answers": [
                    ("a", "Polecenia dozwolone dla użytkownika przez sudo", True),
                    ("b", "Listę wszystkich plików w /var/log", False),
                    ("c", "Wyłącznie historię logowań root", False),
                    ("d", "Wolne miejsce na dysku", False),
                ],
            },
            {
                "text": "Dlaczego długa praca w powłoce root zwiększa ryzyko?",
                "answers": [
                    ("a", "Każde polecenie ma pełne uprawnienia i błąd może uszkodzić system", True),
                    ("b", "Root nie może czytać plików konfiguracyjnych", False),
                    ("c", "Powłoka root zawsze wyłącza sieć", False),
                    ("d", "Root nie może uruchamiać programów", False),
                ],
            },
            {
                "text": "Co robi su - anna?",
                "answers": [
                    ("a", "Przełącza na konto anna wraz z jego środowiskiem logowania", True),
                    ("b", "Usuwa konto anna", False),
                    ("c", "Dodaje konto anna do grupy wheel", False),
                    ("d", "Zmienia hasło konta anna", False),
                ],
            },
            {
                "text": "Która grupa w Rocky Linux 9 jest często używana do przyznawania dostępu do sudo?",
                "answers": [
                    ("a", "wheel", True),
                    ("b", "audio", False),
                    ("c", "nobody", False),
                    ("d", "mail", False),
                ],
            },
            {
                "text": "Co należy zrobić po zakończeniu pracy w tymczasowej powłoce root?",
                "answers": [
                    ("a", "Zakończyć ją poleceniem exit", True),
                    ("b", "Pozostawić ją otwartą na później", False),
                    ("c", "Usunąć konto zwykłego użytkownika", False),
                    ("d", "Nadać wszystkim dostęp do sudo", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Kim jest użytkownik root?",
            "answer": "To konto administracyjne mające pełne uprawnienia w systemie.",
        },
        {
            "question": "Dlaczego konto root wymaga ostrożności?",
            "answer": "Błędne polecenie wykonane jako root może zmienić lub usunąć ważne dane.",
        },
        {
            "question": "Do czego służy sudo?",
            "answer": "Do uruchamiania dozwolonych poleceń z podwyższonymi uprawnieniami.",
        },
        {
            "question": "Co robi sudo -l?",
            "answer": "Pokazuje, jakie polecenia użytkownik może uruchamiać przez sudo.",
        },
        {
            "question": "Co sprawdza sudo whoami?",
            "answer": "Pokazuje użytkownika, jako którego wykonano polecenie przez sudo.",
        },
        {
            "question": "Jaki wynik zwykle zwraca sudo whoami?",
            "answer": "root, jeśli sudo uruchamia polecenie z domyślnymi uprawnieniami administratora.",
        },
        {
            "question": "Czy każdy użytkownik może używać sudo?",
            "answer": "Nie. Musi mieć odpowiednie uprawnienia w konfiguracji sudo.",
        },
        {
            "question": "Jaka grupa często daje dostęp do sudo w Rocky Linux 9?",
            "answer": "Grupa wheel, jeśli standardowa reguła sudo jest aktywna.",
        },
        {
            "question": "Co robi sudo -i?",
            "answer": "Otwiera powłokę logowania root.",
        },
        {
            "question": "Kiedy warto użyć sudo -i?",
            "answer": "Tylko gdy seria świadomych zadań rzeczywiście wymaga powłoki root.",
        },
        {
            "question": "Co robi su - anna?",
            "answer": "Przełącza na konto anna i ładuje jego środowisko logowania.",
        },
        {
            "question": "Co zwykle oznacza su - bez nazwy użytkownika?",
            "answer": "Próbę przełączenia na konto root wraz z jego środowiskiem.",
        },
        {
            "question": "Czym różni się sudo od su?",
            "answer": "sudo uruchamia dozwolone polecenie, a su przełącza bieżące konto użytkownika.",
        },
        {
            "question": "Jakiego hasła zwykle żąda sudo?",
            "answer": "Hasła aktualnego użytkownika, zależnie od konfiguracji systemu.",
        },
        {
            "question": "Jakiego hasła zwykle żąda su?",
            "answer": "Hasła konta docelowego, zależnie od konfiguracji uwierzytelniania.",
        },
        {
            "question": "Do czego służy exit?",
            "answer": "Kończy bieżącą powłokę i wraca do poprzedniej sesji.",
        },
        {
            "question": "Dlaczego warto sprawdzić whoami przed zmianą systemu?",
            "answer": "Aby upewnić się, z jakimi uprawnieniami pracujesz.",
        },
        {
            "question": "Dlaczego sudo do jednego polecenia jest bezpieczniejsze?",
            "answer": "Ogranicza czas i zakres pracy z pełnymi uprawnieniami.",
        },
        {
            "question": "Czy sudo automatycznie czyni polecenie bezpiecznym?",
            "answer": "Nie. Nadal trzeba rozumieć polecenie i jego skutki.",
        },
        {
            "question": "Co zrobić przed uruchomieniem nieznanej komendy przez sudo?",
            "answer": "Sprawdzić jej składnię, źródło i możliwe skutki.",
        },
        {
            "question": "Czy warto pozostawiać otwartą powłokę root?",
            "answer": "Nie. Po zakończeniu zadania należy ją zamknąć.",
        },
        {
            "question": "Czy brak dostępu do sudo jest błędem systemu?",
            "answer": "Nie zawsze. Może być zamierzoną polityką bezpieczeństwa.",
        },
        {
            "question": "Jak sprawdzić przynależność do grup?",
            "answer": "Za pomocą komendy id lub groups.",
        },
        {
            "question": "Czy grupa wheel zawsze gwarantuje dostęp do sudo?",
            "answer": "Nie. Zależy to od aktywnej konfiguracji sudo.",
        },
        {
            "question": "Jaka jest podstawowa zasada pracy administratora?",
            "answer": "Używać najmniejszych uprawnień wystarczających do wykonania zadania.",
        },
    ],
}
