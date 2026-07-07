FIREWALLD_ZONES_SERVICES_PORTS = {
    "module": {
        "title": "Sieć i bezpieczeństwo",
        "description": "Moduł poświęcony podstawom sieci, zdalnego dostępu i zabezpieczania Linuxa.",
    },
    "lesson": {
        "title": "Firewalld — strefy, usługi i porty",
        "level": "Podstawowy+",
        "duration": "50 min",
        "description": (
            "Nauczysz się rozumieć strefy firewalld, różnicę między usługą a portem oraz bezpiecznie "
            "dodawać i usuwać reguły tymczasowe oraz permanentne."
        ),
        "theory": (
            "Firewalld zarządza regułami firewalla przez pojęcie stref. Strefa opisuje poziom zaufania dla "
            "interfejsu sieciowego albo źródła ruchu. Na prostym serwerze najczęściej pracuje się z jedną "
            "aktywną strefą, ale nadal trzeba wiedzieć, której strefy dotyczą zmiany. Komenda "
            "<code>firewall-cmd --get-active-zones</code> pokazuje aktywne strefy, a "
            "<code>firewall-cmd --list-all</code> pokazuje usługi, porty i inne reguły w wybranej strefie. "
            "Usługa w firewalld, na przykład <code>ssh</code> albo <code>http</code>, jest nazwaną definicją "
            "obejmującą porty i protokoły. Port, na przykład <code>8080/tcp</code>, dodaje się wtedy, gdy "
            "nie ma gotowej definicji usługi albo aplikacja działa na niestandardowym porcie. Zmiany runtime "
            "działają od razu, ale nie muszą przetrwać przeładowania firewalla. Zmiany permanentne zapisują się "
            "w konfiguracji, ale zwykle wymagają <code>--reload</code>, aby wejść w życie. Dobry workflow to "
            "najpierw sprawdzić aktywną strefę, potem dodać regułę tymczasowo, przetestować dostęp, a dopiero "
            "później zapisać zmianę jako permanentną."
        ),
        "commands": [
            {
                "command": "sudo firewall-cmd --get-active-zones",
                "description": "Pokazuje aktywne strefy firewalld i powiązane interfejsy.",
                "example": "$ sudo firewall-cmd --get-active-zones",
            },
            {
                "command": "sudo firewall-cmd --list-all",
                "description": "Wyświetla konfigurację domyślnej albo aktywnej strefy.",
                "example": "$ sudo firewall-cmd --list-all",
            },
            {
                "command": "sudo firewall-cmd --add-service=http",
                "description": "Tymczasowo dopuszcza usługę HTTP.",
                "example": "$ sudo firewall-cmd --add-service=http",
            },
            {
                "command": "sudo firewall-cmd --add-port=8080/tcp",
                "description": "Tymczasowo dopuszcza ruch TCP na porcie 8080.",
                "example": "$ sudo firewall-cmd --add-port=8080/tcp",
            },
            {
                "command": "sudo firewall-cmd --remove-service=http",
                "description": "Usuwa tymczasowe dopuszczenie usługi HTTP.",
                "example": "$ sudo firewall-cmd --remove-service=http",
            },
            {
                "command": "sudo firewall-cmd --reload",
                "description": "Przeładowuje konfigurację firewalld.",
                "example": "$ sudo firewall-cmd --reload",
            },
        ],
        "practice_task": (
            "Na maszynie testowej wykonaj <code>sudo firewall-cmd --get-active-zones</code> i "
            "<code>sudo firewall-cmd --list-all</code>. Zapisz aktywną strefę oraz listę usług i portów. "
            "Dodaj tymczasowo usługę HTTP przez <code>sudo firewall-cmd --add-service=http</code> i sprawdź "
            "wynik w <code>--list-all</code>. Następnie usuń ją poleceniem "
            "<code>sudo firewall-cmd --remove-service=http</code>. W osobnym teście dodaj port "
            "<code>8080/tcp</code> przez <code>sudo firewall-cmd --add-port=8080/tcp</code>, sprawdź listę "
            "reguł i przeładuj firewall przez <code>sudo firewall-cmd --reload</code>, obserwując różnicę "
            "między zmianą runtime a trwałą konfiguracją."
        ),
        "common_mistakes": [
            "Dodawanie reguł bez sprawdzenia aktywnej strefy.",
            "Mylenie usługi firewalld z procesem działającym w systemie.",
            "Otwieranie portu, gdy istnieje gotowa usługa firewalld o tej samej roli.",
            "Zakładanie, że zmiana runtime przetrwa reload albo restart.",
            "Dodanie opcji --permanent i zapomnienie o przeładowaniu konfiguracji.",
            "Otwieranie portów bez sprawdzenia, czy aplikacja naprawdę ich potrzebuje.",
        ],
        "summary": (
            "Firewalld używa stref, usług i portów. Strefa opisuje zaufanie do ruchu, usługa jest nazwaną "
            "definicją, a port pozwala dopuścić konkretny numer i protokół. Zmiany runtime są dobre do testów, "
            "a zmiany permanentne służą do trwałej konfiguracji. <code>--get-active-zones</code>, "
            "<code>--list-all</code>, <code>--add-service</code>, <code>--add-port</code> i "
            "<code>--reload</code> to podstawowy zestaw komend."
        ),
    },
    "quiz": {
        "title": "Quiz: firewalld — strefy, usługi i porty",
        "description": "Sprawdź, czy rozumiesz strefy firewalld, usługi, porty i zmiany runtime.",
        "questions": [
            {
                "text": "Czym jest strefa w firewalld?",
                "answers": [
                    ("a", "Zestawem zasad opisującym poziom zaufania dla ruchu", True),
                    ("b", "Katalogiem z kluczami SSH", False),
                    ("c", "Typem rekordu DNS", False),
                    ("d", "Nazwą certyfikatu TLS", False),
                ],
            },
            {
                "text": "Co pokazuje firewall-cmd --get-active-zones?",
                "answers": [
                    ("a", "Aktywne strefy i powiązane interfejsy", True),
                    ("b", "Listę użytkowników systemu", False),
                    ("c", "Tylko logi SELinux", False),
                    ("d", "Zawartość authorized_keys", False),
                ],
            },
            {
                "text": "Czym jest usługa w firewalld?",
                "answers": [
                    ("a", "Nazwaną definicją portów i protokołów, na przykład http", True),
                    ("b", "Zawsze procesem aplikacji", False),
                    ("c", "Hasłem administratora", False),
                    ("d", "Trasą domyślną", False),
                ],
            },
            {
                "text": "Kiedy użyć --add-port=8080/tcp?",
                "answers": [
                    ("a", "Gdy trzeba dopuścić konkretny port TCP, często niestandardowy", True),
                    ("b", "Gdy trzeba utworzyć użytkownika", False),
                    ("c", "Gdy trzeba wygenerować klucz SSH", False),
                    ("d", "Gdy trzeba sprawdzić rekord MX", False),
                ],
            },
            {
                "text": "Co oznacza zmiana runtime w firewalld?",
                "answers": [
                    ("a", "Działa od razu, ale nie musi przetrwać przeładowania konfiguracji", True),
                    ("b", "Zawsze usuwa wszystkie reguły", False),
                    ("c", "Jest zmianą tylko w DNS", False),
                    ("d", "Wyłącza SELinux", False),
                ],
            },
            {
                "text": "Do czego służy firewall-cmd --reload?",
                "answers": [
                    ("a", "Do przeładowania konfiguracji firewalld", True),
                    ("b", "Do restartu sshd", False),
                    ("c", "Do odnowienia certyfikatu", False),
                    ("d", "Do zmiany właściciela pliku", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest firewalld?", "answer": "Usługą do zarządzania firewallem w wielu systemach z rodziny RHEL."},
        {"question": "Czym jest strefa firewalld?", "answer": "Zestawem reguł dla określonego poziomu zaufania ruchu."},
        {"question": "Co pokazuje --get-active-zones?", "answer": "Aktywne strefy i przypisane interfejsy lub źródła."},
        {"question": "Co pokazuje --list-all?", "answer": "Konfigurację strefy, w tym usługi i porty."},
        {"question": "Czym jest usługa w firewalld?", "answer": "Nazwaną definicją portów i protokołów, na przykład ssh lub http."},
        {"question": "Czym jest port w regule firewalld?", "answer": "Konkretnym numerem portu i protokołem, na przykład 8080/tcp."},
        {"question": "Kiedy lepiej użyć usługi niż portu?", "answer": "Gdy firewalld ma gotową definicję dla danej usługi."},
        {"question": "Kiedy użyć --add-port?", "answer": "Gdy trzeba dopuścić konkretny lub niestandardowy port."},
        {"question": "Co robi --add-service=http?", "answer": "Dopuszcza usługę HTTP w strefie."},
        {"question": "Co robi --add-port=8080/tcp?", "answer": "Dopuszcza ruch TCP na porcie 8080."},
        {"question": "Co robi --remove-service=http?", "answer": "Usuwa dopuszczenie usługi HTTP."},
        {"question": "Co robi --reload?", "answer": "Przeładowuje konfigurację firewalld."},
        {"question": "Czym jest konfiguracja runtime?", "answer": "Bieżącą konfiguracją działającą od razu."},
        {"question": "Czym jest konfiguracja permanentna?", "answer": "Trwałą konfiguracją zapisaną na późniejsze przeładowania."},
        {"question": "Czy zmiana bez --permanent jest trwała?", "answer": "Nie, jest zmianą runtime."},
        {"question": "Co może być potrzebne po zmianie permanentnej?", "answer": "Przeładowanie konfiguracji przez firewall-cmd --reload."},
        {"question": "Co sprawdzić przed otwarciem portu?", "answer": "Czy aplikacja go potrzebuje i czy proces naprawdę nasłuchuje."},
        {"question": "Czy firewalld uruchamia aplikację?", "answer": "Nie, tylko kontroluje ruch sieciowy."},
        {"question": "Czy otwarcie portu gwarantuje działanie usługi?", "answer": "Nie, aplikacja musi jeszcze działać i nasłuchiwać."},
        {"question": "Dlaczego zaczynać od aktywnej strefy?", "answer": "Aby zmieniać właściwy zestaw reguł."},
        {"question": "Jaki port zwykle odpowiada HTTPS?", "answer": "443/tcp."},
        {"question": "Jaki port zwykle odpowiada SSH?", "answer": "22/tcp."},
        {"question": "Dlaczego testować zmianę runtime?", "answer": "Bo można sprawdzić efekt przed zapisaniem trwałej reguły."},
        {"question": "Co dokumentować przy regułach firewalla?", "answer": "Powód otwarcia usługi lub portu."},
        {"question": "Jaki jest dobry workflow firewalld?", "answer": "Sprawdź strefę, dodaj tymczasowo, przetestuj, a potem zapisz trwałą zmianę."},
    ],
}
