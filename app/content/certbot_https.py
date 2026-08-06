CERTBOT_HTTPS = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "HTTPS z Let's Encrypt i Certbot",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": (
            "Zabezpieczysz publiczną aplikację protokołem HTTPS, uzyskasz certyfikat Let's Encrypt przez "
            "Certbota i sprawdzisz automatyczne odnawianie certyfikatu."
        ),
        "theory": (
            "HTTP przesyła dane bez ochrony zapewnianej przez szyfrowanie transportu, natomiast HTTPS to "
            "HTTP działający przez TLS. TLS szyfruje połączenie, chroni integralność przesyłanych danych i "
            "pozwala klientowi zweryfikować tożsamość serwera na podstawie certyfikatu. Certyfikat musi "
            "obejmować nazwę używaną przez przeglądarkę, na przykład <code>app.example.com</code>. Przed jego "
            "uzyskaniem rekord DNS domeny powinien wskazywać właściwy serwer, Nginx musi poprawnie obsługiwać "
            "tę nazwę na porcie 80, a firewall i ewentualny firewall dostawcy muszą przepuszczać porty 80 i "
            "443. Port 80 jest potrzebny między innymi do typowej weryfikacji domeny i przekierowania HTTP, "
            "a 443 do ruchu HTTPS. Let's Encrypt jest publicznym urzędem certyfikacji wydającym krótkotrwałe "
            "certyfikaty, a Certbot automatyzuje ich uzyskanie i odnawianie. W systemie zgodnym z RHEL, takim "
            "jak Rocky Linux, instaluje się Certbota wraz z pluginem Nginx. W typowej instalacji Rocky Linux "
            "pakiety te mogą pochodzić z repozytorium EPEL, które trzeba wcześniej włączyć, jeśli nie są "
            "dostępne w aktywnych repozytoriach. Polecenie "
            "<code>certbot --nginx</code> sprawdza domenę, pobiera certyfikat i może bezpiecznie zmodyfikować "
            "konfigurację Nginxa, w tym dodać przekierowanie z HTTP do HTTPS. Aktywne pliki są zarządzane w "
            "<code>/etc/letsencrypt/live/app.example.com/</code>; konfiguracja Nginxa odwołuje się do nich, "
            "ale nie należy ich ręcznie kopiować. Po zmianie zawsze trzeba wykonać <code>nginx -t</code>, a "
            "dopiero potem przeładować Nginxa. Certyfikaty Let's Encrypt są odnawiane okresowo. Sam fakt "
            "uzyskania pierwszego certyfikatu nie wystarcza: należy wykonać test "
            "<code>certbot renew --dry-run</code> i sprawdzić timer systemd. Przy błędzie najpierw kontroluje "
            "się DNS, dostępność portu 80, reguły firewalla, stan Nginxa oraz logi Certbota. Certyfikat "
            "samodzielnie podpisany może służyć w laboratorium, ale nie zastępuje zaufanego certyfikatu dla "
            "publicznej aplikacji."
        ),
        "commands": [
            {
                "command": "sudo dnf install epel-release",
                "description": "Włącza EPEL na Rocky Linux, jeśli pakiety Certbota nie są jeszcze dostępne.",
                "example": "$ sudo dnf install epel-release",
            },
            {
                "command": "sudo dnf install certbot python3-certbot-nginx",
                "description": "Instaluje Certbota i plugin integrujący go z Nginxem.",
                "example": "$ sudo dnf install certbot python3-certbot-nginx",
            },
            {
                "command": "sudo certbot --nginx -d app.example.com",
                "description": "Uzyskuje certyfikat dla domeny i aktualizuje konfigurację Nginxa.",
                "example": "$ sudo certbot --nginx -d app.example.com",
            },
            {
                "command": "sudo certbot renew --dry-run",
                "description": "Testuje pełny mechanizm odnowienia bez zastępowania ważnego certyfikatu.",
                "example": "$ sudo certbot renew --dry-run",
            },
            {
                "command": "systemctl list-timers | grep certbot",
                "description": "Sprawdza timer systemd odpowiedzialny za okresowe uruchamianie odnowienia.",
                "example": "$ systemctl list-timers | grep certbot",
            },
            {
                "command": "sudo nginx -t && sudo systemctl reload nginx",
                "description": "Weryfikuje składnię i przeładowuje poprawną konfigurację bez pełnego restartu.",
                "example": "$ sudo nginx -t\n$ sudo systemctl reload nginx",
            },
            {
                "command": "curl -I https://app.example.com",
                "description": "Sprawdza odpowiedź aplikacji przez publiczny adres HTTPS.",
                "example": "$ curl -I https://app.example.com\nHTTP/2 200",
            },
        ],
        "practice_task": (
            "Dla laboratoryjnej domeny <code>app.example.com</code> sprawdź rekord DNS, stan Nginxa oraz "
            "dostępność portów 80 i 443 w firewalld. Zainstaluj <code>certbot</code> i "
            "<code>python3-certbot-nginx</code>, wykonaj <code>sudo certbot --nginx -d app.example.com</code> "
            "i wybierz przekierowanie HTTP do HTTPS. Następnie uruchom <code>sudo nginx -t</code>, sprawdź "
            "domenę przez <code>curl -I</code>, wykonaj <code>sudo certbot renew --dry-run</code> i potwierdź "
            "obecność timera systemd. Jeśli nie dysponujesz publiczną domeną, opisz każdy krok, wymagania "
            "sieciowe i oczekiwane wyniki bez żądania prawdziwego certyfikatu."
        ),
        "common_mistakes": [
            "Uruchamianie Certbota, zanim DNS domeny wskazuje właściwy serwer.",
            "Blokowanie portu 80 lub 443 w firewalld albo firewallu dostawcy.",
            "Pominięcie testu nginx -t przed przeładowaniem konfiguracji.",
            "Ręczne kopiowanie plików z /etc/letsencrypt i przerywanie mechanizmu odnowienia.",
            "Założenie, że pierwszy certyfikat będzie odnawiał się bez przetestowania timera.",
            "Traktowanie certyfikatu samodzielnie podpisanego jako rozwiązania dla publicznej produkcji.",
        ],
        "summary": (
            "HTTPS wykorzystuje TLS do ochrony połączenia i potwierdzenia tożsamości serwera. Przed użyciem "
            "Certbota potrzebne są poprawny DNS, działający Nginx oraz dostępne porty 80 i 443. Plugin Nginx "
            "może uzyskać certyfikat, skonfigurować HTTPS i przekierowanie. Po wdrożeniu trzeba przetestować "
            "konfigurację, publiczny adres oraz okresowe odnawianie przez timer systemd."
        ),
    },
    "quiz": {
        "title": "Quiz: HTTPS z Let's Encrypt i Certbot",
        "description": "Sprawdź praktyczne rozumienie TLS, Certbota i odnawiania certyfikatów.",
        "questions": [
            {
                "text": "Co zapewnia TLS w połączeniu HTTPS?",
                "answers": [
                    ("a", "Szyfrowanie, integralność i weryfikację tożsamości serwera", True),
                    ("b", "Automatyczną instalację zależności Pythona", False),
                    ("c", "Zastąpienie rekordu DNS", False),
                    ("d", "Uruchomienie aplikacji jako root", False),
                ],
            },
            {
                "text": "Co należy sprawdzić przed żądaniem certyfikatu dla app.example.com?",
                "answers": [
                    ("a", "DNS, działanie Nginxa na porcie 80 i reguły firewalla", True),
                    ("b", "Wyłącznie ilość pamięci RAM", False),
                    ("c", "Czy kod aplikacji jest w /tmp", False),
                    ("d", "Czy certyfikat skopiowano ręcznie", False),
                ],
            },
            {
                "text": "Co robi plugin Certbota dla Nginxa?",
                "answers": [
                    ("a", "Pomaga uzyskać certyfikat i zmodyfikować konfigurację Nginxa", True),
                    ("b", "Tworzy rekord DNS u każdego operatora", False),
                    ("c", "Instaluje aplikację w środowisku venv", False),
                    ("d", "Zastępuje firewall", False),
                ],
            },
            {
                "text": "Po co uruchamiać certbot renew --dry-run?",
                "answers": [
                    ("a", "Aby przetestować mechanizm okresowego odnowienia", True),
                    ("b", "Aby usunąć aktywny certyfikat", False),
                    ("c", "Aby wyświetlić sekrety aplikacji", False),
                    ("d", "Aby zmienić branch Git", False),
                ],
            },
            {
                "text": "Jak postąpić z plikami w /etc/letsencrypt/live?",
                "answers": [
                    ("a", "Pozwolić Certbotowi nimi zarządzać i odwołać się do nich z Nginxa", True),
                    ("b", "Kopiować je ręcznie po każdym odnowieniu", False),
                    ("c", "Dodać je do repozytorium Git", False),
                    ("d", "Przenieść je do katalogu /tmp", False),
                ],
            },
            {
                "text": "Jaka jest właściwa kolejność po zmianie konfiguracji Nginxa?",
                "answers": [
                    ("a", "Najpierw nginx -t, potem reload Nginxa", True),
                    ("b", "Najpierw usunięcie certyfikatu, potem test DNS", False),
                    ("c", "Restart serwera bez sprawdzenia składni", False),
                    ("d", "Wyłączenie portu 443", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym różni się HTTPS od HTTP?", "answer": "HTTPS przenosi HTTP przez szyfrowane i uwierzytelniane połączenie TLS."},
        {"question": "Jaką rolę pełni TLS?", "answer": "Chroni poufność i integralność danych oraz pomaga potwierdzić tożsamość serwera."},
        {"question": "Czym jest certyfikat serwera?", "answer": "Dokumentem cyfrowym łączącym nazwę domeny z kluczem publicznym serwera."},
        {"question": "Czym jest Let's Encrypt?", "answer": "Publicznym urzędem certyfikacji wydającym bezpłatne, krótkotrwałe certyfikaty TLS."},
        {"question": "Czym jest Certbot?", "answer": "Klientem automatyzującym uzyskiwanie i odnawianie certyfikatów."},
        {"question": "Po co plugin python3-certbot-nginx?", "answer": "Integruje Certbota z konfiguracją i weryfikacją Nginxa."},
        {"question": "Co musi wskazywać DNS przed wydaniem certyfikatu?", "answer": "Domena musi kierować na publiczny adres serwera obsługującego żądanie."},
        {"question": "Dlaczego potrzebny jest port 80?", "answer": "Służy typowej weryfikacji HTTP i obsłudze przekierowania do HTTPS."},
        {"question": "Do czego służy port 443?", "answer": "Do przyjmowania publicznych połączeń HTTPS."},
        {"question": "Co może blokować walidację domeny?", "answer": "Błędny DNS, niedziałający Nginx lub firewall blokujący port 80."},
        {"question": "Co robi certbot --nginx -d?", "answer": "Żąda certyfikatu dla domeny i integruje go z Nginxem."},
        {"question": "Po co przekierować HTTP do HTTPS?", "answer": "Aby klienci używający HTTP trafiali na chronioną wersję usługi."},
        {"question": "Gdzie Certbot zarządza aktywnymi certyfikatami?", "answer": "W strukturze /etc/letsencrypt, między innymi w katalogu live dla domeny."},
        {"question": "Czy należy ręcznie kopiować certyfikaty?", "answer": "Nie, utrudnia to bezpieczne automatyczne odnawianie."},
        {"question": "Co sprawdza nginx -t?", "answer": "Składnię i podstawową poprawność konfiguracji Nginxa."},
        {"question": "Kiedy przeładować Nginxa?", "answer": "Po pozytywnym teście konfiguracji."},
        {"question": "Dlaczego certyfikaty trzeba odnawiać?", "answer": "Mają ograniczony okres ważności i po jego upływie klienci je odrzucą."},
        {"question": "Co robi renew --dry-run?", "answer": "Symuluje odnowienie i sprawdza, czy mechanizm działa."},
        {"question": "Jak sprawdzić timer Certbota?", "answer": "Poleceniem systemctl list-timers, filtrując wynik po nazwie certbot."},
        {"question": "Jak sprawdzić publiczny HTTPS?", "answer": "Na przykład poleceniem curl -I https://app.example.com."},
        {"question": "Co sprawdzić przy błędzie Certbota?", "answer": "DNS, port 80, firewall, stan Nginxa i logi Certbota."},
        {"question": "Czy certyfikat samodzielnie podpisany nadaje się do publicznej produkcji?", "answer": "Nie jako typowe zaufane rozwiązanie dla użytkowników publicznej aplikacji."},
        {"question": "Czy DNS sam włącza HTTPS?", "answer": "Nie, potrzebne są certyfikat i konfiguracja serwera webowego."},
        {"question": "Czy firewall musi przepuszczać HTTPS?", "answer": "Tak, port 443 musi być dostępny z wymaganej sieci."},
        {"question": "Jaki jest cel automatycznego odnawiania?", "answer": "Utrzymanie ważnego certyfikatu bez ręcznej wymiany przed każdym wygaśnięciem."},
    ],
}
