GITHUB_ACTIONS_FIRST_WORKFLOW = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "CI/CD z GitHub Actions: pierwszy workflow",
        "level": "Średnio zaawansowany",
        "duration": "55 min",
        "description": "Zapiszesz pierwszy workflow i rozpoznasz zdarzenie, job, runner oraz kroki wykonywane na zmianie kodu.",
        "theory": (
            "CI, czyli ciągła integracja, automatycznie sprawdza zmiany łączone we wspólnym repozytorium. "
            "CD oznacza automatyzację dostarczania lub wdrażania, lecz zakres zawsze trzeba nazwać "
            "dokładnie: przejście testów nie jest jeszcze wdrożeniem. GitHub Actions czyta pliki YAML z "
            "<code>.github/workflows/</code>. Klucz <code>on</code> wskazuje zdarzenia, na przykład "
            "<code>push</code> do <code>main</code> i <code>pull_request</code> kierowany do tej gałęzi. "
            "Workflow ma zadania <code>jobs</code>; każde zadanie działa na runnerze wskazanym przez "
            "<code>runs-on</code>. Wewnątrz zadania kroki <code>steps</code> wykonują polecenia przez "
            "<code>run</code> lub używają gotowej akcji przez <code>uses</code>. "
            "<code>actions/checkout</code> pobiera kod, a <code>actions/setup-python</code> ustawia "
            "Pythona. Zadania nie współdzielą automatycznie plików, dlatego przekazanie wyniku między "
            "nimi wymaga artifactu lub osobnego magazynu. Na początku ustaw <code>permissions: "
            "contents: read</code>, aby token workflow miał tylko potrzebne prawo odczytu. Po zapisie "
            "pliku sprawdź, czy zdarzenia odpowiadają rzeczywistemu procesowi branch i PR."
        ),
        "commands": [
            {"command": "mkdir -p .github/workflows", "description": "Tworzy katalog, z którego GitHub odczytuje definicje workflow.", "example": "$ mkdir -p .github/workflows"},
            {"command": "cat .github/workflows/ci.yml", "description": "Pokazuje kompletny szkielet workflow uruchamianego dla main i PR.", "example": "name: orders-api-ci\non:\n  push:\n    branches: [main]\n  pull_request:\n    branches: [main]\npermissions:\n  contents: read\njobs:\n  checks:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with:\n          python-version: '3.12'\n      - run: python --version"},
            {"command": "git status --short", "description": "Pokazuje, czy plik workflow należy do przygotowanej zmiany.", "example": "$ git status --short"},
            {"command": "git diff -- .github/workflows/ci.yml", "description": "Pozwala sprawdzić zmianę YAML przed przeglądem.", "example": "$ git diff -- .github/workflows/ci.yml"},
            {"command": "gh workflow list", "description": "Pokazuje workflow dostępne w połączonym repozytorium GitHub.", "example": "$ gh workflow list"},
            {"command": "gh run list --workflow ci.yml --limit 5", "description": "Pokazuje ostatnie uruchomienia danego workflow.", "example": "$ gh run list --workflow ci.yml --limit 5"},
            {"command": "gh run view", "description": "Pozwala wybrać uruchomienie i wyświetlić jego wynik.", "example": "$ gh run view"},
        ],
        "practice_task": (
            "Przygotuj ćwiczeniowy <code>.github/workflows/ci.yml</code> dla <code>orders-api</code>. "
            "Ustaw <code>on</code> dla push do main i pull_request do main, "
            "<code>permissions: contents: read</code> oraz job <code>checks</code> na "
            "<code>ubuntu-latest</code>. Dodaj kroki checkout i setup-python z wersją Python 3.12, "
            "a potem krok <code>python --version</code>. Opisz, który element uruchamia workflow, "
            "który wybiera runner i gdzie zobaczysz wynik. Nie wysyłaj zmian do repozytorium w tym ćwiczeniu."
        ),
        "common_mistakes": [
            "Uznawanie przejścia testów CI za automatyczne wdrożenie produkcyjne.",
            "Mylenie zdarzenia on z poleceniem run.",
            "Zakładanie, że drugi job widzi pliki pierwszego bez artifactu.",
            "Nadawanie tokenowi workflow praw zapisu bez potrzeby.",
            "Umieszczanie definicji workflow poza .github/workflows.",
        ],
        "summary": (
            "Workflow określa zdarzenia, zadania, runnery i kroki. Checkout udostępnia kod, "
            "setup-python przygotowuje środowisko, a uprawnienia tokenu powinny być minimalne. "
            "CI weryfikuje zmianę przed dalszym dostarczaniem."
        ),
    },
    "quiz": {
        "title": "Quiz: pierwszy workflow GitHub Actions",
        "description": "Sprawdź strukturę i znaczenie elementów workflow.",
        "questions": [
            {"text": "Co uruchomi workflow po otwarciu PR do main?", "answers": [("a", "Zdarzenie pull_request w sekcji on", True), ("b", "Sama nazwa joba", False), ("c", "Pole permissions", False), ("d", "Katalog app/content", False)]},
            {"text": "Gdzie wskazuje się środowisko wykonania joba?", "answers": [("a", "W runs-on", True), ("b", "W on", False), ("c", "W nazwie artifactu", False), ("d", "W pliku requirements.txt", False)]},
            {"text": "Który krok udostępnia kod repozytorium runnerowi?", "answers": [("a", "actions/checkout", True), ("b", "docker stop", False), ("c", "pg_isready", False), ("d", "EXPOSE 8000", False)]},
            {"text": "Co oznacza permissions: contents: read?", "answers": [("a", "Token ma prawo odczytu zawartości repozytorium", True), ("b", "Token może usunąć repozytorium", False), ("c", "Każdy job ma prawa administratora", False), ("d", "Workflow nie potrzebuje checkout", False)]},
            {"text": "Czy zielony job CI dowodzi, że aplikacja jest wdrożona?", "answers": [("a", "Nie, wdrożenie wymaga osobnego procesu", True), ("b", "Tak, każdy workflow wdraża automatycznie", False), ("c", "Tak, jeśli użyto ubuntu-latest", False), ("d", "Tak, jeśli PR ma opis", False)]},
            {"text": "Dwa joby potrzebują tych samych wygenerowanych plików. Co jest wymagane?", "answers": [("a", "Jawne przekazanie wyniku, na przykład jako artifact", True), ("b", "Założenie, że runner ma wspólny dysk", False), ("c", "Zmiana portu 8000 na 5432", False), ("d", "Usunięcie sekcji on", False)]},
        ],
    },
    "flashcards": [
        {"question": "Co oznacza CI?", "answer": "Ciągłą integrację zmian z automatycznym sprawdzaniem."},
        {"question": "Co oznacza CD?", "answer": "Automatyzację dostarczania lub wdrażania zmian."},
        {"question": "Czy CI automatycznie wdraża aplikację?", "answer": "Nie, potrzebny jest osobny proces dostarczenia."},
        {"question": "Gdzie są pliki GitHub Actions?", "answer": "W .github/workflows/ repozytorium."},
        {"question": "Czym jest workflow?", "answer": "Definicją automatycznego procesu w pliku YAML."},
        {"question": "Co określa on?", "answer": "Zdarzenia uruchamiające workflow."},
        {"question": "Co oznacza push w on?", "answer": "Uruchomienie po wypchnięciu zmian na wskazaną gałąź."},
        {"question": "Co oznacza pull_request w on?", "answer": "Uruchomienie dla zdarzeń dotyczących PR."},
        {"question": "Czym jest job?", "answer": "Zadaniem workflow wykonywanym na runnerze."},
        {"question": "Co ustala runs-on?", "answer": "Rodzaj runnera wykonującego job."},
        {"question": "Czym jest runner?", "answer": "Środowiskiem uruchamiającym kroki joba."},
        {"question": "Co zawiera steps?", "answer": "Uporządkowaną listę kroków joba."},
        {"question": "Co robi run w kroku?", "answer": "Wykonuje polecenie powłoki."},
        {"question": "Co robi uses w kroku?", "answer": "Uruchamia wskazaną akcję GitHub Actions."},
        {"question": "Po co actions/checkout?", "answer": "Pobiera kod repozytorium na runner."},
        {"question": "Po co actions/setup-python?", "answer": "Wybiera wersję Pythona dla joba."},
        {"question": "Co daje contents: read?", "answer": "Prawo odczytu repozytorium dla tokenu workflow."},
        {"question": "Dlaczego ograniczać permissions?", "answer": "Aby token miał tylko uprawnienia potrzebne jobowi."},
        {"question": "Czy joby współdzielą pliki automatycznie?", "answer": "Nie, trzeba jawnie przekazać wynik."},
        {"question": "Czym jest artifact?", "answer": "Plikiem lub zbiorem plików zachowanym jako wynik workflow."},
        {"question": "Co pokazuje gh workflow list?", "answer": "Workflow dostępne w połączonym repozytorium."},
        {"question": "Co pokazuje gh run list?", "answer": "Uruchomienia workflow i ich wyniki."},
        {"question": "Gdzie czytać wynik joba?", "answer": "W uruchomieniu workflow na GitHub lub przez gh run view."},
        {"question": "Co sprawdzić po edycji YAML?", "answer": "Zdarzenia, wcięcia, joby, kroki i zakres uprawnień."},
        {"question": "Po co workflow na PR?", "answer": "Aby sprawdzić zmianę przed jej włączeniem do gałęzi głównej."},
    ],
}
