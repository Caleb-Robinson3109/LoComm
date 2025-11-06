"""Simplified message list for basic chat display."""
import tkinter as tk
from tkinter import ttk
from utils.design_system import Colors, Typography, Spacing


class SimpleMessageList(tk.Frame):
    """Simple message list displaying messages in scrollable format."""

    def __init__(self, master, messages):
        super().__init__(master, bg=Colors.BG_PRIMARY)
        self.messages = messages
        self._create_ui()

    def _create_ui(self):
        """Create the message display interface."""
        # Configure frame
        self.pack(fill=tk.BOTH, expand=True)

        # Main container with border - responsive
        container = tk.Frame(self, bg=Colors.BG_PRIMARY, relief="sunken", bd=2)
        container.pack(fill=tk.BOTH, expand=True)

        # Scrollable text widget for messages
        self.text_widget = tk.Text(
            container,
            wrap=tk.WORD,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            bg=Colors.BG_PRIMARY,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=Spacing.MD,
            state=tk.DISABLED,
            cursor="arrow"
        )

        # Scrollbar with proper configuration
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self._scroll_text)
        self.text_widget.configure(yscrollcommand=self._on_scroll)

        # Pack widgets with proper fill and expand
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mouse wheel to text widget
        self.text_widget.bind("<MouseWheel>", self._on_mousewheel)
        self.text_widget.bind("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.text_widget.bind("<Button-5>", self._on_mousewheel)  # Linux scroll down

        # Initial message display
        self.refresh_display()

    def _scroll_text(self, *args):
        """Scroll the text widget."""
        if self.text_widget.yview() != args:
            self.text_widget.yview(*args)

    def _on_scroll(self, first, last, **kwargs):
        """Handle scrollbar movement."""
        self.text_widget.yview_moveto(first)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.delta > 0:
            # Scroll up
            self.text_widget.yview_scroll(-1, "units")
        else:
            # Scroll down
            self.text_widget.yview_scroll(1, "units")
        return "break"

    def add_message(self, message_data):
        """Add a new message to the display."""
        sender = message_data.get('sender', 'Unknown')
        message = message_data.get('message', '')
        timestamp = message_data.get('timestamp', '')
        message_type = message_data.get('status', 'user')  # user, received, system

        # Update text widget
        self.text_widget.configure(state=tk.NORMAL)

        if message_type == 'system':
            # Center align system messages
            centered_message = f"[{timestamp}] *** {message} ***\n\n"
            self.text_widget.insert(tk.END, centered_message)
        else:
            # Regular user messages
            formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
            self.text_widget.insert(tk.END, formatted_message)

        self.text_widget.configure(state=tk.DISABLED)

        # Auto-scroll to bottom
        self.text_widget.see(tk.END)

    def clear_messages(self):
        """Clear all messages from the display."""
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.configure(state=tk.DISABLED)

    def refresh_display(self):
        """Refresh the display with current messages."""
        self.clear_messages()

        for message_data in self.messages:
            self.add_message(message_data)

    def scroll_to_bottom(self):
        """Scroll to the bottom of the message list."""
        self.text_widget.see(tk.END)

    def scroll_to_top(self):
        """Scroll to the top of the message list."""
        self.text_widget.see("1.0")
