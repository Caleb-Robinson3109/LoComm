"""
LoRa Chat Desktop Application - orchestrates UI frames and controller.
Manages the main application window, including resizing logic and
transitioning between the login modal and the main content area.
"""
import tkinter as tk
from tkinter import messagebox
import time
from collections import deque
from typing import Optional

from services import AppController
from utils.state.status_manager import get_status_manager

from pages.login_page import LoginPage
from pages.chatroom_page import ChatroomPage
from pages.login_page import LoginPage
from pages.main_page import MainPage
from services.app_controller import AppController
from ui.theme_manager import ThemeManager, ensure_styles_initialized
from ui.theme_tokens import AppConfig, Colors, Spacing
from utils.app_logger import get_logger
from utils.window_sizing import calculate_initial_window_size, scale_dimensions
from utils.user_settings import get_user_settings

MAX_UI_PENDING_MESSAGES = 500


class App(tk.Tk):
    """LoRa Chat Desktop Application - UI layer only."""

    def __init__(self):
        super().__init__()
        try:
            preferred_theme = get_user_settings().theme_mode or "light"
            ThemeManager.set_mode(preferred_theme)
        except Exception:
            ThemeManager.set_mode("light")
        ensure_styles_initialized()
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
        self.chatroom_modal: Optional[tk.Toplevel] = None
        self.chatroom_modal_frame: Optional[ChatroomPage] = None

        # Wire up business logic callbacks to UI handlers
        self.app_controller.register_message_callback(self._handle_business_message)
        # Initialize UI with login modal
        self.show_login_modal()

    # ------------------------------------------------------------------ #
    def show_main(self, device_id: str | None = None, device_name: str | None = None,
                  route_id: str | None = None):
        """Show the main chat interface."""
        if self.current_frame:
            self.current_frame.destroy()

        # Reset to full screen dimensions for main interface
        self._init_fullscreen_window()

        # Use business logic controller for session management
        session = self.app_controller.session

        # Update session data if we just paired
        if device_id and device_name:
            # Preserve local device name while updating peer info
            if not hasattr(session, 'local_device_name') or not session.local_device_name:
                session.local_device_name = "Orion"
            session.device_name = device_name
            session.device_id = device_id
            session.paired_at = time.time()

        # Create main frame - pass controller reference for backward compatibility
        self.current_frame = MainPage(self, self, session, self.app_controller, self._handle_logout, self.toggle_theme)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        if route_id:
            try:
                self.current_frame.navigate_to(route_id)
            except Exception:
                pass

        # Chat page removed, no sync needed

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

    def show_login_modal(self):
        """Show the login page as initial interface."""
        # Clear any existing frames
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

        # Create login modal if not exists
        if not self.login_modal:
            self.login_modal = LoginPage(
                self,
                on_login=self._handle_login_success,
                on_register=self._handle_register_click,
                on_forgot_password=self._handle_forgot_password_click
            )

    # ------------------------------------------------------------------ #
    def start_transport_session(self, device_id: str, device_name: str, *, mode: str = "pin",
                                failure_title: str = "Pairing Failed",
                                failure_message: str = "Connection failed.") -> None:
        """Kick off the controller workflow to connect to a device."""

        def on_complete(success: bool, error_msg: str | None):
            if success:
                # Jump straight into chat once transport succeeds.
                self.show_main(device_id, device_name, route_id="home")
            else:
                messagebox.showerror(failure_title, error_msg or failure_message)
                self._clear_session()

        self.app_controller.start_session(device_id, device_name, mode=mode, callback=on_complete)



    # Login modal callbacks
    def _handle_login_success(self, device_name: str, password: str):
        """Handle successful login from modal."""
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
        """Open the chatroom modal using the same pattern as PIN pairing."""
        self.app_controller.status_manager.update_status(AppConfig.STATUS_AWAITING_PEER)
        self._close_chatroom_modal()
        modal = tk.Toplevel(self)
        modal.title("Chatroom")
        modal.configure(bg=Colors.SURFACE)

        # Calculate proper modal size (smaller than main window but larger than PIN modal)
        base_width, base_height = scale_dimensions(432, 378, 0.93, 0.75)
        default_width = max(int(base_width * 1.08), 420)
        default_height = max(int(base_height * 1.06), 420)
        width = max(int(default_width * 1.1 * 0.93), 360)  # 7% smaller than original
        height = max(int(default_height * 1.2 * 0.93), 380)  # 7% smaller than original
        modal.minsize(width, height)
        modal.resizable(True, True)
        modal.transient(self.winfo_toplevel())
        modal.protocol("WM_DELETE_WINDOW", self._close_chatroom_modal)

        # Center the modal window on screen
        modal.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        pos_x = (screen_w - width) // 2
        pos_y = (screen_h - height) // 2
        modal.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        self.chatroom_modal = modal

        # Create chatroom pairing frame inside the modal
        chatroom_frame = ChatroomPage(
            modal,
            lambda chatroom_code: self._handle_chatroom_success(chatroom_code)
        )
        chatroom_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)
        if hasattr(chatroom_frame, "focus_input"):
            chatroom_frame.focus_input()
        self.chatroom_modal_frame = chatroom_frame

    def _close_chatroom_modal(self):
        """Close the chatroom modal."""
        self.chatroom_modal_frame = None
        if self.chatroom_modal and self.chatroom_modal.winfo_exists():
            try:
                self.chatroom_modal.destroy()
            except Exception:
                pass
        self.chatroom_modal = None

    def show_chatroom_modal(self):
        """Show the chatroom modal for 20-digit code entry without destroying the main view."""
        self._open_chatroom_modal()

    def _handle_chatroom_success(self, chatroom_code: str):
        """Handle successful chatroom code entry."""
        # Close chatroom modal
        self._close_chatroom_modal()

        # Show main interface and navigate to devices page
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
        # Show login modal instead of main interface
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
        is_system = bool(sender and sender.lower() == "system")
        if isinstance(self.current_frame, MainPage):
            # Chat page removed, messages not displayed in main interface
            pass
        else:
            self._ui_pending_messages.append((sender, msg, ts))

        # Notify user if message is from external peer
        session = self.app_controller.session
        local_device_name = getattr(session, "local_device_name", "Orion") or "Orion"
        if sender and sender != local_device_name:
            self.notify_incoming_message(sender, msg)

    # ------------------------------------------------------------------ #
    def notify_incoming_message(self, sender: str, msg: str):
        """Notify user of incoming messages."""
        # Audible chimes disabled per request
        pass

    def _handle_app_close(self):
        """Ensure transport cleans up before the window closes."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            try:
                if self.app_controller:
                    self.app_controller.stop_session()
            finally:
                self.destroy()

    def clear_chat_history(self, *, confirm: bool = True):
        """Clear chat history - disabled since chat page removed."""
        # Chat page removed, no history to clear
        pass

    def toggle_theme(self, use_dark: bool):
        """Toggle between light and dark themes."""
        prev_route = None
        if isinstance(self.current_frame, MainPage):
            prev_route = getattr(self.current_frame.sidebar, "current_view", None)
        ThemeManager.toggle_mode(use_dark)
        # Get current session info from business logic layer
        session = self.app_controller.session
        self.configure(bg=Colors.SURFACE)
        self.show_main(session.device_id or None, session.device_name or None, route_id=prev_route)

    # ------------------------------------------------------------------ #
    def _init_main_window(self):
        """Initialize the main application window in center position with compact login dimensions."""
        self.update_idletasks()
        target_w, target_h = calculate_initial_window_size(self)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        # Calculate compact dimensions for login page (50% width and height)
        compact_w = max(target_w // 2, 400)  # 50% of original width, minimum 400px
        compact_h = max(target_h // 2, 300)  # 50% of original height, minimum 300px
        target_w = compact_w  # Use compact width for login
        target_h = compact_h  # Use compact height for login

        # Position window in center of screen
        offset_x = (screen_w - target_w) // 2
        offset_y = (screen_h - target_h) // 2
        self.geometry(f"{target_w}x{target_h}+{offset_x}+{offset_y}")
        self.minsize(400, 300)  # Enforce minimum size
        self.resizable(True, True)

    def _init_fullscreen_window(self):
        """Force the app to occupy the full screen and center position it."""
        self.update_idletasks()
        target_w, target_h = calculate_initial_window_size(self)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        # Center the window on screen instead of right-aligning
        offset_x = max((screen_w - target_w) // 2, 0)
        offset_y = max((screen_h - target_h) // 2, 0)
        self.geometry(f"{target_w}x{target_h}+{offset_x}+{offset_y}")
        self.minsize(800, 600)  # Enforce reasonable minimum size for main app
        self.resizable(True, True)


if __name__ == "__main__":
    App().mainloop()
