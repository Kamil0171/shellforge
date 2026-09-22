OBSERVABILITY_SIGNALS = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Obserwowalność: logi, metryki i ślady",
        "level": "Średnio zaawansowany",
        "duration": "55 min",
        "description": "Dobierzesz log, metrykę lub ślad do pytania diagnostycznego i połączysz je w jedną oś czasu.",
        "theory": (
            "Obserwowalność pomaga wywnioskować stan systemu z jego sygnałów. Log opisuje konkretne "
            "zdarzenie z czasem i kontekstem, metryka liczy lub mierzy zjawisko w czasie, a ślad "
            "pokazuje drogę pojedynczego żądania przez komponenty. Gdy rośnie liczba błędów HTTP, "
            "metryka pokazuje skalę i początek problemu; log wskazuje komunikat błędu; ślad może "
            "pokazać, że większość czasu zajęło zapytanie do <code>app-db</code>. Nie trzeba wdrażać "
            "pełnego systemu distributed tracing, aby zrozumieć tę różnicę. Przydatny jest wspólny "
            "czas, nazwa usługi, identyfikator żądania i wersja aplikacji. Bez zgodnych znaczników czasu "
            "łatwo połączyć niepowiązane zdarzenia. Najpierw określ pytanie: czy problem dotyczy wielu "
            "żądań, konkretnego użytkownika czy jednego zależnego serwisu. Potem wybierz sygnał. "
            "Nie zapisuj w logach tokenów, haseł ani danych osobowych. Kontroluj dostęp i retencję "
            "sygnałów, ponieważ także metadane diagnostyczne mogą być wrażliwe."
        ),
        "commands": [
            {"command": "date --iso-8601=seconds", "description": "Zapisuje czas rozpoczęcia obserwacji z informacją o strefie.", "example": "$ date --iso-8601=seconds"},
            {"command": "curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' http://127.0.0.1:8000/health", "description": "Zbiera prosty wynik HTTP i czas żądania.", "example": "$ curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' http://127.0.0.1:8000/health"},
            {"command": "journalctl -u orders-api --since '10 minutes ago' --no-pager", "description": "Czyta zdarzenia usługi z tego samego okna czasu.", "example": "$ journalctl -u orders-api --since '10 minutes ago' --no-pager"},
            {"command": "docker compose logs --since 10m app-db", "description": "Porównuje logi kontenera bazy z logami aplikacji.", "example": "$ docker compose logs --since 10m app-db"},
            {"command": "grep 'orders-api' /var/log/nginx/error.log | tail -n 20", "description": "Szukając błędów proxy, łączy obserwacje z warstwy HTTP.", "example": "$ grep 'orders-api' /var/log/nginx/error.log | tail -n 20"},
            {"command": "systemctl status orders-api --no-pager", "description": "Dodaje stan procesu do pozostałych sygnałów.", "example": "$ systemctl status orders-api --no-pager"},
        ],
        "practice_task": (
            "Załóż, że <code>orders-api</code> zaczyna odpowiadać wolno po 14:00. Utwórz oś czasu "
            "z odczytu czasu HTTP, liczby błędów w krótkim oknie i logów aplikacji oraz <code>app-db</code>. "
            "Dla każdego sygnału zapisz, na jakie pytanie odpowiada. Zaproponuj identyfikator "
            "żądania, który łączyłby zdarzenia z kilku usług, bez logowania danych klienta."
        ),
        "common_mistakes": [
            "Wyciąganie wniosku o skali awarii z pojedynczego logu.",
            "Interpretowanie średniego czasu żądania jako przebiegu konkretnego requestu.",
            "Porównywanie logów bez kontroli strefy czasu i okna zdarzenia.",
            "Zapisywanie sekretów w danych diagnostycznych.",
            "Uruchamianie skomplikowanego tracingu bez jasnego pytania operacyjnego.",
        ],
        "summary": (
            "Metryki pokazują skalę i trend, logi szczegóły zdarzeń, a ślady przebieg wybranego "
            "żądania. Wspólny czas, usługa i identyfikator pozwalają połączyć sygnały w diagnozę "
            "bez ujawniania poufnych danych."
        ),
    },
    "quiz": {
        "title": "Quiz: logi, metryki i ślady",
        "description": "Dobierz właściwy sygnał do problemu operacyjnego.",
        "questions": [
            {"text": "Chcesz wiedzieć, czy od 14:00 wzrósł odsetek błędów. Który sygnał jest najlepszy?", "answers": [("a", "Metryka błędów w czasie", True), ("b", "Pojedynczy log z rana", False), ("c", "Nazwa obrazu aplikacji", False), ("d", "Lista volume", False)]},
            {"text": "Potrzebujesz dokładnego komunikatu wyjątku dla jednego żądania. Gdzie zaczniesz?", "answers": [("a", "Od logu powiązanego z identyfikatorem żądania", True), ("b", "Od średniej CPU z miesiąca", False), ("c", "Od tagu obrazu", False), ("d", "Od listy użytkowników hosta", False)]},
            {"text": "Co najlepiej pokazuje drogę pojedynczego żądania przez orders-api i app-db?", "answers": [("a", "Ślad żądania", True), ("b", "Sama liczba wszystkich requestów", False), ("c", "Tylko uptime hosta", False), ("d", "Rozmiar pliku backupu", False)]},
            {"text": "Dlaczego wspólny request ID pomaga w diagnostyce?", "answers": [("a", "Łączy zdarzenia tego samego żądania w kilku komponentach", True), ("b", "Zastępuje backup", False), ("c", "Ukrywa wszystkie błędy", False), ("d", "Automatycznie przywraca bazę", False)]},
            {"text": "Dwa logi mają podobny tekst, lecz różne czasy. Co sprawdzisz przed połączeniem ich w jedną awarię?", "answers": [("a", "Strefę czasu i rzeczywiste okno zdarzenia", True), ("b", "Kolor dashboardu", False), ("c", "Wielkość obrazu Dockera", False), ("d", "Nazwę edytora tekstu", False)]},
            {"text": "Która informacja nie powinna trafić do logu diagnostycznego?", "answers": [("a", "Pełny token dostępu użytkownika", True), ("b", "Kod odpowiedzi HTTP", False), ("c", "Czas zdarzenia", False), ("d", "Nazwa usługi", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest obserwowalność?", "answer": "Wnioskowaniem o stanie systemu z emitowanych sygnałów."},
        {"question": "Co opisuje log?", "answer": "Konkretne zdarzenie wraz z czasem i kontekstem."},
        {"question": "Co opisuje metryka?", "answer": "Wartość lub liczbę zjawisk obserwowaną w czasie."},
        {"question": "Co opisuje ślad?", "answer": "Przebieg jednego żądania przez komponenty."},
        {"question": "Który sygnał pokazuje skalę awarii?", "answer": "Metryka, na przykład odsetek błędnych żądań."},
        {"question": "Który sygnał pokazuje komunikat wyjątku?", "answer": "Log powiązany z problematycznym żądaniem."},
        {"question": "Który sygnał pokazuje powolny krok zapytania?", "answer": "Ślad z czasem kolejnych etapów żądania."},
        {"question": "Po co request ID?", "answer": "Łączy logi i zdarzenia jednego żądania."},
        {"question": "Po co nazwa usługi w logu?", "answer": "Wskazuje komponent, który wygenerował zdarzenie."},
        {"question": "Po co wersja aplikacji przy sygnałach?", "answer": "Ułatwia powiązanie regresji z konkretnym wdrożeniem."},
        {"question": "Po co zgodne znaczniki czasu?", "answer": "Pozwalają poprawnie zestawić zdarzenia z różnych usług."},
        {"question": "Czy pojedynczy log pokazuje skalę problemu?", "answer": "Nie, do skali lepsza jest agregowana metryka."},
        {"question": "Czy średnia metryka pokazuje jedno żądanie?", "answer": "Nie, opisuje grupę obserwacji."},
        {"question": "Czy tracing jest potrzebny w każdym prostym serwisie?", "answer": "Nie, należy dobrać koszt narzędzia do problemu."},
        {"question": "Jakie pytanie zadać przed wyborem sygnału?", "answer": "Czy szukam skali, szczegółu zdarzenia czy drogi żądania?"},
        {"question": "Co daje porównanie logów orders-api i app-db?", "answer": "Pomaga ustalić, czy błąd aplikacji wiąże się z bazą."},
        {"question": "Co mierzy curl time_total?", "answer": "Całkowity czas pojedynczego żądania HTTP."},
        {"question": "Jak wybrać okno logów?", "answer": "Użyć journalctl --since z czasem rozpoczęcia problemu."},
        {"question": "Czy metadata diagnostyczna może być wrażliwa?", "answer": "Tak, wymaga kontroli dostępu i retencji."},
        {"question": "Czego nie logować?", "answer": "Haseł, tokenów i zbędnych danych osobowych."},
        {"question": "Co daje oś czasu incydentu?", "answer": "Porządkuje zmianę sygnałów i wykonane działania."},
        {"question": "Czy HTTP 200 wyklucza wolne odpowiedzi?", "answer": "Nie, kod i czas trzeba obserwować osobno."},
        {"question": "Co zrobić po wykryciu trendu błędów?", "answer": "Zawęzić czas i sprawdzić powiązane logi."},
        {"question": "Jak ograniczyć dostęp do sygnałów?", "answer": "Przyznać tylko uprawnienia potrzebne do diagnostyki."},
        {"question": "Co odróżnia trzy sygnały w jednym zdaniu?", "answer": "Metryka mówi ile, log co się stało, ślad którędy przeszło żądanie."},
    ],
}
