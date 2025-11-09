"""Sidebar navigation component for the redesigned UI shell."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from utils.design_system import Colors, Typography, Spacing, DesignUtils, ThemeManager
from utils.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store


class Sidebar(tk.Frame):
    """Left sidebar navigation component with connection summary."""

    def __init__(self, master, nav_items: list[tuple[str, str]],
                 on_nav_select: Optional[Callable[[str], None]] = None,
                 on_theme_toggle: Optional[Callable[[bool], None]] = None):
        super().__init__(master, width=Spacing.SIDEBAR_WIDTH, relief="flat", bd=0, bg=Colors.SURFACE_SIDEBAR)
        self.on_nav_select = on_nav_select
        self.on_theme_toggle = on_theme_toggle
        self.current_view = nav_items[0][0] if nav_items else "home"
        self.nav_items = nav_items

        self.ui_store = get_ui_store()
        self._device_subscription = None
        self._dark_mode = tk.BooleanVar(value=ThemeManager.current_mode() == "dark")

        self._buttons: dict[str, ttk.Button] = {}
        self._build_ui()
        self._apply_snapshot(self.ui_store.get_device_status())
        self._subscribe_to_store()

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
            btn = DesignUtils.create_nav_button(container, label, lambda k=key: self._handle_nav_click(k))
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
            text="Devices",
            command=lambda: self._handle_nav_click("pair"),
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

    def _handle_nav_click(self, route_id: str):
        self.set_active_view(route_id)
        if self.on_nav_select:
            self.on_nav_select(route_id)

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
        self._handle_nav_click("chat")

    def show_pair(self):
        self._handle_nav_click("pair")

    def show_home(self):
        self._handle_nav_click("home")

    def show_settings(self):
        self._handle_nav_click("settings")

    def set_status(self, status_text: str):
        """Compatibility helper for external callers."""
        self.connection_badge.configure(text=status_text)

    # ------------------------------------------------------------------ #
    def _subscribe_to_store(self):
        if self._device_subscription is not None:
            return

        def _callback(snapshot: DeviceStatusSnapshot):
            self._handle_device_snapshot(snapshot)

        self._device_subscription = _callback
        self.ui_store.subscribe_device_status(_callback)

    def _handle_device_snapshot(self, snapshot: DeviceStatusSnapshot):
        self._apply_snapshot(snapshot)

    def _apply_snapshot(self, snapshot: DeviceStatusSnapshot | None):
        if snapshot is None:
            return
        badge_text, badge_color = self._badge_style_for_stage(snapshot.stage)
        self.connection_badge.configure(text=badge_text, bg=badge_color, fg=Colors.SURFACE)
        device_label = snapshot.device_name or ("No device paired" if snapshot.stage != DeviceStage.CONNECTED else "Active device")
        self.device_title.configure(text=device_label)
        caption = snapshot.detail or snapshot.subtitle
        self.device_caption.configure(text=caption)

    @staticmethod
    def _badge_style_for_stage(stage: DeviceStage) -> tuple[str, str]:
        mapping = {
            DeviceStage.READY: ("Ready", Colors.STATE_INFO),
            DeviceStage.SCANNING: ("Scanning", Colors.STATE_INFO),
            DeviceStage.AWAITING_PIN: ("Awaiting PIN", Colors.STATE_WARNING),
            DeviceStage.CONNECTING: ("Connecting", Colors.STATE_INFO),
            DeviceStage.CONNECTED: ("Connected", Colors.STATE_SUCCESS),
            DeviceStage.DISCONNECTED: ("Disconnected", Colors.STATE_ERROR),
        }
        return mapping.get(stage, mapping[DeviceStage.READY])

    def destroy(self):
        if self._device_subscription is not None:
            self.ui_store.unsubscribe_device_status(self._device_subscription)
            self._device_subscription = None
        super().destroy()
