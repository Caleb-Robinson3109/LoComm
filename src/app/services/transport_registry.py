"""
Runtime registry for transport backends.
"""
from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from services.transport_contract import PairingContext, TransportMessage


class TransportBackend(Protocol):
    """Protocol defining the required interface for transport backends."""

    def connect(self, pairing_context: PairingContext | None = None) -> bool: ...

    def disconnect(self) -> bool: ...

    def send(self, message: TransportMessage) -> bool: ...

    def receive(self) -> TransportMessage | None: ...

    def start_pairing(self) -> bool: ...

    def stop_pairing(self) -> bool: ...


@dataclass
class BackendBundle:
    backend: TransportBackend
    profile: str
    label: str
    error: str | None = None


class RealLoCommBackend:
    """Thin adapter around the external LoCommAPI module."""

    label = "locomm-api"

    def __init__(self, api_module):
        self.api = api_module

    def connect(self, pairing_context: PairingContext | None = None) -> bool:
        connect_fn = getattr(self.api, "connect_to_device", None)
        if not connect_fn:
            return False
        return bool(connect_fn())

    def disconnect(self) -> bool:
        disconnect_fn = getattr(self.api, "disconnect_from_device", None)
        if disconnect_fn:
            return bool(disconnect_fn())
        return False

    def send(self, message: TransportMessage) -> bool:
        send_fn = getattr(self.api, "send_message", None)
        if send_fn:
            return bool(send_fn(message.sender, message.payload))
        return False

    def receive(self) -> TransportMessage | None:
        receive_fn = getattr(self.api, "receive_message", None)
        if not receive_fn:
            return None
        sender, payload = receive_fn()
        if not sender and not payload:
            return None
        return TransportMessage(sender=sender, payload=payload)

    def start_pairing(self) -> bool:
        pair_fn = getattr(self.api, "pair_devices", None)
        if pair_fn:
            return bool(pair_fn())
        return False

    def stop_pairing(self) -> bool:
        stop_fn = getattr(self.api, "stop_pair", None)
        if stop_fn:
            return bool(stop_fn())
        return False


class DummyBackend:
    """No-op backend for deviceless execution."""

    def connect(self, pairing_context: PairingContext | None = None) -> bool:
        return True

    def disconnect(self) -> bool:
        return True

    def send(self, message: TransportMessage) -> bool:
        return True

    def receive(self) -> TransportMessage | None:
        return None

    def start_pairing(self) -> bool:
        return True

    def stop_pairing(self) -> bool:
        return True


def get_backend() -> BackendBundle:
    """
    Get the appropriate transport backend.
    Attempts to load the real LoCommAPI backend.
    Falls back to DummyBackend if not available.
    """
    try:
        api_path = Path(__file__).resolve().parent.parent / "api"
        if str(api_path) not in sys.path:
            sys.path.insert(0, str(api_path))
        
        module = importlib.import_module("LoCommAPI")
        return BackendBundle(
            backend=RealLoCommBackend(module),
            profile="locomm",
            label="LoCommAPI"
        )
    except (ImportError, ModuleNotFoundError) as exc:
        return BackendBundle(
            backend=DummyBackend(),
            profile="dummy",
            label="Deviceless (Dummy)",
            error=str(exc)
        )

