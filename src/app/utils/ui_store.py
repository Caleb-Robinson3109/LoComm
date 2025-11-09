from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, List, Optional

from utils.connection_manager import get_connection_manager
from utils.status_manager import get_status_manager


class DeviceStage(Enum):
    READY = auto()
    SCANNING = auto()
    AWAITING_PIN = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    DISCONNECTED = auto()


@dataclass
class DeviceStatusSnapshot:
    stage: DeviceStage
    title: str
    subtitle: str
    detail: str
    device_name: Optional[str] = None


class UIStore:
    """Centralized UI state aggregator for device/pairing status."""

    def __init__(self):
        self._status_manager = get_status_manager()
        self._connection_manager = get_connection_manager()
        self._device_status = DeviceStatusSnapshot(
            stage=DeviceStage.READY,
            title="Ready to pair",
            subtitle="No device paired.",
            detail="Select Devices to begin."
        )
        self._device_callbacks: List[Callable[[DeviceStatusSnapshot], None]] = []

        self._status_manager.register_status_callback(self._handle_status_text)
        self._status_manager.register_device_callback(self._handle_device_change)
        # connection manager already observes status manager, so no extra hook yet

    # ------------------------------------------------------------------ #
    def subscribe_device_status(self, callback: Callable[[DeviceStatusSnapshot], None]):
        self._device_callbacks.append(callback)
        callback(self._device_status)

    def unsubscribe_device_status(self, callback: Callable[[DeviceStatusSnapshot], None]):
        if callback in self._device_callbacks:
            self._device_callbacks.remove(callback)

    def set_pairing_stage(self, stage: DeviceStage, device_name: Optional[str] = None):
        snapshot = self._snapshot_for_stage(stage, device_name)
        self._device_status = snapshot
        self._emit_device_status()

    def get_device_status(self) -> DeviceStatusSnapshot:
        return self._device_status

    # ------------------------------------------------------------------ #
    def _handle_status_text(self, status_text: str, _color: str):
        text = status_text.lower()
        device_name = self._status_manager.get_current_device().device_name
        if "scan" in text:
            self.set_pairing_stage(DeviceStage.SCANNING, device_name)
        elif "awaiting" in text:
            self.set_pairing_stage(DeviceStage.AWAITING_PIN, device_name)
        elif "connecting" in text:
            self.set_pairing_stage(DeviceStage.CONNECTING, device_name)
        elif "disconnect" in text:
            self.set_pairing_stage(DeviceStage.DISCONNECTED, device_name)
        elif "connected" in text:
            self.set_pairing_stage(DeviceStage.CONNECTED, device_name)

    def _handle_device_change(self, device_info):
        if not device_info.is_connected and device_info.device_name:
            self.set_pairing_stage(DeviceStage.DISCONNECTED, device_info.device_name)

    def _snapshot_for_stage(self, stage: DeviceStage, device_name: Optional[str]) -> DeviceStatusSnapshot:
        if stage == DeviceStage.SCANNING:
            return DeviceStatusSnapshot(
                stage=stage,
                title="Scanning…",
                subtitle="Searching for nearby devices.",
                detail="This may take a few seconds.",
                device_name=None
            )
        if stage == DeviceStage.AWAITING_PIN:
            label = device_name or "device"
            return DeviceStatusSnapshot(
                stage=stage,
                title=f"Awaiting PIN for {label}",
                subtitle="Enter the 8-digit code to trust this device.",
                detail="Complete the PIN flow in the Devices tab.",
                device_name=device_name
            )
        if stage == DeviceStage.CONNECTING:
            label = device_name or "device"
            return DeviceStatusSnapshot(
                stage=stage,
                title=f"Connecting to {label}…",
                subtitle="Establishing encrypted transport.",
                detail="You can start chatting once connected.",
                device_name=device_name
            )
        if stage == DeviceStage.CONNECTED:
            label = device_name or "LoRa peer"
            return DeviceStatusSnapshot(
                stage=stage,
                title=f"Connected to {label}",
                subtitle="Secure LoRa link established.",
                detail="Messages will send immediately.",
                device_name=device_name
            )
        if stage == DeviceStage.DISCONNECTED:
            label = device_name or "device"
            return DeviceStatusSnapshot(
                stage=stage,
                title="Disconnected",
                subtitle=f"Disconnected ({label}).",
                detail="Reconnect from the Devices tab.",
                device_name=device_name
            )
        # Default ready state
        return DeviceStatusSnapshot(
            stage=DeviceStage.READY,
            title="Ready to pair",
            subtitle="No device paired. Start by scanning for hardware.",
            detail="Select the Devices tab to begin.",
            device_name=None
        )

    def _emit_device_status(self):
        snapshot = self._device_status
        for callback in list(self._device_callbacks):
            callback(snapshot)


_ui_store: Optional[UIStore] = None


def get_ui_store() -> UIStore:
    global _ui_store
    if _ui_store is None:
        _ui_store = UIStore()
    return _ui_store
