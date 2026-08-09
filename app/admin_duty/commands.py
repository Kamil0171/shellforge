import posixpath
import shlex

from app.admin_duty.engine import get_progress, mark_command_used, penalize
from app.admin_duty.scenarios.incident_001 import (
    CORRECT_EXEC_START,
    SERVICE_FILE_PATH,
)

HOME_DIRECTORY = "/home/operator"
CORRECT_UVICORN_PATH = "/srv/ironvale/venv/bin/uvicorn"
BROKEN_UVICORN_PATH = "/opt/ironvale/venv/bin/uvicorn"
EXPLORATION_COMMANDS = {
    "cat",
    "cd",
    "help",
    "ls",
    "pwd",
}


def get_service_file(state: dict) -> str:
    return state["filesystem"][SERVICE_FILE_PATH]["content"]


def execute_command(command: str, state: dict) -> dict:
    command = command.strip()

    if not command:
        return _response(
            "",
            state,
        )

    try:
        parts = shlex.split(command)
    except ValueError:
        return _response(
            "shell: nieprawidłowo zamknięty cudzysłów.",
            state,
            "error",
        )

    command_name = parts[0]
    command_cost = 0 if command_name in EXPLORATION_COMMANDS else 5
    mark_command_used(
        state,
        command_cost,
    )

    if command_name == "help":
        return _help_response(
            parts[1:],
            state,
        )

    if command_name == "pwd":
        if len(parts) > 1:
            return _response(
                "pwd: zbyt wiele argumentów",
                state,
                "error",
            )

        return _response(
            state["current_working_directory"],
            state,
        )

    if command_name == "cd":
        return _change_directory(
            parts[1:],
            state,
        )

    if command_name == "ls":
        return _list_path(
            parts[1:],
            state,
        )

    if command_name == "cat":
        return _read_files(
            parts[1:],
            state,
        )

    if parts == ["ticket"]:
        output = """INC-001
Priority: P1
Environment: Production
Service: portal.ironvale.internal

Po zakończeniu deploymentu portal zaczął zwracać
502 Bad Gateway.

Cel:
Przywróć działanie usługi bez restartowania całego serwera."""

        return _response(
            output,
            state,
        )

    if parts == ["status"]:
        state["service_checked"] = True

        application_state = "active" if state["service_running"] else "failed"

        output = f"""HOST       SERVICE           STATUS
edge-01    nginx             active
app-01     ironvale-api      {application_state}
db-01      postgresql        active"""

        return _response(
            output,
            state,
        )

    if parts == ["curl", "https://portal.ironvale.internal"]:
        state["portal_checked"] = True

        if state["service_running"]:
            state["portal_verified"] = True

            return _response(
                "HTTP/2 200\nIronVale Portal — service operational",
                state,
                "success",
            )

        return _response(
            "HTTP/2 502\nBad Gateway",
            state,
            "error",
        )

    if _matches_service_command(
        parts,
        ["systemctl", "status"],
    ):
        state["service_checked"] = True

        if state["service_running"]:
            output = """● ironvale-api.service - IronVale API
     Loaded: loaded
     Active: active (running)
   Main PID: 2841 (uvicorn)
     Listen: 127.0.0.1:8100"""

            return _response(
                output,
                state,
                "success",
            )

        output = """× ironvale-api.service - IronVale API
     Loaded: loaded
     Active: failed
    Process: 2782 ExecStart=/opt/ironvale/venv/bin/uvicorn
     Result: exit-code"""

        return _response(
            output,
            state,
            "error",
        )

    if _matches_service_command(
        parts,
        ["journalctl", "-u"],
    ):
        state["service_checked"] = True
        state["cause_identified"] = True

        if state["service_running"]:
            output = """ironvale-api[2841]: Started server process
ironvale-api[2841]: Application startup complete
ironvale-api[2841]: Uvicorn running on 127.0.0.1:8100"""

            return _response(
                output,
                state,
                "success",
            )

        output = """systemd[1]: Starting IronVale API...
systemd[2782]: ironvale-api.service:
Failed to locate executable
/opt/ironvale/venv/bin/uvicorn:
No such file or directory"""

        return _response(
            output,
            state,
            "error",
        )

    if parts == ["edit-service"]:
        _mark_path_discovery(
            SERVICE_FILE_PATH,
            state,
        )

        return {
            "output": "",
            "type": "editor",
            "service_file": get_service_file(state),
            "cwd": state["current_working_directory"],
            "progress": get_progress(state),
        }

    if parts == ["systemctl", "daemon-reload"]:
        if not state["configuration_fixed"]:
            penalize(
                state,
                20,
            )

            return _response(
                (
                    "Nie można poprawnie przeładować jednostki. "
                    "ExecStart jest nieprawidłowy lub go brakuje."
                ),
                state,
                "warning",
            )

        state["daemon_reloaded"] = True

        return _response(
            "Konfiguracja systemd została przeładowana.",
            state,
            "success",
        )

    if _matches_service_command(
        parts,
        ["systemctl", "restart"],
    ):
        if not state["configuration_fixed"]:
            penalize(
                state,
                30,
            )

            return _response(
                (
                    "Job for ironvale-api.service failed. "
                    "Sprawdź status usługi i dziennik."
                ),
                state,
                "error",
            )

        if not state["daemon_reloaded"]:
            penalize(
                state,
                15,
            )

            return _response(
                (
                    "systemd nadal używa poprzedniej definicji jednostki. "
                    "Przeładuj konfigurację."
                ),
                state,
                "warning",
            )

        state["service_running"] = True

        return _response(
            "ironvale-api.service restarted successfully.",
            state,
            "success",
        )

    if parts == ["ss", "-tlnp"]:
        lines = [
            "State  Recv-Q Send-Q Local Address:Port",
            "LISTEN 0      511    0.0.0.0:80",
            "LISTEN 0      511    0.0.0.0:443",
        ]

        if state["service_running"]:
            lines.append(
                'LISTEN 0 2048 127.0.0.1:8100 '
                '0.0.0.0:* users:(("uvicorn",pid=2841))'
            )

        return _response(
            "\n".join(lines),
            state,
        )

    if parts in [
        ["reboot"],
        ["sudo", "reboot"],
    ]:
        penalize(
            state,
            100,
        )

        return _response(
            (
                "Operacja zablokowana przez politykę incydentu. "
                "Najpierw ustal przyczynę awarii."
            ),
            state,
            "error",
        )

    if command_name in {
        "curl",
        "journalctl",
        "ss",
        "systemctl",
    }:
        return _response(
            f"{command_name}: nieobsługiwana składnia; użyj help {command_name}",
            state,
            "warning",
        )

    return _response(
        f"shellforge-lab: polecenie niedostępne w tej misji: {command}",
        state,
        "warning",
    )


