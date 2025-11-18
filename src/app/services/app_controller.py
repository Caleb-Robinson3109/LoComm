"""
Centralized controller that coordinates transport, session state, and persistence.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Callable, List, Optional

from services.lora_transport import LoCommTransport
from services.transport_contract import PairingContext
from services.session_service import SessionService
from services.transport_manager import TransportManager
from utils.state.session import Session
from ui.theme_tokens import AppConfig
from utils.state.connection_manager import get_connection_manager
from utils.state.status_manager import get_status_manager
from utils.app_logger import get_logger
from utils.runtime_settings import get_runtime_settings
from utils.diagnostics import log_transport_event
MessageCallback = Callable[[str, str, float], None]
ResultCallback = Callable[[bool, str | None], None] | None


class AppController:
    """Coordinates transport operations and exposes events to the UI."""

    def __init__(self, ui_root):
        self.root = ui_root
        self.logger = get_logger()
        self.session = Session()
        # Initialize local device name for proper message attribution
        self.session.local_device_name = "Orion"
        self.settings = get_runtime_settings()
        
        # Initialize services
        self.transport_layer = LoCommTransport(ui_root, profile=self.settings.transport_profile)
        self.transport_manager = TransportManager(self.transport_layer, ui_root)
        self.session_service = SessionService()
        self.connection_manager = get_connection_manager()
        self.status_manager = get_status_manager()

        self._message_callbacks: List[MessageCallback] = []

        # Log resolved transport profile for diagnostics
        resolved_profile = f"{self.transport_layer.profile_label} ({self.transport_layer.profile})"
        self.logger.info("Transport profile: %s [hardware]", resolved_profile)
        if self.transport_layer.backend_error:
            self.logger.warning("Transport fallback reason: %s", self.transport_layer.backend_error)
        log_transport_event(
            "transport_profile",
            {
                "profile": self.transport_layer.profile,
                "label": resolved_profile,
                "fallback_reason": self.transport_layer.backend_error,
            }
        )

        # Wire transport callbacks
        self.transport_layer.on_receive = self._handle_transport_message
        self.transport_layer.on_status = self._handle_transport_status

        # Restore last session metadata (not an auto-reconnect)
        self._hydrate_session()

    @property
    def transport(self):
        """Backward compatibility accessor for transport layer."""
        return self.transport_layer

    # ------------------------------------------------------------------ #
    # Persistence helpers
    def _hydrate_session(self) -> None:
        self.session_service.hydrate_session(self.session)

    def _persist_session(self) -> None:
        if self.session.device_id and self.session.device_name:
            self.session_service.save(self.session)
        else:
            self.session_service.clear()

    # ------------------------------------------------------------------ #
    # Event registration
    def register_message_callback(self, callback: MessageCallback) -> None:
        self._message_callbacks.append(callback)

    # ------------------------------------------------------------------ #
    # Transport orchestration
    def start_session(self, device_id: str, device_name: str, *,
                      mode: str = "pin", callback: ResultCallback = None) -> None:
        """
        Start the transport asynchronously and notify caller on completion.
        """
        def on_complete(success: bool, error: str | None = None):
            if success:
                self.session.device_id = device_id
                self.session.device_name = device_name
                self.session.paired_at = time.time()
                self.session.transport_profile = self.transport_layer.profile
                self._safe_connect_device(device_id, device_name)
                self._persist_session()
                log_transport_event("connect_success", {
                    "device_id": device_id,
                    "device_name": device_name,
                    "profile": self.transport_layer.profile,
                    "mode": mode,
                })
            else:
                self._safe_disconnect_device()
                self.session.clear()
                self._persist_session()
                log_transport_event("connect_failed", {
                    "device_id": device_id,
                    "device_name": device_name,
                    "profile": self.transport_layer.profile,
                    "error": error,
                })
            
            if callback:
                callback(success, error)

        self.transport_manager.start_connection(
            device_id=device_id,
            device_name=device_name,
            mode=mode,
            profile=self.settings.transport_profile,
            on_complete=on_complete
        )

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
            self.transport_manager.stop()
        finally:
            self.connection_manager.disconnect_device()
            self.session.clear()
            self._persist_session()
            log_transport_event("disconnect", {"reason": "user"})
            self._emit_status("Disconnected")

    def send_message(self, message: str) -> None:
        sender = getattr(self.session, 'local_device_name', None) or "Orion"
        metadata = {
            "profile": self.session.transport_profile or self.transport_layer.profile,
        }
        log_transport_event("tx", {"sender": sender, "message": message, "metadata": metadata})
        self.transport_manager.send(sender, message, metadata=metadata)

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
