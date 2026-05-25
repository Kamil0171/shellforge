NETWORK_DIAGNOSTICS = {
    "module": {
        "title": "Podstawy terminala",
        "description": "Pierwszy moduł poświęcony pracy w terminalu Linux.",
    },
    "lesson": {
        "title": "Sieć i diagnostyka: ping, curl, ss i podstawy DNS",
        "level": "Podstawowy",
        "duration": "35 min",
        "description": (
            "Poznasz podstawowe komendy do sprawdzania łączności sieciowej, testowania odpowiedzi "
            "serwera, oglądania nasłuchujących portów oraz rozumienia podstaw działania DNS."
        ),
        "theory": (
            "Podczas pracy z Linuxem bardzo często trzeba sprawdzić, czy serwer ma połączenie z siecią, "
            "czy dana domena odpowiada, czy usługa HTTP działa oraz czy aplikacja nasłuchuje na właściwym "
            "porcie. Do podstawowej diagnostyki sieci przydają się proste narzędzia terminalowe. "
            "Komenda ping pozwala sprawdzić, czy host odpowiada w sieci. curl umożliwia wysyłanie "
            "żądań HTTP i sprawdzanie odpowiedzi stron lub API. Komenda ss pokazuje aktywne połączenia "
            "sieciowe oraz porty, na których nasłuchują usługi. DNS tłumaczy nazwy domenowe, takie jak "
            "example.com, na adresy IP zrozumiałe dla komputerów. Zrozumienie tych podstaw pomaga później "
            "diagnozować problemy z Nginx, SSH, aplikacjami webowymi, domenami i certyfikatami HTTPS."
        ),
        "commands": [
            {
                "command": "ping -c 4 1.1.1.1",
                "description": "Wysyła 4 pakiety testowe do adresu IP i sprawdza, czy host odpowiada.",
                "example": "$ ping -c 4 1.1.1.1\n64 bytes from 1.1.1.1: icmp_seq=1 ttl=57 time=12.3 ms",
            },
            {
                "command": "ping -c 4 example.com",
                "description": "Sprawdza łączność z domeną i przy okazji pokazuje, czy nazwa została rozwiązana na adres IP.",
                "example": "$ ping -c 4 example.com\nPING example.com (93.184.216.34)",
            },
            {
                "command": "curl https://example.com",
                "description": "Pobiera odpowiedź HTTP z podanego adresu.",
                "example": "$ curl https://example.com",
            },
            {
                "command": "curl -I https://example.com",
                "description": "Pobiera same nagłówki odpowiedzi HTTP, bez treści strony.",
                "example": "$ curl -I https://example.com\nHTTP/2 200",
            },
            {
                "command": "curl -L https://example.com",
                "description": "Podąża za przekierowaniami HTTP, jeśli serwer je zwraca.",
                "example": "$ curl -L https://example.com",
            },
            {
                "command": "ss -tuln",
                "description": "Pokazuje porty TCP i UDP, na których system nasłuchuje, bez rozwiązywania nazw.",
                "example": "$ ss -tuln\nNetid State  Local Address:Port",
            },
            {
                "command": "ss -tn",
                "description": "Pokazuje aktywne połączenia TCP w formie numerycznej.",
                "example": "$ ss -tn",
            },
            {
                "command": "ss -tulpn",
                "description": "Pokazuje nasłuchujące porty razem z procesami, jeśli użytkownik ma odpowiednie uprawnienia.",
                "example": "$ ss -tulpn",
            },
            {
                "command": "getent hosts example.com",
                "description": "Sprawdza, na jaki adres IP system rozwiązuje podaną nazwę domenową.",
                "example": "$ getent hosts example.com\n93.184.216.34 example.com",
            },
            {
                "command": "cat /etc/resolv.conf",
                "description": "Pokazuje konfigurację resolvera DNS używaną przez system.",
                "example": "$ cat /etc/resolv.conf\nnameserver 1.1.1.1",
            },
        ],
        "practice_task": (
            "Sprawdź łączność z publicznym adresem IP komendą <code>ping -c 4 1.1.1.1</code>. "
            "Następnie sprawdź domenę przez <code>ping -c 4 example.com</code> i zwróć uwagę, czy "
            "domena została zamieniona na adres IP. Użyj <code>curl -I https://example.com</code>, "
            "aby zobaczyć nagłówki odpowiedzi HTTP. Potem sprawdź porty nasłuchujące poleceniem "
            "<code>ss -tuln</code>. Na końcu użyj <code>getent hosts example.com</code> oraz "
            "<code>cat /etc/resolv.conf</code>, żeby zobaczyć podstawowe informacje związane z DNS."
        ),
        "common_mistakes": [
            "Zakładanie, że brak odpowiedzi na ping zawsze oznacza, że serwer nie działa.",
            "Mylenie problemu z DNS z problemem samego połączenia sieciowego.",
            "Sprawdzanie domeny tylko przez przeglądarkę, bez użycia narzędzi terminalowych.",
            "Pomijanie kodów odpowiedzi HTTP zwracanych przez curl.",
            "Mylenie portu nasłuchującego z aktywnym połączeniem wychodzącym.",
            "Używanie ss bez opcji numerycznych i błędna interpretacja nazw usług.",
            "Zakładanie, że otwarty port oznacza poprawne działanie całej aplikacji.",
            "Ignorowanie pliku /etc/resolv.conf podczas diagnozowania problemów z DNS.",
        ],
        "summary": (
            "Podstawowa diagnostyka sieci w Linuxie zaczyna się od kilku prostych narzędzi. "
            "<code>ping</code> pomaga sprawdzić, czy host odpowiada w sieci. <code>curl</code> pozwala "
            "testować odpowiedzi HTTP i nagłówki serwera. <code>ss</code> pokazuje aktywne połączenia "
            "oraz porty, na których nasłuchują usługi. DNS odpowiada za tłumaczenie nazw domenowych "
            "na adresy IP, a komendy <code>getent hosts</code> i <code>cat /etc/resolv.conf</code> "
            "pomagają zobaczyć, jak system rozwiązuje nazwy domen."
        ),
    },
    "quiz": {
        "title": "Quiz: sieć i diagnostyka",
        "description": "Sprawdź, czy rozumiesz podstawy diagnostyki sieci, HTTP, portów i DNS.",
        "questions": [
            {
                "text": "Do czego służy komenda ping?",
                "answers": [
                    ("a", "Do sprawdzania, czy host odpowiada w sieci", True),
                    ("b", "Do edycji plików tekstowych", False),
                    ("c", "Do instalowania pakietów", False),
                    ("d", "Do zmiany uprawnień pliku", False),
                ],
            },
            {
                "text": "Co oznacza opcja -c 4 w komendzie ping?",
                "answers": [
                    ("a", "Wysłanie 4 pakietów testowych", True),
                    ("b", "Utworzenie 4 katalogów", False),
                    ("c", "Sprawdzenie 4 użytkowników", False),
                    ("d", "Usunięcie 4 procesów", False),
                ],
            },
            {
                "text": "Do czego służy curl?",
                "answers": [
                    ("a", "Do wysyłania żądań i sprawdzania odpowiedzi HTTP", True),
                    ("b", "Do wyświetlania procesów", False),
                    ("c", "Do tworzenia grup użytkowników", False),
                    ("d", "Do zmiany hasła", False),
                ],
            },
            {
                "text": "Co robi curl -I https://example.com?",
                "answers": [
                    ("a", "Pobiera nagłówki odpowiedzi HTTP", True),
                    ("b", "Instaluje certyfikat HTTPS", False),
                    ("c", "Usuwa stronę internetową", False),
                    ("d", "Restartuje usługę DNS", False),
                ],
            },
            {
                "text": "Co robi curl -L?",
                "answers": [
                    ("a", "Podąża za przekierowaniami HTTP", True),
                    ("b", "Pokazuje tylko lokalne pliki", False),
                    ("c", "Blokuje połączenie sieciowe", False),
                    ("d", "Tworzy nowego użytkownika", False),
                ],
            },
            {
                "text": "Do czego służy komenda ss?",
                "answers": [
                    ("a", "Do sprawdzania połączeń sieciowych i portów", True),
                    ("b", "Do kopiowania plików", False),
                    ("c", "Do edycji obrazu systemu", False),
                    ("d", "Do zmiany nazwy hosta", False),
                ],
            },
            {
                "text": "Co pokazuje ss -tuln?",
                "answers": [
                    ("a", "Porty TCP i UDP, na których system nasłuchuje", True),
                    ("b", "Tylko zawartość katalogu domowego", False),
                    ("c", "Tylko listę użytkowników", False),
                    ("d", "Tylko historię komend", False),
                ],
            },
            {
                "text": "Co oznacza DNS?",
                "answers": [
                    ("a", "Mechanizm tłumaczenia nazw domenowych na adresy IP", True),
                    ("b", "Program do usuwania pakietów", False),
                    ("c", "Typ uprawnień plików", False),
                    ("d", "Nazwa edytora tekstu", False),
                ],
            },
            {
                "text": "Do czego służy getent hosts example.com?",
                "answers": [
                    ("a", "Do sprawdzenia, na jaki adres IP system rozwiązuje domenę", True),
                    ("b", "Do restartowania serwera WWW", False),
                    ("c", "Do zmiany właściciela pliku", False),
                    ("d", "Do wyłączenia firewalla", False),
                ],
            },
            {
                "text": "Co można sprawdzić w pliku /etc/resolv.conf?",
                "answers": [
                    ("a", "Konfigurację resolvera DNS używaną przez system", True),
                    ("b", "Listę procesów systemowych", False),
                    ("c", "Hasła użytkowników w jawnej postaci", False),
                    ("d", "Historię aktualizacji pakietów", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Do czego służy ping?",
            "answer": "Do sprawdzania, czy host odpowiada w sieci.",
        },
        {
            "question": "Co robi ping -c 4 1.1.1.1?",
            "answer": "Wysyła 4 pakiety testowe do adresu 1.1.1.1.",
        },
        {
            "question": "Dlaczego warto wykonać ping do adresu IP i domeny?",
            "answer": "Adres IP pomaga sprawdzić łączność, a domena dodatkowo pokazuje, czy działa rozwiązywanie DNS.",
        },
        {
            "question": "Czy brak odpowiedzi na ping zawsze oznacza awarię serwera?",
            "answer": "Nie. Ping może być blokowany przez firewall lub konfigurację sieci.",
        },
        {
            "question": "Do czego służy curl?",
            "answer": "Do wysyłania żądań HTTP i sprawdzania odpowiedzi serwera.",
        },
        {
            "question": "Co robi curl -I?",
            "answer": "Pobiera same nagłówki odpowiedzi HTTP.",
        },
        {
            "question": "Co robi curl -L?",
            "answer": "Podąża za przekierowaniami HTTP.",
        },
        {
            "question": "Dlaczego curl jest przydatny przy aplikacji webowej?",
            "answer": "Pozwala sprawdzić, czy strona lub API odpowiada bez używania przeglądarki.",
        },
        {
            "question": "Do czego służy ss?",
            "answer": "Do sprawdzania połączeń sieciowych i portów.",
        },
        {
            "question": "Co pokazuje ss -tuln?",
            "answer": "Porty TCP i UDP, na których system nasłuchuje.",
        },
        {
            "question": "Co oznacza port nasłuchujący?",
            "answer": "Że jakaś usługa czeka na połączenia na danym porcie.",
        },
        {
            "question": "Co pokazuje ss -tn?",
            "answer": "Aktywne połączenia TCP w formie numerycznej.",
        },
        {
            "question": "Co może pokazać ss -tulpn?",
            "answer": "Porty nasłuchujące oraz procesy, które z nich korzystają.",
        },
        {
            "question": "Czym jest DNS?",
            "answer": "Mechanizmem tłumaczenia nazw domenowych na adresy IP.",
        },
        {
            "question": "Po co systemowi DNS?",
            "answer": "Żeby użytkownik mógł używać nazw domen zamiast zapamiętywać adresy IP.",
        },
        {
            "question": "Do czego służy getent hosts?",
            "answer": "Do sprawdzenia, na jaki adres IP system rozwiązuje nazwę hosta.",
        },
        {
            "question": "Co zawiera /etc/resolv.conf?",
            "answer": "Informacje o konfiguracji resolvera DNS używanego przez system.",
        },
        {
            "question": "Czym różni się problem z DNS od problemu z siecią?",
            "answer": "Przy problemie z DNS adres IP może działać, ale domena może się nie rozwiązywać.",
        },
        {
            "question": "Dlaczego otwarty port nie zawsze oznacza, że aplikacja działa poprawnie?",
            "answer": "Bo usługa może nasłuchiwać, ale zwracać błędy albo mieć błędną konfigurację.",
        },
        {
            "question": "Jak szybko sprawdzić nagłówki strony HTTPS?",
            "answer": "Komendą curl -I https://example.com.",
        },
    ],
}