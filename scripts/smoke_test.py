from __future__ import annotations

import argparse
import json
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


class SmokeFailure(RuntimeError):
    pass


def request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    outgoing = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(outgoing, timeout=10) as response:
            content = response.read()
            content_type = response.headers.get_content_type()
            parsed = json.loads(content) if content_type == "application/json" else content
            return response.status, parsed
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise SmokeFailure(f"{method} {path}: HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise SmokeFailure(f"{method} {path}: brak połączenia: {error.reason}") from error


def expect_ok(base_url: str, path: str) -> None:
    status, _ = request(base_url, path)

    if status != 200:
        raise SmokeFailure(f"GET {path}: oczekiwano 200, otrzymano {status}")

    print(f"OK  GET  {path}")


def run_dynamic_flow(base_url: str) -> None:
    status, started = request(
        base_url,
        "/admin-duty/dynamic/api/start",
        method="POST",
        payload={"difficulty": "easy", "seed": 1},
    )

    if status != 200 or not isinstance(started, dict):
        raise SmokeFailure("POST start nie zwrócił poprawnej sesji.")

    session_id = started["session_id"]
    game_map = started.get("game_map", {})
    interactions = game_map.get("interactions", [])
    interaction_types = {interaction.get("type") for interaction in interactions}

    if game_map.get("theme") != "modern-noc":
        raise SmokeFailure("Start sesji nie zwrócił mapy Modern NOC.")

    if interaction_types != {"terminal", "monitoring", "rack", "support"}:
        raise SmokeFailure("Publiczna mapa nie zawiera wymaganych interakcji.")

    if not started.get("monitoring", {}).get("signals"):
        raise SmokeFailure("Start sesji nie zwrócił sygnałów monitoringu.")

    if not started.get("support_center", {}).get("runbooks"):
        raise SmokeFailure("Start sesji nie zwrócił runbooków Support Bay.")

    if started.get("shell", {}).get("current_working_directory") != "/home/operator":
        raise SmokeFailure("Virtual Rocky shell nie wystartował w katalogu operatora.")

    service_nodes = [
        node
        for node in started["infrastructure"]["nodes"]
        if node["type"] == "service"
    ]

    if not service_nodes:
        raise SmokeFailure("Publiczna mapa nie zawiera węzła usługi.")

    print("OK  POST /admin-duty/dynamic/api/start")
    expect_ok(base_url, f"/admin-duty/dynamic/api/sessions/{session_id}")
    shell_commands = (
        ("pwd", "/home/operator"),
        ("cd /etc/systemd/system", ""),
        ("ls -la", ".service"),
        (f"systemctl status {service_nodes[0]['id']}", "Loaded: loaded"),
        (f"journalctl -u {service_nodes[0]['id']}", "systemd[1]"),
    )
    for shell_command, expected_output in shell_commands:
        status, command = request(
            base_url,
            "/admin-duty/dynamic/api/command",
            method="POST",
            payload={"session_id": session_id, "command": shell_command},
        )
        if (
            status != 200
            or not isinstance(command, dict)
            or expected_output not in command.get("output", "")
        ):
            raise SmokeFailure(
                f"Virtual shell nie obsłużył poprawnie: {shell_command}."
            )
        print(f"OK  SHELL {shell_command}")
    status, ended = request(
        base_url,
        "/admin-duty/dynamic/api/end",
        method="POST",
        payload={"session_id": session_id},
    )

    if status != 200 or ended.get("progress", {}).get("status") != "ended":
        raise SmokeFailure("POST end nie zakończył sesji.")

    print("OK  POST /admin-duty/dynamic/api/end")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test lokalnego ShellForge.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    try:
        for path in ("/health", "/", "/admin-duty/", "/admin-duty/dynamic/"):
            expect_ok(args.base_url, path)

        run_dynamic_flow(args.base_url)
    except (SmokeFailure, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"BŁĄD: {error}", file=sys.stderr)
        return 1

    print("\nSmoke test zakończony pomyślnie.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
