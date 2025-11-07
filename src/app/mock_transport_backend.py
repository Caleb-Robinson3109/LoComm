"""
Mock LoRa transport backend used for local development and demos.

This module is intentionally isolated so it can be replaced once the
network/security teams deliver the production-ready implementation.
"""
from __future__ import annotations

import time
from typing import Optional, Tuple


class MockLoCommBackend:
    """Simple in-memory backend that simulates a LoRa link."""

    label = "mock"

    def __init__(self):
        self._connected = False
        self._pending_messages: list[Tuple[str, str]] = []

    def connect(self, pairing_context: Optional[dict] = None) -> bool:
        """
        Pretend to connect to a device.

        Args:
            pairing_context: Optional metadata coming from the UI (unused).
        """
        self._connected = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def send(self, sender: str, message: str) -> bool:
        if not self._connected:
            return False
        # Echo back for demo purposes
        self._pending_messages.append((sender, message))
        return True

    def receive(self) -> Tuple[str, str]:
        if not self._connected:
            time.sleep(0.2)
            return ("", "")

        if self._pending_messages:
            return self._pending_messages.pop(0)

        time.sleep(0.2)
        return ("", "")

    def start_pairing(self) -> bool:
        return True

    def stop_pairing(self) -> bool:
        return True
