CONTAINER_BASICS = {
    "module": {
        "title": "DevOps i automatyzacja",
        "description": "Praktyczne podstawy kontenerów, obrazów aplikacji, PostgreSQL i automatyzacji dostarczania zmian.",
    },
    "lesson": {
        "title": "Podstawy konteneryzacji",
        "level": "Średnio zaawansowany",
        "duration": "50 min",
        "description": "Rozpoznasz obrazy, kontenery i rejestry oraz sprawdzisz, co rzeczywiście uruchamia Docker.",
        "theory": (
            "Kontener to proces odizolowany od innych procesów za pomocą mechanizmów jądra systemu. "
            "Korzysta z jądra hosta, dlatego nie jest pełną maszyną wirtualną z własnym systemem operacyjnym. "
            "Maszyna wirtualna uruchamia własne jądro i daje inny zakres izolacji. Obraz jest niezmiennym "
            "szablonem zawierającym pliki i metadane potrzebne do uruchomienia procesu; kontener jest jego "
            "działającą instancją z zapisywalną warstwą. Z jednego obrazu można uruchomić wiele kontenerów. "
            "Registry przechowuje obrazy, a tag wskazuje wariant, choć może zostać przesunięty na nową wersję. "
            "W powtarzalnym wdrożeniu warto przypiąć obraz do konkretnego digestu. Warstwy obrazu pozwalają "
            "współdzielić niezmienione części między wersjami i ograniczać transfer. Samo pobranie obrazu nie "
            "uruchamia aplikacji. W tym ćwiczeniu obraz Nginxa służy jako obca usługa treningowa; później "
            "zbudujesz obraz własnego <code>orders-api</code>. Pamiętaj, że kontener nie zastępuje kontroli "
            "uprawnień ani aktualizacji bazowego obrazu."
        ),
        "commands": [
            {"command": "docker version", "description": "Sprawdza klienta i dostępność silnika Dockera.", "example": "$ docker version"},
            {"command": "docker pull nginx:1.28", "description": "Pobiera wskazany obraz z registry.", "example": "$ docker pull nginx:1.28"},
            {"command": "docker images nginx", "description": "Pokazuje lokalny obraz, jego tag i rozmiar.", "example": "$ docker images nginx"},
            {"command": "docker image inspect nginx:1.28", "description": "Wyświetla metadane obrazu, w tym jego identyfikator.", "example": "$ docker image inspect nginx:1.28"},
            {"command": "docker history nginx:1.28", "description": "Pokazuje historię warstw budujących obraz.", "example": "$ docker history nginx:1.28"},
            {"command": "docker run --rm nginx:1.28 nginx -v", "description": "Tworzy kontener, uruchamia polecenie i usuwa kontener po zakończeniu.", "example": "$ docker run --rm nginx:1.28 nginx -v"},
        ],
        "practice_task": (
            "Pobierz <code>nginx:1.28</code>, odczytaj jego identyfikator i historię warstw. "
            "Uruchom jednorazowy kontener wyświetlający wersję Nginxa. W notatce rozdziel trzy pojęcia: "
            "obraz zapisany lokalnie, kontener powstały z obrazu oraz registry, z którego pobrano obraz. "
            "Sprawdź, czy po użyciu <code>--rm</code> jednorazowy kontener nadal figuruje na liście."
        ),
        "common_mistakes": [
            "Nazywanie obrazu uruchomionym procesem, mimo że jest tylko szablonem.",
            "Zakładanie, że kontener ma własne jądro systemu operacyjnego.",
            "Uznawanie ruchomego tagu za gwarancję niezmienności wersji.",
            "Traktowanie izolacji kontenera jako kompletnej ochrony hosta.",
        ],
        "summary": (
            "Obraz jest szablonem, kontener jego instancją, a registry miejscem dystrybucji obrazów. "
            "Kontenery współdzielą jądro hosta, a obrazy składają się z warstw. Do odtwarzalnego "
            "wdrożenia potrzebna jest kontrola konkretnej wersji obrazu."
        ),
    },
    "quiz": {
        "title": "Quiz: podstawy konteneryzacji",
        "description": "Sprawdź różnice między obrazem, kontenerem i maszyną wirtualną.",
        "questions": [
            {"text": "Po pobraniu obrazu aplikacja jeszcze nie działa. Co trzeba zrobić?", "answers": [("a", "Uruchomić kontener z obrazu", True), ("b", "Zmienić nazwę tagu", False), ("c", "Wyświetlić historię obrazu", False), ("d", "Usunąć registry", False)]},
            {"text": "Co współdzieli typowy kontener Linux z hostem?", "answers": [("a", "Jądro systemu", True), ("b", "Własny dysk maszyny wirtualnej", False), ("c", "Osobny BIOS", False), ("d", "Zawsze wszystkie procesy hosta", False)]},
            {"text": "Dlaczego sam tag obrazu nie zawsze identyfikuje te same bajty?", "answers": [("a", "Właściciel registry może przesunąć tag na nowy obraz", True), ("b", "Tag jest nazwą działającego kontenera", False), ("c", "Docker usuwa każdy tag po uruchomieniu", False), ("d", "Warstwy obrazu istnieją tylko w pamięci RAM", False)]},
            {"text": "Chcesz odczytać historię warstw pobranego obrazu. Która komenda pomaga?", "answers": [("a", "docker history nginx:1.28", True), ("b", "docker ps", False), ("c", "docker stop nginx:1.28", False), ("d", "docker network ls", False)]},
            {"text": "Co można uruchomić z jednego obrazu?", "answers": [("a", "Wiele niezależnych kontenerów", True), ("b", "Tylko jeden kontener na całym hoście", False), ("c", "Wyłącznie maszynę wirtualną", False), ("d", "Jedynie proces registry", False)]},
            {"text": "Co oznacza --rm w jednorazowym docker run?", "answers": [("a", "Usunięcie kontenera po zakończeniu procesu", True), ("b", "Usunięcie obrazu z registry", False), ("c", "Usunięcie wszystkich wolumenów hosta", False), ("d", "Restart procesu po błędzie", False)]},
        ],
    },
    "flashcards": [
        {"question": "Czym jest kontener?", "answer": "Odizolowaną instancją procesu uruchomioną z obrazu."},
        {"question": "Czym jest obraz?", "answer": "Niezmiennym szablonem plików i metadanych do tworzenia kontenerów."},
        {"question": "Czym jest registry?", "answer": "Usługą przechowywania i dystrybucji obrazów."},
        {"question": "Co współdzieli kontener Linux z hostem?", "answer": "Jądro systemu operacyjnego."},
        {"question": "Co odróżnia VM od kontenera pod względem jądra?", "answer": "VM uruchamia własne jądro, a kontener korzysta z jądra hosta."},
        {"question": "Czy pobranie obrazu uruchamia usługę?", "answer": "Nie, do tego trzeba utworzyć i uruchomić kontener."},
        {"question": "Ile kontenerów może powstać z jednego obrazu?", "answer": "Wiele, każdy z własnym stanem działania."},
        {"question": "Co identyfikuje digest obrazu?", "answer": "Konkretną zawartość obrazu, niezależnie od ruchomego tagu."},
        {"question": "Czy tag musi być niezmienny?", "answer": "Nie, może zostać przypisany do innej wersji obrazu."},
        {"question": "Po co obrazy mają warstwy?", "answer": "Aby współdzielić niezmienione części i przyspieszać pobieranie oraz budowanie."},
        {"question": "Co dodaje działający kontener do obrazu?", "answer": "Własną zapisywalną warstwę i uruchomiony proces."},
        {"question": "Do czego służy docker pull?", "answer": "Pobiera obraz z registry na lokalny host."},
        {"question": "Co pokazuje docker images?", "answer": "Lokalnie dostępne obrazy, tagi i rozmiary."},
        {"question": "Co pokazuje docker history?", "answer": "Historię warstw i instrukcji budowania obrazu."},
        {"question": "Kiedy użyć docker image inspect?", "answer": "Gdy trzeba odczytać dokładne metadane obrazu."},
        {"question": "Co sprawdza docker version?", "answer": "Wersję klienta i kontakt z silnikiem Dockera."},
        {"question": "Co robi docker run?", "answer": "Tworzy kontener z obrazu i uruchamia jego proces."},
        {"question": "Co robi --rm przy docker run?", "answer": "Usuwa kontener po zakończeniu procesu."},
        {"question": "Czy kontener daje pełną izolację bezpieczeństwa?", "answer": "Nie, nadal wymaga właściwych uprawnień i aktualizacji."},
        {"question": "Czy obraz i kontener mają tę samą rolę?", "answer": "Nie, obraz jest szablonem, a kontener jego instancją."},
        {"question": "Co oznacza nazwa nginx:1.28?", "answer": "Repozytorium obrazu nginx i tag 1.28."},
        {"question": "Gdzie trafia obraz po docker pull?", "answer": "Do lokalnego magazynu obrazów silnika Dockera."},
        {"question": "Czy usunięcie kontenera musi usuwać obraz?", "answer": "Nie, obraz pozostaje dostępny niezależnie od instancji."},
        {"question": "Po co przypinać wersję obrazu?", "answer": "Aby ograniczyć nieoczekiwane zmiany między uruchomieniami."},
        {"question": "Co będzie kolejnym krokiem po zrozumieniu obrazu?", "answer": "Poznanie cyklu życia i diagnostyki uruchomionego kontenera."},
    ],
}
