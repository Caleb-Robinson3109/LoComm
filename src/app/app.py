"""
LoRa Chat Desktop Application - orchestrates UI frames and controller.
"""
import tkinter as tk
from tkinter import messagebox
import time
from collections import deque
from typing import Optional

from services import AppController
from pages.login_window import LoginWindow
from pages.main_frame import MainFrame
from pages.welcome_window import WelcomeWindow
from utils.design_system import AppConfig, ensure_styles_initialized, ThemeManager, Colors
from utils.user_settings import get_user_settings
from utils.window_sizing import calculate_initial_window_size, get_login_modal_size

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
        self.user_settings = get_user_settings()
        self.is_dark_mode: bool = self.user_settings.theme_mode == "dark"
        ThemeManager.toggle_mode(self.is_dark_mode)

        self.title(AppConfig.APP_TITLE)
        self.configure(bg=Colors.BG_MAIN)
        # Use compact sizing that matches the login modal footprint
        self._init_main_window(width_scale=1.0, height_scale=1.0)
        self._apply_login_modal_size()
        self.protocol("WM_DELETE_WINDOW", self._handle_app_close)
        self.after(0, self._focus_window)

        # Business logic is delegated to separate controller
        self.app_controller = AppController(self)

        # UI-specific state (not business logic)
        self.current_frame = None
        self._ui_connected = False
        self._ui_pending_messages = deque(maxlen=MAX_UI_PENDING_MESSAGES)
        self.login_modal = None

        # Wire up business logic callbacks to UI handlers
        self.app_controller.register_message_callback(self._handle_business_message)

        #connect to device
        counter = 0
        while not connect_to_device():
            counter += 1
            if counter >= 10:
                run_deviceless_mode()
                print("Failed to connect to device, entering deviceless mode")


        # Initialize UI with welcome screen
        self.show_welcome_screen()

    # ------------------------------------------------------------------ #
    def show_welcome_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
        # Match the compact login dimensions for the welcome screen
        self._init_main_window(width_scale=1.0, height_scale=1.0)
        self._apply_login_modal_size()
        self.current_frame = WelcomeWindow(self, on_login=self.show_login_modal, on_signup=self._handle_signup_request)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

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
                session.local_device_name = device_name
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

        self._init_main_window()  # Reset frame size for login

        # Create login modal if not exists
        if not self.login_modal:
            self.login_modal = LoginWindow(
                self,
                on_login=self._handle_login_success,
            )

    def _handle_signup_request(self):
        self.show_login_modal()
        if self.login_modal:
            self.login_modal.open_register(on_close=self._handle_signup_flow_closed)

    def _handle_signup_flow_closed(self, success: bool):
        if not self.login_modal:
            return
        if success:
            if self.login_modal.password_entry and self.login_modal.password_entry.winfo_exists():
                self.login_modal.password_entry.focus_set()
        else:
            self.login_modal.close_modal()
            self.login_modal = None
            self._init_main_window(width_scale=1.0, height_scale=1.155)
            self.show_welcome_screen()

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
        local_device_name = getattr(session, "local_device_name", "") or ""
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

        # Snapshot current colors so we can repaint widgets
        prev_bg = {
            "BG_MAIN": Colors.BG_MAIN,
            "SURFACE": Colors.SURFACE,
            "SURFACE_ALT": Colors.SURFACE_ALT,
            "BG_ELEVATED": Colors.BG_ELEVATED,
            "BG_ELEVATED_2": Colors.BG_ELEVATED_2,
        }
        prev_fg = {
            "TEXT_PRIMARY": Colors.TEXT_PRIMARY,
            "TEXT_SECONDARY": Colors.TEXT_SECONDARY,
            "TEXT_MUTED": Colors.TEXT_MUTED,
        }

        # Flip theme in design system without rebuilding the UI
        ThemeManager.toggle_mode(use_dark)

        # Refresh current UI surfaces instead of recreating frames
        try:
            self.configure(bg=Colors.SURFACE)
        except Exception:
            pass

        if isinstance(self.current_frame, MainFrame) and hasattr(self.current_frame, "apply_theme"):
            self.current_frame.apply_theme(prev_bg=prev_bg, prev_fg=prev_fg)
        elif hasattr(self.current_frame, "configure"):
            try:
                self.current_frame.configure(bg=Colors.SURFACE)
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    def _init_main_window(self, *, width_scale: float = 1.0, height_scale: float = 1.0):
        """Initialize the main application window for login (compact)."""
        self.update_idletasks()
        target_w, target_h = calculate_initial_window_size(self)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        compact_w = max(target_w // 2, 400)
        compact_h = max(target_h // 2, 300)
        target_w = compact_w
        target_h = compact_h

        scaled_w = max(int(target_w * width_scale), 1)
        scaled_h = max(int(target_h * height_scale), 1)
        offset_x = max((screen_w - scaled_w) // 2, 0)
        offset_y = max((screen_h - scaled_h) // 2, 0)

        self.geometry(f"{scaled_w}x{scaled_h}+{offset_x}+{offset_y}")
        self.minsize(scaled_w, scaled_h)
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

    def _apply_login_modal_size(self):
        """Center the window using the login modal dimensions."""
        size = get_login_modal_size()
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = min(size.width + 20, screen_w)
        height = min(size.height, screen_h)
        width = max(width, size.min_width + 20)
        height = max(height, size.min_height)
        pos_x = max((screen_w - width) // 2, 0)
        pos_y = max((screen_h - height) // 2, 0)
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        self.minsize(size.min_width + 20, size.min_height)
        self.resizable(False, False)


if __name__ == "__main__":
    App().mainloop()
