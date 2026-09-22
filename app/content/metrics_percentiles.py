METRICS_PERCENTILES = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Metryki i percentyle w praktyce",
        "level": "Średnio zaawansowany",
        "duration": "65 min",
        "description": "Dobierzesz typ metryki i odczytasz p50, p95 oraz p99 bez mylenia ich ze średnią.",
        "theory": (
            "Counter liczy zdarzenia i rośnie, dopóki proces się nie zrestartuje; z takiego licznika "
            "oblicza się tempo żądań lub błędów. Gauge pokazuje bieżącą wartość, która może rosnąć "
            "i maleć, na przykład długość kolejki albo liczbę zajętych połączeń. Histogram grupuje "
            "obserwacje czasu odpowiedzi w przedziały, dzięki czemu można szacować percentyle. "
            "p50 to mediana, p95 oznacza granicę, poniżej której mieści się około 95% pomiarów, "
            "a p99 pokazuje dalszy ogon wolnych odpowiedzi. Średnia może ukrywać problem małej "
            "grupy użytkowników, dlatego czytaj ją razem z percentylami i liczbą próbek. "
            "Metryki zasobów obejmują CPU, pamięć, dysk i sieć. Aplikacja powinna pokazywać "
            "czas żądań, błędy HTTP, głębokość kolejki <code>billing-worker</code> oraz użycie "
            "puli połączeń <code>app-db</code>. Nie porównuj p95 z różnych przedziałów czasu bez "
            "sprawdzenia ruchu. W Prometheus klasyczny histogram pozwala szacować percentyl przez "
            "<code>histogram_quantile</code>; to przykład sposobu analizy, bez instalacji narzędzia "
            "w ShellForge."
        ),
        "commands": [
            {"command": "curl -sS -o /dev/null -w '%{time_total}\n' http://127.0.0.1:8000/health", "description": "Mierzy czas pojedynczego żądania, który nie jest jeszcze percentylem.", "example": "$ curl -sS -o /dev/null -w '%{time_total}\n' http://127.0.0.1:8000/health"},
            {"command": "top -b -n 1 | head -n 20", "description": "Pokazuje chwilowy obraz CPU i procesów hosta.", "example": "$ top -b -n 1 | head -n 20"},
            {"command": "free -h", "description": "Sprawdza dostępną pamięć hosta.", "example": "$ free -h"},
            {"command": "df -h /", "description": "Sprawdza zajętość systemu plików.", "example": "$ df -h /"},
            {"command": "ip -s link show", "description": "Pokazuje liczniki ruchu i błędów interfejsów sieciowych.", "example": "$ ip -s link show"},
            {"command": "docker compose exec app-db psql -U orders -d orders -c 'SELECT count(*) FROM pg_stat_activity;'", "description": "Odczytuje liczbę bieżących połączeń PostgreSQL.", "example": "$ docker compose exec app-db psql -U orders -d orders -c 'SELECT count(*) FROM pg_stat_activity;'"},
            {"command": "histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))", "description": "Przykładowe zapytanie PromQL o p95 klasycznego histogramu żądań.", "example": "histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))"},
        ],
        "practice_task": (
            "Zaprojektuj dla <code>orders-api</code> trzy metryki: licznik wszystkich żądań, gauge "
            "zajętych połączeń bazy i histogram czasu odpowiedzi. Dopisz jednostki i okno czasu. "
            "Zinterpretuj sytuację: p50 = 100 ms, p95 = 800 ms, p99 = 2 s, a średnia = 180 ms. "
            "Wskaż, dlaczego sama średnia nie opisuje doświadczenia najwolniejszych żądań. "
            "Porównaj to z CPU, pamięcią, dyskiem, ruchem sieciowym i głębokością kolejki."
        ),
        "common_mistakes": [
            "Używanie countera dla wartości, która może maleć.",
            "Odczytywanie pojedynczego czasu curl jako p95 całej usługi.",
            "Porównywanie percentyli bez wspólnego okna i liczby próbek.",
            "Ignorowanie p99, bo średnia wygląda dobrze.",
            "Mieszanie jednostek sekund i milisekund na jednym wykresie.",
        ],
        "summary": (
            "Counter liczy zdarzenia, gauge pokazuje zmienny stan, a histogram opisuje rozkład "
            "obserwacji. Percentyle odsłaniają wolny ogon odpowiedzi, którego średnia może nie "
            "pokazać. Zawsze podawaj jednostkę, okno czasu i liczbę próbek."
        ),
    },
    "quiz": {
        "title": "Quiz: metryki i percentyle w praktyce",
        "description": "Dobierz typ metryki i wyciągnij właściwy wniosek z opóźnień.",
        "questions": [
            {"text": "Liczba żądań od startu procesu ma tylko rosnąć. Jaki typ metryki pasuje?", "answers": [("a", "Counter", True), ("b", "Gauge", False), ("c", "Nazwa volume", False), ("d", "Kod statusu systemd", False)]},
            {"text": "Długość kolejki rośnie i maleje. Jaki typ metryki pasuje?", "answers": [("a", "Gauge", True), ("b", "Counter bez resetu", False), ("c", "Digest obrazu", False), ("d", "Sam histogram czasu", False)]},
            {"text": "Średnia odpowiedź wynosi 180 ms, ale p99 to 2 s. Co to sugeruje?", "answers": [("a", "Niewielka część żądań jest znacznie wolniejsza", True), ("b", "Każde żądanie trwa 2 s", False), ("c", "Baza na pewno nie działa", False), ("d", "Metryki są identyczne", False)]},
            {"text": "Co oznacza p95 czasu odpowiedzi?", "answers": [("a", "Około 95% pomiarów mieści się na lub poniżej tej wartości", True), ("b", "Dokładnie 95 błędów HTTP", False), ("c", "Średnią z pięciu najwolniejszych żądań", False), ("d", "Bieżące użycie CPU", False)]},
            {"text": "Dlaczego jedna wartość time_total z curl nie wystarcza do p95?", "answers": [("a", "Percentyl wymaga rozkładu wielu pomiarów", True), ("b", "curl nie mierzy czasu", False), ("c", "p95 jest zawsze równy 200", False), ("d", "Trzeba usunąć logi", False)]},
            {"text": "Co trzeba podać przy porównaniu dwóch wykresów opóźnienia?", "answers": [("a", "Jednostkę, okno czasu i liczbę próbek", True), ("b", "Wyłącznie kolor linii", False), ("c", "Nazwę terminala operatora", False), ("d", "Wielkość Dockerfile", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest counter?", "answer": "Licznikiem rosnącym do resetu procesu."},
        {"question": "Do czego pasuje counter?", "answer": "Do liczby żądań lub błędów HTTP."},
        {"question": "Co dzieje się z counterem po restarcie?", "answer": "Może wrócić do zera."},
        {"question": "Czym jest gauge?", "answer": "Wartością chwilową, która może rosnąć i maleć."},
        {"question": "Do czego pasuje gauge?", "answer": "Do długości kolejki lub bieżącej liczby połączeń."},
        {"question": "Czym jest histogram?", "answer": "Zliczeniem obserwacji w przedziałach wartości."},
        {"question": "Co opisuje p50?", "answer": "Medianę zmierzonych wartości."},
        {"question": "Co opisuje p95?", "answer": "Granicę obejmującą około 95% pomiarów."},
        {"question": "Co opisuje p99?", "answer": "Dalszy ogon najwolniejszych pomiarów."},
        {"question": "Dlaczego średnia może mylić?", "answer": "Może ukrywać powolne odpowiedzi małej grupy użytkowników."},
        {"question": "Czy jeden pomiar curl jest p95?", "answer": "Nie, percentyl wymaga wielu obserwacji."},
        {"question": "Po co liczba próbek?", "answer": "Pozwala ocenić, czy percentyl opiera się na istotnej liczbie żądań."},
        {"question": "Po co okno czasu dla percentyla?", "answer": "Wynik zależy od okresu zbierania pomiarów."},
        {"question": "Jaką jednostkę ma latency?", "answer": "Czas, zwykle sekundy lub milisekundy."},
        {"question": "Co mierzy CPU hosta?", "answer": "Wykorzystanie czasu procesora maszyny."},
        {"question": "Co mierzy free -h?", "answer": "Bieżący stan pamięci hosta."},
        {"question": "Co mierzy df -h?", "answer": "Zajętość systemu plików."},
        {"question": "Co pokazuje ip -s link?", "answer": "Liczniki ruchu i błędów interfejsu sieciowego."},
        {"question": "Czym jest queue depth?", "answer": "Liczbą zadań oczekujących w kolejce."},
        {"question": "Co oznacza pełna pula połączeń?", "answer": "Aplikacja może czekać na dostępne połączenie do bazy."},
        {"question": "Co mierzy error rate?", "answer": "Tempo lub udział nieudanych żądań."},
        {"question": "Po co histogram czasu żądań?", "answer": "Pozwala analizować rozkład opóźnień i jego ogon."},
        {"question": "Do czego służy histogram_quantile?", "answer": "Szacuje percentyl z histogramu w Prometheus."},
        {"question": "Czy Prometheus musi działać w ShellForge?", "answer": "Nie, jest przykładem narzędzia omawianego edukacyjnie."},
        {"question": "Co zrobić przy wysokim p99 i niskiej średniej?", "answer": "Zbadać wolne żądania oraz zależności, zamiast ufać samej średniej."},
    ],
}
