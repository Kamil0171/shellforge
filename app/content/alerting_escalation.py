ALERTING_ESCALATION = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Alerty i eskalacja",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": "Ułożysz alert wskazujący wpływ na użytkownika i procedurę potwierdzenia oraz eskalacji.",
        "theory": (
            "Dobry alert mówi, że trzeba podjąć działanie, a nie tylko że pojedyncza liczba drgnęła. "
            "Alert oparty na symptomie, na przykład wysoki odsetek błędów <code>orders-api</code>, "
            "pokazuje wpływ na użytkownika. Alert oparty na przyczynie, na przykład mało miejsca na "
            "dysku <code>app-db</code>, pomaga zdiagnozować źródło; oba są przydatne, lecz nie muszą "
            "wysyłać dwóch identycznych powiadomień. Próg określa wartość wyzwalającą, a czas trwania "
            "warunku odróżnia trwały problem od pojedynczego skoku. Zbyt krótki czas powoduje flapping, "
            "czyli częste przełączanie stanu alertu. Zbyt wiele nieistotnych powiadomień prowadzi do "
            "alert fatigue i pomijania ważnych sygnałów. Poziom severity powinien odpowiadać "
            "rzeczywistemu wpływowi i wymaganej szybkości reakcji. Routing kieruje alert do właściwego "
            "zespołu, acknowledgement potwierdza, że ktoś go przejął, a eskalacja przekazuje go "
            "dalej, gdy nie ma odpowiedzi. Zły alert brzmi „CPU > 60% przez chwilę” bez kontekstu. "
            "Lepszy brzmi „ponad 5% żądań kończy się 5xx przez 10 minut” z usługą, oknem, "
            "dashboardem i runbookiem. Warto sprawdzić także niską liczbę żądań, bo procent przy "
            "małej próbie bywa mylący."
        ),
        "commands": [
            {"command": "curl --fail --max-time 2 http://127.0.0.1:8000/health", "description": "Potwierdza, czy alarmowana instancja odpowiada.", "example": "$ curl --fail --max-time 2 http://127.0.0.1:8000/health"},
            {"command": "journalctl -u orders-api --since '10 minutes ago' -p warning --no-pager", "description": "Sprawdza zdarzenia w oknie alertu.", "example": "$ journalctl -u orders-api --since '10 minutes ago' -p warning --no-pager"},
            {"command": "date --iso-8601=seconds", "description": "Zapisuje czas przyjęcia alertu.", "example": "$ date --iso-8601=seconds"},
            {"command": "df -h /var", "description": "Sprawdza, czy alarm o miejscu ma potwierdzenie na hoście.", "example": "$ df -h /var"},
            {"command": "cat monitoring/alerts.yml", "description": "Pokazuje ćwiczeniową regułę z progiem, minimalnym ruchem i czasem trwania.", "example": "groups:\n  - name: orders-api\n    rules:\n      - alert: OrdersApiHighErrorRate\n        expr: (sum(rate(http_requests_total{service=\"orders-api\",status=~\"5..\"}[5m])) / clamp_min(sum(rate(http_requests_total{service=\"orders-api\"}[5m])), 0.001) > 0.05) and (sum(rate(http_requests_total{service=\"orders-api\"}[5m])) > 1)\n        for: 10m\n        labels:\n          severity: warning"},
            {"command": "systemctl status orders-api --no-pager", "description": "Zestawia alert z aktualnym stanem procesu.", "example": "$ systemctl status orders-api --no-pager"},
        ],
        "practice_task": (
            "Napisz dla <code>orders-api</code> dwa alerty: symptom „ponad 5% odpowiedzi 5xx "
            "przez 10 minut przy wystarczającym ruchu” oraz przyczynę „mało miejsca na dysku "
            "bazy”. Dla każdego podaj próg, okno, severity, odbiorcę, pierwszy test i odnośnik "
            "do runbooka. Zapisz, kiedy operator potwierdza alert i po jakim czasie bez reakcji "
            "następuje eskalacja. Wyjaśnij, dlaczego pojedynczy skok CPU nie powinien budzić dyżurnego."
        ),
        "common_mistakes": [
            "Wywoływanie alarmu z jednego chwilowego skoku bez czasu trwania.",
            "Wysyłanie wielu powiadomień o tym samym objawie do różnych osób bez koordynacji.",
            "Nadawanie najwyższej severity każdemu ostrzeżeniu zasobowemu.",
            "Brak właściciela alertu, runbooka i zasad eskalacji.",
            "Interpretowanie wysokiego procentu błędów bez liczby żądań.",
        ],
        "summary": (
            "Alert powinien wskazywać wpływ, czas trwania, właściciela i działanie. Progi i okna "
            "ograniczają flapping, a jasne severity, potwierdzenie i eskalacja chronią dyżur przed "
            "chaosem i zmęczeniem alertami."
        ),
    },
    "quiz": {
        "title": "Quiz: alerty i eskalacja",
        "description": "Oceń jakość sygnału i kolejne działanie dyżurnego.",
        "questions": [
            {"text": "CPU przekroczył 60% na dwie sekundy bez błędów. Dlaczego alarm do dyżurnego jest słaby?", "answers": [("a", "Nie pokazuje trwałego problemu ani wpływu na użytkownika", True), ("b", "CPU nigdy nie może przekroczyć 60%", False), ("c", "Każdy alert wymaga restartu", False), ("d", "Dwie sekundy to zawsze awaria bazy", False)]},
            {"text": "Błędy 5xx utrzymują się przez 10 minut. Jaki alert najlepiej pokazuje symptom?", "answers": [("a", "Odsetek błędnych żądań z oknem czasu i usługą", True), ("b", "Sama nazwa kontenera", False), ("c", "Liczba plików w repozytorium", False), ("d", "Data instalacji systemu", False)]},
            {"text": "Alert co minutę zmienia stan firing/resolved. Co należy poprawić?", "answers": [("a", "Próg lub wymagany czas trwania warunku", True), ("b", "Usunąć całą obserwowalność", False), ("c", "Zwiększyć uprawnienia tokenu", False), ("d", "Zmienić nazwę bazy", False)]},
            {"text": "Dyżurny przyjął alert. Co oznacza acknowledgement?", "answers": [("a", "Potwierdzenie, że ktoś przejął odpowiedzialność za reakcję", True), ("b", "Dowód trwałej naprawy", False), ("c", "Automatyczne odtworzenie danych", False), ("d", "Usunięcie wszystkich logów", False)]},
            {"text": "Nikt nie potwierdził krytycznego alertu w ustalonym czasie. Co dalej?", "answers": [("a", "Eskalować zgodnie z procedurą dyżurową", True), ("b", "Uznać problem za rozwiązany", False), ("c", "Wyłączyć health check", False), ("d", "Zignorować kolejne sygnały", False)]},
            {"text": "Jedno z dziesięciu żądań zakończyło się błędem. Co warto sprawdzić przed alarmem procentowym?", "answers": [("a", "Liczbę żądań i dłuższe okno, bo próba jest mała", True), ("b", "Wyłącznie kolor wykresu", False), ("c", "Tag obrazu bez logów", False), ("d", "Wersję edytora", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest alert operacyjny?", "answer": "Sygnałem wymagającym określonej reakcji człowieka lub automatu."},
        {"question": "Czym jest alert symptomowy?", "answer": "Powiadomieniem o skutku widocznym dla użytkownika."},
        {"question": "Czym jest alert przyczynowy?", "answer": "Powiadomieniem o stanie zasobu mogącym wywołać problem."},
        {"question": "Po co próg alertu?", "answer": "Wyznacza wartość, od której warunek jest naruszony."},
        {"question": "Po co czas trwania warunku?", "answer": "Odfiltrowuje krótkie skoki bez trwałego wpływu."},
        {"question": "Czym jest flapping?", "answer": "Częstym przełączaniem alertu między stanami."},
        {"question": "Czym jest alert fatigue?", "answer": "Zmęczeniem nadmiarem mało użytecznych powiadomień."},
        {"question": "Co powinno określać severity?", "answer": "Wpływ problemu i wymagany czas reakcji."},
        {"question": "Czym jest routing alertu?", "answer": "Skierowaniem powiadomienia do właściwego odbiorcy."},
        {"question": "Czym jest acknowledgement?", "answer": "Potwierdzeniem przyjęcia alertu do obsługi."},
        {"question": "Czym jest eskalacja?", "answer": "Przekazaniem alertu dalej, gdy wymaga szybszej reakcji."},
        {"question": "Co powinien zawierać alert?", "answer": "Usługę, objaw, okno czasu, severity i drogę do runbooka."},
        {"question": "Dlaczego sam CPU > 60% to słaby alarm?", "answer": "Nie pokazuje wpływu ani trwałości problemu."},
        {"question": "Po co próg błędów 5xx?", "answer": "Pokazuje pogorszenie odpowiedzi widocznych dla klientów."},
        {"question": "Po co uwzględnić liczbę żądań?", "answer": "Mała próba może wyolbrzymić procent błędów."},
        {"question": "Co może być alertem przyczynowym dla app-db?", "answer": "Niski zapas wolnego miejsca na dysku bazy."},
        {"question": "Co oznacza for: 10m w regule Prometheus?", "answer": "Warunek musi trwać 10 minut przed stanem firing."},
        {"question": "Czy acknowledgement kończy incydent?", "answer": "Nie, oznacza przejęcie odpowiedzialności."},
        {"question": "Kiedy eskalować?", "answer": "Gdy brak reakcji lub wpływ przekracza możliwości obecnego dyżuru."},
        {"question": "Po co runbook w alercie?", "answer": "Podaje pierwsze testy i bezpieczne kroki diagnozy."},
        {"question": "Jak ograniczyć duplikaty powiadomień?", "answer": "Grupować powiązane objawy i przypisać właściciela."},
        {"question": "Czy alert powinien wymagać działania?", "answer": "Tak, inaczej lepiej pozostawić sygnał na dashboardzie."},
        {"question": "Co sprawdzić po otrzymaniu alertu?", "answer": "Aktualny health, zakres wpływu i czas początku problemu."},
        {"question": "Co zrobić po fałszywym alarmie?", "answer": "Poprawić regułę na podstawie przyczyny i danych."},
        {"question": "Czym jest dobry alert 5xx?", "answer": "Trwałym przekroczeniem odsetka błędów przy istotnym ruchu."},
    ],
}
