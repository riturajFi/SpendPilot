from pathlib import Path

from dotenv import load_dotenv


def load_env() -> None:
    root = Path(__file__).resolve().parent.parent
    for candidate in (root / ".env", root / "backend" / ".env"):
        if candidate.exists():
            load_dotenv(candidate, override=False)
