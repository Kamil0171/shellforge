import pytest
from pydantic import ValidationError

from app.admin_duty.dynamic_command_parser import (
    MAX_DYNAMIC_COMMAND_LENGTH,
    SYSTEMCTL_COMMANDS,
    CommandParseError,
    parse_dynamic_command,
)
from app.admin_duty.dynamic_command_registry import DynamicCommandRequest


@pytest.mark.parametrize(
    ("command", "command_id"),
    [
        ("systemctl status service-api", "systemd.status"),
        ("systemctl restart service-api", "systemd.restart"),
        ("systemctl cat service-api", "systemd.cat"),
        ("systemctl   status   service-api", "systemd.status"),
        ("  systemctl restart service-api  ", "systemd.restart"),
        ('systemctl status "service-api"', "systemd.status"),
    ],
)
def test_parse_supported_systemctl_command(command, command_id):
    request = parse_dynamic_command(command)

    assert request == DynamicCommandRequest(
        command_id=command_id,
        resource_id="service-api",
    )


@pytest.mark.parametrize("command", ["", " ", "\t\r\n"])
def test_empty_command_is_rejected(command):
    with pytest.raises(CommandParseError, match="nie może być pusta"):
        parse_dynamic_command(command)


@pytest.mark.parametrize(
    "command",
    [
        "systemctl",
        "systemctl restart",
        "systemctl status service-api extra",
    ],
)
def test_systemctl_command_rejects_wrong_argument_count(command):
    with pytest.raises(CommandParseError, match="liczbę argumentów"):
        parse_dynamic_command(command)


@pytest.mark.parametrize(
    "command",
    [
        "service status service-api",
        "wget status service-api",
        "SYSTEMCTL status service-api",
    ],
)
def test_unknown_or_wrong_case_program_is_rejected(command):
    with pytest.raises(CommandParseError, match="Nieobsługiwany program"):
        parse_dynamic_command(command)


@pytest.mark.parametrize(
    "command",
    [
        "systemctl STATUS service-api",
        "systemctl RESTART service-api",
    ],
)
def test_unknown_or_wrong_case_subcommand_is_rejected(command):
    with pytest.raises(CommandParseError, match="Nieobsługiwana podkomenda"):
        parse_dynamic_command(command)


@pytest.mark.parametrize(
    "command",
    [
        "systemctl status invalid/resource",
        "systemctl status 'resource with spaces'",
        "systemctl status _private-resource",
    ],
)
def test_invalid_resource_identifier_is_wrapped(command):
    with pytest.raises(CommandParseError) as error:
        parse_dynamic_command(command)

    assert "identyfikator" in str(error.value)


def test_non_string_command_is_rejected():
    with pytest.raises(CommandParseError, match="musi być tekstem"):
        parse_dynamic_command(None)


def test_command_over_length_limit_is_rejected():
    command = "systemctl status " + "a" * MAX_DYNAMIC_COMMAND_LENGTH

    with pytest.raises(CommandParseError, match="zbyt długa"):
        parse_dynamic_command(command)


def test_invalid_quoting_preserves_shlex_error():
    with pytest.raises(CommandParseError) as error:
        parse_dynamic_command('systemctl status "service-api')

    assert isinstance(error.value.__cause__, ValueError)


@pytest.mark.parametrize(
    "command",
    [
        "systemctl status service-api && rm -rf /",
        "systemctl status service-api || echo failed",
        "systemctl status service-api | cat",
        "systemctl status service-api; rm -rf /",
        "systemctl status service-api > output",
        "systemctl status $(whoami)",
    ],
)
def test_shell_syntax_is_rejected(command):
    with pytest.raises(CommandParseError):
        parse_dynamic_command(command)


def test_systemctl_mapping_contains_exactly_supported_commands_and_is_immutable():
    assert dict(SYSTEMCTL_COMMANDS) == {
        "status": "systemd.status",
        "restart": "systemd.restart",
        "start": "systemd.start",
        "stop": "systemd.stop",
        "cat": "systemd.cat",
        **{
            action: f"systemd.{action}"
            for action in (
                "enable",
                "disable",
                "is-active",
                "is-enabled",
                "list-units",
                "daemon-reload",
            )
        },
    }

    with pytest.raises(TypeError):
        SYSTEMCTL_COMMANDS["stop"] = "systemd.stop"


def test_parsed_request_is_frozen_and_round_trips_json():
    request = parse_dynamic_command("systemctl status service-api")
    restored = DynamicCommandRequest.model_validate_json(request.model_dump_json())

    assert restored == request

    with pytest.raises(ValidationError):
        request.resource_id = "other-service"


@pytest.mark.parametrize(
    ("command", "command_id", "resource_id", "arguments"),
    [
        (
            "nano /etc/systemd/system/example.service",
            "filesystem.edit",
            "/etc/systemd/system/example.service",
            (),
        ),
        ("systemctl daemon-reload", "systemd.daemon-reload", ".", ()),
        ("stat /opt/example/api", "filesystem.path-stat", "/opt/example/api", ()),
        (
            "chmod 755 /opt/example/api",
            "filesystem.chmod",
            "/opt/example/api",
            ("0755",),
        ),
    ],
)
def test_parse_all_content_engine_grammars(command, command_id, resource_id, arguments):
    assert parse_dynamic_command(command) == DynamicCommandRequest(
        command_id=command_id,
        resource_id=resource_id,
        arguments=arguments,
    )


@pytest.mark.parametrize(
    "command",
    [
        "env",
        "env inspect",
        "env restore service-api",
        "stat",
        "stat file-api extra",
        "chmod file-api",
        "chmod 0999 file-api",
        "systemctl set-exec-start service-api invalid/target",
        "env restore service-api $DATABASE_URL",
    ],
)
def test_extended_grammar_rejects_invalid_or_uncontrolled_commands(command):
    with pytest.raises(CommandParseError):
        parse_dynamic_command(command)
