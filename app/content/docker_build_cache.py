DOCKER_BUILD_CACHE = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "Budowanie obrazów: kontekst, .dockerignore i cache",
        "level": "Średnio zaawansowany",
        "duration": "55 min",
        "description": "Ograniczysz kontekst budowania i wykorzystasz cache bez ukrywania zmian w zależnościach.",
        "theory": (
            "Ostatnia kropka w <code>docker build -t orders-api:local .</code> wskazuje kontekst budowania. "
            "Instrukcja <code>COPY</code> może odczytać tylko pliki dostępne w tym kontekście. Przesłanie "
            "całego repozytorium wraz z <code>.git</code>, lokalną bazą i plikami środowiskowymi jest "
            "niepotrzebne oraz ryzykowne. <code>.dockerignore</code> wyklucza takie ścieżki przed budową; "
            "nie zastępuje jednak <code>.gitignore</code>. Docker korzysta z cache warstw, gdy instrukcja "
            "i jej wejście nie zmieniły się. Dlatego najpierw kopiuj <code>requirements.txt</code> i instaluj "
            "zależności, a dopiero później kopiuj częściej zmieniany kod. Zmiana kodu nie powinna wtedy "
            "ponownie instalować pakietów. Zmiana pliku zależności musi tę warstwę unieważnić. Opcja "
            "<code>--no-cache</code> wymusza pełną przebudowę, ale nie jest domyślnym rozwiązaniem "
            "problemów. <code>docker image inspect</code> i <code>docker history</code> pomagają obejrzeć "
            "wynik. Do wydania produkcyjnego potrzebny jest kontrolowany tag lub digest oraz sprawdzenie, "
            "czy w obrazie nie ma prywatnych plików."
        ),
        "commands": [
            {"command": "docker build -t orders-api:local .", "description": "Buduje obraz z bieżącego katalogu jako kontekstu.", "example": "$ docker build -t orders-api:local ."},
            {"command": "cat .dockerignore", "description": "Pozwala sprawdzić reguły wykluczania plików z kontekstu.", "example": "$ cat .dockerignore\n.git\n.venv\n__pycache__\n.env\napp/data"},
            {"command": "docker build --progress=plain -t orders-api:local .", "description": "Pokazuje szczegółowy przebieg budowy i użycie cache.", "example": "$ docker build --progress=plain -t orders-api:local ."},
            {"command": "docker build --no-cache -t orders-api:rebuild .", "description": "Buduje bez cache, gdy świadomie trzeba odtworzyć wszystkie kroki.", "example": "$ docker build --no-cache -t orders-api:rebuild ."},
            {"command": "docker history orders-api:local", "description": "Pokazuje warstwy końcowego obrazu.", "example": "$ docker history orders-api:local"},
            {"command": "docker image inspect orders-api:local", "description": "Odczytuje metadane i identyfikator zbudowanego obrazu.", "example": "$ docker image inspect orders-api:local"},
        ],
        "practice_task": (
            "Dodaj do projektu <code>orders-api</code> plik <code>.dockerignore</code> z wykluczeniem "
            "<code>.git</code>, <code>.venv</code>, <code>__pycache__</code>, <code>.env</code> i lokalnych "
            "danych. Zbuduj obraz dwa razy z <code>--progress=plain</code>, zmień tylko kod aplikacji i "
            "zbuduj ponownie. Zapisz, które kroki użyły cache, a które się powtórzyły. Potem zmień "
            "<code>requirements.txt</code> i wyjaśnij różnicę."
        ),
        "common_mistakes": [
            "Wysyłanie sekretów i lokalnych danych do kontekstu budowania.",
            "Zakładanie, że .gitignore automatycznie zastępuje .dockerignore.",
            "Kopiowanie całego projektu przed instalacją zależności.",
            "Używanie --no-cache przy każdej budowie bez potrzeby.",
        ],
        "summary": (
            "Kontekst określa, które pliki może widzieć budowa. .dockerignore ogranicza jego rozmiar "
            "i ryzyko wycieku. Dobra kolejność COPY i RUN pozwala wykorzystywać cache zależności "
            "bez pomijania rzeczywistych zmian."
        ),
    },
    "quiz": {
        "title": "Quiz: kontekst budowania i cache obrazu",
        "description": "Wybierz właściwe kroki przy budowaniu obrazu aplikacji.",
        "questions": [
            {"text": "Co oznacza kropka na końcu docker build -t orders-api:local .?", "answers": [("a", "Bieżący katalog jest kontekstem budowania", True), ("b", "Obraz ma trafić do katalogu domowego", False), ("c", "Kontener ma działać w tle", False), ("d", "Tag zostanie automatycznie usunięty", False)]},
            {"text": "Do kontekstu trafia lokalny plik .env. Co należy zrobić?", "answers": [("a", "Wykluczyć go przez .dockerignore i trzymać poza obrazem", True), ("b", "Skopiować go jako pierwszą warstwę", False), ("c", "Dodać go do CMD", False), ("d", "Opublikować port bazy", False)]},
            {"text": "Zmienił się tylko app/main.py. Jak zachować cache instalacji pakietów?", "answers": [("a", "Kopiować i instalować requirements.txt przed kopiowaniem kodu", True), ("b", "Używać --no-cache przy każdej budowie", False), ("c", "Kopiować cały projekt przed RUN pip", False), ("d", "Usunąć WORKDIR", False)]},
            {"text": "Czy .gitignore wystarcza do wykluczenia pliku z kontekstu Docker?", "answers": [("a", "Nie, potrzebny jest .dockerignore", True), ("b", "Tak, Docker zawsze czyta wyłącznie .gitignore", False), ("c", "Tak, jeśli port jest opublikowany", False), ("d", "Tak, gdy używa się CMD", False)]},
            {"text": "Co powinno się stać po zmianie requirements.txt?", "answers": [("a", "Warstwa instalacji zależności powinna zostać przebudowana", True), ("b", "Docker powinien bezwarunkowo użyć starej warstwy", False), ("c", "Kontener powinien usunąć volume", False), ("d", "Tag powinien zamienić się w port", False)]},
            {"text": "Kiedy użyć docker build --no-cache?", "answers": [("a", "Gdy świadomie potrzebna jest pełna przebudowa bez cache", True), ("b", "Zawsze przy drobnej zmianie kodu", False), ("c", "Do wyświetlenia działających kontenerów", False), ("d", "Do zablokowania sekretów w obrazie", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest kontekst budowania?", "answer": "Zbiorem plików udostępnionych poleceniu docker build."},
        {"question": "Co oznacza końcowa kropka w docker build?", "answer": "Kontekstem jest bieżący katalog."},
        {"question": "Czy COPY sięgnie poza kontekst?", "answer": "Nie, źródło musi być dostępne w kontekście."},
        {"question": "Po co .dockerignore?", "answer": "Wyklucza zbędne i wrażliwe pliki z kontekstu."},
        {"question": "Czy .gitignore zastępuje .dockerignore?", "answer": "Nie, to odrębne mechanizmy."},
        {"question": "Czy .env powinien wejść do obrazu?", "answer": "Nie, może zawierać poufne dane środowiska."},
        {"question": "Po co wykluczyć .git?", "answer": "Aby nie przesyłać historii repozytorium do budowy."},
        {"question": "Po co wykluczyć .venv?", "answer": "Aby nie kopiować lokalnego środowiska Pythona do obrazu."},
        {"question": "Po co wykluczyć __pycache__?", "answer": "To lokalne pliki pomocnicze, zbędne w kontekście."},
        {"question": "Co cache zapisuje przy budowie?", "answer": "Wyniki kroków, których wejście się nie zmieniło."},
        {"question": "Co unieważnia cache instrukcji COPY?", "answer": "Zmiana kopiowanych plików lub instrukcji."},
        {"question": "Dlaczego requirements.txt kopiować wcześnie?", "answer": "Aby zmianą kodu nie przebudowywać instalacji zależności."},
        {"question": "Co unieważnia warstwę pip install?", "answer": "Zmiana zależności lub wcześniejszej warstwy."},
        {"question": "Jak zobaczyć szczegóły budowy?", "answer": "Użyć docker build --progress=plain."},
        {"question": "Co robi --no-cache?", "answer": "Pomija wcześniejsze wyniki kroków budowy."},
        {"question": "Czy --no-cache jest domyślnym wyborem?", "answer": "Nie, pozbawia budowę korzyści z cache."},
        {"question": "Co sprawdza docker history?", "answer": "Warstwy wynikowego obrazu."},
        {"question": "Co sprawdza docker image inspect?", "answer": "Metadane obrazu, w tym jego identyfikator."},
        {"question": "Po co tag orders-api:local?", "answer": "Rozróżnia lokalny wariant obrazu od innych wersji."},
        {"question": "Czy tag gwarantuje te same bajty?", "answer": "Nie, do tego lepiej służy digest."},
        {"question": "Co ogranicza mały kontekst?", "answer": "Transfer, czas budowy i ryzyko dołączenia prywatnych plików."},
        {"question": "Jak sprawdzić wpływ zmiany kodu na cache?", "answer": "Porównać szczegółowe logi kolejnych budów."},
        {"question": "Czy Dockerfile powinien kopiować lokalną bazę?", "answer": "Nie, dane aplikacji należy trzymać poza obrazem."},
        {"question": "Kiedy warto pełną przebudowę?", "answer": "Gdy trzeba świadomie wyeliminować wpływ wcześniejszego cache."},
        {"question": "Co decyduje o odtwarzalności wydania?", "answer": "Kontrola wersji obrazu bazowego i zależności oraz wynikowej zawartości."},
    ],
}
