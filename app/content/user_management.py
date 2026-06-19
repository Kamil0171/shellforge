USER_MANAGEMENT = {
    "module": {
        "title": "Administracja systemem",
        "description": "Moduł poświęcony podstawowej administracji systemem Linux.",
    },
    "lesson": {
        "title": "Zarządzanie użytkownikami i grupami: useradd, passwd, usermod i userdel",
        "level": "Podstawowy+",
        "duration": "45 min",
        "description": (
            "Nauczysz się tworzyć konta i grupy, ustawiać hasła, zmieniać członkostwo "
            "w grupach oraz bezpiecznie usuwać użytkowników w Rocky Linux 9."
        ),
        "theory": (
            "Konta użytkowników pozwalają oddzielić pliki, procesy i uprawnienia różnych osób "
            "oraz usług. Administrator może utworzyć konto poleceniem <code>useradd</code>, a "
            "opcja <code>-m</code> tworzy katalog domowy. Hasło ustawia się osobnym poleceniem "
            "<code>passwd użytkownik</code>; nie należy umieszczać hasła w historii poleceń. "
            "Grupy ułatwiają przyznawanie wspólnego dostępu. <code>groupadd</code> tworzy grupę, "
            "a <code>usermod -aG grupa użytkownik</code> dopisuje użytkownika do grupy dodatkowej. "
            "Opcja <code>-a</code> jest ważna, ponieważ użycie samego <code>-G</code> może zastąpić "
            "dotychczasową listę grup dodatkowych. Wynik zmian warto sprawdzić przez "
            "<code>id</code> lub <code>groups</code>. Polecenie <code>userdel</code> usuwa konto, "
            "ale domyślnie może pozostawić katalog domowy. <code>userdel -r</code> usuwa również "
            "katalog domowy i pocztę użytkownika, dlatego przed jego użyciem trzeba sprawdzić dane, "
            "procesy i potrzebę wykonania kopii zapasowej. Nowe członkostwo w grupie zwykle zaczyna "
            "obowiązywać w nowej sesji logowania."
        ),
        "commands": [
            {
                "command": "sudo useradd -m anna",
                "description": "Tworzy konto anna wraz z katalogiem domowym.",
                "example": "$ sudo useradd -m anna",
            },
            {
                "command": "sudo passwd anna",
                "description": "Ustawia lub zmienia hasło użytkownika anna.",
                "example": "$ sudo passwd anna",
            },
            {
                "command": "id anna",
                "description": "Pokazuje UID, grupę podstawową i grupy dodatkowe użytkownika.",
                "example": "$ id anna",
            },
            {
                "command": "sudo groupadd devops",
                "description": "Tworzy nową grupę devops.",
                "example": "$ sudo groupadd devops",
            },
            {
                "command": "sudo usermod -aG devops anna",
                "description": "Dodaje użytkownika anna do grupy dodatkowej devops.",
                "example": "$ sudo usermod -aG devops anna",
            },
            {
                "command": "groups anna",
                "description": "Sprawdza grupy, do których należy użytkownik anna.",
                "example": "$ groups anna\nanna : anna devops",
            },
            {
                "command": "sudo userdel anna",
                "description": "Usuwa konto, ale domyślnie może pozostawić jego katalog domowy.",
                "example": "$ sudo userdel anna",
            },
            {
                "command": "sudo userdel -r anna",
                "description": "Usuwa konto oraz jego katalog domowy po wcześniejszej weryfikacji danych.",
                "example": "$ sudo userdel -r anna",
            },
        ],
        "practice_task": (
            "W przeznaczonej do ćwiczeń maszynie utwórz konto <code>labuser</code> poleceniem "
            "<code>sudo useradd -m labuser</code> i ustaw mu hasło przez "
            "<code>sudo passwd labuser</code>. Utwórz grupę <code>operators</code>, dodaj do niej "
            "konto przez <code>sudo usermod -aG operators labuser</code>, a następnie sprawdź wynik "
            "komendami <code>id labuser</code> i <code>groups labuser</code>. Przed sprzątnięciem "
            "ćwiczenia sprawdź zawartość katalogu domowego. Usuń konto i jego dane przez "
            "<code>sudo userdel -r labuser</code> tylko wtedy, gdy masz pewność, że niczego nie "
            "trzeba zachować. Ćwiczenia nie wykonuj na koncie używanym do logowania lub administracji."
        ),
        "common_mistakes": [
            "Tworzenie konta bez katalogu domowego, mimo że użytkownik ma pracować interaktywnie.",
            "Wpisywanie hasła bezpośrednio jako argumentu polecenia lub zapisywanie go w skrypcie.",
            "Użycie <code>usermod -G</code> bez <code>-a</code> i przypadkowe usunięcie innych grup dodatkowych.",
            "Zakładanie, że nowe członkostwo w grupie zawsze zadziała w już otwartej sesji.",
            "Usuwanie konta bez sprawdzenia jego procesów, plików i potrzebnej kopii danych.",
            "Używanie <code>userdel -r</code> bez zrozumienia, że usuwa katalog domowy.",
            "Dodawanie użytkownika do grupy wheel bez uzasadnionej potrzeby administracyjnej.",
        ],
        "summary": (
            "<code>useradd -m</code> tworzy konto z katalogiem domowym, <code>passwd</code> ustawia "
            "hasło, a <code>groupadd</code> tworzy grupę. Bezpieczne dodawanie do grupy dodatkowej "
            "wykorzystuje <code>usermod -aG</code>, po czym zmianę należy sprawdzić przez "
            "<code>id</code> lub <code>groups</code>. <code>userdel -r</code> usuwa także dane "
            "z katalogu domowego, więc wymaga wcześniejszej weryfikacji i ewentualnej kopii zapasowej."
        ),
    },
    "quiz": {
        "title": "Quiz: zarządzanie użytkownikami i grupami",
        "description": "Sprawdź praktyczne rozumienie tworzenia, modyfikowania i usuwania kont.",
        "questions": [
            {
                "text": "Chcesz utworzyć interaktywne konto anna wraz z katalogiem domowym. Której komendy użyjesz?",
                "answers": [
                    ("a", "sudo useradd -m anna", True),
                    ("b", "sudo userdel -r anna", False),
                    ("c", "groups anna", False),
                    ("d", "sudo passwd -d root", False),
                ],
            },
            {
                "text": "Jak bezpiecznie ustawić hasło nowemu użytkownikowi anna?",
                "answers": [
                    ("a", "Uruchomić sudo passwd anna i wpisać hasło w interaktywnym monicie", True),
                    ("b", "Dodać hasło do nazwy użytkownika", False),
                    ("c", "Zapisać hasło w publicznym pliku", False),
                    ("d", "Użyć groups anna", False),
                ],
            },
            {
                "text": "Która komenda dodaje annę do grupy devops bez zastępowania innych grup dodatkowych?",
                "answers": [
                    ("a", "sudo usermod -aG devops anna", True),
                    ("b", "sudo usermod -G devops anna", False),
                    ("c", "sudo userdel devops anna", False),
                    ("d", "sudo groupadd anna devops", False),
                ],
            },
            {
                "text": "Jak sprawdzić UID i wszystkie grupy użytkownika anna?",
                "answers": [
                    ("a", "id anna", True),
                    ("b", "pwd anna", False),
                    ("c", "df -h anna", False),
                    ("d", "hostnamectl anna", False),
                ],
            },
            {
                "text": "Co należy zrobić przed użyciem userdel -r anna?",
                "answers": [
                    ("a", "Sprawdzić dane użytkownika i wykonać potrzebną kopię zapasową", True),
                    ("b", "Dodać annę do wszystkich grup", False),
                    ("c", "Wyłączyć logowanie dla wszystkich kont", False),
                    ("d", "Usunąć plik /etc/passwd", False),
                ],
            },
            {
                "text": "Dlaczego samo usermod -G devops anna może być niebezpieczne?",
                "answers": [
                    ("a", "Może zastąpić dotychczasowe grupy dodatkowe użytkownika", True),
                    ("b", "Zawsze usuwa katalog domowy", False),
                    ("c", "Zmienia nazwę hosta", False),
                    ("d", "Automatycznie usuwa grupę devops", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Do czego służy useradd?",
            "answer": "Do tworzenia nowego konta użytkownika.",
        },
        {
            "question": "Co robi useradd -m anna?",
            "answer": "Tworzy konto anna wraz z katalogiem domowym.",
        },
        {
            "question": "Dlaczego opcja -m jest przydatna?",
            "answer": "Tworzy katalog domowy potrzebny użytkownikowi do interaktywnej pracy.",
        },
        {
            "question": "Do czego służy passwd anna?",
            "answer": "Do ustawienia lub zmiany hasła użytkownika anna.",
        },
        {
            "question": "Czy hasło należy podawać jako zwykły argument polecenia?",
            "answer": "Nie. Należy użyć bezpiecznego, interaktywnego monitu passwd.",
        },
        {
            "question": "Do czego służy groupadd?",
            "answer": "Do tworzenia nowej grupy użytkowników.",
        },
        {
            "question": "Co robi groupadd devops?",
            "answer": "Tworzy grupę o nazwie devops.",
        },
        {
            "question": "Do czego służy usermod?",
            "answer": "Do modyfikowania właściwości istniejącego konta użytkownika.",
        },
        {
            "question": "Co robi usermod -aG devops anna?",
            "answer": "Dodaje użytkownika anna do dodatkowej grupy devops.",
        },
        {
            "question": "Co oznacza -G w usermod?",
            "answer": "Wskazuje listę grup dodatkowych użytkownika.",
        },
        {
            "question": "Co oznacza -a w usermod -aG?",
            "answer": "Dopisuje wskazaną grupę bez zastępowania pozostałych grup dodatkowych.",
        },
        {
            "question": "Dlaczego niebezpieczne jest usermod -G bez -a?",
            "answer": "Może usunąć użytkownika z niewymienionych grup dodatkowych.",
        },
        {
            "question": "Jak sprawdzić dane konta po modyfikacji?",
            "answer": "Za pomocą id nazwa_użytkownika.",
        },
        {
            "question": "Jak szybko sprawdzić grupy użytkownika?",
            "answer": "Za pomocą groups nazwa_użytkownika.",
        },
        {
            "question": "Kiedy nowe członkostwo w grupie zwykle zaczyna działać?",
            "answer": "Po rozpoczęciu nowej sesji logowania użytkownika.",
        },
        {
            "question": "Do czego służy userdel?",
            "answer": "Do usuwania konta użytkownika.",
        },
        {
            "question": "Czy userdel zawsze usuwa katalog domowy?",
            "answer": "Nie. Bez opcji -r katalog domowy może pozostać.",
        },
        {
            "question": "Co robi userdel -r anna?",
            "answer": "Usuwa konto anna oraz jego katalog domowy i lokalną pocztę.",
        },
        {
            "question": "Co sprawdzić przed userdel -r?",
            "answer": "Pliki, procesy użytkownika oraz potrzebę wykonania kopii zapasowej.",
        },
        {
            "question": "Dlaczego grupy ułatwiają administrację?",
            "answer": "Pozwalają przyznawać wspólny dostęp wielu użytkownikom.",
        },
        {
            "question": "Czym różni się grupa podstawowa od dodatkowej?",
            "answer": "Podstawowa jest główną grupą konta, a dodatkowe rozszerzają jego dostęp.",
        },
        {
            "question": "Czy warto nadawać każdemu użytkownikowi grupę wheel?",
            "answer": "Nie. Dostęp administracyjny powinny mieć tylko osoby, które go potrzebują.",
        },
        {
            "question": "Jak sprawdzić, czy konto zostało utworzone?",
            "answer": "Uruchomić id nazwa_użytkownika i sprawdzić zwrócone UID oraz grupy.",
        },
        {
            "question": "Czy należy ćwiczyć userdel na własnym koncie?",
            "answer": "Nie. Do ćwiczeń trzeba użyć osobnego konta w środowisku laboratoryjnym.",
        },
        {
            "question": "Jaka jest bezpieczna kolejność zarządzania kontem?",
            "answer": "Utworzyć konto, ustawić hasło, nadać potrzebne grupy, zweryfikować i ostrożnie usunąć.",
        },
    ],
}
