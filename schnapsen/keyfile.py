"""Read the TypeSafe API key from jef.api at the repository root."""

from pathlib import Path

KEY_PATH = Path(__file__).resolve().parents[1] / "jef.api"


def read_api_key(path: Path | None = None) -> str:
    target = KEY_PATH if path is None else path
    try:
        return target.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
