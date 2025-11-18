"""
Centralized Application State Management.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Callable

from utils.app_logger import get_logger
from ui.theme_tokens import AppConfig

logger = get_logger(__name__)


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
    device_name: str | None = None


@dataclass
class AppState:
    """
    Centralized state container for the application.
    Replaces scattered singletons and provides a unified source of truth.
    """
    # Device State
    device_stage: DeviceStage = DeviceStage.READY
    device_id: str | None = None
    device_name: str | None = None
    device_status_snapshot: DeviceStatusSnapshot | None = None
    
    # User State
    user_name: str = "Orion"
    
    # UI State
    current_view: str = "home"
    theme_mode: str = "light"
    
    # Observers
    _observers: list[Callable[[AppState], None]] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self):
        # Initialize default snapshot
        if self.device_status_snapshot is None:
            self.device_status_snapshot = self._snapshot_for_stage(self.device_stage, self.device_name)

    def update(self, **kwargs):
        """Update state attributes and notify observers."""
        with self._lock:
            changed = False
            for key, value in kwargs.items():
                if hasattr(self, key) and getattr(self, key) != value:
                    setattr(self, key, value)
                    changed = True
            
            # Auto-update snapshot if stage or device name changed
            if "device_stage" in kwargs or "device_name" in kwargs:
                self.device_status_snapshot = self._snapshot_for_stage(self.device_stage, self.device_name)
                changed = True

            if changed:
                self._notify()

    def _snapshot_for_stage(self, stage: DeviceStage, device_name: str | None) -> DeviceStatusSnapshot:
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
                title="Connected",
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


    def subscribe(self, callback: Callable[[AppState], None]):
        """Subscribe to state changes."""
        with self._lock:
            if callback not in self._observers:
                self._observers.append(callback)

    def unsubscribe(self, callback: Callable[[AppState], None]):
        """Unsubscribe from state changes."""
        with self._lock:
            if callback in self._observers:
                self._observers.remove(callback)

    def _notify(self):
        """Notify all observers of state changes."""
        # Copy observers to avoid modification during iteration
        observers = list(self._observers)
        for callback in observers:
            try:
                callback(self)
            except Exception as e:
                logger.error(f"Error in state observer: {e}")


# Global instance
_app_state: AppState | None = None


def get_app_state() -> AppState:
    """Get the global AppState instance."""
    global _app_state
    if _app_state is None:
        _app_state = AppState()
    return _app_state
