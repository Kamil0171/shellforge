DNS_PRACTICE = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "DNS w praktyce",
        "level": "Podstawowy+",
        "duration": "45 min",
        "description": (
            "Nauczysz się sprawdzać, jak system zamienia nazwy domenowe na adresy IP, oraz poznasz "
            "najważniejsze typy rekordów DNS używane przy administracji serwerami."
        ),
        "theory": (
            "DNS to system, który tłumaczy nazwy domenowe na informacje potrzebne komputerom i usługom. "
            "Najczęściej kojarzy się z zamianą nazwy, takiej jak <code>example.com</code>, na adres IP. "
            "Rekord <code>A</code> wskazuje adres IPv4, <code>AAAA</code> adres IPv6, "
            "<code>CNAME</code> alias do innej nazwy, <code>MX</code> serwery poczty, a "
            "<code>TXT</code> tekstowe informacje wykorzystywane między innymi do weryfikacji domeny. "
            "Rozwiązywanie nazw odbywa się przez resolver systemowy, który korzysta z konfiguracji sieci "
            "i wskazanych serwerów DNS. W praktyce administrator powinien umieć odróżnić problem z siecią "
            "od problemu z DNS: jeśli połączenie z adresem IP działa, ale nazwa domenowa nie, podejrzenie "
            "pada na rozwiązywanie nazw. Komendy <code>dig</code>, <code>host</code> i "
            "<code>nslookup</code> pozwalają zadawać zapytania DNS, a <code>resolvectl</code> pokazuje "
            "informacje o resolverze używanym przez system. Przy diagnozie warto sprawdzać konkretny typ "
            "rekordu, nie tylko ogólną odpowiedź."
        ),
        "commands": [
            {
                "command": "dig example.com A",
                "description": "Pyta DNS o rekord A, czyli adres IPv4 domeny.",
                "example": "$ dig example.com A",
            },
            {
                "command": "dig example.com AAAA",
                "description": "Pyta DNS o rekord AAAA, czyli adres IPv6 domeny.",
                "example": "$ dig example.com AAAA",
            },
            {
                "command": "dig example.com MX",
                "description": "Pokazuje rekordy MX wskazujące serwery poczty dla domeny.",
                "example": "$ dig example.com MX",
            },
            {
                "command": "host example.com",
                "description": "Szybko pokazuje podstawowe informacje DNS dla domeny.",
                "example": "$ host example.com",
            },
            {
                "command": "nslookup example.com",
                "description": "Wykonuje proste zapytanie DNS znane z wielu systemów.",
                "example": "$ nslookup example.com",
            },
            {
                "command": "resolvectl status",
                "description": "Pokazuje stan resolvera DNS i serwery DNS używane przez system.",
                "example": "$ resolvectl status",
            },
            {
                "command": "resolvectl query example.com",
                "description": "Sprawdza, jak resolver systemowy rozwiązuje daną nazwę.",
                "example": "$ resolvectl query example.com",
            },
        ],
        "practice_task": (
            "Sprawdź domenę <code>example.com</code> poleceniami <code>dig example.com A</code>, "
            "<code>dig example.com AAAA</code>, <code>host example.com</code> oraz "
            "<code>nslookup example.com</code>. Porównaj, które odpowiedzi pokazują adres IPv4, a które "
            "IPv6. Następnie wykonaj <code>resolvectl status</code> i znajdź serwer DNS używany przez "
            "aktywny interfejs. Na końcu sprawdź <code>dig example.com MX</code> i zapisz, dlaczego rekord "
            "MX ma inne znaczenie niż rekord A."
        ),
        "common_mistakes": [
            "Mylenie rekordu A z dowolnym rekordem DNS.",
            "Zakładanie, że brak rekordu AAAA oznacza awarię całej domeny.",
            "Pomijanie resolvera systemowego podczas diagnozy problemu z nazwami.",
            "Mylenie CNAME z przekierowaniem HTTP.",
            "Sprawdzanie tylko przeglądarki zamiast konkretnego typu rekordu.",
            "Traktowanie DNS jako potwierdzenia, że sama usługa webowa działa poprawnie.",
        ],
        "summary": (
            "DNS zamienia nazwy na informacje, najczęściej adresy IP. Rekord <code>A</code> wskazuje "
            "IPv4, <code>AAAA</code> IPv6, <code>CNAME</code> alias, <code>MX</code> pocztę, a "
            "<code>TXT</code> dane tekstowe. <code>dig</code>, <code>host</code>, "
            "<code>nslookup</code> i <code>resolvectl</code> pomagają sprawdzać odpowiedzi DNS oraz "
            "konfigurację resolvera."
        ),
    },
    "quiz": {
        "title": "Quiz: DNS w praktyce",
        "description": "Sprawdź, czy rozumiesz podstawowe rekordy DNS i narzędzia diagnostyczne.",
        "questions": [
            {
                "text": "Do czego służy DNS?",
                "answers": [
                    ("a", "Do tłumaczenia nazw domenowych na informacje takie jak adresy IP", True),
                    ("b", "Do zmiany uprawnień plików", False),
                    ("c", "Do restartowania usług systemd", False),
                    ("d", "Do tworzenia kont użytkowników", False),
                ],
            },
            {
                "text": "Który rekord DNS wskazuje adres IPv4?",
                "answers": [
                    ("a", "A", True),
                    ("b", "MX", False),
                    ("c", "TXT", False),
                    ("d", "CNAME", False),
                ],
            },
            {
                "text": "Który rekord DNS wskazuje adres IPv6?",
                "answers": [
                    ("a", "AAAA", True),
                    ("b", "A", False),
                    ("c", "SOCK", False),
                    ("d", "PORT", False),
                ],
            },
            {
                "text": "Do czego służy rekord MX?",
                "answers": [
                    ("a", "Do wskazywania serwerów poczty dla domeny", True),
                    ("b", "Do otwierania portu SSH", False),
                    ("c", "Do wyłączania SELinux", False),
                    ("d", "Do pokazywania rozmiaru katalogu", False),
                ],
            },
            {
                "text": "Która komenda pyta o rekord A domeny example.com?",
                "answers": [
                    ("a", "dig example.com A", True),
                    ("b", "ss -tuln example.com", False),
                    ("c", "chmod example.com A", False),
                    ("d", "systemctl status example.com", False),
                ],
            },
            {
                "text": "Co pomaga sprawdzić resolvectl status?",
                "answers": [
                    ("a", "Konfigurację resolvera DNS używaną przez system", True),
                    ("b", "Listę użytkowników w systemie", False),
                    ("c", "Rozmiar pamięci RAM", False),
                    ("d", "Hasło do serwera DNS", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest DNS?", "answer": "Systemem tłumaczącym nazwy domenowe na informacje potrzebne usługom."},
        {"question": "Po co używa się DNS?", "answer": "Aby korzystać z nazw, takich jak example.com, zamiast zapamiętywać adresy IP."},
        {"question": "Co oznacza rekord A?", "answer": "Adres IPv4 przypisany do nazwy."},
        {"question": "Co oznacza rekord AAAA?", "answer": "Adres IPv6 przypisany do nazwy."},
        {"question": "Co oznacza rekord CNAME?", "answer": "Alias wskazujący inną nazwę DNS."},
        {"question": "Co oznacza rekord MX?", "answer": "Serwer poczty obsługujący domenę."},
        {"question": "Co oznacza rekord TXT?", "answer": "Tekstowe dane domeny, często używane do weryfikacji i konfiguracji usług."},
        {"question": "Czy CNAME jest przekierowaniem HTTP?", "answer": "Nie. To alias DNS, a nie odpowiedź serwera WWW."},
        {"question": "Do czego służy dig?", "answer": "Do wykonywania szczegółowych zapytań DNS."},
        {"question": "Co robi dig example.com A?", "answer": "Pyta o adres IPv4 domeny example.com."},
        {"question": "Co robi dig example.com MX?", "answer": "Pyta o serwery poczty domeny example.com."},
        {"question": "Do czego służy host?", "answer": "Do szybkiego sprawdzania informacji DNS o nazwie."},
        {"question": "Do czego służy nslookup?", "answer": "Do prostego odpytywania DNS, także na wielu systemach."},
        {"question": "Do czego służy resolvectl?", "answer": "Do sprawdzania resolvera systemowego i zapytań przez ten resolver."},
        {"question": "Co pokazuje resolvectl status?", "answer": "Między innymi serwery DNS przypisane do interfejsów."},
        {"question": "Co robi resolvectl query example.com?", "answer": "Sprawdza, jak systemowy resolver rozwiązuje nazwę example.com."},
        {"question": "Czym jest resolver?", "answer": "Elementem systemu odpowiedzialnym za rozwiązywanie nazw DNS dla aplikacji."},
        {"question": "Czy DNS potwierdza, że strona WWW działa?", "answer": "Nie. DNS wskazuje adresy lub rekordy, ale nie testuje działania aplikacji."},
        {"question": "Co może oznaczać działający ping do IP i niedziałająca domena?", "answer": "Możliwy problem z DNS."},
        {"question": "Czy brak rekordu AAAA zawsze jest błędem?", "answer": "Nie, domena może działać tylko po IPv4."},
        {"question": "Co oznacza TTL w DNS?", "answer": "Czas, przez który odpowiedź DNS może być przechowywana w cache."},
        {"question": "Dlaczego warto pytać o konkretny typ rekordu?", "answer": "Bo różne rekordy mają różne role i mogą dawać inne odpowiedzi."},
        {"question": "Jaki rekord jest typowy dla weryfikacji domeny?", "answer": "TXT."},
        {"question": "Jaki rekord jest typowy dla poczty?", "answer": "MX."},
        {"question": "Od czego zacząć diagnozę DNS?", "answer": "Od sprawdzenia konkretnej nazwy, typu rekordu i konfiguracji resolvera."},
    ],
}
