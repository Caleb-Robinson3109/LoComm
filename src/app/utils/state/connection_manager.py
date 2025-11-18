"""
Centralized connection management system for the LoRa Chat application.
Provides consistent connection state management across all UI components.
"""
from typing import Callable, Any
import threading
from utils.state.status_manager import get_status_manager
from utils.app_logger import get_logger
from ui.theme_tokens import AppConfig


class ConnectionManager:
    """
    Centralized connection state management that ensures consistency
    across all UI components. Now unified with StatusManager for
    consistent device identity tracking.
    """

    def __init__(self):
        # Delegate to StatusManager for unified device state
        self._status_manager = get_status_manager()
        self._connection_callbacks: list[Callable[[bool, str | None, str | None], None]] = []
        self._device_info_callbacks: list[Callable[[dict[str, Any] | None], None]] = []
        self._lock = threading.Lock()  # Thread safety
        self._logger = get_logger("connection_manager")

    # ========== CONNECTION STATE MANAGEMENT ==========

    def connect_device(self, device_id: str, device_name: str) -> bool:
        """
        Connect to a device and update all registered components.
        Calls StatusManager to populate DeviceInfo.

        Args:
            device_id: Device identifier
            device_name: Device display name

        Returns:
            True if connection was successful
        """
        with self._lock:
            # Use unified status manager to populate DeviceInfo
            success = self._status_manager.connect_device(device_id, device_name)

            if success:
                # Notify all registered components about connection change
                self._notify_connection_change()
                self._notify_device_info_change()

        return success

    def disconnect_device(self) -> bool:
        """
        Disconnect from current device and update all registered components.
        Calls StatusManager to clear DeviceInfo.

        Returns:
            True if disconnection was successful
        """
        with self._lock:
            # Use unified status manager to clear DeviceInfo
            success = self._status_manager.disconnect_device()

            if success:
                # Notify all registered components about disconnection
                self._notify_connection_change()
                self._notify_device_info_change()

        return success

    def is_connected(self) -> bool:
        """Get current connection status."""
        with self._lock:
            return self._status_manager.is_connected()

    def get_connected_device(self) -> dict[str, Any] | None:
        """Get information about currently connected device (alias for get_connected_device_info)."""
        return self.get_connected_device_info()

    def get_connected_device_info(self) -> dict[str, Any] | None:
        """Get information about currently connected device."""
        with self._lock:
            device_info = self._status_manager.get_current_device()
            if device_info.is_connected:
                return {
                    'id': device_info.device_id,
                    'name': device_info.device_name,
                    'is_connected': device_info.is_connected
                }
            return None

    def get_connection_status_text(self) -> str:
        """Get appropriate status text for UI display."""
        device_info = self._status_manager.get_current_device()
        return AppConfig.STATUS_CONNECTED if device_info.is_connected else AppConfig.STATUS_DISCONNECTED

    # ========== CALLBACK REGISTRATION ==========

    def register_connection_callback(self, callback: Callable[[bool, str | None, str | None], None]):
        """
        Register callback for connection state changes.

        Args:
            callback: Function receiving (is_connected, device_id, device_name)
        """
        with self._lock:
            if callback not in self._connection_callbacks:
                self._connection_callbacks.append(callback)

    def unregister_connection_callback(self, callback: Callable[[bool, str | None, str | None], None]):
        """Remove a previously registered connection callback."""
        with self._lock:
            if callback in self._connection_callbacks:
                self._connection_callbacks.remove(callback)

    def register_device_info_callback(self, callback: Callable[[dict[str, Any] | None], None]):
        """
        Register callback for device info changes.

        Args:
            callback: Function receiving device info dict or None
        """
        with self._lock:
            if callback not in self._device_info_callbacks:
                self._device_info_callbacks.append(callback)

    def unregister_device_info_callback(self, callback: Callable[[dict[str, Any] | None], None]):
        """Remove a previously registered device info callback."""
        with self._lock:
            if callback in self._device_info_callbacks:
                self._device_info_callbacks.remove(callback)

    def _notify_connection_change(self):
        """Notify all registered callbacks about connection state change."""
        device_info = self._status_manager.get_current_device()
        for callback in list(self._connection_callbacks):
            try:
                callback(device_info.is_connected, device_info.device_id, device_info.device_name)
            except Exception as e:
                self._logger.warning("Connection callback failed: %s", e)
                self.unregister_connection_callback(callback)

    def _notify_device_info_change(self):
        """Notify all registered callbacks about device info change."""
        device_info = self._status_manager.get_current_device()
        for callback in list(self._device_info_callbacks):
            try:
                if device_info.is_connected:
                    callback({
                        'id': device_info.device_id,
                        'name': device_info.device_name,
                        'is_connected': device_info.is_connected
                    })
                else:
                    callback(None)
            except Exception as e:
                self._logger.warning("Device info callback failed: %s", e)
                self.unregister_device_info_callback(callback)

    # ========== CONVENIENCE METHODS FOR UI COMPONENTS ==========

    def update_button_states(self, connect_btn, disconnect_btn):
        """
        Update button states based on current connection status.

        Args:
            connect_btn: Connect button widget
            disconnect_btn: Disconnect button widget
        """
        device_info = self._status_manager.get_current_device()
        if device_info.is_connected:
            connect_btn.configure(state="disabled", text="Connected")
            disconnect_btn.configure(state="normal", text="Disconnect")
        else:
            connect_btn.configure(state="normal", text="Connect to Device")
            disconnect_btn.configure(state="disabled", text="Disconnect Device")

    def should_disable_connect_button(self, selected_device_id: str | None = None) -> bool:
        """
        Determine if connect button should be disabled.

        Args:
            selected_device_id: Currently selected device ID

        Returns:
            True if connect button should be disabled
        """
        device_info = self._status_manager.get_current_device()
        if not device_info.is_connected:
            return False

        # If connected to a different device, disable connect button
        if selected_device_id and selected_device_id != device_info.device_id:
            return True

        # If connected to the selected device, disable connect button
        if selected_device_id == device_info.device_id:
            return True

        return False

    def disconnect_all(self) -> bool:
        """
        Disconnect all devices and clear connection state.

        Returns:
            True if disconnection was successful
        """
        with self._lock:
            # Use unified status manager for proper cleanup
            success = self._status_manager.disconnect_device()

            if success:
                # Notify all registered components
                self._notify_connection_change()
                self._notify_device_info_change()

        return success


# Global connection manager instance
_connection_manager: ConnectionManager | None = None


class ConnectionManagerFactory:
    """Factory class for creating and managing ConnectionManager instances."""

    _instance: ConnectionManager | None = None

    @classmethod
    def create(cls) -> ConnectionManager:
        """Create a new ConnectionManager instance."""
        return ConnectionManager()

    @classmethod
    def get_singleton(cls) -> ConnectionManager:
        """Get or create the singleton ConnectionManager instance."""
        if cls._instance is None:
            cls._instance = ConnectionManager()
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance (backward compatibility)."""
    return ConnectionManagerFactory.get_singleton()


# Convenience functions for components
def connect_device(device_id: str, device_name: str) -> bool:
    """Connect to a device using global connection manager."""
    return get_connection_manager().connect_device(device_id, device_name)


def disconnect_device() -> bool:
    """Disconnect from current device using global connection manager."""
    return get_connection_manager().disconnect_device()


def is_connected() -> bool:
    """Check if device is connected using global connection manager."""
    return get_connection_manager().is_connected()


def get_connected_device_info() -> dict[str, Any] | None:
    """Get connected device info using global connection manager."""
    return get_connection_manager().get_connected_device_info()
