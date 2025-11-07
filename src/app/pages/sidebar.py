"""Sidebar navigation component for the redesigned UI shell."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from utils.design_system import Colors, Typography, Spacing, DesignUtils, ThemeManager
from utils.status_manager import get_status_manager, DeviceInfo


class Sidebar(tk.Frame):
    """Left sidebar navigation component with connection summary."""

    def __init__(self, master, on_home_click: Optional[Callable] = None,
                 on_chat_click: Optional[Callable] = None,
                 on_pair_click: Optional[Callable] = None,
                 on_settings_click: Optional[Callable] = None,
                 on_about_click: Optional[Callable] = None,
                 on_theme_toggle: Optional[Callable[[bool], None]] = None):
        super().__init__(master, width=Spacing.SIDEBAR_WIDTH, relief="flat", bd=0, bg=Colors.SURFACE_SIDEBAR)
        self.on_home_click = on_home_click
        self.on_chat_click = on_chat_click
        self.on_pair_click = on_pair_click
        self.on_settings_click = on_settings_click
        self.on_about_click = on_about_click
        self.on_theme_toggle = on_theme_toggle
        self.current_view = "home"

        # Use consolidated status manager for consistent status display
        self.status_manager = get_status_manager()
        from utils.design_system import ThemeManager
        self._dark_mode = tk.BooleanVar(value=ThemeManager.current_mode() == "dark")

        # Register for consolidated status updates
        self.status_manager.register_status_callback(self._on_status_change)
        self.status_manager.register_device_callback(self._on_device_change)
        self.status_manager.register_connection_callback(self._on_connection_change)

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

        nav_items = [
            ("home", "Home", self._on_home_click),
            ("chat", "Chat", self._on_chat_click),
            ("pair", "Pair Device", self._on_pair_click),
            ("settings", "Settings", self._on_settings_click),
            ("about", "About", self._on_about_click),
        ]

        for key, label, handler in nav_items:
            btn = DesignUtils.create_nav_button(container, label, handler)
            btn.pack(fill=tk.X, pady=(0, Spacing.SM))
            self._buttons[key] = btn

        tk.Frame(container, bg=Colors.DIVIDER, height=1).pack(fill=tk.X, pady=(Spacing.LG, Spacing.MD))

        # Connection summary card
        card = tk.Frame(container, bg=Colors.SURFACE_ALT, highlightbackground=Colors.DIVIDER, highlightthickness=1, bd=0)
        card.pack(fill=tk.X, pady=(0, Spacing.LG))
        tk.Label(card, text="Device Status", bg=Colors.SURFACE_ALT, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w", padx=Spacing.MD, pady=(Spacing.SM, 0))
        self.status_value = tk.Label(card, text="Disconnected", bg=Colors.SURFACE_ALT, fg=Colors.STATE_ERROR,
                                     font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD))
        self.status_value.pack(anchor="w", padx=Spacing.MD, pady=(0, Spacing.XXS))
        self.device_caption = tk.Label(card, text="No device connected", bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                                       font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR))
        self.device_caption.pack(anchor="w", padx=Spacing.MD, pady=(0, Spacing.SM))
        footer = tk.Frame(container, bg=Colors.SURFACE_SIDEBAR)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(Spacing.LG, 0))
        ttk.Checkbutton(
            footer,
            text="Dark mode",
            variable=self._dark_mode,
            command=self._toggle_theme
        ).pack(anchor="w")
        tk.Label(footer, text="v2.1 Desktop", bg=Colors.SURFACE_SIDEBAR, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w")

        self._update_active_button("home")

    # ------------------------------------------------------------------ #
    def _update_active_button(self, active_view: str):
        for key, button in self._buttons.items():
            style = "Locomm.NavActive.TButton" if key == active_view else "Locomm.Nav.TButton"
            button.configure(style=style)

    def _on_home_click(self):
        self.current_view = "home"
        self._update_active_button("home")
        if self.on_home_click:
            self.on_home_click()

    def _on_chat_click(self):
        self.current_view = "chat"
        self._update_active_button("chat")
        if self.on_chat_click:
            self.on_chat_click()

    def _on_pair_click(self):
        self.current_view = "pair"
        self._update_active_button("pair")
        if self.on_pair_click:
            self.on_pair_click()

    def _on_settings_click(self):
        self.current_view = "settings"
        self._update_active_button("settings")
        if self.on_settings_click:
            self.on_settings_click()

    def _on_about_click(self):
        self.current_view = "about"
        self._update_active_button("about")
        if self.on_about_click:
            self.on_about_click()

    # ------------------------------------------------------------------ #
    def _on_connection_state_change(self, is_connected: bool, device_id: Optional[str], device_name: Optional[str]):
        if is_connected:
            self.status_value.configure(text="Connected", fg=Colors.STATE_SUCCESS)
            label = device_name or device_id or "Active device"
            self.device_caption.configure(text=label)
        else:
            self.status_value.configure(text="Disconnected", fg=Colors.STATE_ERROR)
            self.device_caption.configure(text="No device connected")

    def _on_device_info_change(self, device_info: Optional[dict]):
        if device_info:
            self.device_caption.configure(text=f"{device_info['name']} ({device_info['id']})")

    def _on_legacy_status_change(self, status_text: str, status_color: str):
        # Sidebar mirrors connection events already handled above
        self.status_value.configure(text=status_text, fg=status_color)

    def _toggle_theme(self):
        if self.on_theme_toggle:
            self.on_theme_toggle(self._dark_mode.get())

    # Public helpers ------------------------------------------------------
    def show_chat(self):
        self._on_chat_click()

    def show_pair(self):
        self._on_pair_click()

    def show_home(self):
        self._on_home_click()

    def show_settings(self):
        self._on_settings_click()

    def set_status(self, status_text: str):
        """Compatibility helper for external callers."""
        self.status_value.configure(text=status_text)

    # ------------------------------------------------------------------ #
    # Consolidated status callbacks - these ensure consistent status display
    def _on_status_change(self, status_text: str, status_color: str):
        """Handle consolidated status changes."""
        self.status_value.configure(text=status_text, fg=status_color)

    def _on_device_change(self, device_info: DeviceInfo):
        """Handle device information changes."""
        # Update device caption based on device info
        if device_info.is_connected:
            device_label = device_info.get_display_name()
            self.device_caption.configure(text=device_label)
        else:
            self.device_caption.configure(text="No device connected")

    def _on_connection_change(self, is_connected: bool, device_id: str, device_name: str):
        """Handle connection state changes."""
        # This provides immediate visual feedback for connection changes
        if is_connected:
            self.status_value.configure(text="Connected", fg=Colors.STATE_SUCCESS)
            self.device_caption.configure(text=device_name or device_id or "Active device")
        else:
            self.status_value.configure(text="Disconnected", fg=Colors.STATE_ERROR)
            self.device_caption.configure(text="No device connected")
