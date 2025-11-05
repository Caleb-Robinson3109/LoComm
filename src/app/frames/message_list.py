"""Enhanced message list component with bubble-style display."""
import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable
from .chat_models import ChatMessage, MessageManager, MessageType, MessageStatus
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class MessageBubble(ttk.Frame):
    """Individual message bubble with enhanced styling."""

    def __init__(self, master, message: ChatMessage):
        super().__init__(master)
        self.message = message
        self.is_own = message.is_own_message

        # Configure padding and styling
        self.configure(padding=(Spacing.MD, Spacing.SM))

        # Create message layout
        self._create_bubble()

    def _create_bubble(self):
        """Create the visual bubble for the message."""
        # Main bubble frame
        bubble_frame = ttk.Frame(self)
        bubble_frame.pack(fill=tk.X, expand=True)

        # Sender and time header (only for other people's messages)
        if not self.is_own and self.message.sender != "System":
            sender_label = ttk.Label(
                bubble_frame,
                text=self.message.sender,
                font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD),
                foreground=Colors.TEXT_PRIMARY
            )
            sender_label.pack(anchor="w", pady=(0, Spacing.XS))

        # Message content with proper alignment
        align = "e" if self.is_own else "w"

        # Create message text with background
        content_frame = ttk.Frame(bubble_frame)
        content_frame.pack(fill=tk.X, anchor=align)

        # Message text
        text_widget = tk.Text(
            content_frame,
            wrap="word",
            height=1,  # Auto-height
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#FFFFFF",  # White text
            relief="flat",
            bd=0,
            cursor="arrow"
        )
        text_widget.pack(fill=tk.X, anchor=align)
        text_widget.insert("1.0", self.message.content)
        text_widget.config(state="disabled")

        # Status and time footer (only for own messages)
        if self.is_own:
            footer_frame = ttk.Frame(content_frame)
            footer_frame.pack(anchor="e", pady=(Spacing.XS, 0))

            # Status icon
            status_label = ttk.Label(
                footer_frame,
                text=self.message.status_icon,
                font=(Typography.FONT_PRIMARY, Typography.SIZE_XS),
                foreground="#FFFFFF"  # White text
            )
            status_label.pack(side=tk.RIGHT, padx=(Spacing.XS, 0))

            # Timestamp
            time_label = ttk.Label(
                footer_frame,
                text=self.message.formatted_time,
                font=(Typography.FONT_PRIMARY, Typography.SIZE_XS),
                foreground="#FFFFFF"  # White text
            )
            time_label.pack(side=tk.RIGHT)
        else:
            # Just timestamp for other messages
            time_label = ttk.Label(
                bubble_frame,
                text=self.message.formatted_time,
                font=(Typography.FONT_PRIMARY, Typography.SIZE_XS),
                foreground="#FFFFFF"  # White text
            )
            time_label.pack(anchor="w", pady=(Spacing.XS, 0))


class MessageList(ttk.Frame):
    """Enhanced message display with bubble-style UI."""

    def __init__(self, master, message_manager: MessageManager):
        super().__init__(master)
        self.message_manager = message_manager
        self.message_widgets: List[MessageBubble] = []

        # Register for message updates
        self.message_manager.on_message_update(self._on_message_update)
        self.message_manager.on_history_update(self._on_history_update)

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create the message list UI."""
        # Main scrollable frame
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel
        self._bind_mousewheel()

        # Load existing messages
        self._load_existing_messages()

    def _bind_mousewheel(self):
        """Bind mouse wheel scrolling."""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")

        self.canvas.bind("<Enter>", _bind_to_mousewheel)
        self.canvas.bind("<Leave>", _unbind_from_mousewheel)

    def _load_existing_messages(self):
        """Load existing messages from message manager."""
        messages = self.message_manager.get_recent_messages(50)
        for message in messages:
            self._add_message_widget(message)

    def _on_message_update(self, message: ChatMessage):
        """Handle new message or message update."""
        # If this is a new message (not an update), add it
        if not any(widget.message.id == message.id for widget in self.message_widgets):
            self._add_message_widget(message)
        else:
            # Update existing message widget
            self._update_message_widget(message)

    def _on_history_update(self):
        """Handle history clearing."""
        # Clear all message widgets
        for widget in self.message_widgets:
            widget.destroy()
        self.message_widgets.clear()

    def _add_message_widget(self, message: ChatMessage):
        """Add a new message bubble."""
        bubble = MessageBubble(self.scrollable_frame, message)
        bubble.pack(fill=tk.X, padx=Spacing.TAB_PADDING, pady=(Spacing.SM, 0))
        self.message_widgets.append(bubble)

        # Auto-scroll to bottom
        self._scroll_to_bottom()

    def _update_message_widget(self, message: ChatMessage):
        """Update an existing message widget (e.g., status change)."""
        for widget in self.message_widgets:
            if widget.message.id == message.id:
                widget.message = message
                # Update the status display if it's an own message
                if message.is_own_message:
                    # Find and update status icon and timestamp
                    # For now, just refresh the bubble
                    widget.destroy()
                    new_bubble = MessageBubble(self.scrollable_frame, message)
                    new_bubble.pack(fill=tk.X, padx=Spacing.TAB_PADDING, pady=(Spacing.SM, 0))
                    # Replace in widgets list
                    index = self.message_widgets.index(widget)
                    self.message_widgets[index] = new_bubble
                break

    def _scroll_to_bottom(self):
        """Scroll the canvas to show the latest message."""
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def clear_messages(self):
        """Clear all messages from display."""
        self.message_manager.clear_history()
