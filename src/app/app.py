"""
LoRa Chat Desktop Application - Optimized Version
Main application class providing unified interface and device communication.
"""
import tkinter as tk
from tkinter import messagebox
import threading
import time

from lora_transport_locomm import LoCommTransport
from utils.session import Session
from utils.status_manager import get_status_manager
from pages.pin_pairing_frame import PINPairingFrame
from pages.main_frame import MainFrame
from utils.design_system import AppConfig, ensure_styles_initialized
from utils.connection_manager import get_connection_manager


class App(tk.Tk):
    """LoRa Chat Desktop Application with enhanced UI and connectivity."""

    def __init__(self):
        super().__init__()
        ensure_styles_initialized()
        self.title(AppConfig.APP_TITLE)
        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.minsize(AppConfig.WINDOW_WIDTH - 200, AppConfig.WINDOW_HEIGHT - 100)
        self.resizable(True, True)

        # Initialize core components
        self.session = Session()
        self.connection_manager = get_connection_manager()
        self.transport = LoCommTransport(self)
        self.transport.on_receive = self._on_receive
        self.transport.on_status = self._on_status

        # Message handling
        self._pending_messages = []
        self._current_peer = ""
        self._last_status = "Disconnected"

        # Status management
        self.status_manager = get_status_manager()
        self.status_manager.register_status_callback(self._on_status_update)

        # Initialize UI
        self.current_frame = None
        self.show_main()

    def show_main(self, device_id=None, device_name=None):
        """Show the main chat interface."""
        if self.current_frame:
            self.current_frame.destroy()

        # Update session data
        if device_id and device_name:
            self.session.device_name = device_name
            self.session.device_id = device_id
            self.session.paired_at = time.time()

        # Create main frame
        self.current_frame = MainFrame(self, self, self.session, self.transport, self._handle_logout)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        if hasattr(self.current_frame, "chat_page"):
            self.current_frame.chat_page.sync_session_info()

        # Update status if available
        if self._last_status:
            self.current_frame.update_status(self._last_status)

        # Process pending messages
        if self._pending_messages:
            for sender, msg, ts in self._pending_messages:
                display_name = sender or "Peer"
                self.current_frame.chat_page.append_line(display_name, msg)
                if sender:
                    self._current_peer = sender
            self._pending_messages.clear()

    def show_login(self):
        """Show the PIN pairing screen."""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = PINPairingFrame(self, self._handle_pair_success, self._handle_demo_login)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def start_transport_session(self, device_id: str, device_name: str, *, mode: str = "pin",
                                failure_title: str = "Pairing Failed",
                                failure_message: str = "Connection failed.") -> None:
        """Kick off the background workflow to connect to a device."""

        def finish_session(success: bool, error_msg: str = ""):
            if success:
                self.connection_manager.connect_device(device_id, device_name)
                self.show_main(device_id, device_name)
            else:
                self.connection_manager.disconnect_device()
                messagebox.showerror(failure_title, error_msg or failure_message)
                self._clear_session()

        def worker():
            try:
                def timeout_handler():
                    raise TimeoutError("Connection timeout")

                timeout_timer = threading.Timer(AppConfig.PAIR_DEVICES_TIMEOUT, timeout_handler)
                timeout_timer.start()

                try:
                    pairing_context = {
                        "mode": mode,
                        "device_id": device_id,
                        "device_name": device_name,
                    }
                    ok = self.transport.start(pairing_context)
                    timeout_timer.cancel()
                    self.after(0, lambda: finish_session(ok))
                except TimeoutError:
                    timeout_timer.cancel()
                    self.after(0, lambda: finish_session(False, "Connection timeout. Please check device connection."))
                except Exception as exc:
                    timeout_timer.cancel()
                    self.after(0, lambda: finish_session(False, f"Connection error: {str(exc)}"))
            except Exception as exc:
                self.after(0, lambda: finish_session(False, f"Unexpected error: {str(exc)}"))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_pair_success(self, device_id: str, device_name: str):
        """Handle successful PIN pairing with timeout protection."""
        self.start_transport_session(device_id, device_name)

    def _handle_demo_login(self):
        """Handle demo login (skip PIN pairing)."""
        self.start_transport_session(
            "demo-device",
            "Demo Device",
            mode="demo",
            failure_title="Demo Failed",
            failure_message="Demo connection failed."
        )

    def _handle_logout(self):
        """Handle user logout with proper cleanup."""
        self.transport.stop()
        self._clear_session()
        self._pending_messages.clear()
        self._last_status = "Disconnected"
        self._current_peer = ""
        self.connection_manager.disconnect_device()
        self.show_main()

    def _clear_session(self):
        """Clear session data safely."""
        self.session.clear()

    def _on_receive(self, sender: str, msg: str, ts: float):
        """Handle incoming messages with thread-safe UI updates."""
        if isinstance(self.current_frame, MainFrame):
            display_name = sender or "Peer"
            self.current_frame.chat_page.append_line(display_name, msg)
        else:
            self._pending_messages.append((sender, msg, ts))

        if sender:
            self._current_peer = sender

        if sender and sender != (self.session.device_name or ""):
            self.notify_incoming_message(sender, msg)

    def _on_status(self, text: str):
        """Handle status updates from transport with peer tracking."""
        status_lower = text.lower()

        # Update peer tracking
        if any(keyword in status_lower for keyword in ("disconnected", "connection failed", "invalid pairing code")):
            self._current_peer = ""
        elif any(keyword in status_lower for keyword in ("connected (mock)", "ready")):
            if not self._current_peer:
                self._current_peer = "Awaiting peer"

        # Update UI
        if isinstance(self.current_frame, MainFrame):
            self.current_frame.update_status(text)

        self._last_status = text

    def _on_status_update(self, status_text: str, color: str):
        """Handle centralized status updates."""
        if isinstance(self.current_frame, MainFrame):
            self.current_frame.update_status(status_text)

    def notify_incoming_message(self, sender: str, msg: str):
        """Notify user of incoming messages."""
        self.bell()
        self.after(AppConfig.STATUS_UPDATE_DELAY_SHORT,
                  lambda: self._on_status(self.status_manager.get_current_status()))

    def clear_chat_history(self):
        """Clear chat history with user confirmation."""
        if isinstance(self.current_frame, MainFrame):
            if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the current chat log?"):
                self.current_frame.chat_page.clear_history()


if __name__ == "__main__":
    App().mainloop()
