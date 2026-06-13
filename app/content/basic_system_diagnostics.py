BASIC_SYSTEM_DIAGNOSTICS = {
    "module": {
        "title": "Administracja systemem",
        "description": "Moduł poświęcony podstawowej administracji systemem Linux.",
    },
    "lesson": {
        "title": "Podstawowa diagnostyka systemu: uptime, free, df, du i hostnamectl",
        "level": "Podstawowy",
        "duration": "35 min",
        "description": (
            "Poznasz podstawowe komendy pomagające szybko ocenić stan serwera: obciążenie, "
            "pamięć, miejsce na dysku, rozmiary katalogów oraz informacje o systemie."
        ),
        "theory": (
            "Gdy serwer działa wolno albo brakuje miejsca na dysku, administrator powinien zacząć "
            "od prostych, bezpiecznych komend diagnostycznych. <code>uptime</code> pokazuje, jak "
            "długo system działa, ilu użytkowników jest zalogowanych oraz wartości load average. "
            "Load average pomaga ocenić obciążenie systemu, ale trzeba interpretować go w kontekście "
            "liczby rdzeni CPU i innych objawów. <code>free -h</code> pokazuje użycie pamięci RAM "
            "i swap w czytelnej formie. <code>df -h</code> pokazuje zajętość systemów plików, więc "
            "jest pierwszym wyborem przy problemach z brakiem miejsca. <code>du -sh</code> pozwala "
            "sprawdzić rozmiar konkretnego katalogu, na przykład <code>/var/log</code>. "
            "<code>hostnamectl</code> pokazuje nazwę hosta i podstawowe informacje o systemie, a "
            "<code>uname -r</code> wersję jądra. Te komendy nie naprawiają problemu automatycznie, "
            "ale pomagają szybko ustalić, czy warto najpierw szukać przyczyny w obciążeniu, pamięci, "
            "dysku, logach czy konfiguracji systemu."
        ),
        "commands": [
            {
                "command": "uptime",
                "description": "Pokazuje czas działania systemu, liczbę użytkowników i load average.",
                "example": "$ uptime",
            },
            {
                "command": "free -h",
                "description": "Wyświetla użycie pamięci RAM i swap w czytelnych jednostkach.",
                "example": "$ free -h",
            },
            {
                "command": "df -h",
                "description": "Pokazuje zajętość systemów plików w czytelnej formie.",
                "example": "$ df -h",
            },
            {
                "command": "du -sh /var/log",
                "description": "Pokazuje łączny rozmiar katalogu /var/log.",
                "example": "$ du -sh /var/log",
            },
            {
                "command": "hostnamectl",
                "description": "Wyświetla nazwę hosta i podstawowe informacje o systemie.",
                "example": "$ hostnamectl",
            },
            {
                "command": "uname -r",
                "description": "Pokazuje wersję aktualnie używanego jądra systemu.",
                "example": "$ uname -r",
            },
        ],
        "practice_task": (
            "Wykonaj podstawowy przegląd stanu systemu. Zacznij od <code>uptime</code> i zapisz "
            "wartości load average. Następnie użyj <code>free -h</code>, aby sprawdzić pamięć, "
            "oraz <code>df -h</code>, aby zobaczyć zajętość dysków. Sprawdź rozmiar logów komendą "
            "<code>du -sh /var/log</code>. Na końcu uruchom <code>hostnamectl</code> i "
            "<code>uname -r</code>, żeby zanotować podstawowe informacje o systemie i wersji jądra."
        ),
        "common_mistakes": [
            "Patrzenie wyłącznie na load average bez sprawdzenia pamięci i dysku.",
            "Mylenie <code>df -h</code>, które pokazuje systemy plików, z <code>du -sh</code>, które pokazuje rozmiar katalogu.",
            "Zakładanie, że mała ilość pamięci free zawsze oznacza awarię.",
            "Sprawdzanie rozmiaru całego systemu komendą <code>du</code> bez ograniczenia do konkretnego katalogu.",
            "Ignorowanie zajętości partycji, na której znajdują się logi.",
            "Pomijanie podstawowych informacji o systemie przy zgłaszaniu problemu.",
            "Przechodzenie od razu do restartu serwera bez zebrania podstawowych danych diagnostycznych.",
        ],
        "summary": (
            "Podstawowa diagnostyka zaczyna się od szybkiego sprawdzenia kilku obszarów. "
            "<code>uptime</code> pokazuje czas działania i load average, <code>free -h</code> "
            "pamięć, <code>df -h</code> zajętość systemów plików, a <code>du -sh</code> rozmiar "
            "konkretnego katalogu. <code>hostnamectl</code> i <code>uname -r</code> pomagają "
            "ustalić, z jakim systemem i jądrem pracujesz. Taki zestaw komend daje dobry pierwszy "
            "obraz sytuacji przy wolnym serwerze albo braku miejsca na dysku."
        ),
    },
    "quiz": {
        "title": "Quiz: podstawowa diagnostyka systemu",
        "description": "Sprawdź, czy rozumiesz podstawowe komendy diagnostyczne w Linuxie.",
        "questions": [
            {
                "text": "Co pokazuje komenda uptime?",
                "answers": [
                    ("a", "Czas działania systemu, liczbę użytkowników i load average", True),
                    ("b", "Tylko rozmiar katalogu /tmp", False),
                    ("c", "Listę zainstalowanych pakietów", False),
                    ("d", "Zawartość pliku /etc/passwd", False),
                ],
            },
            {
                "text": "Do czego służy free -h?",
                "answers": [
                    ("a", "Do sprawdzania użycia pamięci RAM i swap", True),
                    ("b", "Do zwalniania wszystkich plików tymczasowych", False),
                    ("c", "Do restartowania usług systemowych", False),
                    ("d", "Do zmiany nazwy hosta", False),
                ],
            },
            {
                "text": "Która komenda pomaga sprawdzić, czy brakuje miejsca na systemie plików?",
                "answers": [
                    ("a", "df -h", True),
                    ("b", "uname -r", False),
                    ("c", "hostnamectl", False),
                    ("d", "uptime --delete", False),
                ],
            },
            {
                "text": "Co pokazuje du -sh /var/log?",
                "answers": [
                    ("a", "Rozmiar katalogu /var/log w czytelnej formie", True),
                    ("b", "Wersję jądra systemu", False),
                    ("c", "Nazwę aktywnego użytkownika", False),
                    ("d", "Listę otwartych portów", False),
                ],
            },
            {
                "text": "Do czego służy hostnamectl?",
                "answers": [
                    ("a", "Do wyświetlania nazwy hosta i podstawowych informacji o systemie", True),
                    ("b", "Do usuwania starych logów", False),
                    ("c", "Do mierzenia temperatury procesora", False),
                    ("d", "Do instalowania pakietów", False),
                ],
            },
            {
                "text": "Co pokazuje uname -r?",
                "answers": [
                    ("a", "Wersję aktualnie używanego jądra systemu", True),
                    ("b", "Rozmiar katalogu domowego", False),
                    ("c", "Aktualne użycie pamięci swap", False),
                    ("d", "Historię logowania użytkowników", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Od czego warto zacząć przy problemie wolnego serwera?",
            "answer": "Od prostych komend diagnostycznych, takich jak uptime, free -h i df -h.",
        },
        {
            "question": "Co pokazuje uptime?",
            "answer": "Czas działania systemu, liczbę zalogowanych użytkowników i load average.",
        },
        {
            "question": "Czym jest load average?",
            "answer": "Wskaźnikiem średniego obciążenia systemu w ostatnich okresach czasu.",
        },
        {
            "question": "Czy load average trzeba interpretować w kontekście CPU?",
            "answer": "Tak, znaczenie wartości zależy między innymi od liczby rdzeni procesora.",
        },
        {
            "question": "Do czego służy free -h?",
            "answer": "Do sprawdzania użycia pamięci RAM i swap w czytelnej formie.",
        },
        {
            "question": "Co oznacza opcja -h w free -h?",
            "answer": "Pokazuje wartości w czytelnych jednostkach, takich jak MiB lub GiB.",
        },
        {
            "question": "Do czego służy df -h?",
            "answer": "Do sprawdzania zajętości systemów plików.",
        },
        {
            "question": "Kiedy szczególnie przydaje się df -h?",
            "answer": "Gdy podejrzewasz brak miejsca na dysku lub partycji.",
        },
        {
            "question": "Do czego służy du -sh?",
            "answer": "Do sprawdzania rozmiaru konkretnego katalogu lub pliku.",
        },
        {
            "question": "Co robi du -sh /var/log?",
            "answer": "Pokazuje łączny rozmiar katalogu /var/log.",
        },
        {
            "question": "Czym różni się df od du?",
            "answer": "df pokazuje zajętość systemów plików, a du rozmiar wskazanych katalogów lub plików.",
        },
        {
            "question": "Do czego służy hostnamectl?",
            "answer": "Do wyświetlania nazwy hosta i podstawowych informacji o systemie.",
        },
        {
            "question": "Co pokazuje uname -r?",
            "answer": "Wersję aktualnie używanego jądra systemu.",
        },
        {
            "question": "Jaka komenda pokazuje informacje o pamięci w czytelnej formie?",
            "answer": "free -h.",
        },
        {
            "question": "Jaka komenda pokazuje zajętość dysków w czytelnej formie?",
            "answer": "df -h.",
        },
        {
            "question": "Jaka komenda pokazuje nazwę hosta?",
            "answer": "hostnamectl.",
        },
        {
            "question": "Jaka komenda pokazuje wersję jądra?",
            "answer": "uname -r.",
        },
        {
            "question": "Co sprawdzić przy komunikacie o braku miejsca na dysku?",
            "answer": "Najpierw df -h, a potem rozmiary podejrzanych katalogów przez du -sh.",
        },
        {
            "question": "Co sprawdzić, gdy serwer działa wolno?",
            "answer": "Obciążenie przez uptime, pamięć przez free -h i dysk przez df -h.",
        },
        {
            "question": "Dlaczego nie warto od razu restartować serwera?",
            "answer": "Bo restart może ukryć objawy problemu, zanim zbierzesz dane diagnostyczne.",
        },
        {
            "question": "Czy free -h automatycznie naprawia problem z pamięcią?",
            "answer": "Nie. To komenda diagnostyczna, która pokazuje stan pamięci.",
        },
        {
            "question": "Czy df -h pokazuje rozmiar pojedynczego katalogu?",
            "answer": "Nie. Do rozmiaru katalogu służy du -sh.",
        },
        {
            "question": "Dlaczego warto sprawdzić /var/log przy braku miejsca?",
            "answer": "Bo logi mogą szybko rosnąć i zajmować dużo miejsca.",
        },
        {
            "question": "Jak zebrać podstawowe informacje o systemie do zgłoszenia problemu?",
            "answer": "Użyć hostnamectl oraz uname -r.",
        },
        {
            "question": "Jaki jest cel podstawowej diagnostyki?",
            "answer": "Szybko ustalić, czy problem dotyczy obciążenia, pamięci, dysku lub informacji o systemie.",
        },
    ],
}
