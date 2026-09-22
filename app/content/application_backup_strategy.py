APPLICATION_BACKUP_STRATEGY = {
    "module": {
        "title": "Monitoring i utrzymanie",
        "description": "Praktyczne sprawdzanie stanu aplikacji, analiza sygnałów, reagowanie na incydenty oraz ochrona i odtwarzanie danych.",
    },
    "lesson": {
        "title": "Strategia backupu aplikacji",
        "level": "Średnio zaawansowany",
        "duration": "65 min",
        "description": "Ułożysz plan kopii danych, konfiguracji i procedury odtwarzania dla ćwiczeniowej aplikacji.",
        "theory": (
            "Backup ma umożliwić powrót do działania po utracie danych, błędzie operatora lub awarii hosta. "
            "Najpierw spisz zasoby: bazę PostgreSQL, pliki przesyłane przez użytkowników, konfigurację "
            "odtwarzalną z bezpiecznego źródła, definicje wdrożenia i potrzebne sekrety. Sam obraz kontenera "
            "ani volume nie zastępują kopii danych. Ustal RPO, czyli największą akceptowaną utratę "
            "zmian, oraz RTO, czyli czas na przywrócenie usługi. Te wymagania wyznaczają częstotliwość, "
            "metodę i lokalizację kopii. Pełna kopia upraszcza odtwarzanie, a kopie przyrostowe oszczędzają "
            "miejsce kosztem zależności od wcześniejszych egzemplarzy. Dla małej bazy logiczny zrzut "
            "<code>pg_dump</code> bywa prostym punktem startu; nie zapewnia odtwarzania do dowolnej sekundy. "
            "Reguła 3-2-1 przypomina o trzech egzemplarzach danych, dwóch rodzajach nośników i jednej kopii "
            "poza główną lokalizacją. W praktyce dobierz niezależną lokalizację, ogranicz dostęp, szyfruj "
            "przechowywane i przesyłane kopie oraz zaplanuj retencję. Monitoruj powodzenie zadania, rozmiar "
            "i wiek ostatniej kopii. Plik, który istnieje, może być niekompletny lub nieodtwarzalny. "
            "Okresowo odtwórz kopię do odizolowanego środowiska testowego i sprawdź ważne dane oraz działanie "
            "aplikacji. Przykłady dotyczą wyłącznie danych ćwiczeniowych; nie kopiuj prawdziwych sekretów "
            "do notatek, repozytorium ani otwartego katalogu."
        ),
        "commands": [
            {"command": "df -h /srv/backups", "description": "Sprawdza miejsce w lokalizacji ćwiczeniowych kopii przed zadaniem.", "example": "$ df -h /srv/backups"},
            {"command": "find /srv/backups -maxdepth 1 -type f -name '*.backup' -printf '%TY-%Tm-%Td %TH:%TM %s %f\n'", "description": "Pokazuje datę i rozmiar zapisanych kopii testowych.", "example": "$ find /srv/backups -maxdepth 1 -type f -name '*.backup' -printf '%TY-%Tm-%Td %TH:%TM %s %f\n'"},
            {"command": "stat /srv/backups/orders-test.backup", "description": "Odczytuje metadane jednej testowej kopii.", "example": "$ stat /srv/backups/orders-test.backup"},
            {"command": "test -s /srv/backups/orders-test.backup", "description": "Weryfikuje istnienie i niezerowy rozmiar pliku.", "example": "$ test -s /srv/backups/orders-test.backup"},
            {"command": "sha256sum /srv/backups/orders-test.backup", "description": "Tworzy sumę do późniejszego porównania integralności pliku.", "example": "$ sha256sum /srv/backups/orders-test.backup"},
            {"command": "ls -ld /srv/backups", "description": "Sprawdza uprawnienia katalogu z kopiami.", "example": "$ ls -ld /srv/backups"},
        ],
        "practice_task": (
            "Dla fikcyjnej aplikacji <code>orders-api</code> z bazą i plikami zamówień przygotuj tabelę: "
            "zasób, metoda kopii, częstotliwość, lokalizacja, retencja i sposób testu. Załóż RPO 24 godziny "
            "i RTO 4 godziny; sprawdź, czy plan je spełnia także po utracie hosta. Na nieszkodliwym pliku "
            "<code>orders-test.backup</code> przećwicz kontrolę daty, rozmiaru i sumy. Dopisz termin testowego "
            "odtworzenia oraz osobę odpowiedzialną za wynik."
        ),
        "common_mistakes": [
            "Traktowanie volume lub drugiego pliku na tym samym hoście jako odpornej kopii.",
            "Kopiowanie tylko bazy, gdy aplikacja przechowuje również pliki użytkowników.",
            "Plan retencji bez informacji, jak daleko wstecz można się cofnąć.",
            "Przechowywanie zrzutów i sekretów w publicznym repozytorium.",
            "Uznanie niepustego pliku za dowód skutecznego odtworzenia.",
        ],
        "summary": (
            "Strategia łączy wymagania RPO i RTO z listą zasobów, niezależną lokalizacją, ochroną, "
            "retencją i regularnym testem odtwarzania. Kontrola pliku jest początkiem weryfikacji, "
            "a pełny dowód daje odtworzenie danych i sprawdzenie aplikacji."
        ),
    },
    "quiz": {
        "title": "Quiz: strategia backupu aplikacji",
        "description": "Dobierz kopię do ryzyka utraty danych i czasu odtworzenia.",
        "questions": [
            {"text": "Aplikacja ma RPO 24 godziny. Co oznacza to dla planu kopii?", "answers": [("a", "Utrata zmian nie może przekroczyć doby, więc kopie i test muszą uwzględnić ten limit", True), ("b", "Odtwarzanie może trwać dowolnie długo", False), ("c", "Wystarczy jeden volume bez kopii", False), ("d", "Można pominąć pliki użytkowników", False)]},
            {"text": "Kopie są tylko na dysku hosta bazy. Jakie ryzyko pozostaje?", "answers": [("a", "Awaria hosta może zniszczyć dane i kopie jednocześnie", True), ("b", "Kopia automatycznie trafia poza host", False), ("c", "Retencja przestaje mieć znaczenie", False), ("d", "RTO zawsze spada do zera", False)]},
            {"text": "Co trzeba uwzględnić poza bazą w aplikacji przyjmującej pliki?", "answers": [("a", "Pliki użytkowników oraz konfigurację potrzebną do odtworzenia usługi", True), ("b", "Wyłącznie bieżący PID procesu", False), ("c", "Tylko kolor panelu", False), ("d", "Jedynie pamięć podręczną przeglądarki", False)]},
            {"text": "Plik kopii ma poprawny rozmiar i sumę. Co potwierdza jego odtwarzalność?", "answers": [("a", "Odtworzenie w izolowanym środowisku i kontrola danych oraz aplikacji", True), ("b", "Sama nazwa pliku", False), ("c", "Sama obecność volume", False), ("d", "Ponowne obliczenie rozmiaru", False)]},
            {"text": "Dlaczego ustala się retencję?", "answers": [("a", "Aby wiedzieć, jak długo są dostępne punkty przywracania i kontrolować miejsce", True), ("b", "Aby pg_dump działał bez bazy", False), ("c", "Aby wyłączyć logi", False), ("d", "Aby zastąpić test odtworzenia", False)]},
            {"text": "Ktoś proponuje wrzucić kopię produkcyjnej bazy do repozytorium. Co zrobisz?", "answers": [("a", "Odmówię i wybiorę chronioną lokalizację z ograniczonym dostępem", True), ("b", "Zaakceptuję, jeśli plik jest mały", False), ("c", "Zamienię nazwę pliku na .txt", False), ("d", "Dodam tylko hasło w README", False)]},
        ],
    },
    "flashcards": [
        {"question": "Co chroni strategia backupu?", "answer": "Dane i możliwość uruchomienia usługi po utracie lub uszkodzeniu zasobów."},
        {"question": "Co oznacza RPO?", "answer": "Maksymalną akceptowaną utratę zmian mierzoną czasem."},
        {"question": "Co oznacza RTO?", "answer": "Maksymalny akceptowany czas przywrócenia usługi."},
        {"question": "Jak RPO wpływa na częstotliwość kopii?", "answer": "Odstęp między punktami odzyskiwania musi mieścić się w dopuszczalnej utracie danych."},
        {"question": "Dlaczego lista zasobów jest pierwszym krokiem?", "answer": "Pozwala objąć planem bazę, pliki i konfigurację potrzebną aplikacji."},
        {"question": "Czy obraz kontenera jest kopią bazy?", "answer": "Nie, zwykle nie zawiera bieżących danych przechowywanych w volume."},
        {"question": "Kiedy przydaje się pełna kopia?", "answer": "Gdy liczy się prostsze odtwarzanie bez łańcucha wcześniejszych kopii."},
        {"question": "Jaki koszt ma kopia przyrostowa?", "answer": "Odtwarzanie może wymagać pełnej kopii i kolejnych kopii przyrostowych."},
        {"question": "Co przypomina reguła 3-2-1?", "answer": "Trzy egzemplarze danych, dwa rodzaje nośników i jedną kopię poza główną lokalizacją."},
        {"question": "Po co kopia poza hostem bazy?", "answer": "Awaria lub utrata hosta nie powinna usuwać wszystkich egzemplarzy."},
        {"question": "Co obejmuje retencja?", "answer": "Czas przechowywania i liczbę dostępnych punktów przywracania."},
        {"question": "Po co szyfrować zrzuty?", "answer": "Aby ograniczyć ujawnienie danych po nieuprawnionym dostępie do nośnika."},
        {"question": "Dlaczego kontrolować uprawnienia kopii?", "answer": "Zrzut może zawierać wrażliwe dane aplikacji."},
        {"question": "Co mierzy wiek ostatniej kopii?", "answer": "Czas od ostatniego udanego punktu odzyskiwania."},
        {"question": "Co wykrywa kontrola rozmiaru?", "answer": "Brak pliku lub podejrzanie małą kopię, ale nie dowodzi odtwarzalności."},
        {"question": "Do czego służy sha256sum?", "answer": "Do porównania integralności tego samego pliku po przeniesieniu."},
        {"question": "Czy suma kontrolna wykrywa błąd logiczny zrzutu?", "answer": "Nie, identyczny uszkodzony logicznie zrzut może mieć zgodną sumę."},
        {"question": "Jak potwierdzić odtwarzalność kopii?", "answer": "Odtworzyć ją w izolowanym teście i sprawdzić dane oraz ważną funkcję aplikacji."},
        {"question": "Po co testować kopię cyklicznie?", "answer": "Aby wykryć błędy procedury, uprawnień i zgodności przed incydentem."},
        {"question": "Czy pg_dump daje dowolny punkt w czasie?", "answer": "Nie, pojedynczy zrzut pozwala wrócić do stanu z chwili wykonania kopii."},
        {"question": "Jak zabezpieczyć sekrety potrzebne do odtworzenia?", "answer": "Przechowywać je w chronionym źródle i opisać sposób dostępu bez wpisywania wartości do runbooka."},
        {"question": "Co powinien zawierać raport zadania kopii?", "answer": "Czas, wynik, lokalizację, rozmiar i ewentualny błąd."},
        {"question": "Po co oszacować miejsce przed backupem?", "answer": "Aby zadanie i retencja nie zapełniły docelowego systemu plików."},
        {"question": "Co zrobić przy nieudanym backupie?", "answer": "Powiadomić odpowiedzialną osobę, ustalić przyczynę i wykonać sprawdzoną kopię."},
        {"question": "Na jakich danych ćwiczyć odtwarzanie?", "answer": "Na przygotowanych danych testowych w odizolowanym środowisku."},
    ],
}
