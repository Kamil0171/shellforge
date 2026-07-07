SSH_ADMINISTRATION = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "SSH w administracji systemem",
        "level": "Podstawowy+",
        "duration": "50 min",
        "description": (
            "Poznasz podstawy bezpiecznego logowania do serwera przez SSH, rolę kluczy oraz pliku "
            "known_hosts, bez wchodzenia w zaawansowaną konfigurację produkcyjną."
        ),
        "theory": (
            "SSH to podstawowy sposób zdalnej pracy z serwerem Linux. Pozwala otworzyć zaszyfrowaną sesję "
            "terminala, uruchamiać polecenia i administrować systemem bez fizycznego dostępu do maszyny. "
            "Typowe połączenie ma postać <code>ssh użytkownik@adres</code>. Domyślnie SSH używa portu "
            "<code>22</code>, ale sam port nie jest mechanizmem bezpieczeństwa. Logowanie może korzystać "
            "z hasła albo z pary kluczy. Klucz prywatny zostaje na komputerze administratora i powinien "
            "być chroniony, a klucz publiczny trafia na serwer do pliku <code>~/.ssh/authorized_keys</code>. "
            "Do utworzenia pary służy <code>ssh-keygen</code>, a do wygodnego skopiowania klucza publicznego "
            "na serwer często używa się <code>ssh-copy-id</code>. Przy pierwszym połączeniu klient SSH pyta "
            "o potwierdzenie odcisku klucza hosta. Po akceptacji zapisuje go w <code>~/.ssh/known_hosts</code>. "
            "Ten plik pomaga wykryć sytuację, w której pod znanym adresem odpowiada inny serwer. W praktyce "
            "należy rozumieć różnicę między kluczem użytkownika, który uwierzytelnia administratora, a kluczem "
            "hosta, który identyfikuje serwer."
        ),
        "commands": [
            {
                "command": "ssh user@example.com",
                "description": "Łączy się z serwerem jako wskazany użytkownik.",
                "example": "$ ssh user@example.com",
            },
            {
                "command": "ssh -p 2222 user@example.com",
                "description": "Łączy się z serwerem SSH na niestandardowym porcie.",
                "example": "$ ssh -p 2222 user@example.com",
            },
            {
                "command": "ssh-keygen -t ed25519 -C \"admin@example.com\"",
                "description": "Tworzy parę kluczy SSH typu ed25519 z komentarzem.",
                "example": "$ ssh-keygen -t ed25519 -C \"admin@example.com\"",
            },
            {
                "command": "ssh-copy-id user@example.com",
                "description": "Kopiuje klucz publiczny użytkownika na serwer.",
                "example": "$ ssh-copy-id user@example.com",
            },
            {
                "command": "ssh-keygen -l -f ~/.ssh/id_ed25519.pub",
                "description": "Pokazuje odcisk klucza publicznego użytkownika.",
                "example": "$ ssh-keygen -l -f ~/.ssh/id_ed25519.pub",
            },
            {
                "command": "ssh-keygen -F example.com",
                "description": "Sprawdza wpis hosta w pliku known_hosts.",
                "example": "$ ssh-keygen -F example.com",
            },
        ],
        "practice_task": (
            "W środowisku laboratoryjnym sprawdź, czy masz katalog <code>~/.ssh</code> i pliki kluczy. "
            "Jeśli nie masz pary testowej, utwórz ją poleceniem "
            "<code>ssh-keygen -t ed25519 -C \"lab@example.com\"</code>, nie nadpisując ważnych kluczy. "
            "Wyświetl odcisk klucza publicznego przez <code>ssh-keygen -l -f ~/.ssh/id_ed25519.pub</code>. "
            "Jeśli masz testowy serwer, połącz się przez <code>ssh user@example.com</code> i sprawdź, czy "
            "host pojawił się w <code>known_hosts</code> przez <code>ssh-keygen -F example.com</code>."
        ),
        "common_mistakes": [
            "Mylenie klucza prywatnego z publicznym i kopiowanie prywatnego na serwer.",
            "Nadpisywanie istniejących kluczy bez sprawdzenia, do czego są używane.",
            "Ignorowanie ostrzeżenia o zmianie klucza hosta.",
            "Zakładanie, że zmiana portu SSH sama w sobie zabezpiecza serwer.",
            "Używanie konta root do codziennej pracy zamiast zwykłego użytkownika z sudo.",
            "Brak hasła do klucza prywatnego na komputerze administratora.",
        ],
        "summary": (
            "SSH umożliwia zdalną, szyfrowaną pracę z serwerem. Klucz publiczny może trafić na serwer, "
            "ale klucz prywatny zostaje u administratora. <code>ssh-keygen</code> tworzy klucze, "
            "<code>ssh-copy-id</code> kopiuje klucz publiczny, a <code>known_hosts</code> pomaga "
            "rozpoznać znany serwer."
        ),
    },
    "quiz": {
        "title": "Quiz: SSH w administracji systemem",
        "description": "Sprawdź, czy rozumiesz podstawy logowania SSH, kluczy i known_hosts.",
        "questions": [
            {
                "text": "Do czego służy SSH?",
                "answers": [
                    ("a", "Do zdalnej, szyfrowanej pracy z serwerem", True),
                    ("b", "Do czyszczenia cache pakietów", False),
                    ("c", "Do zmiany maski plików", False),
                    ("d", "Do tworzenia rekordów MX", False),
                ],
            },
            {
                "text": "Jaki port jest domyślnie używany przez SSH?",
                "answers": [
                    ("a", "22", True),
                    ("b", "53", False),
                    ("c", "80", False),
                    ("d", "443", False),
                ],
            },
            {
                "text": "Który klucz powinien pozostać tylko na komputerze administratora?",
                "answers": [
                    ("a", "Klucz prywatny", True),
                    ("b", "Klucz publiczny", False),
                    ("c", "Rekord MX", False),
                    ("d", "Adres bramy", False),
                ],
            },
            {
                "text": "Do czego służy ssh-copy-id?",
                "answers": [
                    ("a", "Do skopiowania klucza publicznego na serwer", True),
                    ("b", "Do usunięcia konta użytkownika", False),
                    ("c", "Do wyłączenia firewalla", False),
                    ("d", "Do sprawdzenia rozmiaru logów", False),
                ],
            },
            {
                "text": "Co przechowuje plik known_hosts?",
                "answers": [
                    ("a", "Znane klucze hostów serwerów SSH", True),
                    ("b", "Hasła użytkowników w jawnej postaci", False),
                    ("c", "Listę rekordów DNS", False),
                    ("d", "Reguły firewalla", False),
                ],
            },
            {
                "text": "Co może oznaczać ostrzeżenie o zmianie klucza hosta?",
                "answers": [
                    ("a", "Pod znanym adresem odpowiada inny serwer lub zmienił się jego klucz", True),
                    ("b", "Zawsze poprawną aktualizację DNS", False),
                    ("c", "Brak miejsca w katalogu /tmp", False),
                    ("d", "Wyłącznie błąd komendy ls", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest SSH?", "answer": "Protokołem do zdalnej, szyfrowanej pracy z systemem."},
        {"question": "Jaka komenda łączy z serwerem SSH?", "answer": "ssh użytkownik@adres."},
        {"question": "Jaki port domyślnie ma SSH?", "answer": "22."},
        {"question": "Jak wskazać inny port SSH?", "answer": "Opcją -p, na przykład ssh -p 2222 user@example.com."},
        {"question": "Czym jest klucz prywatny SSH?", "answer": "Tajnym kluczem pozostającym na komputerze użytkownika."},
        {"question": "Czym jest klucz publiczny SSH?", "answer": "Kluczem, który można dodać na serwer do autoryzacji logowania."},
        {"question": "Gdzie na serwerze trafia klucz publiczny użytkownika?", "answer": "Zwykle do ~/.ssh/authorized_keys."},
        {"question": "Do czego służy ssh-keygen?", "answer": "Do tworzenia i analizowania kluczy SSH."},
        {"question": "Co robi ssh-keygen -t ed25519?", "answer": "Tworzy parę kluczy typu ed25519."},
        {"question": "Po co komentarz w kluczu SSH?", "answer": "Ułatwia rozpoznanie właściciela lub przeznaczenia klucza."},
        {"question": "Do czego służy ssh-copy-id?", "answer": "Do skopiowania klucza publicznego na serwer."},
        {"question": "Czym jest known_hosts?", "answer": "Plikiem z zapamiętanymi kluczami hostów SSH."},
        {"question": "Po co klient SSH zapisuje host w known_hosts?", "answer": "Aby później wykrywać zmianę tożsamości serwera."},
        {"question": "Czym jest klucz hosta?", "answer": "Kluczem identyfikującym serwer SSH."},
        {"question": "Czy klucz hosta i klucz użytkownika to to samo?", "answer": "Nie. Klucz hosta identyfikuje serwer, a klucz użytkownika administratora."},
        {"question": "Co sprawdza ssh-keygen -F example.com?", "answer": "Wpis hosta w known_hosts."},
        {"question": "Co pokazuje ssh-keygen -l -f klucz.pub?", "answer": "Odcisk wskazanego klucza publicznego."},
        {"question": "Czy należy kopiować klucz prywatny na serwer?", "answer": "Nie, na serwer trafia klucz publiczny."},
        {"question": "Czy hasło do klucza prywatnego jest przydatne?", "answer": "Tak, chroni klucz, gdy plik zostanie skopiowany przez niepowołaną osobę."},
        {"question": "Czy zmiana portu SSH zastępuje dobre uwierzytelnianie?", "answer": "Nie, to nie zastępuje kluczy, aktualizacji i zasad dostępu."},
        {"question": "Dlaczego warto używać zwykłego użytkownika z sudo?", "answer": "Ogranicza codzienną pracę bezpośrednio na koncie root."},
        {"question": "Co zrobić przy ostrzeżeniu o zmianie klucza hosta?", "answer": "Zweryfikować przyczynę przed zaakceptowaniem nowego klucza."},
        {"question": "Czy SSH służy tylko do logowania interaktywnego?", "answer": "Nie, może też uruchamiać zdalne polecenia i kopiować dane przez narzędzia używające SSH."},
        {"question": "Co jest podstawą bezpiecznej pracy z kluczami?", "answer": "Ochrona klucza prywatnego i rozważne dodawanie kluczy publicznych."},
        {"question": "Jaki jest pierwszy test dostępu SSH?", "answer": "Połączenie ssh użytkownik@adres i analiza komunikatu błędu lub sukcesu."},
    ],
}
