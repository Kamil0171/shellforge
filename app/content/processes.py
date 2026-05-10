PROCESSES = {
    "module": {
        "title": "Podstawy terminala",
        "description": "Pierwszy moduł poświęcony pracy w terminalu Linux.",
    },
    "lesson": {
        "title": "Procesy w Linuxie: ps, top, kill i PID",
        "level": "Podstawowy",
        "duration": "30 min",
        "description": (
            "Poznasz podstawowe pojęcia związane z procesami w Linuxie: PID, uruchomione programy, "
            "podgląd procesów oraz bezpieczne kończenie działania procesu."
        ),
        "theory": (
            "Proces to uruchomiony program działający w systemie. Każdy proces ma swój unikalny "
            "identyfikator PID. Linux pozwala sprawdzać działające procesy, obserwować zużycie zasobów "
            "oraz kończyć procesy, które przestały odpowiadać. Do podstawowych komend należą ps, top, "
            "kill oraz pgrep. Umiejętność pracy z procesami jest ważna przy administracji systemem, "
            "diagnozowaniu problemów i utrzymywaniu aplikacji."
        ),
        "commands": [
            {
                "command": "ps",
                "description": "Wyświetla procesy uruchomione w aktualnej sesji terminala.",
                "example": "$ ps\nPID TTY          TIME CMD\n1234 pts/0    00:00:00 bash",
            },
            {
                "command": "ps aux",
                "description": "Wyświetla szeroką listę procesów działających w systemie.",
                "example": "$ ps aux",
            },
            {
                "command": "top",
                "description": "Pokazuje dynamiczny podgląd procesów i zużycia zasobów systemu.",
                "example": "$ top",
            },
            {
                "command": "pgrep nginx",
                "description": "Wyszukuje PID procesów pasujących do podanej nazwy.",
                "example": "$ pgrep nginx\n1320\n1321",
            },
            {
                "command": "kill 1234",
                "description": "Wysyła sygnał zakończenia do procesu o PID 1234.",
                "example": "$ kill 1234",
            },
            {
                "command": "kill -9 1234",
                "description": "Wymusza zakończenie procesu. Należy używać ostrożnie.",
                "example": "$ kill -9 1234",
            },
        ],
        "practice_task": (
            "Otwórz terminal i wykonaj kolejno: <code>ps</code>, <code>ps aux</code>, "
            "<code>top</code>. W programie <code>top</code> zwróć uwagę na kolumnę PID oraz zużycie CPU i pamięci. "
            "Wyjdź z <code>top</code> klawiszem <code>q</code>. Następnie użyj <code>pgrep</code> dla wybranego procesu, "
            "np. <code>pgrep bash</code>."
        ),
        "common_mistakes": [
            "Mylenie procesu z plikiem programu.",
            "Używanie <code>kill -9</code> jako pierwszej opcji zamiast zwykłego <code>kill</code>.",
            "Próba zakończenia procesu bez sprawdzenia jego PID.",
            "Zakładanie, że <code>ps</code> i <code>top</code> pokazują dokładnie to samo.",
            "Kończenie procesów systemowych bez zrozumienia ich roli.",
        ],
        "summary": (
            "Procesy są podstawowym elementem działania Linuxa. Komenda <code>ps</code> pozwala "
            "zobaczyć procesy, <code>top</code> umożliwia ich dynamiczny podgląd, <code>pgrep</code> pomaga "
            "znaleźć PID, a <code>kill</code> pozwala zakończyć wybrany proces."
        ),
    },
    "quiz": {
        "title": "Quiz: procesy w Linuxie",
        "description": "Sprawdź, czy rozumiesz podstawy pracy z procesami w Linuxie.",
        "questions": [
            {
                "text": "Czym jest proces w Linuxie?",
                "answers": [
                    ("a", "Uruchomionym programem działającym w systemie", True),
                    ("b", "Tylko plikiem tekstowym", False),
                    ("c", "Katalogiem domowym użytkownika", False),
                    ("d", "Rodzajem uprawnienia pliku", False),
                ],
            },
            {
                "text": "Co oznacza PID?",
                "answers": [
                    ("a", "Process ID, czyli identyfikator procesu", True),
                    ("b", "Path ID, czyli identyfikator ścieżki", False),
                    ("c", "Package ID, czyli numer pakietu", False),
                    ("d", "Permission ID, czyli identyfikator uprawnień", False),
                ],
            },
            {
                "text": "Która komenda pokazuje procesy w aktualnej sesji terminala?",
                "answers": [
                    ("a", "pwd", False),
                    ("b", "ps", True),
                    ("c", "chmod", False),
                    ("d", "mkdir", False),
                ],
            },
            {
                "text": "Do czego służy komenda top?",
                "answers": [
                    ("a", "Do dynamicznego podglądu procesów i zasobów systemu", True),
                    ("b", "Do tworzenia katalogów", False),
                    ("c", "Do zmiany nazwy użytkownika", False),
                    ("d", "Do kopiowania plików", False),
                ],
            },
            {
                "text": "Co robi komenda kill 1234?",
                "answers": [
                    ("a", "Wysyła sygnał zakończenia do procesu o PID 1234", True),
                    ("b", "Tworzy proces o numerze 1234", False),
                    ("c", "Wyświetla katalog 1234", False),
                    ("d", "Zmienia uprawnienia pliku 1234", False),
                ],
            },
            {
                "text": "Dlaczego kill -9 należy stosować ostrożnie?",
                "answers": [
                    ("a", "Bo wymusza zakończenie procesu", True),
                    ("b", "Bo zawsze usuwa cały system", False),
                    ("c", "Bo zmienia właściciela pliku", False),
                    ("d", "Bo tworzy nowych użytkowników", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Czym jest proces?",
            "answer": "Proces to uruchomiony program działający w systemie.",
        },
        {
            "question": "Co oznacza PID?",
            "answer": "Process ID, czyli unikalny identyfikator procesu.",
        },
        {
            "question": "Po co proces ma PID?",
            "answer": "Aby system i użytkownik mogli jednoznacznie wskazać konkretny proces.",
        },
        {
            "question": "Co robi komenda ps?",
            "answer": "Wyświetla procesy uruchomione w aktualnej sesji terminala.",
        },
        {
            "question": "Co robi komenda ps aux?",
            "answer": "Wyświetla szeroką listę procesów działających w systemie.",
        },
        {
            "question": "Co robi komenda top?",
            "answer": "Pokazuje dynamiczny podgląd procesów i zużycia zasobów systemu.",
        },
        {
            "question": "Jak wyjść z programu top?",
            "answer": "Najczęściej klawiszem q.",
        },
        {
            "question": "Co można zobaczyć w top?",
            "answer": "Procesy, PID, zużycie CPU, pamięci i inne informacje o systemie.",
        },
        {
            "question": "Co robi komenda pgrep nginx?",
            "answer": "Wyszukuje PID procesów, których nazwa pasuje do nginx.",
        },
        {
            "question": "Do czego służy kill?",
            "answer": "Do wysyłania sygnałów do procesów, najczęściej do ich zakończenia.",
        },
        {
            "question": "Co robi kill 1234?",
            "answer": "Wysyła sygnał zakończenia do procesu o PID 1234.",
        },
        {
            "question": "Czy kill zawsze natychmiast zabija proces?",
            "answer": "Nie. Domyślnie wysyła sygnał zakończenia, który proces może obsłużyć.",
        },
        {
            "question": "Co robi kill -9 1234?",
            "answer": "Wymusza zakończenie procesu o PID 1234.",
        },
        {
            "question": "Dlaczego kill -9 należy stosować ostrożnie?",
            "answer": "Bo wymusza przerwanie procesu bez normalnego zakończenia pracy.",
        },
        {
            "question": "Czy proces i program to dokładnie to samo?",
            "answer": "Nie. Program to plik lub kod, a proces to uruchomiona instancja programu.",
        },
        {
            "question": "Czy jeden program może mieć wiele procesów?",
            "answer": "Tak. Ten sam program może być uruchomiony wiele razy.",
        },
        {
            "question": "Czy każdy proces ma PID?",
            "answer": "Tak. Każdy proces w systemie ma swój identyfikator PID.",
        },
        {
            "question": "Co warto zrobić przed użyciem kill?",
            "answer": "Sprawdzić właściwy PID procesu.",
        },
        {
            "question": "Która komenda pomaga znaleźć PID po nazwie procesu?",
            "answer": "pgrep.",
        },
        {
            "question": "Która komenda daje dynamiczny podgląd procesów?",
            "answer": "top.",
        },
        {
            "question": "Która komenda pokazuje listę procesów?",
            "answer": "ps.",
        },
        {
            "question": "Czy ps pokazuje dynamiczny widok jak top?",
            "answer": "Nie. ps pokazuje wynik w danym momencie.",
        },
        {
            "question": "Czy top odświeża informacje na bieżąco?",
            "answer": "Tak. top pokazuje dynamiczny widok aktualizowany w czasie.",
        },
        {
            "question": "Co oznacza CPU w widoku procesów?",
            "answer": "Zużycie procesora przez proces.",
        },
        {
            "question": "Co oznacza pamięć w widoku procesów?",
            "answer": "Ilość pamięci RAM używanej przez proces.",
        },
        {
            "question": "Czy warto kończyć nieznane procesy systemowe?",
            "answer": "Nie, jeśli nie wiesz, za co odpowiadają.",
        },
        {
            "question": "Dlaczego znajomość procesów jest ważna?",
            "answer": "Pomaga diagnozować problemy, obciążenie systemu i działanie aplikacji.",
        },
        {
            "question": "Czy proces może przestać odpowiadać?",
            "answer": "Tak. Wtedy można próbować zakończyć go za pomocą kill.",
        },
        {
            "question": "Czy kill usuwa plik programu z dysku?",
            "answer": "Nie. kill działa na proces, nie usuwa pliku programu.",
        },
        {
            "question": "Co jest bezpieczniejsze na początku: kill czy kill -9?",
            "answer": "Zwykłe kill, bo pozwala procesowi zakończyć się łagodniej.",
        },
    ],
}