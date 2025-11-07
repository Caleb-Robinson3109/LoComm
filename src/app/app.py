"""
LoRa Chat Desktop Application - orchestrates UI frames and controller.
"""
import tkinter as tk
from tkinter import messagebox
import time

from services import AppController
from utils.status_manager import get_status_manager
from pages.pin_pairing_frame import PINPairingFrame
from pages.main_frame import MainFrame
from utils.design_system import AppConfig, ensure_styles_initialized


class App(tk.Tk):
    """LoRa Chat Desktop Application with enhanced UI and connectivity."""

    def __init__(self):
        super().__init__()
        ensure_styles_initialized()
        self.title(AppConfig.APP_TITLE)
        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.minsize(AppConfig.MIN_WINDOW_WIDTH, AppConfig.MIN_WINDOW_HEIGHT)
        self.resizable(True, True)

        # Initialize controller + state
        self.controller = AppController(self)
        self.session = self.controller.session

        # Message handling
        self._pending_messages = []
        self._current_peer = ""
        self._last_status = "Disconnected"

        # Status management
        self.status_manager = get_status_manager()
        self.status_manager.register_status_callback(self._on_status_update)
        self.controller.register_message_callback(self._handle_incoming_message)
        self.controller.register_status_callback(self._handle_status_text)

        # Initialize UI
        self.current_frame = None
        self.show_main()

    # ------------------------------------------------------------------ #
    def show_main(self, device_id: str | None = None, device_name: str | None = None):
        """Show the main chat interface."""
        if self.current_frame:
            self.current_frame.destroy()

        # Update session data if we just paired
        if device_id and device_name:
            self.session.device_name = device_name
            self.session.device_id = device_id
            self.session.paired_at = time.time()

        # Create main frame
        self.current_frame = MainFrame(self, self, self.session, self.controller, self._handle_logout)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        if hasattr(self.current_frame, "chat_page"):
            self.current_frame.chat_page.sync_session_info()

        # Update status if available
        if self._last_status:
            self.current_frame.update_status(self._last_status)

        # Process pending messages
        if self._pending_messages:
            for sender, msg, _ in self._pending_messages:
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

    # ------------------------------------------------------------------ #
    def start_transport_session(self, device_id: str, device_name: str, *, mode: str = "pin",
                                failure_title: str = "Pairing Failed",
                                failure_message: str = "Connection failed.") -> None:
        """Kick off the controller workflow to connect to a device."""

        def on_complete(success: bool, error_msg: str | None):
            if success:
                self.show_main(device_id, device_name)
            else:
                messagebox.showerror(failure_title, error_msg or failure_message)
                self._clear_session()

        self.controller.start_session(device_id, device_name, mode=mode, callback=on_complete)

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
        self.controller.stop_session()
        self._clear_session()
        self._pending_messages.clear()
        self._last_status = "Disconnected"
        self._current_peer = ""
        self.show_main()

    def _clear_session(self):
        """Clear session data safely."""
        self.session.clear()

    # ------------------------------------------------------------------ #
    # Controller callbacks
    def _handle_incoming_message(self, sender: str, msg: str, ts: float):
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

    def _handle_status_text(self, text: str):
        """Handle status updates from transport with peer tracking."""
        status_lower = text.lower()

        if any(keyword in status_lower for keyword in ("disconnected", "connection failed", "invalid pairing code")):
            self._current_peer = ""
        elif any(keyword in status_lower for keyword in ("connected (mock)", "ready", "demo")):
            if not self._current_peer:
                self._current_peer = "Awaiting peer"

        if isinstance(self.current_frame, MainFrame):
            self.current_frame.update_status(text)

        self._last_status = text

    def _on_status_update(self, status_text: str, color: str):
        """Handle centralized status updates."""
        if isinstance(self.current_frame, MainFrame):
            self.current_frame.update_status(status_text)

    # ------------------------------------------------------------------ #
    def notify_incoming_message(self, sender: str, msg: str):
        """Notify user of incoming messages."""
        self.bell()
        self.after(AppConfig.STATUS_UPDATE_DELAY_SHORT,
                   lambda: self._handle_status_text(self.status_manager.get_current_status()))

    def clear_chat_history(self):
        """Clear chat history with user confirmation."""
        if isinstance(self.current_frame, MainFrame):
            if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the current chat log?"):
                self.current_frame.chat_page.clear_history()


if __name__ == "__main__":
    App().mainloop()
