"""
Transport orchestration service.
Handles threading, locking, and connection management for the transport layer.
"""
from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable

from services.lora_transport import LoCommTransport
from services.transport_contract import PairingContext
from ui.theme_tokens import AppConfig
from utils.app_logger import get_logger
from utils.diagnostics import log_transport_event

ResultCallback = Callable[[bool, str | None], None] | None


class TransportManager:
    """Manages transport connections and background tasks using ThreadPoolExecutor."""

    def __init__(self, transport: LoCommTransport, ui_root):
        self.transport = transport
        self.root = ui_root
        self.logger = get_logger()
        # Executor for connection tasks (serialized)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="TransportWorker")
        self._current_future: Future | None = None

    def start_connection(self, 
                        device_id: str, 
                        device_name: str, 
                        mode: str, 
                        profile: str,
                        on_complete: ResultCallback) -> None:
        """
        Start a connection attempt in a background thread.
        
        Args:
            device_id: Target device ID
            device_name: Target device name
            mode: Connection mode (e.g., "pin")
            profile: Requested transport profile
            on_complete: Callback(success, error_msg) invoked on main thread
        """
        # Check if a connection attempt is already in progress
        if self._current_future and not self._current_future.done():
            if on_complete:
                self.root.after(0, lambda: on_complete(False, "Connection already in progress"))
            return

        self._current_future = self._executor.submit(
            self._connection_worker, 
            device_id, 
            device_name, 
            mode, 
            profile, 
            on_complete
        )

    def _connection_worker(self, 
                          device_id: str, 
                          device_name: str, 
                          mode: str, 
                          profile: str, 
                          on_complete: ResultCallback):
        """Background worker for connection logic."""
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
                    "requested_profile": profile,
                    "active_profile": self.transport.profile,
                }
            )
            
            log_transport_event("connect_attempt", {
                "device_id": device_id,
                "device_name": device_name,
                "mode": mode,
                "profile": self.transport.profile,
            })
            
            self.logger.info("Connecting to %s (%s) via %s mode", device_name, device_id, mode)
            success = self.transport.start(pairing_context)

            if timeout_event.is_set():
                self.logger.warning("Connection timeout for %s", device_id)
                self.transport.stop()
                self._finish(on_complete, False, "Connection timeout. Please check device connection.")
            elif success:
                self._finish(on_complete, True, None)
            else:
                self._finish(on_complete, False, "Connection failed.")
        except Exception as exc:
            self.logger.exception("Transport connection error: %s", exc)
            try:
                self.transport.stop()
            except Exception:
                pass
            self._finish(on_complete, False, f"Connection error: {exc}")
        finally:
            timer.cancel()

    def _finish(self, callback: ResultCallback, success: bool, error: str | None) -> None:
        """Helper to schedule callback on main thread."""
        if callback:
            self.root.after(0, lambda: callback(success, error))

    def stop(self) -> None:
        """Stop the transport."""
        self.transport.stop()
        # Optionally cancel pending futures if we wanted to be aggressive
        # if self._current_future:
        #     self._current_future.cancel()

    def send(self, sender: str, message: str, metadata: dict = None) -> None:
        """Send a message via transport."""
        # Sending is currently synchronous in the transport layer or handles its own threading?
        # LoCommTransport.send calls backend.send. 
        # If backend.send is blocking, we should probably offload it too.
        # For now, keeping it as is to match previous behavior, but could be improved.
        self.transport.send(sender, message, metadata=metadata)

    def shutdown(self):
        """Cleanup resources."""
        self._executor.shutdown(wait=False)
