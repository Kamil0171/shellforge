SELINUX_TROUBLESHOOTING = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "SELinux — diagnostyka problemów",
        "level": "Podstawowy+",
        "duration": "55 min",
        "description": (
            "Nauczysz się rozpoznawać sytuacje, w których problem może dotyczyć SELinux, sprawdzać logi audytu "
            "oraz korygować podstawowe konteksty plików."
        ),
        "theory": (
            "SELinux często ujawnia się wtedy, gdy klasyczne uprawnienia wyglądają poprawnie, usługa działa, "
            "ale aplikacja nadal nie może odczytać pliku, zapisać danych albo połączyć się z zasobem. Pierwszym "
            "krokiem nie powinno być wyłączenie SELinux, tylko sprawdzenie trybu pracy przez <code>getenforce</code> "
            "i <code>sestatus</code>. Następnie warto obejrzeć konteksty plików przez <code>ls -Z</code>. Jeśli "
            "plik został skopiowany w nietypowy sposób albo utworzony w innym katalogu, może mieć kontekst "
            "niezgodny z oczekiwaniami usługi. Polecenie <code>restorecon</code> przywraca domyślne konteksty "
            "zgodne z polityką dla danej ścieżki. Logi audytu można przeszukiwać narzędziem <code>ausearch</code>, "
            "na przykład pod kątem odmów dostępu oznaczonych jako AVC. Na tym poziomie wystarczy umieć zebrać "
            "sygnały: tryb SELinux, kontekst procesu i pliku oraz wpis audytu. <code>semanage fcontext</code> "
            "to narzędzie do definiowania trwałych reguł etykietowania ścieżek, ale przed użyciem trzeba rozumieć, "
            "jaki typ kontekstu jest właściwy dla danej usługi."
        ),
        "commands": [
            {
                "command": "getenforce",
                "description": "Pokazuje bieżący tryb SELinux.",
                "example": "$ getenforce",
            },
            {
                "command": "sestatus",
                "description": "Wyświetla szczegółowy status SELinux.",
                "example": "$ sestatus",
            },
            {
                "command": "ls -Z /var/www/html",
                "description": "Pokazuje konteksty SELinux plików w katalogu.",
                "example": "$ ls -Z /var/www/html",
            },
            {
                "command": "sudo restorecon -Rv /var/www/html",
                "description": "Przywraca domyślne konteksty SELinux dla wskazanej ścieżki.",
                "example": "$ sudo restorecon -Rv /var/www/html",
            },
            {
                "command": "sudo ausearch -m AVC -ts recent",
                "description": "Szuka niedawnych odmów SELinux typu AVC w logach audytu.",
                "example": "$ sudo ausearch -m AVC -ts recent",
            },
            {
                "command": "sudo semanage fcontext -l",
                "description": "Wyświetla reguły etykietowania kontekstów plików.",
                "example": "$ sudo semanage fcontext -l",
            },
        ],
        "practice_task": (
            "Na maszynie z SELinux wykonaj <code>getenforce</code> i <code>sestatus</code>. Następnie sprawdź "
            "konteksty przykładowego katalogu przez <code>ls -Z /var/www/html</code> albo innej ścieżki dostępnej "
            "w labie. Jeśli pracujesz na środowisku testowym, uruchom <code>sudo restorecon -Rv /var/www/html</code> "
            "i porównaj wynik przed oraz po. Na końcu sprawdź ostatnie odmowy poleceniem "
            "<code>sudo ausearch -m AVC -ts recent</code>. Jeśli komenda nie zwróci wpisów, zapisz, że brak wpisów "
            "AVC jest również informacją diagnostyczną."
        ),
        "common_mistakes": [
            "Wyłączanie SELinux zamiast sprawdzenia trybu, kontekstów i logów.",
            "Zakładanie, że poprawne chmod i chown zawsze wystarczą.",
            "Uruchamianie restorecon na przypadkowych ścieżkach bez zrozumienia celu.",
            "Ignorowanie logów audytu przy błędach dostępu aplikacji.",
            "Mylenie tymczasowej poprawy z trwałą regułą etykietowania.",
            "Używanie semanage fcontext bez wiedzy, jaki typ kontekstu jest właściwy.",
        ],
        "summary": (
            "Diagnoza SELinux zaczyna się od <code>getenforce</code>, <code>sestatus</code>, sprawdzenia "
            "kontekstów przez <code>ls -Z</code> i analizy odmów przez <code>ausearch</code>. "
            "<code>restorecon</code> przywraca domyślne etykiety, a <code>semanage fcontext</code> służy do "
            "trwałego opisu etykietowania ścieżek. Celem jest zrozumienie blokady, a nie szybkie wyłączenie "
            "warstwy bezpieczeństwa."
        ),
    },
    "quiz": {
        "title": "Quiz: SELinux — diagnostyka problemów",
        "description": "Sprawdź, czy potrafisz rozpocząć podstawową diagnozę problemów SELinux.",
        "questions": [
            {
                "text": "Kiedy warto podejrzewać SELinux?",
                "answers": [
                    ("a", "Gdy uprawnienia wyglądają poprawnie, a usługa nadal ma odmowę dostępu", True),
                    ("b", "Gdy brakuje rekordu MX", False),
                    ("c", "Gdy chcesz zmienić hasło użytkownika", False),
                    ("d", "Gdy kończy się miejsce w cache przeglądarki", False),
                ],
            },
            {
                "text": "Która komenda pokazuje bieżący tryb SELinux?",
                "answers": [
                    ("a", "getenforce", True),
                    ("b", "ssh-copy-id", False),
                    ("c", "ip route", False),
                    ("d", "curl -I", False),
                ],
            },
            {
                "text": "Do czego służy ls -Z?",
                "answers": [
                    ("a", "Do pokazywania kontekstów SELinux", True),
                    ("b", "Do otwierania portów", False),
                    ("c", "Do generowania certyfikatów", False),
                    ("d", "Do tworzenia rekordów DNS", False),
                ],
            },
            {
                "text": "Co robi restorecon?",
                "answers": [
                    ("a", "Przywraca domyślne konteksty SELinux dla ścieżki", True),
                    ("b", "Restartuje sshd", False),
                    ("c", "Zmienia bramę domyślną", False),
                    ("d", "Kopiuje klucz publiczny", False),
                ],
            },
            {
                "text": "Czego szuka ausearch -m AVC -ts recent?",
                "answers": [
                    ("a", "Niedawnych odmów SELinux typu AVC", True),
                    ("b", "Aktywnych stref firewalld", False),
                    ("c", "Nagłówków HTTP", False),
                    ("d", "Listy kont użytkowników", False),
                ],
            },
            {
                "text": "Do czego służy semanage fcontext?",
                "answers": [
                    ("a", "Do zarządzania regułami etykietowania kontekstów plików", True),
                    ("b", "Do sprawdzania trasy pakietów", False),
                    ("c", "Do szyfrowania klucza prywatnego SSH", False),
                    ("d", "Do pobierania certyfikatu strony", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Kiedy SELinux może być podejrzany?", "answer": "Gdy klasyczne uprawnienia są poprawne, ale dostęp nadal jest blokowany."},
        {"question": "Jaki jest pierwszy test trybu SELinux?", "answer": "getenforce."},
        {"question": "Co pokazuje sestatus?", "answer": "Szczegółowy status SELinux."},
        {"question": "Co oznacza AVC w logach?", "answer": "Odmowę dostępu związaną z polityką SELinux."},
        {"question": "Do czego służy ausearch?", "answer": "Do przeszukiwania logów audytu."},
        {"question": "Co robi ausearch -m AVC -ts recent?", "answer": "Pokazuje niedawne odmowy SELinux typu AVC."},
        {"question": "Co pokazuje ls -Z?", "answer": "Konteksty SELinux plików."},
        {"question": "Co może pójść źle po skopiowaniu pliku?", "answer": "Plik może mieć niewłaściwy kontekst SELinux."},
        {"question": "Do czego służy restorecon?", "answer": "Do przywracania domyślnych kontekstów SELinux."},
        {"question": "Co oznacza opcja -R w restorecon?", "answer": "Działanie rekurencyjne na katalogu i jego zawartości."},
        {"question": "Co oznacza opcja -v w restorecon?", "answer": "Wyświetlanie informacji o wykonanych zmianach."},
        {"question": "Czy restorecon zmienia chmod?", "answer": "Nie, dotyczy kontekstów SELinux."},
        {"question": "Czy SELinux zastępuje właściciela pliku?", "answer": "Nie, działa obok właściciela i uprawnień."},
        {"question": "Po co sprawdzać kontekst procesu?", "answer": "Bo polityka decyduje, które procesy mogą używać danych typów plików."},
        {"question": "Czym jest semanage fcontext?", "answer": "Narzędziem do trwałych reguł etykietowania ścieżek."},
        {"question": "Czy semanage fcontext od razu zmienia etykiety plików?", "answer": "Nie zawsze; zwykle po regule stosuje się restorecon."},
        {"question": "Dlaczego nie wyłączać SELinux od razu?", "answer": "Bo osłabia to bezpieczeństwo i ukrywa prawdziwą przyczynę."},
        {"question": "Co oznacza brak wpisów AVC?", "answer": "Że w ostatnich logach nie widać odmów tego typu albo trzeba sprawdzić inny zakres czasu."},
        {"question": "Czy każdy błąd 403 to SELinux?", "answer": "Nie, to tylko jedna z możliwych przyczyn."},
        {"question": "Co sprawdzić oprócz SELinux?", "answer": "Uprawnienia plików, konfigurację usługi, firewall i logi aplikacji."},
        {"question": "Jaki tryb SELinux blokuje niedozwolone akcje?", "answer": "Enforcing."},
        {"question": "Jaki tryb loguje naruszenia bez blokowania?", "answer": "Permissive."},
        {"question": "Czy disabled pomaga w diagnozie polityki?", "answer": "Nie, wyłącza mechanizm zamiast pokazać jego działanie."},
        {"question": "Co jest celem diagnozy SELinux?", "answer": "Zrozumieć blokadę i naprawić kontekst lub politykę."},
        {"question": "Jaki jest podstawowy zestaw komend diagnostycznych SELinux?", "answer": "getenforce, sestatus, ls -Z, restorecon i ausearch."},
    ],
}
