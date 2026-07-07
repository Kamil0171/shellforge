NETWORK_DNS_ROUTING_CONNECTIONS = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "Diagnostyka DNS, routingu i połączeń",
        "level": "Podstawowy+",
        "duration": "55 min",
        "description": (
            "Poznasz prostą kolejność diagnozy problemów sieciowych: trasa, DNS, połączenie, firewall "
            "i nasłuchiwanie usługi."
        ),
        "theory": (
            "Przy problemach sieciowych łatwo skupić się na pierwszym komunikacie błędu, ale lepsze efekty daje "
            "spokojna diagnoza warstwami. Najpierw warto sprawdzić routing, czyli którędy system wysyła ruch. "
            "<code>ip route</code> pokazuje między innymi trasę domyślną i bramę, przez którą wychodzi ruch poza "
            "lokalną sieć. <code>ping</code> pomaga sprawdzić podstawową osiągalność adresu IP, choć brak odpowiedzi "
            "nie zawsze oznacza awarię, bo ICMP może być blokowany. <code>tracepath</code> albo "
            "<code>traceroute</code> pokazuje kolejne przeskoki na trasie do celu. DNS diagnozuje się oddzielnie: "
            "jeśli adres IP odpowiada, ale nazwa domenowa nie, problem może dotyczyć resolvera lub rekordów DNS. "
            "<code>dig</code> pokazuje odpowiedzi DNS, a <code>resolvectl</code> konfigurację resolvera systemowego. "
            "Gdy trasa i DNS wyglądają dobrze, trzeba sprawdzić, czy usługa nasłuchuje i czy port jest dostępny. "
            "<code>ss</code> pokazuje lokalne porty i połączenia. Typowe przyczyny problemów to błąd DNS, brak trasy "
            "domyślnej, blokada firewalla, usługa nasłuchująca tylko lokalnie albo usługa, która w ogóle nie działa."
        ),
        "commands": [
            {
                "command": "ip route",
                "description": "Pokazuje tablicę routingu, w tym trasę domyślną.",
                "example": "$ ip route",
            },
            {
                "command": "ping -c 4 1.1.1.1",
                "description": "Sprawdza podstawową osiągalność publicznego adresu IP.",
                "example": "$ ping -c 4 1.1.1.1",
            },
            {
                "command": "tracepath example.com",
                "description": "Pokazuje trasę pakietów do wskazanej nazwy lub adresu.",
                "example": "$ tracepath example.com",
            },
            {
                "command": "dig example.com A",
                "description": "Sprawdza rekord A domeny, czyli adres IPv4.",
                "example": "$ dig example.com A",
            },
            {
                "command": "resolvectl status",
                "description": "Pokazuje konfigurację resolvera DNS używanego przez system.",
                "example": "$ resolvectl status",
            },
            {
                "command": "ss -tuln",
                "description": "Pokazuje lokalne porty TCP i UDP, na których system nasłuchuje.",
                "example": "$ ss -tuln",
            },
        ],
        "practice_task": (
            "Wykonaj <code>ip route</code> i znajdź trasę zaczynającą się od <code>default</code>. Następnie "
            "sprawdź połączenie z adresem IP przez <code>ping -c 4 1.1.1.1</code> oraz trasę do domeny przez "
            "<code>tracepath example.com</code> albo <code>traceroute example.com</code>, jeśli masz to narzędzie. "
            "Potem porównaj wynik <code>dig example.com A</code> i <code>resolvectl status</code>. Na końcu "
            "uruchom <code>ss -tuln</code> i zapisz, które lokalne usługi nasłuchują. Spróbuj przypisać każdy "
            "problem do jednej kategorii: DNS, routing, firewall albo usługa nie nasłuchuje."
        ),
        "common_mistakes": [
            "Zakładanie, że każdy problem z domeną jest problemem aplikacji.",
            "Diagnozowanie DNS bez porównania testu do adresu IP.",
            "Pomijanie trasy domyślnej w ip route.",
            "Traktowanie braku odpowiedzi ping jako jednoznacznego dowodu awarii hosta.",
            "Sprawdzanie firewalla przed potwierdzeniem, że usługa naprawdę nasłuchuje.",
            "Mylenie problemu lokalnego resolvera z problemem publicznych rekordów DNS.",
        ],
        "summary": (
            "Praktyczna diagnoza sieci polega na sprawdzaniu kolejnych warstw: routing przez "
            "<code>ip route</code>, podstawową osiągalność przez <code>ping</code>, trasę przez "
            "<code>tracepath</code> lub <code>traceroute</code>, DNS przez <code>dig</code> i "
            "<code>resolvectl</code>, a nasłuchiwanie usług przez <code>ss</code>. Taka kolejność pomaga "
            "odróżnić problem z DNS, trasą, firewallem i samą usługą."
        ),
    },
    "quiz": {
        "title": "Quiz: diagnostyka DNS, routingu i połączeń",
        "description": "Sprawdź, czy umiesz rozdzielić problemy DNS, routingu, firewalla i usług.",
        "questions": [
            {
                "text": "Co pokazuje ip route?",
                "answers": [
                    ("a", "Tablicę routingu, w tym trasę domyślną", True),
                    ("b", "Klucze SSH użytkownika", False),
                    ("c", "Certyfikat TLS strony", False),
                    ("d", "Listę pytań quizu", False),
                ],
            },
            {
                "text": "Co może sugerować sytuacja: ping do IP działa, ale domena nie działa?",
                "answers": [
                    ("a", "Problem z DNS lub resolverem", True),
                    ("b", "Zawsze uszkodzony dysk", False),
                    ("c", "Zawsze błędny chmod", False),
                    ("d", "Wyłącznie problem z kluczem SSH", False),
                ],
            },
            {
                "text": "Do czego służy tracepath albo traceroute?",
                "answers": [
                    ("a", "Do pokazania kolejnych przeskoków na trasie do celu", True),
                    ("b", "Do edycji sshd_config", False),
                    ("c", "Do dopisania klucza publicznego", False),
                    ("d", "Do przywracania kontekstów SELinux", False),
                ],
            },
            {
                "text": "Która komenda sprawdza rekord A domeny example.com?",
                "answers": [
                    ("a", "dig example.com A", True),
                    ("b", "ss -tuln example.com", False),
                    ("c", "chmod example.com A", False),
                    ("d", "restorecon example.com", False),
                ],
            },
            {
                "text": "Co pokazuje ss -tuln?",
                "answers": [
                    ("a", "Lokalne porty TCP i UDP, na których system nasłuchuje", True),
                    ("b", "Trasę DNS", False),
                    ("c", "Hasła użytkowników", False),
                    ("d", "Zawartość certyfikatu CA", False),
                ],
            },
            {
                "text": "Co sprawdzić, gdy usługa nie odpowiada z zewnątrz?",
                "answers": [
                    ("a", "Czy nasłuchuje, czy firewall dopuszcza ruch i czy trasa działa", True),
                    ("b", "Tylko kolor terminala", False),
                    ("c", "Wyłącznie rozmiar katalogu domowego", False),
                    ("d", "Tylko nazwę użytkownika lokalnego", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Co pokazuje ip route?", "answer": "Tablicę routingu systemu."},
        {"question": "Czym jest trasa domyślna?", "answer": "Trasą używaną, gdy nie ma bardziej szczegółowej trasy do celu."},
        {"question": "Czym jest brama domyślna?", "answer": "Routerem, przez który host wysyła ruch poza lokalną sieć."},
        {"question": "Co robi ping?", "answer": "Sprawdza podstawową osiągalność hosta przez ICMP."},
        {"question": "Czy brak ping zawsze oznacza awarię?", "answer": "Nie, ICMP może być blokowany."},
        {"question": "Po co testować adres IP i domenę osobno?", "answer": "Aby oddzielić problem z łącznością od problemu DNS."},
        {"question": "Co robi tracepath?", "answer": "Pokazuje kolejne przeskoki na trasie do celu."},
        {"question": "Co robi traceroute?", "answer": "Również pokazuje trasę pakietów, jeśli narzędzie jest dostępne."},
        {"question": "Do czego służy dig?", "answer": "Do wykonywania zapytań DNS."},
        {"question": "Co robi dig example.com A?", "answer": "Pyta o adres IPv4 domeny example.com."},
        {"question": "Do czego służy resolvectl status?", "answer": "Do sprawdzania konfiguracji resolvera DNS."},
        {"question": "Czym jest resolver?", "answer": "Elementem systemu odpowiedzialnym za rozwiązywanie nazw DNS."},
        {"question": "Co może oznaczać działający IP i niedziałająca nazwa?", "answer": "Problem z DNS."},
        {"question": "Co może oznaczać brak trasy domyślnej?", "answer": "Host może nie wiedzieć, jak wysłać ruch poza lokalną sieć."},
        {"question": "Co pokazuje ss -tuln?", "answer": "Nasłuchujące porty TCP i UDP."},
        {"question": "Co oznacza usługa nie nasłuchuje?", "answer": "Proces nie czeka na połączenia na oczekiwanym porcie."},
        {"question": "Czy firewall może blokować działającą usługę?", "answer": "Tak, usługa może działać lokalnie i być niedostępna z sieci."},
        {"question": "Jaki jest dobry pierwszy krok diagnozy sieci?", "answer": "Sprawdzenie ip route i podstawowej łączności."},
        {"question": "Kiedy podejrzewać firewall?", "answer": "Gdy usługa nasłuchuje, ale ruch z zewnątrz nie dociera."},
        {"question": "Kiedy podejrzewać usługę?", "answer": "Gdy port nie nasłuchuje albo aplikacja zwraca błąd."},
        {"question": "Kiedy podejrzewać DNS?", "answer": "Gdy nazwa się nie rozwiązuje albo wskazuje zły adres."},
        {"question": "Co oznacza default w ip route?", "answer": "Domyślną trasę dla ruchu do nieznanych sieci."},
        {"question": "Dlaczego diagnozować warstwami?", "answer": "Bo pozwala szybciej znaleźć kategorię problemu."},
        {"question": "Czy jedna komenda wystarczy do pełnej diagnozy?", "answer": "Nie, zwykle trzeba porównać kilka wyników."},
        {"question": "Jaki jest praktyczny schemat diagnozy?", "answer": "Routing, ping, trasa, DNS, nasłuchiwanie i firewall."},
    ],
}
