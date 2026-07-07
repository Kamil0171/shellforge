SELINUX_BASICS = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "SELinux — podstawowe pojęcia",
        "level": "Podstawowy+",
        "duration": "45 min",
        "description": (
            "Poznasz podstawowe tryby SELinux, znaczenie kontekstów bezpieczeństwa oraz pierwsze komendy "
            "do sprawdzania stanu SELinux w systemach takich jak Rocky Linux."
        ),
        "theory": (
            "SELinux to mechanizm kontroli dostępu, który działa obok klasycznych uprawnień Linuxa. "
            "Nawet jeśli użytkownik i uprawnienia pliku wyglądają poprawnie, SELinux może zablokować "
            "działanie, jeśli polityka bezpieczeństwa na to nie pozwala. W trybie <code>enforcing</code> "
            "SELinux egzekwuje reguły i blokuje niedozwolone akcje. W trybie <code>permissive</code> "
            "nie blokuje, ale zapisuje ostrzeżenia, co pomaga w diagnozie. Tryb <code>disabled</code> "
            "oznacza, że SELinux jest wyłączony. Ważnym pojęciem jest kontekst bezpieczeństwa, widoczny "
            "na przykład przez <code>ls -Z</code>. Kontekst opisuje między innymi typ obiektu, a polityka "
            "SELinux decyduje, które procesy mogą korzystać z danych typów plików. Początkujący administrator "
            "nie musi od razu pisać polityk SELinux, ale powinien umieć sprawdzić tryb pracy, status systemu "
            "i konteksty plików. W Rocky Linux SELinux jest istotną warstwą bezpieczeństwa, dlatego nie należy "
            "traktować wyłączenia go jako pierwszego rozwiązania problemu."
        ),
        "commands": [
            {
                "command": "getenforce",
                "description": "Pokazuje bieżący tryb SELinux w krótkiej formie.",
                "example": "$ getenforce",
            },
            {
                "command": "sestatus",
                "description": "Wyświetla szczegółowy status SELinux.",
                "example": "$ sestatus",
            },
            {
                "command": "ls -Z",
                "description": "Pokazuje pliki z kontekstami bezpieczeństwa SELinux.",
                "example": "$ ls -Z",
            },
            {
                "command": "ls -Zd /var/www/html",
                "description": "Pokazuje kontekst bezpieczeństwa wskazanego katalogu.",
                "example": "$ ls -Zd /var/www/html",
            },
            {
                "command": "ps -eZ | head",
                "description": "Pokazuje przykładowe procesy razem z kontekstami SELinux.",
                "example": "$ ps -eZ | head",
            },
            {
                "command": "id -Z",
                "description": "Pokazuje kontekst SELinux aktualnego użytkownika, jeśli jest dostępny.",
                "example": "$ id -Z",
            },
        ],
        "practice_task": (
            "Na maszynie z SELinux wykonaj <code>getenforce</code> i <code>sestatus</code>. Zapisz, "
            "czy system działa w trybie enforcing, permissive czy disabled. Następnie uruchom "
            "<code>ls -Z</code> w katalogu domowym oraz <code>ls -Zd /tmp</code>, aby zobaczyć konteksty "
            "plików i katalogów. Jeśli masz katalog webowy w środowisku testowym, porównaj jego kontekst "
            "z kontekstem zwykłego pliku w katalogu domowym. Nie zmieniaj polityki ani nie wyłączaj SELinux "
            "w tym ćwiczeniu."
        ),
        "common_mistakes": [
            "Traktowanie SELinux jako zwykłych uprawnień rwx.",
            "Wyłączanie SELinux jako pierwsza reakcja na problem z usługą.",
            "Pomijanie kontekstu pliku podczas diagnozowania dostępu.",
            "Mylenie trybu permissive z całkowitym wyłączeniem SELinux.",
            "Zakładanie, że poprawny właściciel pliku zawsze wystarcza aplikacji.",
            "Ignorowanie faktu, że procesy także mają konteksty SELinux.",
        ],
        "summary": (
            "SELinux jest dodatkową warstwą kontroli dostępu. Tryb <code>enforcing</code> blokuje działania "
            "niezgodne z polityką, <code>permissive</code> głównie loguje naruszenia, a "
            "<code>disabled</code> oznacza wyłączenie mechanizmu. <code>getenforce</code>, "
            "<code>sestatus</code> i <code>ls -Z</code> pomagają rozpocząć diagnozę bez zmieniania "
            "konfiguracji bezpieczeństwa."
        ),
    },
    "quiz": {
        "title": "Quiz: SELinux — podstawowe pojęcia",
        "description": "Sprawdź, czy rozumiesz tryby SELinux, konteksty i podstawowe komendy.",
        "questions": [
            {
                "text": "Czym jest SELinux?",
                "answers": [
                    ("a", "Dodatkowym mechanizmem kontroli dostępu w systemie Linux", True),
                    ("b", "Edytorem tekstu", False),
                    ("c", "Systemem DNS", False),
                    ("d", "Programem do czyszczenia cache DNF", False),
                ],
            },
            {
                "text": "Co oznacza tryb enforcing?",
                "answers": [
                    ("a", "SELinux egzekwuje politykę i może blokować niedozwolone akcje", True),
                    ("b", "SELinux jest całkowicie wyłączony", False),
                    ("c", "Firewall otwiera wszystkie porty", False),
                    ("d", "SSH działa bez kluczy", False),
                ],
            },
            {
                "text": "Co oznacza tryb permissive?",
                "answers": [
                    ("a", "SELinux nie blokuje, ale zapisuje naruszenia polityki", True),
                    ("b", "System usuwa wszystkie konteksty", False),
                    ("c", "DNS działa tylko po IPv6", False),
                    ("d", "Każdy użytkownik dostaje root", False),
                ],
            },
            {
                "text": "Która komenda pokazuje krótko bieżący tryb SELinux?",
                "answers": [
                    ("a", "getenforce", True),
                    ("b", "ip route", False),
                    ("c", "ssh-copy-id", False),
                    ("d", "firewall-cmd --list-all", False),
                ],
            },
            {
                "text": "Do czego służy ls -Z?",
                "answers": [
                    ("a", "Do pokazania kontekstów bezpieczeństwa SELinux", True),
                    ("b", "Do pokazania rekordów DNS", False),
                    ("c", "Do otwierania portów", False),
                    ("d", "Do tworzenia kluczy SSH", False),
                ],
            },
            {
                "text": "Dlaczego nie warto zaczynać diagnozy od wyłączenia SELinux?",
                "answers": [
                    ("a", "Bo usuwa się ważną warstwę ochrony zamiast zrozumieć przyczynę blokady", True),
                    ("b", "Bo getenforce przestaje istnieć", False),
                    ("c", "Bo DNS zawsze wymaga SELinux", False),
                    ("d", "Bo port 443 zmienia się na 22", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest SELinux?", "answer": "Mechanizmem kontroli dostępu działającym obok klasycznych uprawnień Linuxa."},
        {"question": "Czy SELinux zastępuje chmod?", "answer": "Nie, działa jako dodatkowa warstwa kontroli."},
        {"question": "Co oznacza enforcing?", "answer": "SELinux egzekwuje politykę i blokuje niedozwolone akcje."},
        {"question": "Co oznacza permissive?", "answer": "SELinux nie blokuje, ale loguje naruszenia polityki."},
        {"question": "Co oznacza disabled?", "answer": "SELinux jest wyłączony."},
        {"question": "Co robi getenforce?", "answer": "Pokazuje bieżący tryb SELinux."},
        {"question": "Co robi sestatus?", "answer": "Pokazuje szczegółowy status SELinux."},
        {"question": "Co robi ls -Z?", "answer": "Pokazuje konteksty SELinux plików."},
        {"question": "Co robi ls -Zd katalog?", "answer": "Pokazuje kontekst wskazanego katalogu jako obiektu."},
        {"question": "Czym jest kontekst SELinux?", "answer": "Etykietą bezpieczeństwa opisującą obiekt lub proces."},
        {"question": "Czy procesy mają konteksty SELinux?", "answer": "Tak, można je zobaczyć na przykład przez ps -eZ."},
        {"question": "Co pokazuje ps -eZ?", "answer": "Procesy razem z kontekstami SELinux."},
        {"question": "Co pokazuje id -Z?", "answer": "Kontekst SELinux aktualnego użytkownika, jeśli jest dostępny."},
        {"question": "Dlaczego poprawne rwx może nie wystarczyć?", "answer": "Bo SELinux może nadal blokować dostęp według polityki."},
        {"question": "Czy permissive to to samo co disabled?", "answer": "Nie, permissive nadal działa i loguje naruszenia."},
        {"question": "Dlaczego nie wyłączać SELinux od razu?", "answer": "Bo to osłabia bezpieczeństwo i ukrywa prawdziwą przyczynę problemu."},
        {"question": "Co najpierw sprawdzić przy podejrzeniu SELinux?", "answer": "Tryb przez getenforce i status przez sestatus."},
        {"question": "Co sprawdzić przy problemie z dostępem do pliku?", "answer": "Klasyczne uprawnienia oraz kontekst przez ls -Z."},
        {"question": "Czy Rocky Linux często używa SELinux?", "answer": "Tak, SELinux jest ważną częścią systemów z rodziny RHEL."},
        {"question": "Czym jest polityka SELinux?", "answer": "Zbiorem reguł określających dozwolone działania procesów i obiektów."},
        {"question": "Czy początkujący musi pisać polityki SELinux?", "answer": "Nie, na start wystarczy umieć sprawdzać tryb i konteksty."},
        {"question": "Co oznacza typ w kontekście SELinux?", "answer": "Część etykiety używana przez politykę do decyzji o dostępie."},
        {"question": "Czy SELinux jest firewallem?", "answer": "Nie, kontroluje dostęp procesów i obiektów, a firewall kontroluje ruch sieciowy."},
        {"question": "Czy SELinux jest powodem każdego błędu 403?", "answer": "Nie, to jedna z możliwych przyczyn do sprawdzenia."},
        {"question": "Jaki jest bezpieczny cel pierwszej lekcji SELinux?", "answer": "Nauczyć się sprawdzać stan i konteksty bez zmiany polityki."},
    ],
}
