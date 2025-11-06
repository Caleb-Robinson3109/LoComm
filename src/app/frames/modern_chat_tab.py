"""Complete modern chat tab interface integrating all sophisticated chat components."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, List
import time
import threading
from datetime import datetime
from .chat_models import ChatMessage, MessageManager, MessageType, MessageStatus
from .modern_message_list import ModernMessageList
from .modern_message_composer import ModernMessageComposer
from .modern_message_bubble import ModernMessageBubble
from utils.design_system import Colors, Typography, Spacing, DesignUtils
from lora_transport_locomm import LoCommTransport


class DeviceStatusIndicator(ttk.Frame):
    """Modern device status indicator with sophisticated visual states."""

    def __init__(self, master, on_disconnect: Optional[Callable] = None):
        super().__init__(master)
        self.on_disconnect = on_disconnect
        self.device_name = ""
        self.device_id = ""
        self.signal_strength = 0
        self.battery_level = 100

        self._create_status_ui()

    def _create_status_ui(self):
        """Create the device status interface."""
        # Main container
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, padx=Spacing.TAB_PADDING, pady=(Spacing.SM, 0))

        # Left side - Device info
        device_frame = ttk.Frame(status_frame)
        device_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Device name and status
        self.device_name_label = tk.Label(
            device_frame,
            text="No device connected",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY,
            anchor="w"
        )
        self.device_name_label.pack(fill=tk.X)

        # Status details
        self.status_details = tk.Label(
            device_frame,
            text="Click 'Pair' to connect a device",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_PRIMARY,
            anchor="w"
        )
        self.status_details.pack(fill=tk.X)

        # Right side - Connection controls
        controls_frame = ttk.Frame(status_frame)
        controls_frame.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        # Signal strength indicator
        self.signal_frame = ttk.Frame(controls_frame)
        self.signal_frame.pack(side=tk.RIGHT, padx=(Spacing.XS, 0))

        # Battery indicator
        self.battery_frame = ttk.Frame(controls_frame)
        self.battery_frame.pack(side=tk.RIGHT, padx=(Spacing.XS, 0))

        # Disconnect button
        self.disconnect_btn = DesignUtils.create_styled_button(
            controls_frame,
            "Disconnect",
            self._on_disconnect_click,
            style='Warning.TButton'
        )
        self.disconnect_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        self.disconnect_btn.pack_forget()  # Hidden by default

    def update_device_status(self, device_name: str, device_id: str, status: str,
                           signal_strength: int = 0, battery_level: int = 100):
        """Update device status display."""
        self.device_name = device_name
        self.device_id = device_id
        self.signal_strength = max(0, min(100, signal_strength))
        self.battery_level = max(0, min(100, battery_level))

        # Update device name
        if device_name:
            self.device_name_label.config(text=device_name)
        else:
            self.device_name_label.config(text="Unknown Device")

        # Update status details
        self._update_status_details(status)

        # Update indicators
        self._update_signal_indicator()
        self._update_battery_indicator()

        # Show disconnect button if connected
        if status.lower() in ['connected', 'ready', 'authenticated']:
            self.disconnect_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        else:
            self.disconnect_btn.pack_forget()

    def _update_status_details(self, status: str):
        """Update status details with appropriate styling."""
        status_lower = status.lower()

        if any(word in status_lower for word in ['connected', 'ready', 'authenticated']):
            status_color = Colors.STATUS_CONNECTED
            status_icon = "🟢"
            detail_text = f"Connected • Signal: {self.signal_strength}% • Battery: {self.battery_level}%"
        elif any(word in status_lower for word in ['connecting', 'pairing', 'verifying']):
            status_color = Colors.STATUS_CONNECTING
            status_icon = "🟡"
            detail_text = f"Connecting... • Signal: {self.signal_strength}%"
        elif any(word in status_lower for word in ['disconnected', 'failed']):
            status_color = Colors.STATUS_DISCONNECTED
            status_icon = "🔴"
            detail_text = "Disconnected"
        else:
            status_color = Colors.TEXT_MUTED
            status_icon = "⚪"
            detail_text = status

        self.status_details.config(text=f"{status_icon} {detail_text}", fg=status_color)

    def _update_signal_indicator(self):
        """Update signal strength indicator."""
        # Clear existing indicators
        for widget in self.signal_frame.winfo_children():
            widget.destroy()

        # Signal bars (4 bars total)
        bars = 4
        filled_bars = int((self.signal_strength / 100) * bars)

        for i in range(bars):
            bar_color = Colors.ACCENT_GREEN if i < filled_bars else Colors.BORDER_PRIMARY
            bar_height = (i + 1) * 3  # Increasing height

            bar = tk.Label(
                self.signal_frame,
                text="█",
                font=(Typography.FONT_PRIMARY, bar_height),
                fg=bar_color,
                bg=Colors.BG_PRIMARY
            )
            bar.pack(side=tk.LEFT, padx=(1, 0))

    def _update_battery_indicator(self):
        """Update battery level indicator."""
        # Clear existing indicators
        for widget in self.battery_frame.winfo_children():
            widget.destroy()

        # Battery icon and percentage
        if self.battery_level > 20:
            battery_color = Colors.STATUS_CONNECTED
            battery_icon = "🔋"
        elif self.battery_level > 10:
            battery_color = Colors.STATUS_CONNECTING
            battery_icon = "🪫"
        else:
            battery_color = Colors.STATUS_FAILED
            battery_icon = "🪫"

        battery_label = tk.Label(
            self.battery_frame,
            text=f"{battery_icon} {self.battery_level}%",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg=battery_color,
            bg=Colors.BG_PRIMARY
        )
        battery_label.pack()

    def _on_disconnect_click(self):
        """Handle disconnect button click."""
        if self.on_disconnect:
            self.on_disconnect()
        if self.device_name:
            self.update_device_status(
                self.device_name,
                self.device_id,
                "Disconnected",
                0,
                0
            )


class ConversationHeader(ttk.Frame):
    """Modern conversation header with context and actions."""

    def __init__(self, master, on_settings: Optional[Callable] = None,
                 on_clear_chat: Optional[Callable] = None,
                 on_export_chat: Optional[Callable] = None):
        super().__init__(master)
        self.on_settings = on_settings
        self.on_clear_chat = on_clear_chat
        self.on_export_chat = on_export_chat
        self.message_count = 0
        self.participant_count = 1

        self._create_header_ui()

    def _create_header_ui(self):
        """Create the conversation header."""
        # Main container
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=Spacing.TAB_PADDING, pady=(Spacing.SM, Spacing.MD))

        # Left side - Conversation info
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Conversation title
        self.title_label = tk.Label(
            info_frame,
            text="LoRa Chat",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG, Typography.WEIGHT_BOLD),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY,
            anchor="w"
        )
        self.title_label.pack(fill=tk.X)

        # Conversation details
        self.details_label = tk.Label(
            info_frame,
            text="No active conversation",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_PRIMARY,
            anchor="w"
        )
        self.details_label.pack(fill=tk.X)

        # Right side - Action buttons
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side=tk.RIGHT)

        # Settings button
        settings_btn = DesignUtils.create_styled_button(
            actions_frame,
            "⚙️",
            lambda: self._on_settings_click(),
            style='Ghost.TButton',
            width=4
        )
        settings_btn.pack(side=tk.LEFT, padx=(Spacing.XS, 0))
        DesignUtils.create_tooltip_text(settings_btn, "Chat Settings")

        # Export button
        export_btn = DesignUtils.create_styled_button(
            actions_frame,
            "📤",
            lambda: self._on_export_click(),
            style='Ghost.TButton',
            width=4
        )
        export_btn.pack(side=tk.LEFT, padx=(Spacing.XS, 0))
        DesignUtils.create_tooltip_text(export_btn, "Export Chat")

        # Clear button
        clear_btn = DesignUtils.create_styled_button(
            actions_frame,
            "🗑️",
            lambda: self._on_clear_click(),
            style='Ghost.TButton',
            width=4
        )
        clear_btn.pack(side=tk.LEFT, padx=(Spacing.XS, 0))
        DesignUtils.create_tooltip_text(clear_btn, "Clear Chat History")

    def update_conversation_info(self, title: str, participant_count: int = 1,
                               message_count: int = 0, last_activity: Optional[str] = None):
        """Update conversation information."""
        self.title_label.config(text=title)
        self.participant_count = participant_count
        self.message_count = message_count

        # Format details
        details = []
        if participant_count > 1:
            details.append(f"{participant_count} participants")
        if message_count > 0:
            details.append(f"{message_count} messages")
        if last_activity:
            details.append(f"Last: {last_activity}")

        self.details_label.config(text=" • ".join(details) if details else "No activity yet")

    def _on_settings_click(self):
        """Handle settings button click."""
        if self.on_settings:
            self.on_settings()

    def _on_export_click(self):
        """Handle export button click."""
        if self.on_export_chat:
            self.on_export_chat()

    def _on_clear_click(self):
        """Handle clear button click."""
        if self.on_clear_chat:
            result = messagebox.askyesno(
                "Clear Chat History",
                "Are you sure you want to clear all chat history? This action cannot be undone.",
                icon='warning'
            )
            if result:
                self.on_clear_chat()


class ModernChatTab(ttk.Frame):
    """Complete modern chat tab with sophisticated features."""

    def __init__(self, master, transport: LoCommTransport, username: str,
                 on_disconnect: Optional[Callable] = None):
        super().__init__(master)
        self.master = master
        self.transport = transport
        self.username = username
        self.on_disconnect = on_disconnect

        # Message management
        self.message_manager = MessageManager()
        self.message_history: List[ChatMessage] = []

        # Connection state
        self._connected = False
        self.device_name = ""
        self.device_id = ""

        # Create UI
        self._create_chat_ui()

        # Start message processing
        self._start_message_processing()

    def _create_chat_ui(self):
        """Create the complete chat interface."""
        # Main container with padding
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        # Device status indicator
        self.device_status = DeviceStatusIndicator(
            main_frame,
            on_disconnect=self._handle_disconnect
        )
        self.device_status.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Conversation header
        self.conversation_header = ConversationHeader(
            main_frame,
            on_settings=self._open_chat_settings,
            on_clear_chat=self._clear_chat_history,
            on_export_chat=self._export_chat_history
        )
        self.conversation_header.pack(fill=tk.X, pady=(0, Spacing.MD))

        # Message list (main chat area)
        self.message_list = ModernMessageList(main_frame, self.message_manager)
        self.message_list.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))

        # Message composer
        self.composer = ModernMessageComposer(
            main_frame,
            on_send=self._send_message
        )
        self.composer.pack(fill=tk.X)

        # Initial state
        self._update_connection_state(False)

    def _start_message_processing(self):
        """Start background message processing."""
        # This would typically connect to transport callbacks
        # For now, we'll simulate message reception
        pass

    def _send_message(self, content: str, attachments: Optional[List] = None):
        """Send a message through the transport."""
        if not self._connected or not content.strip():
            return

        # Create message
        message = self.message_manager.add_message_by_parts(
            sender="Me",
            content=content,
            message_type=MessageType.TEXT,
            status=MessageStatus.PENDING
        )

        # Send through transport
        try:
            self.transport.send(self.username, content)

            # Update status to sent
            self.message_manager.update_message_status(
                message.id,
                MessageStatus.SENT
            )

            # Simulate delivery confirmation after a short delay
            self.after(1000, lambda: self._confirm_delivery(message.id))

        except Exception as e:
            # Update status to failed
            self.message_manager.update_message_status(
                message.id,
                MessageStatus.FAILED
            )
            self._show_error(f"Failed to send message: {str(e)}")

    def _confirm_delivery(self, message_id: str):
        """Confirm message delivery (simulated)."""
        self.message_manager.update_message_status(
            message_id,
            MessageStatus.DELIVERED
        )

    def _receive_message(self, sender: str, content: str, timestamp: Optional[float] = None):
        """Receive a message from another device."""
        if timestamp is None:
            timestamp = time.time()

        # Add message to manager
        message = self.message_manager.add_message_by_parts(
            sender=sender,
            content=content,
            message_type=MessageType.TEXT
        )

        # Update timestamp manually
        message.timestamp = timestamp

        # Update conversation info
        self._update_conversation_info()

    def _handle_disconnect(self):
        """Handle disconnect request."""
        if hasattr(self.transport, 'stop'):
            self.transport.stop()

        self._update_connection_state(False)
        self.device_name = ""
        self.device_id = ""

        if self.on_disconnect:
            self.on_disconnect()

    def set_status(self, status_text: str):
        """Update connection status."""
        status_lower = status_text.lower()

        if any(word in status_lower for word in ['authenticated', 'ready', 'connected']):
            if not self._connected:
                self._update_connection_state(True)
            # Try to extract device name from status
            if 'device:' in status_lower:
                parts = status_text.split('device:')
                if len(parts) > 1:
                    self.device_name = parts[1].strip().split()[0]
                    self.device_id = f"dev_{hash(self.device_name) % 10000}"

        elif any(word in status_lower for word in ['disconnected', 'failed', 'timeout']):
            self._update_connection_state(False)
            self.device_name = ""
            self.device_id = ""

        # Update device status display
        self.device_status.update_device_status(
            self.device_name,
            self.device_id,
            status_text,
            signal_strength=85,  # Simulated
            battery_level=75     # Simulated
        )

    def _update_connection_state(self, connected: bool):
        """Update all components for connection state change."""
        self._connected = connected

        # Update composer
        self.composer.set_connection_status(connected)

        # Update conversation header
        if connected and self.device_name:
            self.conversation_header.update_conversation_info(
                f"Chat with {self.device_name}",
                participant_count=2,
                message_count=len(self.message_history),
                last_activity=datetime.now().strftime("%H:%M")
            )
        else:
            self.conversation_header.update_conversation_info(
                "No active conversation",
                message_count=0
            )

        # Add system message on connection
        if connected and not self._has_system_message("Connected to device"):
            system_msg = self.message_manager.add_message_by_parts(
                sender="System",
                content=f"Connected to {self.device_name or 'LoRa device'}",
                message_type=MessageType.SYSTEM
            )

    def _has_system_message(self, content: str) -> bool:
        """Check if system message already exists."""
        for message in self.message_manager.messages:
            if (message.message_type == MessageType.SYSTEM and
                content.lower() in message.content.lower()):
                return True
        return False

    def _update_conversation_info(self):
        """Update conversation header with current stats."""
        if self._connected and self.device_name:
            self.conversation_header.update_conversation_info(
                f"Chat with {self.device_name}",
                participant_count=2,
                message_count=len(self.message_manager.messages),
                last_activity=datetime.now().strftime("%H:%M")
            )

    def _open_chat_settings(self):
        """Open chat settings dialog."""
        # This would open a settings dialog for chat preferences
        print("Opening chat settings...")

    def _clear_chat_history(self):
        """Clear chat history."""
        self.message_manager.clear_history()
        self.message_history.clear()
        self._update_conversation_info()

        # Add system message
        system_msg = self.message_manager.add_message_by_parts(
            sender="System",
            content="Chat history cleared",
            message_type=MessageType.SYSTEM
        )

    def _export_chat_history(self):
        """Export chat history to file."""
        try:
            from tkinter import filedialog
            from utils.chat_history_manager import export_chat_history
            from utils.session import Session

            # Create a temporary session for export
            temp_session = Session()
            temp_session.username = self.username

            # Ask for export location
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ],
                title="Export Chat History"
            )

            if filename:
                # Export using existing functionality
                success = export_chat_history(self.message_manager, temp_session, None)
                if success:
                    messagebox.showinfo("Export Complete", f"Chat history exported to {filename}")
                else:
                    messagebox.showerror("Export Failed", "Failed to export chat history")

        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting chat: {str(e)}")

    def _show_error(self, message: str):
        """Show error message."""
        messagebox.showerror("Chat Error", message)

    def handle_device_connection(self, device_id: str, device_name: str):
        """Handle device connection from pair tab."""
        self.device_id = device_id
        self.device_name = device_name

        # Update status with device info
        if device_id and device_name:
            self.set_status(f"Connected to device: {device_name}")
        else:
            self.set_status("Disconnected")

    def get_message_count(self) -> int:
        """Get total message count."""
        return len(self.message_manager.messages)

    def get_recent_messages(self, count: int = 50) -> List[ChatMessage]:
        """Get recent messages."""
        return self.message_manager.get_recent_messages(count)

    def search_messages(self, query: str) -> List[ChatMessage]:
        """Search messages (delegated to message list)."""
        # This would integrate with the search functionality in ModernMessageList
        results = []
        query_lower = query.lower()
        for message in self.message_manager.messages:
            if query_lower in message.content.lower():
                results.append(message)
        return results

    def set_typing_indicator(self, is_typing: bool):
        """Set typing indicator (for future enhancement)."""
        # This would show when the other user is typing
        pass

    def get_chat_statistics(self) -> Dict:
        """Get chat statistics."""
        return {
            'total_messages': len(self.message_manager.messages),
            'own_messages': len([m for m in self.message_manager.messages if m.is_own_message]),
            'other_messages': len([m for m in self.message_manager.messages if not m.is_own_message]),
            'system_messages': len([m for m in self.message_manager.messages if m.message_type == MessageType.SYSTEM]),
            'connection_time': datetime.now().isoformat() if self._connected else None,
            'device_name': self.device_name
        }
