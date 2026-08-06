POST_DEPLOYMENT_DIAGNOSTICS = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Logi i diagnostyka problemów po wdrożeniu",
        "level": "Średnio zaawansowany",
        "duration": "65 min",
        "description": (
            "Zdiagnozujesz nieudane wdrożenie warstwa po warstwie: od procesu i portu aplikacji przez Nginx i "
            "TLS aż po DNS oraz zasoby systemu."
        ),
        "theory": (
            "Skuteczna diagnostyka nie polega na wielokrotnym restartowaniu usługi, lecz na ustaleniu, w której "
            "warstwie znika poprawna odpowiedź. Najpierw <code>systemctl status example-app</code> pokazuje, czy "
            "proces został uruchomiony, a <code>journalctl -u example-app</code> ujawnia błędy importu, brak "
            "konfiguracji, problemy z uprawnieniami lub bazą. Opcja <code>-n 100</code> pobiera ostatnie wpisy, "
            "<code>--since</code> ogranicza czas, <code>-f</code> śledzi nowe zdarzenia, a <code>-b</code> może "
            "ograniczyć logi do bieżącego uruchomienia systemu. Kolejny krok to bezpośredni test Uvicorna na "
            "<code>127.0.0.1:8000</code> i kontrola nasłuchu przez <code>ss -tlnp</code>. Jeśli aplikacja lokalnie "
            "odpowiada, sprawdza się <code>nginx -t</code>, status Nginxa oraz "
            "<code>/var/log/nginx/error.log</code> i <code>access.log</code>. Dopiero potem bada się publiczną "
            "domenę, TLS oraz DNS przez <code>curl</code> i <code>dig</code>. Warstwy mają różne objawy: błędny "
            "DNS prowadzi pod niewłaściwy adres; problem TLS zatrzymuje zestawienie bezpiecznego połączenia; "
            "Nginx może zwrócić 502, gdy nie połączy się z Uvicornem; aplikacja może zwrócić 500 przy błędzie "
            "kodu lub bazy. Kod 404 oznacza brak wskazanego zasobu lub niedopasowaną trasę, 502 Bad Gateway "
            "zwykle problem z upstreamem, 503 Service Unavailable niedostępność usługi, a 500 Internal Server "
            "Error błąd obsługi żądania. Kody są wskazówką, nie pełną diagnozą. Trzeba też sprawdzić procesy i "
            "zasoby: pełny dysk może uniemożliwić zapis bazy lub logów, brak pamięci może zakończyć proces, a "
            "wysokie obciążenie może powodować timeouty. <code>df -h</code>, <code>free -h</code> i "
            "<code>uptime</code> szybko pokazują podstawowy stan. Rozsądna kolejność to: status i logi aplikacji, "
            "lokalny port, lokalna odpowiedź, Nginx, publiczny HTTPS, DNS i zasoby. Restart wykonuje się dopiero "
            "wtedy, gdy wynika z diagnozy; bez rozpoznania przyczyny może chwilowo ukryć problem i zatrzeć część "
            "kontekstu."
        ),
        "commands": [
            {
                "command": "systemctl status example-app --no-pager -l",
                "description": "Pokazuje stan usługi aplikacji i pełne ostatnie komunikaty.",
                "example": "$ systemctl status example-app --no-pager -l",
            },
            {
                "command": "journalctl -u example-app -n 100 --no-pager",
                "description": "Wyświetla sto ostatnich wpisów dziennika jednostki.",
                "example": "$ journalctl -u example-app -n 100 --no-pager",
            },
            {
                "command": "journalctl -u example-app --since \"10 minutes ago\"",
                "description": "Ogranicza logi do okresu obejmującego ostatnie wdrożenie.",
                "example": "$ journalctl -u example-app --since \"10 minutes ago\"",
            },
            {
                "command": "journalctl -u example-app -f",
                "description": "Śledzi nowe logi podczas kontrolowanego testu żądania.",
                "example": "$ journalctl -u example-app -f",
            },
            {
                "command": "sudo nginx -t && systemctl status nginx --no-pager -l",
                "description": "Sprawdza konfigurację i stan warstwy reverse proxy.",
                "example": "$ sudo nginx -t\n$ systemctl status nginx --no-pager -l",
            },
            {
                "command": "sudo tail -n 100 /var/log/nginx/error.log",
                "description": "Pokazuje ostatnie błędy połączeń, konfiguracji i upstreamu Nginxa.",
                "example": "$ sudo tail -n 100 /var/log/nginx/error.log",
            },
            {
                "command": "curl -v http://127.0.0.1:8000/ && curl -I https://app.example.com/",
                "description": "Porównuje bezpośrednią odpowiedź Uvicorna z publicznym adresem HTTPS.",
                "example": "$ curl -v http://127.0.0.1:8000/\n$ curl -I https://app.example.com/",
            },
            {
                "command": "ss -tlnp && ps aux",
                "description": "Pokazuje nasłuchujące porty i uruchomione procesy.",
                "example": "$ ss -tlnp\n$ ps aux",
            },
            {
                "command": "df -h && free -h && uptime && dig app.example.com",
                "description": "Sprawdza dysk, pamięć, obciążenie oraz rozwiązanie domeny.",
                "example": "$ df -h\n$ free -h\n$ uptime\n$ dig app.example.com",
            },
        ],
        "practice_task": (
            "Przeanalizuj laboratoryjny przypadek, w którym <code>https://app.example.com</code> zwraca 502. "
            "Sprawdź kolejno status i logi <code>example-app</code> z ostatnich 10 minut, nasłuch portu przez "
            "<code>ss -tlnp</code>, odpowiedź <code>curl -v http://127.0.0.1:8000/</code>, test i log błędów "
            "Nginxa, publiczny HTTPS oraz rekord DNS. Na końcu sprawdź <code>df -h</code>, <code>free -h</code> "
            "i <code>uptime</code>. Dla każdego kroku zapisz obserwację i wniosek. Nie restartuj usługi, dopóki "
            "nie wskażesz hipotezy, którą restart ma sprawdzić lub naprawić."
        ),
        "common_mistakes": [
            "Restartowanie usługi bez wcześniejszego zapisania stanu i odczytania logów.",
            "Diagnozowanie publicznej domeny bez bezpośredniego testu 127.0.0.1:8000.",
            "Traktowanie każdego 502 jako błędu DNS.",
            "Sprawdzanie tylko logów aplikacji i pomijanie error.log Nginxa.",
            "Ignorowanie pełnego dysku, braku pamięci i wysokiego obciążenia.",
            "Wyciąganie wniosków z samego kodu HTTP bez korelacji z logami.",
            "Używanie journalctl -f bez ograniczenia wcześniejszych wpisów do czasu wdrożenia.",
        ],
        "summary": (
            "Problemy po wdrożeniu należy rozdzielać na DNS, TLS, Nginx, Uvicorn, aplikację i bazę danych. "
            "Status oraz journalctl pokazują stan procesu, lokalny curl i ss weryfikują upstream, a test i logi "
            "Nginxa wyjaśniają błędy reverse proxy. Publiczny test, DNS i zasoby systemu uzupełniają obraz. "
            "Restart ma wynikać z diagnozy, ponieważ wykonany bez przyczyny może tylko ukryć problem."
        ),
    },
    "quiz": {
        "title": "Quiz: logi i diagnostyka problemów po wdrożeniu",
        "description": "Sprawdź umiejętność diagnozowania aplikacji warstwa po warstwie.",
        "questions": [
            {
                "text": "Od czego najlepiej zacząć diagnostykę niedziałającej usługi?",
                "answers": [
                    ("a", "Od statusu i logów jednostki aplikacji", True),
                    ("b", "Od wielokrotnego restartu serwera", False),
                    ("c", "Od usunięcia bazy", False),
                    ("d", "Od zmiany rekordu DNS bez testów", False),
                ],
            },
            {
                "text": "Po co testować 127.0.0.1:8000 przed publiczną domeną?",
                "answers": [
                    ("a", "Aby oddzielić działanie aplikacji od Nginxa, TLS i DNS", True),
                    ("b", "Aby odnowić certyfikat", False),
                    ("c", "Aby utworzyć backup", False),
                    ("d", "Aby zmienić branch", False),
                ],
            },
            {
                "text": "Co często oznacza odpowiedź 502 z Nginxa?",
                "answers": [
                    ("a", "Nginx nie uzyskał poprawnej odpowiedzi od upstreamu", True),
                    ("b", "Zawsze błędny rekord A", False),
                    ("c", "Zawsze brak pliku CSS", False),
                    ("d", "Poprawnie zakończone wdrożenie", False),
                ],
            },
            {
                "text": "Jak wyświetlić logi usługi z ostatnich dziesięciu minut?",
                "answers": [
                    ("a", "journalctl -u example-app --since \"10 minutes ago\"", True),
                    ("b", "git log -1 --oneline", False),
                    ("c", "df -h", False),
                    ("d", "certbot renew --dry-run", False),
                ],
            },
            {
                "text": "Który zestaw sprawdza podstawowe zasoby systemu?",
                "answers": [
                    ("a", "df -h, free -h i uptime", True),
                    ("b", "git fetch, pull i log", False),
                    ("c", "dig, host i CNAME", False),
                    ("d", "chmod, chown i umask", False),
                ],
            },
            {
                "text": "Dlaczego nie należy zaczynać od restartu?",
                "answers": [
                    ("a", "Może chwilowo ukryć problem i utrudnić rozpoznanie przyczyny", True),
                    ("b", "Systemd nie obsługuje restartu", False),
                    ("c", "Restart zawsze usuwa repozytorium", False),
                    ("d", "Restart zmienia domenę", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Co pokazuje systemctl status?", "answer": "Stan jednostki, PID procesu i ostatnie komunikaty uruchomienia."},
        {"question": "Co pokazuje journalctl -u?", "answer": "Wpisy dziennika powiązane z wybraną jednostką systemd."},
        {"question": "Do czego służy journalctl -n 100?", "answer": "Do wyświetlenia stu ostatnich wpisów."},
        {"question": "Do czego służy journalctl --since?", "answer": "Do ograniczenia logów do wskazanego czasu."},
        {"question": "Co robi journalctl -f?", "answer": "Śledzi nowe wpisy pojawiające się w dzienniku."},
        {"question": "Jak ograniczyć logi do bieżącego uruchomienia systemu?", "answer": "Użyć opcji -b w journalctl."},
        {"question": "Co sprawdza curl do 127.0.0.1:8000?", "answer": "Bezpośrednią odpowiedź Uvicorna z pominięciem Nginxa."},
        {"question": "Co pokazuje ss -tlnp?", "answer": "Nasłuchujące porty TCP i, przy odpowiednich uprawnieniach, procesy."},
        {"question": "Co sprawdza nginx -t?", "answer": "Składnię i podstawową poprawność konfiguracji Nginxa."},
        {"question": "Gdzie jest typowy error log Nginxa?", "answer": "W /var/log/nginx/error.log."},
        {"question": "Do czego służy access log Nginxa?", "answer": "Rejestruje obsłużone żądania i ich kody odpowiedzi."},
        {"question": "Co zwykle oznacza 404?", "answer": "Żądany zasób lub trasa nie zostały znalezione."},
        {"question": "Co zwykle oznacza 502?", "answer": "Reverse proxy nie otrzymało poprawnej odpowiedzi od upstreamu."},
        {"question": "Co zwykle oznacza 503?", "answer": "Usługa jest chwilowo niedostępna."},
        {"question": "Co zwykle oznacza 500?", "answer": "Aplikacja napotkała wewnętrzny błąd podczas obsługi żądania."},
        {"question": "Jak rozpoznać problem DNS?", "answer": "Porównać wynik dig z oczekiwanym adresem serwera."},
        {"question": "Jak rozpoznać warstwę TLS?", "answer": "Sprawdzić zestawianie HTTPS, nazwę certyfikatu i jego ważność."},
        {"question": "Jak odróżnić Nginx od Uvicorna?", "answer": "Porównać publiczną odpowiedź z bezpośrednim lokalnym curl."},
        {"question": "Co może wskazywać błąd bazy?", "answer": "Log aplikacji z błędem połączenia, uprawnień, zapisu lub zapytania."},
        {"question": "Co pokazuje df -h?", "answer": "Wykorzystanie miejsca w systemach plików."},
        {"question": "Co pokazuje free -h?", "answer": "Stan pamięci operacyjnej i swapu."},
        {"question": "Co pokazuje uptime?", "answer": "Czas działania systemu i średnie obciążenie."},
        {"question": "Po co używać ps aux?", "answer": "Aby sprawdzić uruchomione procesy i podstawowe informacje o zasobach."},
        {"question": "Dlaczego restart może mylić?", "answer": "Może chwilowo usunąć objaw bez usunięcia przyczyny."},
        {"question": "Jaka jest dobra kolejność diagnostyki?", "answer": "Usługa i logi, port, lokalny endpoint, Nginx, HTTPS, DNS i zasoby."},
    ],
}
