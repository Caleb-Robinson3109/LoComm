from __future__ import annotations

from typing import Callable

from state.store import get_app_state, DeviceStage, DeviceStatusSnapshot

# Re-export types for backward compatibility
__all__ = ["DeviceStage", "DeviceStatusSnapshot", "UIStore", "get_ui_store"]


class UIStore:
    """
    Centralized UI state aggregator for device/pairing status.
    Now a wrapper around AppState for backward compatibility.
    """

    def __init__(self):
        self._app_state = get_app_state()
        self._device_callbacks: list[Callable[[DeviceStatusSnapshot], None]] = []
        
        # Subscribe to AppState changes
        self._app_state.subscribe(self._handle_app_state_change)

    def subscribe_device_status(self, callback: Callable[[DeviceStatusSnapshot], None]):
        self._device_callbacks.append(callback)
        if self._app_state.device_status_snapshot:
            callback(self._app_state.device_status_snapshot)

    def unsubscribe_device_status(self, callback: Callable[[DeviceStatusSnapshot], None]):
        if callback in self._device_callbacks:
            self._device_callbacks.remove(callback)

    def get_device_status(self) -> DeviceStatusSnapshot:
        return self._app_state.device_status_snapshot

    def set_pairing_stage(self, stage: DeviceStage, device_name: str | None = None):
        """Update the pairing stage in the central AppState."""
        self._app_state.update(device_stage=stage, device_name=device_name)

    def _handle_app_state_change(self, app_state):
        if app_state.device_status_snapshot:
            self._emit_device_status(app_state.device_status_snapshot)

    def _emit_device_status(self, snapshot: DeviceStatusSnapshot):
        stale_callbacks: list[Callable[[DeviceStatusSnapshot], None]] = []
        for callback in list(self._device_callbacks):
            try:
                callback(snapshot)
            except Exception:
                stale_callbacks.append(callback)
        for callback in stale_callbacks:
            try:
                self._device_callbacks.remove(callback)
            except ValueError:
                pass

    def close(self):
        """Unhook callbacks to prevent leaks."""
        self._app_state.unsubscribe(self._handle_app_state_change)

    def __del__(self):
        self.close()


_ui_store: UIStore | None = None


def get_ui_store() -> UIStore:
    global _ui_store
    if _ui_store is None:
        _ui_store = UIStore()
    return _ui_store

