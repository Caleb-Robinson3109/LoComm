"""Sidebar navigation component for the redesigned UI shell."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from utils.design_system import Colors, Typography, Spacing, DesignUtils


class Sidebar(tk.Frame):
    """Left sidebar navigation component for main navigation."""

    def __init__(self, master, nav_items: list[tuple[str, str]],
                 on_nav_select: Optional[Callable[[str], None]] = None,
                 on_theme_toggle: Optional[Callable[[bool], None]] = None):
        super().__init__(master, width=Spacing.SIDEBAR_WIDTH, relief="flat", bd=0, bg=Colors.SURFACE_SIDEBAR)
        self.on_nav_select = on_nav_select
        self.on_theme_toggle = on_theme_toggle
        self.nav_items = nav_items
        self.current_view = nav_items[0][0] if nav_items else "home"

        self._buttons: dict[str, ttk.Button] = {}

        self.container = tk.Frame(self, bg=Colors.SURFACE_SIDEBAR)
        self.container.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)
        tk.Frame(self.container, height=int(Spacing.XL * 1.5), bg=Colors.SURFACE_SIDEBAR).pack(fill=tk.X)

        self._build_nav_sections()
        self._build_footer()
        self._update_active_button(self.current_view)

    def _build_nav_sections(self):
        self.nav_frame = tk.Frame(self.container, bg=Colors.SURFACE_SIDEBAR)
        self.nav_frame.pack(fill=tk.X)

        self.bottom_frame = tk.Frame(self.container, bg=Colors.SURFACE_SIDEBAR)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(Spacing.LG, 0))

        top_items = []
        bottom_items = []
        for key, label in self.nav_items:
            if key in ("settings", "about", "help"):
                bottom_items.append((key, label))
            else:
                top_items.append((key, label))

        self._render_nav_group(self.nav_frame, top_items)

        self.spacer = tk.Frame(self.container, bg=Colors.SURFACE_SIDEBAR)
        self.spacer.pack(fill=tk.BOTH, expand=True)

        self._render_nav_group(self.bottom_frame, bottom_items)

    def _render_nav_group(self, parent, items):
        for key, label in items:
            btn = DesignUtils.create_nav_button(parent, label, lambda k=key: self._handle_nav_click(k))
            btn.pack(fill=tk.X, pady=(0, Spacing.SM))
            self._buttons[key] = btn

    def _build_footer(self):
        footer = tk.Frame(self, bg=Colors.SURFACE_SIDEBAR)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(Spacing.XS, Spacing.XS))
        tk.Label(
            footer,
            text="v2.1 Desktop",
            bg=Colors.SURFACE_SIDEBAR,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w", padx=Spacing.MD, pady=(0, Spacing.XXS))

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
