SSH_KEYS_PRACTICE = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "Klucze SSH w praktyce",
        "level": "Podstawowy+",
        "duration": "50 min",
        "description": (
            "Przećwiczysz tworzenie pary kluczy SSH, kopiowanie klucza publicznego na serwer, "
            "ustawianie uprawnień katalogu .ssh i diagnozowanie typowych problemów z logowaniem."
        ),
        "theory": (
            "Logowanie kluczami SSH opiera się na parze kluczy: prywatnym i publicznym. Klucz prywatny zostaje "
            "na komputerze użytkownika i powinien być chroniony jak sekret. Klucz publiczny można przekazać na "
            "serwer, najczęściej do pliku <code>~/.ssh/authorized_keys</code> użytkownika, na którego konto "
            "chcemy się logować. Parę kluczy tworzy <code>ssh-keygen</code>. W nowych konfiguracjach dobrym "
            "wyborem jest typ <code>ed25519</code>, o ile systemy po obu stronach go obsługują. Narzędzie "
            "<code>ssh-copy-id</code> automatyzuje dopisanie klucza publicznego do <code>authorized_keys</code>. "
            "W praktyce bardzo ważne są uprawnienia: katalog <code>~/.ssh</code> powinien być dostępny tylko dla "
            "właściciela, a plik <code>authorized_keys</code> nie może być zapisywalny przez innych użytkowników. "
            "Do testowania konkretnego klucza używa się <code>ssh -i</code>. Jeśli logowanie nie działa, warto "
            "sprawdzić, czy używany jest właściwy użytkownik, właściwy klucz, poprawny plik publiczny na serwerze "
            "oraz poprawne uprawnienia katalogów i plików."
        ),
        "commands": [
            {
                "command": "ssh-keygen -t ed25519 -C \"admin@example.com\"",
                "description": "Tworzy nową parę kluczy SSH typu ed25519 z komentarzem.",
                "example": "$ ssh-keygen -t ed25519 -C \"admin@example.com\"",
            },
            {
                "command": "ssh-copy-id user@example.com",
                "description": "Kopiuje domyślny klucz publiczny do authorized_keys na serwerze.",
                "example": "$ ssh-copy-id user@example.com",
            },
            {
                "command": "ssh-copy-id -i ~/.ssh/id_ed25519.pub user@example.com",
                "description": "Kopiuje wskazany klucz publiczny na serwer.",
                "example": "$ ssh-copy-id -i ~/.ssh/id_ed25519.pub user@example.com",
            },
            {
                "command": "chmod 700 ~/.ssh",
                "description": "Ustawia prywatne uprawnienia katalogu .ssh.",
                "example": "$ chmod 700 ~/.ssh",
            },
            {
                "command": "chmod 600 ~/.ssh/authorized_keys",
                "description": "Ustawia bezpieczne uprawnienia pliku authorized_keys.",
                "example": "$ chmod 600 ~/.ssh/authorized_keys",
            },
            {
                "command": "ssh -i ~/.ssh/id_ed25519 user@example.com",
                "description": "Łączy się z serwerem przy użyciu wskazanego klucza prywatnego.",
                "example": "$ ssh -i ~/.ssh/id_ed25519 user@example.com",
            },
        ],
        "practice_task": (
            "W środowisku testowym utwórz parę kluczy poleceniem "
            "<code>ssh-keygen -t ed25519 -C \"lab@example.com\"</code>, pilnując, aby nie nadpisać ważnego "
            "klucza. Sprawdź, które pliki powstały w <code>~/.ssh</code>. Jeśli masz serwer testowy, skopiuj "
            "klucz publiczny przez <code>ssh-copy-id -i ~/.ssh/id_ed25519.pub user@example.com</code>. Na serwerze "
            "sprawdź katalog <code>~/.ssh</code> i plik <code>authorized_keys</code>, a potem ustaw "
            "<code>chmod 700 ~/.ssh</code> i <code>chmod 600 ~/.ssh/authorized_keys</code>. Na końcu przetestuj "
            "logowanie przez <code>ssh -i ~/.ssh/id_ed25519 user@example.com</code>."
        ),
        "common_mistakes": [
            "Kopiowanie klucza prywatnego na serwer zamiast publicznego.",
            "Nadpisanie używanego klucza bez sprawdzenia jego roli.",
            "Zbyt szerokie uprawnienia katalogu .ssh lub pliku authorized_keys.",
            "Logowanie na innego użytkownika niż ten, którego authorized_keys został uzupełniony.",
            "Używanie ssh -i z plikiem .pub zamiast kluczem prywatnym.",
            "Brak hasła do klucza prywatnego na komputerze używanym poza laboratorium.",
        ],
        "summary": (
            "Klucze SSH składają się z części prywatnej i publicznej. Prywatna zostaje u użytkownika, publiczna "
            "trafia na serwer do <code>authorized_keys</code>. <code>ssh-keygen</code> tworzy klucze, "
            "<code>ssh-copy-id</code> kopiuje klucz publiczny, <code>chmod</code> pomaga ustawić poprawne "
            "uprawnienia, a <code>ssh -i</code> pozwala wskazać konkretny klucz przy logowaniu."
        ),
    },
    "quiz": {
        "title": "Quiz: klucze SSH w praktyce",
        "description": "Sprawdź, czy rozumiesz pary kluczy, authorized_keys i podstawowe uprawnienia SSH.",
        "questions": [
            {
                "text": "Który klucz powinien zostać tylko na komputerze użytkownika?",
                "answers": [
                    ("a", "Klucz prywatny", True),
                    ("b", "Klucz publiczny", False),
                    ("c", "Rekord A", False),
                    ("d", "Port 443", False),
                ],
            },
            {
                "text": "Gdzie na serwerze zwykle trafia klucz publiczny użytkownika?",
                "answers": [
                    ("a", "~/.ssh/authorized_keys", True),
                    ("b", "/var/log/messages", False),
                    ("c", "/etc/resolv.conf", False),
                    ("d", "/tmp/sshd_config", False),
                ],
            },
            {
                "text": "Do czego służy ssh-copy-id?",
                "answers": [
                    ("a", "Do dopisania klucza publicznego do konta na serwerze", True),
                    ("b", "Do zmiany trybu SELinux", False),
                    ("c", "Do sprawdzenia trasy routingu", False),
                    ("d", "Do wystawienia certyfikatu TLS", False),
                ],
            },
            {
                "text": "Jakie uprawnienia są typowe dla katalogu ~/.ssh?",
                "answers": [
                    ("a", "700", True),
                    ("b", "777", False),
                    ("c", "000", False),
                    ("d", "222", False),
                ],
            },
            {
                "text": "Co robi ssh -i ~/.ssh/id_ed25519 user@example.com?",
                "answers": [
                    ("a", "Loguje się z użyciem wskazanego klucza prywatnego", True),
                    ("b", "Kopiuje logi systemowe", False),
                    ("c", "Otwiera port w firewallu", False),
                    ("d", "Sprawdza certyfikat HTTPS", False),
                ],
            },
            {
                "text": "Jaki błąd często powoduje niedziałające logowanie kluczem?",
                "answers": [
                    ("a", "Zbyt szerokie uprawnienia .ssh lub authorized_keys", True),
                    ("b", "Brak rekordu MX dla domeny", False),
                    ("c", "Zbyt mały katalog /tmp", False),
                    ("d", "Brak komendy df", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Z czego składa się para kluczy SSH?", "answer": "Z klucza prywatnego i publicznego."},
        {"question": "Czym jest klucz prywatny?", "answer": "Sekretną częścią pary kluczy, która zostaje na komputerze użytkownika."},
        {"question": "Czym jest klucz publiczny?", "answer": "Częścią klucza, którą można dodać na serwer do autoryzacji."},
        {"question": "Czy klucz prywatny kopiuje się na serwer?", "answer": "Nie, na serwer trafia klucz publiczny."},
        {"question": "Do czego służy ssh-keygen?", "answer": "Do tworzenia i zarządzania kluczami SSH."},
        {"question": "Co robi ssh-keygen -t ed25519?", "answer": "Tworzy parę kluczy typu ed25519."},
        {"question": "Po co komentarz w kluczu SSH?", "answer": "Pomaga rozpoznać właściciela lub przeznaczenie klucza."},
        {"question": "Gdzie zwykle są klucze użytkownika?", "answer": "W katalogu ~/.ssh."},
        {"question": "Co zawiera authorized_keys?", "answer": "Klucze publiczne, którym wolno logować się na konto użytkownika."},
        {"question": "Do czego służy ssh-copy-id?", "answer": "Do wygodnego skopiowania klucza publicznego na serwer."},
        {"question": "Jak wskazać konkretny klucz publiczny w ssh-copy-id?", "answer": "Opcją -i, na przykład ssh-copy-id -i ~/.ssh/id_ed25519.pub user@example.com."},
        {"question": "Jak wskazać konkretny klucz prywatny przy logowaniu?", "answer": "Opcją ssh -i ścieżka_do_klucza."},
        {"question": "Jakie uprawnienia ustawić na ~/.ssh?", "answer": "Zwykle 700."},
        {"question": "Jakie uprawnienia ustawić na authorized_keys?", "answer": "Zwykle 600."},
        {"question": "Dlaczego uprawnienia .ssh są ważne?", "answer": "OpenSSH może odrzucić zbyt szeroko dostępne pliki dla bezpieczeństwa."},
        {"question": "Co oznacza plik z końcówką .pub?", "answer": "Klucz publiczny."},
        {"question": "Czy ssh -i powinno wskazywać plik .pub?", "answer": "Nie, wskazuje klucz prywatny."},
        {"question": "Co sprawdzić, gdy klucz nie działa?", "answer": "Użytkownika, właściwy klucz, authorized_keys i uprawnienia."},
        {"question": "Dlaczego warto dodać hasło do klucza prywatnego?", "answer": "Chroni klucz, jeśli ktoś skopiuje plik."},
        {"question": "Czy authorized_keys jest wspólne dla wszystkich kont?", "answer": "Nie, każde konto ma własny plik w swoim katalogu domowym."},
        {"question": "Co może oznaczać Permission denied (publickey)?", "answer": "Serwer nie zaakceptował użytego klucza lub konto jest błędne."},
        {"question": "Czy można mieć wiele kluczy SSH?", "answer": "Tak, często używa się różnych kluczy do różnych środowisk."},
        {"question": "Co zrobić przed wygenerowaniem nowego klucza?", "answer": "Sprawdzić, czy nie nadpiszesz ważnego istniejącego klucza."},
        {"question": "Po co testować logowanie po skopiowaniu klucza?", "answer": "Aby potwierdzić, że serwer akceptuje nowy klucz."},
        {"question": "Jaka jest najważniejsza zasada kluczy SSH?", "answer": "Chroń klucz prywatny i kopiuj tylko klucz publiczny."},
    ],
}
