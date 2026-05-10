FILE_PERMISSIONS = {
    "module": {
        "title": "Podstawy terminala",
        "description": "Pierwszy moduł poświęcony pracy w terminalu Linux.",
    },
    "lesson": {
        "title": "Uprawnienia plików: chmod, rwx, 755 i 644",
        "level": "Podstawowy",
        "duration": "30 min",
        "description": (
            "Poznasz podstawy uprawnień plików w Linuxie: odczyt, zapis, wykonywanie, "
            "właściciela, grupę, innych użytkowników oraz komendę chmod."
        ),
        "theory": (
            "W Linuxie każdy plik i katalog ma zestaw uprawnień określających, kto może go "
            "odczytywać, modyfikować lub uruchamiać. Uprawnienia są podzielone na trzy grupy: "
            "właściciela, grupę oraz innych użytkowników. Symbol r oznacza odczyt, w oznacza zapis, "
            "a x oznacza wykonywanie. Komenda chmod pozwala zmieniać te uprawnienia w formie "
            "symbolicznej, na przykład chmod u+x script.sh, albo numerycznej, na przykład chmod 755 script.sh."
        ),
        "commands": [
            {
                "command": "ls -l",
                "description": "Wyświetla szczegółową listę plików wraz z uprawnieniami.",
                "example": "$ ls -l\n-rw-r--r-- 1 student student 120 notes.txt",
            },
            {
                "command": "chmod u+x script.sh",
                "description": "Dodaje właścicielowi pliku prawo wykonywania.",
                "example": "$ chmod u+x script.sh",
            },
            {
                "command": "chmod g-w notes.txt",
                "description": "Odbiera grupie prawo zapisu do pliku.",
                "example": "$ chmod g-w notes.txt",
            },
            {
                "command": "chmod 755 script.sh",
                "description": "Ustawia pełne uprawnienia dla właściciela oraz odczyt i wykonywanie dla grupy i innych.",
                "example": "$ chmod 755 script.sh",
            },
            {
                "command": "chmod 644 notes.txt",
                "description": "Ustawia odczyt i zapis dla właściciela oraz tylko odczyt dla grupy i innych.",
                "example": "$ chmod 644 notes.txt",
            },
            {
                "command": "chmod 700 private.sh",
                "description": "Ustawia pełne uprawnienia tylko dla właściciela.",
                "example": "$ chmod 700 private.sh",
            },
        ],
        "practice_task": (
            "Utwórz plik <code>script.sh</code>, sprawdź jego uprawnienia komendą <code>ls -l</code>, "
            "nadaj właścicielowi prawo wykonywania za pomocą <code>chmod u+x script.sh</code>, "
            "a następnie ponownie sprawdź wynik komendą <code>ls -l</code>. Następnie ustaw "
            "uprawnienia <code>chmod 755 script.sh</code> i porównaj zapis symboliczny uprawnień."
        ),
        "common_mistakes": [
            "Mylenie prawa odczytu <code>r</code> z prawem wykonywania <code>x</code>.",
            "Używanie <code>chmod 777</code> bez zrozumienia konsekwencji.",
            "Zakładanie, że każdy plik tekstowy powinien mieć prawo wykonywania.",
            "Mylenie właściciela pliku z grupą pliku.",
            "Brak sprawdzenia uprawnień komendą <code>ls -l</code> przed zmianą.",
        ],
        "summary": (
            "Uprawnienia plików są jednym z fundamentów pracy z Linuxem. Komenda <code>ls -l</code> "
            "pozwala je odczytać, a <code>chmod</code> pozwala je zmieniać. Najczęściej spotykane "
            "tryby to <code>644</code> dla zwykłych plików oraz <code>755</code> dla skryptów i katalogów."
        ),
    },
    "quiz": {
        "title": "Quiz: uprawnienia plików",
        "description": "Sprawdź, czy rozumiesz podstawy uprawnień plików w Linuxie.",
        "questions": [
            {
                "text": "Co oznacza litera r w uprawnieniach pliku?",
                "answers": [
                    ("a", "Prawo restartu systemu", False),
                    ("b", "Prawo odczytu", True),
                    ("c", "Prawo usunięcia użytkownika", False),
                    ("d", "Prawo zmiany katalogu", False),
                ],
            },
            {
                "text": "Co oznacza litera w w uprawnieniach pliku?",
                "answers": [
                    ("a", "Prawo zapisu", True),
                    ("b", "Prawo wykonywania", False),
                    ("c", "Prawo odczytu", False),
                    ("d", "Prawo wejścia do katalogu domowego", False),
                ],
            },
            {
                "text": "Co oznacza litera x w uprawnieniach pliku?",
                "answers": [
                    ("a", "Prawo wykonywania", True),
                    ("b", "Prawo kopiowania", False),
                    ("c", "Prawo usuwania", False),
                    ("d", "Prawo sprawdzenia ścieżki", False),
                ],
            },
            {
                "text": "Która komenda wyświetla uprawnienia plików?",
                "answers": [
                    ("a", "pwd", False),
                    ("b", "ls -l", True),
                    ("c", "cd -l", False),
                    ("d", "mkdir -p", False),
                ],
            },
            {
                "text": "Co robi komenda chmod u+x script.sh?",
                "answers": [
                    ("a", "Usuwa plik script.sh", False),
                    ("b", "Dodaje właścicielowi prawo wykonywania", True),
                    ("c", "Tworzy katalog script.sh", False),
                    ("d", "Kopiuje plik script.sh", False),
                ],
            },
            {
                "text": "Który tryb jest często używany dla zwykłych plików tekstowych?",
                "answers": [
                    ("a", "777", False),
                    ("b", "000", False),
                    ("c", "644", True),
                    ("d", "111", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Co oznacza r w uprawnieniach pliku?",
            "answer": "Oznacza prawo odczytu, czyli read.",
        },
        {
            "question": "Co oznacza w w uprawnieniach pliku?",
            "answer": "Oznacza prawo zapisu, czyli write.",
        },
        {
            "question": "Co oznacza x w uprawnieniach pliku?",
            "answer": "Oznacza prawo wykonywania, czyli execute.",
        },
        {
            "question": "Jak sprawdzić uprawnienia plików?",
            "answer": "Za pomocą komendy ls -l.",
        },
        {
            "question": "Co pokazuje pierwszy znak w wyniku ls -l?",
            "answer": "Typ obiektu, na przykład plik zwykły albo katalog.",
        },
        {
            "question": "Co oznacza znak - na początku wyniku ls -l?",
            "answer": "Oznacza zwykły plik.",
        },
        {
            "question": "Co oznacza litera d na początku wyniku ls -l?",
            "answer": "Oznacza katalog.",
        },
        {
            "question": "Na jakie trzy grupy dzielą się uprawnienia?",
            "answer": "Na właściciela, grupę oraz innych użytkowników.",
        },
        {
            "question": "Kto to jest właściciel pliku?",
            "answer": "Użytkownik, do którego należy dany plik.",
        },
        {
            "question": "Co oznacza grupa pliku?",
            "answer": "Grupa użytkowników, do której przypisany jest plik.",
        },
        {
            "question": "Kim są inni użytkownicy w kontekście uprawnień?",
            "answer": "To użytkownicy, którzy nie są właścicielem i nie należą do grupy pliku.",
        },
        {
            "question": "Do czego służy chmod?",
            "answer": "Do zmiany uprawnień plików i katalogów.",
        },
        {
            "question": "Co robi chmod u+x script.sh?",
            "answer": "Dodaje właścicielowi prawo wykonywania pliku script.sh.",
        },
        {
            "question": "Co oznacza u w chmod u+x?",
            "answer": "Oznacza użytkownika będącego właścicielem pliku.",
        },
        {
            "question": "Co oznacza g w chmod?",
            "answer": "Oznacza grupę pliku.",
        },
        {
            "question": "Co oznacza o w chmod?",
            "answer": "Oznacza innych użytkowników.",
        },
        {
            "question": "Co oznacza a w chmod?",
            "answer": "Oznacza wszystkich: właściciela, grupę i innych.",
        },
        {
            "question": "Co robi chmod g-w notes.txt?",
            "answer": "Odbiera grupie prawo zapisu do pliku notes.txt.",
        },
        {
            "question": "Co robi chmod a+r file.txt?",
            "answer": "Dodaje wszystkim prawo odczytu pliku.",
        },
        {
            "question": "Co oznacza tryb 755?",
            "answer": "Właściciel ma pełne prawa, grupa i inni mają odczyt oraz wykonywanie.",
        },
        {
            "question": "Co oznacza tryb 644?",
            "answer": "Właściciel ma odczyt i zapis, grupa i inni tylko odczyt.",
        },
        {
            "question": "Co oznacza tryb 700?",
            "answer": "Tylko właściciel ma pełne uprawnienia.",
        },
        {
            "question": "Dlaczego chmod 777 bywa niebezpieczny?",
            "answer": "Bo daje wszystkim pełne prawa odczytu, zapisu i wykonywania.",
        },
        {
            "question": "Czy każdy plik powinien mieć prawo wykonywania?",
            "answer": "Nie. Prawo wykonywania nadaje się głównie skryptom i programom.",
        },
        {
            "question": "Jaki tryb jest częsty dla zwykłych plików?",
            "answer": "644.",
        },
        {
            "question": "Jaki tryb jest częsty dla katalogów i skryptów?",
            "answer": "755.",
        },
        {
            "question": "Co warto zrobić przed zmianą uprawnień?",
            "answer": "Sprawdzić aktualne uprawnienia komendą ls -l.",
        },
        {
            "question": "Czy chmod zmienia właściciela pliku?",
            "answer": "Nie. chmod zmienia uprawnienia, a nie właściciela.",
        },
        {
            "question": "Czy chmod usuwa pliki?",
            "answer": "Nie. chmod służy do zmiany uprawnień.",
        },
        {
            "question": "Dlaczego uprawnienia są ważne w Linuxie?",
            "answer": "Pomagają kontrolować dostęp do plików i zwiększają bezpieczeństwo systemu.",
        },
    ],
}