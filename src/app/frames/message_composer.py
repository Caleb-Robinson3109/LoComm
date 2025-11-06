"""Enhanced message composer with multi-line support and shortcuts."""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class MessageComposer(ttk.Frame):
    """Enhanced message input component with multi-line support."""

    def __init__(self, master, on_send: Optional[Callable[[str], None]] = None):
        super().__init__(master)
        self.on_send = on_send
        self._connected = False
        self._message_queue = []

        # Create UI
        self._create_ui()

        # Start with input disabled
        self._set_input_state(False)

    def _create_ui(self):
        """Create the message composer UI."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.X, expand=True)

        # ---------- Input Area ---------- #
        input_container = ttk.Frame(main_frame)
        input_container.pack(fill=tk.X, expand=True, padx=Spacing.TAB_PADDING)

        # Text input with enhanced styling
        self.text_widget = tk.Text(
            input_container,
            height=3,  # Multi-line support
            wrap="word",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#FFFFFF",  # White text
            bg="#2D2D2D",  # Dark background
            relief="flat",
            bd=1
        )
        self.text_widget.pack(fill=tk.X, expand=True, side=tk.LEFT)

        # Bind keyboard shortcuts
        self._bind_shortcuts()

        # Send button
        self.send_btn = DesignUtils.create_styled_button(
            input_container, "Send", self._send_message,
            style='Primary.TButton'
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(Spacing.MD, 0), pady=(0, Spacing.SM))

        # Character counter
        self.char_counter = ttk.Label(
            input_container,
            text="0/500",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            foreground="#FFFFFF"  # White text
        )
        self.char_counter.pack(side=tk.RIGHT, padx=(Spacing.SM, 0), pady=(Spacing.SM, 0))

        # Bind character counting
        self.text_widget.bind("<KeyRelease>", self._update_char_counter)

        # Tips footer
        tips_frame = ttk.Frame(main_frame)
        tips_frame.pack(fill=tk.X, padx=Spacing.TAB_PADDING, pady=(Spacing.XS, 0))

        ttk.Label(
            tips_frame,
            text="Press Ctrl+Enter for new line, Enter to send",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XS),
            foreground="#FFFFFF"  # White text
        ).pack(side=tk.LEFT)

        # Connection status indicator
        self.connection_status = ttk.Label(
            tips_frame,
            text="Not Connected",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XS),
            foreground="#FFFFFF"  # White text
        )
        self.connection_status.pack(side=tk.RIGHT)

    def _bind_shortcuts(self):
        """Bind keyboard shortcuts for better UX."""
        def on_key_press(event):
            # Ctrl+Enter = new line
            if event.keysym == "Return" and event.state & 0x4:  # Control key
                # Insert new line normally
                return

            # Enter alone = send message
            elif event.keysym == "Return":
                self._send_message()
                return "break"  # Prevent default newline insertion

        self.text_widget.bind("<KeyPress>", on_key_press)

    def _update_char_counter(self, event=None):
        """Update character counter."""
        content = self.text_widget.get("1.0", "end-1c")  # Get text without final newline
        char_count = len(content)

        # Limit to 500 characters
        if char_count > 500:
            # Truncate if over limit
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", content[:500])
            char_count = 500

        # Update counter display
        counter_text = f"{char_count}/500"
        self.char_counter.config(text=counter_text)

        # Always white text, no color changes
        self.char_counter.config(foreground="#FFFFFF")

    def _send_message(self):
        """Send the current message."""
        if not self._connected:
            return

        content = self.text_widget.get("1.0", "end-1c").strip()
        if not content:
            return

        # Clear input
        self.text_widget.delete("1.0", "end")
        self._update_char_counter()

        # Call send callback
        if self.on_send:
            self.on_send(content)

        # Focus back to input
        self.text_widget.focus_set()

    def _set_input_state(self, enabled: bool):
        """Enable or disable the input components."""
        self._connected = enabled

        state = "normal" if enabled else "disabled"
        self.text_widget.config(state=state)
        self.send_btn.config(state=state)

        # Update connection status display
        if enabled:
            self.connection_status.config(
                text="Connected",
                foreground="#FFFFFF"  # White text
            )
        else:
            self.connection_status.config(
                text="Not Connected",
                foreground="#FFFFFF"  # White text
            )

        # Clear text if disabling
        if not enabled:
            self.text_widget.delete("1.0", "end")
            self._update_char_counter()

    def set_connection_status(self, connected: bool):
        """Update connection status externally."""
        self._set_input_state(connected)

    def focus_input(self):
        """Focus the input widget."""
        self.text_widget.focus_set()

    def get_input_text(self) -> str:
        """Get the current input text."""
        return self.text_widget.get("1.0", "end-1c").strip()

    def clear_input(self):
        """Clear the input text."""
        self.text_widget.delete("1.0", "end")
        self._update_char_counter()

    def append_text(self, text: str):
        """Append text to the input (for drafts or restore)."""
        self.text_widget.insert("end", text)
        self._update_char_counter()
