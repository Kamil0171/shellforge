SERVICE_OBJECTIVES = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "SLI, SLO, SLA i budżet błędów",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": "Zdefiniujesz mierzalny cel dostępności i opóźnienia oraz zinterpretujesz prosty budżet błędów.",
        "theory": (
            "SLI to wskaźnik poziomu usługi, na przykład udział poprawnie obsłużonych żądań "
            "<code>orders-api</code> w określonym czasie. SLO to wewnętrzny cel dla wskaźnika: "
            "co najmniej 99,9% poprawnych żądań w ciągu 30 dni. SLA jest zobowiązaniem wobec "
            "odbiorcy usługi i może określać konsekwencje niespełnienia uzgodnionego poziomu. "
            "Wskaźnik dostępności musi mieć jasny mianownik, bo brak ruchu nie jest automatycznie "
            "dowodem pełnej dostępności. Dla API warto osobno rozważyć cel opóźnienia, na przykład "
            "95% żądań poniżej 500 ms. Budżet błędów to dopuszczalna część niepowodzeń wynikająca "
            "z SLO. Przy celu 99,9% pozostaje 0,1% błędnych żądań w tym samym oknie; to nie jest "
            "przyzwolenie na ignorowanie pojedynczego krytycznego incydentu. Uproszczony odpowiednik "
            "czasowy dla 30 dni to 43,2 minuty niedostępności, ale tylko wtedy, gdy dostępność "
            "mierzona jest czasowo. Wskaźnik oparty na żądaniach liczy się inaczej. Porównuj SLI "
            "z celem i zapisuj okno, wyłączenia oraz sposób pomiaru. Nie potrzebujesz złożonych "
            "formuł SRE, aby wiedzieć, kiedy jakość usługi odbiega od obietnicy."
        ),
        "commands": [
            {"command": "curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' http://127.0.0.1:8000/health", "description": "Zbiera pojedynczy pomiar kodu i czasu do definicji wskaźnika.", "example": "$ curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' http://127.0.0.1:8000/health"},
            {"command": "python3 -c 'total=10000; good=9980; print(f\"{good / total:.2%}\")'", "description": "Liczy uproszczony SLI poprawnych żądań: 99,80%.", "example": "$ python3 -c 'total=10000; good=9980; print(f\"{good / total:.2%}\")'\n99.80%"},
            {"command": "python3 -c 'print(round(30 * 24 * 60 * (1 - 0.999), 1))'", "description": "Liczy czasowy odpowiednik budżetu przy 99,9% dostępności przez 30 dni.", "example": "$ python3 -c 'print(round(30 * 24 * 60 * (1 - 0.999), 1))'\n43.2"},
            {"command": "date -u --iso-8601=seconds", "description": "Zapisuje czas UTC potrzebny do jednoznacznego okna pomiaru.", "example": "$ date -u --iso-8601=seconds"},
            {"command": "journalctl -u orders-api --since '30 minutes ago' --no-pager", "description": "Porównuje pogorszenie SLI ze zdarzeniami aplikacji.", "example": "$ journalctl -u orders-api --since '30 minutes ago' --no-pager"},
            {"command": "git rev-parse HEAD", "description": "Zapisuje wersję kodu związaną z okresem pomiaru.", "example": "$ git rev-parse HEAD"},
        ],
        "practice_task": (
            "Dla <code>orders-api</code> zapisz dwa SLI: udział poprawnych żądań i udział "
            "żądań poniżej 500 ms. Ustal SLO 99,9% oraz 95% w oknie 30 dni. Oblicz wynik "
            "dla 9980 poprawnych odpowiedzi z 10000 i wskaż, czy cel dostępności został "
            "spełniony. W notatce odróżnij budżet błędnych żądań od uproszczonego budżetu czasu "
            "niedostępności i opisz, czego wymagałoby formalne SLA."
        ),
        "common_mistakes": [
            "Mylenie SLI będącego pomiarem z SLO będącym celem.",
            "Traktowanie wewnętrznego SLO jako automatycznej umowy SLA.",
            "Przeliczanie budżetu żądań na minuty bez założeń o ruchu i metodzie pomiaru.",
            "Podawanie procentu bez okresu i mianownika.",
            "Ignorowanie ważnego incydentu tylko dlatego, że budżet nie został jeszcze wyczerpany.",
        ],
        "summary": (
            "SLI mierzy usługę, SLO wyznacza cel, a SLA opisuje zobowiązanie wobec odbiorcy. "
            "Budżet błędów wynika z celu i tego samego okna pomiaru. Dobrze opisany wskaźnik "
            "pomaga podejmować decyzje bez mylenia procentu żądań z minutami niedostępności."
        ),
    },
    "quiz": {
        "title": "Quiz: SLI, SLO, SLA i budżet błędów",
        "description": "Sprawdź interpretację celu i pomiaru jakości usługi.",
        "questions": [
            {"text": "99,80% żądań było poprawnych przy celu 99,9%. Co stwierdzisz?", "answers": [("a", "SLI jest poniżej SLO w tym oknie", True), ("b", "SLO zostało przekroczone na plus", False), ("c", "SLA automatycznie nie istnieje", False), ("d", "Brak błędów w systemie", False)]},
            {"text": "Które zdanie poprawnie odróżnia SLI od SLO?", "answers": [("a", "SLI jest pomiarem, a SLO celem dla tego pomiaru", True), ("b", "Oba są nazwą pliku logu", False), ("c", "SLO jest zawsze liczbą serwerów", False), ("d", "SLI jest umową z karą finansową", False)]},
            {"text": "Dlaczego 0,1% błędnych żądań nie zawsze równa się 43,2 minuty awarii?", "answers": [("a", "Wskaźnik żądań i wskaźnik czasu mają inne mianowniki", True), ("b", "Minuta ma 100 sekund", False), ("c", "HTTP nie mierzy czasu", False), ("d", "Budżet błędów usuwa logi", False)]},
            {"text": "Co powinien zawierać cel opóźnienia?", "answers": [("a", "Próg czasu, udział żądań i okno pomiaru", True), ("b", "Tylko numer portu", False), ("c", "Wyłącznie kolor wykresu", False), ("d", "Nazwę katalogu backupu", False)]},
            {"text": "Czym SLA różni się od wewnętrznego SLO?", "answers": [("a", "Jest uzgodnionym zobowiązaniem wobec odbiorcy", True), ("b", "Zawsze jest metryką CPU", False), ("c", "Nie wymaga określenia zakresu", False), ("d", "Automatycznie zastępuje health check", False)]},
            {"text": "W okresie bez ruchu nie ma błędnych żądań. Czy to dowodzi 100% dostępności dla użytkowników?", "answers": [("a", "Nie, trzeba określić metodę pomiaru i brakujący mianownik", True), ("b", "Tak, zawsze", False), ("c", "Tak, jeśli host ma wolny dysk", False), ("d", "Tak, jeśli nie było deployu", False)]},
        ],
    },
    "flashcards": [
        {"question": "Co oznacza SLI?", "answer": "Mierzalny wskaźnik poziomu usługi."},
        {"question": "Co oznacza SLO?", "answer": "Cel dla wybranego SLI w określonym czasie."},
        {"question": "Co oznacza SLA?", "answer": "Uzgodnione zobowiązanie poziomu usługi wobec odbiorcy."},
        {"question": "Czym różni się SLI od SLO?", "answer": "SLI mierzy, SLO określa oczekiwaną wartość."},
        {"question": "Czy każde SLO jest SLA?", "answer": "Nie, SLA wymaga odrębnego uzgodnienia."},
        {"question": "Jakie SLI pasuje do dostępności API?", "answer": "Udział poprawnie obsłużonych żądań w określonym oknie."},
        {"question": "Jaki mianownik ma SLI żądań?", "answer": "Liczbę żądań objętych pomiarem."},
        {"question": "Jakie SLI pasuje do latency?", "answer": "Udział żądań mieszczących się w granicy czasu."},
        {"question": "Co znaczy 95% poniżej 500 ms?", "answer": "Co najmniej 95% mierzonych żądań ma czas poniżej progu."},
        {"question": "Po co okno pomiaru SLO?", "answer": "Wskazuje okres, w którym oceniamy wynik."},
        {"question": "Czym jest error budget?", "answer": "Dopuszczalną częścią niepowodzeń wynikającą z SLO."},
        {"question": "Ile błędów dopuszcza cel 99,9% żądań?", "answer": "0,1% żądań w tym samym oknie."},
        {"question": "Ile minut to 0,1% z 30 dni?", "answer": "43,2 minuty w uproszczonym pomiarze czasowym."},
        {"question": "Czy budżet żądań równa się budżetowi czasu?", "answer": "Nie bez dodatkowych założeń o ruchu i pomiarze."},
        {"question": "Co daje 9980/10000 poprawnych odpowiedzi?", "answer": "SLI 99,80%, poniżej celu 99,9%."},
        {"question": "Czy brak ruchu oznacza 100% dostępności?", "answer": "Nie, wskaźnik żądań nie ma wtedy próbek."},
        {"question": "Co zapisać przy definicji SLI?", "answer": "Licznik, mianownik, okno i zakres żądań."},
        {"question": "Czy budżet pozwala ignorować incydent?", "answer": "Nie, ważny wpływ wymaga reakcji."},
        {"question": "Po co oddzielny cel opóźnienia?", "answer": "Usługa może odpowiadać bez błędów, ale za wolno."},
        {"question": "Co porównuje operator po incydencie?", "answer": "Zmierzony SLI z odpowiednim SLO."},
        {"question": "Po co zapisać wersję kodu przy SLI?", "answer": "Ułatwia powiązanie regresji z wydaniem."},
        {"question": "Czy SLO bez metody pomiaru jest użyteczne?", "answer": "Nie, wynik musi być odtwarzalny i jednoznaczny."},
        {"question": "Co jest podstawą alertu o jakości?", "answer": "Objaw mierzony przez SLI i jego znaczenie dla użytkownika."},
        {"question": "Kiedy budżet się wyczerpuje?", "answer": "Gdy niepowodzenia przekraczają dopuszczalną część okna."},
        {"question": "Dlaczego liczba próbek ma znaczenie?", "answer": "Przy małym ruchu procent może być niestabilny."},
    ],
}
