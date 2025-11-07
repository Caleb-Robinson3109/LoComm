"""
LoRa transport adapter for GUI communication.
Provides unified interface for real and mock implementations.
"""
from __future__ import annotations

import importlib
import os
import sys
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple

from mock_transport_backend import MockLoCommBackend

DEBUG = False  # Set to True for debug output


from abc import ABC, abstractmethod
from typing import Protocol

@dataclass
class BackendBundle:
    backend: Any
    label: str
    is_mock: bool
    error: Optional[str] = None

class TransportBackend(Protocol):
    """Protocol defining the common interface for transport backends."""

    def connect(self, pairing_context: Optional[dict] = None) -> bool: ...
    def disconnect(self) -> bool: ...
    def send(self, sender: str, message: str) -> bool: ...
    def receive(self) -> tuple[str, str]: ...
    def start_pairing(self) -> bool: ...
    def stop_pairing(self) -> bool: ...


class RealLoCommBackend:
    """Thin wrapper around the external LoCommAPI module."""

    label = "locomm-api"

    def __init__(self, api_module: Any):
        self.api = api_module

    def connect(self, pairing_context: Optional[dict] = None) -> bool:
        connect_fn = getattr(self.api, "connect_to_device", None)
        if not connect_fn:
            return False
        return bool(connect_fn())

    def disconnect(self) -> bool:
        disconnect_fn = getattr(self.api, "disconnect_from_device", None)
        if disconnect_fn:
            return bool(disconnect_fn())
        return False

    def send(self, sender: str, message: str) -> bool:
        send_fn = getattr(self.api, "send_message", None)
        if send_fn:
            return bool(send_fn(sender, message))
        return False

    def receive(self) -> Tuple[str, str]:
        receive_fn = getattr(self.api, "receive_message", None)
        if receive_fn:
            return receive_fn()
        return ("", "")

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


def _load_backend() -> BackendBundle:
    """Attempt to load the real backend, falling back to the mock implementation."""
    api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api"))
    if api_path not in sys.path:
        sys.path.insert(0, api_path)

    try:
        module = importlib.import_module("LoCommAPI")
        if DEBUG:
            print(f"[LoRaTransport] Loaded LoCommAPI backend from {api_path}")
        return BackendBundle(RealLoCommBackend(module), "LoCommAPI", False)
    except Exception as exc:  # noqa: BLE001 - we want a broad fallback
        if DEBUG:
            print(f"[LoRaTransport] Falling back to mock backend: {exc!r}")
        return BackendBundle(MockLoCommBackend(), "MockLoCommBackend", True, str(exc))


class LoCommTransport:
    """Transport adapter for LoRa communication with unified interface."""

    def __init__(self, ui_root: tk.Misc):
        self.root = ui_root
        self.on_receive: Optional[Callable[[str, str, float], None]] = None
        self.on_status: Optional[Callable[[str], None]] = None
        self.running = False
        self._rx_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        backend_bundle = _load_backend()
        self._backend = backend_bundle.backend
        self._backend_label = backend_bundle.label
        self._is_mock = backend_bundle.is_mock

    def start(self, pairing_context: Optional[dict] = None) -> bool:
        """Connect to a device using the supplied pairing context."""
        try:
            if DEBUG:
                print(f"[LoRaTransport] Starting connection via {self._backend_label}")

            success = self._backend.connect(pairing_context)
            if not success:
                if self.on_status:
                    self.on_status("Connection failed")
                return False

            self.running = True
            self._start_rx_thread()

            status_text = "Connected"
            if pairing_context and pairing_context.get("mode") == "demo":
                status_text = "Connected (demo mode)"
            elif self._is_mock:
                status_text = "Connected (mock backend)"

            if self.on_status:
                self.on_status(status_text)
            return True

        except Exception as exc:  # noqa: BLE001
            if DEBUG:
                print(f"[LoRaTransport] Connection error: {exc!r}")
            if self.on_status:
                self.on_status(f"Connection error: {exc}")
            return False

    def _start_rx_thread(self) -> None:
        """Start background receive thread."""
        self._stop_event.clear()
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        self._rx_thread.start()

    def stop(self) -> None:
        """Stop communication and disconnect device."""
        self.running = False
        self._stop_event.set()

        try:
            self._backend.disconnect()
        except Exception as exc:  # noqa: BLE001
            if DEBUG:
                print(f"[LoRaTransport] Disconnect error: {exc!r}")

        if self.on_status:
            self.on_status("Disconnected")

    def send(self, name: str, text: str) -> None:
        """Send message to connected device."""
        if not self.running:
            if self.on_status:
                self.on_status("Not connected")
            return

        try:
            success = self._backend.send(name, text)
            if not success and self.on_status:
                self.on_status("Send failed")
        except Exception as exc:  # noqa: BLE001
            if DEBUG:
                print(f"[LoRaTransport] Send error: {exc!r}")
            if self.on_status:
                self.on_status("Send error")

    def pair_devices(self) -> bool:
        """Start device pairing."""
        try:
            return bool(self._backend.start_pairing())
        except Exception as exc:  # noqa: BLE001
            if DEBUG:
                print(f"[LoRaTransport] Pairing error: {exc!r}")
        return False

    def stop_pairing(self) -> bool:
        """Stop device pairing."""
        try:
            return bool(self._backend.stop_pairing())
        except Exception as exc:  # noqa: BLE001
            if DEBUG:
                print(f"[LoRaTransport] Stop pairing error: {exc!r}")
        return False

    def _rx_loop(self) -> None:
        """Background receive loop for incoming messages."""
        while not self._stop_event.is_set():
            try:
                sender, msg = self._backend.receive()
                if sender and msg and self.on_receive:
                    timestamp = time.time()
                    # Ensure callback is callable before calling
                    callback = self.on_receive
                    if callback:
                        self.root.after(0, lambda s=sender, m=msg, ts=timestamp: callback(s, m, ts))
            except Exception as exc:  # noqa: BLE001
                if DEBUG:
                    print(f"[LoRaTransport] Receive error: {exc!r}")

            time.sleep(0.2)
