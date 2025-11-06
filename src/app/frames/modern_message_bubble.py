"""Modern message bubble component with sophisticated layout and delivery indicators."""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from datetime import datetime
from .chat_models import ChatMessage, MessageStatus
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class MessageActionButton(ttk.Button):
    """Individual action button for message operations."""

    def __init__(self, parent, action_type: str, icon: str, tooltip: str, command: Callable):
        super().__init__(parent, text=icon, style='MessageAction.TButton',
                        command=command, width=3)

        # Apply hover effects
        DesignUtils.apply_hover_effect(self, Colors.BG_TERTIARY)

        # Add tooltip
        DesignUtils.create_tooltip_text(self, tooltip)

        # Store action type
        self.action_type = action_type

        # Configure styling
        self.configure(
            relief="flat",
            borderwidth=0,
            cursor="hand2"
        )


class ModernMessageBubble(ttk.Frame):
    """Sophisticated message bubble with modern chat application styling."""

    def __init__(self, master, message: ChatMessage, show_username: bool = True,
                 on_message_action: Optional[Callable] = None):
        super().__init__(master)
        self.message = message
        self.is_own = message.is_own_message
        self.show_username = show_username
        self.on_message_action = on_message_action
        self.action_buttons: list[MessageActionButton] = []
        self.hide_timer = None  # Initialize hide_timer attribute

        # Configure frame styling
        self.configure(style='ChatFrame.TFrame')
        self.pack_configure(padx=Spacing.MESSAGE_MARGIN[0], pady=Spacing.MESSAGE_MARGIN[1])

        # Create the message bubble
        self._create_bubble()

        # Add hover effects
        self._add_hover_effects()

    def _create_bubble(self):
        """Create the complete message bubble layout."""
        # Main container
        container = ttk.Frame(self)
        container.pack(fill=tk.X, expand=True)

        # Username and timestamp header (for other users and system messages)
        if not self.is_own or self.message.sender.lower() == "system":
            self._create_header(container)

        # Message bubble content
        self._create_bubble_content(container)

        # Action buttons (hidden by default, show on hover)
        self._create_action_buttons(container)

        # Own message status indicators
        if self.is_own and self.message.sender.lower() != "system":
            self._create_status_indicators(container)

    def _create_header(self, parent):
        """Create message header with username and timestamp."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(anchor="w", pady=(0, Spacing.XS))

        # Username label
        username_text = self.message.sender if self.show_username else ""
        if username_text:
            username_color = Colors.MESSAGE_OTHER if not self.is_own else Colors.MESSAGE_ME

            username_label = tk.Label(
                header_frame,
                text=username_text,
                font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD),
                fg=username_color,
                bg=Colors.BG_CHAT_AREA,
                cursor="hand2"
            )
            username_label.pack(side=tk.LEFT)
            username_label.bind("<Button-1>", lambda e: self._on_username_click())

        # Timestamp label (right-aligned)
        timestamp_text = self.message.formatted_time
        timestamp_label = tk.Label(
            header_frame,
            text=timestamp_text,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XS),
            fg=Colors.TEXT_TIMESTAMP,
            bg=Colors.BG_CHAT_AREA,
            cursor="hand2"
        )
        timestamp_label.pack(side=tk.RIGHT)
        timestamp_label.bind("<Button-1>", lambda e: self._on_timestamp_click())

    def _create_bubble_content(self, parent):
        """Create the main message bubble content."""
        # Main message frame
        message_frame = DesignUtils.create_message_bubble(parent, self.is_own)
        message_frame.pack(
            anchor="e" if self.is_own else "w",
            fill=tk.X,
            expand=True,
            pady=(Spacing.SM, 0)
        )

        # Message text with proper word wrapping
        message_text = self.message.content
        message_color = (
            Colors.MESSAGE_OWN_TEXT if self.is_own else
            Colors.MESSAGE_OTHER_TEXT if self.message.sender.lower() != "system" else
            Colors.MESSAGE_SYSTEM_TEXT
        )

        # Create scrollable text widget for long messages
        self.message_text = tk.Text(
            message_frame,
            wrap="word",
            height=1,  # Auto-height based on content
            font=(Typography.FONT_CHAT, Typography.SIZE_MD),
            fg=message_color,
            bg=Colors.BG_MESSAGE_OWN if self.is_own else Colors.BG_MESSAGE_OTHER,
            relief="flat",
            bd=0,
            cursor="ibeam",
            selectbackground=Colors.BTN_PRIMARY,
            selectforeground=Colors.TEXT_PRIMARY,
            highlightthickness=0
        )
        self.message_text.pack(fill=tk.X, expand=True)
        self.message_text.insert("1.0", message_text)
        self.message_text.config(state="disabled")

        # Bind selection and click events
        self.message_text.bind("<Button-1>", lambda e: self._on_message_click())
        self.message_text.bind("<Double-Button-1>", lambda e: self._on_message_double_click())

        # Configure tags for better text rendering
        self._configure_text_tags()

    def _configure_text_tags(self):
        """Configure text tags for proper message rendering."""
        # Configure tag for selected text
        if hasattr(self, 'message_text'):
            self.message_text.tag_configure(
                "selected",
                background=Colors.BTN_PRIMARY,
                foreground=Colors.TEXT_PRIMARY
            )

    def _create_action_buttons(self, parent):
        """Create message action buttons (copy, reply, etc.)."""
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(anchor="e", pady=(Spacing.XS, 0))

        # Hide initially, show on hover
        actions_frame.pack_forget()
        self.actions_frame = actions_frame

        # Define available actions
        actions = [
            ("copy", "📋", "Copy message"),
            ("reply", "↩️", "Reply to message"),
            ("edit", "✏️", "Edit message"),
            ("delete", "🗑️", "Delete message")
        ]

        for action_type, icon, tooltip in actions:
            if action_type == "edit" and not self.is_own:
                continue  # Only allow editing own messages

            btn = MessageActionButton(
                actions_frame,
                action_type,
                icon,
                tooltip,
                lambda at=action_type: self._on_action_click(at)
            )
            btn.pack(side=tk.RIGHT, padx=(Spacing.XS, 0))
            self.action_buttons.append(btn)

    def _create_status_indicators(self, parent):
        """Create delivery status indicators for own messages."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(anchor="e", pady=(Spacing.XS, 0))

        # Status icon with color
        status_color = DesignUtils.get_delivery_status_color(self.message.status.value)
        status_text = self._get_status_icon()

        status_label = tk.Label(
            status_frame,
            text=status_text,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XS),
            fg=status_color,
            bg=Colors.BG_MESSAGE_OWN if self.is_own else Colors.BG_MESSAGE_OTHER,
            cursor="hand2"
        )
        status_label.pack(side=tk.RIGHT)

        # Add tooltip for status
        DesignUtils.create_tooltip_text(status_label, f"Status: {self.message.status.value.title()}")
        status_label.bind("<Button-1>", lambda e: self._on_status_click())

        self.status_label = status_label

    def _get_status_icon(self) -> str:
        """Get status icon based on message status."""
        icons = {
            MessageStatus.PENDING: "⏳",
            MessageStatus.SENT: "✓",
            MessageStatus.DELIVERED: "✓✓",
            MessageStatus.FAILED: "❌"
        }
        return icons.get(self.message.status, "•")

    def _add_hover_effects(self):
        """Add hover effects to show/hide action buttons."""
        def show_actions(event):
            if hasattr(self, 'actions_frame'):
                # Cancel any pending hide
                if self.hide_timer is not None:
                    self.after_cancel(self.hide_timer)
                    self.hide_timer = None

                # Show action buttons
                self.actions_frame.pack(anchor="e", pady=(Spacing.XS, 0))

        def hide_actions(event):
            # Delay hiding to allow clicking on buttons
            if hasattr(self, 'actions_frame'):
                self.hide_timer = self.after(500, lambda: self.actions_frame.pack_forget())

        # Bind hover events to entire bubble
        self.bind("<Enter>", show_actions)
        self.bind("<Leave>", hide_actions)

        # Also bind to text widget
        if hasattr(self, 'message_text'):
            self.message_text.bind("<Enter>", show_actions)
            self.message_text.bind("<Leave>", hide_actions)

    def _on_message_click(self, event=None):
        """Handle message click event."""
        if self.on_message_action:
            self.on_message_action(self.message, "click")

    def _on_message_double_click(self, event=None):
        """Handle message double-click event (e.g., for selection)."""
        if self.on_message_action:
            self.on_message_action(self.message, "double_click")

    def _on_username_click(self, event=None):
        """Handle username click event."""
        if self.on_message_action:
            self.on_message_action(self.message, "username_click", self.message.sender)

    def _on_timestamp_click(self, event=None):
        """Handle timestamp click event."""
        if self.on_message_action:
            self.on_message_action(self.message, "timestamp_click", self.message.timestamp)

    def _on_status_click(self, event=None):
        """Handle status indicator click event."""
        if self.on_message_action:
            self.on_message_action(self.message, "status_click", self.message.status)

    def _on_action_click(self, action_type: str):
        """Handle action button click."""
        if self.on_message_action:
            self.on_message_action(self.message, f"action_{action_type}")

    def update_status(self, new_status: MessageStatus):
        """Update the message status and refresh display."""
        self.message.status = new_status

        # Update status indicator if it exists
        if hasattr(self, 'status_label'):
            status_color = DesignUtils.get_delivery_status_color(new_status.value)
            status_text = self._get_status_icon()

            self.status_label.config(text=status_text, fg=status_color)

    def select_text(self):
        """Select all text in the message bubble."""
        if hasattr(self, 'message_text'):
            self.message_text.config(state="normal")
            self.message_text.tag_add("sel", "1.0", "end")
            self.message_text.tag_configure("sel", background=Colors.BTN_PRIMARY)
            self.message_text.config(state="disabled")

    def copy_to_clipboard(self):
        """Copy message content to clipboard."""
        content = self.message.content
        self.clipboard_clear()
        self.clipboard_append(content)

    def update_message_content(self, new_content: str):
        """Update the message content."""
        self.message.content = new_content

        if hasattr(self, 'message_text'):
            self.message_text.config(state="normal")
            self.message_text.delete("1.0", "end")
            self.message_text.insert("1.0", new_content)
            self.message_text.config(state="disabled")

    def show_copy_feedback(self):
        """Show visual feedback when message is copied."""
        # Temporary highlight effect using ttk style instead of configure
        original_style = self.cget('style')
        self.configure(style='Primary.TButton')
        self.after(300, lambda: self.configure(style=original_style))

    def get_hover_area(self):
        """Get the hover area for the entire message bubble."""
        return self
