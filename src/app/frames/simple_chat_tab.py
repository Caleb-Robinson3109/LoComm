"""Simplified chat tab for minimal messaging experience."""
import tkinter as tk
from tkinter import ttk, messagebox
import time
from utils.design_system import Colors, Typography, Spacing, DesignUtils
from .simple_message_list import SimpleMessageList
from .simple_message_composer import SimpleMessageComposer


class SimpleChatTab(tk.Frame):
    """Simplified chat tab with minimal messaging interface."""

    def __init__(self, master, transport, username, on_disconnect=None):
        super().__init__(master, bg=Colors.BG_PRIMARY)
        self.transport = transport
        self.username = username
        self.on_disconnect = on_disconnect
        self.messages = []
        self.device_id = "Unknown"  # Will be updated from paired device
        self.paired_username = "Unknown"  # Will be updated from paired device
        self.is_connected = False

        self._create_ui()

    def _create_ui(self):
        """Create the simplified chat interface."""
        # Configure frame to be responsive
        self.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)

        # Create header section with device info (like settings tab)
        self._create_header_section()

        # Create main container for message area and composer
        main_area = tk.Frame(self, bg=Colors.BG_PRIMARY)
        main_area.pack(fill=tk.BOTH, expand=True)

        # Configure main_area grid weights for 71/29 split (71% message, 29% composer)
        main_area.grid_rowconfigure(0, weight=71)  # Message area gets 71% of space
        main_area.grid_rowconfigure(1, weight=29)  # Composer gets 29% of space
        main_area.grid_columnconfigure(0, weight=1)  # Single column

        # Create message area container (71% height)
        self.message_container = tk.Frame(main_area, bg=Colors.BG_PRIMARY)
        self.message_container.grid(row=0, column=0, sticky="nsew", pady=(0, Spacing.SM))

        # Message list (scrollable)
        self.message_list = SimpleMessageList(self.message_container, self.messages)
        self.message_list.pack(fill=tk.BOTH, expand=True)

        # Message composer with embedded send button (29% height)
        self.composer = SimpleMessageComposer(
            main_area,
            on_send=self._handle_send_message
        )
        self.composer.grid(row=1, column=0, sticky="ew", pady=(0, 0))

    def _create_header_section(self):
        """Create header section with device info and controls."""
        header_section = ttk.LabelFrame(self, text="Device Information")
        header_section.pack(fill=tk.X, pady=(0, Spacing.MD))

        header_content = ttk.Frame(header_section)
        header_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # Device info row
        info_frame = ttk.Frame(header_content)
        info_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Device ID
        ttk.Label(info_frame, text="Device ID:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(side=tk.LEFT)
        ttk.Label(info_frame, text=self.device_id,
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM)).pack(side=tk.LEFT, padx=(Spacing.SM, 0))

        # Username
        ttk.Label(info_frame, text="Username:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(side=tk.RIGHT)
        ttk.Label(info_frame, text=self.paired_username,
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM)).pack(side=tk.RIGHT, padx=(0, Spacing.SM))

        # Status and buttons row
        status_frame = ttk.Frame(header_content)
        status_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Status indicator
        self.status_label = ttk.Label(status_frame, text="Status: Disconnected",
                                     font=(Typography.FONT_PRIMARY, Typography.SIZE_SM))
        self.status_label.pack(side=tk.LEFT)

        # Buttons frame
        buttons_frame = ttk.Frame(status_frame)
        buttons_frame.pack(side=tk.RIGHT)

        # Clear chat button
        DesignUtils.create_styled_button(buttons_frame, text="Clear Chat", command=self._clear_chat,
                                        style='Secondary.TButton').pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        # Disconnect button
        DesignUtils.create_styled_button(buttons_frame, text="Disconnect", command=self._disconnect,
                                        style='Danger.TButton').pack(side=tk.RIGHT)


    def _handle_send_message(self, message_text):
        """Handle sending a message."""
        if not message_text.strip():
            return

        # Add message to local list
        message_data = {
            'sender': self.username,
            'message': message_text.strip(),
            'timestamp': self._get_current_time(),
            'status': 'sent'
        }
        self.messages.append(message_data)

        # Update UI
        self.message_list.add_message(message_data)

        # Send via transport if available
        if self.transport and hasattr(self.transport, 'send'):
            try:
                self.transport.send(self.username, message_text.strip())
            except Exception:
                pass

    def _get_current_time(self):
        """Get current timestamp for messages."""
        return time.strftime("%H:%M")

    def _clear_chat(self):
        """Clear all messages from the chat."""
        result = messagebox.askyesno("Clear Chat", "Are you sure you want to clear all messages?")
        if result:
            self.clear_history()
            # Add status message after clearing
            self._add_status_message("Chat cleared")

    def _disconnect(self):
        """Handle disconnect request."""
        # Add status message before disconnecting
        self._add_status_message("Disconnected from device")
        self.is_connected = False
        self.update_status("Disconnected")
        if self.on_disconnect:
            self.on_disconnect()

    def _add_status_message(self, message_text):
        """Add a status message to the chat."""
        status_message_data = {
            'sender': 'System',
            'message': message_text,
            'timestamp': self._get_current_time(),
            'status': 'system'
        }
        self.messages.append(status_message_data)
        self.message_list.add_message(status_message_data)

    def append_line(self, sender, msg):
        """Append incoming message to the chat."""
        message_data = {
            'sender': sender,
            'message': msg,
            'timestamp': self._get_current_time(),
            'status': 'received'
        }
        self.messages.append(message_data)
        self.message_list.add_message(message_data)

    def clear_history(self):
        """Clear all messages from the chat."""
        self.messages.clear()
        self.message_list.clear_messages()

    def clear_messages(self):
        """Alias for clear_history to maintain interface compatibility."""
        self.clear_history()

    def update_status(self, status_text):
        """Update status display."""
        self.status_label.configure(text=f"Status: {status_text}")
        if "connected" in status_text.lower():
            self.is_connected = True
        else:
            self.is_connected = False

    def handle_device_connection(self, device_id, device_name):
        """Handle device connection state change."""
        if device_id and device_name:
            self.device_id = device_id
            self.username = device_name
            self.update_status("Connected")
        else:
            self.update_status("Disconnected")
