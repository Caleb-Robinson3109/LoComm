"""
Runtime registry for transport backends.
Provides hot-swappable profiles so the UI can toggle between mock and real
implementations without code changes.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib
import os
import sys
from pathlib import Path
from typing import Callable, Dict, Optional, Protocol, Tuple

from services.transport_contract import PairingContext, TransportMessage
from mock.backend import MockLoCommBackend


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
    is_mock: bool
    error: Optional[str] = None


@dataclass
class TransportProfile:
    key: str
    label: str
    factory: Callable[[], TransportBackend]
    is_mock: bool = False
    description: str = ""


class RealLoCommBackend:
    """Thin adapter around the external LoCommAPI module."""

    label = "locomm-api"

    def __init__(self, api_module):
        self.api = api_module

    def connect(self, pairing_context: Optional[PairingContext] = None) -> bool:
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
    Resolve a backend profile. Supports "auto" which attempts the real backend
    before falling back to mock.
    """
    desired = (profile or get_default_profile()).lower()
    if desired == "auto":
        bundle, err = _try_profile("locomm")
        if bundle:
            return bundle
        mock_bundle, mock_err = _try_profile("mock")
        if mock_bundle:
            mock_bundle.error = err
            return mock_bundle
        reason = err or mock_err or "Unknown error"
        raise RuntimeError(f"No transport profiles available: {reason}")

    bundle, err = _try_profile(desired)
    if bundle:
        return bundle
    if err:
        raise RuntimeError(f"Transport profile '{desired}' failed: {err}")
    raise RuntimeError(f"Unknown transport profile '{desired}'")


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
            is_mock=profile.is_mock,
        ), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def _register_builtin_profiles() -> None:
    def _load_mock() -> TransportBackend:
        return MockLoCommBackend()

    register_profile(
        TransportProfile(
            key="mock",
            label="MockLoCommBackend",
            factory=_load_mock,
            is_mock=True,
            description="In-memory transport used for UI development and tests.",
        )
    )

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
            is_mock=False,
            description="Production transport provided by the hardware/network team.",
        )
    )


_register_builtin_profiles()
