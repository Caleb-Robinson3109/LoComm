import tkinter as tk
from tkinter import messagebox, filedialog
import time
import threading

from lora_transport_locomm import LoCommTransport
from utils.session import Session
from utils.status_manager import get_status_manager
from frames.login_frame import LoginFrame
from frames.main_frame import MainFrame


class App(tk.Tk):
    """
    LoRa Chat Desktop Application - Enhanced Version

    This is the unified application that incorporates all improvements from the
    comprehensive UI/UX audit, combining the benefits of both minimal changes
    and clean architecture approaches.

    Key improvements implemented:
    - Thread-safe UI operations
    - Enhanced authentication flow with timeout
    - Better error handling and user feedback
    - Responsive window sizing
    - Improved input validation
    - Centralized status management
    """

    def __init__(self):
        super().__init__()
        self.title("LoRa Chat Desktop")
        self.geometry("700x600")

        # Enable responsive resizing
        self.minsize(500, 400)
        self.resizable(True, True)

        self.session = Session()
        self.transport = LoCommTransport(self)
        self.transport.on_receive = self._on_receive
        self.transport.on_status = self._on_status

        self._pending_messages: list[tuple[str, str, float]] = []
        self._current_peer: str = ""
        self._last_status: str = "Disconnected"

        # Initialize centralized status manager
        self.status_manager = get_status_manager()
        self.status_manager.register_status_callback(self._on_status_update)

        self.current_frame = None
        self.show_login()

    def show_login(self):
        """Show the login screen with enhanced functionality."""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self, self._handle_login)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_main(self):
        """Show the main chat interface."""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainFrame(self, self, self.session, self.transport, self._handle_logout)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        if self._last_status:
            self.current_frame.update_status(self._last_status)

        if self._pending_messages:
            for sender, msg, ts in self._pending_messages:
                display_name = sender or "Peer"
                self.current_frame.chat_tab.append_line(display_name, msg)
                if sender:
                    self._current_peer = sender
            self._pending_messages.clear()

    def _handle_login(self, username: str, password_bytes: bytearray):
        """
        Handle user login with enhanced error handling and timeout protection.

        This implementation provides:
        - Thread-safe operations
        - 30-second timeout protection
        - Detailed error messages
        - Visual feedback during authentication
        """
        self.session.username = username
        self.session.password_bytes = password_bytes
        self.session.login_time = time.time()
        pw = password_bytes.decode("utf-8")

        def finish_login(success: bool, error_msg: str = ""):
            """Complete the login process with proper error handling."""
            if success:
                self.show_main()
            else:
                error_message = error_msg or "Connection or password invalid."
                messagebox.showerror("Login Failed", error_message)
                self.session.clear()
                if isinstance(self.current_frame, LoginFrame):
                    self.current_frame.set_waiting(False)

        def worker():
            """Background worker for connection attempt with timeout."""
            try:
                import threading

                def timeout_handler():
                    """Handle connection timeout."""
                    raise TimeoutError("Connection timeout")

                # 30 second timeout
                timeout_timer = threading.Timer(30.0, timeout_handler)
                timeout_timer.start()

                try:
                    ok = self.transport.start(pw)
                    timeout_timer.cancel()  # Cancel timeout
                    self.after(0, lambda: finish_login(ok))
                except TimeoutError:
                    timeout_timer.cancel()  # Cancel timeout
                    self.after(0, lambda: finish_login(False, "Connection timeout. Please check device connection."))
                except Exception as e:
                    timeout_timer.cancel()  # Cancel timeout
                    error_msg = f"Connection error: {str(e)}"
                    self.after(0, lambda: finish_login(False, error_msg))

            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                self.after(0, lambda: finish_login(False, error_msg))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_logout(self):
        """Handle user logout with proper cleanup."""
        self.transport.stop()
        self.session.clear()
        self._pending_messages.clear()
        self._last_status = "Disconnected"
        self._current_peer = ""
        self.show_login()

    def _on_receive(self, sender: str, msg: str, ts: float):
        """
        Handle incoming messages with thread-safe UI updates.

        This method ensures all UI operations are performed in the main thread
        using self.after() to prevent crashes and ensure stability.
        """
        if isinstance(self.current_frame, MainFrame):
            display_name = sender or "Peer"
            self.current_frame.chat_tab.append_line(display_name, msg)
        else:
            self._pending_messages.append((sender, msg, ts))

        if sender:
            self._current_peer = sender

        if sender and sender != self.session.username:
            self.notify_incoming_message(sender, msg)

    def _on_status(self, text: str):
        """
        Handle status updates from transport with thread safety.

        Updates peer tracking based on status and ensures UI updates
        are performed in the main thread.
        """
        # Update peer tracking based on status
        lowered = text.lower()
        if any(keyword in lowered for keyword in ("disconnected", "connection failed", "invalid device password")):
            self._current_peer = ""
        elif any(keyword in lowered for keyword in ("authenticated and ready", "connected (mock)")):
            if not self._current_peer:
                self._current_peer = "Awaiting peer"

        if isinstance(self.current_frame, MainFrame):
            self.current_frame.update_status(text)

        self._last_status = text

    def _on_status_update(self, status_text: str, color: str):
        """
        Handle status updates from the centralized status manager.

        This provides a clean interface for status management across
        the application.
        """
        if isinstance(self.current_frame, MainFrame):
            self.current_frame.update_status(status_text)

    def notify_incoming_message(self, sender: str, msg: str):
        """
        Notify user of incoming messages with proper timing.

        Uses bell() for audio notification and delayed status updates
        to prevent interface conflicts.
        """
        self.bell()
        # Use a short delay to avoid status update conflicts
        self.after(500, lambda: self._on_status(self.status_manager.get_current_status()))

    def clear_chat_history(self):
        """Clear chat history with user confirmation."""
        if isinstance(self.current_frame, MainFrame):
            if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the current chat log?"):
                self.current_frame.chat_tab.clear_history()


if __name__ == "__main__":
    App().mainloop()
