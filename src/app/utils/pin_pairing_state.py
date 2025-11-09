"""
Helper that encapsulates PIN pairing validation and lockout awareness.
Provides a shared entry point for the UI and other components to reason about PIN state.
"""
from __future__ import annotations

from typing import Optional, Tuple

from utils.pin_authentication import get_pin_auth, get_security_status


class PinPairingState:
    """Keeps validation rules and lockout awareness for the pairing UI."""

    DEFAULT_CLIENT_IDENTIFIER = "desktop-client"

    def __init__(self, client_identifier: Optional[str] = None):
        self.client_identifier = client_identifier or self.DEFAULT_CLIENT_IDENTIFIER
        self.auth = get_pin_auth()

    def get_pin_length(self) -> int:
        """Get the configured PIN length."""
        return self.auth.get_pin_length()

    def validate_pin(self, pin: str) -> Tuple[bool, Optional[str]]:
        """Validate format of a PIN (length + charset)."""
        if not pin:
            return False, "Please enter a PIN"
        length = self.get_pin_length()
        if len(pin) != length:
            return False, f"PIN must be exactly {length} characters"
        if not self.auth.validate_pin_format(pin):
            return False, "PIN must contain only letters A-Z and numbers"
        return True, None

    def check_lockout(self) -> Tuple[bool, Optional[str], float]:
        """Check if the client is currently locked out."""
        status = get_security_status(self.client_identifier)
        if status["is_locked"]:
            minutes = int(status["lockout_remaining_seconds"] // 60)
            message = f"Account locked for {minutes} more minutes"
            return True, message, status["lockout_remaining_seconds"]
        return False, None, 0.0