def save_service_file(content: str, state: dict) -> dict:
    state["filesystem"][SERVICE_FILE_PATH]["content"] = content
    state["daemon_reloaded"] = False

    exec_start_lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip().startswith("ExecStart=")
    ]
    expected_exec_start = f"ExecStart={CORRECT_EXEC_START}"
    configuration_fixed = exec_start_lines == [expected_exec_start]

    state["configuration_fixed"] = configuration_fixed

    if configuration_fixed:
        state["cause_identified"] = True
        message = (
            "Zmiany zostały zapisane. "
            "systemd nie przeładował jeszcze konfiguracji."
        )
    else:
        message = (
            "Zmiany zostały zapisane, ale ExecStart nadal jest "
            "nieprawidłowy lub go brakuje."
        )

    return {
        "success": True,
        "configuration_fixed": configuration_fixed,
        "message": message,
        "cwd": state["current_working_directory"],
        "progress": get_progress(state),
    }


def _help_response(
    arguments: list[str],
    state: dict,
) -> dict:
    if len(arguments) > 1:
        return _response(
            "help: zbyt wiele argumentów",
            state,
            "error",
        )

    topic = arguments[0] if arguments else None

    help_topics = {
        "cat": "cat <plik> [plik...] — wyświetla zawartość plików",
        "cd": "cd [ścieżka] — zmienia katalog; cd i cd ~ wracają do katalogu domowego",
        "curl": "curl <adres> — wykonuje symulowane zapytanie HTTP",
        "journalctl": "journalctl -u <usługa> — pokazuje dziennik wskazanej usługi",
        "ls": "ls [-la] [ścieżka] — wyświetla zawartość katalogu",
        "pwd": "pwd — pokazuje bieżący katalog roboczy",
        "ss": "ss -tlnp — pokazuje nasłuchujące porty i procesy",
        "systemctl": (
            "systemctl status <usługa>\n"
            "systemctl restart <usługa>\n"
            "systemctl daemon-reload\n"
            "Polecenia sprawdzają stan, restartują usługę lub przeładowują jednostki."
        ),
    }

    if topic:
        text = help_topics.get(topic)

        if text is None:
            return _response(
                f"help: brak pomocy dla polecenia '{topic}'",
                state,
                "warning",
            )

        return _response(
            text,
            state,
        )

    output = """Dostępne polecenia:

help [polecenie]        pomoc ogólna lub dla wybranego polecenia
pwd                     bieżący katalog roboczy
ls [-la] [ścieżka]      listowanie plików i katalogów
cd [ścieżka]            zmiana katalogu
cat <plik> [plik...]     odczyt plików
ticket                  treść zgłoszenia incydentu
status                  skrócony stan infrastruktury
curl <adres>            symulowane zapytanie HTTP
systemctl ...           obsługa usług systemd
journalctl ...           dziennik usług
ss ...                  informacje o portach
edit-service            edycja jednostki w edytorze gry
clear                   wyczyszczenie terminala

Użyj help <polecenie>, aby zobaczyć składnię."""

    return _response(
        output,
        state,
    )


