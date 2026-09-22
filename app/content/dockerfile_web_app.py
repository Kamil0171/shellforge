DOCKERFILE_WEB_APP = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "Dockerfile dla aplikacji webowej",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": "Zapiszesz instrukcje budowania obrazu prostej aplikacji Python i odróżnisz etap budowy od uruchomienia.",
        "theory": (
            "Dockerfile jest przepisem na obraz, a nie skryptem uruchamianym przy każdym starcie kontenera. "
            "<code>FROM</code> wybiera obraz bazowy, <code>WORKDIR</code> ustala katalog roboczy, "
            "<code>COPY</code> przenosi pliki z kontekstu budowania, a <code>RUN</code> wykonuje polecenie "
            "podczas budowy. <code>CMD</code> określa domyślny proces, który użytkownik może zastąpić "
            "argumentami <code>docker run</code>. <code>ENTRYPOINT</code> ustala wykonywalny punkt wejścia; "
            "argumenty z <code>CMD</code> mogą być jego domyślnymi parametrami. Dla aplikacji ASGI wystarczy "
            "jedno czytelne <code>CMD</code> z Uvicornem. <code>EXPOSE 8000</code> dokumentuje port wewnątrz "
            "obrazu, ale go nie publikuje. <code>ENV</code> nadaje niepoufne wartości domyślne; sekretów nie "
            "wolno wpisywać do Dockerfile, bo zostaną utrwalone w obrazie. W ćwiczeniu <code>orders-api</code> "
            "ma plik <code>requirements.txt</code> oraz punkt wejścia <code>app.main:app</code>. "
            "Uvicorn musi nasłuchiwać na <code>0.0.0.0</code> wewnątrz kontenera, aby ruch przez opublikowany "
            "port mógł do niego dotrzeć. Następne lekcje poprawią cache i bezpieczeństwo tego prostego obrazu."
        ),
        "commands": [
            {"command": "FROM python:3.12-slim", "description": "Wybiera bazowy obraz Pythona; w projekcie wersję należy kontrolować.", "example": "FROM python:3.12-slim"},
            {"command": "WORKDIR /srv/orders-api", "description": "Ustala katalog dla kolejnych instrukcji.", "example": "WORKDIR /srv/orders-api"},
            {"command": "COPY requirements.txt .", "description": "Kopiuje listę zależności z kontekstu do obrazu.", "example": "COPY requirements.txt ."},
            {"command": "RUN python -m pip install --no-cache-dir -r requirements.txt", "description": "Instaluje zależności na etapie budowy.", "example": "RUN python -m pip install --no-cache-dir -r requirements.txt"},
            {"command": "COPY app ./app", "description": "Kopiuje kod aplikacji po instalacji zależności.", "example": "COPY app ./app"},
            {"command": "ENV PYTHONDONTWRITEBYTECODE=1", "description": "Ustawia niepoufną domyślną konfigurację Pythona.", "example": "ENV PYTHONDONTWRITEBYTECODE=1"},
            {"command": "EXPOSE 8000", "description": "Dokumentuje wewnętrzny port serwera.", "example": "EXPOSE 8000"},
            {"command": "CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]", "description": "Definiuje domyślny proces aplikacji w formie exec.", "example": "CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]"},
            {"command": "ENTRYPOINT [\"python\"]", "description": "Alternatywny wariant Dockerfile: stały program z argumentami w CMD, zamiast wcześniejszego CMD uruchamiającego Uvicorn.", "example": "ENTRYPOINT [\"python\"]\nCMD [\"-m\", \"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]"},
        ],
        "practice_task": (
            "Napisz Dockerfile dla <code>orders-api</code> z plikami <code>requirements.txt</code> i "
            "<code>app/main.py</code>. Ułóż instalację zależności przed kopiowaniem kodu, dodaj "
            "<code>EXPOSE 8000</code> i <code>CMD</code> dla Uvicorna. Zbuduj obraz poleceniem "
            "<code>docker build -t orders-api:local .</code> i uruchom go z publikacją portu tylko na "
            "<code>127.0.0.1</code>. Sprawdź endpoint przez <code>curl</code>; nie dodawaj haseł do obrazu."
        ),
        "common_mistakes": [
            "Mylenie RUN, wykonywanego przy budowie, z CMD, uruchamianym przy starcie.",
            "Używanie 127.0.0.1 jako adresu nasłuchu Uvicorna wewnątrz kontenera.",
            "Zakładanie, że EXPOSE zastępuje publikację portu przez -p.",
            "Zapisywanie hasła przez ENV lub RUN w warstwach obrazu.",
            "Kopiowanie kodu przed zależnościami, co niepotrzebnie unieważnia cache instalacji.",
        ],
        "summary": (
            "Dockerfile opisuje obraz krok po kroku. FROM, WORKDIR, COPY i RUN budują środowisko, "
            "CMD uruchamia proces, a EXPOSE dokumentuje port. Sekrety i konfiguracja środowiska "
            "powinny być dostarczane poza obrazem."
        ),
    },
    "quiz": {
        "title": "Quiz: Dockerfile dla aplikacji webowej",
        "description": "Sprawdź rolę instrukcji Dockerfile w obrazie aplikacji.",
        "questions": [
            {"text": "Zależności mają być zainstalowane przy budowaniu obrazu. Która instrukcja to robi?", "answers": [("a", "RUN python -m pip install -r requirements.txt", True), ("b", "CMD python -m pip install -r requirements.txt", False), ("c", "EXPOSE requirements.txt", False), ("d", "ENV requirements.txt", False)]},
            {"text": "Uvicorn działa w kontenerze, ale opublikowany port nie odpowiada. Jaki adres nasłuchu sprawdzisz?", "answers": [("a", "0.0.0.0 wewnątrz kontenera", True), ("b", "Wyłącznie 127.0.0.1 wewnątrz kontenera", False), ("c", "Adres registry", False), ("d", "Nazwę volume", False)]},
            {"text": "Co robi EXPOSE 8000 bez opcji -p przy docker run?", "answers": [("a", "Dokumentuje port, nie publikuje go na hoście", True), ("b", "Publikuje port na całym internecie", False), ("c", "Uruchamia Uvicorna", False), ("d", "Tworzy sieć o numerze 8000", False)]},
            {"text": "Dlaczego nie wpisywać hasła w ENV Dockerfile?", "answers": [("a", "Wartość utrwali się w metadanych obrazu", True), ("b", "ENV działa tylko dla numerów", False), ("c", "Hasło zablokuje instrukcję FROM", False), ("d", "Docker usunie cały obraz", False)]},
            {"text": "Jak wskazać domyślny proces aplikacji uruchamiany przy starcie?", "answers": [("a", "Przez CMD w Dockerfile", True), ("b", "Przez COPY requirements.txt", False), ("c", "Przez docker history", False), ("d", "Przez docker volume ls", False)]},
            {"text": "Kiedy wykona się instrukcja RUN w Dockerfile?", "answers": [("a", "Podczas budowania obrazu", True), ("b", "Przy każdym żądaniu HTTP", False), ("c", "Dopiero po docker stop", False), ("d", "Tylko przy pobieraniu z registry", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest Dockerfile?", "answer": "Plikiem instrukcji budowania obrazu."},
        {"question": "Co wskazuje FROM?", "answer": "Bazowy obraz lub etap budowania."},
        {"question": "Co ustala WORKDIR?", "answer": "Katalog roboczy kolejnych instrukcji i procesu."},
        {"question": "Co robi COPY?", "answer": "Przenosi pliki z kontekstu budowania do obrazu."},
        {"question": "Kiedy działa RUN?", "answer": "Podczas budowania obrazu."},
        {"question": "Kiedy działa CMD?", "answer": "Jako domyślny proces przy starcie kontenera."},
        {"question": "Do czego służy ENTRYPOINT?", "answer": "Ustala wykonywalny punkt wejścia kontenera."},
        {"question": "Jak współpracują ENTRYPOINT i CMD?", "answer": "CMD może dostarczyć domyślne argumenty dla ENTRYPOINT."},
        {"question": "Czy docker run może zastąpić CMD?", "answer": "Tak, podając inne polecenie po nazwie obrazu."},
        {"question": "Co oznacza forma exec CMD?", "answer": "Listę JSON z programem i argumentami, bez pośredniej powłoki."},
        {"question": "Czy EXPOSE publikuje port hosta?", "answer": "Nie, tylko dokumentuje port wewnętrzny."},
        {"question": "Jak opublikować port przy uruchomieniu?", "answer": "Opcją -p polecenia docker run."},
        {"question": "Po co ENV w Dockerfile?", "answer": "Do niepoufnych wartości domyślnych obrazu."},
        {"question": "Dlaczego nie umieszczać sekretu w Dockerfile?", "answer": "Może pozostać w warstwach lub metadanych obrazu."},
        {"question": "Co oznacza app.main:app?", "answer": "Moduł Python app.main i obiekt ASGI app."},
        {"question": "Dlaczego Uvicorn w kontenerze używa 0.0.0.0?", "answer": "Aby odbierać ruch docierający do interfejsu kontenera."},
        {"question": "Po co kopiować requirements.txt osobno?", "answer": "Aby zmianą kodu nie unieważniać warstwy instalacji zależności."},
        {"question": "Co robi --no-cache-dir w pip?", "answer": "Nie zachowuje lokalnego cache pobranych pakietów w obrazie."},
        {"question": "Co oznacza python:3.12-slim?", "answer": "Obraz Python 3.12 w wariancie slim."},
        {"question": "Czy sam Dockerfile tworzy obraz?", "answer": "Nie, trzeba wywołać docker build."},
        {"question": "Co robi docker build -t orders-api:local .?", "answer": "Buduje obraz z bieżącego katalogu i nadaje mu tag."},
        {"question": "Co jest kontekstem w docker build ... .?", "answer": "Bieżący katalog przesłany do procesu budowania."},
        {"question": "Jak sprawdzić aplikację po uruchomieniu obrazu?", "answer": "Opublikować port i wysłać żądanie curl do endpointu."},
        {"question": "Czy WORKDIR tworzy katalog, gdy go brak?", "answer": "Tak, Docker tworzy wskazany katalog w obrazie."},
        {"question": "Co stanie się z CMD, gdy proces zakończy pracę?", "answer": "Kontener również zakończy działanie."},
    ],
}
