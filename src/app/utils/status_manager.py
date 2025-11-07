"""
Consolidated Status Management System for the LoRa Chat application.
Provides centralized status categorization, device state management, and UI updates.
"""
from __future__ import annotations

import threading
import tkinter as tk
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from utils.design_system import Colors
from utils.design_system import (
    STATUS_DISCONNECTED_KEYWORDS,
    STATUS_CONNECTED_KEYWORDS,
    STATUS_ERROR_KEYWORDS
)


@dataclass
class DeviceInfo:
    """Represents information about a connected device."""
    device_id: str = ""
    device_name: str = ""
    is_connected: bool = False
    connection_type: str = "None"  # "LoRa", "Mock", "Demo", etc.
    status_text: str = "Disconnected"
    last_activity: float = 0.0

    def get_display_name(self) -> str:
        """Get the display name for the device."""
        if self.device_name:
            return self.device_name
        elif self.device_id:
            return f"Device {self.device_id[:8]}"
        else:
            return "No device"

    def get_status_summary(self) -> str:
        """Get a summary of the current status."""
        if not self.is_connected:
            return "Disconnected"

        if self.device_name:
            return f"Connected to {self.device_name}"
        else:
            return "Connected"

    def get_conversation_title(self) -> str:
        """Get the title for conversation view."""
        if self.is_connected and self.device_name:
            return f"Chat with {self.device_name}"
        elif self.is_connected:
            return "Active Conversation"
        else:
            return "No Conversation"


