FIREWALL_BASICS = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "Firewall — podstawy",
        "level": "Podstawowy+",
        "duration": "45 min",
        "description": (
            "Nauczysz się, po co używa się firewalla, jak rozumieć dopuszczanie i blokowanie ruchu "
            "oraz jak sprawdzać podstawowy stan firewalld w Rocky Linux."
        ),
        "theory": (
            "Firewall kontroluje ruch sieciowy przychodzący i wychodzący zgodnie z regułami. Dla początkującego "
            "administratora najważniejsze jest rozumienie, że usługa może działać i nasłuchiwać na porcie, "
            "ale ruch z zewnątrz nadal może być zablokowany przez firewall. Dopuszczenie ruchu oznacza, że "
            "reguły pozwalają pakietom dotrzeć do usługi. Blokowanie oznacza, że firewall odrzuca lub ignoruje "
            "ruch, zanim aplikacja będzie mogła odpowiedzieć. W systemach z rodziny RHEL, w tym Rocky Linux, "
            "często używa się <code>firewalld</code>. Narzędzie <code>firewall-cmd</code> pozwala sprawdzać "
            "aktywne strefy, usługi i porty. Strefa opisuje poziom zaufania dla interfejsu lub źródła ruchu. "
            "W podstawowej administracji warto najpierw sprawdzić, czy <code>firewalld</code> działa, jaka jest "
            "strefa domyślna i jakie usługi są dopuszczone. Dopiero potem zmienia się reguły. W laboratorium "
            "można dodać usługę tymczasowo, bez opcji <code>--permanent</code>, aby zobaczyć efekt do "
            "następnego przeładowania konfiguracji."
        ),
        "commands": [
            {
                "command": "systemctl status firewalld",
                "description": "Sprawdza, czy usługa firewalld działa.",
                "example": "$ systemctl status firewalld",
            },
            {
                "command": "sudo firewall-cmd --state",
                "description": "Pokazuje prosty stan firewalld.",
                "example": "$ sudo firewall-cmd --state",
            },
            {
                "command": "sudo firewall-cmd --get-default-zone",
                "description": "Wyświetla domyślną strefę firewalld.",
                "example": "$ sudo firewall-cmd --get-default-zone",
            },
            {
                "command": "sudo firewall-cmd --get-active-zones",
                "description": "Pokazuje aktywne strefy i przypisane do nich interfejsy.",
                "example": "$ sudo firewall-cmd --get-active-zones",
            },
            {
                "command": "sudo firewall-cmd --list-all",
                "description": "Wyświetla reguły aktywnej strefy, w tym usługi i porty.",
                "example": "$ sudo firewall-cmd --list-all",
            },
            {
                "command": "sudo firewall-cmd --add-service=http",
                "description": "Tymczasowo dopuszcza usługę HTTP w aktywnej strefie.",
                "example": "$ sudo firewall-cmd --add-service=http",
            },
            {
                "command": "sudo firewall-cmd --remove-service=http",
                "description": "Usuwa tymczasowe dopuszczenie usługi HTTP.",
                "example": "$ sudo firewall-cmd --remove-service=http",
            },
        ],
        "practice_task": (
            "Na maszynie laboratoryjnej wykonaj <code>systemctl status firewalld</code>, "
            "<code>sudo firewall-cmd --state</code>, <code>sudo firewall-cmd --get-default-zone</code> "
            "i <code>sudo firewall-cmd --list-all</code>. Zapisz, które usługi są dopuszczone w aktywnej "
            "strefie. Jeśli to bezpieczne środowisko testowe, dodaj tymczasowo usługę HTTP przez "
            "<code>sudo firewall-cmd --add-service=http</code>, ponownie wykonaj <code>--list-all</code>, "
            "a potem cofnij zmianę przez <code>sudo firewall-cmd --remove-service=http</code>."
        ),
        "common_mistakes": [
            "Zakładanie, że działająca usługa automatycznie jest dostępna z sieci.",
            "Dodawanie reguł bez sprawdzenia aktywnej strefy.",
            "Mylenie usługi firewalld z konkretną usługą aplikacji, na przykład HTTP.",
            "Wprowadzanie zmian permanentnych bez wcześniejszego testu tymczasowego.",
            "Otwieranie portów bez wiedzy, jaki proces na nich nasłuchuje.",
            "Diagnozowanie firewalla bez sprawdzenia portów przez ss.",
        ],
        "summary": (
            "Firewall decyduje, jaki ruch jest dopuszczony albo blokowany. W Rocky Linux typowym narzędziem "
            "jest <code>firewalld</code>, sprawdzany przez <code>systemctl status firewalld</code> i "
            "<code>firewall-cmd</code>. Przed zmianą reguł warto sprawdzić stan, strefę, listę usług oraz "
            "to, czy aplikacja naprawdę nasłuchuje na danym porcie."
        ),
    },
    "quiz": {
        "title": "Quiz: firewall — podstawy",
        "description": "Sprawdź, czy rozumiesz podstawową rolę firewalla i komendy firewalld.",
        "questions": [
            {
                "text": "Po co używa się firewalla?",
                "answers": [
                    ("a", "Do kontrolowania dopuszczanego i blokowanego ruchu sieciowego", True),
                    ("b", "Do tworzenia kont użytkowników", False),
                    ("c", "Do edycji plików tekstowych", False),
                    ("d", "Do wyświetlania rozmiaru katalogów", False),
                ],
            },
            {
                "text": "Co może się stać, gdy usługa nasłuchuje, ale firewall blokuje ruch?",
                "answers": [
                    ("a", "Usługa lokalnie działa, ale z zewnątrz może być niedostępna", True),
                    ("b", "System automatycznie usuwa usługę", False),
                    ("c", "DNS zawsze przestaje działać", False),
                    ("d", "SELinux zostaje wyłączony", False),
                ],
            },
            {
                "text": "Jak sprawdzić stan usługi firewalld?",
                "answers": [
                    ("a", "systemctl status firewalld", True),
                    ("b", "passwd firewalld", False),
                    ("c", "du -sh firewalld", False),
                    ("d", "ssh-keygen firewalld", False),
                ],
            },
            {
                "text": "Do czego służy firewall-cmd --list-all?",
                "answers": [
                    ("a", "Do pokazania reguł aktywnej strefy", True),
                    ("b", "Do wyświetlenia wszystkich plików w /var", False),
                    ("c", "Do utworzenia klucza SSH", False),
                    ("d", "Do zmiany rekordu DNS", False),
                ],
            },
            {
                "text": "Czym jest strefa w firewalld?",
                "answers": [
                    ("a", "Zestawem reguł opisującym poziom zaufania dla ruchu", True),
                    ("b", "Katalogiem domowym użytkownika", False),
                    ("c", "Typem rekordu DNS", False),
                    ("d", "Trybem pracy SELinux", False),
                ],
            },
            {
                "text": "Dlaczego warto testować zmianę bez --permanent?",
                "answers": [
                    ("a", "Bo łatwiej sprawdzić efekt bez trwałej zmiany konfiguracji", True),
                    ("b", "Bo trwałe reguły nigdy nie działają", False),
                    ("c", "Bo wyłącza to wszystkie porty", False),
                    ("d", "Bo zastępuje aktualizacje systemu", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest firewall?", "answer": "Mechanizmem kontrolującym ruch sieciowy według reguł."},
        {"question": "Co oznacza dopuszczenie ruchu?", "answer": "Reguły pozwalają pakietom dotrzeć do usługi."},
        {"question": "Co oznacza blokowanie ruchu?", "answer": "Firewall zatrzymuje ruch zgodnie z regułami."},
        {"question": "Czy działająca usługa zawsze jest dostępna z sieci?", "answer": "Nie, firewall może blokować ruch."},
        {"question": "Czym jest firewalld?", "answer": "Usługą zarządzającą firewallem często używaną w systemach RHEL i Rocky Linux."},
        {"question": "Jak sprawdzić usługę firewalld?", "answer": "systemctl status firewalld."},
        {"question": "Do czego służy firewall-cmd?", "answer": "Do sprawdzania i zmiany konfiguracji firewalld."},
        {"question": "Co robi firewall-cmd --state?", "answer": "Pokazuje prosty stan działania firewalld."},
        {"question": "Co robi firewall-cmd --get-default-zone?", "answer": "Pokazuje domyślną strefę."},
        {"question": "Co robi firewall-cmd --get-active-zones?", "answer": "Pokazuje aktywne strefy i powiązane interfejsy."},
        {"question": "Co robi firewall-cmd --list-all?", "answer": "Pokazuje konfigurację aktywnej strefy."},
        {"question": "Czym jest strefa firewalld?", "answer": "Zestawem zasad dla określonego poziomu zaufania ruchu."},
        {"question": "Co oznacza usługa w firewalld?", "answer": "Nazwany zestaw portów i protokołów, na przykład http lub ssh."},
        {"question": "Co robi firewall-cmd --add-service=http?", "answer": "Dopuszcza usługę HTTP w aktywnej strefie, domyślnie tymczasowo."},
        {"question": "Co robi firewall-cmd --remove-service=http?", "answer": "Usuwa dopuszczenie usługi HTTP z aktywnej strefy."},
        {"question": "Co oznacza opcja --permanent?", "answer": "Zapisuje zmianę w trwałej konfiguracji firewalld."},
        {"question": "Dlaczego ostrożnie używać --permanent?", "answer": "Bo zmiana pozostanie po przeładowaniu lub restarcie."},
        {"question": "Co sprawdzić przed otwarciem portu?", "answer": "Czy znasz usługę, proces, port i potrzebę dostępu."},
        {"question": "Jak powiązać firewall z diagnostyką portów?", "answer": "Najpierw sprawdzić ss, a potem reguły firewalla."},
        {"question": "Czy firewall zastępuje aktualizacje systemu?", "answer": "Nie, to tylko jedna warstwa ochrony."},
        {"question": "Czy firewall naprawia błędną konfigurację aplikacji?", "answer": "Nie, kontroluje ruch, ale nie poprawia aplikacji."},
        {"question": "Jaki port zwykle warto chronić szczególnie ostrożnie?", "answer": "SSH na porcie 22 lub innym skonfigurowanym porcie."},
        {"question": "Co znaczy, że zmiana jest tymczasowa?", "answer": "Nie jest zapisana jako permanentna i może zniknąć po przeładowaniu."},
        {"question": "Dlaczego warto dokumentować otwarte usługi?", "answer": "Aby wiedzieć, dlaczego ruch został dopuszczony."},
        {"question": "Jaki jest dobry pierwszy krok przy firewallu?", "answer": "Sprawdzenie statusu firewalld i listy aktywnych reguł."},
    ],
}
