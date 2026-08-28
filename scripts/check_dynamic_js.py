from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
JS_DIRECTORY = REPOSITORY_ROOT / "app" / "static" / "admin_duty" / "dynamic"


def main() -> int:
    node_override = os.getenv("SHELLFORGE_NODE")
    node = node_override if node_override and Path(node_override).is_file() else None
    node = node or shutil.which("node")

    if node is None:
        print("BŁĄD: Node.js nie jest dostępny.", file=sys.stderr)
        return 1

    files = sorted(JS_DIRECTORY.glob("*.js"))
    if not files:
        print("BŁĄD: nie znaleziono plików Dynamic Incident JS.", file=sys.stderr)
        return 1

    for path in files:
        relative = path.relative_to(REPOSITORY_ROOT)
        completed = subprocess.run(
            [node, "--check", str(relative)],
            cwd=REPOSITORY_ROOT,
            check=False,
        )
        if completed.returncode != 0:
            return completed.returncode
        print(f"OK  {relative.as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
