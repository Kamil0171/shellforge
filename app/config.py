from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "shellforge.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
APP_NAME = "ShellForge"
APP_VERSION = "0.1.0"
