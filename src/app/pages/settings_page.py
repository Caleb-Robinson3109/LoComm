"""Settings page leveraging the refreshed design system."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, Spacing, DesignUtils
from utils.ui_helpers import create_scroll_container
from .base_page import BasePage, PageContext


class SettingsPage(BasePage):
    """Minimal page announcing that settings live here."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(0, Spacing.LG))
        body = scroll.frame

        DesignUtils.hero_header(
            body,
            title="Locomm Desktop Settings",
            subtitle="Configure notifications and diagnostics."
        )

        card, content = DesignUtils.card(body, "Notifications & diagnostics", "Basic controls")
        card.pack(fill=tk.BOTH, expand=True)
        self._build_toggle(content, "Desktop notifications", True)
        self._build_toggle(content, "Sound alerts", False)
        DesignUtils.button(content, text="Export diagnostics", variant="secondary").pack(anchor="w", pady=(Spacing.SM, 0))

    def _build_toggle(self, parent, label, initial):
        row = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        row.pack(fill=tk.X, pady=(Spacing.XS, 0))
        tk.Label(
            row,
            text=label,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=("TkDefaultFont", 11, "bold"),
        ).pack(side=tk.LEFT)
        var = tk.BooleanVar(value=initial)
        btn = DesignUtils.button(row, text="On" if initial else "Off", variant="ghost")
        btn.pack(side=tk.RIGHT)
        def toggle():
            var.set(not var.get())
            btn.configure(text="On" if var.get() else "Off")
        btn.configure(command=toggle)
