APPLICATION_MONITORING = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Monitoring aplikacji i zależności",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": "Zbudujesz prostą tablicę stanu usługi z sygnałów aplikacji, hosta i zależnej bazy.",
        "theory": (
            "Monitoring odpowiada na pytanie, czy usługa działa dla użytkownika i co ogranicza jej "
            "pracę. Dostępność endpointu to tylko jeden wymiar. Obserwuj ruch żądań, odsetek błędów, "
            "opóźnienie oraz nasycenie zasobów. Wzrost ruchu bez wzrostu błędów może być normalny, "
            "ale ten sam ruch przy wyczerpanej puli połączeń wskazuje ryzyko. Metryki hosta, takie jak "
            "CPU, pamięć, dysk i sieć, opisują maszynę. Metryki aplikacji opisują jej żądania, "
            "kolejki i połączenia. Niski CPU hosta nie wyklucza awarii <code>orders-api</code>. "
            "Zależna baza <code>app-db</code> potrzebuje własnego sygnału gotowości i czasu odpowiedzi. "
            "W prostym laboratorium wystarczą <code>curl</code>, <code>uptime</code>, <code>free</code> "
            "i <code>df</code>. W większym środowisku Prometheus może zbierać metryki, a Grafana je "
            "wizualizować; tutaj są przykładami narzędzi, nie częścią runtime ShellForge. Dashboard "
            "powinien pokazywać czas, jednostki i źródło danych. Brak próbki może oznaczać awarię "
            "monitoringu, a nie poprawny stan usługi."
        ),
        "commands": [
            {"command": "curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' http://127.0.0.1:8000/health", "description": "Zbiera wynik i czas jednego żądania do aplikacji.", "example": "$ curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' http://127.0.0.1:8000/health"},
            {"command": "uptime", "description": "Pokazuje czas pracy hosta i średnie obciążenie.", "example": "$ uptime"},
            {"command": "free -h", "description": "Sprawdza pamięć hosta w czytelnych jednostkach.", "example": "$ free -h"},
            {"command": "df -h /", "description": "Sprawdza wolne miejsce na systemie plików hosta.", "example": "$ df -h /"},
            {"command": "ss -s", "description": "Pokazuje zbiorczy stan połączeń sieciowych.", "example": "$ ss -s"},
            {"command": "docker compose exec app-db pg_isready -U orders -d orders", "description": "Kontroluje gotowość zależnej bazy w ćwiczeniowym Compose.", "example": "$ docker compose exec app-db pg_isready -U orders -d orders"},
            {"command": "docker compose ps", "description": "Pokazuje stan usług aplikacji i bazy w projekcie.", "example": "$ docker compose ps"},
        ],
        "practice_task": (
            "Dla <code>orders-api</code> przygotuj prostą tablicę z pięcioma polami: dostępność, "
            "ruch, czas odpowiedzi, błędy i nasycenie. Obok wpisz stan <code>app-db</code> oraz CPU, "
            "pamięć i dysk hosta. Dla dwóch scenariuszy — baza nie odpowiada i dysk prawie pełny — "
            "wskaż, które pola zmienią się najpierw i jaki test potwierdzi przypuszczenie. Nie uznawaj "
            "braku danych monitoringu za dowód zdrowia aplikacji."
        ),
        "common_mistakes": [
            "Uznawanie poprawnego uptime hosta za dowód działania aplikacji.",
            "Ignorowanie zależnej bazy podczas diagnozy błędów aplikacji.",
            "Mieszanie jednostek czasu odpowiedzi, na przykład sekund i milisekund.",
            "Odczytywanie braku danych jako zera błędów.",
            "Budowanie dashboardu bez okna czasu i źródła sygnału.",
        ],
        "summary": (
            "Monitoruj objawy widoczne dla użytkownika oraz zasoby hosta i zależności. Ruch, błędy, "
            "opóźnienie i nasycenie dają szerszy obraz niż sam uptime. Prometheus i Grafana są "
            "przykładami zbierania i prezentacji tych sygnałów."
        ),
    },
    "quiz": {
        "title": "Quiz: monitoring aplikacji i zależności",
        "description": "Sprawdź, które sygnały potwierdzają wpływ problemu na użytkownika.",
        "questions": [
            {"text": "Host ma niski CPU, lecz orders-api zwraca 503. Jaki wniosek jest właściwy?", "answers": [("a", "Metryka hosta nie wyklucza awarii aplikacji lub bazy", True), ("b", "Usługa na pewno działa", False), ("c", "Należy usunąć dashboard", False), ("d", "CPU zastępuje test HTTP", False)]},
            {"text": "Rośnie ruch i odsetek błędów, a pula połączeń bazy jest pełna. Co sprawdzisz?", "answers": [("a", "Zależną bazę i limit połączeń", True), ("b", "Tylko kolor wykresu", False), ("c", "Wyłącznie nazwę gałęzi Git", False), ("d", "Rozmiar obrazka na stronie", False)]},
            {"text": "Która metryka mówi o doświadczeniu użytkownika bardziej bezpośrednio niż uptime hosta?", "answers": [("a", "Czas odpowiedzi ważnego endpointu", True), ("b", "Liczba katalogów w /opt", False), ("c", "Wersja powłoki", False), ("d", "Data instalacji Pythona", False)]},
            {"text": "W dashboardzie zniknęły wszystkie próbki metryk. Co trzeba sprawdzić?", "answers": [("a", "Czy działa zbieranie danych monitoringu", True), ("b", "Założyć, że błędy spadły do zera", False), ("c", "Od razu usunąć bazę", False), ("d", "Zastąpić health check tagiem obrazu", False)]},
            {"text": "Co mierzy df -h /?", "answers": [("a", "Wolne miejsce systemu plików hosta", True), ("b", "Odsetek błędnych żądań", False), ("c", "Czas zapytania SQL", False), ("d", "Liczbę aktywnych użytkowników aplikacji", False)]},
            {"text": "Jaka jest rola Grafany w omawianym układzie?", "answers": [("a", "Wizualizacja zebranych sygnałów", True), ("b", "Zastąpienie bazy PostgreSQL", False), ("c", "Wykonanie wszystkich backupów", False), ("d", "Automatyczny restart każdego procesu", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest monitoring aplikacji?", "answer": "Ciągłą obserwacją działania usługi i jej wpływu na użytkownika."},
        {"question": "Co oznacza uptime usługi?", "answer": "Czas lub udział czasu, w którym usługa jest dostępna według przyjętego testu."},
        {"question": "Co oznacza traffic?", "answer": "Wolumen żądań docierających do usługi."},
        {"question": "Co oznacza latency?", "answer": "Czas potrzebny na odpowiedź na żądanie."},
        {"question": "Co oznacza error rate?", "answer": "Udział lub tempo błędnych żądań w określonym oknie."},
        {"question": "Co oznacza saturation?", "answer": "Stopień wykorzystania ograniczonego zasobu."},
        {"question": "Co może ograniczyć orders-api mimo niskiego CPU?", "answer": "Pełna pula połączeń bazy lub kolejka żądań."},
        {"question": "Czym różnią się metryki hosta od aplikacji?", "answer": "Host opisuje maszynę, aplikacja własne żądania i zasoby."},
        {"question": "Czy dobry uptime hosta gwarantuje działanie API?", "answer": "Nie, proces i zależności mogą zawodzić."},
        {"question": "Po co monitorować app-db osobno?", "answer": "Awaria zależności może powodować błędy API."},
        {"question": "Co sprawdza pg_isready?", "answer": "Czy PostgreSQL przyjmuje połączenia."},
        {"question": "Co pokazuje free -h?", "answer": "Stan pamięci hosta."},
        {"question": "Co pokazuje df -h /?", "answer": "Wolne miejsce systemu plików zawierającego katalog główny."},
        {"question": "Co pokazuje uptime hosta?", "answer": "Czas pracy i średnie obciążenie systemu."},
        {"question": "Co pokazuje ss -s?", "answer": "Zbiorczy stan połączeń sieciowych."},
        {"question": "Po co jednostka przy czasie odpowiedzi?", "answer": "Bez niej sekundy można pomylić z milisekundami."},
        {"question": "Po co okno czasu na dashboardzie?", "answer": "Pozwala rozpoznać trend i początek incydentu."},
        {"question": "Co oznacza brak próbek?", "answer": "Możliwą awarię zbierania danych, niekoniecznie zdrową usługę."},
        {"question": "Do czego może służyć Prometheus?", "answer": "Do zbierania i odpytywania metryk."},
        {"question": "Do czego może służyć Grafana?", "answer": "Do wizualizacji sygnałów na dashboardzie."},
        {"question": "Co daje dashboard zależności aplikacji?", "answer": "Pozwala powiązać błędy usługi ze stanem bazy lub innego zaplecza."},
        {"question": "Co monitorować poza procesem orders-api?", "answer": "Endpoint, ruch, błędy, czas odpowiedzi i bazę."},
        {"question": "Co może oznaczać pełny dysk?", "answer": "Ryzyko błędów zapisu i niedostępności usługi."},
        {"question": "Co zrobić po wykryciu nasycenia?", "answer": "Potwierdzić ograniczony zasób i wpływ na żądania."},
        {"question": "Jaki jest cel prostej tablicy monitoringu?", "answer": "Szybko pokazać stan użytkownika, aplikacji i zależności."},
    ],
}
