LOG_ANALYSIS = {
    "module": {
        "title": "Administracja systemem",
        "description": "Moduł poświęcony podstawowej administracji systemem Linux.",
    },
    "lesson": {
        "title": "Analiza logów w praktyce: journalctl, /var/log i filtrowanie zdarzeń",
        "level": "Podstawowy+",
        "duration": "45 min",
        "description": (
            "Nauczysz się zawężać logi według czasu, usługi, priorytetu i tekstu oraz "
            "łączyć informacje z journala i plików w katalogu /var/log."
        ),
        "theory": (
            "Skuteczna analiza logów nie polega na czytaniu tysięcy wpisów od początku. Najpierw "
            "trzeba określić przybliżony czas problemu, usługę i objaw, a potem stopniowo zawężać "
            "wynik. Systemd journal przechowuje ustrukturyzowane zdarzenia, które można filtrować "
            "przez <code>journalctl</code>. Opcja <code>-u</code> wybiera jednostkę, "
            "<code>--since</code> i <code>--until</code> ograniczają czas, <code>-p</code> wybiera "
            "priorytet, a <code>-b</code> wskazuje uruchomienie systemu. Priorytety obejmują między "
            "innymi <code>warning</code>, <code>err</code>, <code>crit</code> i "
            "<code>emerg</code>. W Rocky Linux klasyczne logi mogą znajdować się w "
            "<code>/var/log/messages</code>, <code>/var/log/secure</code> oraz podkatalogach "
            "konkretnych usług. Do plików przydają się <code>tail</code>, <code>less</code> i "
            "<code>grep</code>. Wyszukiwanie powinno uwzględniać kontekst: samo słowo "
            "„error” nie wykryje każdego problemu, a pojedynczy wpis bez czasu i sąsiednich linii "
            "może prowadzić do błędnego wniosku. Rotacja logów powoduje, że starsze dane mogą "
            "znajdować się w plikach z numerem lub rozszerzeniem kompresji. Analizę warto prowadzić "
            "od objawu do dowodu: zanotować czas, odtworzyć problem, obserwować nowe wpisy i "
            "porównać komunikaty różnych warstw systemu."
        ),
        "commands": [
            {
                "command": "journalctl --since \"30 minutes ago\"",
                "description": "Pokazuje zdarzenia z ostatnich 30 minut.",
                "example": "$ journalctl --since \"30 minutes ago\"",
            },
            {
                "command": "journalctl --since \"2026-06-19 10:00\" --until \"2026-06-19 10:15\"",
                "description": "Ogranicza dziennik do konkretnego przedziału czasu.",
                "example": "$ journalctl --since \"2026-06-19 10:00\" --until \"2026-06-19 10:15\"",
            },
            {
                "command": "journalctl -u crond -p warning -b",
                "description": "Pokazuje ostrzeżenia i poważniejsze wpisy crond z bieżącego uruchomienia.",
                "example": "$ journalctl -u crond -p warning -b",
            },
            {
                "command": "journalctl -f",
                "description": "Obserwuje nowe wpisy w journalu na żywo.",
                "example": "$ journalctl -f",
            },
            {
                "command": "sudo tail -n 50 /var/log/messages",
                "description": "Pokazuje 50 ostatnich linii ogólnego logu systemowego.",
                "example": "$ sudo tail -n 50 /var/log/messages",
            },
            {
                "command": "sudo less /var/log/secure",
                "description": "Pozwala wygodnie przeglądać log zdarzeń uwierzytelniania.",
                "example": "$ sudo less /var/log/secure",
            },
            {
                "command": "sudo grep -i \"failed\" /var/log/secure",
                "description": "Wyszukuje słowo failed bez rozróżniania wielkości liter.",
                "example": "$ sudo grep -i \"failed\" /var/log/secure",
            },
            {
                "command": "sudo grep -n -C 2 \"error\" /var/log/messages",
                "description": "Pokazuje numery linii oraz dwie linie kontekstu wokół dopasowania.",
                "example": "$ sudo grep -n -C 2 \"error\" /var/log/messages",
            },
            {
                "command": "ls -lh /var/log",
                "description": "Pokazuje pliki logów wraz z ich rozmiarami i datami.",
                "example": "$ ls -lh /var/log",
            },
        ],
        "practice_task": (
            "Zanotuj bieżący czas, a następnie w jednym terminalu uruchom "
            "<code>sudo journalctl -f</code>. W drugim terminalu wykonaj bezpieczną akcję "
            "generującą wpis, na przykład <code>sudo systemctl status crond</code>, i sprawdź, "
            "czy pojawiło się powiązane zdarzenie. Zakończ obserwację klawiszami Ctrl+C. Potem "
            "wyświetl logi z ostatnich 15 minut, ogranicz je do usługi crond i porównaj wynik z "
            "<code>journalctl -u crond -p warning --since \"15 minutes ago\"</code>. Na końcu "
            "sprawdź listę plików w <code>/var/log</code> i, bez modyfikowania danych, wyszukaj "
            "w dostępnym logu wpisy zawierające „failed” wraz z kontekstem."
        ),
        "common_mistakes": [
            "Czytanie całego dziennika bez ograniczenia czasu, usługi lub liczby wpisów.",
            "Zakładanie, że każdy problem zawiera dosłowne słowo error.",
            "Ignorowanie znacznika czasu i kolejności zdarzeń.",
            "Wyciąganie wniosku z pojedynczej linii bez sprawdzenia kontekstu.",
            "Mylenie braku uprawnień do odczytu logu z brakiem wpisów.",
            "Pomijanie rotowanych plików podczas szukania starszego zdarzenia.",
            "Usuwanie lub czyszczenie logów przed zakończeniem diagnozy.",
        ],
        "summary": (
            "Analizę logów prowadź od czasu i objawu do coraz dokładniejszych filtrów. "
            "<code>journalctl</code> filtruje zdarzenia według jednostki, czasu, uruchomienia "
            "systemu i priorytetu. W <code>/var/log</code> korzystaj z <code>tail</code>, "
            "<code>less</code> i <code>grep</code>, zachowując kontekst wpisów. Logi są dowodem "
            "diagnostycznym, dlatego nie należy ich usuwać przed wyjaśnieniem problemu."
        ),
    },
    "quiz": {
        "title": "Quiz: analiza logów w praktyce",
        "description": "Sprawdź, czy potrafisz zawężać zdarzenia i interpretować wynik.",
        "questions": [
            {
                "text": "Awaria wystąpiła około 10:05. Jaki filtr najbardziej ograniczy niepotrzebne wpisy?",
                "answers": [
                    ("a", "Zakres --since i --until obejmujący czas awarii", True),
                    ("b", "Wyświetlenie całego journala od początku", False),
                    ("c", "Usunięcie plików z /var/log", False),
                    ("d", "Zmiana nazwy hosta", False),
                ],
            },
            {
                "text": "Co robi journalctl -u crond -p warning -b?",
                "answers": [
                    ("a", "Pokazuje ostrzeżenia i poważniejsze wpisy crond z bieżącego startu", True),
                    ("b", "Restartuje crond po każdym ostrzeżeniu", False),
                    ("c", "Usuwa ostrzeżenia z dziennika", False),
                    ("d", "Włącza crond przy starcie systemu", False),
                ],
            },
            {
                "text": "Dlaczego grep -C 2 jest przydatny podczas analizy logu?",
                "answers": [
                    ("a", "Pokazuje linie otaczające dopasowanie", True),
                    ("b", "Kompresuje log dwukrotnie", False),
                    ("c", "Czyści dwie ostatnie linie", False),
                    ("d", "Zmienia priorytet wpisu", False),
                ],
            },
            {
                "text": "Nie znaleziono słowa error. Jaki wniosek jest poprawny?",
                "answers": [
                    ("a", "Problem nadal może być opisany innym słowem lub priorytetem", True),
                    ("b", "System na pewno działa poprawnie", False),
                    ("c", "Należy natychmiast usunąć journal", False),
                    ("d", "Logi są zawsze nieprzydatne", False),
                ],
            },
            {
                "text": "Do czego służy journalctl -f?",
                "answers": [
                    ("a", "Do obserwowania nowych zdarzeń na żywo", True),
                    ("b", "Do formatowania partycji", False),
                    ("c", "Do włączania firewalla", False),
                    ("d", "Do edycji crontaba", False),
                ],
            },
            {
                "text": "Gdzie w Rocky Linux mogą znajdować się zdarzenia uwierzytelniania?",
                "answers": [
                    ("a", "W /var/log/secure oraz w journalu", True),
                    ("b", "Wyłącznie w /tmp/passwords", False),
                    ("c", "W /etc/hostname", False),
                    ("d", "W /opt/bin", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Od czego zacząć analizę logów?", "answer": "Od określenia czasu, objawu i powiązanej usługi."},
        {"question": "Do czego służy journalctl --since?", "answer": "Do ustawienia początku analizowanego zakresu czasu."},
        {"question": "Do czego służy journalctl --until?", "answer": "Do ustawienia końca analizowanego zakresu czasu."},
        {"question": "Co robi opcja -u?", "answer": "Filtruje journal według jednostki systemd."},
        {"question": "Co robi opcja -p?", "answer": "Filtruje wpisy według priorytetu."},
        {"question": "Co oznacza priorytet warning?", "answer": "Ostrzeżenie oraz, przy takim filtrze, także poważniejsze zdarzenia."},
        {"question": "Co oznacza priorytet err?", "answer": "Błąd o wyższym znaczeniu niż zwykłe ostrzeżenie."},
        {"question": "Co robi journalctl -b?", "answer": "Pokazuje wpisy z bieżącego uruchomienia systemu."},
        {"question": "Co robi journalctl -f?", "answer": "Wyświetla nowe wpisy w miarę ich pojawiania się."},
        {"question": "Jak zakończyć journalctl -f?", "answer": "Nacisnąć Ctrl+C."},
        {"question": "Do czego służy /var/log/messages?", "answer": "Do przechowywania wielu ogólnych komunikatów systemowych w Rocky Linux."},
        {"question": "Co może zawierać /var/log/secure?", "answer": "Zdarzenia związane z uwierzytelnianiem i bezpieczeństwem."},
        {"question": "Co robi tail -n 50?", "answer": "Pokazuje 50 ostatnich linii pliku."},
        {"question": "Dlaczego less jest wygodny przy logach?", "answer": "Pozwala przewijać i wyszukiwać bez edytowania pliku."},
        {"question": "Co robi grep -i?", "answer": "Wyszukuje bez rozróżniania wielkości liter."},
        {"question": "Co robi grep -n?", "answer": "Dodaje numery linii do dopasowań."},
        {"question": "Co robi grep -C 2?", "answer": "Pokazuje dwie linie kontekstu przed i po dopasowaniu."},
        {"question": "Dlaczego samo szukanie error nie wystarcza?", "answer": "Problemy mogą być opisane jako failed, denied, timeout lub innym komunikatem."},
        {"question": "Dlaczego czas wpisu jest ważny?", "answer": "Pozwala połączyć zdarzenie z momentem wystąpienia objawu."},
        {"question": "Czym jest rotacja logów?", "answer": "Okresowym zamykaniem, archiwizowaniem i zastępowaniem plików logów."},
        {"question": "Gdzie mogą być starsze logi plikowe?", "answer": "W rotowanych plikach z numerem, datą lub rozszerzeniem kompresji."},
        {"question": "Co może oznaczać Permission denied przy odczycie logu?", "answer": "Brak wymaganych uprawnień, a nie brak danych."},
        {"question": "Dlaczego nie usuwać logów podczas diagnozy?", "answer": "Można utracić dowody potrzebne do ustalenia przyczyny."},
        {"question": "Po co odtwarzać problem podczas obserwacji logów?", "answer": "Aby powiązać nowy objaw z konkretnymi wpisami."},
        {"question": "Jaki jest dobry schemat filtrowania?", "answer": "Czas, usługa, priorytet, tekst i kontekst sąsiednich zdarzeń."},
    ],
}
