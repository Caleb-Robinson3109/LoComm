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


def _read_config_file() -> Dict[str, Any]:
    if not _CONFIG_PATH.exists():
        return {}
    try:
        with _CONFIG_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


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
