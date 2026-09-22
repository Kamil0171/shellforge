PIPELINE_DELIVERY_DIAGNOSTICS = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "Dostarczanie zmian i diagnostyka pipeline",
        "level": "Średnio zaawansowany",
        "duration": "70 min",
        "description": "Zaprojektujesz kontrolowane przejście od PR i testów do kandydata wydania oraz zdiagnozujesz błąd workflow.",
        "theory": (
            "Praca nad zmianą zaczyna się na osobnej gałęzi. PR uruchamia CI, a jego wynik jest bramką "
            "przed włączeniem kodu do <code>main</code>. Po zatwierdzeniu można zbudować wersjonowany "
            "obraz i zachować identyfikator commita oraz wynik testów. Artifact jest wynikiem workflow; "
            "nie powinien zawierać sekretów. Etap dostarczania może przygotować obraz i instrukcję "
            "wydania, a właściwy deployment wymaga osobnego joba zależnego od testów, jawnego wyzwalacza "
            "i kontroli środowiska. <code>needs: checks</code> wiąże job z wynikiem jakości. "
            "<code>workflow_dispatch</code> pozwala na ręczne uruchomienie; reguły środowiska GitHub "
            "mogą wymagać zatwierdzenia przed użyciem sekretów. Token <code>GITHUB_TOKEN</code> powinien "
            "mieć minimalne uprawnienia, a poświadczenia zewnętrzne należy pobierać z kontrolowanych "
            "sekretów lub krótkotrwałej tożsamości. Nie przekazuj ich do joba testującego nieufny PR. "
            "Przy niepowodzeniu znajdź pierwszą błędną fazę: trigger, runner, checkout, instalacja, "
            "test, build albo uprawnienia. Czytaj log konkretnego kroku i porównaj komendy z lokalnym "
            "wynikiem. Powtórne uruchomienie bez diagnozy może ukryć niestabilny test; wynik, commit "
            "i przyczynę zapisz przed kolejną próbą."
        ),
        "commands": [
            {"command": "git status --short", "description": "Sprawdza stan zmian przed przygotowaniem PR.", "example": "$ git status --short"},
            {"command": "git rev-parse HEAD", "description": "Zapisuje dokładny commit związany z wynikiem CI.", "example": "$ git rev-parse HEAD"},
            {"command": "gh run list --limit 5", "description": "Pokazuje najnowsze uruchomienia workflow.", "example": "$ gh run list --limit 5"},
            {"command": "gh run view --log-failed", "description": "Pozwala wybrać uruchomienie i odczytać log nieudanych kroków.", "example": "$ gh run view --log-failed"},
            {"command": "gh run view", "description": "Otwiera szczegóły wybranego uruchomienia w CLI.", "example": "$ gh run view"},
            {"command": "needs: checks", "description": "Fragment YAML uzależniający job dostarczania od pozytywnego wyniku kontroli.", "example": "jobs:\n  checks:\n    runs-on: ubuntu-latest\n    steps:\n      - run: pytest\n  delivery:\n    needs: checks\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo 'Kontrole zakończone'"},
        ],
        "practice_task": (
            "Rozpisz dla <code>orders-api</code> drogę zmiany: branch, PR, wynik Ruff i pytest, "
            "budowa obrazu, identyfikator commita, kontrolowany job dostarczenia oraz osobna decyzja "
            "o wdrożeniu. W ćwiczeniowym YAML dodaj <code>needs: checks</code> i wyzwalacz "
            "<code>workflow_dispatch</code> dla etapu wymagającego decyzji operatora; nie dodawaj "
            "prawdziwego wdrożenia. Na przygotowanym nieudanym uruchomieniu znajdź pierwszy błędny "
            "krok przez <code>gh run view --log-failed</code>, zapisz przyczynę i lokalną komendę do "
            "odtworzenia problemu."
        ),
        "common_mistakes": [
            "Udzielanie sekretów jobowi uruchamianemu dla nieufnego PR.",
            "Uruchamianie joba dostarczenia bez zależności od kontroli jakości.",
            "Mylenie artifactu lub obrazu z już wykonanym wdrożeniem.",
            "Dawanie GITHUB_TOKEN szerokich praw zapisu bez uzasadnienia.",
            "Ponawianie nieudanego pipeline bez analizy pierwszego błędnego kroku.",
            "Brak zapisu commita odpowiadającego przygotowanemu wydaniu.",
        ],
        "summary": (
            "CI sprawdza PR, a późniejszy etap może przygotować wersjonowany wynik do dostarczenia. "
            "Job zależny od testów, kontrolowane sekrety i jawna decyzja ograniczają ryzyko wdrożenia. "
            "Diagnoza zaczyna się od pierwszego błędnego kroku i jego logu."
        ),
    },
    "quiz": {
        "title": "Quiz: dostarczanie zmian i diagnostyka pipeline",
        "description": "Wybierz bezpieczną bramkę wydania i właściwy pierwszy krok diagnozy.",
        "questions": [
            {"text": "Job dostarczania ma ruszyć tylko po testach. Co zapiszesz w YAML?", "answers": [("a", "needs: checks", True), ("b", "EXPOSE 8000", False), ("c", "docker volume create", False), ("d", "POSTGRES_DB=checks", False)]},
            {"text": "PR z nieufnego źródła uruchamia testy. Gdzie powinny trafić sekrety wdrożeniowe?", "answers": [("a", "Tylko do osobnego, kontrolowanego joba dostarczania", True), ("b", "Do wszystkich kroków testujących PR", False), ("c", "Do publicznego artifactu", False), ("d", "Do Dockerfile w gałęzi PR", False)]},
            {"text": "Co pozwala jawnie uruchomić workflow przez operatora?", "answers": [("a", "workflow_dispatch", True), ("b", "runs-on", False), ("c", "EXPOSE", False), ("d", "pg_isready", False)]},
            {"text": "Pipeline nie przeszedł. Co sprawdzisz najpierw?", "answers": [("a", "Pierwszy błędny krok i jego log", True), ("b", "Wyłącznie ostatnią zieloną wersję", False), ("c", "Losowo ponowisz cały proces bez notatki", False), ("d", "Usuniesz historię uruchomień", False)]},
            {"text": "Co wiąże przygotowany obraz z konkretną zmianą kodu?", "answers": [("a", "Zapisany identyfikator commita i kontrolowany tag lub digest", True), ("b", "Sama nazwa localhost", False), ("c", "Dowolny ruchomy tag bez zapisu commita", False), ("d", "Nazwa katalogu .github", False)]},
            {"text": "Czy artifact zbudowany po testach oznacza działające wdrożenie?", "answers": [("a", "Nie, potrzebny jest osobny krok i weryfikacja środowiska", True), ("b", "Tak, artifact zawsze uruchamia serwer", False), ("c", "Tak, jeśli workflow ma on: push", False), ("d", "Tak, jeśli obraz ma EXPOSE", False)]},
        ],
    },
    "flashcards": [
        {"question": "Po co osobna gałąź dla zmiany?", "answer": "Pozwala sprawdzić i omówić zmianę przed włączeniem do main."},
        {"question": "Co weryfikuje CI na PR?", "answer": "Kod kandydujący do połączenia z gałęzią główną."},
        {"question": "Czym jest bramka jakości?", "answer": "Warunkiem przejścia testów i kontroli przed dalszym etapem."},
        {"question": "Co oznacza needs: checks?", "answer": "Job zależy od wcześniejszego joba checks."},
        {"question": "Po co identyfikator commita przy wydaniu?", "answer": "Wskazuje dokładny kod związany z wynikiem testów."},
        {"question": "Czym jest kandydat do wydania?", "answer": "Sprawdzonym artefaktem przygotowanym do dalszej decyzji."},
        {"question": "Czy build jest deploymentem?", "answer": "Nie, tworzy artefakt lub obraz bez uruchamiania go w środowisku."},
        {"question": "Czy artifact może zawierać sekret?", "answer": "Nie, wynik workflow powinien być oczyszczony z poufnych danych."},
        {"question": "Co robi workflow_dispatch?", "answer": "Umożliwia ręczne uruchomienie workflow."},
        {"question": "Po co chronione środowisko GitHub?", "answer": "Może wymagać zatwierdzenia przed użyciem jego sekretów."},
        {"question": "Kiedy udostępniać sekret wdrożeniowy?", "answer": "Wyłącznie kontrolowanemu jobowi, który go naprawdę potrzebuje."},
        {"question": "Czego nie dawać jobowi nieufnego PR?", "answer": "Poświadczeń produkcyjnych i nadmiernych uprawnień."},
        {"question": "Jaką zasadę stosować dla GITHUB_TOKEN?", "answer": "Najmniejsze uprawnienia wystarczające do zadania."},
        {"question": "Czy contents: read pozwala zapisać kod do repozytorium?", "answer": "Nie, daje tylko prawo odczytu zawartości."},
        {"question": "Co jest pierwszym krokiem diagnozy CI?", "answer": "Znaleźć pierwszą nieudaną fazę i jej log."},
        {"question": "Jakie fazy sprawdzać przy błędzie?", "answer": "Trigger, runner, checkout, instalację, test, build i uprawnienia."},
        {"question": "Jak znaleźć przebieg wymagający diagnozy?", "answer": "Sprawdzić statusy uruchomień przez gh run list."},
        {"question": "Do czego służy gh run view --log-failed?", "answer": "Do odczytu logów nieudanych kroków uruchomienia."},
        {"question": "Po co lokalnie odtworzyć błędną komendę?", "answer": "Ułatwia odróżnienie błędu kodu od konfiguracji runnera."},
        {"question": "Czy samo ponowienie joba rozwiązuje problem?", "answer": "Nie, może ukryć niestabilność bez rozpoznania przyczyny."},
        {"question": "Co zapisać po błędzie pipeline?", "answer": "Commit, krok, komunikat, przyczynę i wynik poprawki."},
        {"question": "Kiedy dopuszczać job dostarczania?", "answer": "Po pozytywnych testach i wymaganych zatwierdzeniach."},
        {"question": "Co odróżnia delivery od deploymentu?", "answer": "Dostarczenie przygotowuje wynik, a wdrożenie uruchamia go w środowisku."},
        {"question": "Po co zapisać digest obrazu?", "answer": "Aby wskazać dokładną zawartość wdrażanego obrazu."},
        {"question": "Jaki warunek kończy ścieżkę wydania?", "answer": "Weryfikacja działania w docelowym środowisku po wdrożeniu."},
    ],
}
