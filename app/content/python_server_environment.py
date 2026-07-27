PYTHON_SERVER_ENVIRONMENT = {
    "module": {
        "title": "Deployment aplikacji",
        "description": "Moduł poświęcony praktycznemu wdrażaniu aplikacji webowej na serwerze Linux.",
    },
    "lesson": {
        "title": "Środowisko Python na serwerze",
        "level": "Średnio zaawansowany",
        "duration": "50 min",
        "description": (
            "Utworzysz izolowane środowisko Python na serwerze, zainstalujesz zależności i sprawdzisz, "
            "czy aplikacja używa właściwego interpretera oraz spójnego zestawu pakietów."
        ),
        "theory": (
            "Systemowy Python jest używany także przez narzędzia systemu, dlatego instalowanie pakietów "
            "aplikacji globalnym <code>pip</code> może powodować konflikty. Moduł <code>venv</code> tworzy "
            "izolowane środowisko z własnym interpreterem i katalogiem pakietów. Dla przykładowej aplikacji "
            "może to być <code>/opt/example-app/venv</code>. Po aktywacji powłoka wskazuje pliki wykonywalne "
            "z tego środowiska, ale skrypty automatyczne i systemd nie powinny polegać na aktywacji. Mogą "
            "wywoływać bezpośrednio <code>/opt/example-app/venv/bin/python</code> lub program z katalogu "
            "<code>bin</code>. Polecenie <code>python -m pip</code> jednoznacznie uruchamia pip powiązany "
            "z wybranym interpreterem. Po instalacji z <code>requirements.txt</code> warto wykonać "
            "<code>pip check</code>, aby znaleźć niespełnione lub sprzeczne zależności. Katalog kodu i venv "
            "musi mieć właściciela oraz uprawnienia pozwalające dedykowanemu użytkownikowi czytać kod i "
            "uruchamiać pliki. Odtwarzalność oznacza, że na świeżym serwerze można utworzyć nowe venv i "
            "zainstalować ten sam kontrolowany zestaw zależności, zamiast kopiować przypadkowy stan z komputera."
        ),
        "commands": [
            {
                "command": "python3 -m venv /opt/example-app/venv",
                "description": "Tworzy środowisko wirtualne dla aplikacji.",
                "example": "$ python3 -m venv /opt/example-app/venv",
            },
            {
                "command": "source /opt/example-app/venv/bin/activate",
                "description": "Aktywuje venv w bieżącej sesji powłoki.",
                "example": "$ source /opt/example-app/venv/bin/activate",
            },
            {
                "command": "which python",
                "description": "Pokazuje interpreter wybierany po wpisaniu python.",
                "example": "$ which python\n/opt/example-app/venv/bin/python",
            },
            {
                "command": "python -m pip install -r /opt/example-app/requirements.txt",
                "description": "Instaluje zależności przy użyciu pip powiązanego z aktywnym interpreterem.",
                "example": "$ python -m pip install -r /opt/example-app/requirements.txt",
            },
            {
                "command": "python -m pip check",
                "description": "Sprawdza zgodność zainstalowanych zależności.",
                "example": "$ python -m pip check\nNo broken requirements found.",
            },
            {
                "command": "sudo chown -R example-app:example-app /opt/example-app",
                "description": "Ustawia właściciela katalogu aplikacji i jego zawartości.",
                "example": "$ sudo chown -R example-app:example-app /opt/example-app",
            },
        ],
        "practice_task": (
            "W katalogu laboratoryjnym odpowiadającym <code>/opt/example-app</code> utwórz venv poleceniem "
            "<code>python3 -m venv /opt/example-app/venv</code>. Aktywuj je, sprawdź wynik "
            "<code>which python</code> i <code>python -m pip --version</code>, a następnie zainstaluj "
            "zależności z <code>requirements.txt</code>. Uruchom <code>python -m pip check</code>. Na końcu "
            "wyjdź z venv poleceniem <code>deactivate</code> i porównaj ścieżkę interpretera. Jeżeli ćwiczysz "
            "bez uprawnień do /opt, odtwórz taką samą strukturę w swoim katalogu laboratoryjnym."
        ),
        "common_mistakes": [
            "Instalowanie pakietów aplikacji globalnie do systemowego Pythona.",
            "Uruchamianie zwykłego pip bez sprawdzenia, z którym interpreterem jest powiązany.",
            "Kopiowanie gotowego venv między serwerami zamiast odtworzenia go z requirements.txt.",
            "Nadawanie całemu katalogowi aplikacji zbyt szerokich uprawnień.",
            "Zakładanie, że usługa systemd automatycznie aktywuje venv.",
            "Pomijanie pip check po instalacji lub aktualizacji zależności.",
        ],
        "summary": (
            "Venv izoluje zależności aplikacji od systemowego Pythona. Środowisko tworzy się przez "
            "<code>python3 -m venv</code>, a właściwy interpreter można potwierdzić przez "
            "<code>which python</code>. Instalacja przez <code>python -m pip</code> ogranicza ryzyko użycia "
            "niewłaściwego pip, a <code>pip check</code> sprawdza spójność pakietów. W produkcji proces może "
            "bezpośrednio używać programu z katalogu venv bez aktywowania go w powłoce."
        ),
    },
    "quiz": {
        "title": "Quiz: środowisko Python na serwerze",
        "description": "Sprawdź praktyczne rozumienie venv, pip i uprawnień katalogu aplikacji.",
        "questions": [
            {
                "text": "Dlaczego nie należy instalować zależności aplikacji globalnym pip?",
                "answers": [
                    ("a", "Mogą kolidować z pakietami systemowymi i innymi aplikacjami", True),
                    ("b", "Globalny pip nie potrafi czytać requirements.txt", False),
                    ("c", "Uniemożliwia to działanie DNS", False),
                    ("d", "Każda instalacja globalna zamyka port 8000", False),
                ],
            },
            {
                "text": "Które polecenie tworzy venv dla przykładowej aplikacji?",
                "answers": [
                    ("a", "python3 -m venv /opt/example-app/venv", True),
                    ("b", "pip check /opt/example-app", False),
                    ("c", "source requirements.txt", False),
                    ("d", "systemctl enable python", False),
                ],
            },
            {
                "text": "Co potwierdza which python po aktywacji venv?",
                "answers": [
                    ("a", "Ścieżkę interpretera wybieranego przez powłokę", True),
                    ("b", "Właściciela rekordu DNS", False),
                    ("c", "Port używany przez Nginx", False),
                    ("d", "Status jednostki systemd", False),
                ],
            },
            {
                "text": "Dlaczego warto używać python -m pip?",
                "answers": [
                    ("a", "Uruchamia pip powiązany z konkretnym interpreterem Python", True),
                    ("b", "Automatycznie tworzy usługę systemd", False),
                    ("c", "Zmienia właściciela katalogu", False),
                    ("d", "Testuje konfigurację Nginxa", False),
                ],
            },
            {
                "text": "Co robi python -m pip check?",
                "answers": [
                    ("a", "Sprawdza, czy zainstalowane pakiety mają zgodne zależności", True),
                    ("b", "Aktualizuje wszystkie pakiety systemowe", False),
                    ("c", "Sprawdza dostępność domeny", False),
                    ("d", "Uruchamia aplikację na porcie 8000", False),
                ],
            },
            {
                "text": "Jak usługa systemd może użyć venv bez aktywacji?",
                "answers": [
                    ("a", "Wywołać bezpośrednio program z /opt/example-app/venv/bin", True),
                    ("b", "Zainstalować zależności globalnie jako root", False),
                    ("c", "Dodać venv do rekordu A", False),
                    ("d", "Skopiować venv do /tmp przy każdym starcie", False),
                ],
            },
        ],
    },
    "flashcards": [
        {"question": "Czym jest systemowy Python?", "answer": "Interpreterem dostarczanym przez system, używanym także przez jego narzędzia."},
        {"question": "Czym jest venv?", "answer": "Izolowanym środowiskiem Pythona z własnym interpreterem i katalogiem pakietów."},
        {"question": "Po co izolować zależności?", "answer": "Aby aplikacje nie nadpisywały sobie pakietów i nie kolidowały z systemem."},
        {"question": "Jak utworzyć venv?", "answer": "Poleceniem python3 -m venv ścieżka."},
        {"question": "Gdzie może znajdować się venv aplikacji?", "answer": "Na przykład w /opt/example-app/venv."},
        {"question": "Jak aktywować venv w Bashu?", "answer": "Poleceniem source /opt/example-app/venv/bin/activate."},
        {"question": "Co zmienia aktywacja venv?", "answer": "Modyfikuje środowisko bieżącej powłoki, aby wybierała programy z venv."},
        {"question": "Jak opuścić aktywne venv?", "answer": "Poleceniem deactivate."},
        {"question": "Co pokazuje which python?", "answer": "Ścieżkę programu python wybieranego przez powłokę."},
        {"question": "Dlaczego używać python -m pip?", "answer": "Aby mieć pewność, że pip należy do wybranego interpretera."},
        {"question": "Jak zainstalować requirements.txt?", "answer": "Poleceniem python -m pip install -r requirements.txt."},
        {"question": "Co robi pip check?", "answer": "Wykrywa niespełnione lub sprzeczne zależności zainstalowanych pakietów."},
        {"question": "Czy venv należy kopiować między serwerami?", "answer": "Nie, lepiej odtworzyć je z kontrolowanej listy zależności."},
        {"question": "Co oznacza odtwarzalne środowisko?", "answer": "Można je ponownie zbudować z określonej wersji Pythona i listy zależności."},
        {"question": "Kto musi czytać kod aplikacji?", "answer": "Użytkownik, jako którego działa proces aplikacji."},
        {"question": "Jak zmienić właściciela katalogu?", "answer": "Poleceniem chown, na przykład chown -R użytkownik:grupa katalog."},
        {"question": "Czy chmod 777 jest dobrym rozwiązaniem problemów z dostępem?", "answer": "Nie, nadaje niepotrzebnie szerokie uprawnienia."},
        {"question": "Czy systemd aktywuje venv przez source?", "answer": "Nie musi; ExecStart może wskazywać bezpośrednią ścieżkę do programu w venv."},
        {"question": "Gdzie znajdują się programy venv na Linuxie?", "answer": "W podkatalogu bin środowiska wirtualnego."},
        {"question": "Jak sprawdzić wersję pip wybranego Pythona?", "answer": "Poleceniem python -m pip --version."},
        {"question": "Co zawiera requirements.txt?", "answer": "Nazwy zależności, często wraz z kontrolowanymi wersjami."},
        {"question": "Kiedy uruchomić pip check?", "answer": "Po instalacji lub aktualizacji zależności."},
        {"question": "Dlaczego nie używać przypadkowego polecenia pip?", "answer": "Może wskazywać pip innego interpretera niż ten używany przez aplikację."},
        {"question": "Czy aktywacja venv jest trwała?", "answer": "Nie, dotyczy bieżącej sesji powłoki."},
        {"question": "Jaki jest cel poprawnych uprawnień?", "answer": "Zapewnić procesowi potrzebny dostęp bez nadawania praw innym użytkownikom."},
    ],
}
