"""
LoRa transport adapter for GUI communication.
Provides unified interface for real and mock implementations.
"""
from __future__ import annotations

import threading
import time
import tkinter as tk
from typing import Callable, Optional

from services.transport_contract import PairingContext, TransportMessage
from services.transport_registry import BackendBundle, resolve_backend

DEBUG = False  # Set to True for debug output


class LoCommTransport:
    """Transport adapter for LoRa communication with unified interface."""

    def __init__(self, ui_root: tk.Misc, profile: str | None = None):
        self.root = ui_root
        self.on_receive: Optional[Callable[[str, str, float], None]] = None
        self.on_status: Optional[Callable[[str], None]] = None
        self.running = False
        self._rx_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        backend_bundle = resolve_backend(profile)
        self._backend = backend_bundle.backend
        self._backend_label = backend_bundle.label
        self._profile_key = backend_bundle.profile
        self._is_mock = backend_bundle.is_mock
        self._backend_error = backend_bundle.error

    @property
    def profile(self) -> str:
        return self._profile_key

    @property
    def profile_label(self) -> str:
        return self._backend_label

    @property
    def is_mock(self) -> bool:
        return self._is_mock

    @property
    def backend_error(self) -> Optional[str]:
        return self._backend_error

    def start(self, pairing_context: Optional[PairingContext | dict] = None) -> bool:
        """Connect to a device using the supplied pairing context."""
        current_thread_id = threading.get_ident()
        main_thread_id = threading.main_thread().ident
        print(f"[LoRaTransport] start() called from thread {current_thread_id} (main={current_thread_id == main_thread_id})")

        try:
            if DEBUG:
                print(f"[LoRaTransport] Starting connection via {self._backend_label}")

            raw_mode = None
            if isinstance(pairing_context, PairingContext):
                raw_mode = pairing_context.mode
            elif isinstance(pairing_context, dict):
                raw_mode = pairing_context.get("mode")

            normalized_context = self._normalize_pairing_context(pairing_context)
            success = self._backend.connect(normalized_context)
            if not success:
                if self.on_status:
                    # CRITICAL FIX: Queue status callbacks on main thread to prevent Tk violations
                    status_msg = "Connection failed"
                    self.root.after(0, lambda: self._safe_status_callback(status_msg))
                return False

            self.running = True
            self._start_rx_thread()

            status_text = "Connected"
            if raw_mode == "demo":
                status_text = "Connected (demo mode)"

            if self.on_status:
                # CRITICAL FIX: Queue status callbacks on main thread to prevent Tk violations
                self.root.after(0, lambda: self._safe_status_callback(status_text))
            return True

        except Exception as exc:  # noqa: BLE001
            print(f"[LoRaTransport] Connection error: {exc!r}")
            if self.on_status:
                # CRITICAL FIX: Queue status callbacks on main thread to prevent Tk violations
                message = f"Connection error: {exc}"
                self.root.after(0, lambda text=message: self._safe_status_callback(text))
            return False

    def _safe_status_callback(self, status_text: str):
        """Thread-safe status callback wrapper."""
        try:
            if self.on_status:
                self.on_status(status_text)
        except Exception as exc:
            if DEBUG:
                print(f"[LoRaTransport] Status callback error: {exc!r}")

    def _start_rx_thread(self) -> None:
        """Start background receive thread."""
        self._stop_event.clear()
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        self._rx_thread.start()

    def stop(self) -> None:
        """Stop communication and disconnect device."""
        stop_thread_id = threading.get_ident()
        print(f"[LoRaTransport] stop() called from thread {stop_thread_id}")

        self.running = False
        self._stop_event.set()

        try:
            self._backend.disconnect()
        except Exception as exc:  # noqa: BLE001
            if DEBUG:
                print(f"[LoRaTransport] Disconnect error: {exc!r}")

        if self.on_status:
            # CRITICAL FIX: Queue status callbacks on main thread to prevent Tk violations
            self.root.after(0, lambda: self._safe_status_callback("Disconnected"))

    def send(self, name: str, text: str, metadata: Optional[dict] = None) -> None:
        """Send message to connected device."""
        if not self.running:
            if self.on_status:
                self.on_status("Not connected")
            return

        message = TransportMessage(sender=name, payload=text, metadata=metadata or {})
        try:
            success = self._backend.send(message)
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
        rx_thread_id = threading.get_ident()
        print(f"[LoRaTransport] _rx_loop started on thread {rx_thread_id}")

        while not self._stop_event.is_set():
            try:
                message = self._backend.receive()
                if message and self.on_receive:
                    timestamp = time.time()
                    # Ensure callback is callable before calling
                    callback = self.on_receive
                    if callback:
                        print(f"[LoRaTransport] Scheduling receive callback on main thread from thread {rx_thread_id}")
                        self.root.after(
                            0,
                            lambda m=message, ts=timestamp: callback(m.sender, m.payload, ts)
                        )
            except Exception as exc:  # noqa: BLE001
                if DEBUG:
                    print(f"[LoRaTransport] Receive error: {exc!r}")

            time.sleep(0.2)

        print(f"[LoRaTransport] _rx_loop ending on thread {rx_thread_id}")

    def _normalize_pairing_context(self, context: Optional[PairingContext | dict]) -> Optional[PairingContext]:
        if context is None:
            return None
        if isinstance(context, PairingContext):
            return context
        return PairingContext(
            device_id=context.get("device_id", ""),
            device_name=context.get("device_name", ""),
            mode=context.get("mode", "pin"),
            metadata=context.get("metadata") or {},
        )
