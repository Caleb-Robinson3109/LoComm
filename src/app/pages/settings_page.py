"""Settings page leveraging the refreshed design system."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, Spacing, DesignUtils, ThemeManager, Typography
from utils.ui_helpers import create_page_scaffold
from .base_page import BasePage, PageContext


class SettingsPage(BasePage):
    """Minimal page announcing that settings live here."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.scaffold = create_page_scaffold(
            self,
            title="Locomm Desktop Settings",
            subtitle="Configure notifications and diagnostics.",
            padding=(0, Spacing.LG),
        )
        body = self.scaffold.body

        appearance_card, appearance_content = DesignUtils.card(body, "Appearance", "Adjust how Locomm looks.")
        appearance_card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.LG))
        self._build_theme_toggle(appearance_content)

        card, content = DesignUtils.card(body, "Notifications & diagnostics", "Basic controls")
        card.pack(fill=tk.BOTH, expand=True)
        self._build_toggle(content, "Desktop notifications", True)
        self._build_toggle(content, "Sound alerts", False)
        # Toolbar button removed per latest spec

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
        var = tk.BooleanVar(master=self, value=initial)
        btn = DesignUtils.button(row, text="On" if initial else "Off", variant="ghost")
        btn.pack(side=tk.RIGHT)
        def toggle():
            var.set(not var.get())
            btn.configure(text="On" if var.get() else "Off")
        btn.configure(command=toggle)

    def _build_theme_toggle(self, parent):
        row = tk.Frame(parent, bg=Colors.SURFACE_ALT, padx=Spacing.SM, pady=Spacing.SM)
        row.pack(fill=tk.X, pady=(Spacing.XS, 0))

        tk.Label(
            row,
            text="Dark mode",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
        ).pack(side=tk.LEFT)

        self.theme_var = tk.BooleanVar(value=ThemeManager.current_mode() == "dark")
        toggle_btn = DesignUtils.button(
            row,
            text="On" if self.theme_var.get() else "Off",
            variant="secondary",
            command=self._toggle_theme,
        )
        toggle_btn.pack(side=tk.RIGHT)
        self._theme_button = toggle_btn

    def _toggle_theme(self):
        new_value = not self.theme_var.get()
        self.theme_var.set(new_value)
        if hasattr(self, "_theme_button"):
            self._theme_button.configure(text="On" if new_value else "Off")
        if self.context and hasattr(self.context.app, "toggle_theme"):
            self.context.app.toggle_theme(new_value)

    def on_show(self):
        current = ThemeManager.current_mode() == "dark"
        if hasattr(self, "theme_var"):
            self.theme_var.set(current)
            if hasattr(self, "_theme_button"):
                self._theme_button.configure(text="On" if current else "Off")

    def destroy(self):
        if hasattr(self, "scaffold"):
            self.scaffold.destroy()
        return super().destroy()
