FILES_AND_DIRECTORIES = {
    "module": {
        "title": "Podstawy terminala",
        "description": "Pierwszy moduł poświęcony pracy w terminalu Linux.",
    },
    "lesson": {
        "title": "Pliki i katalogi: mkdir, touch, cp, mv i rm",
        "level": "Podstawowy",
        "duration": "25 min",
        "description": (
            "Poznasz podstawowe komendy do tworzenia katalogów i plików, "
            "kopiowania, przenoszenia, zmiany nazw oraz usuwania danych w terminalu."
        ),
        "theory": (
            "Po opanowaniu poruszania się po systemie plików warto nauczyć się "
            "zarządzać plikami i katalogami. W Linuxie wiele podstawowych operacji "
            "wykonuje się za pomocą prostych komend terminala. Komenda mkdir tworzy "
            "katalogi, touch może utworzyć pusty plik, cp kopiuje dane, mv przenosi "
            "lub zmienia nazwę, a rm usuwa pliki. Przy usuwaniu należy zachować "
            "szczególną ostrożność, ponieważ w terminalu operacje mogą być trudne "
            "do cofnięcia."
        ),
        "commands": [
            {
                "command": "mkdir projekty",
                "description": "Tworzy katalog o nazwie projekty.",
                "example": "$ mkdir projekty",
            },
            {
                "command": "mkdir -p nauka/linux",
                "description": "Tworzy katalogi zagnieżdżone, jeśli jeszcze nie istnieją.",
                "example": "$ mkdir -p nauka/linux",
            },
            {
                "command": "touch notes.txt",
                "description": "Tworzy pusty plik albo aktualizuje czas modyfikacji istniejącego pliku.",
                "example": "$ touch notes.txt",
            },
            {
                "command": "cp notes.txt kopia.txt",
                "description": "Kopiuje plik notes.txt do pliku kopia.txt.",
                "example": "$ cp notes.txt kopia.txt",
            },
            {
                "command": "cp -r projekty backup",
                "description": "Kopiuje katalog projekty wraz z zawartością do katalogu backup.",
                "example": "$ cp -r projekty backup",
            },
            {
                "command": "mv notes.txt dokument.txt",
                "description": "Zmienia nazwę pliku notes.txt na dokument.txt.",
                "example": "$ mv notes.txt dokument.txt",
            },
            {
                "command": "mv dokument.txt projekty/",
                "description": "Przenosi plik dokument.txt do katalogu projekty.",
                "example": "$ mv dokument.txt projekty/",
            },
            {
                "command": "rm dokument.txt",
                "description": "Usuwa plik dokument.txt.",
                "example": "$ rm dokument.txt",
            },
            {
                "command": "rm -r projekty",
                "description": "Usuwa katalog projekty wraz z zawartością.",
                "example": "$ rm -r projekty",
            },
        ],
        "practice_task": (
            "Otwórz terminal i wykonaj kolejno: <code>mkdir shellforge-lab</code>, "
            "<code>cd shellforge-lab</code>, <code>touch notes.txt</code>, "
            "<code>cp notes.txt notes-copy.txt</code>, <code>mv notes-copy.txt backup.txt</code>, "
            "<code>ls -la</code>, <code>rm backup.txt</code>, <code>cd ..</code>. "
            "Zwróć uwagę, które komendy tworzą dane, które je kopiują, a które usuwają."
        ),
        "common_mistakes": [
            "Mylenie <code>cp</code> z <code>mv</code>.",
            "Próba skopiowania katalogu komendą <code>cp</code> bez opcji <code>-r</code>.",
            "Usunięcie niewłaściwego pliku przez wpisanie złej nazwy.",
            "Używanie <code>rm -r</code> bez sprawdzenia, w jakim katalogu aktualnie się znajdujesz.",
            "Brak spacji między komendą a argumentem, np. <code>mkdirprojekty</code>.",
        ],
        "summary": (
            "Komendy <code>mkdir</code>, <code>touch</code>, <code>cp</code>, "
            "<code>mv</code> i <code>rm</code> są podstawą pracy z plikami i katalogami. "
            "Dzięki nim możesz tworzyć, kopiować, przenosić, zmieniać nazwy i usuwać dane "
            "bez używania graficznego menedżera plików."
        ),
    },
        "quiz": {
        "title": "Quiz: pliki i katalogi",
        "description": "Sprawdź, czy rozumiesz podstawowe operacje na plikach i katalogach.",
        "questions": [
            {
                "text": "Która komenda tworzy katalog?",
                "answers": [
                    ("a", "touch", False),
                    ("b", "mkdir", True),
                    ("c", "rm", False),
                    ("d", "pwd", False),
                ],
            },
            {
                "text": "Do czego służy komenda touch notes.txt?",
                "answers": [
                    ("a", "Do usunięcia pliku notes.txt", False),
                    ("b", "Do utworzenia pustego pliku notes.txt lub aktualizacji czasu modyfikacji", True),
                    ("c", "Do skopiowania pliku notes.txt", False),
                    ("d", "Do przejścia do katalogu notes.txt", False),
                ],
            },
            {
                "text": "Która komenda kopiuje plik a.txt do b.txt?",
                "answers": [
                    ("a", "mv a.txt b.txt", False),
                    ("b", "rm a.txt b.txt", False),
                    ("c", "cp a.txt b.txt", True),
                    ("d", "mkdir a.txt b.txt", False),
                ],
            },
            {
                "text": "Do czego może służyć komenda mv?",
                "answers": [
                    ("a", "Do przenoszenia plików i zmiany ich nazw", True),
                    ("b", "Tylko do usuwania katalogów", False),
                    ("c", "Tylko do wyświetlania zawartości katalogu", False),
                    ("d", "Do sprawdzania aktualnego katalogu", False),
                ],
            },
            {
                "text": "Która komenda usuwa plik notes.txt?",
                "answers": [
                    ("a", "rm notes.txt", True),
                    ("b", "cp notes.txt", False),
                    ("c", "mkdir notes.txt", False),
                    ("d", "pwd notes.txt", False),
                ],
            },
            {
                "text": "Dlaczego przy kopiowaniu katalogu często używa się cp -r?",
                "answers": [
                    ("a", "Bo -r oznacza restart systemu", False),
                    ("b", "Bo -r pozwala kopiować katalog wraz z zawartością", True),
                    ("c", "Bo -r usuwa pliki ukryte", False),
                    ("d", "Bo -r pokazuje aktualną ścieżkę", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Co robi komenda mkdir?",
            "answer": "Tworzy katalog.",
        },
        {
            "question": "Co oznacza mkdir?",
            "answer": "Make directory, czyli utwórz katalog.",
        },
        {
            "question": "Co robi mkdir projekty?",
            "answer": "Tworzy katalog o nazwie projekty.",
        },
        {
            "question": "Co robi mkdir -p nauka/linux?",
            "answer": "Tworzy katalogi zagnieżdżone, jeśli jeszcze nie istnieją.",
        },
        {
            "question": "Kiedy warto użyć mkdir -p?",
            "answer": "Gdy chcesz utworzyć kilka poziomów katalogów naraz.",
        },
        {
            "question": "Co robi komenda touch?",
            "answer": "Tworzy pusty plik albo aktualizuje czas modyfikacji istniejącego pliku.",
        },
        {
            "question": "Co robi touch notes.txt?",
            "answer": "Tworzy pusty plik notes.txt, jeśli jeszcze nie istnieje.",
        },
        {
            "question": "Czy touch usuwa pliki?",
            "answer": "Nie. touch nie służy do usuwania plików.",
        },
        {
            "question": "Co robi komenda cp?",
            "answer": "Kopiuje pliki lub katalogi.",
        },
        {
            "question": "Co robi cp a.txt b.txt?",
            "answer": "Tworzy kopię pliku a.txt pod nazwą b.txt.",
        },
        {
            "question": "Czy cp usuwa plik źródłowy?",
            "answer": "Nie. cp kopiuje dane i zostawia oryginał.",
        },
        {
            "question": "Co robi cp -r katalog kopia?",
            "answer": "Kopiuje katalog wraz z jego zawartością.",
        },
        {
            "question": "Do czego służy opcja -r przy cp?",
            "answer": "Do kopiowania rekurencyjnego, czyli katalogów wraz z zawartością.",
        },
        {
            "question": "Co robi komenda mv?",
            "answer": "Przenosi pliki lub katalogi albo zmienia ich nazwy.",
        },
        {
            "question": "Co robi mv notes.txt dokument.txt?",
            "answer": "Zmienia nazwę pliku notes.txt na dokument.txt.",
        },
        {
            "question": "Co robi mv dokument.txt projekty/?",
            "answer": "Przenosi plik dokument.txt do katalogu projekty.",
        },
        {
            "question": "Czy mv zostawia kopię pliku w starym miejscu?",
            "answer": "Nie. mv przenosi plik albo zmienia jego nazwę.",
        },
        {
            "question": "Jaka jest różnica między cp a mv?",
            "answer": "cp kopiuje dane, a mv przenosi je lub zmienia nazwę.",
        },
        {
            "question": "Co robi komenda rm?",
            "answer": "Usuwa pliki.",
        },
        {
            "question": "Co robi rm notes.txt?",
            "answer": "Usuwa plik notes.txt.",
        },
        {
            "question": "Czy rm przenosi plik do kosza?",
            "answer": "Nie. W terminalu rm usuwa plik bez typowego kosza znanego z GUI.",
        },
        {
            "question": "Dlaczego przy rm trzeba uważać?",
            "answer": "Bo można usunąć ważne dane i trudno je odzyskać.",
        },
        {
            "question": "Co robi rm -r katalog?",
            "answer": "Usuwa katalog wraz z zawartością.",
        },
        {
            "question": "Kiedy używa się rm -r?",
            "answer": "Gdy chcesz usunąć katalog i jego zawartość.",
        },
        {
            "question": "Dlaczego rm -r jest niebezpieczne?",
            "answer": "Bo usuwa całe katalogi z plikami w środku.",
        },
        {
            "question": "Co warto zrobić przed użyciem rm?",
            "answer": "Sprawdzić aktualny katalog komendą pwd i listę plików komendą ls.",
        },
        {
            "question": "Jak sprawdzić, czy plik został utworzony?",
            "answer": "Można użyć komendy ls.",
        },
        {
            "question": "Jak sprawdzić, czy katalog został utworzony?",
            "answer": "Można użyć komendy ls albo ls -la.",
        },
        {
            "question": "Co jest błędne w mkdirprojekty?",
            "answer": "Brakuje spacji między mkdir a nazwą katalogu.",
        },
        {
            "question": "Jaka jest poprawna forma mkdirprojekty?",
            "answer": "mkdir projekty.",
        },
        {
            "question": "Czy nazwy plików w Linuxie rozróżniają wielkość liter?",
            "answer": "Tak. notes.txt i Notes.txt mogą oznaczać różne pliki.",
        },
        {
            "question": "Czy katalog i plik mogą mieć tę samą nazwę w tym samym katalogu?",
            "answer": "Nie. W jednym katalogu nazwy muszą być unikalne.",
        },
        {
            "question": "Co zrobić, gdy rm nie może usunąć katalogu?",
            "answer": "Jeśli to katalog z zawartością, można użyć rm -r, ale ostrożnie.",
        },
        {
            "question": "Co zrobić, gdy cp nie kopiuje katalogu?",
            "answer": "Użyć opcji -r, np. cp -r katalog kopia.",
        },
        {
            "question": "Jak utworzyć plik test.txt?",
            "answer": "touch test.txt.",
        },
        {
            "question": "Jak utworzyć katalog lab?",
            "answer": "mkdir lab.",
        },
        {
            "question": "Jak skopiować plik test.txt do copy.txt?",
            "answer": "cp test.txt copy.txt.",
        },
        {
            "question": "Jak zmienić nazwę old.txt na new.txt?",
            "answer": "mv old.txt new.txt.",
        },
        {
            "question": "Jak usunąć plik old.txt?",
            "answer": "rm old.txt.",
        },
        {
            "question": "Jak usunąć katalog lab z zawartością?",
            "answer": "rm -r lab.",
        },
    ],
}