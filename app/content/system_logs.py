SYSTEM_LOGS = {
    "module": {
        "title": "Podstawy terminala",
        "description": "Pierwszy moduł poświęcony pracy w terminalu Linux.",
    },
    "lesson": {
        "title": "Logi systemowe: journalctl i /var/log",
        "level": "Podstawowy",
        "duration": "35 min",
        "description": (
            "Poznasz podstawowe sposoby przeglądania logów w Linuxie, pracę z journalctl "
            "oraz najważniejsze pliki w katalogu /var/log."
        ),
        "theory": (
            "Logi to zapisy zdarzeń generowane przez system operacyjny, usługi i aplikacje. "
            "Dzięki nim administrator może sprawdzić, co działo się w systemie, kiedy wystąpił "
            "błąd, czy usługa uruchomiła się poprawnie oraz dlaczego aplikacja przestała działać. "
            "We współczesnych dystrybucjach Linuxa ważną rolę pełni systemd journal, który można "
            "przeglądać za pomocą komendy journalctl. Oprócz tego wiele logów znajduje się nadal "
            "w katalogu /var/log. Przykładowo logi systemowe mogą znajdować się w /var/log/messages, "
            "a logi serwera Nginx w /var/log/nginx/access.log i /var/log/nginx/error.log. "
            "Podstawowa analiza logów polega na sprawdzeniu najnowszych wpisów, filtrowaniu ich "
            "według usługi, czasu lub priorytetu oraz obserwowaniu logów na żywo podczas testowania "
            "działania systemu."
        ),
        "commands": [
            {
                "command": "journalctl",
                "description": "Wyświetla logi z systemd journal.",
                "example": "$ journalctl",
            },
            {
                "command": "journalctl -n 50",
                "description": "Pokazuje ostatnie 50 wpisów z dziennika systemowego.",
                "example": "$ journalctl -n 50",
            },
            {
                "command": "journalctl -f",
                "description": "Pokazuje nowe wpisy logów na żywo.",
                "example": "$ journalctl -f",
            },
            {
                "command": "journalctl -u sshd",
                "description": "Wyświetla logi konkretnej usługi systemd, na przykład sshd.",
                "example": "$ journalctl -u sshd",
            },
            {
                "command": "journalctl -u example-app",
                "description": "Wyświetla logi przykładowej usługi aplikacyjnej.",
                "example": "$ journalctl -u example-app",
            },
            {
                "command": "journalctl -u example-app -f",
                "description": "Śledzi logi przykładowej usługi aplikacyjnej na żywo.",
                "example": "$ journalctl -u example-app -f",
            },
            {
                "command": "journalctl --since \"today\"",
                "description": "Pokazuje logi od początku bieżącego dnia.",
                "example": "$ journalctl --since \"today\"",
            },
            {
                "command": "journalctl --since \"1 hour ago\"",
                "description": "Pokazuje logi z ostatniej godziny.",
                "example": "$ journalctl --since \"1 hour ago\"",
            },
            {
                "command": "journalctl -p err",
                "description": "Pokazuje wpisy o priorytecie błędu i wyższym.",
                "example": "$ journalctl -p err",
            },
            {
                "command": "ls /var/log",
                "description": "Wyświetla pliki i katalogi z logami systemowymi.",
                "example": "$ ls /var/log",
            },
            {
                "command": "tail -n 50 /var/log/messages",
                "description": "Pokazuje ostatnie 50 linii z pliku logów systemowych.",
                "example": "$ tail -n 50 /var/log/messages",
            },
            {
                "command": "tail -f /var/log/messages",
                "description": "Śledzi dopisywane na bieżąco wpisy w pliku logów.",
                "example": "$ tail -f /var/log/messages",
            },
            {
                "command": "grep \"error\" /var/log/messages",
                "description": "Wyszukuje wpisy zawierające słowo error w pliku logów.",
                "example": "$ grep \"error\" /var/log/messages",
            },
            {
                "command": "tail -n 50 /var/log/nginx/access.log",
                "description": "Pokazuje ostatnie wpisy z logu dostępowego Nginx.",
                "example": "$ tail -n 50 /var/log/nginx/access.log",
            },
            {
                "command": "tail -n 50 /var/log/nginx/error.log",
                "description": "Pokazuje ostatnie wpisy z logu błędów Nginx.",
                "example": "$ tail -n 50 /var/log/nginx/error.log",
            },
        ],
        "practice_task": (
            "Wyświetl ostatnie wpisy z dziennika systemowego poleceniem "
            "<code>journalctl -n 50</code>. Następnie sprawdź logi wybranej usługi, na przykład "
            "<code>journalctl -u sshd</code>. Użyj <code>journalctl --since \"1 hour ago\"</code>, "
            "aby ograniczyć wynik do ostatniej godziny. Potem sprawdź katalog <code>/var/log</code> "
            "poleceniem <code>ls /var/log</code>. Na końcu użyj <code>tail -n 50 /var/log/messages</code> "
            "oraz <code>grep \"error\" /var/log/messages</code>, aby przećwiczyć podstawowe "
            "przeglądanie i filtrowanie logów."
        ),
        "common_mistakes": [
            "Czytanie całego dziennika bez ograniczenia liczby wpisów lub zakresu czasu.",
            "Mylenie logów systemd journal z plikami znajdującymi się w /var/log.",
            "Pomijanie opcji -u przy diagnozowaniu konkretnej usługi systemd.",
            "Brak użycia -f podczas obserwowania logów na żywo.",
            "Zakładanie, że każdy błąd aplikacji będzie widoczny tylko w jednym miejscu.",
            "Sprawdzanie wyłącznie logów aplikacji i pomijanie logów serwera WWW.",
            "Wyszukiwanie tylko słowa error i ignorowanie innych komunikatów ostrzegawczych.",
            "Nieodróżnianie logu dostępowego od logu błędów w Nginx.",
        ],
        "summary": (
            "Logi są jednym z najważniejszych źródeł informacji podczas administrowania Linuxem. "
            "<code>journalctl</code> pozwala przeglądać dziennik systemd, filtrować wpisy według "
            "usługi, czasu i priorytetu oraz obserwować logi na żywo. Katalog <code>/var/log</code> "
            "zawiera wiele klasycznych plików logów, takich jak <code>/var/log/messages</code> "
            "oraz logi usług, na przykład <code>/var/log/nginx/access.log</code> i "
            "<code>/var/log/nginx/error.log</code>. W praktyce diagnostyka problemów często zaczyna "
            "się właśnie od sprawdzenia najnowszych wpisów w logach."
        ),
    },
    "quiz": {
        "title": "Quiz: logi systemowe",
        "description": "Sprawdź, czy rozumiesz podstawy pracy z journalctl i katalogiem /var/log.",
        "questions": [
            {
                "text": "Do czego służą logi systemowe?",
                "answers": [
                    ("a", "Do zapisywania informacji o zdarzeniach, błędach i działaniu usług", True),
                    ("b", "Do kompilowania programów", False),
                    ("c", "Do zmiany haseł użytkowników", False),
                    ("d", "Do tworzenia partycji dysku", False),
                ],
            },
            {
                "text": "Do czego służy komenda journalctl?",
                "answers": [
                    ("a", "Do przeglądania dziennika systemd", True),
                    ("b", "Do instalowania pakietów", False),
                    ("c", "Do zmiany właściciela pliku", False),
                    ("d", "Do usuwania katalogów", False),
                ],
            },
            {
                "text": "Co robi journalctl -n 50?",
                "answers": [
                    ("a", "Pokazuje ostatnie 50 wpisów z dziennika", True),
                    ("b", "Tworzy 50 nowych logów", False),
                    ("c", "Usuwa 50 najstarszych wpisów", False),
                    ("d", "Pokazuje 50 użytkowników", False),
                ],
            },
            {
                "text": "Co robi journalctl -f?",
                "answers": [
                    ("a", "Pokazuje nowe wpisy logów na żywo", True),
                    ("b", "Formatuje dysk", False),
                    ("c", "Zamyka usługę systemową", False),
                    ("d", "Tworzy nowy plik konfiguracyjny", False),
                ],
            },
            {
                "text": "Do czego służy journalctl -u sshd?",
                "answers": [
                    ("a", "Do wyświetlania logów usługi sshd", True),
                    ("b", "Do tworzenia użytkownika sshd", False),
                    ("c", "Do instalowania klienta SSH", False),
                    ("d", "Do czyszczenia katalogu /var/log", False),
                ],
            },
            {
                "text": "Co pozwala zrobić journalctl --since \"1 hour ago\"?",
                "answers": [
                    ("a", "Wyświetlić logi z ostatniej godziny", True),
                    ("b", "Cofnąć system o godzinę", False),
                    ("c", "Zmienić strefę czasową", False),
                    ("d", "Utworzyć harmonogram zadania", False),
                ],
            },
            {
                "text": "Gdzie zwykle znajdują się klasyczne pliki logów w Linuxie?",
                "answers": [
                    ("a", "W katalogu /var/log", True),
                    ("b", "W katalogu /home/logs", False),
                    ("c", "W katalogu /etc/users", False),
                    ("d", "W katalogu /boot/tmp", False),
                ],
            },
            {
                "text": "Co robi tail -n 50 /var/log/messages?",
                "answers": [
                    ("a", "Pokazuje ostatnie 50 linii z pliku /var/log/messages", True),
                    ("b", "Usuwa ostatnie 50 linii z pliku", False),
                    ("c", "Tworzy kopię pliku messages", False),
                    ("d", "Zmienia uprawnienia pliku messages", False),
                ],
            },
            {
                "text": "Do czego służy grep podczas pracy z logami?",
                "answers": [
                    ("a", "Do wyszukiwania konkretnych słów lub wzorców w logach", True),
                    ("b", "Do restartowania usług", False),
                    ("c", "Do sprawdzania zajętości dysku", False),
                    ("d", "Do zmiany nazwy hosta", False),
                ],
            },
            {
                "text": "Czym różni się access.log od error.log w Nginx?",
                "answers": [
                    ("a", "access.log zapisuje żądania, a error.log błędy serwera", True),
                    ("b", "access.log służy do haseł, a error.log do użytkowników", False),
                    ("c", "access.log jest katalogiem, a error.log usługą", False),
                    ("d", "Nie ma między nimi żadnej różnicy", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Czym są logi systemowe?",
            "answer": "To zapisy zdarzeń generowane przez system, usługi i aplikacje.",
        },
        {
            "question": "Po co administrator sprawdza logi?",
            "answer": "Aby diagnozować błędy, awarie usług i nietypowe zachowanie systemu.",
        },
        {
            "question": "Do czego służy journalctl?",
            "answer": "Do przeglądania dziennika systemd.",
        },
        {
            "question": "Co robi journalctl -n 50?",
            "answer": "Pokazuje ostatnie 50 wpisów z dziennika.",
        },
        {
            "question": "Co robi journalctl -f?",
            "answer": "Śledzi nowe wpisy logów na żywo.",
        },
        {
            "question": "Do czego służy journalctl -u?",
            "answer": "Do filtrowania logów konkretnej usługi systemd.",
        },
        {
            "question": "Jak sprawdzić logi usługi sshd?",
            "answer": "Komendą journalctl -u sshd.",
        },
        {
            "question": "Jak śledzić logi przykładowej usługi na żywo?",
            "answer": "Komendą journalctl -u example-app -f.",
        },
        {
            "question": "Co robi journalctl --since \"today\"?",
            "answer": "Pokazuje logi od początku bieżącego dnia.",
        },
        {
            "question": "Co robi journalctl --since \"1 hour ago\"?",
            "answer": "Pokazuje logi z ostatniej godziny.",
        },
        {
            "question": "Co robi journalctl -p err?",
            "answer": "Pokazuje wpisy o priorytecie błędu i wyższym.",
        },
        {
            "question": "Gdzie znajdują się klasyczne pliki logów?",
            "answer": "Najczęściej w katalogu /var/log.",
        },
        {
            "question": "Co może zawierać /var/log/messages?",
            "answer": "Ogólne komunikaty systemowe i wpisy związane z działaniem systemu.",
        },
        {
            "question": "Do czego służy tail -n 50?",
            "answer": "Do pokazania ostatnich 50 linii pliku.",
        },
        {
            "question": "Do czego służy tail -f?",
            "answer": "Do obserwowania dopisywanych na bieżąco wpisów w pliku.",
        },
        {
            "question": "Do czego służy grep w analizie logów?",
            "answer": "Do wyszukiwania konkretnych słów lub wzorców w plikach logów.",
        },
        {
            "question": "Co zawiera /var/log/nginx/access.log?",
            "answer": "Wpisy dotyczące żądań obsłużonych przez Nginx.",
        },
        {
            "question": "Co zawiera /var/log/nginx/error.log?",
            "answer": "Informacje o błędach Nginx.",
        },
        {
            "question": "Dlaczego warto ograniczać logi zakresem czasu?",
            "answer": "Bo pełny dziennik może być bardzo długi i trudny do analizy.",
        },
        {
            "question": "Od czego często zaczyna się diagnostyka awarii usługi?",
            "answer": "Od sprawdzenia najnowszych wpisów w logach tej usługi.",
        },
    ],
}