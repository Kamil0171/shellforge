from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def run_step(label: str, command: list[str]) -> bool:
    print(f"\n==> {label}", flush=True)

    try:
        completed = subprocess.run(command, cwd=REPOSITORY_ROOT, check=False)
    except FileNotFoundError:
        print(f"BŁĄD: nie znaleziono programu: {command[0]}", file=sys.stderr)
        return False

    if completed.returncode != 0:
        print(f"BŁĄD: etap zakończył się kodem {completed.returncode}.", file=sys.stderr)
        return False

    print("OK", flush=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Lokalny quality gate ShellForge.")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Uruchom tylko szybki podzbiór testów pytest.",
    )
    args = parser.parse_args()

    pytest_command = [sys.executable, "-m", "pytest"]

    if args.fast:
        pytest_command.extend(
            [
                "tests/test_basic.py",
                "tests/test_admin_duty_dynamic_pages.py",
                "-q",
            ]
        )

    steps = (
        ("Ruff", [sys.executable, "-m", "ruff", "check", "."]),
        ("pytest", pytest_command),
        ("Składnia wszystkich Dynamic Incident JS", [sys.executable, "scripts/check_dynamic_js.py"]),
        ("Whitespace i konflikty diff", ["git", "diff", "--check"]),
    )

    for label, command in steps:
        if not run_step(label, command):
            return 1

    print("\nWszystkie lokalne kontrole zakończone pomyślnie.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