def _change_directory(
    arguments: list[str],
    state: dict,
) -> dict:
    if len(arguments) > 1:
        return _response(
            "cd: zbyt wiele argumentów",
            state,
            "error",
        )

    requested_path = arguments[0] if arguments else HOME_DIRECTORY
    resolved_path = _resolve_path(
        requested_path,
        state,
    )
    node = state["filesystem"].get(resolved_path)

    if node is None:
        return _response(
            f"cd: {requested_path}: Nie ma takiego pliku ani katalogu",
            state,
            "error",
        )

    if node["type"] != "directory":
        return _response(
            f"cd: {requested_path}: Nie jest katalogiem",
            state,
            "error",
        )

    state["current_working_directory"] = resolved_path

    return _response(
        "",
        state,
    )


def _list_path(
    arguments: list[str],
    state: dict,
) -> dict:
    long_format = False
    show_all = False
    paths = []

    for argument in arguments:
        if argument.startswith("-") and argument != "-":
            flags = argument[1:]

            if not flags or any(flag not in {"a", "l"} for flag in flags):
                return _response(
                    f"ls: nieznana opcja '{argument}'",
                    state,
                    "error",
                )

            long_format = long_format or "l" in flags
            show_all = show_all or "a" in flags
        else:
            paths.append(argument)

    if len(paths) > 1:
        return _response(
            "ls: ta symulacja obsługuje jedną ścieżkę naraz",
            state,
            "error",
        )

    requested_path = paths[0] if paths else "."
    resolved_path = _resolve_path(
        requested_path,
        state,
    )
    filesystem = state["filesystem"]
    node = filesystem.get(resolved_path)

    if node is None:
        return _response(
            f"ls: nie można uzyskać dostępu do '{requested_path}': "
            "Nie ma takiego pliku ani katalogu",
            state,
            "error",
        )

    _mark_path_discovery(
        resolved_path,
        state,
    )

    if node["type"] == "file":
        entries = [
            (
                posixpath.basename(resolved_path),
                resolved_path,
                node,
            )
        ]
    else:
        entries = _directory_entries(
            resolved_path,
            state,
        )

        if not show_all:
            entries = [
                entry
                for entry in entries
                if not entry[0].startswith(".")
            ]

        if show_all:
            parent_path = _parent_path(resolved_path)
            entries = [
                (".", resolved_path, node),
                ("..", parent_path, filesystem[parent_path]),
                *entries,
            ]

    if not long_format:
        return _response(
            "  ".join(entry[0] for entry in entries),
            state,
        )

    lines = []

    if node["type"] == "directory":
        lines.append(f"total {_directory_total(entries)}")

    lines.extend(
        _format_long_entry(name, entry_node)
        for name, _, entry_node in entries
    )

    return _response(
        "\n".join(lines),
        state,
    )


