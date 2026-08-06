ENVIRONMENT_SECRETS = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Zmienne środowiskowe i sekrety aplikacji",
        "level": "Średnio zaawansowany",
        "duration": "60 min",
        "description": (
            "Oddzielisz konfigurację od kodu, przygotujesz chroniony plik .env dla usługi systemd i "
            "nauczysz się sprawdzać konfigurację bez ujawniania sekretów."
        ),
        "theory": (
            "Kod opisuje zachowanie aplikacji, a konfiguracja określa wartości zależne od środowiska, takie "
            "jak tryb pracy, adres bazy lub klucz używany do podpisywania danych. Zmienne środowiskowe są "
            "parami nazwa-wartość przekazywanymi procesowi. Sekret to wartość wymagająca szczególnej ochrony, "
            "na przykład hasło, token lub klucz. Nie należy zapisywać sekretów w repozytorium, ponieważ "
            "pozostają w historii Git nawet po usunięciu z bieżącego pliku. Plik "
            "<code>/opt/example-app/.env</code> może przechowywać konfigurację konkretnego serwera, a "
            "<code>.env.example</code> tylko nazwy wymaganych zmiennych i bezpieczne wartości przykładowe. "
            "Prawdziwy <code>.env</code> należy dodać do <code>.gitignore</code>. Plik na serwerze powinien "
            "należeć do użytkownika usługi i mieć uprawnienia 600. W jednostce systemd dyrektywa "
            "<code>EnvironmentFile=/opt/example-app/.env</code> wczytuje wartości bez umieszczania ich w "
            "<code>ExecStart</code>. Aplikacja powinna odczytać konfigurację przy starcie, sprawdzić wymagane "
            "pola i zakończyć się czytelnym błędem bez drukowania sekretu. Brak zmiennej, pusty ciąg i wartość "
            "o błędnym formacie to trzy różne przypadki, które wymagają osobnej walidacji. Po zmianie pliku "
            "trzeba zrestartować usługę, ponieważ działający proces zwykle nie odczyta go ponownie. Obecność "
            "zmiennej można sprawdzić przez <code>grep -q</code>, który zwraca kod wyjścia bez drukowania "
            "wartości. Rotacja sekretu polega na wygenerowaniu nowej wartości, bezpiecznym podmienieniu jej w "
            "źródle konfiguracji, restarcie usługi, weryfikacji działania i unieważnieniu starej wartości, gdy "
            "dany system to umożliwia. Plik .env jest prostym rozwiązaniem dla pojedynczego serwera, ale nie "
            "zapewnia centralnego audytu ani dystrybucji. Bardziej rozbudowane środowiska mogą używać "
            "zewnętrznych menedżerów sekretów."
        ),
        "commands": [
            {
                "command": "sudo install -o example-app -g example-app -m 600 /dev/null /opt/example-app/.env",
                "description": "Tworzy pusty plik konfiguracji z ograniczonym dostępem i właściwym właścicielem.",
                "example": "$ sudo install -o example-app -g example-app -m 600 /dev/null /opt/example-app/.env",
            },
            {
                "command": "test -f /opt/example-app/.env",
                "description": "Sprawdza istnienie pliku bez wyświetlania jego zawartości.",
                "example": "$ test -f /opt/example-app/.env",
            },
            {
                "command": "grep -q '^SECRET_KEY=' /opt/example-app/.env",
                "description": "Sprawdza obecność wpisu SECRET_KEY wyłącznie przez kod wyjścia.",
                "example": "$ grep -q '^SECRET_KEY=' /opt/example-app/.env",
            },
            {
                "command": "sudo systemctl show example-app --property=EnvironmentFiles",
                "description": "Pokazuje, z jakiego pliku środowiskowego korzysta jednostka systemd.",
                "example": "$ sudo systemctl show example-app --property=EnvironmentFiles",
            },
            {
                "command": "sudo systemctl restart example-app",
                "description": "Uruchamia proces ponownie, aby odczytał zaktualizowaną konfigurację.",
                "example": "$ sudo systemctl restart example-app",
            },
            {
                "command": "sudo stat -c '%U %G %a' /opt/example-app/.env",
                "description": "Sprawdza właściciela, grupę i tryb pliku bez ujawniania sekretów.",
                "example": "$ sudo stat -c '%U %G %a' /opt/example-app/.env\nexample-app example-app 600",
            },
        ],
        "practice_task": (
            "Przygotuj <code>.env.example</code> zawierający nazwy <code>APP_ENV</code>, "
            "<code>DATABASE_URL</code> i <code>SECRET_KEY</code> bez prawdziwego sekretu. Dodaj "
            "<code>.env</code> do <code>.gitignore</code>. Na serwerze utwórz "
            "<code>/opt/example-app/.env</code> z właścicielem <code>example-app</code> i trybem 600, a jako "
            "wartości laboratoryjne użyj <code>APP_ENV=production</code>, "
            "<code>DATABASE_URL=sqlite:////opt/example-app/data/app.db</code> i "
            "<code>SECRET_KEY=change-me-in-production</code>. Dodaj <code>EnvironmentFile</code> do "
            "przykładowej jednostki, zrestartuj usługę i sprawdź jedynie obecność wymaganych wpisów."
        ),
        "common_mistakes": [
            "Dodawanie prawdziwego pliku .env lub sekretu do repozytorium Git.",
            "Nadawanie plikowi .env zbyt szerokich uprawnień odczytu.",
            "Wpisywanie sekretu bezpośrednio w ExecStart jednostki systemd.",
            "Wyświetlanie pełnych wartości zmiennych w logach lub poleceniach diagnostycznych.",
            "Brak restartu usługi po zmianie konfiguracji środowiskowej.",
            "Traktowanie brakującej, pustej i błędnej wartości jako tego samego przypadku.",
        ],
        "summary": (
            "Konfiguracja zależna od środowiska powinna być oddzielona od kodu, a sekrety nie mogą trafiać "
            "do repozytorium ani logów. Plik .env na pojedynczym serwerze wymaga właściwego właściciela i "
            "trybu 600, natomiast .env.example dokumentuje wymagane nazwy. Systemd może wczytać plik przez "
            "EnvironmentFile, a po zmianie wartości usługę trzeba zrestartować i bezpiecznie zweryfikować."
        ),
    },
    "quiz": {
        "title": "Quiz: zmienne środowiskowe i sekrety aplikacji",
        "description": "Sprawdź bezpieczne zarządzanie konfiguracją aplikacji na serwerze.",
        "questions": [
            {
                "text": "Dlaczego sekretu nie należy zapisywać w repozytorium?",
                "answers": [
                    ("a", "Może pozostać w historii i trafić do osób mających dostęp do repozytorium", True),
                    ("b", "Git nie obsługuje plików tekstowych", False),
                    ("c", "Systemd automatycznie go usuwa", False),
                    ("d", "Sekret uniemożliwia utworzenie brancha", False),
                ],
            },
            {
                "text": "Do czego służy .env.example?",
                "answers": [
                    ("a", "Dokumentuje wymagane zmienne bez prawdziwych sekretów", True),
                    ("b", "Przechowuje produkcyjne tokeny", False),
                    ("c", "Zastępuje .gitignore", False),
                    ("d", "Uruchamia usługę systemd", False),
                ],
            },
            {
                "text": "Jakie uprawnienia są odpowiednie dla pliku .env użytkownika usługi?",
                "answers": [
                    ("a", "600 i właściwy właściciel", True),
                    ("b", "777 dla wszystkich", False),
                    ("c", "644 niezależnie od zawartości", False),
                    ("d", "Brak właściciela", False),
                ],
            },
            {
                "text": "Jak bezpiecznie sprawdzić obecność SECRET_KEY w pliku?",
                "answers": [
                    ("a", "Użyć grep -q i sprawdzić kod wyjścia", True),
                    ("b", "Wydrukować cały plik w publicznym logu", False),
                    ("c", "Dodać wartość do nazwy procesu", False),
                    ("d", "Wysłać plik do repozytorium", False),
                ],
            },
            {
                "text": "Co zrobić po zmianie wartości w .env używanym przez usługę?",
                "answers": [
                    ("a", "Zrestartować usługę i zweryfikować jej działanie", True),
                    ("b", "Zrestartować DNS", False),
                    ("c", "Usunąć EnvironmentFile", False),
                    ("d", "Zmienić port HTTPS", False),
                ],
            },
            {
                "text": "Jak aplikacja powinna reagować na brak wymaganej zmiennej?",
                "answers": [
                    ("a", "Zgłosić czytelny błąd bez ujawniania sekretu", True),
                    ("b", "Kontynuować zawsze z pustą wartością", False),
                    ("c", "Wypisać wszystkie zmienne do logu", False),
                    ("d", "Automatycznie zapisać sekret w Git", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym różni się kod od konfiguracji?", "answer": "Kod opisuje zachowanie, a konfiguracja wartości zależne od środowiska."},
        {"question": "Czym jest zmienna środowiskowa?", "answer": "Nazwaną wartością przekazywaną procesowi przez jego środowisko."},
        {"question": "Czym jest sekret aplikacji?", "answer": "Poufną wartością, na przykład hasłem, tokenem lub kluczem podpisującym."},
        {"question": "Dlaczego sekret nie powinien trafić do Git?", "answer": "Może pozostać w historii i zostać ujawniony osobom z dostępem."},
        {"question": "Do czego służy plik .env?", "answer": "Do przechowywania konfiguracji środowiskowej konkretnego wdrożenia."},
        {"question": "Do czego służy .env.example?", "answer": "Dokumentuje nazwy zmiennych i bezpieczne przykłady bez sekretów."},
        {"question": "Co dodać do .gitignore?", "answer": "Prawdziwy plik .env i inne lokalne pliki zawierające sekrety."},
        {"question": "Jaki tryb może mieć .env?", "answer": "600, aby odczytywał i zapisywał go tylko właściciel."},
        {"question": "Kto powinien być właścicielem .env?", "answer": "Użytkownik usługi lub konto zarządzające konfiguracją zgodnie z modelem uprawnień."},
        {"question": "Co robi EnvironmentFile w systemd?", "answer": "Wczytuje zmienne z pliku do środowiska uruchamianego procesu."},
        {"question": "Dlaczego nie wpisywać sekretu w ExecStart?", "answer": "Może być łatwiej ujawniony w konfiguracji i informacjach o procesie."},
        {"question": "Kiedy aplikacja odczytuje zmienne?", "answer": "Najczęściej podczas uruchamiania procesu."},
        {"question": "Co zrobić po zmianie .env?", "answer": "Zrestartować usługę i sprawdzić jej działanie."},
        {"question": "Jak sprawdzić istnienie .env?", "answer": "Poleceniem test -f /opt/example-app/.env."},
        {"question": "Co daje grep -q?", "answer": "Sprawdza dopasowanie kodem wyjścia bez drukowania znalezionej wartości."},
        {"question": "Czy brak i pusta wartość są tym samym?", "answer": "Nie, zmienna może nie istnieć albo istnieć z pustą wartością."},
        {"question": "Czym jest błędna wartość?", "answer": "Wartością obecną, lecz niezgodną z wymaganym formatem lub zakresem."},
        {"question": "Jak logować błąd konfiguracji?", "answer": "Podać nazwę problematycznego pola i przyczynę bez jego poufnej wartości."},
        {"question": "Czym jest rotacja sekretu?", "answer": "Kontrolowaną wymianą starej wartości na nową i unieważnieniem starej."},
        {"question": "Co sprawdzić po rotacji?", "answer": "Status usługi, logi bez sekretów i działanie funkcji zależnej od wartości."},
        {"question": "Czy APP_ENV zwykle jest sekretem?", "answer": "Nie, lecz nadal jest konfiguracją zależną od środowiska."},
        {"question": "Czy DATABASE_URL może być sekretem?", "answer": "Tak, jeśli zawiera dane uwierzytelniające do bazy."},
        {"question": "Jak sprawdzić źródło zmiennych systemd?", "answer": "Poleceniem systemctl show z właściwością EnvironmentFiles."},
        {"question": "Jakie ograniczenie ma lokalny .env?", "answer": "Nie zapewnia centralnej dystrybucji, audytu ani automatycznej rotacji."},
        {"question": "Co stosują większe środowiska?", "answer": "Mogą korzystać z zewnętrznych menedżerów sekretów."},
    ],
}
