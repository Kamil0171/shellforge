import re
import shlex
from types import MappingProxyType

from pydantic import ValidationError

from app.admin_duty.dynamic_command_registry import DynamicCommandRequest

MAX_DYNAMIC_COMMAND_LENGTH = 1024
SYSTEMCTL_COMMANDS = MappingProxyType(
    {
        "status": "systemd.status",
        "restart": "systemd.restart",
        "start": "systemd.start",
        "stop": "systemd.stop",
        "cat": "systemd.cat",
        "set-exec-start": "systemd.set-exec-start",
    }
)
ENV_COMMANDS = MappingProxyType(
    {"inspect": "environment.inspect", "restore": "environment.restore"}
)
SIMPLE_COMMANDS = MappingProxyType(
    {
        "pwd": "shell.pwd",
        "hostname": "system.hostname",
        "uptime": "system.uptime",
        "whoami": "system.whoami",
        "id": "system.id",
    }
)


class CommandParseError(ValueError):
    pass


IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")


def _identifier(value: str) -> str:
    if not IDENTIFIER_PATTERN.fullmatch(value):
        raise CommandParseError("Komenda zawiera nieprawidłowy identyfikator lub argument.")
    return value


def _request(command_id: str, resource_id: str = ".", arguments=()):
    try:
        return DynamicCommandRequest(
            command_id=command_id,
            resource_id=resource_id,
            arguments=tuple(arguments),
        )
    except ValidationError as error:
        raise CommandParseError("Komenda zawiera nieprawidłowy argument.") from error


def _require(tokens: list[str], lengths: set[int], message: str) -> None:
    if len(tokens) not in lengths:
        raise CommandParseError(message)


def parse_dynamic_command(command: str) -> DynamicCommandRequest:
    if not isinstance(command, str):
        raise CommandParseError("Komenda musi być tekstem.")
    if len(command) > MAX_DYNAMIC_COMMAND_LENGTH:
        raise CommandParseError("Komenda jest zbyt długa.")
    if not command.strip():
        raise CommandParseError("Komenda nie może być pusta.")
    try:
        tokens = shlex.split(command)
    except ValueError as error:
        raise CommandParseError("Komenda zawiera nieprawidłowe cytowanie.") from error

    program = tokens[0]
    if program in SIMPLE_COMMANDS:
        _require(tokens, {1}, f"Komenda {program} nie przyjmuje argumentów.")
        return _request(SIMPLE_COMMANDS[program])
    if program == "cd":
        _require(tokens, {1, 2}, "Komenda cd przyjmuje najwyżej jedną ścieżkę.")
        return _request("shell.cd", tokens[1] if len(tokens) == 2 else "~")
    if program == "ls":
        options = [token for token in tokens[1:] if token.startswith("-")]
        paths = [token for token in tokens[1:] if not token.startswith("-")]
        valid_options = {"-l", "-a", "-la", "-al"}
        if any(option not in valid_options for option in options) or len(paths) > 1:
            raise CommandParseError(
                "Obsługiwane warianty ls to: ls, ls -l, ls -la [ścieżka]."
            )
        return _request("filesystem.list", paths[0] if paths else ".", options)
    if program in {"cat", "stat"}:
        _require(tokens, {2}, f"Komenda {program} wymaga jednej ścieżki.")
        command_id = "filesystem.read"
        if program == "stat":
            command_id = (
                "filesystem.stat"
                if tokens[1].startswith("file-") and "/" not in tokens[1]
                else "filesystem.path-stat"
            )
        return _request(command_id, tokens[1])
    if program in {"head", "tail"}:
        if len(tokens) == 2:
            return _request(f"filesystem.{program}", tokens[1])
        if (
            len(tokens) == 4
            and tokens[1] == "-n"
            and tokens[2].isdigit()
            and 1 <= int(tokens[2]) <= 100
        ):
            return _request(f"filesystem.{program}", tokens[3], (tokens[2],))
        raise CommandParseError(f"Obsługiwana składnia: {program} [-n N] <plik>.")
    if program == "grep":
        _require(tokens, {3}, "Obsługiwana składnia: grep <wzorzec> <plik>.")
        return _request("filesystem.grep", tokens[2], (tokens[1],))
    if program == "uname":
        _require(tokens, {1, 2}, "Obsługiwana składnia: uname lub uname -a.")
        if len(tokens) == 2 and tokens[1] != "-a":
            raise CommandParseError("Obsługiwana składnia: uname lub uname -a.")
        return _request("system.uname", arguments=tokens[1:])
    if program in {"free", "df"}:
        _require(tokens, {2}, f"Obsługiwana składnia: {program} -h.")
        if tokens[1] != "-h":
            raise CommandParseError(f"Obsługiwana składnia: {program} -h.")
        command_id = "resources.memory" if program == "free" else "resources.disk"
        return _request(command_id, arguments=("-h",))
    if program == "ip":
        _require(tokens, {2}, "Obsługiwana składnia: ip addr lub ip route.")
        if tokens[1] not in {"addr", "route"}:
            raise CommandParseError("Obsługiwana składnia: ip addr lub ip route.")
        return _request(f"network.{tokens[1]}")
    if program == "ss":
        _require(tokens, {2}, "Obsługiwana składnia: ss -lntp.")
        if tokens[1] != "-lntp":
            raise CommandParseError("Obsługiwana składnia: ss -lntp.")
        return _request("network.listeners", arguments=(tokens[1],))
    if program == "journalctl":
        if len(tokens) == 3 and tokens[1] == "-u":
            return _request("journal.read", tokens[2])
        if len(tokens) == 2 and tokens[1] == "-xe":
            return _request("journal.xe")
        raise CommandParseError(
            "Obsługiwana składnia: journalctl -u <usługa> lub journalctl -xe."
        )
    if program == "systemctl":
        if len(tokens) not in {3, 4}:
            raise CommandParseError(
                "Komenda systemctl ma nieprawidłową liczbę argumentów."
            )
        command_id = SYSTEMCTL_COMMANDS.get(tokens[1])
        if command_id is None:
            raise CommandParseError(
                f"Nieobsługiwana podkomenda systemctl: {tokens[1]}."
            )
        expected = 4 if tokens[1] == "set-exec-start" else 3
        _require(
            tokens,
            {expected},
            "Komenda systemctl ma nieprawidłową liczbę argumentów.",
        )
        return _request(
            command_id,
            _identifier(tokens[2]),
            tuple(_identifier(argument) for argument in tokens[3:]),
        )
    if program == "env":
        if len(tokens) not in {3, 4}:
            raise CommandParseError(
                "Komenda env ma nieprawidłową liczbę argumentów."
            )
        command_id = ENV_COMMANDS.get(tokens[1])
        expected = 4 if tokens[1] == "restore" else 3
        if command_id is None or len(tokens) != expected:
            raise CommandParseError("Komenda env ma nieprawidłową składnię.")
        return _request(
            command_id,
            _identifier(tokens[2]),
            tuple(_identifier(argument) for argument in tokens[3:]),
        )
    if program == "chmod":
        if len(tokens) != 3 or tokens[1] != "restore":
            raise CommandParseError(
                "Obsługiwana składnia to: chmod restore <file-resource>."
            )
        return _request("filesystem.restore-permissions", _identifier(tokens[2]))
    raise CommandParseError(f"Nieobsługiwany program: {program}.")
