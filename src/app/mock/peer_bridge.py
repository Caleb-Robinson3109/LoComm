"""
Bridge that wires desktop chat and mock peer UI together.
"""
from __future__ import annotations

from typing import Callable, Optional


class MockPeerBridge:
    """Mediator between the mock backend and the mock peer UI."""

    def __init__(self):
        self._peer_callback: Optional[Callable[[str, str], None]] = None
        self._backend = None

    def register_backend(self, backend) -> None:
        self._backend = backend

    def unregister_backend(self, backend) -> None:
        if self._backend is backend:
            self._backend = None

    def register_peer_callback(self, callback: Callable[[str, str], None]) -> None:
        self._peer_callback = callback

    def unregister_peer_callback(self, callback: Callable[[str, str], None]) -> None:
        if self._peer_callback is callback:
            self._peer_callback = None

    def notify_peer(self, sender: str, text: str) -> None:
        if self._peer_callback:
            self._peer_callback(sender, text)

    def send_from_peer(self, text: str) -> None:
        if self._backend:
            self._backend.inject_peer_message(text)


_BRIDGE = MockPeerBridge()


def get_peer_bridge() -> MockPeerBridge:
    return _BRIDGE
