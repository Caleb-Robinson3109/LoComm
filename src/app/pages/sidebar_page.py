"""Sidebar navigation component for the redesigned UI shell."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from utils.design_system import Colors, ThemeManager, Typography, Spacing
from ui.components import DesignUtils
from ui.helpers import sidebar_container, sidebar_nav_section, sidebar_footer
from utils.chatroom_registry import get_active_code, register_chatroom_listener, unregister_chatroom_listener


class SidebarPage(tk.Frame):
    """Left sidebar navigation component for main navigation."""

    def __init__(
        self,
        master,
        nav_items: list[tuple[str, str]],
        on_nav_select: Optional[Callable[[str], None]] = None,
        on_theme_toggle: Optional[Callable[[bool], None]] = None,
        on_back: Optional[Callable[[], None]] = None,
    ):
        ThemeManager.ensure()
        super().__init__(master, width=Spacing.SIDEBAR_WIDTH, relief="flat", bd=0, bg=Colors.BG_ELEVATED)
        self.on_nav_select = on_nav_select
        self.on_theme_toggle = on_theme_toggle
        self.on_back = on_back
        self.nav_items = nav_items
        self.current_view = nav_items[0][0] if nav_items else "home"
        self._peers_enabled = bool(get_active_code())

        self._buttons: dict[str, ttk.Button] = {}
        self._chatroom_listener = lambda code: self._update_peer_access(bool(code))

        self.container = sidebar_container(self)
        tk.Frame(self.container, height=int(Spacing.XL * 1.5), bg=Colors.SURFACE_SIDEBAR).pack(fill=tk.X)

        self._build_nav_sections()
        self._build_footer()
        self._update_active_button(self.current_view)
        register_chatroom_listener(self._chatroom_listener)

    def _build_nav_sections(self):
        # Back button at the very top
        if self.on_back:
            back_btn = DesignUtils.create_nav_button(self.container, text="← Back", command=self.on_back)
            back_btn.pack(fill=tk.X, pady=(0, Spacing.MD))

        top_items = []
        bottom_items = []
        for key, label in self.nav_items:
            if key in ("settings", "about", "help"):
                bottom_items.append((key, label))
            else:
                top_items.append((key, label))

        self.nav_frame = sidebar_nav_section(
            self.container, top_items, self._handle_nav_click, self._register_nav_button
        )

        self.spacer = tk.Frame(self.container, bg=Colors.SURFACE_SIDEBAR)
        self.spacer.pack(fill=tk.BOTH, expand=True)

        self.bottom_frame = sidebar_nav_section(
            self.container, bottom_items, self._handle_nav_click, self._register_nav_button
        )
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(Spacing.LG, 0))

    def _build_footer(self):
        sidebar_footer(self, "v2.3.0 Desktop")

    # ------------------------------------------------------------------ #
    def _update_peer_access(self, enabled: bool):
        self._peers_enabled = enabled
        peer_btn = self._buttons.get("pair")
        if peer_btn:
            peer_btn.configure(state="normal" if enabled else "disabled")

    def _update_active_button(self, active_view: str):
        for key, button in self._buttons.items():
            style = "Locomm.NavActive.TButton" if key == active_view else "Locomm.Nav.TButton"
            button.configure(style=style)
        # Keep peers disabled when no active chatroom
        if not self._peers_enabled:
            self._update_peer_access(False)

    def _register_nav_button(self, key: str, button: ttk.Button):
        self._buttons[key] = button

    def _handle_nav_click(self, route_id: str):
        if route_id == "pair" and not self._peers_enabled:
            return
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

    # Public helpers ------------------------------------------------------ #
    def show_chat(self):
        self._handle_nav_click("chat")

    def show_pair(self):
        self._handle_nav_click("pair")

    def show_home(self):
        self._handle_nav_click("home")

    def show_settings(self):
        self._handle_nav_click("settings")

    def destroy(self):
        unregister_chatroom_listener(self._chatroom_listener)
        super().destroy()
