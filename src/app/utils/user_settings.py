"""Per-user UI preferences persisted between sessions."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Dict, Any


@dataclass
class UserSettings:
    theme_mode: str = "light"
    notifications_enabled: bool = True
    sound_alerts_enabled: bool = False


_SETTINGS_PATH = Path.home() / ".locomm" / "ui_settings.json"
_INSTANCE: UserSettings | None = None


def _ensure_path() -> None:
    _SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_from_disk() -> Dict[str, Any]:
    if not _SETTINGS_PATH.exists():
        return {}
    try:
        with _SETTINGS_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_to_disk(payload: Dict[str, Any]) -> None:
    _ensure_path()
    try:
        with _SETTINGS_PATH.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
    except OSError:
        pass


def _populate(data: Dict[str, Any]) -> UserSettings:
    return UserSettings(
        theme_mode=data.get("theme_mode", "light"),
        notifications_enabled=data.get("notifications_enabled", True),
        sound_alerts_enabled=data.get("sound_alerts_enabled", False),
    )


def get_user_settings() -> UserSettings:
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = _populate(_load_from_disk())
    return _INSTANCE


def save_user_settings(settings: UserSettings) -> None:
    payload = asdict(settings)
    _save_to_disk(payload)
    global _INSTANCE
    _INSTANCE = settings
