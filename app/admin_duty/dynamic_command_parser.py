import re
import shlex
from types import MappingProxyType

from pydantic import ValidationError

from app.admin_duty.dynamic_command_registry import DynamicCommandRequest

MAX_DYNAMIC_COMMAND_LENGTH = 1024
SYSTEMCTL_COMMANDS = MappingProxyType(
    {
        action: f"systemd.{action}"
        for action in (
            "status",
            "restart",
            "start",
            "stop",
            "cat",
            "enable",
            "disable",
            "is-active",
            "is-enabled",
            "list-units",
            "daemon-reload",
        )
    }
)


class CommandParseError(ValueError):
    pass


def _request(command_id, resource_id=".", arguments=()):
    try:
        return DynamicCommandRequest(
            command_id=command_id, resource_id=resource_id, arguments=tuple(arguments)
        )
    except ValidationError as error:
        raise CommandParseError("Nieprawidłowe argumenty polecenia.") from error


def require(condition, syntax):
    if not condition:
        raise CommandParseError(
            f"Sprawdź liczbę argumentów i flagi. Obsługiwana składnia: {syntax}."
        )


def filesystem(program, args):
    if program == "pwd":
        require(not args, "pwd")
        return _request("shell.pwd")
    if program == "cd":
        require(len(args) <= 1, "cd [ścieżka]")
        return _request("shell.cd", args[0] if args else "~")
    flags = [item for item in args if item.startswith("-")]
    paths = [item for item in args if not item.startswith("-")]
    simple = {
        "cat": "read",
        "stat": "path-stat",
        "touch": "touch",
        "rmdir": "rmdir",
        "nano": "edit",
    }
    if program in simple:
        require(len(args) == 1, f"{program} <ścieżka>")
        return _request(
            simple[program]
            if "." in simple[program]
            else f"filesystem.{simple[program]}",
            args[0],
        )
    if program in {"cp", "mv"}:
        require(len(args) == 2 and not flags, f"{program} <źródło> <cel>")
        return _request(
            "filesystem.copy" if program == "cp" else "filesystem.move",
            args[0],
            args[1:],
        )
    if program in {"chmod", "chown"}:
        require(len(args) == 2, f"{program} <tryb/właściciel> <plik>")
        if program == "chmod":
            require(
                bool(re.fullmatch(r"0?[0-7]{3}", args[0])),
                "chmod <tryb ósemkowy, np. 755> <plik>",
            )
            value = args[0].zfill(4)
        else:
            require(
                bool(
                    re.fullmatch(r"[a-z_][a-z0-9_-]*(?::[a-z_][a-z0-9_-]*)?", args[0])
                ),
                "chown użytkownik[:grupa] <plik>",
            )
            value = args[0]
        return _request(f"filesystem.{program}", args[1], (value,))
    if program in {"head", "tail"}:
        require(
            len(args) == 1
            or (
                len(args) == 3
                and args[0] == "-n"
                and args[1].isdigit()
                and 1 <= int(args[1]) <= 100
            ),
            f"{program} [-n N] <plik>",
        )
        return _request(
            f"filesystem.{program}", args[-1], (args[1],) if len(args) == 3 else ()
        )
    if program == "grep":
        require(len(args) == 2, "grep <wzorzec> <plik>")
        return _request("filesystem.grep", args[1], (args[0],))
    if program == "find":
        require(
            len(args) <= 1 or (len(args) == 3 and args[1] == "-name"),
            "find [ścieżka] [-name wzorzec]",
        )
        return _request(
            "filesystem.find",
            args[0] if args else ".",
            (args[2],) if len(args) == 3 else (),
        )
    allowed = {
        "ls": {"-a", "-l", "-la", "-al"},
        "mkdir": {"-p"},
        "rm": {"-r", "-R"},
        "du": {"-h", "-s", "-sh", "-hs"},
    }
    require(
        set(flags) <= allowed[program]
        and len(paths) <= 1
        and (paths or program in {"ls", "du"}),
        f"{program} [flagi] <ścieżka>",
    )
    if program == "du" and any("h" in flag for flag in flags):
        flags = ["-h"]
    capability = {"ls": "list", "rm": "remove"}.get(program, program)
    return _request(f"filesystem.{capability}", paths[0] if paths else ".", flags)


