"""
Runtime registry for transport backends.
Provides a registry so transports can be resolved dynamically.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib
import os
import sys
from pathlib import Path
from typing import Callable, Dict, Optional, Protocol, Tuple

from services.transport_contract import PairingContext, TransportMessage


class TransportBackend(Protocol):
    """Protocol defining the required interface for transport backends."""

    def connect(self, pairing_context: Optional[PairingContext] = None) -> bool: ...

    def disconnect(self) -> bool: ...

    def send(self, message: TransportMessage) -> bool: ...

    def receive(self) -> Optional[TransportMessage]: ...

    def start_pairing(self) -> bool: ...

    def stop_pairing(self) -> bool: ...


@dataclass
class BackendBundle:
    backend: TransportBackend
    profile: str
    label: str
    error: Optional[str] = None


@dataclass
class TransportProfile:
    key: str
    label: str
    factory: Callable[[], TransportBackend]
    description: str = ""


class RealLoCommBackend:
    """Thin adapter around the external LoCommAPI module."""

    label = "locomm-api"

    def __init__(self, api_module):
        self.api = api_module
        self._globals = getattr(api_module, "LoCommGlobals", None)
        self._connected = False

    def connect(self, pairing_context: Optional[PairingContext] = None) -> bool:
        # Avoid redundant reconnects if already connected
        if self._connected:
            return True
        if self._globals is not None and getattr(self._globals, "connected", False):
            # If API already has an active connection, reuse it
            self._connected = True
            return True
        connect_fn = getattr(self.api, "connect_to_device", None)
        if not connect_fn:
            return False
        ok = bool(connect_fn())
        self._connected = ok
        return ok

    def disconnect(self) -> bool:
        disconnect_fn = getattr(self.api, "disconnect_from_device", None)
        self._connected = False
        if disconnect_fn:
            return bool(disconnect_fn())
        return False

    def send(self, message: TransportMessage) -> bool:
        send_fn = getattr(self.api, "send_message", None)
        if send_fn:
            # LoCommAPI expects sender_name, receiver_id, message
            try:
                return bool(send_fn(message.sender, 255, message.payload))
            except TypeError:
                # Fallback in case signature differs
                return bool(send_fn(message.sender, message.payload))
        return False

    def receive(self) -> Optional[TransportMessage]:
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


_REGISTRY: Dict[str, TransportProfile] = {}


def register_profile(profile: TransportProfile) -> None:
    _REGISTRY[profile.key] = profile


def list_profiles() -> Dict[str, TransportProfile]:
    return dict(_REGISTRY)


def get_default_profile() -> str:
    return os.environ.get("LOCOMM_TRANSPORT_PROFILE", "auto")


def resolve_backend(profile: Optional[str] = None) -> BackendBundle:
    """
    Resolve a backend profile. "auto" simply maps to the production backend.
    """
    desired = (profile or get_default_profile()).lower()
    if desired == "auto":
        desired = "locomm"

    bundle, err = _try_profile(desired)
    if bundle:
        return bundle
    reason = err or f"Unknown transport profile '{desired}'"
    raise RuntimeError(f"No transport profiles available: {reason}")


def _try_profile(profile_key: str) -> Tuple[Optional[BackendBundle], Optional[str]]:
    profile = _REGISTRY.get(profile_key)
    if not profile:
        return None, f"Profile '{profile_key}' is not registered"
    try:
        backend = profile.factory()
        return BackendBundle(
            backend=backend,
            profile=profile.key,
            label=profile.label,
        ), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def _register_builtin_profiles() -> None:
    def _load_real() -> TransportBackend:
        api_path = Path(__file__).resolve().parent.parent / "api"
        if str(api_path) not in sys.path:
            sys.path.insert(0, str(api_path))
        module = importlib.import_module("LoCommAPI")
        return RealLoCommBackend(module)

    register_profile(
        TransportProfile(
            key="locomm",
            label="LoCommAPI",
            factory=_load_real,
            description="Production transport provided by the hardware/network team.",
        )
    )


_register_builtin_profiles()
