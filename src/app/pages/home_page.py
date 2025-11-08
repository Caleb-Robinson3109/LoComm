"""Modernized Home page built on the refreshed design system."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, DesignUtils, Spacing, Typography
from utils.status_manager import get_status_manager
from utils.ui_helpers import create_scroll_container


class HomePage(tk.Frame):
    """Conversation hub that mirrors Signal-style first run experience."""

    def __init__(self, master, app, session, host):
        super().__init__(master, bg=Colors.SURFACE)
        self.app = app
        self.session = session
        self.host = host
        self.status_manager = get_status_manager()

        self.connection_title_var = tk.StringVar(value="No device paired")
        self.connection_subtitle_var = tk.StringVar(value="Start by pairing a LoRa contact to open a secure chat.")
        self.connection_badge_var = tk.StringVar(value="Disconnected")
        self.connection_detail_var = tk.StringVar(value="Awaiting secure PIN handoff")

        self.pack(fill=tk.BOTH, expand=True)
        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(Spacing.LG, Spacing.LG))
        body = scroll.frame

        DesignUtils.hero_header(
            body,
            title="Secure conversations, Signal-level polish",
            subtitle="Pair LoRa hardware, verify trust, and jump back into chats from a single dashboard.",
            actions=[]
        )
        self._build_status_card(body)
        self._update_status_card()
        self._registered_callbacks = []
        self.status_manager.register_status_callback(self._on_status_change)
        self.status_manager.register_device_callback(self._on_device_change)
        self._registered_callbacks.extend([
            ("status", self._on_status_change),
            ("device", self._on_device_change),
        ])

    def _build_status_card(self, parent):
        card, content = DesignUtils.card(
            parent,
            "Current status",
            "Live view of your device connection state"
        )
        card.pack(fill=tk.X, pady=(Spacing.LG, 0))
        card.pack_propagate(False)
        content.configure(height=180)

        self.status_badge = tk.Label(
            content,
            textvariable=self.connection_badge_var,
            bg=Colors.STATE_ERROR,
            fg=Colors.SURFACE,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
            padx=Spacing.LG,
            pady=Spacing.SM
        )
        self.status_badge.pack(anchor="w", pady=(0, Spacing.SM))

        self.status_title = tk.Label(
            content,
            textvariable=self.connection_title_var,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD)
        )
        self.status_title.pack(anchor="w")

        self.status_subtitle = tk.Label(
            content,
            textvariable=self.connection_subtitle_var,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=520,
            justify="left"
        )
        self.status_subtitle.pack(anchor="w", pady=(Spacing.XXS, 0))

        self.status_detail = tk.Label(
            content,
            textvariable=self.connection_detail_var,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)
        )
        self.status_detail.pack(anchor="w", pady=(Spacing.SM, 0))

    def _update_status_card(self):
        device_info = self.status_manager.get_current_device()
        status = (self.status_manager.get_current_status() or "").lower()
        badge_color = Colors.STATE_INFO
        title = "Ready to pair"
        subtitle = "No device paired. Start by scanning for hardware and exchanging the PIN."
        detail = "Select Devices to begin."

        if "scan" in status:
            badge_color = Colors.STATE_INFO
            title = "Scanning…"
            subtitle = "Scanning nearby devices for LoRa hardware."
            detail = "This takes a few seconds."
        elif "awaiting pin" in status or "awaiting" in status:
            badge_color = Colors.STATE_WARNING
            label = device_info.device_name or detail
            title = f"Awaiting PIN for {label}"
            subtitle = "Enter the 8-digit code to trust this device."
            detail = "Complete the PIN flow in the Devices tab."
        elif "connecting" in status:
            badge_color = Colors.STATE_INFO
            label = device_info.device_name or "device"
            title = f"Connecting to {label}…"
            subtitle = "Establishing encrypted transport."
            detail = "You can start chatting once connected."
        elif "connected" in status:
            badge_color = Colors.STATE_SUCCESS
            label = device_info.device_name or "LoRa peer"
            title = f"Connected to {label}"
            subtitle = "Secure LoRa link established."
            detail = "Messages will send immediately."
        elif "disconnected" in status:
            badge_color = Colors.STATE_ERROR
            label = device_info.device_name or device_info.device_id or "device"
            title = "Disconnected"
            subtitle = f"Disconnected ({label})."
            detail = "Reconnect by selecting the device again."

        self.connection_badge_var.set(status.title() if status else "Status")
        self.connection_title_var.set(title)
        self.connection_subtitle_var.set(subtitle)
        self.connection_detail_var.set(detail)
        self.status_badge.configure(bg=badge_color)

    def _on_status_change(self, status_text: str, color: str):
        self.connection_badge_var.set(status_text)
        self.status_badge.configure(bg=color)
        self._update_status_card()

    def _on_device_change(self, device_info):
        self._update_status_card()

    def destroy(self):
        for kind, callback in getattr(self, "_registered_callbacks", []):
            if kind == "status":
                try:
                    self.status_manager.unregister_status_callback(callback)
                except Exception:
                    pass
            elif kind == "device":
                try:
                    self.status_manager.unregister_device_callback(callback)
                except Exception:
                    pass
        return super().destroy()
