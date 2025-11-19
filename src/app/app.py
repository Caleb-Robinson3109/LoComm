"""
LoRa Chat Desktop Application - orchestrates UI frames and controller.
"""
import tkinter as tk
from tkinter import messagebox
import time
from collections import deque
from typing import Optional

from services import AppController
from utils.state.status_manager import get_status_manager

from pages.login_modal import LoginModal
from pages.chatroom_window import ChatroomWindow
from pages.main_frame import MainFrame
from utils.design_system import AppConfig, ensure_styles_initialized, ThemeManager, Colors, Spacing
from utils.window_sizing import calculate_initial_window_size
from ui.helpers import create_centered_modal, ModalScaffold

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../api')))

from LoCommAPI import *

MAX_UI_PENDING_MESSAGES = 500


class App(tk.Tk):
    """LoRa Chat Desktop Application - UI layer only."""

    def __init__(self):
        super().__init__()

        # Set up styles and force light mode on startup
        ensure_styles_initialized()
        # Canonical theme flag for the whole app
        self.is_dark_mode: bool = False
        # Force ThemeManager into light mode regardless of saved settings
        ThemeManager.toggle_mode(False)

        self.title(AppConfig.APP_TITLE)
        self.configure(bg=Colors.BG_MAIN)
        self._init_main_window()  # Initialize in proper position
        self.protocol("WM_DELETE_WINDOW", self._handle_app_close)
        self.after(0, self._focus_window)

        # Business logic is delegated to separate controller
        self.app_controller = AppController(self)

        # UI-specific state (not business logic)
        self.current_frame = None
        self._ui_connected = False
        self._ui_pending_messages = deque(maxlen=MAX_UI_PENDING_MESSAGES)
        self.login_modal = None
        self.chatroom_modal: Optional[ModalScaffold] = None
        self.chatroom_modal_frame: Optional[ChatroomWindow] = None

        # Wire up business logic callbacks to UI handlers
        self.app_controller.register_message_callback(self._handle_business_message)

        #connect to device

        while not connect_to_device():
            pass


        # Initialize UI with login modal
        self.show_login_modal()

    # ------------------------------------------------------------------ #
    def show_main(
        self,
        device_id: str | None = None,
        device_name: str | None = None,
        route_id: str | None = None,
    ):
        """Show the main interface."""
        if self.current_frame:
            self.current_frame.destroy()

        # Reset to full screen dimensions for main interface
        self._init_fullscreen_window()

        # Use business logic controller for session management
        session = self.app_controller.session

        # Update session data if we just paired
        if device_id and device_name:
            # Preserve local device name while updating peer info
            if not hasattr(session, "local_device_name") or not session.local_device_name:
                session.local_device_name = "Orion"
            session.device_name = device_name
            session.device_id = device_id
            session.paired_at = time.time()

        # Create main frame - pass controller reference for backward compatibility
        self.current_frame = MainFrame(
            self,
            self,
            session,
            self.app_controller,
            self._handle_logout,
            self.toggle_theme,
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        if route_id:
            try:
                self.current_frame.navigate_to(route_id)
            except Exception:
                pass

        # Chat page removed, no sync needed

        # Process pending UI messages (no-op for now, chat removed)
        if self._ui_pending_messages:
            self._ui_pending_messages.clear()

    def show_login_modal(self):
        """Show the login page as initial interface."""
        # Clear any existing frames
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

        # Create login modal if not exists
        if not self.login_modal:
            self.login_modal = LoginModal(
                self,
                on_login=self._handle_login_success,
                on_register=self._handle_register_click,
                on_forgot_password=self._handle_forgot_password_click,
            )

    # ------------------------------------------------------------------ #
    def start_transport_session(
        self,
        device_id: str,
        device_name: str,
        *,
        mode: str = "pin",
        failure_title: str = "Pairing Failed",
        failure_message: str = "Connection failed.",
    ) -> None:
        """Kick off the controller workflow to connect to a device."""

        def on_complete(success: bool, error_msg: str | None):
            if success:
                # Jump straight into main shell once transport succeeds.
                self.show_main(device_id, device_name, route_id="home")
            else:
                messagebox.showerror(failure_title, error_msg or failure_message)
                self._clear_session()

        self.app_controller.start_session(
            device_id,
            device_name,
            mode=mode,
            callback=on_complete,
        )

    # Login modal callbacks
    def _handle_login_success(self, device_name: str, password: str):
        """Handle successful login from modal."""

        #enter name on device
        if store_name_on_device(device_name):
            print("enter pairing code okay")
        else:
            print("enter pairing code fail")

        # Set local device name for the session
        session = self.app_controller.session
        session.local_device_name = device_name

        # Close login modal
        if self.login_modal:
            self.login_modal.close_modal()
            self.login_modal = None

        # Show main interface and go to home page
        self.show_main(route_id="home")

    def _open_chatroom_modal(self):
        """Open the chatroom modal."""
        self.app_controller.status_manager.update_status(AppConfig.STATUS_AWAITING_PEER)
        self._close_chatroom_modal()

        scaffold = create_centered_modal(
            self,
            title="Chatroom",
            width_ratio=0.0,
            height_ratio=0.0,
            min_width=560,
            min_height=500,
            bg=Colors.SURFACE,
            use_scroll=False,
        )

        self.chatroom_modal = scaffold

        # Create chatroom frame inside the modal body
        chatroom_frame = ChatroomWindow(
            scaffold.body,
            lambda chatroom_code: self._handle_chatroom_success(chatroom_code),
        )
        chatroom_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)
        if hasattr(chatroom_frame, "focus_input"):
            chatroom_frame.focus_input()
        self.chatroom_modal_frame = chatroom_frame

        scaffold.toplevel.protocol("WM_DELETE_WINDOW", self._close_chatroom_modal)

    def _close_chatroom_modal(self):
        """Close the chatroom modal."""
        self.chatroom_modal_frame = None
        if self.chatroom_modal and self.chatroom_modal.toplevel.winfo_exists():
            try:
                self.chatroom_modal.toplevel.destroy()
            except Exception:
                pass
        self.chatroom_modal = None

    def show_chatroom_modal(self):
        """Show the chatroom modal for 20 digit code entry without destroying the main view."""
        self._open_chatroom_modal()

    def _handle_chatroom_success(self, chatroom_code: str):
        """Handle successful chatroom code entry."""
        self._close_chatroom_modal()
        self.show_main(route_id="pair")

    def _handle_register_click(self):
        """Handle register link click."""
        messagebox.showinfo("Register", "Registration feature will be implemented in the future.")

    def _handle_forgot_password_click(self):
        """Handle forgot password link click."""
        messagebox.showinfo("Forgot Password", "Password recovery feature will be implemented in the future.")

    def _handle_logout(self):
        """Handle user logout with proper cleanup."""
        self.app_controller.stop_session()
        self._clear_session()
        self._ui_pending_messages.clear()
        self.show_login_modal()

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

        # Chat page removed, keep messages in queue if needed later
        self._ui_pending_messages.append((sender, msg, ts))

        # Notify user if message is from external peer
        session = self.app_controller.session
        local_device_name = getattr(session, "local_device_name", "Orion") or "Orion"
        if sender and sender != local_device_name:
            self.notify_incoming_message(sender, msg)

    def notify_incoming_message(self, sender: str, msg: str):
        """Notify user of incoming messages (disabled)."""
        pass

    def _handle_app_close(self):
        """Ensure transport cleans up before the window closes."""
        try:
            if self.app_controller:
                self.app_controller.stop_session()
        finally:
            self.destroy()

    def clear_chat_history(self, *, confirm: bool = True):
        """Clear chat history - disabled since chat page removed."""
        pass

    def toggle_theme(self, use_dark: bool):
        """Toggle between light and dark themes for the whole app."""
        # Store canonical state
        self.is_dark_mode = bool(use_dark)

        # Preserve current route (home, settings, about, etc)
        prev_route = None
        if isinstance(self.current_frame, MainFrame):
            prev_route = getattr(self.current_frame.sidebar, "current_view", None)

        # Flip theme in design system
        ThemeManager.toggle_mode(use_dark)

        # Recreate main frame with same route
        session = self.app_controller.session
        self.configure(bg=Colors.SURFACE)
        self.show_main(session.device_id or None, session.device_name or None, route_id=prev_route)

    # ------------------------------------------------------------------ #
    def _init_main_window(self):
        """Initialize the main application window for login (compact)."""
        self.update_idletasks()
        target_w, target_h = calculate_initial_window_size(self)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        compact_w = max(target_w // 2, 400)
        compact_h = max(target_h // 2, 300)
        target_w = compact_w
        target_h = compact_h

        offset_x = (screen_w - target_w) // 2
        offset_y = (screen_h - target_h) // 2
        self.geometry(f"{target_w}x{target_h}+{offset_x}+{offset_y}")
        self.minsize(target_w, target_h)
        self.resizable(True, True)

    def _init_fullscreen_window(self):
        """Force the app to occupy the full screen and center position it."""
        self.update_idletasks()
        target_w, target_h = calculate_initial_window_size(self)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        offset_x = max((screen_w - target_w) // 2, 0)
        offset_y = max((screen_h - target_h) // 2, 0)
        self.geometry(f"{target_w}x{target_h}+{offset_x}+{offset_y}")
        self.minsize(target_w, target_h)
        self.resizable(True, True)


if __name__ == "__main__":
    App().mainloop()
