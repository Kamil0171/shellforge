import shlex
from types import MappingProxyType

from pydantic import ValidationError

from app.admin_duty.dynamic_command_registry import DynamicCommandRequest

MAX_DYNAMIC_COMMAND_LENGTH = 1024
SYSTEMCTL_COMMANDS = MappingProxyType(
    {
        "status": "systemd.status",
        "restart": "systemd.restart",
        "cat": "systemd.cat",
        "set-exec-start": "systemd.set-exec-start",
    }
)
ENV_COMMANDS = MappingProxyType(
    {
        "inspect": "environment.inspect",
        "restore": "environment.restore",
    }
)


class CommandParseError(ValueError):
    pass


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

    if program == "systemctl":
        if len(tokens) not in {3, 4}:
            raise CommandParseError(
                "Komenda systemctl ma nieprawidłową liczbę argumentów."
            )

        subcommand = tokens[1]
        command_id = SYSTEMCTL_COMMANDS.get(subcommand)
        expected_length = 4 if subcommand == "set-exec-start" else 3

        if command_id is None:
            raise CommandParseError(
                f"Nieobsługiwana podkomenda systemctl: {subcommand}."
            )

        if len(tokens) != expected_length:
            raise CommandParseError(
                "Komenda systemctl ma nieprawidłową liczbę argumentów."
            )

        resource_id = tokens[2]
        arguments = tuple(tokens[3:])
    elif program == "env":
        if len(tokens) not in {3, 4}:
            raise CommandParseError("Komenda env ma nieprawidłową liczbę argumentów.")

        subcommand = tokens[1]
        command_id = ENV_COMMANDS.get(subcommand)
        expected_length = 4 if subcommand == "restore" else 3

        if command_id is None:
            raise CommandParseError(f"Nieobsługiwana podkomenda env: {subcommand}.")

        if len(tokens) != expected_length:
            raise CommandParseError("Komenda env ma nieprawidłową liczbę argumentów.")

        resource_id = tokens[2]
        arguments = tuple(tokens[3:])
    elif program == "stat":
        if len(tokens) != 2:
            raise CommandParseError("Komenda stat wymaga identyfikatora zasobu.")

        command_id = "filesystem.stat"
        resource_id = tokens[1]
        arguments = ()
    elif program == "chmod":
        if len(tokens) != 3 or tokens[1] != "restore":
            raise CommandParseError(
                "Obsługiwana składnia to: chmod restore <file-resource>."
            )

        command_id = "filesystem.restore-permissions"
        resource_id = tokens[2]
        arguments = ()
    else:
        raise CommandParseError(f"Nieobsługiwany program: {program}.")

    try:
        return DynamicCommandRequest(
            command_id=command_id,
            resource_id=resource_id,
            arguments=arguments,
        )
    except ValidationError as error:
        raise CommandParseError(
            "Komenda zawiera nieprawidłowy identyfikator lub argument."
        ) from error
