USERS_AND_GROUPS = {
    "module": {
        "title": "Podstawy terminala",
        "description": "Pierwszy moduł poświęcony pracy w terminalu Linux.",
    },
    "lesson": {
        "title": "Użytkownicy i grupy: whoami, id i groups",
        "level": "Podstawowy",
        "duration": "25 min",
        "description": (
            "Poznasz podstawowe komendy do sprawdzania aktualnego użytkownika, "
            "identyfikatora UID, grup użytkownika oraz podstawowych informacji o koncie w Linuxie."
        ),
        "theory": (
            "Linux jest systemem wieloużytkownikowym. Oznacza to, że z jednego systemu może "
            "korzystać wielu użytkowników, a każdy z nich może mieć inne uprawnienia. "
            "Każdy użytkownik ma swoją nazwę, identyfikator UID oraz może należeć do jednej "
            "lub wielu grup. Grupy ułatwiają zarządzanie dostępem do plików, katalogów i zasobów. "
            "Komendy whoami, id oraz groups pozwalają szybko sprawdzić, kim jesteś w systemie "
            "i do jakich grup należysz."
        ),
        "commands": [
            {
                "command": "whoami",
                "description": "Wyświetla nazwę aktualnie zalogowanego użytkownika.",
                "example": "$ whoami\nstudent",
            },
            {
                "command": "id",
                "description": "Wyświetla UID, GID oraz grupy aktualnego użytkownika.",
                "example": "$ id\nuid=1000(student) gid=1000(student) groups=1000(student),10(wheel)",
            },
            {
                "command": "id student",
                "description": "Wyświetla informacje o wskazanym użytkowniku.",
                "example": "$ id student\nuid=1000(student) gid=1000(student) groups=1000(student),10(wheel)",
            },
            {
                "command": "groups",
                "description": "Wyświetla grupy, do których należy aktualny użytkownik.",
                "example": "$ groups\nstudent wheel",
            },
            {
                "command": "groups student",
                "description": "Wyświetla grupy wskazanego użytkownika.",
                "example": "$ groups student\nstudent : student wheel",
            },
        ],
        "practice_task": (
            "Otwórz terminal i wykonaj kolejno: <code>whoami</code>, <code>id</code>, "
            "<code>groups</code>. Zwróć uwagę na nazwę użytkownika, wartość <code>uid</code>, "
            "wartość <code>gid</code> oraz listę grup. Następnie wykonaj <code>id twoja_nazwa_uzytkownika</code> "
            "i porównaj wynik z komendą <code>id</code>."
        ),
        "common_mistakes": [
            "Mylenie nazwy użytkownika z nazwą hosta.",
            "Zakładanie, że każdy użytkownik ma takie same uprawnienia.",
            "Mylenie UID z GID.",
            "Nieuwzględnianie tego, że użytkownik może należeć do wielu grup.",
            "Zakładanie, że komenda <code>whoami</code> pokazuje wszystkie informacje o użytkowniku.",
        ],
        "summary": (
            "Komendy <code>whoami</code>, <code>id</code> i <code>groups</code> pomagają "
            "zrozumieć, jako jaki użytkownik pracujesz w systemie Linux. To ważna podstawa "
            "przed nauką uprawnień, administracji użytkownikami, sudo oraz zabezpieczania systemu."
        ),
    },
    "quiz": {
        "title": "Quiz: użytkownicy i grupy",
        "description": "Sprawdź, czy rozumiesz podstawowe informacje o użytkownikach i grupach w Linuxie.",
        "questions": [
            {
                "text": "Co pokazuje komenda whoami?",
                "answers": [
                    ("a", "Aktualny katalog roboczy", False),
                    ("b", "Nazwę aktualnie zalogowanego użytkownika", True),
                    ("c", "Listę procesów", False),
                    ("d", "Adres IP systemu", False),
                ],
            },
            {
                "text": "Co oznacza UID?",
                "answers": [
                    ("a", "Identyfikator użytkownika", True),
                    ("b", "Identyfikator katalogu", False),
                    ("c", "Nazwa grupy", False),
                    ("d", "Numer portu sieciowego", False),
                ],
            },
            {
                "text": "Co oznacza GID?",
                "answers": [
                    ("a", "Identyfikator grupy", True),
                    ("b", "Identyfikator procesu", False),
                    ("c", "Aktualny katalog", False),
                    ("d", "Nazwa hosta", False),
                ],
            },
            {
                "text": "Która komenda pokazuje UID, GID i grupy użytkownika?",
                "answers": [
                    ("a", "pwd", False),
                    ("b", "ls -la", False),
                    ("c", "id", True),
                    ("d", "touch", False),
                ],
            },
            {
                "text": "Która komenda pokazuje grupy aktualnego użytkownika?",
                "answers": [
                    ("a", "groups", True),
                    ("b", "mkdir", False),
                    ("c", "chmod", False),
                    ("d", "cd", False),
                ],
            },
            {
                "text": "Czy użytkownik może należeć do wielu grup?",
                "answers": [
                    ("a", "Nie, zawsze tylko do jednej", False),
                    ("b", "Tak, może należeć do wielu grup", True),
                    ("c", "Tylko użytkownik root może należeć do grup", False),
                    ("d", "Grupy nie istnieją w Linuxie", False),
                ],
            },
        ],
    },
    "flashcards": [
        {
            "question": "Co robi komenda whoami?",
            "answer": "Wyświetla nazwę aktualnie zalogowanego użytkownika.",
        },
        {
            "question": "Kiedy warto użyć whoami?",
            "answer": "Gdy chcesz szybko sprawdzić, jako jaki użytkownik pracujesz w terminalu.",
        },
        {
            "question": "Czy whoami pokazuje UID użytkownika?",
            "answer": "Nie. whoami pokazuje nazwę użytkownika, a UID zobaczysz komendą id.",
        },
        {
            "question": "Co robi komenda id?",
            "answer": "Wyświetla UID, GID oraz grupy użytkownika.",
        },
        {
            "question": "Co oznacza UID?",
            "answer": "User ID, czyli numeryczny identyfikator użytkownika.",
        },
        {
            "question": "Co oznacza GID?",
            "answer": "Group ID, czyli numeryczny identyfikator grupy.",
        },
        {
            "question": "Co pokazuje id bez argumentów?",
            "answer": "Informacje o aktualnym użytkowniku.",
        },
        {
            "question": "Co robi id student?",
            "answer": "Pokazuje informacje o użytkowniku student.",
        },
        {
            "question": "Co robi komenda groups?",
            "answer": "Wyświetla grupy, do których należy aktualny użytkownik.",
        },
        {
            "question": "Co robi groups student?",
            "answer": "Wyświetla grupy użytkownika student.",
        },
        {
            "question": "Czy użytkownik może należeć do wielu grup?",
            "answer": "Tak. Użytkownik może należeć do jednej grupy podstawowej i wielu dodatkowych.",
        },
        {
            "question": "Po co w Linuxie są grupy?",
            "answer": "Grupy ułatwiają zarządzanie dostępem do plików, katalogów i zasobów.",
        },
        {
            "question": "Czy nazwa użytkownika i UID to to samo?",
            "answer": "Nie. Nazwa jest tekstowa, a UID jest numerycznym identyfikatorem.",
        },
        {
            "question": "Czy nazwa grupy i GID to to samo?",
            "answer": "Nie. Nazwa grupy jest tekstowa, a GID jest numerycznym identyfikatorem.",
        },
        {
            "question": "Co oznacza uid=1000(student)?",
            "answer": "Użytkownik student ma identyfikator UID równy 1000.",
        },
        {
            "question": "Co oznacza gid=1000(student)?",
            "answer": "Podstawowa grupa użytkownika ma identyfikator GID równy 1000 i nazwę student.",
        },
        {
            "question": "Co oznacza groups=1000(student),10(wheel)?",
            "answer": "Użytkownik należy do grup student oraz wheel.",
        },
        {
            "question": "Czym jest grupa podstawowa użytkownika?",
            "answer": "To główna grupa przypisana użytkownikowi, widoczna między innymi jako GID.",
        },
        {
            "question": "Czym są grupy dodatkowe?",
            "answer": "To dodatkowe grupy, do których należy użytkownik oprócz grupy podstawowej.",
        },
        {
            "question": "Czy grupy mają znaczenie przy uprawnieniach plików?",
            "answer": "Tak. Uprawnienia plików są podzielone między właściciela, grupę i innych.",
        },
        {
            "question": "Co warto sprawdzić przed analizą problemu z uprawnieniami?",
            "answer": "Warto sprawdzić użytkownika komendą whoami oraz grupy komendą id lub groups.",
        },
        {
            "question": "Czy whoami pokazuje nazwę hosta?",
            "answer": "Nie. whoami pokazuje nazwę użytkownika.",
        },
        {
            "question": "Czy id służy do zmiany użytkownika?",
            "answer": "Nie. id tylko wyświetla informacje o użytkowniku.",
        },
        {
            "question": "Czy groups tworzy nową grupę?",
            "answer": "Nie. groups tylko pokazuje grupy użytkownika.",
        },
        {
            "question": "Jaka komenda jest najlepsza do szybkiego sprawdzenia aktualnego użytkownika?",
            "answer": "whoami.",
        },
        {
            "question": "Jaka komenda jest najlepsza do sprawdzenia UID i GID?",
            "answer": "id.",
        },
        {
            "question": "Jaka komenda jest najlepsza do sprawdzenia listy grup?",
            "answer": "groups.",
        },
        {
            "question": "Dlaczego UID jest ważny?",
            "answer": "System identyfikuje użytkowników głównie po UID, a nie tylko po nazwie.",
        },
        {
            "question": "Dlaczego GID jest ważny?",
            "answer": "GID wskazuje grupę, która może mieć określone uprawnienia do plików i katalogów.",
        },
        {
            "question": "Czy dwóch użytkowników powinno mieć ten sam UID?",
            "answer": "Nie. UID powinien jednoznacznie identyfikować użytkownika.",
        },
    ],
}