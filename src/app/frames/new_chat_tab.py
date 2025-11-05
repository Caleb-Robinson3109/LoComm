"""New redesigned ChatTab with component-based architecture."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from .chat_models import MessageManager, ChatMessage, MessageType, MessageStatus
from .chat_header import ChatHeader
from .message_list import MessageList
from .message_composer import MessageComposer
from lora_transport_locomm import LoCommTransport
from utils.design_system import Colors, Typography, Spacing


class ChatTab(ttk.Frame):
    """Redesigned chat tab with component-based architecture."""

    def __init__(self, master, transport: LoCommTransport, username: str,
                 on_disconnect: Optional[Callable] = None, on_device_connected: Optional[Callable] = None):
        super().__init__(master)

        # Core dependencies
        self.master = master
        self.transport = transport
        self.username = username
        self.on_disconnect = on_disconnect
        self.on_device_connected = on_device_connected

        # Message management
        self.message_manager = MessageManager()
        self._connected = False
        self.device_connected = False
        self.current_device_name = None

        # Initialize UI components
        self._create_ui()

        # Set up transport callbacks
        self._setup_transport_callbacks()

        # Register for message manager updates
        self.message_manager.on_message_update(self._on_message_status_update)

    def _create_ui(self):
        """Create the chat tab UI using components."""
        # Main layout - vertical stacking
        self.pack(fill=tk.BOTH, expand=True)

        # ---------- Header Component ---------- #
        self.header = ChatHeader(self, on_disconnect=self._handle_disconnect)
        self.header.set_clear_chat_callback(self._handle_clear_chat)
        self.header.pack(fill=tk.X, padx=Spacing.TAB_PADDING, pady=(Spacing.MD, Spacing.SM))

        # ---------- Message List Component ---------- #
        self.message_list = MessageList(self, self.message_manager)
        self.message_list.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING)

        # ---------- Message Composer Component ---------- #
        self.composer = MessageComposer(self, on_send=self._handle_send_message)
        self.composer.pack(fill=tk.X, padx=Spacing.TAB_PADDING, pady=(Spacing.SM, Spacing.MD))

    def _setup_transport_callbacks(self):
        """Set up callbacks from the transport layer."""
        # The transport will call these when status/messages change
        # This maintains compatibility with existing transport interface
        pass

    def _handle_send_message(self, content: str):
        """Handle sending a new message."""
        if not self._connected:
            return

        # Add message to our message manager
        message = self.message_manager.add_message_by_parts(
            sender="Me",
            content=content,
            message_type=MessageType.TEXT,
            status=MessageStatus.PENDING
        )

        # Send through transport
        try:
            success = self.transport.send(self.username, content)
            if success:
                # Update to SENT status
                self.message_manager.update_message_status(message.id, MessageStatus.SENT)
            else:
                # Update to FAILED status
                self.message_manager.update_message_status(message.id, MessageStatus.FAILED)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.message_manager.update_message_status(message.id, MessageStatus.FAILED)

    def _handle_clear_chat(self):
        """Handle clear chat request."""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear all chat history?"):
            self.message_manager.clear_history()
            # Add system message
            self.message_manager.add_message_by_parts(
                sender="System",
                content="Chat history cleared.",
                message_type=MessageType.SYSTEM
            )

    def _handle_disconnect(self):
        """Handle disconnect request."""
        if self.on_disconnect:
            self.on_disconnect()

    def _on_message_status_update(self, message: ChatMessage):
        """Handle updates to message status (for delivery confirmation)."""
        # This could be expanded to handle delivery receipts, etc.
        # For now, we just log the status change
        if message.is_own_message and message.status == MessageStatus.FAILED:
            # Show error feedback
            self._show_send_error("Message sending failed")

    def _show_send_error(self, error_message: str):
        """Show error message to user."""
        # Add error message to chat
        self.message_manager.add_message_by_parts(
            sender="System",
            content=f"Error: {error_message}",
            message_type=MessageType.ERROR
        )

    # ---------- Public API (for compatibility with existing code) ---------- #

    def append_line(self, who: str, msg: str):
        """Append a line to the chat (legacy compatibility)."""
        # Convert old-style call to new message manager
        message_type = MessageType.SYSTEM if who == "System" else MessageType.TEXT
        status = MessageStatus.DELIVERED if who != "Me" else MessageStatus.SENT

        self.message_manager.add_message_by_parts(
            sender=who,
            content=msg,
            message_type=message_type,
            status=status
        )

    def set_status(self, text: str):
        """Set connection status (legacy compatibility)."""
        self.header.set_status(text)
        self.composer.set_connection_status(self._is_connected_status(text))

        # Add system messages for important status changes
        lowered = text.lower()
        if any(keyword in lowered for keyword in ("authenticated", "ready", "connected (mock)")):
            if not self._connected:
                self.append_line("System", "Connected to LoComm device.")
            self._connected = True
        elif any(keyword in lowered for keyword in ("disconnected", "connection failed", "invalid device password")):
            if self._connected:
                self.append_line("System", text)
            self._connected = False
        elif "send failed" in lowered:
            self.append_line("System", text)

    def _is_connected_status(self, status_text: str) -> bool:
        """Check if status indicates connected state."""
        lowered = status_text.lower()
        return any(keyword in lowered for keyword in ("authenticated", "ready", "connected (mock)"))

    def handle_device_connection(self, device_id: str, device_name: str):
        """Handle device connection from PairTab."""
        if device_id and device_name:
            # Device connected
            self.device_connected = True
            self.current_device_name = device_name
            self.append_line("System", f"Connected to device: {device_name}")
            # Enable chat composer
            self.composer.set_connection_status(True)
        else:
            # Device disconnected
            self.device_connected = False
            self.current_device_name = None
            self.append_line("System", "Device disconnected")
            # Disable chat composer
            self.composer.set_connection_status(False)

    def get_history_lines(self) -> list[str]:
        """Get chat history as text lines (legacy compatibility)."""
        return self.message_manager.get_history_text()

    def clear_history(self):
        """Clear chat history (legacy compatibility)."""
        self.message_manager.clear_history()

    def focus_input(self):
        """Focus the message input (legacy compatibility)."""
        self.composer.focus_input()
