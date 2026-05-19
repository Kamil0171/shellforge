PACKAGE_MANAGEMENT = {
    "module": {
        "title": "Podstawy terminala",
        "description": "Pierwszy moduł poświęcony pracy w terminalu Linux.",
    },
    "lesson": {
        "title": "Pakiety i aktualizacje: yum, rpm i repozytoria",
        "level": "Podstawowy",
        "duration": "35 min",
        "description": (
            "Poznasz podstawowe komendy do aktualizowania systemu, instalowania programów, "
            "sprawdzania pakietów oraz rozumienia roli repozytoriów w systemie Linux."
        ),
        "theory": (
            "W systemach Linux programy najczęściej instaluje się jako pakiety. Pakiet zawiera "
            "pliki programu, informacje o wersji oraz zależności potrzebne do poprawnego działania. "
            "Menedżer pakietów ułatwia instalowanie, aktualizowanie i usuwanie oprogramowania. "
            "W systemach z rodziny Red Hat, takich jak Rocky Linux, często używa się polecenia yum. "
            "Repozytorium to zdalne źródło pakietów, z którego system pobiera oprogramowanie. "
            "Polecenie rpm pozwala sprawdzać informacje o pakietach zainstalowanych lokalnie. "
            "Znajomość podstaw pracy z pakietami jest konieczna przed instalowaniem usług takich jak "
            "Nginx, firewalld, Git, Python lub narzędzia administracyjne."
        ),
        "commands": [
            {
                "command": "yum update",
                "description": "Aktualizuje pakiety zainstalowane w systemie.",
                "example": "$ yum update",
            },
            {
                "command": "yum install nginx",
                "description": "Instaluje wybrany pakiet z dostępnych repozytoriów.",
                "example": "$ yum install nginx",
            },
            {
                "command": "yum remove nginx",
                "description": "Usuwa wskazany pakiet z systemu.",
                "example": "$ yum remove nginx",
            },
            {
                "command": "yum search nginx",
                "description": "Wyszukuje pakiety związane z podaną frazą.",
                "example": "$ yum search nginx",
            },
            {
                "command": "yum info nginx",
                "description": "Pokazuje szczegółowe informacje o pakiecie.",
                "example": "$ yum info nginx",
            },
            {
                "command": "yum list installed",
                "description": "Wyświetla listę pakietów zainstalowanych w systemie.",
                "example": "$ yum list installed",
            },
            {
                "command": "yum repolist",
                "description": "Wyświetla aktywne repozytoria pakietów.",
                "example": "$ yum repolist",
            },
            {
                "command": "rpm -q nginx",
                "description": "Sprawdza, czy konkretny pakiet jest zainstalowany.",
                "example": "$ rpm -q nginx",
            },
            {
                "command": "rpm -qa",
                "description": "Wyświetla wszystkie pakiety zainstalowane w systemie.",
                "example": "$ rpm -qa",
            },
        ],
        "practice_task": (
            "Sprawdź listę aktywnych repozytoriów poleceniem <code>yum repolist</code>. "
            "Następnie wyszukaj przykładowy pakiet za pomocą <code>yum search</code>, na przykład "
            "<code>yum search nginx</code>. Podejrzyj szczegóły pakietu komendą "
            "<code>yum info nginx</code>. Sprawdź, czy pakiet jest zainstalowany przez "
            "<code>rpm -q nginx</code>. Na końcu wyświetl fragment listy zainstalowanych pakietów "
            "komendą <code>yum list installed</code>."
        ),
        "common_mistakes": [
            "Instalowanie pakietów bez wcześniejszego sprawdzenia, do czego służą.",
            "Mylenie <code>yum search</code> z <code>yum install</code>.",
            "Usuwanie pakietów bez upewnienia się, czy nie są potrzebne innym usługom.",
            "Zakładanie, że pakiet jest zainstalowany, bez sprawdzenia tego komendą <code>rpm -q</code>.",
            "Pomijanie aktualizacji systemu na serwerze.",
            "Nieczytanie komunikatów wyświetlanych przez menedżer pakietów.",
            "Mylenie repozytorium z pojedynczym pakietem.",
        ],
        "summary": (
            "Pakiety są podstawowym sposobem instalowania oprogramowania w Linuxie. "
            "Komenda <code>yum update</code> aktualizuje system, <code>yum install</code> instaluje "
            "pakiety, <code>yum remove</code> je usuwa, <code>yum search</code> wyszukuje dostępne "
            "oprogramowanie, a <code>yum info</code> pokazuje szczegóły pakietu. Repozytoria są "
            "źródłami pakietów, z których korzysta system. Polecenia <code>rpm -q</code> i "
            "<code>rpm -qa</code> pomagają sprawdzać pakiety zainstalowane lokalnie."
        ),
    },
    "quiz": {
        "title": "Quiz: pakiety i aktualizacje",
        "description": "Sprawdź, czy rozumiesz podstawy pracy z pakietami, yum, rpm i repozytoriami.",
        "questions": [
            {
                "text": "Do czego służy menedżer pakietów?",
                "answers": [
                    ("a", "Do instalowania, aktualizowania i usuwania oprogramowania", True),
                    ("b", "Do zmiany nazwy użytkownika", False),
                    ("c", "Do wyłączania monitora", False),
                    ("d", "Do tworzenia partycji bez systemu plików", False),
                ],
            },
            {
                "text": "Co robi komenda yum update?",
                "answers": [
                    ("a", "Aktualizuje pakiety zainstalowane w systemie", True),
                    ("b", "Usuwa wszystkie pliki użytkownika", False),
                    ("c", "Zmienia hasło roota", False),
                    ("d", "Tworzy nowy katalog", False),
                ],
            },
            {
                "text": "Która komenda instaluje pakiet nginx?",
                "answers": [
                    ("a", "yum install nginx", True),
                    ("b", "yum search nginx", False),
                    ("c", "rpm -qa nginx", False),
                    ("d", "chmod nginx", False),
                ],
            },
            {
                "text": "Do czego służy yum search?",
                "answers": [
                    ("a", "Do wyszukiwania pakietów", True),
                    ("b", "Do restartowania systemu", False),
                    ("c", "Do kasowania logów", False),
                    ("d", "Do zmiany właściciela pliku", False),
                ],
            },
            {
                "text": "Co pokazuje yum info?",
                "answers": [
                    ("a", "Szczegółowe informacje o pakiecie", True),
                    ("b", "Tylko aktualny katalog", False),
                    ("c", "Tylko listę użytkowników", False),
                    ("d", "Wyłącznie historię logowania", False),
                ],
            },
            {
                "text": "Czym jest repozytorium pakietów?",
                "answers": [
                    ("a", "Źródłem pakietów, z którego system może pobierać oprogramowanie", True),
                    ("b", "Plikiem tekstowym z hasłem użytkownika", False),
                    ("c", "Tymczasowym katalogiem procesów", False),
                    ("d", "Nazwą procesu systemowego", False),
                ],
            },
            {
                "text": "Co robi komenda yum repolist?",
                "answers": [
                    ("a", "Wyświetla aktywne repozytoria", True),
                    ("b", "Wyłącza wszystkie usługi", False),
                    ("c", "Usuwa repozytorium domowe użytkownika", False),
                    ("d", "Pokazuje tylko otwarte porty", False),
                ],
            },
            {
                "text": "Do czego służy rpm -q nginx?",
                "answers": [
                    ("a", "Do sprawdzenia, czy pakiet nginx jest zainstalowany", True),
                    ("b", "Do instalacji pakietu nginx z internetu", False),
                    ("c", "Do zmiany nazwy pakietu", False),
                    ("d", "Do wyłączenia usługi nginx", False),
                ],
            },
            {
                "text": "Co pokazuje rpm -qa?",
                "answers": [
                    ("a", "Listę wszystkich zainstalowanych pakietów", True),
                    ("b", "Tylko aktualną datę", False),
                    ("c", "Tylko aktywne procesy", False),
                    ("d", "Tylko reguły firewalla", False),
                ],
            },
            {
                "text": "Dlaczego warto czytać komunikaty menedżera pakietów?",
                "answers": [
                    ("a", "Bo informują o instalowanych pakietach, zależnościach i możliwych zmianach", True),
                    ("b", "Bo zawsze zawierają hasło administratora", False),
                    ("c", "Bo automatycznie naprawiają każdą usługę", False),
                    ("d", "Bo zastępują dokumentację systemu", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Do czego służy yum?",
            "answer": "Do zarządzania pakietami, czyli instalowania, aktualizowania i usuwania oprogramowania.",
        },
        {
            "question": "Co robi yum update?",
            "answer": "Aktualizuje pakiety zainstalowane w systemie.",
        },
        {
            "question": "Jak zainstalować pakiet nginx przez yum?",
            "answer": "Komendą yum install nginx.",
        },
        {
            "question": "Jak usunąć pakiet przez yum?",
            "answer": "Komendą yum remove nazwa-pakietu.",
        },
        {
            "question": "Do czego służy yum search?",
            "answer": "Do wyszukiwania pakietów związanych z podaną frazą.",
        },
        {
            "question": "Do czego służy yum info?",
            "answer": "Do wyświetlania szczegółowych informacji o pakiecie.",
        },
        {
            "question": "Co pokazuje yum list installed?",
            "answer": "Listę pakietów zainstalowanych w systemie.",
        },
        {
            "question": "Co pokazuje yum repolist?",
            "answer": "Listę aktywnych repozytoriów pakietów.",
        },
        {
            "question": "Czym jest repozytorium?",
            "answer": "Źródłem pakietów, z którego system pobiera oprogramowanie.",
        },
        {
            "question": "Do czego służy rpm?",
            "answer": "Do pracy z lokalnymi pakietami RPM i sprawdzania informacji o zainstalowanych pakietach.",
        },
        {
            "question": "Co robi rpm -q nginx?",
            "answer": "Sprawdza, czy pakiet nginx jest zainstalowany.",
        },
        {
            "question": "Co robi rpm -qa?",
            "answer": "Wyświetla wszystkie pakiety zainstalowane w systemie.",
        },
        {
            "question": "Czy yum pobiera pakiety z repozytoriów?",
            "answer": "Tak, yum korzysta ze skonfigurowanych repozytoriów pakietów.",
        },
        {
            "question": "Dlaczego nie warto usuwać pakietów bez namysłu?",
            "answer": "Bo mogą być potrzebne innym programom lub usługom.",
        },
        {
            "question": "Czy yum search instaluje pakiet?",
            "answer": "Nie. yum search tylko wyszukuje pakiety.",
        },
        {
            "question": "Czy yum install instaluje pakiet?",
            "answer": "Tak. yum install instaluje wskazany pakiet.",
        },
        {
            "question": "Po co sprawdzać yum info przed instalacją?",
            "answer": "Aby zobaczyć opis pakietu, wersję, repozytorium i inne szczegóły.",
        },
        {
            "question": "Czy aktualizacje są ważne na serwerze?",
            "answer": "Tak, pomagają utrzymywać bezpieczeństwo i stabilność systemu.",
        },
        {
            "question": "Jaka komenda pokazuje aktywne repozytoria?",
            "answer": "yum repolist.",
        },
        {
            "question": "Jaka komenda sprawdza lokalnie zainstalowany pakiet?",
            "answer": "rpm -q nazwa-pakietu.",
        },
    ],
}