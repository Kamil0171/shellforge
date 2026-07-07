SSH_SECURE_CONFIGURATION = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "Bezpieczna konfiguracja SSH",
        "level": "Podstawowy+",
        "duration": "50 min",
        "description": (
            "Poznasz podstawowe opcje konfiguracji serwera SSH, sposób bezpiecznego testowania zmian "
            "oraz praktyczne znaczenie logowania kluczami zamiast hasłem."
        ),
        "theory": (
            "OpenSSH Server pozwala administratorowi zdalnie logować się do systemu, dlatego jego konfiguracja "
            "ma duży wpływ na bezpieczeństwo serwera. Główny plik konfiguracyjny to "
            "<code>/etc/ssh/sshd_config</code>. Przed zmianami warto mieć aktywną drugą sesję SSH albo dostęp "
            "konsolowy, aby nie odciąć sobie dostępu przez błędną konfigurację. Bezpieczna praca zaczyna się od "
            "edycji przez <code>sudoedit</code>, sprawdzenia składni poleceniem <code>sshd -t</code>, a dopiero "
            "potem restartu usługi. Opcja <code>PermitRootLogin</code> kontroluje logowanie bezpośrednio na konto "
            "root. W typowej administracji lepiej używać zwykłego użytkownika i <code>sudo</code>, bo daje to "
            "lepszą kontrolę i ślad działań. <code>PasswordAuthentication</code> decyduje, czy serwer przyjmuje "
            "logowanie hasłem. Gdy działa logowanie kluczami, wyłączenie haseł ogranicza skuteczność zgadywania "
            "haseł przez Internet. <code>PubkeyAuthentication</code> odpowiada za logowanie kluczami publicznymi. "
            "Po każdej zmianie należy sprawdzić status usługi i wykonać test logowania w nowej sesji, zanim "
            "zamknie się dotychczasowe połączenie."
        ),
        "commands": [
            {
                "command": "sudoedit /etc/ssh/sshd_config",
                "description": "Bezpiecznie otwiera główny plik konfiguracji serwera SSH do edycji.",
                "example": "$ sudoedit /etc/ssh/sshd_config",
            },
            {
                "command": "sudo sshd -t",
                "description": "Sprawdza składnię konfiguracji sshd bez restartowania usługi.",
                "example": "$ sudo sshd -t",
            },
            {
                "command": "sudo systemctl restart sshd",
                "description": "Restartuje usługę SSH po poprawnym sprawdzeniu konfiguracji.",
                "example": "$ sudo systemctl restart sshd",
            },
            {
                "command": "sudo systemctl status sshd",
                "description": "Pokazuje bieżący stan usługi sshd i ostatnie komunikaty.",
                "example": "$ sudo systemctl status sshd",
            },
            {
                "command": "sudo journalctl -u sshd -n 50",
                "description": "Wyświetla ostatnie wpisy logów usługi sshd.",
                "example": "$ sudo journalctl -u sshd -n 50",
            },
            {
                "command": "ssh user@example.com",
                "description": "Testuje logowanie do serwera po zmianie konfiguracji.",
                "example": "$ ssh user@example.com",
            },
        ],
        "practice_task": (
            "Na maszynie laboratoryjnej otwórz <code>/etc/ssh/sshd_config</code> przez "
            "<code>sudoedit /etc/ssh/sshd_config</code> i odszukaj opcje <code>PermitRootLogin</code>, "
            "<code>PasswordAuthentication</code> oraz <code>PubkeyAuthentication</code>. Nie zmieniaj ich na "
            "serwerze produkcyjnym bez planu dostępu awaryjnego. W labie ustaw bezpieczne wartości, sprawdź "
            "składnię przez <code>sudo sshd -t</code>, zrestartuj usługę poleceniem "
            "<code>sudo systemctl restart sshd</code> i potwierdź stan przez <code>sudo systemctl status sshd</code>. "
            "Przed zamknięciem starej sesji wykonaj nowe połączenie testowe."
        ),
        "common_mistakes": [
            "Restartowanie sshd bez wcześniejszego sprawdzenia konfiguracji przez sshd -t.",
            "Zamykanie jedynej aktywnej sesji SSH przed testem nowego logowania.",
            "Pozostawianie logowania hasłem mimo poprawnie działających kluczy SSH.",
            "Dopuszczanie bezpośredniego logowania root do codziennej administracji.",
            "Mylenie konfiguracji klienta SSH z konfiguracją serwera sshd.",
            "Wprowadzanie zmian produkcyjnych bez dostępu konsolowego lub planu awaryjnego.",
        ],
        "summary": (
            "Bezpieczna konfiguracja SSH polega na rozważnym ograniczaniu metod logowania i testowaniu każdej "
            "zmiany. <code>PermitRootLogin</code>, <code>PasswordAuthentication</code> i "
            "<code>PubkeyAuthentication</code> to podstawowe opcje, które warto rozumieć. Przed restartem używaj "
            "<code>sshd -t</code>, po restarcie sprawdzaj <code>systemctl status sshd</code> i zawsze testuj nowe "
            "połączenie przed zamknięciem starej sesji."
        ),
    },
    "quiz": {
        "title": "Quiz: bezpieczna konfiguracja SSH",
        "description": "Sprawdź, czy rozumiesz podstawowe opcje sshd_config i bezpieczny proces zmian.",
        "questions": [
            {
                "text": "Po co uruchamia się sudo sshd -t przed restartem usługi?",
                "answers": [
                    ("a", "Aby sprawdzić składnię konfiguracji sshd", True),
                    ("b", "Aby usunąć stare klucze hosta", False),
                    ("c", "Aby otworzyć port HTTP", False),
                    ("d", "Aby wyczyścić logi systemowe", False),
                ],
            },
            {
                "text": "Za co odpowiada opcja PermitRootLogin?",
                "answers": [
                    ("a", "Za możliwość bezpośredniego logowania na konto root przez SSH", True),
                    ("b", "Za nazwę serwera DNS", False),
                    ("c", "Za domyślną strefę firewalld", False),
                    ("d", "Za rozmiar katalogu /tmp", False),
                ],
            },
            {
                "text": "Dlaczego warto wyłączyć PasswordAuthentication, gdy klucze SSH działają poprawnie?",
                "answers": [
                    ("a", "Bo ogranicza to ryzyko zgadywania haseł przez sieć", True),
                    ("b", "Bo usuwa potrzebę aktualizacji systemu", False),
                    ("c", "Bo automatycznie konfiguruje DNS", False),
                    ("d", "Bo zmienia port HTTPS na 443", False),
                ],
            },
            {
                "text": "Co oznacza PubkeyAuthentication?",
                "answers": [
                    ("a", "Obsługę logowania z użyciem kluczy publicznych", True),
                    ("b", "Włączenie logowania bez użytkownika", False),
                    ("c", "Wyświetlenie listy procesów", False),
                    ("d", "Tryb pracy SELinux", False),
                ],
            },
            {
                "text": "Jaki jest bezpieczny krok po restarcie sshd?",
                "answers": [
                    ("a", "Sprawdzenie statusu usługi i test nowego połączenia", True),
                    ("b", "Natychmiastowe zamknięcie wszystkich sesji", False),
                    ("c", "Usunięcie katalogu ~/.ssh", False),
                    ("d", "Wyłączenie firewalla", False),
                ],
            },
            {
                "text": "Dlaczego warto mieć drugą sesję SSH podczas zmian?",
                "answers": [
                    ("a", "Aby nie stracić dostępu, jeśli nowa konfiguracja zablokuje logowanie", True),
                    ("b", "Aby przyspieszyć DNS", False),
                    ("c", "Aby wymusić permissive w SELinux", False),
                    ("d", "Aby automatycznie dodać certyfikat TLS", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Gdzie znajduje się główna konfiguracja serwera SSH?", "answer": "Zwykle w /etc/ssh/sshd_config."},
        {"question": "Do czego służy sudoedit /etc/ssh/sshd_config?", "answer": "Do bezpiecznej edycji konfiguracji sshd z uprawnieniami administratora."},
        {"question": "Co robi sshd -t?", "answer": "Sprawdza składnię konfiguracji serwera SSH."},
        {"question": "Kiedy restartować sshd?", "answer": "Po sprawdzeniu, że konfiguracja przechodzi test sshd -t."},
        {"question": "Jak zrestartować usługę SSH w Rocky Linux?", "answer": "sudo systemctl restart sshd."},
        {"question": "Jak sprawdzić stan usługi sshd?", "answer": "sudo systemctl status sshd."},
        {"question": "Co kontroluje PermitRootLogin?", "answer": "Możliwość bezpośredniego logowania root przez SSH."},
        {"question": "Dlaczego ograniczać logowanie root?", "answer": "Bo lepiej pracować na zwykłym koncie i podnosić uprawnienia przez sudo."},
        {"question": "Co kontroluje PasswordAuthentication?", "answer": "Możliwość logowania hasłem przez SSH."},
        {"question": "Kiedy rozważyć wyłączenie logowania hasłem?", "answer": "Gdy logowanie kluczami działa poprawnie i masz sprawdzony dostęp awaryjny."},
        {"question": "Co kontroluje PubkeyAuthentication?", "answer": "Możliwość logowania przy użyciu kluczy SSH."},
        {"question": "Dlaczego klucze są zwykle bezpieczniejsze niż hasła?", "answer": "Nie są zgadywane tak jak hasła i opierają się na kryptografii klucza publicznego."},
        {"question": "Co zrobić przed zamknięciem starej sesji SSH?", "answer": "Przetestować nowe logowanie w osobnym terminalu."},
        {"question": "Dlaczego druga sesja SSH pomaga przy zmianach?", "answer": "Pozwala zachować dostęp, gdy nowa konfiguracja blokuje logowanie."},
        {"question": "Czy zmiana portu SSH zastępuje klucze?", "answer": "Nie, to nie zastępuje dobrego uwierzytelniania."},
        {"question": "Co pokazuje journalctl -u sshd?", "answer": "Logi związane z usługą sshd."},
        {"question": "Czy klient ssh i serwer sshd to to samo?", "answer": "Nie. ssh to klient, a sshd to demon serwera SSH."},
        {"question": "Co oznacza błąd składni w sshd_config?", "answer": "Konfiguracja może nie zostać poprawnie wczytana przez usługę."},
        {"question": "Dlaczego nie robić zmian SSH bez planu awaryjnego?", "answer": "Bo można odciąć sobie zdalny dostęp do serwera."},
        {"question": "Jaki jest pierwszy test po zmianie sshd_config?", "answer": "sudo sshd -t."},
        {"question": "Jaki jest drugi test po restarcie sshd?", "answer": "systemctl status sshd oraz nowe połączenie SSH."},
        {"question": "Czy PasswordAuthentication no usuwa konta użytkowników?", "answer": "Nie, wyłącza tylko logowanie hasłem przez SSH."},
        {"question": "Czy PubkeyAuthentication yes wymaga authorized_keys?", "answer": "Tak, klucz publiczny użytkownika musi być dostępny na serwerze."},
        {"question": "Co jest lepsze do codziennej administracji niż root przez SSH?", "answer": "Zwykłe konto użytkownika z dostępem sudo."},
        {"question": "Jaka jest dobra zasada zmian w SSH?", "answer": "Zmieniaj mało, testuj składnię, restartuj świadomie i sprawdzaj nowe logowanie."},
    ],
}
