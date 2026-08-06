GIT_APPLICATION_UPDATE = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Aktualizacja aplikacji przez Git",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": (
            "Przeprowadzisz ręczną, kontrolowaną aktualizację aplikacji z brancha main, a następnie "
            "zrestartujesz usługę i wykonasz podstawowy smoke test."
        ),
        "theory": (
            "Repozytorium Git może być źródłem wersji kodu wdrażanej na serwerze. Przed aktualizacją trzeba "
            "wejść do <code>/opt/example-app/app</code>, potwierdzić branch <code>main</code> i sprawdzić, czy "
            "working tree jest czyste. Lokalne zmiany na serwerze utrudniają ustalenie rzeczywistej wersji i "
            "mogą wejść w konflikt z kodem z repozytorium, dlatego plików produkcyjnych nie należy ręcznie "
            "edytować. <code>git fetch origin</code> pobiera informacje i obiekty z repozytorium zdalnego, "
            "ale sam nie przesuwa bieżącego brancha. <code>git pull</code> pobiera zmiany i integruje je z "
            "bieżącym branchem. W kontrolowanym deploymencie warto użyć "
            "<code>git pull --ff-only origin main</code>: polecenie powiedzie się tylko wtedy, gdy branch można "
            "przesunąć bez tworzenia merge commita. Nie rozwiązuje to wszystkich ryzyk, ale zatrzymuje "
            "wdrożenie przy rozbieżnej historii zamiast samodzielnie scalać kod na serwerze. Operacje Git w "
            "katalogu aplikacji powinien wykonywać właściciel repozytorium, zwykle użytkownik usługi lub "
            "dedykowane konto wdrożeniowe, a nie przypadkowo root. Przed pobraniem warto zapisać bieżący commit, "
            "a po nim sprawdzić <code>git log -1 --oneline</code>. Jeżeli zmienił się "
            "<code>requirements.txt</code> lub dokumentacja wydania tego wymaga, należy zainstalować zależności "
            "przez interpreter z <code>/opt/example-app/venv</code>. Nie trzeba wykonywać tej operacji przy "
            "każdym wdrożeniu bez potrzeby. Następnie restartuje się <code>example-app.service</code>, sprawdza "
            "status i logi oraz wywołuje lokalny endpoint na <code>127.0.0.1:8000</code>. "
            "<code>git reset --hard</code> nie jest standardową procedurą aktualizacji: może bezpowrotnie usunąć "
            "lokalne zmiany i ukryć przyczynę rozbieżności. W tej lekcji wdrożenie pozostaje ręczne; automatyczne "
            "CI/CD wymaga osobnego projektu procesu."
        ),
        "commands": [
            {
                "command": "cd /opt/example-app/app && git branch --show-current && git status --short",
                "description": "Potwierdza katalog, branch i czystość working tree przed wdrożeniem.",
                "example": "$ cd /opt/example-app/app\n$ git branch --show-current\nmain\n$ git status --short",
            },
            {
                "command": "git fetch origin",
                "description": "Pobiera aktualne dane z origin bez zmiany bieżącego brancha.",
                "example": "$ git fetch origin",
            },
            {
                "command": "git pull --ff-only origin main",
                "description": "Aktualizuje main tylko wtedy, gdy możliwy jest fast-forward.",
                "example": "$ git pull --ff-only origin main",
            },
            {
                "command": "git log -1 --oneline",
                "description": "Pokazuje commit znajdujący się aktualnie na szczycie wdrożonego brancha.",
                "example": "$ git log -1 --oneline\n7ab12cd Prepare release",
            },
            {
                "command": "/opt/example-app/venv/bin/python -m pip install -r requirements.txt",
                "description": "Aktualizuje zależności, gdy zmienił się requirements.txt lub wymaga tego wydanie.",
                "example": "$ /opt/example-app/venv/bin/python -m pip install -r requirements.txt",
            },
            {
                "command": "sudo systemctl restart example-app && sudo systemctl status example-app --no-pager -l",
                "description": "Restartuje usługę i natychmiast pokazuje jej szczegółowy stan.",
                "example": "$ sudo systemctl restart example-app\n$ sudo systemctl status example-app --no-pager -l",
            },
            {
                "command": "curl -sS -o /dev/null -w \"%{http_code}\\n\" http://127.0.0.1:8000/",
                "description": "Wykonuje prosty lokalny smoke test i wypisuje kod HTTP.",
                "example": "$ curl -sS -o /dev/null -w \"%{http_code}\\n\" http://127.0.0.1:8000/\n200",
            },
        ],
        "practice_task": (
            "Przygotuj ręczną aktualizację repozytorium w <code>/opt/example-app/app</code>. Jako użytkownik "
            "właściwy dla repozytorium sprawdź branch i czyste working tree, zapisz bieżący commit, wykonaj "
            "<code>git fetch origin</code>, przejrzyj zmiany i użyj "
            "<code>git pull --ff-only origin main</code>. Sprawdź najnowszy commit. Zaktualizuj zależności "
            "tylko wtedy, gdy zmienił się requirements.txt, potem zrestartuj usługę, oceń jej status i wykonaj "
            "test HTTP na 127.0.0.1:8000. Zapisz wyniki kolejnych kroków w notatce wdrożeniowej."
        ),
        "common_mistakes": [
            "Wykonywanie pull bez sprawdzenia brancha i lokalnych zmian.",
            "Ręczna edycja kodu na serwerze produkcyjnym.",
            "Używanie zwykłego pull, który może utworzyć nieplanowany merge commit.",
            "Uruchamianie Git jako root mimo innego właściciela repozytorium.",
            "Instalowanie zależności globalnie zamiast w venv aplikacji.",
            "Kończenie wdrożenia po restarcie bez statusu, logów i smoke testu.",
            "Stosowanie git reset --hard do maskowania rozbieżności na serwerze.",
        ],
        "summary": (
            "Kontrolowana aktualizacja zaczyna się od właściwego brancha, czystego working tree i zapisu "
            "bieżącego commita. Fetch pobiera stan zdalny bez integracji, a pull --ff-only zatrzymuje proces "
            "przy rozbieżnej historii. Po pobraniu zmian aktualizuje się zależności tylko w razie potrzeby, "
            "restartuje usługę i weryfikuje commit, status, logi oraz lokalny endpoint."
        ),
    },
    "quiz": {
        "title": "Quiz: aktualizacja aplikacji przez Git",
        "description": "Sprawdź zasady kontrolowanego ręcznego deploymentu przez Git.",
        "questions": [
            {
                "text": "Co sprawdzić przed pobraniem zmian na serwerze?",
                "answers": [
                    ("a", "Bieżący branch i czystość working tree", True),
                    ("b", "Wyłącznie rozmiar certyfikatu", False),
                    ("c", "Kolor terminala", False),
                    ("d", "Czy działa automatyczne CI/CD", False),
                ],
            },
            {
                "text": "Czym fetch różni się od pull?",
                "answers": [
                    ("a", "Fetch pobiera dane bez integracji, a pull także integruje je z branchem", True),
                    ("b", "Fetch usuwa repozytorium", False),
                    ("c", "Pull wyłącznie pokazuje log", False),
                    ("d", "Nie ma między nimi różnicy", False),
                ],
            },
            {
                "text": "Dlaczego stosować pull --ff-only podczas wdrożenia?",
                "answers": [
                    ("a", "Zatrzymuje aktualizację, gdy wymagałaby nieplanowanego scalenia", True),
                    ("b", "Usuwa wszystkie lokalne pliki", False),
                    ("c", "Automatycznie naprawia testy", False),
                    ("d", "Zmienia właściciela repozytorium", False),
                ],
            },
            {
                "text": "Kiedy aktualizować zależności z requirements.txt?",
                "answers": [
                    ("a", "Gdy plik się zmienił lub wymagają tego zmiany aplikacji", True),
                    ("b", "Zawsze po każdym wyświetleniu statusu", False),
                    ("c", "Dopiero po usunięciu venv", False),
                    ("d", "Nigdy na serwerze", False),
                ],
            },
            {
                "text": "Kto powinien wykonywać Git w katalogu aplikacji?",
                "answers": [
                    ("a", "Właściciel repozytorium lub dedykowany użytkownik wdrożeniowy", True),
                    ("b", "Zawsze anonimowy użytkownik", False),
                    ("c", "Każdy użytkownik przez chmod 777", False),
                    ("d", "Proces Nginxa przez przeglądarkę", False),
                ],
            },
            {
                "text": "Co należy zrobić po restarcie usługi?",
                "answers": [
                    ("a", "Sprawdzić status, logi i wykonać smoke test", True),
                    ("b", "Założyć, że wdrożenie się udało", False),
                    ("c", "Usunąć poprzedni commit", False),
                    ("d", "Wyłączyć lokalny endpoint", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Po co sprawdzać branch przed wdrożeniem?", "answer": "Aby aktualizować zamierzoną linię kodu, na przykład main."},
        {"question": "Co oznacza czyste working tree?", "answer": "Brak niezapisanych lokalnych zmian śledzonych przez Git."},
        {"question": "Dlaczego lokalne zmiany na serwerze są ryzykowne?", "answer": "Utrudniają odtworzenie wersji i mogą kolidować z repozytorium."},
        {"question": "Co robi git fetch origin?", "answer": "Pobiera zdalne obiekty i referencje bez integracji z bieżącym branchem."},
        {"question": "Co robi git pull?", "answer": "Pobiera zmiany i integruje je z bieżącym branchem."},
        {"question": "Co oznacza --ff-only?", "answer": "Zezwala wyłącznie na przesunięcie brancha bez tworzenia merge commita."},
        {"question": "Co się stanie przy rozbieżnej historii i --ff-only?", "answer": "Polecenie zakończy się błędem i zatrzyma aktualizację."},
        {"question": "Po co zapisać commit przed wdrożeniem?", "answer": "Aby znać dokładną wersję wyjściową i punkt możliwego rollbacku."},
        {"question": "Co pokazuje git log -1 --oneline?", "answer": "Skrócony identyfikator i opis bieżącego commita."},
        {"question": "Kto powinien uruchamiać Git?", "answer": "Użytkownik będący właścicielem repozytorium lub dedykowane konto wdrożeniowe."},
        {"question": "Dlaczego nie edytować kodu ręcznie na produkcji?", "answer": "Serwer przestaje wtedy odpowiadać jednoznacznej wersji z repozytorium."},
        {"question": "Kiedy uruchomić pip install?", "answer": "Gdy zmieniły się wymagania lub wydanie wymaga nowych zależności."},
        {"question": "Którego Pythona użyć do instalacji?", "answer": "Interpretera z /opt/example-app/venv."},
        {"question": "Po co restartować usługę?", "answer": "Aby uruchomić nowy proces z aktualnym kodem i konfiguracją."},
        {"question": "Co sprawdza systemctl status?", "answer": "Stan jednostki i ostatnie komunikaty związane z uruchomieniem."},
        {"question": "Czym jest smoke test?", "answer": "Krótkim testem potwierdzającym, że kluczowy endpoint odpowiada."},
        {"question": "Dlaczego testować 127.0.0.1:8000?", "answer": "Pozwala sprawdzić aplikację bez warstwy Nginxa i publicznej sieci."},
        {"question": "Czy sam restart potwierdza sukces?", "answer": "Nie, potrzebne są status, logi i test odpowiedzi."},
        {"question": "Dlaczego git reset --hard jest ryzykowny?", "answer": "Może bezpowrotnie usunąć lokalne zmiany i ukryć rozbieżność."},
        {"question": "Czy fetch zmienia pliki robocze?", "answer": "Nie, sam fetch nie aktualizuje bieżącego brancha."},
        {"question": "Czy ta procedura jest CI/CD?", "answer": "Nie, to ręczny i kontrolowany deployment."},
        {"question": "Co zrobić, gdy --ff-only odmawia aktualizacji?", "answer": "Zatrzymać wdrożenie i wyjaśnić rozbieżność poza produkcyjnym serwerem."},
        {"question": "Po co używać status --short?", "answer": "Daje zwięzły widok lokalnych zmian przed wdrożeniem."},
        {"question": "Co zwraca curl z %{http_code}?", "answer": "Kod odpowiedzi HTTP bez pobierania treści do terminala."},
        {"question": "Co dokumentować po aktualizacji?", "answer": "Commit, czas, wykonane kroki, wyniki testów i ewentualne problemy."},
    ],
}
