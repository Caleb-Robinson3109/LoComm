"""Custom styled dialogs to replace native tkinter messageboxes."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from ui.components import DesignUtils
from ui.theme_tokens import Colors, Spacing, Typography, Space
from ui.theme_manager import ThemeManager


class CustomDialog(tk.Toplevel):
    """Base class for custom styled dialogs."""

    def __init__(self, parent, title: str, message: str, width: int = 400):
        super().__init__(parent)
        ThemeManager.ensure()
        self.title(title)
        self.configure(bg=Colors.SURFACE)
        self.transient(parent)
        self.resizable(False, False)
        
        # Calculate position to center on parent
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Estimate height based on content
        height = 200 
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main container
        self.container = tk.Frame(self, bg=Colors.SURFACE, padx=Spacing.LG, pady=Spacing.LG)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            self.container,
            text=title,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
            anchor="w"
        ).pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # Message
        tk.Label(
            self.container,
            text=message,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR),
            wraplength=width - (Spacing.LG * 2),
            justify="left",
            anchor="w"
        ).pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.XL))
        
        # Buttons area
        self.button_frame = tk.Frame(self.container, bg=Colors.SURFACE)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.result = None
        
        # Modal behavior
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.focus_set()

    def _on_close(self):
        self.destroy()

    def add_button(self, text: str, command: Callable, variant: str = "primary", width: int = 10):
        btn = DesignUtils.button(
            self.button_frame,
            text=text,
            command=lambda: [command(), self.destroy()],
            variant=variant,
            width=width
        )
        btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        return btn


class Dialogs:
    """Static helper methods to show dialogs."""

    @staticmethod
    def show_info(parent, title: str, message: str):
        """Show an information dialog."""
        dlg = CustomDialog(parent, title, message)
        dlg.add_button("OK", lambda: None, variant="primary")
        parent.wait_window(dlg)

    @staticmethod
    def show_error(parent, title: str, message: str):
        """Show an error dialog."""
        dlg = CustomDialog(parent, title, message)
        dlg.add_button("OK", lambda: None, variant="danger")
        parent.wait_window(dlg)

    @staticmethod
    def ask_yes_no(parent, title: str, message: str) -> bool:
        """Show a Yes/No confirmation dialog. Returns True for Yes."""
        dlg = CustomDialog(parent, title, message)
        result = {"value": False}
        
        def on_yes():
            result["value"] = True
            
        dlg.add_button("Yes", on_yes, variant="primary")
        dlg.add_button("No", lambda: None, variant="secondary")
        
        parent.wait_window(dlg)
        return result["value"]
