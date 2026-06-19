DISK_SPACE_CLEANUP = {
    "module": {
        "title": "Administracja systemem",
        "description": "Moduł poświęcony podstawowej administracji systemem Linux.",
    },
    "lesson": {
        "title": "Miejsce na dysku i porządkowanie systemu: df, du, cache i logi",
        "level": "Podstawowy+",
        "duration": "45 min",
        "description": (
            "Nauczysz się znajdować źródło zajętego miejsca i bezpiecznie porządkować "
            "cache pakietów oraz logi bez przypadkowego usuwania danych."
        ),
        "theory": (
            "Brak miejsca na dysku może zatrzymać aktualizacje, zapis logów i działanie usług. "
            "<code>df</code> pokazuje wykorzystanie całych systemów plików, natomiast "
            "<code>du</code> oblicza rozmiar wskazanych katalogów i plików. To różne perspektywy: "
            "najpierw używa się <code>df -h</code>, aby znaleźć zapełniony system plików, a potem "
            "<code>du</code>, aby zawęzić źródło problemu. Opcja <code>-x</code> pomaga pozostać "
            "w jednym systemie plików. Warto sprawdzić także inode przez <code>df -i</code>, "
            "ponieważ ogromna liczba małych plików może uniemożliwić tworzenie nowych danych mimo "
            "wolnych bajtów. Typowymi źródłami wzrostu są logi, cache menedżera pakietów, dane "
            "aplikacji i pliki tymczasowe. W Rocky Linux cache DNF można analizować i czyścić "
            "poleceniem <code>dnf clean</code>. Rozmiar journala sprawdza "
            "<code>journalctl --disk-usage</code>, a jego kontrolowane ograniczenie umożliwia "
            "<code>journalctl --vacuum-size</code> lub <code>--vacuum-time</code>. Czyszczenie "
            "musi następować dopiero po identyfikacji danych i ocenie ich znaczenia. Nie należy "
            "usuwać losowo zawartości <code>/var</code>, aktywnych logów ani plików należących "
            "do bazy danych. Po sprzątaniu trzeba ponownie uruchomić pomiar i potwierdzić efekt."
        ),
        "commands": [
            {
                "command": "df -h",
                "description": "Pokazuje zajętość systemów plików w czytelnych jednostkach.",
                "example": "$ df -h",
            },
            {
                "command": "df -i",
                "description": "Pokazuje wykorzystanie inode w systemach plików.",
                "example": "$ df -i",
            },
            {
                "command": "sudo du -xhd 1 /var",
                "description": "Porównuje katalogi pierwszego poziomu w /var bez przechodzenia na inne systemy plików.",
                "example": "$ sudo du -xhd 1 /var",
            },
            {
                "command": "sudo du -xah /var/log | sort -h | tail -n 20",
                "description": "Pokazuje największe elementy w /var/log.",
                "example": "$ sudo du -xah /var/log | sort -h | tail -n 20",
            },
            {
                "command": "sudo dnf clean packages",
                "description": "Usuwa pobrane pakiety z cache DNF.",
                "example": "$ sudo dnf clean packages",
            },
            {
                "command": "sudo dnf clean all",
                "description": "Czyści pakiety i metadane cache DNF, które mogą zostać pobrane ponownie.",
                "example": "$ sudo dnf clean all",
            },
            {
                "command": "journalctl --disk-usage",
                "description": "Pokazuje miejsce zajmowane przez pliki journala.",
                "example": "$ journalctl --disk-usage",
            },
            {
                "command": "sudo journalctl --vacuum-time=14d",
                "description": "Usuwa zarchiwizowane wpisy journala starsze niż 14 dni.",
                "example": "$ sudo journalctl --vacuum-time=14d",
            },
            {
                "command": "sudo journalctl --vacuum-size=500M",
                "description": "Ogranicza zarchiwizowany journal do około 500 MB.",
                "example": "$ sudo journalctl --vacuum-size=500M",
            },
        ],
        "practice_task": (
            "W maszynie laboratoryjnej wykonaj <code>df -h</code> i <code>df -i</code>. Wskaż "
            "system plików o najwyższym użyciu procentowym oraz sprawdź, czy problem dotyczy "
            "bajtów czy inode. Następnie uruchom <code>sudo du -xhd 1 /var</code> i zawęź analizę "
            "do największego katalogu, nie usuwając żadnych danych. Sprawdź "
            "<code>journalctl --disk-usage</code> oraz rozmiary elementów w "
            "<code>/var/cache/dnf</code>. Zaproponuj najbezpieczniejszą akcję porządkową. Jeśli "
            "środowisko jest przeznaczone do ćwiczeń, wyczyść wyłącznie cache pakietów przez "
            "<code>sudo dnf clean packages</code>, a potem ponownie wykonaj pomiary i porównaj wynik."
        ),
        "common_mistakes": [
            "Używanie df i du zamiennie bez rozumienia, co mierzą.",
            "Usuwanie plików przed ustaleniem, który system plików jest zapełniony.",
            "Pomijanie wykorzystania inode pokazywanego przez df -i.",
            "Uruchamianie du od katalogu / bez ograniczenia systemu plików i głębokości.",
            "Kasowanie całego /var/log zamiast użycia rotacji i kontrolowanego vacuum.",
            "Traktowanie cache, logów i danych aplikacji jako równie bezpiecznych do usunięcia.",
            "Brak ponownego pomiaru po wykonaniu porządkowania.",
        ],
        "summary": (
            "Najpierw użyj <code>df -h</code> i <code>df -i</code>, aby określić rodzaj i miejsce "
            "problemu. Następnie zawężaj analizę przez <code>du -xhd 1</code>. Cache DNF można "
            "odtworzyć, ale dane aplikacji wymagają szczególnej ochrony. Journal ograniczaj "
            "kontrolowanymi opcjami vacuum. Każde sprzątanie powinno kończyć się ponownym pomiarem."
        ),
    },
    "quiz": {
        "title": "Quiz: miejsce na dysku i porządkowanie systemu",
        "description": "Sprawdź, czy potrafisz znaleźć źródło problemu i dobrać bezpieczną akcję.",
        "questions": [
            {
                "text": "Które polecenie najlepiej pokaże, który system plików jest prawie pełny?",
                "answers": [
                    ("a", "df -h", True),
                    ("b", "whoami", False),
                    ("c", "systemctl enable", False),
                    ("d", "crontab -e", False),
                ],
            },
            {
                "text": "System ma wolne gigabajty, ale nie można tworzyć nowych małych plików. Co sprawdzić?",
                "answers": [
                    ("a", "Wykorzystanie inode przez df -i", True),
                    ("b", "Nazwę hosta przez hostnamectl", False),
                    ("c", "Autostart crond", False),
                    ("d", "Listę użytkowników przez whoami", False),
                ],
            },
            {
                "text": "Do czego służy du -xhd 1 /var?",
                "answers": [
                    ("a", "Do porównania rozmiarów katalogów w /var na jednym systemie plików", True),
                    ("b", "Do usunięcia katalogu /var", False),
                    ("c", "Do pokazania wolnej pamięci RAM", False),
                    ("d", "Do restartu usługi logów", False),
                ],
            },
            {
                "text": "Która akcja jest zwykle bezpieczniejsza niż ręczne kasowanie plików z /var/log?",
                "answers": [
                    ("a", "Użycie skonfigurowanej rotacji lub journalctl --vacuum-*", True),
                    ("b", "Usunięcie całego katalogu /var", False),
                    ("c", "Wyłączenie zapisu wszystkich logów", False),
                    ("d", "Formatowanie systemu plików", False),
                ],
            },
            {
                "text": "Co robi dnf clean packages?",
                "answers": [
                    ("a", "Usuwa pobrane pakiety z cache DNF", True),
                    ("b", "Odinstalowuje wszystkie zainstalowane programy", False),
                    ("c", "Usuwa konta użytkowników", False),
                    ("d", "Czyści logi SSH", False),
                ],
            },
            {
                "text": "Co należy zrobić po zwolnieniu miejsca?",
                "answers": [
                    ("a", "Ponownie wykonać pomiary i potwierdzić efekt", True),
                    ("b", "Założyć, że problem zniknął bez sprawdzania", False),
                    ("c", "Usunąć jeszcze kilka losowych katalogów", False),
                    ("d", "Wyłączyć systemd", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Co pokazuje df?", "answer": "Wykorzystanie całych systemów plików."},
        {"question": "Co robi df -h?", "answer": "Pokazuje rozmiary w czytelnych jednostkach, takich jak MB i GB."},
        {"question": "Co pokazuje df -i?", "answer": "Wykorzystanie inode w systemach plików."},
        {"question": "Czym jest inode?", "answer": "Strukturą przechowującą metadane obiektu w systemie plików."},
        {"question": "Czy mogą skończyć się inode mimo wolnych bajtów?", "answer": "Tak, szczególnie przy bardzo dużej liczbie małych plików."},
        {"question": "Co pokazuje du?", "answer": "Miejsce zajmowane przez wskazane pliki i katalogi."},
        {"question": "Jaka jest różnica między df i du?", "answer": "df mierzy system plików, a du sumuje widoczne dane w wybranej ścieżce."},
        {"question": "Co oznacza -h w du?", "answer": "Wyświetlanie rozmiarów w czytelnych jednostkach."},
        {"question": "Co oznacza -d 1 w du?", "answer": "Ograniczenie raportu do jednego poziomu katalogów."},
        {"question": "Co oznacza -x w du?", "answer": "Pozostanie w obrębie jednego systemu plików."},
        {"question": "Od czego zacząć problem pełnego dysku?", "answer": "Od df -h i wskazania zapełnionego systemu plików."},
        {"question": "Co sprawdzić po df -h?", "answer": "Największe katalogi przez odpowiednio ograniczone du."},
        {"question": "Co robi sort -h?", "answer": "Sortuje wartości rozmiarów zapisane w czytelnych jednostkach."},
        {"question": "Po co używać tail po sort -h?", "answer": "Aby zobaczyć końcowe, czyli zwykle największe pozycje."},
        {"question": "Czym jest cache DNF?", "answer": "Pobranymi pakietami i metadanymi, które DNF może odtworzyć."},
        {"question": "Co robi dnf clean packages?", "answer": "Usuwa pobrane pliki pakietów z cache."},
        {"question": "Co robi dnf clean all?", "answer": "Czyści pakiety i metadane cache DNF."},
        {"question": "Co pokazuje journalctl --disk-usage?", "answer": "Łączne miejsce zajmowane przez pliki journala."},
        {"question": "Co robi journalctl --vacuum-time=14d?", "answer": "Usuwa zarchiwizowane wpisy journala starsze niż 14 dni."},
        {"question": "Co robi journalctl --vacuum-size=500M?", "answer": "Ogranicza rozmiar zarchiwizowanego journala do około 500 MB."},
        {"question": "Czy należy ręcznie usuwać aktywne pliki logów?", "answer": "Nie. Lepiej użyć rotacji lub narzędzia zarządzającego journalem."},
        {"question": "Dlaczego /var wymaga ostrożności?", "answer": "Może zawierać logi, cache, bazy danych i ważne dane usług."},
        {"question": "Czy cache i dane aplikacji są tym samym?", "answer": "Nie. Cache zwykle można odtworzyć, a dane aplikacji mogą być unikalne."},
        {"question": "Co zrobić przed usunięciem dużego pliku?", "answer": "Ustalić właściciela, przeznaczenie, aktywne użycie i możliwość bezpiecznego odtworzenia."},
        {"question": "Jak zakończyć porządkowanie systemu?", "answer": "Powtórzyć df, du lub pomiar journala i udokumentować rezultat."},
    ],
}
