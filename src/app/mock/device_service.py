"""
Mock device catalogue used by the UI and mock transport.
All data lives under mock/data so it can be stripped from production builds.
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
    data_path = Path(__file__).resolve().parent / "data" / "devices.json"

    def __init__(self):
        self._devices: Dict[str, MockDevice] = {}
        self._base_devices: Dict[str, MockDevice] = {}
        self._dynamic_counter = 0
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
        self._base_devices = devices
        self._devices = dict(devices)

    def refresh(self) -> None:
        self._load()

    def list_devices(self) -> List[MockDevice]:
        devices = list(self._devices.values())
        # Ensure Mock device is always first
        mock_device = next((d for d in devices if d.device_id == "MOCK"), None)
        if mock_device:
            devices.remove(mock_device)
            devices.insert(0, mock_device)
        return devices

    def get_device(self, device_id: str) -> Optional[MockDevice]:
        return self._devices.get(device_id)

    def pick_default(self) -> Optional[MockDevice]:
        return next(iter(self._devices.values()), None)

    def simulate_scan(self) -> List[MockDevice]:
        """Create synthetic devices so the UI feels dynamic."""
        name_pool = [
            "Orion", "Luna", "Nova", "Aria", "Atlas", "Beacon", "Nimbus", "Echo",
            "Vertex", "Helio", "Cobalt", "Quasar", "Drift", "Pulse", "Solstice",
            "Zenith", "Aurora", "Comet", "Vega", "Juno", "Sierra", "Ranger", "Harbor",
            "Sentinel", "Vertex", "Photon", "Falcon", "Iris", "Mint", "Summit"
        ]
        statuses = ["Available", "Sleeping", "Busy"]
        discovered: List[MockDevice] = []
        for _ in range(2):
            self._dynamic_counter += 1
            device_id = f"SIM{self._dynamic_counter:03d}"
            name = name_pool[self._dynamic_counter % len(name_pool)]
            status = statuses[self._dynamic_counter % len(statuses)]
            metadata = {"firmware": f"1.3.{self._dynamic_counter}", "region": "EU868"}
            telemetry = {
                "rssi": -70 - self._dynamic_counter,
                "snr": 4.0,
                "battery": max(30, 95 - self._dynamic_counter * 3),
            }
            device = MockDevice(
                device_id=device_id,
                name=name,
                status=status,
                last_seen="Just found",
                metadata=metadata,
                telemetry=telemetry,
            )
            self._devices[device_id] = device
            discovered.append(device)
        return discovered


_SERVICE: Optional[MockDeviceService] = None


def get_mock_device_service() -> MockDeviceService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = MockDeviceService()
    return _SERVICE
