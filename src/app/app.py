"""
LoRa Chat Desktop Application - orchestrates UI frames and controller.
"""
import tkinter as tk
from tkinter import messagebox
import time
from collections import deque

from services import AppController
from utils.status_manager import get_status_manager
from pages.pin_pairing_frame import PINPairingFrame
from pages.main_frame import MainFrame
from utils.design_system import AppConfig, ensure_styles_initialized, ThemeManager, Colors
from mock.peer_chat_window import refresh_mock_peer_window_theme

MAX_UI_PENDING_MESSAGES = 500


class App(tk.Tk):
    """LoRa Chat Desktop Application - UI layer only."""

    def __init__(self):
        super().__init__()
        ensure_styles_initialized()
        self.title(AppConfig.APP_TITLE)
        self._init_fullscreen_window()
        self.protocol("WM_DELETE_WINDOW", self._handle_app_close)
        self.after(0, self._focus_window)

        # Business logic is delegated to separate controller
        self.app_controller = AppController(self)

        # UI-specific state (not business logic)
        self.current_frame = None
        self._ui_connected = False
        self._ui_pending_messages = deque(maxlen=MAX_UI_PENDING_MESSAGES)

        # Wire up business logic callbacks to UI handlers
        self.app_controller.register_message_callback(self._handle_business_message)
        self.app_controller.register_status_callback(self._handle_business_status)

        # Initialize UI
        self.show_main()

    # ------------------------------------------------------------------ #
    def show_main(self, device_id: str | None = None, device_name: str | None = None,
                  route_id: str | None = None):
        """Show the main chat interface."""
        if self.current_frame:
            self.current_frame.destroy()

        # Use business logic controller for session management
        session = self.app_controller.session

        # Update session data if we just paired
        if device_id and device_name:
            # CRITICAL FIX: Preserve local device name while updating peer info
            if not hasattr(session, 'local_device_name') or not session.local_device_name:
                session.local_device_name = "Orion"
            session.device_name = device_name
            session.device_id = device_id
            session.paired_at = time.time()

        # Create main frame - pass controller reference for backward compatibility
        self.current_frame = MainFrame(self, self, session, self.app_controller, self._handle_logout, self.toggle_theme)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        if route_id:
            try:
                self.current_frame.navigate_to(route_id)
            except Exception:
                pass

        if hasattr(self.current_frame, "chat_page"):
            self.current_frame.chat_page.sync_session_info()

        # Process pending UI messages
        if self._ui_pending_messages:
            for sender, msg, _ in self._ui_pending_messages:
                display_name = sender or "Peer"
                is_system = bool(sender and sender.lower() == "system")
                self.current_frame.chat_page.append_line(
                    display_name,
                    msg,
                    is_system=is_system,
                )
            self._ui_pending_messages.clear()

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
                # Jump straight into chat once transport succeeds.
                self.show_main(device_id, device_name, route_id="chat")
            else:
                messagebox.showerror(failure_title, error_msg or failure_message)
                self._clear_session()

        self.app_controller.start_session(device_id, device_name, mode=mode, callback=on_complete)

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
        self.app_controller.stop_session()
        self._clear_session()
        self._ui_pending_messages.clear()
        self.show_main()

    def _clear_session(self):
        """Clear session data safely."""
        self.app_controller.session.clear()

    def _focus_window(self):
        """Bring window to front when launching."""
        try:
            self.lift()
            self.attributes("-topmost", True)
            self.after(200, lambda: self.attributes("-topmost", False))
            self.focus_force()
        except tk.TclError:
            pass

    # ------------------------------------------------------------------ #
    # Business logic callback methods
    def _handle_business_message(self, sender: str, msg: str, ts: float):
        """Handle incoming messages from business logic layer."""
        normalized_sender = (sender or "").strip()
        if normalized_sender and normalized_sender.lower() == "system" and "firmware" in (msg or "").lower():
            return
        is_system = bool(sender and sender.lower() == "system")
        if isinstance(self.current_frame, MainFrame):
            display_name = sender or "Peer"
            self.current_frame.chat_page.append_line(
                display_name,
                msg,
                is_system=is_system,
            )
        else:
            self._ui_pending_messages.append((sender, msg, ts))

        # Notify user if message is from external peer
        session = self.app_controller.session
        local_device_name = getattr(session, "local_device_name", "Orion") or "Orion"
        if sender and sender != local_device_name:
            self.notify_incoming_message(sender, msg)

    def _handle_business_status(self, text: str):
        """Handle status updates from business logic layer."""
        if isinstance(self.current_frame, MainFrame):
            self.current_frame.update_status(text)

    def _on_status_update(self, status_text: str, color: str):
        """Handle centralized status updates."""
        if isinstance(self.current_frame, MainFrame):
            self.current_frame.update_status(status_text)

    # ------------------------------------------------------------------ #
    def notify_incoming_message(self, sender: str, msg: str):
        """Notify user of incoming messages."""
        # Audible chimes disabled per request
        pass

    def _handle_app_close(self):
        """Ensure transport cleans up before the window closes."""
        try:
            if self.app_controller:
                self.app_controller.stop_session()
        finally:
            self.destroy()

    def clear_chat_history(self, *, confirm: bool = True):
        """Clear chat history, optionally skipping confirmation."""
        if not isinstance(self.current_frame, MainFrame):
            return
        proceed = True
        if confirm:
            proceed = messagebox.askyesno("Clear Chat", "Are you sure you want to clear the current chat log?")
        if proceed:
            self.current_frame.chat_page.clear_history()

    def toggle_theme(self, use_dark: bool):
        """Toggle between light and dark themes."""
        prev_route = None
        if isinstance(self.current_frame, MainFrame):
            prev_route = getattr(self.current_frame.sidebar, "current_view", None)
        ThemeManager.toggle_mode(use_dark)
        refresh_mock_peer_window_theme()
        # Get current session info from business logic layer
        session = self.app_controller.session
        self.configure(bg=Colors.SURFACE)
        self.show_main(session.device_id or None, session.device_name or None, route_id=prev_route)

    # ------------------------------------------------------------------ #
    def _init_fullscreen_window(self):
        """Force the app to occupy the full screen and prevent shrinking."""
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        target_w = int(screen_w * AppConfig.WINDOW_WIDTH_RATIO)
        target_h = int(screen_h * AppConfig.WINDOW_HEIGHT_RATIO)
        offset_x = max(screen_w - target_w, 0)
        offset_y = 0
        self.geometry(f"{target_w}x{target_h}+{offset_x}+{offset_y}")
        min_height = max(int(target_h * 0.9), AppConfig.MIN_WINDOW_HEIGHT)
        self.minsize(target_w, min_height)
        self.resizable(True, True)


if __name__ == "__main__":
    App().mainloop()
