"""
Centralized controller that coordinates transport, session state, and persistence.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Callable, List, Optional

from lora_transport_locomm import LoCommTransport
from utils.session import Session
from utils.design_system import AppConfig
from utils.connection_manager import get_connection_manager
from utils.status_manager import get_status_manager
from utils.app_logger import get_logger

MessageCallback = Callable[[str, str, float], None]
StatusCallback = Callable[[str], None]
ResultCallback = Optional[Callable[[bool, Optional[str]], None]]


class SessionStore:
    """Persist the most recent successful pairing."""

    def __init__(self):
        self.base_dir = Path.home() / ".locomm"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.base_dir / "session.json"

    def load(self) -> Optional[dict]:
        if not self.path.exists():
            return None
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError):
            return None

    def save(self, session: Session) -> None:
        data = {
            "device_id": session.device_id,
            "device_name": session.device_name,
            "paired_at": session.paired_at,
        }
        try:
            with self.path.open("w", encoding="utf-8") as handle:
                json.dump(data, handle)
        except OSError:
            pass

    def clear(self) -> None:
        try:
            if self.path.exists():
                self.path.unlink()
        except OSError:
            pass


class AppController:
    """Coordinates transport operations and exposes events to the UI."""

    def __init__(self, ui_root):
        self.root = ui_root
        self.logger = get_logger()
        self.session = Session()
        self.transport = LoCommTransport(ui_root)
        self.connection_manager = get_connection_manager()
        self.status_manager = get_status_manager()
        self.store = SessionStore()

        self._message_callbacks: List[MessageCallback] = []
        self._status_callbacks: List[StatusCallback] = []
        self._worker_lock = threading.Lock()

        # Wire transport callbacks
        self.transport.on_receive = self._handle_transport_message
        self.transport.on_status = self._handle_transport_status

        # Restore last session metadata (not an auto-reconnect)
        self._hydrate_session_from_store()

    # ------------------------------------------------------------------ #
    # Persistence helpers
    def _hydrate_session_from_store(self) -> None:
        cached = self.store.load()
        if not cached:
            return
        self.session.device_id = cached.get("device_id", "")
        self.session.device_name = cached.get("device_name", "")
        self.session.paired_at = cached.get("paired_at", 0.0)

    def _persist_session(self) -> None:
        if self.session.device_id and self.session.device_name:
            self.store.save(self.session)
        else:
            self.store.clear()

    # ------------------------------------------------------------------ #
    # Event registration
    def register_message_callback(self, callback: MessageCallback) -> None:
        self._message_callbacks.append(callback)

    def register_status_callback(self, callback: StatusCallback) -> None:
        self._status_callbacks.append(callback)

    # ------------------------------------------------------------------ #
    # Transport orchestration
    def start_session(self, device_id: str, device_name: str, *,
                      mode: str = "pin", callback: ResultCallback = None) -> None:
        """
        Start the transport asynchronously and notify caller on completion.

        Args:
            device_id: Remote device identifier.
            device_name: Friendly name for display.
            mode: Connection mode ("pin" or "demo").
            callback: Optional completion handler receiving (success, error_message).
        """

        def finish(success: bool, error: Optional[str] = None) -> None:
            if success:
                self.session.device_id = device_id
                self.session.device_name = device_name
                self.session.paired_at = time.time()
                self.connection_manager.connect_device(device_id, device_name)
                self._persist_session()
            else:
                self.connection_manager.disconnect_device()
                self.session.clear()
                self._persist_session()

            if callback:
                self.root.after(0, lambda: callback(success, error))

        def worker():
            timeout_event = threading.Event()

            def timeout_handler():
                timeout_event.set()

            timer = threading.Timer(AppConfig.PAIR_DEVICES_TIMEOUT, timeout_handler)
            timer.start()

            try:
                pairing_context = {
                    "mode": mode,
                    "device_id": device_id,
                    "device_name": device_name,
                }
                self.logger.info("Connecting to %s (%s) via %s mode", device_name, device_id, mode)
                success = self.transport.start(pairing_context)

                if timeout_event.is_set():
                    self.logger.warning("Connection timeout for %s", device_id)
                    finish(False, "Connection timeout. Please check device connection.")
                elif success:
                    finish(True, None)
                else:
                    finish(False, "Connection failed.")
            except Exception as exc:  # noqa: BLE001
                self.logger.exception("Transport connection error: %s", exc)
                finish(False, f"Connection error: {exc}")
            finally:
                timer.cancel()

        threading.Thread(target=worker, daemon=True).start()

    def stop_session(self) -> None:
        """Disconnect transport and reset session state."""
        try:
            self.transport.stop()
        finally:
            self.connection_manager.disconnect_device()
            self.session.clear()
            self._persist_session()

    def send_message(self, message: str) -> None:
        sender = self.session.device_name or "This Device"
        self.transport.send(sender, message)

    # ------------------------------------------------------------------ #
    # Transport callbacks
    def _handle_transport_message(self, sender: str, msg: str, ts: float) -> None:
        for callback in self._message_callbacks:
            try:
                callback(sender, msg, ts)
            except Exception:
                self.logger.exception("Message callback failed")

    def _handle_transport_status(self, status_text: str) -> None:
        self.status_manager.update_status(status_text, self.session.device_name)
        for callback in self._status_callbacks:
            try:
                callback(status_text)
            except Exception:
                self.logger.exception("Status callback failed")
