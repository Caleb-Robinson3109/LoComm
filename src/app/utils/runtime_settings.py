"""
Runtime settings loader for the Locomm desktop app.
Allows hot-swapping transport backends via env vars or ~/.locomm/runtime.json.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any, Dict


@dataclass
class RuntimeSettings:
    transport_profile: str = "auto"


_SETTINGS: RuntimeSettings | None = None
_CONFIG_PATH = Path.home() / ".locomm" / "runtime.json"


def _ensure_dir() -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _read_config_file() -> Dict[str, Any]:
    if not _CONFIG_PATH.exists():
        return {}
    try:
        with _CONFIG_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


def _write_config_file(data: Dict[str, Any]) -> None:
    _ensure_dir()
    try:
        with _CONFIG_PATH.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
    except OSError:
        pass


def _load_settings() -> RuntimeSettings:
    data = _read_config_file()
    transport_profile = os.environ.get(
        "LOCOMM_TRANSPORT_PROFILE",
        data.get("transport_profile", "auto")
    )
    return RuntimeSettings(transport_profile=transport_profile.lower())


def get_runtime_settings() -> RuntimeSettings:
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = _load_settings()
    return _SETTINGS


def refresh_runtime_settings() -> RuntimeSettings:
    """Force reload, useful for tests."""
    global _SETTINGS
    _SETTINGS = _load_settings()
    return _SETTINGS


def save_runtime_settings(settings: RuntimeSettings) -> None:
    """Persist runtime settings to disk."""
    payload = {"transport_profile": settings.transport_profile}
    _write_config_file(payload)
    global _SETTINGS
    _SETTINGS = settings


def set_transport_profile(profile: str) -> RuntimeSettings:
    """Helper to update the transport profile and persist to disk."""
    profile = (profile or "auto").lower()
    settings = RuntimeSettings(transport_profile=profile)
    save_runtime_settings(settings)
    return settings