def system(program, args):
    if program == "systemctl":
        require(bool(args), "systemctl <akcja> [jednostka]")
        if args[0] not in SYSTEMCTL_COMMANDS:
            raise CommandParseError("Nieobsługiwana podkomenda systemctl.")
        action = args[0]
        if action in {"daemon-reload", "list-units"}:
            require(len(args) == 1, f"systemctl {action}")
        elif action == "status":
            require(len(args) in {1, 2}, "systemctl status [jednostka]")
        else:
            require(len(args) == 2, f"systemctl {action} <jednostka>")
        if len(args) > 1 and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:@-]*", args[1]):
            raise CommandParseError("Nieprawidłowy identyfikator jednostki.")
        return _request(
            SYSTEMCTL_COMMANDS[action], args[1] if len(args) > 1 else ".", args[2:]
        )
    if program == "journalctl":
        unit, index = ".", 0
        extra = []
        while index < len(args):
            flag = args[index]
            if flag == "-xe":
                index += 1
                continue
            require(
                flag in {"-u", "-n", "--since"} and index + 1 < len(args),
                "journalctl [-u jednostka] [-n N] [--since data] [-xe]",
            )
            value = args[index + 1]
            if flag == "-u":
                unit = value
            else:
                require(
                    flag != "-n" or (value.isdigit() and 1 <= int(value) <= 100),
                    "journalctl -n 1..100",
                )
                extra.extend((flag, value))
            index += 2
        return _request("journal.read", unit, extra)
    flags = {"uname": {"-a"}, "ps": {"aux", "-ef"}, "free": {"-h"}, "df": {"-h"}}
    require(
        not args or (program in flags and len(args) == 1 and args[0] in flags[program]),
        f"{program} [obsługiwana flaga]",
    )
    ids = {"ps": "processes.list", "free": "resources.memory", "df": "resources.disk"}
    return _request(ids.get(program, f"system.{program}"), arguments=args)


def network(program, args):
    if program == "ip":
        require(
            len(args) == 1 and args[0] in {"addr", "link", "route"},
            "ip addr|link|route",
        )
        return _request(f"network.{args[0]}")
    if program == "ss":
        require(not args or args == ["-lntp"], "ss [-lntp]")
        return _request("network.listeners")
    if program == "nmcli":
        require(
            args in (["device", "status"], ["connection", "show"])
            or (
                len(args) == 3 and args[0] == "connection" and args[1] in {"up", "down"}
            ),
            "nmcli device status | connection show|up|down [nazwa]",
        )
        return _request("networkmanager.command", arguments=args)
    if program == "getent":
        require(len(args) == 2 and args[0] == "hosts", "getent hosts <nazwa>")
        args = args[1:]
    if program == "ping" and len(args) == 3:
        require(args[:2] == ["-c", "1"], "ping [-c 1] <host>")
        args = args[2:]
    if program == "curl" and len(args) == 2:
        require(args[0] in {"-I", "-i"}, "curl [-I|-i] <URL>")
        args = args[1:]
    require(len(args) == 1, f"{program} <host/URL>")
    return _request(f"network.{program}", args[0])


def packages(program, args):
    if program == "rpm":
        require(
            args == ["-qa"] or (len(args) == 2 and args[0] in {"-q", "-qi"}),
            "rpm -qa | -q|-qi pakiet",
        )
        return _request("packages.rpm", args[1] if len(args) == 2 else ".", args[:1])
    args = [item for item in args if item != "-y"]
    require(bool(args), f"{program} install|remove|update|info|list|repolist|clean")
    action = args[0]
    valid = action in {"install", "remove", "info"} and len(args) == 2
    valid |= action == "update" and len(args) <= 2
    valid |= args in (["list"], ["list", "installed"], ["repolist"], ["clean", "all"])
    require(
        valid,
        f"{program} install|remove|info <pakiet> | update [pakiet] | list [installed] | repolist | clean all",
    )
    return _request("packages.command", arguments=args)


