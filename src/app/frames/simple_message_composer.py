"""Simplified message composer with embedded send button."""
import tkinter as tk
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class SimpleMessageComposer(tk.Frame):
    """Simple message composer with text input and send button."""

    def __init__(self, master, on_send=None):
        super().__init__(master, bg=Colors.BG_PRIMARY)
        self.on_send = on_send

        self._create_ui()

    def _create_ui(self):
        """Create the composer interface."""
        # Main container - configure to allow expansion
        composer_frame = tk.Frame(self, bg=Colors.BG_PRIMARY)
        composer_frame.pack(fill=tk.X, expand=True)

        # Create input container that takes 60% of width (reduced by 40%)
        input_container = tk.Frame(composer_frame, bg=Colors.BG_PRIMARY)
        input_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))

        # Text input field - now constrained to 60% width
        self.text_input = tk.Text(
            input_container,
            height=2,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=8,
            wrap=tk.WORD
        )
        self.text_input.pack(fill=tk.X)
        self.text_input.bind("<Control-Return>", self._on_send_click)
        self.text_input.bind("<Return>", self._on_send_click)  # Enter sends message

        # Send button using DesignUtils (like settings tab) - stays on right
        self.send_btn = DesignUtils.create_styled_button(
            composer_frame,
            text="Send",
            command=self._on_send_click,
            style='Primary.TButton'
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(0, 0), pady=0)

        # Focus on text input
        self.text_input.focus_set()

    def _on_send_click(self, event=None):
        """Handle send button click or Enter key."""
        message_text = self.text_input.get("1.0", tk.END).strip()
        if message_text and self.on_send:
            self.on_send(message_text)
            self.text_input.delete("1.0", tk.END)

    def clear_input(self):
        """Clear the text input."""
        self.text_input.delete("1.0", tk.END)
        self.text_input.focus_set()

    def get_input(self):
        """Get the current text input."""
        return self.text_input.get("1.0", tk.END).strip()

    def focus_input(self):
        """Focus the text input."""
        self.text_input.focus_set()
