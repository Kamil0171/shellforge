NETWORK_PORTS_SERVICES = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "Porty i usługi sieciowe",
        "level": "Podstawowy+",
        "duration": "45 min",
        "description": (
            "Poznasz rolę portów, podstawową różnicę między TCP i UDP oraz komendy do sprawdzania, "
            "które usługi nasłuchują w systemie."
        ),
        "theory": (
            "Adres IP wskazuje hosta, a port wskazuje konkretną usługę na tym hoście. Dzięki temu jeden "
            "serwer może jednocześnie obsługiwać SSH, DNS i stronę WWW. Port 22 jest typowo używany przez "
            "SSH, 53 przez DNS, 80 przez HTTP, a 443 przez HTTPS. TCP to protokół połączeniowy, który "
            "sprawdza dostarczenie danych i jest używany między innymi przez SSH oraz HTTPS. UDP jest "
            "prostszy i bezpołączeniowy, często używany tam, gdzie liczy się szybkość lub krótkie zapytania, "
            "na przykład w DNS. Port nasłuchujący oznacza, że proces czeka na połączenia lub datagramy. "
            "Nie oznacza jednak automatycznie, że cała aplikacja działa poprawnie. Komenda <code>ss</code> "
            "pokazuje gniazda sieciowe, <code>lsof</code> pomaga powiązać port z procesem, a "
            "<code>nc</code> pozwala wykonać prosty test połączenia. W praktyce diagnozę zaczyna się od "
            "pytania: czy usługa działa, czy nasłuchuje na właściwym adresie i porcie, czy firewall nie "
            "blokuje ruchu oraz czy aplikacja odpowiada zgodnie z oczekiwaniem."
        ),
        "commands": [
            {
                "command": "ss -tuln",
                "description": "Pokazuje nasłuchujące porty TCP i UDP w formie numerycznej.",
                "example": "$ ss -tuln",
            },
            {
                "command": "ss -tulpn",
                "description": "Pokazuje porty wraz z procesami, jeśli użytkownik ma odpowiednie uprawnienia.",
                "example": "$ sudo ss -tulpn",
            },
            {
                "command": "ss -tn",
                "description": "Pokazuje aktywne połączenia TCP.",
                "example": "$ ss -tn",
            },
            {
                "command": "sudo lsof -iTCP -sTCP:LISTEN -P -n",
                "description": "Wyświetla procesy nasłuchujące na portach TCP bez zamiany numerów na nazwy.",
                "example": "$ sudo lsof -iTCP -sTCP:LISTEN -P -n",
            },
            {
                "command": "nc -vz example.com 443",
                "description": "Sprawdza, czy można nawiązać połączenie TCP z portem 443.",
                "example": "$ nc -vz example.com 443",
            },
            {
                "command": "nc -vzu 1.1.1.1 53",
                "description": "Wykonuje podstawowy test UDP portu 53, którego wynik wymaga ostrożnej interpretacji.",
                "example": "$ nc -vzu 1.1.1.1 53",
            },
        ],
        "practice_task": (
            "Wykonaj <code>ss -tuln</code> i odszukaj lokalne porty nasłuchujące. Jeśli masz uprawnienia, "
            "uruchom <code>sudo ss -tulpn</code> oraz <code>sudo lsof -iTCP -sTCP:LISTEN -P -n</code>, "
            "aby powiązać porty z procesami. Następnie sprawdź zdalny port HTTPS przez "
            "<code>nc -vz example.com 443</code>. Zapisz, czym różni się port nasłuchujący lokalnie od "
            "testu połączenia do portu na zdalnym serwerze."
        ),
        "common_mistakes": [
            "Mylenie adresu IP z portem usługi.",
            "Zakładanie, że otwarty port oznacza poprawną odpowiedź aplikacji.",
            "Pomijanie różnicy między TCP i UDP podczas diagnozy.",
            "Używanie ss bez opcji -n i mylenie nazw usług z numerami portów.",
            "Sprawdzanie tylko firewalla bez potwierdzenia, że proces naprawdę nasłuchuje.",
            "Nadmierne zaufanie do testów UDP, które nie zawsze dają jednoznaczną odpowiedź.",
        ],
        "summary": (
            "Port wskazuje usługę na hoście. SSH zwykle używa portu <code>22</code>, DNS "
            "<code>53</code>, HTTP <code>80</code>, a HTTPS <code>443</code>. TCP jest połączeniowy, "
            "UDP bezpołączeniowy. <code>ss</code>, <code>lsof</code> i <code>nc</code> pomagają "
            "sprawdzić nasłuchiwanie, procesy i podstawową dostępność portów."
        ),
    },
    "quiz": {
        "title": "Quiz: porty i usługi sieciowe",
        "description": "Sprawdź, czy rozumiesz porty, TCP, UDP i podstawowe narzędzia diagnostyczne.",
        "questions": [
            {
                "text": "Co wskazuje port w połączeniu sieciowym?",
                "answers": [
                    ("a", "Konkretną usługę na hoście", True),
                    ("b", "Rozmiar dysku", False),
                    ("c", "Nazwę użytkownika", False),
                    ("d", "Poziom uprawnień pliku", False),
                ],
            },
            {
                "text": "Który port jest typowo używany przez SSH?",
                "answers": [
                    ("a", "22", True),
                    ("b", "53", False),
                    ("c", "80", False),
                    ("d", "443", False),
                ],
            },
            {
                "text": "Który port jest typowo używany przez HTTPS?",
                "answers": [
                    ("a", "443", True),
                    ("b", "22", False),
                    ("c", "25", False),
                    ("d", "110", False),
                ],
            },
            {
                "text": "Jaka jest podstawowa cecha TCP?",
                "answers": [
                    ("a", "Jest protokołem połączeniowym", True),
                    ("b", "Służy wyłącznie do logów systemowych", False),
                    ("c", "Zastępuje adres IP", False),
                    ("d", "Działa tylko lokalnie", False),
                ],
            },
            {
                "text": "Co pokazuje ss -tuln?",
                "answers": [
                    ("a", "Nasłuchujące porty TCP i UDP", True),
                    ("b", "Listę kont użytkowników", False),
                    ("c", "Tylko błędy SELinux", False),
                    ("d", "Zawartość katalogu /tmp", False),
                ],
            },
            {
                "text": "Do czego przydaje się nc -vz example.com 443?",
                "answers": [
                    ("a", "Do prostego testu połączenia TCP z portem 443", True),
                    ("b", "Do zmiany hasła SSH", False),
                    ("c", "Do wyłączenia firewalla", False),
                    ("d", "Do utworzenia rekordu DNS", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest port?", "answer": "Numerem wskazującym konkretną usługę na hoście."},
        {"question": "Po co hostowi porty?", "answer": "Aby wiele usług mogło działać pod jednym adresem IP."},
        {"question": "Jaki port zwykle ma SSH?", "answer": "22."},
        {"question": "Jaki port zwykle ma DNS?", "answer": "53."},
        {"question": "Jaki port zwykle ma HTTP?", "answer": "80."},
        {"question": "Jaki port zwykle ma HTTPS?", "answer": "443."},
        {"question": "Czym jest TCP?", "answer": "Połączeniowym protokołem transportowym."},
        {"question": "Czym jest UDP?", "answer": "Bezpołączeniowym protokołem transportowym."},
        {"question": "Który protokół jest typowy dla SSH?", "answer": "TCP."},
        {"question": "Który protokół jest często używany przez DNS?", "answer": "UDP, choć DNS może używać także TCP."},
        {"question": "Co oznacza port nasłuchujący?", "answer": "Proces czeka na ruch przychodzący na danym porcie."},
        {"question": "Czy otwarty port gwarantuje działanie aplikacji?", "answer": "Nie, aplikacja może nasłuchiwać, ale odpowiadać błędnie."},
        {"question": "Co pokazuje ss?", "answer": "Gniazda sieciowe, połączenia i porty."},
        {"question": "Co oznacza -t w ss?", "answer": "Pokazanie TCP."},
        {"question": "Co oznacza -u w ss?", "answer": "Pokazanie UDP."},
        {"question": "Co oznacza -l w ss?", "answer": "Pokazanie portów nasłuchujących."},
        {"question": "Co oznacza -n w ss?", "answer": "Pokazanie wartości numerycznych bez rozwiązywania nazw."},
        {"question": "Co oznacza -p w ss?", "answer": "Pokazanie procesu używającego gniazda, jeśli są uprawnienia."},
        {"question": "Do czego służy lsof przy sieci?", "answer": "Do powiązania portu z procesem i plikiem gniazda."},
        {"question": "Po co używać opcji -P -n w lsof?", "answer": "Aby nie zamieniać portów i adresów na nazwy."},
        {"question": "Do czego służy nc?", "answer": "Do prostych testów połączeń i pracy z portami."},
        {"question": "Co robi nc -vz host 443?", "answer": "Sprawdza możliwość połączenia TCP z portem 443."},
        {"question": "Dlaczego UDP trudniej testować niż TCP?", "answer": "Bo brak połączenia i odpowiedzi nie zawsze jednoznacznie oznacza blokadę."},
        {"question": "Co sprawdzić, gdy port nie odpowiada?", "answer": "Proces, nasłuchiwanie, firewall, adres i trasę sieciową."},
        {"question": "Jaki jest dobry pierwszy test lokalnych usług?", "answer": "ss -tuln."},
    ],
}