def security(program, args):
    if program == "firewall-cmd":
        selected = [item for item in args if item != "--permanent"]
        require(
            len(selected) == 1 and len(args) <= 2, "firewall-cmd [--permanent] <opcja>"
        )
        option = selected[0]
        require(
            option
            in {
                "--state",
                "--get-active-zones",
                "--list-all",
                "--list-services",
                "--list-ports",
                "--reload",
            }
            or bool(re.fullmatch(r"--(?:add|remove)-(?:service|port)=.+", option)),
            "firewall-cmd --list-all|--add-service=...|--add-port=...",
        )
        return _request("firewalld.command", arguments=args)
    if program in {"getenforce", "sestatus"}:
        require(not args, program)
    elif program == "setenforce":
        require(
            len(args) == 1 and args[0].lower() in {"0", "1", "enforcing", "permissive"},
            "setenforce 0|1",
        )
    elif program == "restorecon":
        require(
            len(args) == 1 or (len(args) == 2 and args[0] == "-R"),
            "restorecon [-R] <ścieżka>",
        )
    else:
        require(args == ["fcontext", "-l"], "semanage fcontext -l")
    return _request(f"selinux.{program}", args[-1] if args else ".", args)


PARSERS = {
    **dict.fromkeys(
        (
            "pwd",
            "cd",
            "ls",
            "cat",
            "head",
            "tail",
            "grep",
            "stat",
            "find",
            "mkdir",
            "touch",
            "cp",
            "mv",
            "rm",
            "rmdir",
            "chmod",
            "chown",
            "du",
            "nano",
        ),
        filesystem,
    ),
    **dict.fromkeys(
        (
            "hostname",
            "hostnamectl",
            "uname",
            "uptime",
            "whoami",
            "id",
            "date",
            "ps",
            "free",
            "df",
            "systemctl",
            "journalctl",
        ),
        system,
    ),
    **dict.fromkeys(("ip", "ss", "ping", "curl", "getent", "dig", "nmcli"), network),
    **dict.fromkeys(("dnf", "yum", "rpm"), packages),
    **dict.fromkeys(
        (
            "getenforce",
            "sestatus",
            "setenforce",
            "restorecon",
            "semanage",
            "firewall-cmd",
        ),
        security,
    ),
}


def parse_dynamic_command(command):
    if not isinstance(command, str):
        raise CommandParseError("Komenda musi być tekstem.")
    if not command.strip():
        raise CommandParseError("Komenda nie może być pusta.")
    if len(command) > MAX_DYNAMIC_COMMAND_LENGTH:
        raise CommandParseError("Komenda jest zbyt długa.")
    quote = None
    escaped = False
    for char in command:
        if escaped:
            escaped = False
            continue
        if char == "\\" and quote != "'":
            escaped = True
        elif char == quote:
            quote = None
        elif char in "\"'" and quote is None:
            quote = char
        elif quote is None and char in "|&;<>()\n\r":
            raise CommandParseError(
                "Operator powłoki nie jest jeszcze obsługiwany (Shell operator not supported yet)."
            )
    if "`" in command or "$(" in command:
        raise CommandParseError(
            "Operator powłoki nie jest jeszcze obsługiwany (Shell operator not supported yet)."
        )
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars="|&;<>()")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError as error:
        raise CommandParseError("Nieprawidłowe cytowanie.") from error
    if not tokens or tokens[0] not in PARSERS:
        raise CommandParseError(
            f"Nieobsługiwany program: {tokens[0] if tokens else ''}."
        )
    return PARSERS[tokens[0]](tokens[0], tokens[1:])
