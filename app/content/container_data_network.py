CONTAINER_DATA_NETWORK = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "Dane, porty i sieć kontenerów",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": "Udostępnisz usługę na hoście, podłączysz trwałe dane i połączysz dwa kontenery prywatną siecią.",
        "theory": (
            "Zapisy w zwykłej warstwie kontenera znikają wraz z jego usunięciem. Nazwany volume przechowuje "
            "dane poza cyklem życia instancji i można go podłączyć ponownie. Publikacja portu przez "
            "<code>-p 127.0.0.1:8080:80</code> łączy port 8080 lokalnego hosta z portem 80 kontenera. "
            "Adres <code>127.0.0.1</code> ogranicza dostęp do hosta; pominięcie adresu może wystawić usługę "
            "na wszystkich interfejsach. Samo <code>EXPOSE</code> w obrazie nie publikuje portu. Sieć "
            "zdefiniowana przez użytkownika pozwala kontenerom komunikować się po nazwach; nazwa kontenera "
            "jest wtedy rozwiązywana przez wbudowany DNS Dockera. Ruch między kontenerami na tej samej "
            "sieci nie wymaga publikowania portu bazy na hoście. Zmienne środowiskowe przekazują konfigurację "
            "w czasie uruchomienia, ale ich wartości mogą być widoczne w metadanych kontenera, więc nie należy "
            "wkładać tam niekontrolowanie sekretów. W produkcji użyj mechanizmu sekretów i ogranicz dostęp do "
            "hosta. Po ćwiczeniu usuń kontenery i sieć, a volume zachowaj do sprawdzenia trwałości."
        ),
        "commands": [
            {"command": "docker volume create orders-data", "description": "Tworzy nazwany magazyn danych niezależny od kontenera.", "example": "$ docker volume create orders-data"},
            {"command": "docker network create orders-net", "description": "Tworzy sieć dla usług, które mają się odnajdywać po nazwie.", "example": "$ docker network create orders-net"},
            {"command": "docker run -d --name orders-web --network orders-net -p 127.0.0.1:8080:80 -v orders-data:/usr/share/nginx/html nginx:1.28", "description": "Uruchamia usługę z lokalnie opublikowanym portem i podłączonym volume.", "example": "$ docker run -d --name orders-web --network orders-net -p 127.0.0.1:8080:80 -v orders-data:/usr/share/nginx/html nginx:1.28"},
            {"command": "curl -I http://127.0.0.1:8080/", "description": "Sprawdza odpowiedź usługi przez port hosta.", "example": "$ curl -I http://127.0.0.1:8080/"},
            {"command": "docker run --rm --network orders-net nginx:1.28 getent hosts orders-web", "description": "Sprawdza rozwiązywanie nazwy kontenera w tej samej sieci.", "example": "$ docker run --rm --network orders-net nginx:1.28 getent hosts orders-web"},
            {"command": "docker volume inspect orders-data", "description": "Odczytuje metadane magazynu danych.", "example": "$ docker volume inspect orders-data"},
            {"command": "docker network inspect orders-net", "description": "Pokazuje podłączone kontenery i konfigurację sieci.", "example": "$ docker network inspect orders-net"},
        ],
        "practice_task": (
            "Utwórz <code>orders-data</code> i <code>orders-net</code>, uruchom <code>orders-web</code> tylko "
            "na adresie lokalnym hosta i potwierdź odpowiedź przez <code>curl</code>. W drugim kontenerze "
            "sprawdź, czy nazwa <code>orders-web</code> rozwiązuje się w tej sieci. Porównaj port hosta "
            "z portem wewnątrz kontenera. Zatrzymaj i usuń usługę, lecz zachowaj volume; sprawdź, że "
            "nadal figuruje na liście."
        ),
        "common_mistakes": [
            "Zakładanie, że EXPOSE automatycznie wystawia usługę na hoście.",
            "Publikowanie portu bazy danych mimo komunikacji wyłącznie wewnątrz sieci.",
            "Przechowywanie ważnych danych tylko w zapisywalnej warstwie kontenera.",
            "Uznawanie zmiennej środowiskowej za bezpieczny sejf na sekrety.",
            "Mylenie portu hosta z portem procesu w kontenerze.",
        ],
        "summary": (
            "Volume zachowuje dane po usunięciu instancji, publikacja portu udostępnia usługę hostowi, "
            "a prywatna sieć umożliwia komunikację kontenerów po nazwach. Zakres publikacji portu i "
            "sposób podania sekretów trzeba dobrać świadomie."
        ),
    },
    "quiz": {
        "title": "Quiz: dane, porty i sieć kontenerów",
        "description": "Sprawdź trwałość danych i komunikację usług.",
        "questions": [
            {"text": "Po usunięciu kontenera baza ma zachować dane. Gdzie je umieścisz?", "answers": [("a", "W nazwanym volume podłączonym do katalogu danych", True), ("b", "Wyłącznie w zapisywalnej warstwie kontenera", False), ("c", "W tagu obrazu", False), ("d", "W nazwie sieci", False)]},
            {"text": "Co oznacza -p 127.0.0.1:8080:80?", "answers": [("a", "Port 8080 lokalnego hosta prowadzi do portu 80 kontenera", True), ("b", "Port 80 hosta prowadzi do portu 8080 kontenera", False), ("c", "Oba porty są dostępne tylko z registry", False), ("d", "Tworzy volume o numerze 8080", False)]},
            {"text": "Dwie usługi na tej samej sieci użytkownika mają się odnajdywać. Czego użyje klient?", "answers": [("a", "Nazwy kontenera lub usługi w tej sieci", True), ("b", "Zawsze adresu 127.0.0.1 klienta", False), ("c", "Tagu obrazu zamiast hosta", False), ("d", "Numeru volume jako adresu DNS", False)]},
            {"text": "Czy EXPOSE 80 samo udostępni usługę poza kontenerem?", "answers": [("a", "Nie, publikację portu ustala się przy uruchomieniu", True), ("b", "Tak, zawsze na wszystkich interfejsach", False), ("c", "Tak, ale tylko po docker volume create", False), ("d", "Tak, po docker images", False)]},
            {"text": "Aplikacja łączy się z bazą w tej samej prywatnej sieci. Czy trzeba publikować port bazy na hoście?", "answers": [("a", "Nie, komunikacja sieciowa między kontenerami nie wymaga tego", True), ("b", "Tak, bez publikacji nie działa DNS", False), ("c", "Tak, volume wymaga portu 5432", False), ("d", "Tak, każde połączenie musi przejść przez localhost hosta", False)]},
            {"text": "Dlaczego nie należy traktować zwykłej zmiennej środowiskowej jako sejfu?", "answers": [("a", "Jej wartość może być widoczna w metadanych i dla uprawnionych procesów", True), ("b", "Nie może przechowywać tekstu", False), ("c", "Docker automatycznie publikuje ją w registry", False), ("d", "Zawsze usuwa volume", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest nazwany volume?", "answer": "Magazynem danych zarządzanym przez Dockera poza życiem kontenera."},
        {"question": "Co robi docker volume create?", "answer": "Tworzy nazwany magazyn danych."},
        {"question": "Czy docker rm usuwa automatycznie nazwany volume?", "answer": "Nie, volume pozostaje niezależnie od kontenera."},
        {"question": "Co oznacza -v orders-data:/data?", "answer": "Podłącza volume orders-data pod /data w kontenerze."},
        {"question": "Co dzieje się z zapisem w warstwie kontenera po jego usunięciu?", "answer": "Zapis znika razem z instancją."},
        {"question": "Co oznacza pierwsza liczba w -p 8080:80?", "answer": "Port hosta."},
        {"question": "Co oznacza druga liczba w -p 8080:80?", "answer": "Port procesu w kontenerze."},
        {"question": "Po co wskazać 127.0.0.1 przy -p?", "answer": "Aby ograniczyć publikację do lokalnego interfejsu hosta."},
        {"question": "Czy EXPOSE publikuje port?", "answer": "Nie, dokumentuje zamiar użycia portu w obrazie."},
        {"question": "Do czego służy docker network create?", "answer": "Tworzy sieć, do której można podłączyć kontenery."},
        {"question": "Jak kontenery odnajdują się w sieci użytkownika?", "answer": "Przez DNS rozpoznający ich nazwy."},
        {"question": "Czy baza musi mieć -p dla aplikacji w tej samej sieci?", "answer": "Nie, wewnętrzny ruch nie wymaga portu hosta."},
        {"question": "Co pokaże docker network inspect?", "answer": "Konfigurację sieci i listę podłączonych kontenerów."},
        {"question": "Co pokaże docker volume inspect?", "answer": "Metadane volume, w tym punkt przechowywania."},
        {"question": "Co sprawdza curl -I?", "answer": "Nagłówki odpowiedzi HTTP usługi."},
        {"question": "Co oznacza localhost wewnątrz kontenera?", "answer": "Ten sam kontener, a nie inny kontener ani host."},
        {"question": "Kiedy publikować port na hoście?", "answer": "Gdy usługa ma być osiągalna z hosta lub z zewnątrz."},
        {"question": "Czym różni się sieć od volume?", "answer": "Sieć przenosi ruch, a volume przechowuje dane."},
        {"question": "Jak przekazać zwykłą konfigurację przy docker run?", "answer": "Przez -e NAZWA=wartość lub kontrolowany plik env."},
        {"question": "Czy env chroni sekret przed administratorami Dockera?", "answer": "Nie, uprawnione osoby mogą odczytać konfigurację kontenera."},
        {"question": "Co grozi przy -p 8080:80 bez adresu?", "answer": "Port może być dostępny na wszystkich interfejsach hosta."},
        {"question": "Po co odróżniać port hosta od portu kontenera?", "answer": "Aby poprawnie skonfigurować klienta i zakres dostępu."},
        {"question": "Co przetestować po publikacji portu?", "answer": "Rzeczywistą odpowiedź usługi na wskazanym adresie hosta."},
        {"question": "Jak sprawdzić, czy volume przetrwał usunięcie kontenera?", "answer": "Odczytać listę przez docker volume ls."},
        {"question": "Co ogranicza powierzchnię dostępu do bazy?", "answer": "Brak publikacji jej portu i użycie prywatnej sieci."},
    ],
}
