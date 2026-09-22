CI_TESTS_BUILD = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "Automatyczne testy i budowanie w pipeline",
        "level": "Średnio zaawansowany",
        "duration": "65 min",
        "description": "Złożysz kroki instalacji, Ruff, pytest i budowy obrazu w jedną bramkę jakości z raportem testów.",
        "theory": (
            "Pipeline powinien odtwarzać kroki, które działają lokalnie: pobranie kodu, ustawienie Pythona, "
            "instalację zależności, Ruff, pytest i budowę obrazu. W projekcie <code>orders-api</code> "
            "zakładamy, że <code>requirements.txt</code> zawiera także narzędzia testowe; jeśli projekt "
            "rozdziela zależności, workflow musi instalować odpowiednią grupę. Kolejność ma znaczenie: "
            "gdy Ruff lub pytest zwróci kod różny od zera, job kończy się błędem i obraz nie powinien "
            "stać się kandydatem do wydania. <code>docker build</code> sprawdza, czy aplikacja daje się "
            "spakować, ale sam w sobie nie publikuje obrazu do registry. <code>pytest --junitxml</code> "
            "zapisuje wynik w pliku. <code>actions/upload-artifact</code> może zachować raport także po "
            "niepowodzeniu testów, gdy krok ma <code>if: always()</code>. Artifact nie powinien zawierać "
            "haseł, danych osobowych ani pliku env. Nazwa artifactu ułatwia powiązanie go z uruchomieniem. "
            "Warto sprawdzić wersje używanych akcji i przypinać je zgodnie z polityką projektu, a przy "
            "wyższych wymaganiach bezpieczeństwa do pełnych commit SHA. Przed rozbudową workflow "
            "upewnij się, że te same komendy przechodzą lokalnie."
        ),
        "commands": [
            {"command": "python -m pip install -r requirements.txt", "description": "Instaluje zależności z wersjonowanego pliku.", "example": "$ python -m pip install -r requirements.txt"},
            {"command": "ruff check .", "description": "Kończy krok błędem, gdy kod narusza reguły Ruff.", "example": "$ ruff check ."},
            {"command": "pytest --junitxml=reports/pytest.xml", "description": "Uruchamia testy i zapisuje raport JUnit.", "example": "$ pytest --junitxml=reports/pytest.xml"},
            {"command": "docker build -t orders-api:ci .", "description": "Sprawdza budowę obrazu bez publikowania do registry.", "example": "$ docker build -t orders-api:ci ."},
            {"command": "- uses: actions/checkout@v4", "description": "Przykładowy krok YAML pobierający kod w istniejącej wersji akcji.", "example": "- name: Pobierz kod\n  uses: actions/checkout@v4"},
            {"command": "- uses: actions/setup-python@v5", "description": "Przykładowy krok YAML wybierający Pythona.", "example": "- name: Ustaw Python\n  uses: actions/setup-python@v5\n  with:\n    python-version: '3.12'"},
            {"command": "- uses: actions/upload-artifact@v4", "description": "Przykładowy krok YAML zapisujący raport także po błędzie testów.", "example": "- name: Zachowaj raport\n  if: always()\n  uses: actions/upload-artifact@v4\n  with:\n    name: pytest-report\n    path: reports/pytest.xml"},
        ],
        "practice_task": (
            "Rozszerz ćwiczeniowy job <code>checks</code> dla <code>orders-api</code>: zainstaluj "
            "zależności, uruchom <code>ruff check .</code>, <code>pytest --junitxml=reports/pytest.xml</code> "
            "i dopiero potem <code>docker build -t orders-api:ci .</code>. Dodaj krok upload-artifact "
            "dla raportu z <code>if: always()</code>. Wymuś lokalnie jeden błąd testu i opisz, "
            "który krok joba powinien się zatrzymać oraz dlaczego raport ma pozostać dostępny."
        ),
        "common_mistakes": [
            "Budowanie lub publikowanie obrazu mimo niepowodzenia testów.",
            "Zakładanie, że runner ma zależności projektu bez instalacji.",
            "Przesyłanie w artifactach plików env lub prywatnych danych.",
            "Uznawanie udanej budowy obrazu za test działania aplikacji.",
            "Pomijanie raportu po błędzie przez brak if: always().",
        ],
        "summary": (
            "Kroki CI powinny odtwarzać lokalny quality gate i zatrzymywać dalsze działania po błędzie. "
            "Budowa obrazu weryfikuje pakowanie, a raport testów jako artifact ułatwia diagnozę. "
            "Publikowanie i wdrażanie wymagają osobnej decyzji."
        ),
    },
    "quiz": {
        "title": "Quiz: testy i budowanie w pipeline",
        "description": "Sprawdź kolejność bramek jakości i sposób zachowania wyników.",
        "questions": [
            {"text": "Ruff zwraca błąd. Co powinno stać się z krokiem budowy obrazu?", "answers": [("a", "Nie powinien zostać wykonany w tym jobie", True), ("b", "Powinien opublikować obraz mimo błędu", False), ("c", "Powinien usunąć testy", False), ("d", "Powinien zmienić gałąź main", False)]},
            {"text": "Po co pytest --junitxml=reports/pytest.xml?", "answers": [("a", "Aby zapisać wynik testów jako plik raportu", True), ("b", "Aby uruchomić PostgreSQL", False), ("c", "Aby opublikować obraz", False), ("d", "Aby ustawić permissions", False)]},
            {"text": "Raport ma być zachowany także po błędzie testów. Jaki warunek dodać do upload-artifact?", "answers": [("a", "if: always()", True), ("b", "if: success()", False), ("c", "EXPOSE 8000", False), ("d", "depends_on: app-db", False)]},
            {"text": "Co potwierdza udane docker build w CI?", "answers": [("a", "Że obraz dał się zbudować z bieżącego kodu", True), ("b", "Że działa produkcyjna baza", False), ("c", "Że wykonano deployment", False), ("d", "Że wszystkie endpointy są poprawne", False)]},
            {"text": "Jakie pliki wolno dodać do artifactu testów?", "answers": [("a", "Raport bez sekretów i prywatnych danych", True), ("b", "Plik env z hasłem produkcyjnym", False), ("c", "Lokalny zrzut bazy klientów", False), ("d", "Klucz SSH runnera", False)]},
            {"text": "Runner nie znajduje modułu pytest. Jaki krok najpierw sprawdzisz?", "answers": [("a", "Instalację zależności testowych", True), ("b", "Publikację portu 5432", False), ("c", "Nazwę volume bazy", False), ("d", "Ustawienie EXPOSE w Dockerfile", False)]},
        ],
    },
    "flashcards": [
        {"question": "Jaka kolejność podstawowego CI?", "answer": "Checkout, Python, zależności, Ruff, pytest, budowa."},
        {"question": "Po co checkout w jobie?", "answer": "Udostępnia pliki projektu na runnerze."},
        {"question": "Po co setup-python?", "answer": "Wybiera wersję interpretera dla testów."},
        {"question": "Co instaluje requirements.txt?", "answer": "Zależności zapisane przez projekt."},
        {"question": "Co gdy narzędzia testowe są w osobnej grupie?", "answer": "Workflow musi jawnie zainstalować tę grupę."},
        {"question": "Co weryfikuje Ruff?", "answer": "Reguły jakości i stylu kodu skonfigurowane w projekcie."},
        {"question": "Co weryfikuje pytest?", "answer": "Zachowanie sprawdzane przez testy projektu."},
        {"question": "Co znaczy niezerowy kod wyjścia?", "answer": "Krok zakończył się niepowodzeniem."},
        {"question": "Co dzieje się z kolejnymi zwykłymi krokami po błędzie?", "answer": "Są pomijane, jeśli nie mają szczególnego warunku."},
        {"question": "Co weryfikuje docker build?", "answer": "Możliwość zbudowania obrazu z bieżącego kontekstu."},
        {"question": "Czy docker build publikuje obraz?", "answer": "Nie, do tego potrzebny jest osobny krok."},
        {"question": "Czy budowa obrazu testuje działanie endpointów?", "answer": "Nie, wymaga to uruchomienia i osobnych testów."},
        {"question": "Co tworzy --junitxml w pytest?", "answer": "Raport testów w formacie JUnit XML."},
        {"question": "Czym jest artifact workflow?", "answer": "Zachowanym plikiem wynikowym uruchomienia."},
        {"question": "Po co upload-artifact?", "answer": "Pozwala pobrać raport po zakończeniu joba."},
        {"question": "Co daje if: always()?", "answer": "Pozwala wykonać krok także po niepowodzeniu wcześniejszych kroków."},
        {"question": "Czy artifact może zawierać hasła?", "answer": "Nie, raporty trzeba oczyścić z sekretów i prywatnych danych."},
        {"question": "Co odróżnia build od publish?", "answer": "Build tworzy lokalny obraz, publish wysyła go do registry."},
        {"question": "Po co uruchomić te same komendy lokalnie?", "answer": "Aby szybko odtworzyć błędy CI."},
        {"question": "Jak ustalić, który krok zawiódł?", "answer": "Otworzyć log nieudanego joba i kroku."},
        {"question": "Czy wersje akcji trzeba kontrolować?", "answer": "Tak, dla powtarzalności i bezpieczeństwa workflow."},
        {"question": "Co daje przypięcie akcji do SHA?", "answer": "Wskazuje dokładny commit implementacji akcji."},
        {"question": "Dlaczego testy przed buildem?", "answer": "Błąd powinien zablokować tworzenie kandydata do wydania."},
        {"question": "Czy zielony lint zastępuje testy?", "answer": "Nie, sprawdzają inne rodzaje problemów."},
        {"question": "Co zachować po błędzie pytest?", "answer": "Log kroku i raport testów do diagnozy."},
    ],
}
