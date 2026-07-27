UVICORN_APPLICATION = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Uruchamianie aplikacji przez Uvicorn",
        "level": "Średnio zaawansowany",
        "duration": "50 min",
        "description": (
            "Uruchomisz aplikację ASGI przez Uvicorn na lokalnym porcie serwera i przeprowadzisz podstawową "
            "diagnostykę odpowiedzi HTTP, nasłuchującego portu oraz procesu."
        ),
        "theory": (
            "ASGI jest interfejsem łączącym asynchroniczną aplikację Python z serwerem obsługującym ruch "
            "sieciowy. Uvicorn jest serwerem ASGI, który importuje aplikację i nasłuchuje na wskazanym adresie "
            "oraz porcie. Zapis <code>app.main:app</code> oznacza moduł <code>app.main</code> i obiekt "
            "<code>app</code>. W układzie z Nginxem Uvicorn może nasłuchiwać na "
            "<code>127.0.0.1:8000</code>. Adres pętli zwrotnej jest dostępny lokalnie na serwerze, dzięki "
            "czemu publiczny ruch trafia najpierw do reverse proxy. Opcje <code>--host</code> i "
            "<code>--port</code> określają miejsce nasłuchu. Tryb <code>--reload</code> obserwuje pliki i "
            "restartuje proces podczas pracy programistycznej, lecz nie jest przeznaczony do produkcji. Po "
            "uruchomieniu trzeba niezależnie sprawdzić odpowiedź przez <code>curl</code>, port przez "
            "<code>ss</code> oraz proces przez <code>ps</code>. Komunikat o zajętym adresie zwykle oznacza, "
            "że inny proces już używa tego samego połączenia adresu i portu."
        ),
        "commands": [
            {
                "command": "/opt/example-app/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000",
                "description": "Uruchamia aplikację na lokalnym adresie i porcie 8000.",
                "example": "$ /opt/example-app/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000",
            },
            {
                "command": "curl -i http://127.0.0.1:8000/",
                "description": "Wysyła lokalne żądanie i pokazuje nagłówki oraz treść odpowiedzi.",
                "example": "$ curl -i http://127.0.0.1:8000/",
            },
            {
                "command": "curl -fsS http://127.0.0.1:8000/health",
                "description": "Sprawdza przykładowy endpoint health i zwraca błąd przy nieudanej odpowiedzi.",
                "example": "$ curl -fsS http://127.0.0.1:8000/health",
            },
            {
                "command": "ss -lntp | grep ':8000'",
                "description": "Pokazuje proces nasłuchujący na porcie TCP 8000.",
                "example": "$ ss -lntp | grep ':8000'",
            },
            {
                "command": "ps -ef | grep '[u]vicorn'",
                "description": "Wyszukuje uruchomione procesy Uvicorna bez dopasowania samego grep.",
                "example": "$ ps -ef | grep '[u]vicorn'",
            },
            {
                "command": "sudo lsof -iTCP:8000 -sTCP:LISTEN",
                "description": "Pomaga ustalić, który proces zajmuje port 8000, jeśli lsof jest dostępny.",
                "example": "$ sudo lsof -iTCP:8000 -sTCP:LISTEN",
            },
        ],
        "practice_task": (
            "Z katalogu <code>/opt/example-app</code> uruchom laboratoryjną aplikację poleceniem "
            "<code>/opt/example-app/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000</code>. "
            "W drugiej sesji wykonaj <code>curl -i http://127.0.0.1:8000/</code>, sprawdź port przez "
            "<code>ss -lntp</code> i odszukaj proces przez <code>ps</code>. Następnie spróbuj uruchomić drugą "
            "instancję na tym samym porcie, odczytaj błąd i uruchom ją na innym porcie. Zakończ procesy "
            "laboratoryjne po ćwiczeniu."
        ),
        "common_mistakes": [
            "Pomylenie ścieżki pliku z zapisem moduł:obiekt wymaganym przez Uvicorn.",
            "Uruchamianie polecenia z katalogu, z którego moduł aplikacji nie jest importowalny.",
            "Używanie --reload w środowisku produkcyjnym.",
            "Wystawianie Uvicorna publicznie mimo planowanego użycia Nginxa jako reverse proxy.",
            "Restartowanie procesu bez sprawdzenia, kto już zajmuje port.",
            "Sprawdzanie wyłącznie procesu bez testu rzeczywistej odpowiedzi HTTP.",
        ],
        "summary": (
            "Uvicorn uruchamia aplikację ASGI wskazaną zapisem <code>moduł:obiekt</code>. W typowym wdrożeniu "
            "z Nginxem nasłuchuje lokalnie na <code>127.0.0.1:8000</code>. Poprawne działanie należy sprawdzić "
            "na trzech poziomach: proces istnieje, port nasłuchuje i aplikacja odpowiada przez HTTP. "
            "<code>--reload</code> jest wygodny lokalnie, ale nie powinien być częścią uruchomienia produkcyjnego."
        ),
    },
    "quiz": {
        "title": "Quiz: uruchamianie aplikacji przez Uvicorn",
        "description": "Sprawdź, czy rozumiesz ASGI, zapis moduł:obiekt i diagnostykę lokalnego procesu.",
        "questions": [
            {
                "text": "Jaką rolę pełni Uvicorn?",
                "answers": [
                    ("a", "Jest serwerem ASGI uruchamiającym aplikację Python", True),
                    ("b", "Jest publicznym resolverem DNS", False),
                    ("c", "Jest menedżerem pakietów systemowych", False),
                    ("d", "Jest formatem pliku jednostki systemd", False),
                ],
            },
            {
                "text": "Co wskazuje część po dwukropku w app.main:app?",
                "answers": [
                    ("a", "Obiekt aplikacji o nazwie app", True),
                    ("b", "Port aplikacji", False),
                    ("c", "Użytkownika systemowego", False),
                    ("d", "Katalog środowiska wirtualnego", False),
                ],
            },
            {
                "text": "Dlaczego Uvicorn może nasłuchiwać na 127.0.0.1?",
                "answers": [
                    ("a", "Bo publiczny ruch ma przekazywać do niego lokalny Nginx", True),
                    ("b", "Bo ten adres jest publicznym adresem każdego VPS", False),
                    ("c", "Bo 127.0.0.1 automatycznie tworzy rekord A", False),
                    ("d", "Bo tylko ten adres obsługuje ASGI", False),
                ],
            },
            {
                "text": "Które polecenie testuje odpowiedź aplikacji na lokalnym porcie?",
                "answers": [
                    ("a", "curl -i http://127.0.0.1:8000/", True),
                    ("b", "python3 --version", False),
                    ("c", "systemctl daemon-reload", False),
                    ("d", "dig app.example.com", False),
                ],
            },
            {
                "text": "Dlaczego nie używać --reload w produkcji?",
                "answers": [
                    ("a", "Jest to mechanizm deweloperski obserwujący pliki i restartujący proces", True),
                    ("b", "Wyłącza on wszystkie endpointy HTTP", False),
                    ("c", "Usuwa środowisko wirtualne", False),
                    ("d", "Zmienia rekord DNS aplikacji", False),
                ],
            },
            {
                "text": "Co najczęściej oznacza błąd zajętego portu 8000?",
                "answers": [
                    ("a", "Inny proces już nasłuchuje na tym adresie i porcie", True),
                    ("b", "Brakuje rekordu CNAME", False),
                    ("c", "Plik requirements.txt jest pusty", False),
                    ("d", "Nginx nie ma certyfikatu HTTPS", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest ASGI?", "answer": "Interfejsem między asynchroniczną aplikacją Python a serwerem obsługującym ruch."},
        {"question": "Czym jest Uvicorn?", "answer": "Serwerem ASGI dla aplikacji Python."},
        {"question": "Co oznacza zapis moduł:obiekt?", "answer": "Wskazuje moduł do importu i obiekt aplikacji znajdujący się w tym module."},
        {"question": "Co oznacza app.main:app?", "answer": "Moduł app.main i obiekt app."},
        {"question": "Do czego służy --host?", "answer": "Określa adres, na którym Uvicorn ma nasłuchiwać."},
        {"question": "Do czego służy --port?", "answer": "Określa numer portu TCP serwera aplikacji."},
        {"question": "Czym jest 127.0.0.1?", "answer": "Adresem pętli zwrotnej dostępnym lokalnie na danym hoście."},
        {"question": "Dlaczego używać 127.0.0.1 z Nginxem?", "answer": "Aby Uvicorn przyjmował połączenia lokalne przekazane przez reverse proxy."},
        {"question": "Jak uruchomić Uvicorn z venv?", "answer": "Wywołać /opt/example-app/venv/bin/uvicorn z punktem wejścia i opcjami."},
        {"question": "Jak szybko sprawdzić odpowiedź HTTP?", "answer": "Poleceniem curl skierowanym do lokalnego adresu i portu."},
        {"question": "Co pokazuje curl -i?", "answer": "Nagłówki odpowiedzi HTTP oraz jej treść."},
        {"question": "Co daje curl -f?", "answer": "Powoduje błąd polecenia przy odpowiedzi HTTP oznaczającej niepowodzenie."},
        {"question": "Jak sprawdzić port 8000?", "answer": "Poleceniem ss -lntp z filtrem dla portu 8000."},
        {"question": "Co oznacza LISTEN przy porcie?", "answer": "Proces oczekuje na przychodzące połączenia."},
        {"question": "Jak znaleźć proces Uvicorna?", "answer": "Na przykład poleceniem ps -ef z odpowiednim filtrem."},
        {"question": "Co oznacza zajęty port?", "answer": "Inny proces jest już powiązany z tym adresem i portem."},
        {"question": "Jak rozwiązać konflikt portu?", "answer": "Zidentyfikować istniejący proces albo świadomie wybrać inny wolny port."},
        {"question": "Do czego służy --reload?", "answer": "Do automatycznego przeładowywania aplikacji po zmianach podczas developmentu."},
        {"question": "Czy --reload jest ustawieniem produkcyjnym?", "answer": "Nie, jest przeznaczone do pracy programistycznej."},
        {"question": "Co sprawdzić oprócz istnienia procesu?", "answer": "Nasłuch portu i prawidłową odpowiedź HTTP."},
        {"question": "Dlaczego katalog roboczy ma znaczenie?", "answer": "Python musi móc zaimportować wskazany moduł aplikacji."},
        {"question": "Czy działający proces gwarantuje poprawną odpowiedź?", "answer": "Nie, aplikacja może działać jako proces, ale zwracać błędy."},
        {"question": "Czy otwarty port gwarantuje poprawną treść?", "answer": "Nie, trzeba jeszcze wykonać żądanie i sprawdzić odpowiedź."},
        {"question": "Jaki adres testować lokalnie?", "answer": "Na przykład http://127.0.0.1:8000/."},
        {"question": "Jaka jest podstawowa kolejność diagnostyki?", "answer": "Sprawdzić proces, nasłuchujący port, odpowiedź curl i komunikaty błędów."},
    ],
}
