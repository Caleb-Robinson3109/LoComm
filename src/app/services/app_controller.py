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
from services.transport_contract import PairingContext
from utils.session import Session
from utils.design_system import AppConfig
from utils.connection_manager import get_connection_manager
from utils.status_manager import get_status_manager
from utils.app_logger import get_logger
from utils.runtime_settings import get_runtime_settings
from utils.mock_config import get_mock_config, set_mock_scenario
from utils.diagnostics import log_transport_event

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
            "local_device_name": getattr(session, "local_device_name", "This Device"),
            "paired_at": session.paired_at,
            "transport_profile": getattr(session, "transport_profile", "auto"),
            "mock_scenario": getattr(session, "mock_scenario", "default"),
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
        # CRITICAL FIX: Initialize local device name for proper message attribution
        self.session.local_device_name = "This Device"
        self.settings = get_runtime_settings()
        self.mock_config = get_mock_config()
        self.transport = LoCommTransport(ui_root, profile=self.settings.transport_profile)
        self.connection_manager = get_connection_manager()
        self.status_manager = get_status_manager()
        self.store = SessionStore()

        self._message_callbacks: List[MessageCallback] = []
        self._status_callbacks: List[StatusCallback] = []
        self._worker_lock = threading.Lock()

        # Log resolved transport profile for diagnostics
        resolved_profile = f"{self.transport.profile_label} ({self.transport.profile})"
        resolved_mode = "mock" if self.transport.is_mock else "hardware"
        self.logger.info("Transport profile: %s [%s]", resolved_profile, resolved_mode)
        if self.transport.backend_error:
            self.logger.warning("Transport fallback reason: %s", self.transport.backend_error)
        log_transport_event(
            "transport_profile",
            {
                "profile": self.transport.profile,
                "label": resolved_profile,
                "is_mock": self.transport.is_mock,
                "fallback_reason": self.transport.backend_error,
                "mock_scenario": self.mock_config.scenario,
            }
        )

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
        self.session.local_device_name = cached.get("local_device_name", "This Device")
        self.session.paired_at = cached.get("paired_at", 0.0)
        self.session.transport_profile = cached.get("transport_profile", "auto")
        self.session.mock_scenario = cached.get("mock_scenario", "default")

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
        # CRITICAL FIX: Use worker lock to prevent overlapping transport threads
        if not self._worker_lock.acquire(timeout=0.1):
            if callback:
                self.root.after(0, lambda: callback(False, "Connection already in progress"))
            return

        def finish(success: bool, error: Optional[str] = None) -> None:
            try:
                if success:
                    self.session.device_id = device_id
                    self.session.device_name = device_name
                    self.session.paired_at = time.time()
                    self.session.transport_profile = self.transport.profile
                    self.session.mock_scenario = self.mock_config.scenario
                    # CRITICAL FIX: Queue connection updates on main thread to prevent Tk violations
                    self.root.after(0, lambda: self._safe_connect_device(device_id, device_name))
                    self._persist_session()
                    log_transport_event("connect_success", {
                        "device_id": device_id,
                        "device_name": device_name,
                        "profile": self.transport.profile,
                        "scenario": self.mock_config.scenario,
                    })
                else:
                    # CRITICAL FIX: Stop transport first to prevent resource leaks
                    self.transport.stop()
                    # CRITICAL FIX: Queue disconnection updates on main thread
                    self.root.after(0, self._safe_disconnect_device)
                    self.session.clear()
                    self._persist_session()
                    log_transport_event("connect_failed", {
                        "device_id": device_id,
                        "device_name": device_name,
                        "profile": self.transport.profile,
                        "scenario": self.mock_config.scenario,
                        "error": error,
                    })

                if callback:
                    # CRITICAL FIX: Schedule callback on main thread
                    self.root.after(0, lambda cb=callback: cb(success, error))
            finally:
                # Always release the worker lock
                self._worker_lock.release()

        def worker():
            timeout_event = threading.Event()

            def timeout_handler():
                timeout_event.set()

            timer = threading.Timer(AppConfig.PAIR_DEVICES_TIMEOUT, timeout_handler)
            timer.start()

            try:
                pairing_context = PairingContext(
                    mode=mode,
                    device_id=device_id,
                    device_name=device_name,
                    metadata={
                        "requested_profile": self.settings.transport_profile,
                        "active_profile": self.transport.profile,
                        "scenario": self.mock_config.scenario,
                    }
                )
                self._emit_status(f"Connecting to {device_name} ({device_id})…")
                log_transport_event("connect_attempt", {
                    "device_id": device_id,
                    "device_name": device_name,
                    "mode": mode,
                    "profile": self.transport.profile,
                    "requested_profile": self.settings.transport_profile,
                    "scenario": self.mock_config.scenario,
                })
                self.logger.info("Connecting to %s (%s) via %s mode", device_name, device_id, mode)
                success = self.transport.start(pairing_context)

                if timeout_event.is_set():
                    self.logger.warning("Connection timeout for %s", device_id)
                    # CRITICAL FIX: Stop transport to prevent resource leaks on timeout
                    self.transport.stop()
                    log_transport_event("connect_timeout", {
                        "device_id": device_id,
                        "device_name": device_name,
                    })
                    finish(False, "Connection timeout. Please check device connection.")
                elif success:
                    finish(True, None)
                else:
                    finish(False, "Connection failed.")
            except Exception as exc:  # noqa: BLE001
                self.logger.exception("Transport connection error: %s", exc)
                # CRITICAL FIX: Stop transport on exceptions too
                try:
                    self.transport.stop()
                except Exception:
                    pass
                finish(False, f"Connection error: {exc}")
            finally:
                timer.cancel()

        threading.Thread(target=worker, daemon=True).start()

    def start_mock_session(self, device_id: str, device_name: str) -> bool:
        """Immediate connect path for mock devices to avoid extra threads."""
        pairing_context = PairingContext(
            mode="mock",
            device_id=device_id,
            device_name=device_name,
            metadata={
                "requested_profile": self.settings.transport_profile,
                "active_profile": self.transport.profile,
                "scenario": self.mock_config.scenario,
            }
        )
        try:
            success = self.transport.start(pairing_context)
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("Mock transport start failed: %s", exc)
            success = False

        self.logger.info("Mock session connection result: success=%s", success)
        if success:
            self.session.device_id = device_id
            self.session.device_name = device_name
            self.session.paired_at = time.time()
            self.session.transport_profile = self.transport.profile
            self.session.mock_scenario = self.mock_config.scenario
            self._safe_connect_device(device_id, device_name)
            self._persist_session()
            log_transport_event("connect_success", {
                "device_id": device_id,
                "device_name": device_name,
                "profile": self.transport.profile,
                "scenario": self.mock_config.scenario,
                "mode": "mock",
            })
            return True

        self.transport.stop()
        log_transport_event("connect_failed", {
            "device_id": device_id,
            "device_name": device_name,
            "profile": self.transport.profile,
            "scenario": self.mock_config.scenario,
            "mode": "mock",
        })
        return False

    def _safe_connect_device(self, device_id: str, device_name: str):
        """Thread-safe device connection."""
        try:
            self.connection_manager.connect_device(device_id, device_name)
        except Exception as exc:
            self.logger.exception("Safe connect device error: %s", exc)

    def _safe_disconnect_device(self):
        """Thread-safe device disconnection."""
        try:
            self.connection_manager.disconnect_device()
        except Exception as exc:
            self.logger.exception("Safe disconnect device error: %s", exc)

    def stop_session(self) -> None:
        """Disconnect transport and reset session state."""
        try:
            self.transport.stop()
        finally:
            self.connection_manager.disconnect_device()
            self.session.clear()
            self._persist_session()
            log_transport_event("disconnect", {"reason": "user"})
            self._emit_status("Disconnected")

    def set_mock_scenario(self, scenario: str) -> None:
        """Allow UI to change active mock scenario without restart."""
        self.mock_config = set_mock_scenario(scenario)
        self.session.mock_scenario = self.mock_config.scenario
        log_transport_event("scenario_change", {"scenario": self.mock_config.scenario})

    def send_message(self, message: str) -> None:
        # CRITICAL FIX: Use local device name instead of peer name for proper attribution
        sender = getattr(self.session, 'local_device_name', None) or "This Device"
        metadata = {
            "profile": self.session.transport_profile or self.transport.profile,
            "scenario": self.session.mock_scenario or self.mock_config.scenario,
        }
        log_transport_event("tx", {"sender": sender, "message": message, "metadata": metadata})
        self.transport.send(sender, message, metadata=metadata)

    # ------------------------------------------------------------------ #
    # Transport callbacks
    def _handle_transport_message(self, sender: str, msg: str, ts: float) -> None:
        log_transport_event("rx", {"sender": sender, "message": msg, "ts": ts})
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
        log_transport_event("status", {"text": status_text})

    def _emit_status(self, text: str):
        """Push status text through the consolidated status manager."""
        def dispatch():
            try:
                self.status_manager.update_status(text, self.session.device_name)
            except Exception:
                self.logger.exception("Status emit failed")
            else:
                log_transport_event("status", {"text": text, "source": "controller"})

        try:
            self.root.after(0, dispatch)
        except Exception:
            dispatch()
