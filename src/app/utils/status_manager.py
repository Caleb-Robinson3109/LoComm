"""
Centralized status management for the LoRa Chat application.
Provides consistent status categorization and UI updates.
"""
from typing import Optional, Callable
import tkinter as tk
from utils.design_system import Colors
from utils.config import (
    STATUS_DISCONNECTED_KEYWORDS,
    STATUS_CONNECTED_KEYWORDS,
    STATUS_ERROR_KEYWORDS
)


class StatusManager:
    """
    Centralized status management system that handles status categorization,
    color determination, and provides methods for status updates.
    """

    def __init__(self):
        self._current_status: str = "Disconnected"
        self._status_callbacks: list[Callable[[str, str], None]] = []

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

        # All status colors are white now
        color_map = {
            "connected": "#FFFFFF",
            "disconnected": "#FFFFFF",
            "error": "#FFFFFF",
            "warning": "#FFFFFF"
        }

        return color_map.get(category, "#FFFFFF")

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

        # Notify callbacks
        for callback in self._status_callbacks:
            try:
                callback(status_text, color)
            except Exception:
                pass  # Silently ignore callback errors

        # Determine display status based on peer connectivity
        if peer_name and self.categorize_status(status_text) == "connected":
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

    def get_current_status(self) -> str:
        """Get the current status text."""
        return self._current_status

    def get_status_indicator_text(self, peer_name: Optional[str] = None) -> str:
        """
        Get the appropriate peer status text.

        Args:
            peer_name: Current peer name

        Returns:
            Formatted peer status text
        """
        category = self.categorize_status(self._current_status)

        if category == "disconnected":
            return "Not connected"
        elif category == "connected":
            if peer_name and peer_name not in ("Not connected", ""):
                return peer_name
            else:
                return "Awaiting peer"
        else:
            return peer_name or "Not connected"


# Global status manager instance
_status_manager: Optional[StatusManager] = None


def get_status_manager() -> StatusManager:
    """Get the global status manager instance."""
    global _status_manager
    if _status_manager is None:
        _status_manager = StatusManager()
    return _status_manager


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
