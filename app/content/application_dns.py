APPLICATION_DNS = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Domena i rekordy DNS dla aplikacji",
        "level": "Średnio zaawansowany",
        "duration": "55 min",
        "description": (
            "Skierujesz domenę lub subdomenę na serwer aplikacji i sprawdzisz rekordy DNS z kilku perspektyw, "
            "od publicznych resolverów po lokalny plik hosts."
        ),
        "theory": (
            "Domena główna, na przykład <code>example.com</code>, może mieć subdomenę "
            "<code>app.example.com</code> przeznaczoną dla aplikacji. Rekord <code>A</code> wiąże nazwę z "
            "adresem IPv4, a <code>AAAA</code> z IPv6. Rekord <code>CNAME</code> tworzy alias do innej nazwy "
            "DNS; nie jest zamiennikiem rekordu adresowego w każdej sytuacji. Warto publikować tylko rekordy "
            "dla protokołów faktycznie skonfigurowanych na serwerze. Nazwa użyta w DNS powinna odpowiadać "
            "<code>server_name app.example.com</code> w Nginxie. TTL określa, jak długo odpowiedź może być "
            "przechowywana w cache. Po zmianie część resolverów może nadal zwracać starszą wartość aż do "
            "wygaśnięcia cache; ten proces potocznie nazywa się propagacją DNS. <code>dig</code>, "
            "<code>host</code> i <code>getent hosts</code> pokazują wynik z różnych perspektyw. Zapytania do "
            "resolverów takich jak <code>1.1.1.1</code> i <code>8.8.8.8</code> pomagają porównać publiczny "
            "stan. Lokalny wpis w <code>/etc/hosts</code> może chwilowo mapować domenę do IP na jednym "
            "komputerze, lecz nie publikuje niczego w DNS. Poprawny DNS wskazuje host, ale nie uruchamia "
            "Nginxa, nie otwiera portu i nie gwarantuje odpowiedzi aplikacji."
        ),
        "commands": [
            {
                "command": "dig A app.example.com",
                "description": "Pyta domyślny resolver o rekord IPv4 subdomeny.",
                "example": "$ dig A app.example.com",
            },
            {
                "command": "dig AAAA app.example.com",
                "description": "Sprawdza, czy dla subdomeny opublikowano rekord IPv6.",
                "example": "$ dig AAAA app.example.com",
            },
            {
                "command": "dig @1.1.1.1 app.example.com A +short",
                "description": "Pyta wybrany publiczny resolver o krótki wynik rekordu A.",
                "example": "$ dig @1.1.1.1 app.example.com A +short\n203.0.113.10",
            },
            {
                "command": "dig @8.8.8.8 app.example.com A +short",
                "description": "Pozwala porównać odpowiedź z innym publicznym resolverem.",
                "example": "$ dig @8.8.8.8 app.example.com A +short\n203.0.113.10",
            },
            {
                "command": "host app.example.com",
                "description": "Pokazuje prostą informację o adresach przypisanych do nazwy.",
                "example": "$ host app.example.com",
            },
            {
                "command": "getent hosts app.example.com",
                "description": "Sprawdza rozwiązanie nazwy używane przez lokalny system, także z uwzględnieniem hosts.",
                "example": "$ getent hosts app.example.com",
            },
        ],
        "practice_task": (
            "Dla laboratoryjnej subdomeny <code>app.example.com</code> zaplanuj rekord A wskazujący adres IPv4 "
            "serwera. Jeśli serwer nie obsługuje poprawnie IPv6, nie dodawaj rekordu AAAA. Zapisz wartość TTL "
            "i skonfiguruj zgodny <code>server_name</code> w przykładowym bloku Nginxa. Sprawdź wynik przez "
            "<code>dig</code>, <code>host</code> i <code>getent hosts</code>, a następnie porównaj odpowiedzi "
            "resolverów 1.1.1.1 oraz 8.8.8.8. Jeżeli nie zarządzasz prawdziwą domeną, wykonaj ćwiczenie jako "
            "plan i opcjonalnie użyj lokalnego wpisu hosts wyłącznie w laboratorium."
        ),
        "common_mistakes": [
            "Skierowanie rekordu A na nieaktualny lub prywatny adres IPv4 serwera.",
            "Dodanie rekordu AAAA mimo braku działającej konfiguracji IPv6.",
            "Niezgodność domeny w DNS z wartością server_name w Nginxie.",
            "Oczekiwanie natychmiastowej zmiany mimo aktywnego cache i wcześniejszego TTL.",
            "Traktowanie wpisu w /etc/hosts jako publicznej konfiguracji DNS.",
            "Użycie CNAME bez zrozumienia, że wskazuje nazwę, a nie bezpośrednio adres IP.",
            "Wnioskowanie z poprawnego DNS, że aplikacja i port HTTP muszą działać.",
        ],
        "summary": (
            "Rekord A kieruje nazwę na IPv4, AAAA na IPv6, a CNAME tworzy alias do innej nazwy. Domena w DNS "
            "musi być zgodna z <code>server_name</code> Nginxa. TTL i cache DNS wyjaśniają, dlaczego różne "
            "resolvery mogą przez pewien czas zwracać inne odpowiedzi. <code>dig</code>, <code>host</code> i "
            "<code>getent hosts</code> pozwalają porównać stan publiczny z lokalnym rozwiązywaniem nazw."
        ),
    },
    "quiz": {
        "title": "Quiz: domena i rekordy DNS dla aplikacji",
        "description": "Sprawdź praktyczne rozumienie rekordów, TTL, cache i diagnostyki DNS.",
        "questions": [
            {
                "text": "Który rekord kieruje app.example.com bezpośrednio na adres IPv4?",
                "answers": [
                    ("a", "A", True),
                    ("b", "AAAA", False),
                    ("c", "CNAME zawsze zawierający IPv4", False),
                    ("d", "TXT", False),
                ],
            },
            {
                "text": "Kiedy rekord AAAA ma sens?",
                "answers": [
                    ("a", "Gdy serwer i usługa są poprawnie dostępne przez IPv6", True),
                    ("b", "Gdy serwer ma wyłącznie IPv4", False),
                    ("c", "Gdy chcemy utworzyć venv", False),
                    ("d", "Gdy Uvicorn zgłasza zajęty port", False),
                ],
            },
            {
                "text": "Co przechowuje rekord CNAME?",
                "answers": [
                    ("a", "Alias wskazujący inną nazwę DNS", True),
                    ("b", "Polecenie uruchamiające systemd", False),
                    ("c", "Zawsze bezpośredni adres IPv6", False),
                    ("d", "Nagłówek X-Real-IP", False),
                ],
            },
            {
                "text": "Jak TTL wpływa na zmianę DNS?",
                "answers": [
                    ("a", "Określa, jak długo odpowiedź może pozostawać w cache", True),
                    ("b", "Uruchamia Nginx po zmianie rekordu", False),
                    ("c", "Wybiera wersję Pythona", False),
                    ("d", "Zmienia właściciela katalogu aplikacji", False),
                ],
            },
            {
                "text": "Po co pytać dwa publiczne resolvery przez dig?",
                "answers": [
                    ("a", "Aby porównać, czy oba widzą już tę samą wartość rekordu", True),
                    ("b", "Aby automatycznie zmienić rekord u operatora domeny", False),
                    ("c", "Aby przeładować konfigurację Nginxa", False),
                    ("d", "Aby zainstalować Uvicorna", False),
                ],
            },
            {
                "text": "Co daje wpis app.example.com w lokalnym /etc/hosts?",
                "answers": [
                    ("a", "Lokalne mapowanie nazwy na tym komputerze, bez publikacji w DNS", True),
                    ("b", "Publiczny rekord widoczny dla wszystkich użytkowników internetu", False),
                    ("c", "Automatyczny certyfikat HTTPS", False),
                    ("d", "Nową jednostkę systemd na serwerze", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest domena główna?", "answer": "Nazwą bazową, na przykład example.com."},
        {"question": "Czym jest subdomena?", "answer": "Nazwą umieszczoną przed domeną główną, na przykład app.example.com."},
        {"question": "Co zawiera rekord A?", "answer": "Adres IPv4 przypisany do nazwy DNS."},
        {"question": "Co zawiera rekord AAAA?", "answer": "Adres IPv6 przypisany do nazwy DNS."},
        {"question": "Co zawiera rekord CNAME?", "answer": "Alias wskazujący inną nazwę DNS."},
        {"question": "Czy CNAME wskazuje bezpośrednio adres IP?", "answer": "Nie, wskazuje inną nazwę DNS."},
        {"question": "Jaki adres powinien zawierać rekord A aplikacji?", "answer": "Publiczny adres IPv4 właściwego serwera."},
        {"question": "Kiedy nie dodawać AAAA?", "answer": "Gdy serwer lub usługa nie działa poprawnie przez IPv6."},
        {"question": "Co oznacza TTL?", "answer": "Czas, przez który odpowiedź DNS może być przechowywana w cache."},
        {"question": "Czym jest propagacja DNS?", "answer": "Potocznym określeniem okresu, gdy resolvery odświeżają zapisane odpowiedzi po zmianie."},
        {"question": "Czym jest cache DNS?", "answer": "Tymczasowo zapisaną odpowiedzią używaną bez ponownego pytania serwera autorytatywnego."},
        {"question": "Dlaczego resolvery mogą zwracać różne IP?", "answer": "Mogą mieć odpowiedzi zapisane w cache z różnym czasem wygaśnięcia."},
        {"question": "Co sprawdza dig A?", "answer": "Rekord IPv4 wskazanej nazwy."},
        {"question": "Co sprawdza dig AAAA?", "answer": "Rekord IPv6 wskazanej nazwy."},
        {"question": "Co daje dig +short?", "answer": "Wyświetla skróconą odpowiedź bez większości metadanych."},
        {"question": "Jak wskazać resolver w dig?", "answer": "Dodać @adres-resolvera, na przykład @1.1.1.1."},
        {"question": "Do czego służy host?", "answer": "Do prostego sprawdzania rekordów i adresów nazwy DNS."},
        {"question": "Do czego służy getent hosts?", "answer": "Do sprawdzenia rozwiązywania nazwy używanego przez lokalny system."},
        {"question": "Czy getent uwzględnia /etc/hosts?", "answer": "Tak, zgodnie z lokalną konfiguracją źródeł nazw."},
        {"question": "Czy /etc/hosts publikuje rekord DNS?", "answer": "Nie, wpływa tylko na lokalne rozwiązywanie nazwy."},
        {"question": "Jak DNS łączy się z Nginxem?", "answer": "Nazwa kieruje na serwer, a zgodny server_name wybiera właściwy blok."},
        {"question": "Czy poprawny DNS uruchamia aplikację?", "answer": "Nie, proces aplikacji i Nginx muszą działać niezależnie."},
        {"question": "Czy DNS otwiera port 80?", "answer": "Nie, dostęp do portu zależy od usługi, sieci i firewalla."},
        {"question": "Co sprawdzić po zmianie rekordu?", "answer": "Wartość i TTL przez kilka resolverów oraz lokalne rozwiązanie nazwy."},
        {"question": "Jaki jest typowy błąd przy domenie aplikacji?", "answer": "Rekord wskazuje niewłaściwy adres albo nie pasuje do server_name."},
    ],
}
