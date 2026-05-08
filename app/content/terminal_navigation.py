TERMINAL_NAVIGATION = {
    "module": {
        "title": "Podstawy terminala",
        "description": "Pierwszy moduł poświęcony pracy w terminalu Linux.",
    },
    "lesson": {
        "title": "Gdzie jestem? Komendy pwd, ls i cd",
        "level": "Podstawowy",
        "duration": "20 min",
        "description": (
            "Poznasz podstawowe komendy do sprawdzania aktualnego katalogu, "
            "wyświetlania plików oraz poruszania się po systemie plików."
        ),
        "theory": (
            "Terminal pozwala wykonywać polecenia tekstowe w systemie Linux. "
            "Jedną z pierwszych umiejętności jest poruszanie się po systemie plików. "
            "System plików można wyobrazić sobie jako drzewo katalogów. "
            "Użytkownik znajduje się zawsze w jakimś aktualnym katalogu roboczym."
        ),
        "commands": [
            {
                "command": "pwd",
                "description": "Wyświetla aktualny katalog roboczy.",
                "example": "$ pwd\n/home/student",
            },
            {
                "command": "ls",
                "description": "Wyświetla pliki i katalogi w bieżącym katalogu.",
                "example": "$ ls\nDocuments Downloads Pictures",
            },
            {
                "command": "ls -la",
                "description": "Wyświetla szczegółową listę plików, także ukrytych.",
                "example": "$ ls -la\n-rw-r--r-- 1 student student 120 notes.txt",
            },
            {
                "command": "cd Documents",
                "description": "Przechodzi do katalogu Documents.",
                "example": "$ cd Documents",
            },
            {
                "command": "cd ..",
                "description": "Przechodzi katalog wyżej.",
                "example": "$ cd ..",
            },
            {
                "command": "cd ~",
                "description": "Przechodzi do katalogu domowego użytkownika.",
                "example": "$ cd ~",
            },
        ],
        "practice_task": (
            "Otwórz terminal i wykonaj kolejno: <code>pwd</code>, <code>ls</code>, "
            "<code>cd Documents</code>, <code>pwd</code>, <code>cd ..</code>, "
            "<code>pwd</code>, <code>cd ~</code>, <code>pwd</code>. "
            "Zwróć uwagę, jak zmienia się aktualny katalog roboczy."
        ),
        "common_mistakes": [
            "Wpisanie <code>cdDocuments</code> zamiast <code>cd Documents</code>.",
            "Mylenie komendy <code>pwd</code> z <code>cd</code>.",
            "Próba wejścia do katalogu, który nie istnieje.",
            "Nieuwzględnianie wielkości liter w nazwach katalogów.",
        ],
        "summary": (
            "Komendy <code>pwd</code>, <code>ls</code> i <code>cd</code> są podstawą pracy "
            "w terminalu. Dzięki nim wiesz, gdzie jesteś, co znajduje się w katalogu "
            "i jak przechodzić między katalogami."
        ),
    },
    "quiz": {
        "title": "Quiz: pwd, ls i cd",
        "description": "Sprawdź, czy rozumiesz podstawowe komendy poruszania się po terminalu.",
        "questions": [
            {
                "text": "Do czego służy komenda pwd?",
                "answers": [
                    ("a", "Do usuwania katalogów", False),
                    ("b", "Do wyświetlania aktualnego katalogu roboczego", True),
                    ("c", "Do tworzenia nowych użytkowników", False),
                    ("d", "Do restartowania systemu", False),
                ],
            },
            {
                "text": "Która komenda wyświetla zawartość katalogu?",
                "answers": [
                    ("a", "ls", True),
                    ("b", "cd", False),
                    ("c", "pwd", False),
                    ("d", "mkdir", False),
                ],
            },
            {
                "text": "Co robi komenda cd ..?",
                "answers": [
                    ("a", "Przechodzi do katalogu domowego", False),
                    ("b", "Usuwa aktualny katalog", False),
                    ("c", "Przechodzi katalog wyżej", True),
                    ("d", "Wyświetla pliki ukryte", False),
                ],
            },
            {
                "text": "Która komenda przechodzi do katalogu domowego użytkownika?",
                "answers": [
                    ("a", "cd /", False),
                    ("b", "cd home", False),
                    ("c", "cd ~", True),
                    ("d", "pwd ~", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Co robi komenda pwd?",
            "answer": "Wyświetla aktualny katalog roboczy.",
        },
        {
            "question": "Co oznacza skrót pwd?",
            "answer": "Print working directory, czyli pokaż aktualny katalog roboczy.",
        },
        {
            "question": "Kiedy warto użyć komendy pwd?",
            "answer": "Gdy chcesz sprawdzić, w którym katalogu aktualnie się znajdujesz.",
        },
        {
            "question": "Czy pwd zmienia aktualny katalog?",
            "answer": "Nie. Komenda pwd tylko wyświetla aktualną lokalizację.",
        },
        {
            "question": "Jaki przykładowy wynik może zwrócić pwd?",
            "answer": "/home/student.",
        },
        {
            "question": "Co robi komenda ls?",
            "answer": "Wyświetla zawartość katalogu.",
        },
        {
            "question": "Czy ls bez argumentów pokazuje zawartość bieżącego katalogu?",
            "answer": "Tak. Bez argumentów ls pokazuje pliki i katalogi w aktualnym katalogu.",
        },
        {
            "question": "Co może pokazać komenda ls?",
            "answer": "Nazwy plików oraz katalogów znajdujących się w danym katalogu.",
        },
        {
            "question": "Czy ls zmienia aktualny katalog?",
            "answer": "Nie. ls tylko wyświetla zawartość katalogu.",
        },
        {
            "question": "Co robi komenda ls -l?",
            "answer": "Wyświetla szczegółową listę plików i katalogów.",
        },
        {
            "question": "Co robi komenda ls -a?",
            "answer": "Pokazuje również pliki ukryte.",
        },
        {
            "question": "Co robi komenda ls -la?",
            "answer": "Wyświetla szczegółową listę wszystkich plików, także ukrytych.",
        },
        {
            "question": "Czym są pliki ukryte w Linuxie?",
            "answer": "To pliki, których nazwa zaczyna się od kropki.",
        },
        {
            "question": "Jaki przykład pliku ukrytego można spotkać w Linuxie?",
            "answer": ".bashrc.",
        },
        {
            "question": "Czy ls -la pokazuje uprawnienia plików?",
            "answer": "Tak. W trybie szczegółowym widać między innymi uprawnienia.",
        },
        {
            "question": "Co robi komenda cd?",
            "answer": "Zmienia aktualny katalog roboczy.",
        },
        {
            "question": "Co oznacza skrót cd?",
            "answer": "Change directory, czyli zmień katalog.",
        },
        {
            "question": "Czy cd bez argumentu może przenieść do katalogu domowego?",
            "answer": "Tak, w wielu powłokach cd bez argumentu przenosi do katalogu domowego.",
        },
        {
            "question": "Co robi komenda cd Documents?",
            "answer": "Próbuje przejść do katalogu Documents.",
        },
        {
            "question": "Co robi komenda cd ..?",
            "answer": "Przechodzi jeden katalog wyżej.",
        },
        {
            "question": "Co oznaczają dwie kropki w ścieżce?",
            "answer": "Oznaczają katalog nadrzędny.",
        },
        {
            "question": "Co robi komenda cd ~?",
            "answer": "Przechodzi do katalogu domowego użytkownika.",
        },
        {
            "question": "Co oznacza znak ~ w ścieżce?",
            "answer": "Oznacza katalog domowy aktualnego użytkownika.",
        },
        {
            "question": "Co robi komenda cd /?",
            "answer": "Przechodzi do katalogu głównego systemu plików.",
        },
        {
            "question": "Czym jest katalog główny w Linuxie?",
            "answer": "To najwyższy katalog w systemie plików, oznaczany jako /.",
        },
        {
            "question": "Czym jest ścieżka bezwzględna?",
            "answer": "To ścieżka zaczynająca się od katalogu głównego /.",
        },
        {
            "question": "Podaj przykład ścieżki bezwzględnej.",
            "answer": "/home/student/Documents.",
        },
        {
            "question": "Czym jest ścieżka względna?",
            "answer": "To ścieżka liczona od aktualnego katalogu.",
        },
        {
            "question": "Podaj przykład ścieżki względnej.",
            "answer": "Documents albo ../Downloads.",
        },
        {
            "question": "Czy Linux rozróżnia wielkość liter w nazwach katalogów?",
            "answer": "Tak. Documents i documents to różne nazwy.",
        },
        {
            "question": "Dlaczego cd documents może nie działać?",
            "answer": "Bo katalog może nazywać się Documents z wielką literą.",
        },
        {
            "question": "Jaki błąd może wystąpić przy wejściu do nieistniejącego katalogu?",
            "answer": "No such file or directory.",
        },
        {
            "question": "Co jest błędne w komendzie cdDocuments?",
            "answer": "Brakuje spacji między komendą cd a nazwą katalogu.",
        },
        {
            "question": "Jaka jest poprawna forma komendy cdDocuments?",
            "answer": "cd Documents.",
        },
        {
            "question": "Czy między komendą a argumentem zwykle powinna być spacja?",
            "answer": "Tak. Przykład: cd Documents.",
        },
        {
            "question": "Co oznacza aktualny katalog roboczy?",
            "answer": "To katalog, w którym aktualnie wykonujesz komendy.",
        },
        {
            "question": "Jak sprawdzić aktualny katalog roboczy?",
            "answer": "Za pomocą komendy pwd.",
        },
        {
            "question": "Jak wyświetlić zawartość aktualnego katalogu?",
            "answer": "Za pomocą komendy ls.",
        },
        {
            "question": "Jak przejść do katalogu domowego?",
            "answer": "Za pomocą cd ~ albo często samego cd.",
        },
        {
            "question": "Jak przejść katalog wyżej?",
            "answer": "Za pomocą komendy cd ...",
        },
        {
            "question": "Jak sprawdzić pliki ukryte w katalogu?",
            "answer": "Za pomocą ls -a albo ls -la.",
        },
        {
            "question": "Jak wyświetlić szczegółowe informacje o plikach?",
            "answer": "Za pomocą ls -l albo ls -la.",
        },
        {
            "question": "Czy pwd, ls i cd są podstawowymi komendami terminala?",
            "answer": "Tak. To jedne z pierwszych komend potrzebnych do pracy w Linuxie.",
        },
        {
            "question": "Która komenda mówi gdzie jesteś?",
            "answer": "pwd.",
        },
        {
            "question": "Która komenda pokazuje co jest w katalogu?",
            "answer": "ls.",
        },
        {
            "question": "Która komenda pozwala zmienić katalog?",
            "answer": "cd.",
        },
        {
            "question": "Czy ls -la zmienia zawartość katalogu?",
            "answer": "Nie. Ta komenda tylko wyświetla informacje.",
        },
        {
            "question": "Czy cd usuwa pliki?",
            "answer": "Nie. cd służy tylko do zmiany katalogu.",
        },
        {
            "question": "Czy pwd tworzy katalog?",
            "answer": "Nie. pwd tylko wyświetla aktualną ścieżkę.",
        },
        {
            "question": "Dlaczego warto często używać pwd podczas nauki?",
            "answer": "Pomaga kontrolować, w którym katalogu aktualnie jesteś.",
        },
        {
            "question": "Dlaczego warto używać ls po przejściu do katalogu?",
            "answer": "Żeby sprawdzić, jakie pliki i katalogi są dostępne.",
        },
        {
            "question": "Co oznacza katalog nadrzędny?",
            "answer": "To katalog znajdujący się jeden poziom wyżej.",
        },
        {
            "question": "Co oznacza katalog domowy?",
            "answer": "To prywatny katalog użytkownika, np. /home/student.",
        },
        {
            "question": "Czy /home/student i /home/Student to zawsze to samo?",
            "answer": "Nie. Linux rozróżnia wielkość liter.",
        },
        {
            "question": "Co warto zrobić, gdy cd zwraca błąd?",
            "answer": "Sprawdzić nazwę katalogu komendą ls i upewnić się, że wpisano ją poprawnie.",
        },
        {
            "question": "Czy można podać ścieżkę jako argument komendy ls?",
            "answer": "Tak. Na przykład ls /home/student.",
        },
        {
            "question": "Co robi ls /?",
            "answer": "Wyświetla zawartość katalogu głównego.",
        },
        {
            "question": "Co robi cd ../..?",
            "answer": "Przechodzi dwa poziomy katalogów wyżej.",
        },
        {
            "question": "Co robi pwd po wykonaniu cd ..?",
            "answer": "Pokazuje nową lokalizację po przejściu katalog wyżej.",
        },
        {
            "question": "Dlaczego komendy terminala warto ćwiczyć praktycznie?",
            "answer": "Bo najłatwiej je zapamiętać przez realne używanie w terminalu.",
        },
        {
            "question": "Jaki jest dobry pierwszy schemat ćwiczenia terminala?",
            "answer": "pwd, ls, cd do katalogu, pwd, cd .., pwd.",
        },
    ],
}