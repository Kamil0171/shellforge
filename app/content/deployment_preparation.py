DEPLOYMENT_PREPARATION = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Przygotowanie aplikacji do wdrożenia",
        "level": "Średnio zaawansowany",
        "duration": "55 min",
        "description": (
            "Przygotujesz aplikację i serwer do powtarzalnego wdrożenia, sprawdzając kod, zależności, "
            "punkt wejścia, zasoby systemu oraz port przeznaczony dla aplikacji."
        ),
        "theory": (
            "Środowisko lokalne służy do wygodnego tworzenia i testowania kodu, natomiast środowisko "
            "produkcyjne powinno działać przewidywalnie, bez trybu debugowania i automatycznego przeładowania. "
            "Przed wdrożeniem trzeba znać punkt wejścia aplikacji ASGI, na przykład "
            "<code>app.main:app</code>, gdzie część przed dwukropkiem wskazuje moduł Pythona, a część po nim "
            "obiekt aplikacji. Zależności powinny być zapisane w <code>requirements.txt</code>, aby dało się "
            "odtworzyć środowisko na serwerze. Praktyczny układ rozdziela kod w "
            "<code>/opt/example-app</code>, konfigurację zawierającą wartości środowiskowe w "
            "<code>/opt/example-app/.env</code> oraz środowisko wirtualne w "
            "<code>/opt/example-app/venv</code>. Plik <code>.env</code> nie powinien trafiać do publicznego "
            "repozytorium. Aplikację warto uruchamiać jako dedykowany użytkownik systemowy z dostępem tylko do "
            "potrzebnych plików. Przed instalacją należy sprawdzić wersje Pythona i Gita, wolne miejsce, "
            "właściciela katalogu oraz to, czy planowany port, na przykład 8000, nie jest już zajęty. Taka "
            "checklista oddziela problemy aplikacji od braków w przygotowaniu serwera."
        ),
        "commands": [
            {
                "command": "python3 --version",
                "description": "Sprawdza wersję Pythona dostępną na serwerze.",
                "example": "$ python3 --version\nPython 3.11.9",
            },
            {
                "command": "git --version",
                "description": "Sprawdza, czy Git jest zainstalowany i pokazuje jego wersję.",
                "example": "$ git --version\ngit version 2.43.5",
            },
            {
                "command": "df -h /opt",
                "description": "Pokazuje wolne miejsce w systemie plików zawierającym katalog aplikacji.",
                "example": "$ df -h /opt",
            },
            {
                "command": "sudo ss -lntp | grep ':8000'",
                "description": "Sprawdza, czy port TCP 8000 jest już używany przez proces nasłuchujący.",
                "example": "$ sudo ss -lntp | grep ':8000'",
            },
            {
                "command": "sudo install -d -o example-app -g example-app /opt/example-app",
                "description": "Tworzy katalog aplikacji z odpowiednim właścicielem i grupą.",
                "example": "$ sudo install -d -o example-app -g example-app /opt/example-app",
            },
            {
                "command": "find /opt/example-app -maxdepth 2 -type f",
                "description": "Pomaga sprawdzić rozmieszczenie plików aplikacji przed uruchomieniem.",
                "example": "$ find /opt/example-app -maxdepth 2 -type f",
            },
        ],
        "practice_task": (
            "Przygotuj checklistę dla przykładowej aplikacji z punktem wejścia "
            "<code>app.main:app</code>. Sprawdź <code>python3 --version</code>, "
            "<code>git --version</code>, <code>df -h /opt</code> oraz dostępność portu 8000 przez "
            "<code>sudo ss -lntp | grep ':8000'</code>. Rozrysuj strukturę "
            "<code>/opt/example-app</code> z osobnymi miejscami na kod, <code>venv</code> i "
            "<code>.env</code>. Zapisz, który użytkownik ma uruchamiać proces i jakie pliki musi odczytywać. "
            "Nie wpisuj prawdziwych sekretów do pliku ćwiczeniowego."
        ),
        "common_mistakes": [
            "Włączanie w produkcji trybu debugowania lub automatycznego przeładowania kodu.",
            "Brak jednoznacznie określonego punktu wejścia aplikacji.",
            "Instalowanie zależności bez aktualnego pliku requirements.txt.",
            "Umieszczanie sekretów w repozytorium razem z kodem.",
            "Uruchamianie aplikacji jako root bez technicznej potrzeby.",
            "Pomijanie kontroli miejsca na dysku i zajętych portów.",
        ],
        "summary": (
            "Dobre wdrożenie zaczyna się przed uruchomieniem procesu. Trzeba znać punkt wejścia, zapisać "
            "zależności, rozdzielić kod, konfigurację i środowisko wirtualne oraz wybrać dedykowanego "
            "użytkownika i lokalny port. Kontrola wersji narzędzi, miejsca na dysku i portów pozwala wykryć "
            "problemy jeszcze przed instalacją aplikacji."
        ),
    },
    "quiz": {
        "title": "Quiz: przygotowanie aplikacji do wdrożenia",
        "description": "Sprawdź, czy potrafisz przygotować kod i serwer przed wdrożeniem.",
        "questions": [
            {
                "text": "Co oznacza zapis app.main:app?",
                "answers": [
                    ("a", "Moduł app.main i znajdujący się w nim obiekt app", True),
                    ("b", "Adres IP i numer portu aplikacji", False),
                    ("c", "Nazwę użytkownika i grupy systemowej", False),
                    ("d", "Ścieżkę do pliku z logami Nginxa", False),
                ],
            },
            {
                "text": "Po co utrzymywać plik requirements.txt?",
                "answers": [
                    ("a", "Aby można było odtworzyć zestaw zależności aplikacji", True),
                    ("b", "Aby otworzyć port w firewallu", False),
                    ("c", "Aby utworzyć rekord DNS", False),
                    ("d", "Aby zastąpić plik jednostki systemd", False),
                ],
            },
            {
                "text": "Który układ najlepiej rozdziela elementy wdrożenia?",
                "answers": [
                    ("a", "Kod, konfiguracja i środowisko wirtualne w wyraźnie określonych miejscach", True),
                    ("b", "Wszystkie pliki wraz z sekretami w publicznym repozytorium", False),
                    ("c", "Kod aplikacji zapisany w /tmp bez właściciela", False),
                    ("d", "Jedno globalne środowisko Python dla wszystkich aplikacji", False),
                ],
            },
            {
                "text": "Dlaczego warto użyć dedykowanego użytkownika systemowego?",
                "answers": [
                    ("a", "Aby ograniczyć uprawnienia procesu do potrzebnych zasobów", True),
                    ("b", "Aby aplikacja mogła zawsze działać jako root", False),
                    ("c", "Aby automatycznie skonfigurować DNS", False),
                    ("d", "Aby zastąpić środowisko wirtualne", False),
                ],
            },
            {
                "text": "Jak sprawdzić, czy port 8000 jest zajęty?",
                "answers": [
                    ("a", "Użyć ss do wyświetlenia nasłuchujących portów TCP", True),
                    ("b", "Uruchomić df -h /opt", False),
                    ("c", "Odczytać git --version", False),
                    ("d", "Wywołać python3 --version", False),
                ],
            },
            {
                "text": "Co należy zrobić z produkcyjnymi sekretami?",
                "answers": [
                    ("a", "Przechowywać je poza publicznym repozytorium i ograniczyć dostęp", True),
                    ("b", "Dodać je do requirements.txt", False),
                    ("c", "Wpisać je do nazwy jednostki systemd", False),
                    ("d", "Umieścić je w publicznym rekordzie DNS", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym różni się środowisko produkcyjne od lokalnego?", "answer": "Powinno działać przewidywalnie, bez narzędzi deweloperskich takich jak automatyczny reload."},
        {"question": "Czym jest punkt wejścia aplikacji?", "answer": "Wskazaniem modułu i obiektu, które serwer ma zaimportować i uruchomić."},
        {"question": "Co oznacza app.main:app?", "answer": "Moduł Pythona app.main oraz obiekt aplikacji o nazwie app."},
        {"question": "Po co jest requirements.txt?", "answer": "Opisuje zależności potrzebne do odtworzenia środowiska aplikacji."},
        {"question": "Gdzie może znajdować się kod przykładowej aplikacji?", "answer": "W neutralnej lokalizacji, na przykład /opt/example-app."},
        {"question": "Gdzie może znajdować się venv aplikacji?", "answer": "Na przykład w /opt/example-app/venv."},
        {"question": "Gdzie może znajdować się konfiguracja środowiskowa?", "answer": "Na przykład w /opt/example-app/.env z ograniczonym dostępem."},
        {"question": "Czy plik .env powinien trafić do publicznego repozytorium?", "answer": "Nie, może zawierać sekrety i konfigurację środowiska."},
        {"question": "Po co dedykowany użytkownik systemowy?", "answer": "Aby proces miał tylko uprawnienia potrzebne do działania aplikacji."},
        {"question": "Czy aplikacja powinna domyślnie działać jako root?", "answer": "Nie, należy użyć konta o ograniczonych uprawnieniach."},
        {"question": "Jak sprawdzić wersję Pythona?", "answer": "Poleceniem python3 --version."},
        {"question": "Jak sprawdzić wersję Gita?", "answer": "Poleceniem git --version."},
        {"question": "Jak sprawdzić wolne miejsce dla /opt?", "answer": "Poleceniem df -h /opt."},
        {"question": "Jak sprawdzić nasłuchujące porty TCP?", "answer": "Poleceniem ss -lntp, zwykle z uprawnieniami pozwalającymi zobaczyć procesy."},
        {"question": "Jaki port może obsługiwać lokalnie przykładowa aplikacja?", "answer": "Na przykład port 8000."},
        {"question": "Co oznacza zajęty port?", "answer": "Inny proces już nasłuchuje na danym adresie i numerze portu."},
        {"question": "Dlaczego sprawdzać strukturę katalogów?", "answer": "Aby upewnić się, że kod, konfiguracja i venv są we właściwych miejscach."},
        {"question": "Kto powinien być właścicielem katalogu aplikacji?", "answer": "Konto przeznaczone do wdrażania lub uruchamiania aplikacji, zgodnie z przyjętym modelem uprawnień."},
        {"question": "Co należy ustalić przed wdrożeniem?", "answer": "Punkt wejścia, zależności, użytkownika, katalog roboczy, konfigurację i port."},
        {"question": "Czy debugowanie powinno być aktywne w produkcji?", "answer": "Nie, może ujawniać informacje i zmniejszać przewidywalność działania."},
        {"question": "Dlaczego warto stosować checklistę?", "answer": "Zmniejsza ryzyko pominięcia podstawowych zależności i zasobów."},
        {"question": "Co sprawdza find z opcją -maxdepth?", "answer": "Wyświetla pliki w ograniczonej głębokości struktury katalogów."},
        {"question": "Co powinno być odtwarzalne?", "answer": "Środowisko Pythona i zestaw zależności aplikacji."},
        {"question": "Dlaczego oddzielać konfigurację od kodu?", "answer": "Ta sama wersja kodu może wtedy działać z różną konfiguracją w różnych środowiskach."},
        {"question": "Jaki jest cel kontroli przed wdrożeniem?", "answer": "Wykryć braki serwera i konfiguracji przed uruchomieniem aplikacji."},
    ],
}
