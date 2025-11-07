"""
Centralized connection management system for the LoRa Chat application.
Provides consistent connection state management across all UI components.
"""
from typing import Optional, Callable, Dict, Any
import threading
from utils.status_manager import update_global_status


class ConnectionManager:
    """
    Centralized connection state management that ensures consistency
    across all UI components (pair tab, chat tab, sidebar, etc.)
    """

    def __init__(self):
        self._current_device_id: Optional[str] = None
        self._current_device_name: Optional[str] = None
        self._is_connected: bool = False
        self._connection_callbacks: list[Callable[[bool, Optional[str], Optional[str]], None]] = []
        self._device_info_callbacks: list[Callable[[Optional[Dict[str, Any]]], None]] = []
        self._lock = threading.Lock()  # Thread safety

    # ========== CONNECTION STATE MANAGEMENT ==========

    def connect_device(self, device_id: str, device_name: str) -> bool:
        """
        Connect to a device and update all registered components.

        Args:
            device_id: Device identifier
            device_name: Device display name

        Returns:
            True if connection was successful
        """
        with self._lock:
            self._current_device_id = device_id
            self._current_device_name = device_name
            self._is_connected = True

            # Update global status manager
            update_global_status("Connected", device_name)

            # Notify all registered components
            self._notify_connection_change()
            self._notify_device_info_change()

        return True

    def disconnect_device(self) -> bool:
        """
        Disconnect from current device and update all registered components.

        Returns:
            True if disconnection was successful
        """
        with self._lock:
            self._current_device_id = None
            self._current_device_name = None
            self._is_connected = False

            # Update global status manager
            update_global_status("Disconnected")

            # Notify all registered components
            self._notify_connection_change()
            self._notify_device_info_change()

        return True

    def is_connected(self) -> bool:
        """Get current connection status."""
        with self._lock:
            return self._is_connected

    def get_connected_device(self) -> Optional[Dict[str, Any]]:
        """Get information about currently connected device (alias for get_connected_device_info)."""
        return self.get_connected_device_info()

    def get_connected_device_info(self) -> Optional[Dict[str, Any]]:
        """Get information about currently connected device."""
        with self._lock:
            if self._is_connected and self._current_device_id:
                return {
                    'id': self._current_device_id,
                    'name': self._current_device_name,
                    'is_connected': self._is_connected
                }
            return None

    def get_connection_status_text(self) -> str:
        """Get appropriate status text for UI display."""
        if self._is_connected:
            return f"Connected to {self._current_device_name}" if self._current_device_name else "Connected"
        else:
            return "Disconnected"

    # ========== CALLBACK REGISTRATION ==========

    def register_connection_callback(self, callback: Callable[[bool, Optional[str], Optional[str]], None]):
        """
        Register callback for connection state changes.

        Args:
            callback: Function receiving (is_connected, device_id, device_name)
        """
        with self._lock:
            self._connection_callbacks.append(callback)

    def register_device_info_callback(self, callback: Callable[[Optional[Dict[str, Any]]], None]):
        """
        Register callback for device info changes.

        Args:
            callback: Function receiving device info dict or None
        """
        with self._lock:
            self._device_info_callbacks.append(callback)

    def _notify_connection_change(self):
        """Notify all registered callbacks about connection state change."""
        for callback in self._connection_callbacks:
            try:
                callback(self._is_connected, self._current_device_id, self._current_device_name)
            except Exception:
                pass  # Silently ignore callback errors

    def _notify_device_info_change(self):
        """Notify all registered callbacks about device info change."""
        device_info = self.get_connected_device_info()
        for callback in self._device_info_callbacks:
            try:
                callback(device_info)
            except Exception:
                pass  # Silently ignore callback errors

    # ========== CONVENIENCE METHODS FOR UI COMPONENTS ==========

    def update_button_states(self, connect_btn, disconnect_btn):
        """
        Update button states based on current connection status.

        Args:
            connect_btn: Connect button widget
            disconnect_btn: Disconnect button widget
        """
        if self._is_connected:
            connect_btn.configure(state="disabled", text="Connected")
            disconnect_btn.configure(state="normal", text="Disconnect")
        else:
            connect_btn.configure(state="normal", text="Connect to Device")
            disconnect_btn.configure(state="disabled", text="Disconnect Device")

    def should_disable_connect_button(self, selected_device_id: Optional[str] = None) -> bool:
        """
        Determine if connect button should be disabled.

        Args:
            selected_device_id: Currently selected device ID

        Returns:
            True if connect button should be disabled
        """
        if not self._is_connected:
            return False

        # If connected to a different device, disable connect button
        if selected_device_id and selected_device_id != self._current_device_id:
            return True

        # If connected to the selected device, disable connect button
        if selected_device_id == self._current_device_id:
            return True

        return False

    def disconnect_all(self) -> bool:
        """
        Disconnect all devices and clear connection state.

        Returns:
            True if disconnection was successful
        """
        with self._lock:
            self._current_device_id = None
            self._current_device_name = None
            self._is_connected = False

            # Update global status manager
            update_global_status("Disconnected")

            # Notify all registered components
            self._notify_connection_change()
            self._notify_device_info_change()

        return True


# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


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


def get_connected_device_info() -> Optional[Dict[str, Any]]:
    """Get connected device info using global connection manager."""
    return get_connection_manager().get_connected_device_info()
