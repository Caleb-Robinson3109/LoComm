"""
Mock device catalogue used by the UI and mock transport.
Loads editable JSON so developers can add/remove devices without code changes.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class MockDevice:
    device_id: str
    name: str
    status: str
    last_seen: str
    metadata: Dict[str, Any]
    telemetry: Dict[str, Any]

    def to_table_row(self) -> tuple[str, str, str, str]:
        """Convenience helper for ttk tree usage."""
        return (self.device_id, self.name, self.status, self.last_seen)


class MockDeviceService:
    data_path = Path(__file__).resolve().parent.parent / "mock_data" / "devices.json"

    def __init__(self):
        self._devices: Dict[str, MockDevice] = {}
        self._load()

    def _load(self) -> None:
        if not self.data_path.exists():
            self._devices = {}
            return
        try:
            with self.data_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            self._devices = {}
            return

        devices: Dict[str, MockDevice] = {}
        for entry in payload:
            device = MockDevice(
                device_id=entry.get("id", ""),
                name=entry.get("name", "Unnamed device"),
                status=entry.get("status", "Unknown"),
                last_seen=entry.get("last_seen", "Unknown"),
                metadata=entry.get("metadata") or {},
                telemetry=entry.get("telemetry") or {},
            )
            if device.device_id:
                devices[device.device_id] = device
        self._devices = devices

    def refresh(self) -> None:
        self._load()

    def list_devices(self) -> List[MockDevice]:
        return list(self._devices.values())

    def get_device(self, device_id: str) -> Optional[MockDevice]:
        return self._devices.get(device_id)

    def pick_default(self) -> Optional[MockDevice]:
        return next(iter(self._devices.values()), None)


_SERVICE: Optional[MockDeviceService] = None


def get_mock_device_service() -> MockDeviceService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = MockDeviceService()
    return _SERVICE