def _read_files(
    arguments: list[str],
    state: dict,
) -> dict:
    if not arguments:
        return _response(
            "cat: brak argumentu z nazwą pliku",
            state,
            "error",
        )

    outputs = []
    has_error = False

    for requested_path in arguments:
        resolved_path = _resolve_path(
            requested_path,
            state,
        )
        node = state["filesystem"].get(resolved_path)

        if node is None:
            outputs.append(
                f"cat: {requested_path}: Nie ma takiego pliku ani katalogu"
            )
            has_error = True
            continue

        if node["type"] == "directory":
            outputs.append(
                f"cat: {requested_path}: Jest katalogiem"
            )
            has_error = True
            continue

        _mark_path_discovery(
            resolved_path,
            state,
        )
        outputs.append(node["content"].rstrip("\n"))

    return _response(
        "\n".join(outputs),
        state,
        "error" if has_error else "normal",
    )


def _resolve_path(
    requested_path: str,
    state: dict,
) -> str:
    if requested_path == "~":
        candidate = HOME_DIRECTORY
    elif requested_path.startswith("~/"):
        candidate = posixpath.join(
            HOME_DIRECTORY,
            requested_path[2:],
        )
    elif requested_path.startswith("/"):
        candidate = requested_path
    else:
        candidate = posixpath.join(
            state["current_working_directory"],
            requested_path,
        )

    normalized = posixpath.normpath(candidate)

    return "/" + normalized.lstrip("/")


def _directory_entries(
    directory_path: str,
    state: dict,
) -> list[tuple[str, str, dict]]:
    entries = []

    for path, node in state["filesystem"].items():
        if path == directory_path:
            continue

        if _parent_path(path) == directory_path:
            entries.append(
                (
                    posixpath.basename(path),
                    path,
                    node,
                )
            )

    return sorted(
        entries,
        key=lambda entry: entry[0],
    )


def _parent_path(path: str) -> str:
    if path == "/":
        return "/"

    return posixpath.dirname(path) or "/"


def _directory_total(entries: list[tuple[str, str, dict]]) -> int:
    return sum(
        4
        for name, _, node in entries
        if name not in {".", ".."} and node["type"] == "directory"
    )


def _format_long_entry(
    name: str,
    node: dict,
) -> str:
    size = 4096 if node["type"] == "directory" else len(
        node["content"].encode("utf-8")
    )

    return (
        f"{node['mode']} 1 {node['owner']:<8} {node['group']:<8} "
        f"{size:>5} sie  7 20:15 {name}"
    )


def _mark_path_discovery(
    path: str,
    state: dict,
) -> None:
    filesystem = state["filesystem"]

    if path == SERVICE_FILE_PATH:
        state["service_file_inspected"] = True

    if path in {
        CORRECT_UVICORN_PATH,
        posixpath.dirname(CORRECT_UVICORN_PATH),
    } and CORRECT_UVICORN_PATH in filesystem:
        state["correct_binary_found"] = True

    if path in {
        BROKEN_UVICORN_PATH,
        posixpath.dirname(BROKEN_UVICORN_PATH),
    } and BROKEN_UVICORN_PATH not in filesystem:
        state["broken_binary_checked"] = True

    if state["service_file_inspected"] and state["correct_binary_found"]:
        state["cause_identified"] = True


def _matches_service_command(
    parts: list[str],
    prefix: list[str],
) -> bool:
    return (
        parts[: len(prefix)] == prefix
        and len(parts) == len(prefix) + 1
        and parts[-1] in {
            "ironvale-api",
            "ironvale-api.service",
        }
    )


def _response(
    output: str,
    state: dict,
    response_type: str = "normal",
) -> dict:
    return {
        "output": output,
        "type": response_type,
        "cwd": state["current_working_directory"],
        "progress": get_progress(state),
    }
