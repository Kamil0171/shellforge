import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import SecretStr

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "shellforge.db"

APP_NAME = os.getenv("APP_NAME", "ShellForge")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_DESCRIPTION = os.getenv(
    "APP_DESCRIPTION",
    "Edukacyjna aplikacja webowa do nauki Linuxa i DevOps.",
)

APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")


@dataclass(frozen=True, slots=True)
class IncidentAISettings:
    enabled: bool = False
    provider: str = ""
    model: str = ""
    api_key: SecretStr = field(default_factory=lambda: SecretStr(""), repr=False)
    timeout_seconds: float = 20

    @classmethod
    def from_environment(cls):
        provider = os.getenv("SHELLFORGE_AI_PROVIDER", "").strip().lower()
        model = os.getenv("GEMMA_MODEL", "").strip()
        key = os.getenv("GEMMA_API_KEY", "").strip()
        enabled = os.getenv("SHELLFORGE_AI_GENERATION_ENABLED", "false").lower() == "true"
        try:
            timeout = float(os.getenv("SHELLFORGE_AI_TIMEOUT_SECONDS", "20"))
            if not 1 <= timeout <= 60:
                return cls()
        except ValueError:
            return cls()
        if (
            not enabled or provider != "gemma" or not key
            or any(ord(character) < 33 or ord(character) > 126 for character in key)
            or not re.fullmatch(r"gemma-[a-z0-9-]{1,80}", model)
        ):
            return cls()
        return cls(True, provider, model, SecretStr(key), timeout)
