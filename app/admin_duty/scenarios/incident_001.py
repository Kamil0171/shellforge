BROKEN_EXEC_START = (
    "/opt/ironvale/venv/bin/uvicorn "
    "app.main:app --host 127.0.0.1 --port 8100"
)

CORRECT_EXEC_START = (
    "/srv/ironvale/venv/bin/uvicorn "
    "app.main:app --host 127.0.0.1 --port 8100"
)

SERVICE_FILE_PATH = "/etc/systemd/system/ironvale-api.service"

SERVICE_FILE = """[Unit]
Description=IronVale API
After=network.target

[Service]
User=ironvale
Group=ironvale
WorkingDirectory=/srv/ironvale/app
ExecStart={exec_start}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

VIRTUAL_FILESYSTEM = {
    "/": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "root",
        "group": "root",
    },
    "/etc": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "root",
        "group": "root",
    },
    "/etc/systemd": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "root",
        "group": "root",
    },
    "/etc/systemd/system": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "root",
        "group": "root",
    },
    "/etc/systemd/system/ironvale-api.service": {
        "type": "file",
        "mode": "-rw-r--r--",
        "owner": "root",
        "group": "root",
        "content": SERVICE_FILE.format(exec_start=BROKEN_EXEC_START),
    },
    "/etc/systemd/system/multi-user.target.wants": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "root",
        "group": "root",
    },
    "/home": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "root",
        "group": "root",
    },
    "/home/operator": {
        "type": "directory",
        "mode": "drwxr-x---",
        "owner": "operator",
        "group": "operator",
    },
    "/home/operator/.profile": {
        "type": "file",
        "mode": "-rw-r--r--",
        "owner": "operator",
        "group": "operator",
        "content": "export EDITOR=vi\n",
    },
    "/opt": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "root",
        "group": "root",
    },
    "/opt/ironvale": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "ironvale",
        "group": "ironvale",
    },
    "/opt/ironvale/venv": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "ironvale",
        "group": "ironvale",
    },
    "/opt/ironvale/venv/bin": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "ironvale",
        "group": "ironvale",
    },
    "/srv": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "root",
        "group": "root",
    },
    "/srv/ironvale": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "ironvale",
        "group": "ironvale",
    },
    "/srv/ironvale/app": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "ironvale",
        "group": "ironvale",
    },
    "/srv/ironvale/venv": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "ironvale",
        "group": "ironvale",
    },
    "/srv/ironvale/venv/bin": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "ironvale",
        "group": "ironvale",
    },
    "/srv/ironvale/venv/bin/python": {
        "type": "file",
        "mode": "-rwxr-xr-x",
        "owner": "ironvale",
        "group": "ironvale",
        "content": "ELF 64-bit LSB executable, x86-64\n",
    },
    "/srv/ironvale/venv/bin/uvicorn": {
        "type": "file",
        "mode": "-rwxr-xr-x",
        "owner": "ironvale",
        "group": "ironvale",
        "content": (
            "#!/srv/ironvale/venv/bin/python\n"
            "from uvicorn.main import main\n"
        ),
    },
    "/var": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "root",
        "group": "root",
    },
    "/var/log": {
        "type": "directory",
        "mode": "drwxr-xr-x",
        "owner": "root",
        "group": "root",
    },
}


SCENARIO = {
    "id": "INC-001",
    "slug": "inc-001",
    "title": "502 po wdrożeniu",
    "company": "IronVale Systems",
    "environment": "Produkcja",
    "difficulty": "Podstawowy",
    "difficulty_level": 1,
    "estimated_time": "10–15 min",
    "status": "available",
    "tags": [
        "Linux",
        "systemd",
        "diagnostyka",
    ],
    "description": (
        "Po wieczornym wdrożeniu portal IronVale Systems przestał "
        "odpowiadać prawidłowo. Użytkownicy otrzymują błąd "
        "502 Bad Gateway."
    ),
    "objective": (
        "Przywróć działanie portalu bez restartowania całego serwera."
    ),
    "briefing": (
        "Monitoring zgłosił wzrost odpowiedzi HTTP 502 kilka minut "
        "po zakończeniu wdrożenia. Warstwa brzegowa i baza danych "
        "nadal odpowiadają, ale usługa aplikacyjna nie działa "
        "prawidłowo. Zdiagnozuj problem i przywróć usługę."
    ),
    "infrastructure": {
        "domain": "portal.ironvale.internal",
        "edge_server": "edge-01",
        "application_server": "app-01",
        "database_server": "db-01",
        "operations_host": "ops-01",
        "service": "ironvale-api.service",
        "application_port": 8100,
    },
    "available_tools": [
        "Terminal administracyjny",
        "Monitoring usług",
        "Zgłoszenie INC-001",
    ],
    "objectives": [
        {
            "key": "check_portal",
            "label": "Sprawdź dostępność portalu",
        },
        {
            "key": "identify_layer",
            "label": "Ustal, która warstwa infrastruktury zawodzi",
        },
        {
            "key": "find_cause",
            "label": "Zidentyfikuj przyczynę problemu",
        },
        {
            "key": "restore_service",
            "label": "Przywróć działanie aplikacji",
        },
        {
            "key": "verify_portal",
            "label": "Potwierdź poprawne działanie portalu",
        },
    ],
    "hints": [
        {
            "cost": 25,
            "text": (
                "Błąd 502 nie musi oznaczać problemu z samym Nginxem. "
                "Sprawdź również usługę znajdującą się za reverse proxy."
            ),
        },
        {
            "cost": 50,
            "text": (
                "Sprawdź stan usługi ironvale-api oraz jej ostatnie "
                "komunikaty w dzienniku systemd."
            ),
        },
        {
            "cost": 100,
            "text": (
                "Zwróć uwagę na ścieżkę programu określoną w ExecStart "
                "jednostki ironvale-api.service."
            ),
        },
    ],
    "solution": [
        {
            "command": "curl https://portal.ironvale.internal",
            "purpose": (
                "Potwierdź zgłoszony problem i sprawdź kod odpowiedzi portalu."
            ),
        },
        {
            "command": "systemctl status ironvale-api",
            "purpose": (
                "Sprawdź, czy usługa aplikacyjna za reverse proxy działa."
            ),
        },
        {
            "command": "journalctl -u ironvale-api",
            "purpose": (
                "Odczytaj ostatnie komunikaty usługi i ustal przyczynę awarii."
            ),
        },
        {
            "command": "cat /etc/systemd/system/ironvale-api.service",
            "purpose": (
                "Zweryfikuj aktualną definicję jednostki i wartość ExecStart."
            ),
        },
        {
            "command": "edit-service",
            "purpose": "Otwórz plik jednostki w edytorze gry.",
            "instruction": (
                "W wierszu ExecStart zmień ścieżkę "
                "/opt/ironvale/venv/bin/uvicorn na "
                "/srv/ironvale/venv/bin/uvicorn, a następnie zapisz plik."
            ),
        },
        {
            "command": "systemctl daemon-reload",
            "purpose": (
                "Przeładuj konfigurację systemd po zmianie pliku jednostki."
            ),
        },
        {
            "command": "systemctl restart ironvale-api",
            "purpose": "Uruchom ponownie usługę z poprawioną konfiguracją.",
        },
        {
            "command": "curl https://portal.ironvale.internal",
            "purpose": (
                "Wykonaj test końcowy i potwierdź odpowiedź HTTP 200."
            ),
        },
    ],
    "filesystem": VIRTUAL_FILESYSTEM,
    "initial_state": {
        "current_working_directory": "/home/operator",
        "configuration_fixed": False,
        "daemon_reloaded": False,
        "service_running": False,
        "mission_complete": False,
        "commands_used": 0,
        "score": 1000,
        "portal_checked": False,
        "service_checked": False,
        "cause_identified": False,
        "service_file_inspected": False,
        "correct_binary_found": False,
        "broken_binary_checked": False,
        "portal_verified": False,
        "hints_used": 0,
        "solution_viewed": False,
    },
}
