"""Read API keys from files at the repository root."""

from pathlib import Path

KEY_PATH = Path(__file__).resolve().parents[1] / "jef.api"
CHAT_KEY_PATH = Path(__file__).resolve().parents[1] / "chat.api"
CHAT_URL = "https://api.openai.com/v1/chat/completions"
CHAT_MODEL = "gpt-6-sol"


def read_api_key(path: Path | None = None) -> str:
    target = KEY_PATH if path is None else path
    return _read(target)


def read_chat_api_key(path: Path | None = None) -> str:
    return read_chat_settings(path)[2]


def read_chat_settings(path: Path | None = None) -> tuple[str, str, str]:
    """Return the ChatGPT URL, model, and API key."""
    target = CHAT_KEY_PATH if path is None else path
    try:
        text = target.read_text(encoding="utf-8")
    except OSError:
        return CHAT_URL, CHAT_MODEL, ""
    fields: dict[str, str] = {}
    for line in text.splitlines():
        name, separator, value = line.partition("=")
        if separator:
            fields[name.strip()] = value.strip()
    if "key" in fields:
        key = fields["key"]
    else:
        key = text.strip()
    return fields.get("url") or CHAT_URL, fields.get("model") or CHAT_MODEL, key


def _read(target: Path) -> str:
    try:
        return target.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
