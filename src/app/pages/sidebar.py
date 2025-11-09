"""Sidebar navigation component for the redesigned UI shell."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from utils.design_system import Colors, Typography, Spacing, DesignUtils, ThemeManager


class Sidebar(tk.Frame):
    """Left sidebar navigation component for main navigation."""

    def __init__(self, master, nav_items: list[tuple[str, str]],
                 on_nav_select: Optional[Callable[[str], None]] = None,
                 on_theme_toggle: Optional[Callable[[bool], None]] = None):
        super().__init__(master, width=Spacing.SIDEBAR_WIDTH, relief="flat", bd=0, bg=Colors.SURFACE_SIDEBAR)
        self.on_nav_select = on_nav_select
        self.on_theme_toggle = on_theme_toggle
        self.current_view = nav_items[0][0] if nav_items else "home"
        self.nav_items = nav_items

        self._dark_mode = tk.BooleanVar(value=ThemeManager.current_mode() == "dark")

        self._buttons: dict[str, ttk.Button] = {}
        self._build_ui()

    # ------------------------------------------------------------------ #
    def _build_ui(self):
        container = tk.Frame(self, bg=Colors.SURFACE_SIDEBAR)
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)

        header = tk.Frame(container, bg=Colors.SURFACE_SIDEBAR)
        header.pack(fill=tk.X, pady=(0, Spacing.LG))
        tk.Label(header, text="Locomm", bg=Colors.SURFACE_SIDEBAR, fg=Colors.TEXT_PRIMARY,
                 font=(Typography.FONT_UI, Typography.SIZE_20, Typography.WEIGHT_BOLD)).pack(anchor="w")
        tk.Label(header, text="Secure LoRa Communication", bg=Colors.SURFACE_SIDEBAR, fg=Colors.TEXT_SECONDARY,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="w")

        for key, label in self.nav_items:
            if key == "mock":
                # Add divider before Mock button
                tk.Frame(container, bg=Colors.DIVIDER, height=1).pack(fill=tk.X, pady=(Spacing.LG, Spacing.SM))
            btn = DesignUtils.create_nav_button(container, label, lambda k=key: self._handle_nav_click(k))
            btn.pack(fill=tk.X, pady=(0, Spacing.SM))
            self._buttons[key] = btn

        tk.Frame(container, bg=Colors.DIVIDER, height=1).pack(fill=tk.X, pady=(Spacing.LG, Spacing.MD))

        footer = tk.Frame(container, bg=Colors.SURFACE_SIDEBAR)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(Spacing.LG, 0))
        self.theme_button = tk.Frame(
            footer,
            bg=Colors.SURFACE_ALT,
            highlightbackground=Colors.DIVIDER,
            highlightthickness=1,
            bd=0,
            padx=Spacing.SM,
            pady=Spacing.XXS
        )
        self.theme_button.pack(fill=tk.X, pady=(0, Spacing.XXS))
        self.theme_button.bind("<Button-1>", self._handle_theme_toggle)
        self.theme_icon = tk.Label(
            self.theme_button,
            text="",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD)
        )
        self.theme_icon.pack(side=tk.LEFT, padx=(0, Spacing.XXS))
        self.theme_label = tk.Label(
            self.theme_button,
            text="",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
            padx=Spacing.SM
        )
        self.theme_label.pack(side=tk.LEFT)
        self._refresh_theme_button()
        tk.Label(footer, text="v2.1 Desktop", bg=Colors.SURFACE_SIDEBAR, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w")

        self._update_active_button("home")

    # ------------------------------------------------------------------ #
    def _update_active_button(self, active_view: str):
        for key, button in self._buttons.items():
            style = "Locomm.NavActive.TButton" if key == active_view else "Locomm.Nav.TButton"
            button.configure(style=style)

    def _handle_nav_click(self, route_id: str):
        self.set_active_view(route_id)
        if self.on_nav_select:
            self.on_nav_select(route_id)

    def set_active_view(self, view_name: str):
        """Public helper so MainFrame can update selection when switching programmatically."""
        self.current_view = view_name
        self._update_active_button(view_name)

    def _handle_theme_toggle(self, _event=None):
        self._dark_mode.set(not self._dark_mode.get())
        self._refresh_theme_button()
        if self.on_theme_toggle:
            self.on_theme_toggle(self._dark_mode.get())

    def _refresh_theme_button(self):
        """Update the appearance of the theme toggle pill."""
        if not hasattr(self, "theme_button"):
            return
        is_dark = self._dark_mode.get()
        icon = "●" if is_dark else "○"
        label = "Dark mode On" if is_dark else "Dark mode Off"
        bg = Colors.SURFACE_ALT if is_dark else Colors.SURFACE_SELECTED
        fg = Colors.TEXT_PRIMARY
        self.theme_button.configure(bg=bg)
        self.theme_icon.configure(text=icon, bg=bg, fg=fg)
        self.theme_label.configure(text=label, bg=bg, fg=fg)

    def set_status(self, status_text: str):
        """Compatibility stub so main_frame can call without popup badge."""
        return
    # Public helpers ------------------------------------------------------
    def show_chat(self):
        self._handle_nav_click("chat")

    def show_pair(self):
        self._handle_nav_click("pair")

    def show_home(self):
        self._handle_nav_click("home")

    def show_settings(self):
        self._handle_nav_click("settings")

    def destroy(self):
        super().destroy()
