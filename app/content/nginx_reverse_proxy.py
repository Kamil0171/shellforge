NGINX_REVERSE_PROXY = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Nginx jako reverse proxy",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": (
            "Skonfigurujesz Nginx jako reverse proxy przekazujące żądania HTTP do lokalnego Uvicorna oraz "
            "nauczysz się rozróżniać błędy proxy, serwera ASGI i samej aplikacji."
        ),
        "theory": (
            "Reverse proxy przyjmuje żądania klientów i przekazuje je do serwera aplikacji. W tym układzie "
            "Nginx nasłuchuje publicznie na porcie 80, a Uvicorn tylko lokalnie na "
            "<code>127.0.0.1:8000</code>. Blok <code>server</code> wybiera port przez <code>listen 80</code> "
            "i domenę przez <code>server_name app.example.com</code>. W <code>location /</code> dyrektywa "
            "<code>proxy_pass http://127.0.0.1:8000</code> wskazuje upstream. Nagłówki przekazywane przez "
            "<code>proxy_set_header</code> zachowują nazwę hosta, adres klienta i oryginalny schemat: "
            "<code>Host</code>, <code>X-Real-IP</code>, <code>X-Forwarded-For</code> oraz "
            "<code>X-Forwarded-Proto</code>. Przed przeładowaniem konfigurację sprawdza się przez "
            "<code>nginx -t</code>; dopiero poprawny wynik uzasadnia <code>systemctl reload nginx</code>. "
            "Błąd 502 Bad Gateway zwykle oznacza, że Nginx nie może uzyskać poprawnej odpowiedzi od upstreamu. "
            "Najpierw trzeba więc wywołać Uvicorna lokalnym curl, potem sprawdzić nasłuch i usługę, a następnie "
            "logi Nginxa. Kod 500 zwrócony zarówno lokalnie, jak i przez Nginx częściej wskazuje błąd aplikacji. "
            "Ta lekcja świadomie pozostaje przy HTTP; HTTPS jest osobnym etapem."
        ),
        "commands": [
            {
                "command": "/etc/nginx/conf.d/example-app.conf",
                "description": "Przykładowy blok server przekazujący żądania HTTP do lokalnego Uvicorna.",
                "example": (
                    "server {\n"
                    "    listen 80;\n"
                    "    server_name app.example.com;\n"
                    "\n"
                    "    location / {\n"
                    "        proxy_pass http://127.0.0.1:8000;\n"
                    "        proxy_set_header Host $host;\n"
                    "        proxy_set_header X-Real-IP $remote_addr;\n"
                    "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
                    "        proxy_set_header X-Forwarded-Proto $scheme;\n"
                    "    }\n"
                    "}"
                ),
            },
            {
                "command": "sudo nginx -t",
                "description": "Sprawdza składnię i poprawność całej konfiguracji Nginxa.",
                "example": "$ sudo nginx -t\nsyntax is ok\ntest is successful",
            },
            {
                "command": "sudo systemctl reload nginx",
                "description": "Wczytuje poprawną konfigurację bez pełnego restartu usługi.",
                "example": "$ sudo systemctl reload nginx",
            },
            {
                "command": "curl -i http://127.0.0.1:8000/",
                "description": "Testuje Uvicorna i aplikację z pominięciem Nginxa.",
                "example": "$ curl -i http://127.0.0.1:8000/",
            },
            {
                "command": "curl -i -H 'Host: app.example.com' http://127.0.0.1/",
                "description": "Testuje lokalny wybór bloku server na podstawie nagłówka Host.",
                "example": "$ curl -i -H 'Host: app.example.com' http://127.0.0.1/",
            },
            {
                "command": "systemctl status nginx",
                "description": "Pokazuje stan procesu Nginxa i ostatnie komunikaty usługi.",
                "example": "$ systemctl status nginx",
            },
            {
                "command": "sudo tail -n 50 /var/log/nginx/error.log",
                "description": "Pokazuje ostatnie błędy Nginxa, w tym problemy z połączeniem do upstreamu.",
                "example": "$ sudo tail -n 50 /var/log/nginx/error.log",
            },
        ],
        "practice_task": (
            "Przygotuj laboratoryjny blok <code>server</code> z "
            "<code>listen 80</code>, <code>server_name app.example.com</code> i "
            "<code>location /</code>. Ustaw <code>proxy_pass http://127.0.0.1:8000</code> oraz nagłówki "
            "<code>Host</code>, <code>X-Real-IP</code>, <code>X-Forwarded-For</code> i "
            "<code>X-Forwarded-Proto</code>. Uruchom lokalną aplikację, wykonaj <code>nginx -t</code>, a po "
            "poprawnym teście przeładuj Nginx. Porównaj curl bezpośrednio do portu 8000 z żądaniem przez port "
            "80. Na końcu zatrzymaj laboratoryjnego Uvicorna, zaobserwuj 502 i potwierdź przyczynę w logu."
        ),
        "common_mistakes": [
            "Przeładowanie Nginxa bez wcześniejszego wykonania nginx -t.",
            "Wskazanie w proxy_pass błędnego adresu lub portu Uvicorna.",
            "Brak zgodności server_name z domeną wysyłaną w nagłówku Host.",
            "Pomijanie nagłówków przekazujących host, adres klienta i schemat.",
            "Traktowanie każdego błędu HTTP jako problemu Nginxa.",
            "Szukanie przyczyny 502 bez sprawdzenia lokalnej odpowiedzi Uvicorna.",
            "Dodawanie konfiguracji HTTPS w etapie przeznaczonym wyłącznie dla HTTP.",
        ],
        "summary": (
            "Nginx odbiera publiczne żądania HTTP i przekazuje je do lokalnego Uvicorna przez "
            "<code>proxy_pass</code>. <code>server_name</code> wybiera domenę, a "
            "<code>proxy_set_header</code> zachowuje ważne informacje o żądaniu. Każdą zmianę należy najpierw "
            "sprawdzić przez <code>nginx -t</code>. Diagnostyka idzie warstwami: lokalna aplikacja i Uvicorn, "
            "połączenie Nginxa z upstreamem, a dopiero potem publiczna domena."
        ),
    },
    "quiz": {
        "title": "Quiz: Nginx jako reverse proxy",
        "description": "Sprawdź konfigurację proxy i metody rozróżniania problemów poszczególnych warstw.",
        "questions": [
            {
                "text": "Czym jest reverse proxy?",
                "answers": [
                    ("a", "Serwerem przyjmującym żądania i przekazującym je do aplikacji", True),
                    ("b", "Środowiskiem wirtualnym Pythona", False),
                    ("c", "Typem rekordu DNS wskazującym IPv6", False),
                    ("d", "Poleceniem do instalacji pakietów", False),
                ],
            },
            {
                "text": "Co robi proxy_pass http://127.0.0.1:8000?",
                "answers": [
                    ("a", "Przekazuje żądanie do lokalnego serwera aplikacji", True),
                    ("b", "Tworzy publiczny rekord A", False),
                    ("c", "Uruchamia Uvicorna w venv", False),
                    ("d", "Włącza HTTPS", False),
                ],
            },
            {
                "text": "Po co przekazywać nagłówek Host?",
                "answers": [
                    ("a", "Aby aplikacja otrzymała nazwę hosta używaną przez klienta", True),
                    ("b", "Aby zmienić użytkownika procesu", False),
                    ("c", "Aby utworzyć plik requirements.txt", False),
                    ("d", "Aby sprawdzić wolne miejsce na dysku", False),
                ],
            },
            {
                "text": "Co wykonać przed systemctl reload nginx?",
                "answers": [
                    ("a", "sudo nginx -t", True),
                    ("b", "python -m pip check", False),
                    ("c", "systemctl daemon-reload dla każdej odpowiedzi", False),
                    ("d", "dig +trace bez wskazania domeny", False),
                ],
            },
            {
                "text": "Od czego zacząć diagnostykę błędu 502?",
                "answers": [
                    ("a", "Od sprawdzenia lokalnej odpowiedzi upstreamu na 127.0.0.1:8000", True),
                    ("b", "Od wymiany rekordu A na CNAME", False),
                    ("c", "Od usunięcia środowiska wirtualnego", False),
                    ("d", "Od instalacji certyfikatu HTTPS", False),
                ],
            },
            {
                "text": "Aplikacja zwraca 500 bezpośrednio i przez Nginx. Gdzie najpierw szukać przyczyny?",
                "answers": [
                    ("a", "W aplikacji i jej logach", True),
                    ("b", "Wyłącznie w publicznym DNS", False),
                    ("c", "W rekordzie AAAA niezależnie od konfiguracji", False),
                    ("d", "W poleceniu nginx -t, bo każdy 500 jest błędem składni", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest reverse proxy?", "answer": "Serwerem odbierającym żądania klientów i przekazującym je do serwera aplikacji."},
        {"question": "Jaką rolę pełni Nginx?", "answer": "Przyjmuje ruch HTTP i przekazuje go do lokalnego Uvicorna."},
        {"question": "Dlaczego Uvicorn słucha lokalnie?", "answer": "Publiczny ruch ma trafiać najpierw do Nginxa."},
        {"question": "Co rozpoczyna blok wirtualnego serwera?", "answer": "Dyrektywa server z konfiguracją zawartą w nawiasach klamrowych."},
        {"question": "Co oznacza listen 80?", "answer": "Nginx ma przyjmować ruch HTTP na porcie 80."},
        {"question": "Do czego służy server_name?", "answer": "Dopasowuje blok server do nazwy hosta żądania."},
        {"question": "Co oznacza location /?", "answer": "Regułę obsługującą żądania rozpoczynające się od głównej ścieżki."},
        {"question": "Do czego służy proxy_pass?", "answer": "Wskazuje adres serwera aplikacji, do którego Nginx przekazuje żądania."},
        {"question": "Jaki jest przykładowy upstream?", "answer": "http://127.0.0.1:8000."},
        {"question": "Po co przekazywać Host?", "answer": "Aby aplikacja znała nazwę hosta używaną przez klienta."},
        {"question": "Co zawiera X-Real-IP?", "answer": "Adres IP klienta widziany przez Nginx."},
        {"question": "Co zawiera X-Forwarded-For?", "answer": "Łańcuch adresów klienta i pośredniczących proxy."},
        {"question": "Co zawiera X-Forwarded-Proto?", "answer": "Oryginalny schemat żądania, na przykład http lub https."},
        {"question": "Co robi nginx -t?", "answer": "Sprawdza składnię i możliwość wczytania konfiguracji Nginxa."},
        {"question": "Kiedy przeładować Nginx?", "answer": "Po poprawnym wyniku nginx -t."},
        {"question": "Co robi systemctl reload nginx?", "answer": "Wczytuje nową konfigurację bez zwykłego pełnego restartu."},
        {"question": "Co zwykle oznacza 502 Bad Gateway?", "answer": "Proxy nie uzyskało poprawnej odpowiedzi od upstreamu."},
        {"question": "Jak ominąć Nginx w teście?", "answer": "Wykonać curl bezpośrednio do 127.0.0.1:8000."},
        {"question": "Jak lokalnie przetestować server_name?", "answer": "Wysłać curl do Nginxa z nagłówkiem Host: app.example.com."},
        {"question": "Gdzie są błędy Nginxa?", "answer": "Zwykle w /var/log/nginx/error.log oraz dzienniku usługi."},
        {"question": "Co sugeruje 500 także bez Nginxa?", "answer": "Problem w aplikacji lub jej zależnościach."},
        {"question": "Co sugeruje poprawny curl do Uvicorna i 502 przez Nginx?", "answer": "Problem w konfiguracji proxy, dostępie do upstreamu lub politykach systemu."},
        {"question": "Czy ta konfiguracja obejmuje HTTPS?", "answer": "Nie, ten etap dotyczy wyłącznie reverse proxy HTTP."},
        {"question": "Dlaczego diagnozować warstwami?", "answer": "Pozwala ustalić, czy błąd leży w aplikacji, Uvicornie czy Nginxie."},
        {"question": "Jaka jest kolejność bezpiecznej zmiany Nginxa?", "answer": "Edycja konfiguracji, nginx -t, reload i test odpowiedzi."},
    ],
}