class StatusManager:
    """
    Consolidated status management system that handles both status categorization
    and device state management. This replaces both the old StatusManager and
    UnifiedStatusProvider for a cleaner architecture.
    """

    def __init__(self):
        # Status categorization
        self._current_status: str = "Disconnected"
        self._status_callbacks: list[Callable[[str, str], None]] = []
        self._callback_lock = threading.Lock()

        # Device state management
        self.current_device = DeviceInfo()
        self._device_callbacks: list[Callable[[DeviceInfo], None]] = []
        self._connection_callbacks: list[Callable[[bool, str, str], None]] = []

    def categorize_status(self, status_text: str) -> str:
        """
        Categorize status text into standard status categories.

        Args:
            status_text: Raw status text from the system

        Returns:
            Status category: "connected", "disconnected", "error", or "warning"
        """
        lowered = status_text.lower()

        # Check for connected/ready status
        if any(keyword in lowered for keyword in STATUS_CONNECTED_KEYWORDS):
            return "connected"

        # Check for disconnected/failed status
        elif any(keyword in lowered for keyword in STATUS_DISCONNECTED_KEYWORDS):
            return "disconnected"

        # Check for error status
        elif any(keyword in lowered for keyword in STATUS_ERROR_KEYWORDS):
            return "error"

        # Default to warning for unknown statuses
        else:
            return "warning"

    def get_status_color(self, status_text: str) -> str:
        """
        Get the appropriate color for a status text.

        Args:
            status_text: Raw status text

        Returns:
            Color string for the status
        """
        category = self.categorize_status(status_text)

        # Color mapping for different status categories
        color_map = {
            "connected": "#00C7B1",      # Teal
            "disconnected": "#FF5A5F",   # Red
            "error": "#FF5A5F",         # Red
            "warning": "#F2A93B"        # Orange
        }

        return color_map.get(category, "#FF5A5F")

    def update_status(self, status_text: str, peer_name: Optional[str] = None) -> tuple[str, str]:
        """
        Update status with consistent handling and return status information.

        Args:
            status_text: New status text
            peer_name: Optional peer name

        Returns:
            Tuple of (display_status, status_color)
        """
        self._current_status = status_text
        color = self.get_status_color(status_text)

        # Update device status
        self.current_device.status_text = status_text

        # Update connection state based on status
        category = self.categorize_status(status_text)
        if category == "connected":
            self.current_device.is_connected = True
        elif category in ["disconnected", "error"]:
            self.current_device.is_connected = False

        # CRITICAL FIX: Thread-safe callback execution with proper synchronization
        callbacks_to_execute = []

        with self._callback_lock:
            # Copy callbacks to avoid issues if they modify during iteration
            callbacks_to_execute.extend(self._status_callbacks)

        # Execute callbacks outside the lock to prevent deadlocks
        for callback in callbacks_to_execute:
            try:
                thread_id = threading.get_ident()
                main_thread_id = threading.main_thread().ident
                print(f"[STATUS_CALLBACK] Calling status callback from thread {thread_id} (main={thread_id == main_thread_id})")
                callback(status_text, color)
            except Exception:
                pass  # Silently ignore callback errors

        # CRITICAL FIX: Thread-safe device callback execution
        device_callbacks_to_execute = []

        with self._callback_lock:
            device_callbacks_to_execute.extend(self._device_callbacks)

        for callback in device_callbacks_to_execute:
            try:
                thread_id = threading.get_ident()
                main_thread_id = threading.main_thread().ident
                print(f"[STATUS_CALLBACK] Calling device callback from thread {thread_id} (main={thread_id == main_thread_id})")
                callback(self.current_device)
            except Exception:
                pass  # Silently ignore callback errors

        # Determine display status based on peer connectivity
        if peer_name and category == "connected":
            if not peer_name or peer_name == "Not connected":
                display_status = "Awaiting peer"
            else:
                display_status = f"Paired with: {peer_name}"
        else:
            display_status = status_text

        return display_status, color

    def register_status_callback(self, callback: Callable[[str, str], None]):
        """
        Register a callback for status updates.

        Args:
            callback: Function that receives (status_text, color) as parameters
        """
        self._status_callbacks.append(callback)

    def register_device_callback(self, callback: Callable[[DeviceInfo], None]):
        """
        Register callback for device info changes.

        Args:
            callback: Function receiving DeviceInfo object
        """
        self._device_callbacks.append(callback)

    def register_connection_callback(self, callback: Callable[[bool, str, str], None]):
        """
        Register callback for connection state changes.

        Args:
            callback: Function receiving (is_connected, device_id, device_name)
        """
        self._connection_callbacks.append(callback)

    def unregister_status_callback(self, callback: Callable[[str, str], None]) -> bool:
        """
        Unregister a callback for status updates.

        Args:
            callback: Function to remove from callbacks

        Returns:
            True if callback was found and removed
        """
        with self._callback_lock:
            try:
                self._status_callbacks.remove(callback)
                return True
            except ValueError:
                return False

    def unregister_device_callback(self, callback: Callable[[DeviceInfo], None]) -> bool:
        """
        Unregister a callback for device info changes.

        Args:
            callback: Function to remove from callbacks

        Returns:
            True if callback was found and removed
        """
        with self._callback_lock:
            try:
                self._device_callbacks.remove(callback)
                return True
            except ValueError:
                return False

    def unregister_connection_callback(self, callback: Callable[[bool, str, str], None]) -> bool:
        """
        Unregister a callback for connection state changes.

        Args:
            callback: Function to remove from callbacks

        Returns:
            True if callback was found and removed
        """
        with self._callback_lock:
            try:
                self._connection_callbacks.remove(callback)
                return True
            except ValueError:
                return False

    def clear_all_callbacks(self):
        """
        Clear all registered callbacks. Use with caution - this is for cleanup only.
        """
        with self._callback_lock:
            self._status_callbacks.clear()
            self._device_callbacks.clear()
            self._connection_callbacks.clear()

    # Device state management methods
    def connect_device(self, device_id: str, device_name: str) -> bool:
        """
        Connect to a device and update all registered components.

        Args:
            device_id: Device identifier
            device_name: Device display name

        Returns:
            True if connection was successful
        """
        self.current_device.device_id = device_id
        self.current_device.device_name = device_name
        self.current_device.is_connected = True
        self.current_device.last_activity = 0.0  # Reset activity

        # Update status to reflect connection
        self.update_status("Connected", device_name)

        # Notify all registered components
        for callback in self._connection_callbacks:
            try:
                callback(True, device_id, device_name)
            except Exception:
                pass  # Silently ignore callback errors

        for callback in self._device_callbacks:
            try:
                callback(self.current_device)
            except Exception:
                pass  # Silently ignore callback errors

        return True

    def disconnect_device(self) -> bool:
        """
        Disconnect from current device and update all registered components.

        Returns:
            True if disconnection was successful
        """
        self.current_device.device_id = ""
        self.current_device.device_name = ""
        self.current_device.is_connected = False
        self.current_device.last_activity = 0.0

        # Update status to reflect disconnection
        self.update_status("Disconnected")

        # Notify all registered components
        for callback in self._connection_callbacks:
            try:
                callback(False, "", "")
            except Exception:
                pass  # Silently ignore callback errors

        for callback in self._device_callbacks:
            try:
                callback(self.current_device)
            except Exception:
                pass  # Silently ignore callback errors

        return True

    # Convenience properties
    def get_current_status(self) -> str:
        """Get the current status text."""
        return self._current_status

    def get_current_device(self) -> DeviceInfo:
        """Get current device information."""
        return self.current_device

    def is_connected(self) -> bool:
        """Check if currently connected to a device."""
        return self.current_device.is_connected

    def can_send_messages(self) -> bool:
        """Check if messages can be sent."""
        return self.is_connected() and bool(self._current_status.lower() in ["connected", "ready"])

    def get_conversation_title(self) -> str:
        """Get the title for the current conversation."""
        return self.current_device.get_conversation_title()

    def get_status_summary(self) -> str:
        """Get a summary of current status."""
        return self.current_device.get_status_summary()

    def get_current_status_color(self) -> str:
        """Get the appropriate color for current status."""
        return self.get_status_color(self._current_status)

    def force_update(self):
        """Force an update of the current status."""
        # Trigger all callbacks with current state
        status_color = self.get_current_status_color()
        for callback in self._status_callbacks:
            try:
                callback(self._current_status, status_color)
            except Exception:
                pass

        for callback in self._device_callbacks:
            try:
                callback(self.current_device)
            except Exception:
                pass

        for callback in self._connection_callbacks:
            try:
                callback(self.current_device.is_connected,
                        self.current_device.device_id,
                        self.current_device.device_name)
            except Exception:
                pass


# Global status manager instance
_status_manager: Optional[StatusManager] = None


def get_status_manager() -> StatusManager:
    """Get the global status manager instance."""
    global _status_manager
    if _status_manager is None:
        _status_manager = StatusManager()
    return _status_manager


def reset_status_manager():
    """Reset the global manager (useful for testing)."""
    global _status_manager
    _status_manager = None


# Legacy convenience functions for backward compatibility
def update_global_status(status_text: str, peer_name: Optional[str] = None) -> tuple[str, str]:
    """
    Convenience function to update global status.

    Args:
        status_text: New status text
        peer_name: Optional peer name

    Returns:
        Tuple of (display_status, status_color)
    """
    return get_status_manager().update_status(status_text, peer_name)


def register_status_callback(callback: Callable[[str, str], None]):
    """Register a callback for global status updates."""
    get_status_manager().register_status_callback(callback)


def connect_device(device_id: str, device_name: str) -> bool:
    """Connect to a device using global status manager."""
    return get_status_manager().connect_device(device_id, device_name)


def disconnect_device() -> bool:
    """Disconnect from current device using global status manager."""
    return get_status_manager().disconnect_device()


def is_connected() -> bool:
    """Check if device is connected using global status manager."""
    return get_status_manager().is_connected()
