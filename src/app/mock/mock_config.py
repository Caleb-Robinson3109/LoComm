"""
Mock configuration helpers for adjusting scenarios at runtime.
Settings persist to ~/.locomm/mock_config.json so developers can swap
network simulations without code changes.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict


@dataclass
class MockConfig:
    scenario: str = "default"


_CONFIG_PATH = Path.home() / ".locomm" / "mock_config.json"
_CONFIG: MockConfig | None = None


def _ensure_dir() -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_from_disk() -> Dict[str, Any]:
    if not _CONFIG_PATH.exists():
        return {}
    try:
        with _CONFIG_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_to_disk(data: Dict[str, Any]) -> None:
    _ensure_dir()
    try:
        with _CONFIG_PATH.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
    except OSError:
        pass


def _load_config() -> MockConfig:
    raw = _load_from_disk()
    scenario = raw.get("scenario", "default")
    return MockConfig(scenario=scenario)


def get_mock_config() -> MockConfig:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = _load_config()
    return _CONFIG


def set_mock_scenario(scenario: str) -> MockConfig:
    """Persist a new mock scenario selection."""
    global _CONFIG
    scenario = scenario or "default"
    _CONFIG = MockConfig(scenario=scenario)
    _save_to_disk({"scenario": scenario})
    return _CONFIG


def refresh_mock_config() -> MockConfig:
    """Force reload (useful for tests)."""
    global _CONFIG
    _CONFIG = _load_config()
    return _CONFIG
