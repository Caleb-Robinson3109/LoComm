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
                 on_theme_toggle: Optional[Callable[[bool], None]] = None):
        super().__init__(master, width=Spacing.SIDEBAR_WIDTH, relief="flat", bd=0, bg=Colors.SURFACE_SIDEBAR)
        self.on_home_click = on_home_click
        self.on_chat_click = on_chat_click
        self.on_pair_click = on_pair_click
        self.on_settings_click = on_settings_click
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

        # CRITICAL FIX: Track registered callbacks for cleanup
        self._registered_callbacks = [
            ("status", self.status_manager, self._on_status_change),
            ("device", self.status_manager, self._on_device_change),
            ("connection", self.status_manager, self._on_connection_change)
        ]

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
            ("pair", "Devices", self._on_pair_click),
            ("settings", "Settings", self._on_settings_click),
        ]

        for key, label, handler in nav_items:
            btn = DesignUtils.create_nav_button(container, label, handler)
            btn.pack(fill=tk.X, pady=(0, Spacing.SM))
            self._buttons[key] = btn

        tk.Frame(container, bg=Colors.DIVIDER, height=1).pack(fill=tk.X, pady=(Spacing.LG, Spacing.MD))

        # Connection summary card
        card = tk.Frame(container, bg=Colors.SURFACE_ALT, highlightbackground=Colors.DIVIDER, highlightthickness=1, bd=0)
        card.pack(fill=tk.X, pady=(0, Spacing.LG))

        card_header = tk.Frame(card, bg=Colors.SURFACE_ALT)
        card_header.pack(fill=tk.X, padx=Spacing.MD, pady=(Spacing.MD, Spacing.SM))
        tk.Label(card_header, text="Active Device", bg=Colors.SURFACE_ALT, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(side=tk.LEFT, anchor="w")
        self.connection_badge = tk.Label(
            card_header,
            text="Disconnected",
            bg=Colors.STATE_ERROR,
            fg=Colors.SURFACE,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
            padx=Spacing.SM,
            pady=int(Spacing.XS / 2)
        )
        self.connection_badge.pack(side=tk.RIGHT)

        info = tk.Frame(card, bg=Colors.SURFACE_ALT)
        info.pack(fill=tk.X, padx=Spacing.MD, pady=(0, Spacing.MD))
        self.device_title = tk.Label(
            info,
            text="No device paired",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD)
        )
        self.device_title.pack(anchor="w")
        self.device_caption = tk.Label(
            info,
            text="Pair a LoRa contact to begin chatting securely.",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=220,
            justify="left"
        )
        self.device_caption.pack(anchor="w", pady=(Spacing.XXS, 0))

        action_row = tk.Frame(card, bg=Colors.SURFACE_ALT)
        action_row.pack(fill=tk.X, padx=Spacing.MD, pady=(0, Spacing.MD))
        DesignUtils.button(
            action_row,
            text="Pair new device",
            command=self._on_pair_click,
            variant="secondary"
        ).pack(fill=tk.X)

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

    def _on_home_click(self):
        self.set_active_view("home")
        if self.on_home_click:
            self.on_home_click()

    def _on_chat_click(self):
        self.set_active_view("chat")
        if self.on_chat_click:
            self.on_chat_click()

    def _on_pair_click(self):
        self.set_active_view("pair")
        if self.on_pair_click:
            self.on_pair_click()

    def _on_settings_click(self):
        self.set_active_view("settings")
        if self.on_settings_click:
            self.on_settings_click()

    def set_active_view(self, view_name: str):
        """Public helper so MainFrame can update selection when switching programmatically."""
        self.current_view = view_name
        self._update_active_button(view_name)

    # ------------------------------------------------------------------ #
    def _on_connection_state_change(self, is_connected: bool, device_id: Optional[str], device_name: Optional[str]):
        if is_connected:
            label = device_name or device_id or "Active device"
            self._update_device_summary(status_text="Connected", status_color=Colors.STATE_SUCCESS, device_label=label)
        else:
            caption = "Pair a LoRa contact to begin chatting securely."
            if device_name:
                caption = f"Disconnected ({device_name})"
            elif device_id:
                caption = f"Disconnected ({device_id})"
            self._update_device_summary(status_text="Disconnected", status_color=Colors.STATE_ERROR,
                                        device_label="No device paired",
                                        caption=caption)

    def _on_device_info_change(self, device_info: Optional[dict]):
        if device_info:
            self.device_caption.configure(text=f"{device_info['name']} ({device_info['id']})")

    def _on_legacy_status_change(self, status_text: str, status_color: str):
        # Sidebar mirrors connection events already handled above
        self._update_device_summary(status_text=status_text, status_color=status_color)

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
        self._update_device_summary(status_text=status_text)

    # ------------------------------------------------------------------ #
    # Consolidated status callbacks - these ensure consistent status display
    def _on_status_change(self, status_text: str, status_color: str):
        """Handle consolidated status changes."""
        self._update_device_summary(status_text=status_text, status_color=status_color)

    def _on_device_change(self, device_info: DeviceInfo):
        """Handle device information changes."""
        # Update device caption based on device info
        if device_info.is_connected:
            device_label = device_info.get_display_name()
            caption = f"Secure LoRa link • {device_info.status_text or 'Ready'}"
            self._update_device_summary(device_label=device_label, caption=caption)
        else:
            caption = "Pair a LoRa contact to begin chatting securely."
            if device_info.device_name:
                caption = f"Disconnected ({device_info.device_name})"
            elif device_info.device_id:
                caption = f"Disconnected ({device_info.device_id})"
            self._update_device_summary(device_label="No device paired", caption=caption)

    def _on_connection_change(self, is_connected: bool, device_id: str, device_name: str):
        """Handle connection state changes."""
        # This provides immediate visual feedback for connection changes
        if is_connected:
            label = device_name or device_id or "Active device"
            self._update_device_summary(status_text="Connected", status_color=Colors.STATE_SUCCESS,
                                        device_label=label)
        else:
            caption = "Pair a LoRa contact to begin chatting securely."
            if device_name:
                caption = f"Disconnected ({device_name})"
            elif device_id:
                caption = f"Disconnected ({device_id})"
            self._update_device_summary(status_text="Disconnected", status_color=Colors.STATE_ERROR,
                                        device_label="No device paired",
                                        caption=caption)

    def _update_device_summary(self, status_text: str | None = None, status_color: str | None = None,
                               device_label: str | None = None, caption: str | None = None):
        """Centralized helper so every callback renders the same UI."""
        if status_text:
            self.connection_badge.configure(text=status_text)
        if status_color:
            self.connection_badge.configure(bg=status_color, fg=Colors.SURFACE)
        if device_label:
            self.device_title.configure(text=device_label)
        if caption:
            self.device_caption.configure(text=caption)

    def destroy(self):
        """CRITICAL FIX: Clean up registered callbacks to prevent memory leaks."""
        try:
            # Unregister all callbacks to prevent memory leaks
            for callback_type, manager, callback in self._registered_callbacks:
                if callback_type == "status" and hasattr(manager, 'unregister_status_callback'):
                    manager.unregister_status_callback(callback)
                elif callback_type == "device" and hasattr(manager, 'unregister_device_callback'):
                    manager.unregister_device_callback(callback)
                elif callback_type == "connection" and hasattr(manager, 'unregister_connection_callback'):
                    manager.unregister_connection_callback(callback)
        except Exception as e:
            print(f"Error cleaning up sidebar callbacks: {e}")
        finally:
            super().destroy()
