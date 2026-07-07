TLS_HTTPS_BASICS = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "Podstawy TLS i HTTPS",
        "level": "Podstawowy+",
        "duration": "50 min",
        "description": (
            "Poznasz rolę TLS i HTTPS, podstawowe elementy certyfikatu oraz proste komendy do sprawdzania "
            "bezpiecznego połączenia ze stroną."
        ),
        "theory": (
            "HTTP przesyła żądania i odpowiedzi bez własnej warstwy szyfrowania. HTTPS to HTTP używane przez "
            "połączenie chronione TLS. TLS zapewnia poufność, integralność i uwierzytelnienie serwera, dzięki "
            "czemu użytkownik może sprawdzić, czy łączy się z właściwą stroną i czy dane nie są łatwo czytane "
            "po drodze. Certyfikat serwera zawiera między innymi nazwę domeny, okres ważności, klucz publiczny "
            "i informację o wystawcy. Klucz prywatny odpowiadający certyfikatowi zostaje na serwerze i musi być "
            "chroniony. CA, czyli urząd certyfikacji, podpisuje certyfikat lub pośredni certyfikat w łańcuchu "
            "zaufania. Przeglądarka i narzędzia systemowe sprawdzają, czy certyfikat pasuje do domeny, czy nie "
            "wygasł i czy prowadzi do zaufanego CA. Do podstawowej diagnostyki wystarczy <code>curl -I</code>, "
            "który pokaże nagłówki odpowiedzi HTTPS, oraz <code>openssl s_client</code>, który pozwala obejrzeć "
            "szczegóły połączenia TLS i łańcucha certyfikatów. Certyfikat nie naprawia błędów aplikacji, ale jest "
            "niezbędną warstwą bezpiecznej komunikacji w publicznym internecie."
        ),
        "commands": [
            {
                "command": "curl -I https://example.com",
                "description": "Pobiera nagłówki odpowiedzi HTTPS bez treści strony.",
                "example": "$ curl -I https://example.com",
            },
            {
                "command": "curl -Iv https://example.com",
                "description": "Pokazuje bardziej szczegółowy przebieg połączenia, w tym informacje TLS.",
                "example": "$ curl -Iv https://example.com",
            },
            {
                "command": "openssl s_client -connect example.com:443 -servername example.com",
                "description": "Nawiązuje połączenie TLS i pokazuje informacje o certyfikacie serwera.",
                "example": "$ openssl s_client -connect example.com:443 -servername example.com",
            },
            {
                "command": "openssl s_client -connect example.com:443 -servername example.com -showcerts",
                "description": "Pokazuje certyfikaty przesłane przez serwer w trakcie połączenia TLS.",
                "example": "$ openssl s_client -connect example.com:443 -servername example.com -showcerts",
            },
            {
                "command": "echo | openssl s_client -connect example.com:443 -servername example.com",
                "description": "Wykonuje szybki test połączenia TLS bez ręcznego kończenia sesji.",
                "example": "$ echo | openssl s_client -connect example.com:443 -servername example.com",
            },
            {
                "command": "curl -I http://example.com",
                "description": "Pozwala porównać odpowiedź HTTP z odpowiedzią HTTPS, jeśli serwer obsługuje oba warianty.",
                "example": "$ curl -I http://example.com",
            },
        ],
        "practice_task": (
            "Porównaj odpowiedzi <code>curl -I http://example.com</code> i "
            "<code>curl -I https://example.com</code>. Zwróć uwagę na kod odpowiedzi, ewentualne przekierowanie "
            "oraz użyty schemat adresu. Następnie uruchom "
            "<code>openssl s_client -connect example.com:443 -servername example.com</code> i odszukaj informacje "
            "o certyfikacie, nazwie serwera oraz wyniku weryfikacji. Na końcu zapisz własnymi słowami, czym różni "
            "się certyfikat od klucza prywatnego i dlaczego klucza prywatnego nie wolno udostępniać."
        ),
        "common_mistakes": [
            "Mylenie HTTPS z samym przekierowaniem HTTP.",
            "Traktowanie certyfikatu jako sekretu, a klucza prywatnego jako pliku publicznego.",
            "Ignorowanie daty ważności certyfikatu.",
            "Pomijanie zgodności nazwy domeny z certyfikatem.",
            "Zakładanie, że poprawny certyfikat oznacza brak błędów w aplikacji.",
            "Uruchamianie openssl s_client bez parametru -servername przy domenach korzystających z SNI.",
        ],
        "summary": (
            "HTTPS to HTTP chronione przez TLS. Certyfikat pomaga potwierdzić tożsamość serwera, klucz prywatny "
            "musi pozostać tajny, a CA buduje łańcuch zaufania. <code>curl -I</code> pozwala szybko sprawdzić "
            "odpowiedź HTTPS, a <code>openssl s_client</code> pokazuje szczegóły połączenia TLS i certyfikatów. "
            "Poprawny TLS jest podstawą bezpiecznej komunikacji, ale nie zastępuje poprawnej konfiguracji aplikacji."
        ),
    },
    "quiz": {
        "title": "Quiz: podstawy TLS i HTTPS",
        "description": "Sprawdź, czy rozumiesz różnicę między HTTP, HTTPS, certyfikatem i kluczem prywatnym.",
        "questions": [
            {
                "text": "Czym jest HTTPS?",
                "answers": [
                    ("a", "HTTP używany przez połączenie chronione TLS", True),
                    ("b", "Nową nazwą dla DNS", False),
                    ("c", "Trybem pracy SELinux", False),
                    ("d", "Typem konta użytkownika", False),
                ],
            },
            {
                "text": "Co powinno pozostać tajne na serwerze?",
                "answers": [
                    ("a", "Klucz prywatny certyfikatu", True),
                    ("b", "Publiczny certyfikat serwera", False),
                    ("c", "Kod odpowiedzi HTTP", False),
                    ("d", "Nazwa domeny", False),
                ],
            },
            {
                "text": "Jaką rolę pełni CA?",
                "answers": [
                    ("a", "Wystawia lub poświadcza certyfikaty w łańcuchu zaufania", True),
                    ("b", "Restartuje usługę sshd", False),
                    ("c", "Dodaje reguły firewalld", False),
                    ("d", "Zastępuje routing", False),
                ],
            },
            {
                "text": "Co robi curl -I https://example.com?",
                "answers": [
                    ("a", "Pobiera nagłówki odpowiedzi HTTPS", True),
                    ("b", "Generuje nowy klucz prywatny", False),
                    ("c", "Zmienia kontekst SELinux", False),
                    ("d", "Wyświetla tablicę routingu", False),
                ],
            },
            {
                "text": "Do czego służy openssl s_client?",
                "answers": [
                    ("a", "Do testowania połączenia TLS i oglądania informacji o certyfikacie", True),
                    ("b", "Do edycji authorized_keys", False),
                    ("c", "Do zmiany strefy firewalld", False),
                    ("d", "Do sprawdzania zużycia dysku", False),
                ],
            },
            {
                "text": "Dlaczego certyfikaty są ważne?",
                "answers": [
                    ("a", "Pomagają potwierdzić tożsamość serwera i szyfrować komunikację przez TLS", True),
                    ("b", "Gwarantują brak błędów w kodzie aplikacji", False),
                    ("c", "Zawsze otwierają porty w firewallu", False),
                    ("d", "Automatycznie tworzą użytkownika deploy", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest HTTP?", "answer": "Protokołem wymiany żądań i odpowiedzi używanym przez strony i API."},
        {"question": "Czym jest HTTPS?", "answer": "HTTP przesyłanym przez połączenie zabezpieczone TLS."},
        {"question": "Czym jest TLS?", "answer": "Protokołem zapewniającym szyfrowanie, integralność i uwierzytelnienie połączenia."},
        {"question": "Co daje szyfrowanie TLS?", "answer": "Utrudnia odczytanie danych po drodze między klientem i serwerem."},
        {"question": "Co oznacza integralność w TLS?", "answer": "Pomaga wykryć modyfikację danych w trakcie przesyłania."},
        {"question": "Co oznacza uwierzytelnienie serwera?", "answer": "Klient może sprawdzić, czy certyfikat pasuje do oczekiwanej domeny."},
        {"question": "Czym jest certyfikat serwera?", "answer": "Publicznym dokumentem kryptograficznym opisującym między innymi domenę i klucz publiczny."},
        {"question": "Czym jest klucz prywatny certyfikatu?", "answer": "Sekretnym kluczem na serwerze odpowiadającym certyfikatowi."},
        {"question": "Czy certyfikat publiczny jest sekretem?", "answer": "Nie, sekret stanowi klucz prywatny."},
        {"question": "Czym jest CA?", "answer": "Urzędem certyfikacji poświadczającym certyfikaty."},
        {"question": "Czym jest łańcuch zaufania?", "answer": "Powiązaniem certyfikatów od serwera do zaufanego CA."},
        {"question": "Co sprawdza klient HTTPS?", "answer": "Między innymi nazwę domeny, ważność certyfikatu i zaufanie do CA."},
        {"question": "Co oznacza wygaśnięty certyfikat?", "answer": "Certyfikat jest poza okresem ważności i klient może go odrzucić."},
        {"question": "Co oznacza niezgodność nazwy domeny?", "answer": "Certyfikat nie pasuje do adresu, z którym łączy się klient."},
        {"question": "Do czego służy curl -I?", "answer": "Do pobierania samych nagłówków odpowiedzi HTTP lub HTTPS."},
        {"question": "Co może pokazać curl -Iv?", "answer": "Szczegóły połączenia, w tym informacje TLS."},
        {"question": "Do czego służy openssl s_client?", "answer": "Do ręcznego testowania połączenia TLS z serwerem."},
        {"question": "Po co parametr -servername w openssl s_client?", "answer": "Przekazuje nazwę domeny przez SNI, aby serwer wybrał właściwy certyfikat."},
        {"question": "Jaki port zwykle obsługuje HTTPS?", "answer": "443/tcp."},
        {"question": "Jaki port zwykle obsługuje HTTP?", "answer": "80/tcp."},
        {"question": "Czy HTTPS oznacza, że aplikacja nie ma błędów?", "answer": "Nie, HTTPS zabezpiecza transport, ale nie naprawia aplikacji."},
        {"question": "Czy certyfikat otwiera port w firewallu?", "answer": "Nie, firewall konfiguruje się osobno."},
        {"question": "Co porównać przy HTTP i HTTPS?", "answer": "Kod odpowiedzi, nagłówki, przekierowania i schemat adresu."},
        {"question": "Dlaczego chronić klucz prywatny?", "answer": "Bo jego wyciek może pozwolić podszyć się pod serwer."},
        {"question": "Jaki jest prosty test HTTPS?", "answer": "curl -I https://example.com oraz openssl s_client -connect example.com:443 -servername example.com."},
    ],
}
