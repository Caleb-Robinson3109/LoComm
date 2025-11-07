"""Modernized Home page built on the refreshed design system."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, DesignUtils, Spacing, Typography
from utils.status_manager import get_status_manager, DeviceInfo
from utils.ui_helpers import create_scroll_container


class HomePage(tk.Frame):
    """Conversation hub that mirrors Signal-style first run experience."""

    def __init__(self, master, app, session, host):
        super().__init__(master, bg=Colors.SURFACE)
        self.app = app
        self.session = session
        self.host = host
        self.status_manager = get_status_manager()

        self._registered_callbacks = [
            ("device", self.status_manager, self._on_device_change),
            ("status", self.status_manager, self._on_status_change),
        ]
        self.status_manager.register_device_callback(self._on_device_change)
        self.status_manager.register_status_callback(self._on_status_change)

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
            actions=[{"text": "Resume chat", "command": host.show_chat_page},
                     {"text": "Pair a device", "command": host.show_pair_page, "variant": "secondary"}]
        )

        self._build_connection_card(body)
        self._build_conversation_section(body)

        self._update_connection_summary()
        self._render_conversation_cards()

    # ------------------------------------------------------------------ #
    def _build_connection_card(self, parent):
        card, content = DesignUtils.card(
            parent,
            "Session health",
            "Live connection details + trust posture at a glance.",
            actions=[{"text": "View settings", "command": self.host.show_settings_page, "variant": "ghost"}]
        )
        card.pack(fill=tk.X, pady=(0, Spacing.LG))

        header = tk.Frame(content, bg=Colors.SURFACE_ALT)
        header.pack(fill=tk.X, pady=(0, Spacing.SM))
        tk.Label(header, textvariable=self.connection_title_var, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_PRIMARY,
                 font=(Typography.FONT_UI, Typography.SIZE_20, Typography.WEIGHT_BOLD)).pack(anchor="w")
        tk.Label(header, textvariable=self.connection_subtitle_var, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="w", pady=(Spacing.XXS, 0))

        badge_row = tk.Frame(content, bg=Colors.SURFACE_ALT)
        badge_row.pack(fill=tk.X, pady=(Spacing.SM, Spacing.SM))
        self.connection_badge = tk.Label(
            badge_row,
            textvariable=self.connection_badge_var,
            bg=Colors.STATE_ERROR,
            fg=Colors.SURFACE,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
            padx=Spacing.MD,
            pady=int(Spacing.XS / 2)
        )
        self.connection_badge.pack(side=tk.LEFT)
        tk.Label(badge_row, textvariable=self.connection_detail_var, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(side=tk.LEFT, padx=(Spacing.MD, 0))

        action_row = tk.Frame(content, bg=Colors.SURFACE_ALT)
        action_row.pack(fill=tk.X, pady=(Spacing.SM, 0))
        DesignUtils.button(
            action_row,
            text="Open chat",
            command=self.host.show_chat_page
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        DesignUtils.button(
            action_row,
            text="Pair another device",
            command=self.host.show_pair_page,
            variant="secondary"
        ).pack(side=tk.LEFT)

    def _build_conversation_section(self, parent):
        section, body = DesignUtils.section(parent, "Recent conversations", "Jump back into chats or start a new one.")
        self.conversation_body = body

    def _render_conversation_cards(self):
        for child in self.conversation_body.winfo_children():
            child.destroy()

        for convo in self._conversation_model():
            card = tk.Frame(self.conversation_body, bg=Colors.SURFACE_ALT, highlightbackground=Colors.DIVIDER,
                            highlightthickness=1, bd=0)
            card.pack(fill=tk.X, pady=(0, Spacing.SM))
            top = tk.Frame(card, bg=Colors.SURFACE_ALT)
            top.pack(fill=tk.X, padx=Spacing.MD, pady=(Spacing.MD, Spacing.XXS))
            tk.Label(top, text=convo["title"], bg=Colors.SURFACE_ALT, fg=Colors.TEXT_PRIMARY,
                     font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD)).pack(anchor="w")
            tk.Label(top, text=convo["subtitle"], bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                     font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="w")

            pill = tk.Label(card, text=convo["status"], bg=convo["status_color"], fg=Colors.SURFACE,
                            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
                            padx=Spacing.SM, pady=int(Spacing.XS / 2))
            pill.pack(anchor="w", padx=Spacing.MD, pady=(0, Spacing.XS))

            bottom = tk.Frame(card, bg=Colors.SURFACE_ALT)
            bottom.pack(fill=tk.X, padx=Spacing.MD, pady=(0, Spacing.MD))
            tk.Label(bottom, text=convo["body"], bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                     font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
                     wraplength=540, justify="left").pack(side=tk.LEFT, fill=tk.X, expand=True)
            if convo.get("action"):
                DesignUtils.button(bottom, **convo["action"]).pack(side=tk.RIGHT)

    def _conversation_model(self) -> list[dict]:
        device_info = self.status_manager.get_current_device()
        conversations: list[dict] = []

        if device_info.is_connected and device_info.device_name:
            conversations.append({
                "title": device_info.device_name,
                "subtitle": "Live LoRa session",
                "status": "Connected",
                "status_color": Colors.STATE_SUCCESS,
                "body": "Messages are real-time and end-to-end authenticated. Resume exactly where you left off.",
                "action": {"text": "Open", "command": self.host.show_chat_page, "variant": "secondary"}
            })
        elif self.session.device_name:
            conversations.append({
                "title": self.session.device_name,
                "subtitle": "Previously paired",
                "status": "Ready to reconnect",
                "status_color": Colors.STATE_INFO,
                "body": "Device remembered from the last secure PIN exchange. Connect again when hardware is nearby.",
                "action": {"text": "Reconnect", "command": self.host.show_chat_page, "variant": "secondary"}
            })

        conversations.append({
            "title": "Demo Device",
            "subtitle": "Mock transport (safe to explore)",
            "status": "Sandbox",
            "status_color": Colors.STATE_WARNING,
            "body": "Use the built-in demo mode to test UI flows even without LoRa radios connected.",
            "action": {"text": "Launch demo", "command": self.host.show_pair_page, "variant": "ghost"}
        })

        conversations.append({
            "title": "Pair a new device",
            "subtitle": "Signal-style PIN verification",
            "status": "Step 1",
            "status_color": Colors.STATE_INFO,
            "body": "Scan for nearby hardware, exchange the 8-digit code, and trust the session before messages unlock.",
            "action": {"text": "Start pairing", "command": self.host.show_pair_page}
        })

        return conversations

    def _update_connection_summary(self):
        device_info = self.status_manager.get_current_device()
        if device_info.is_connected:
            self.connection_title_var.set(f"Connected to {device_info.device_name or 'LoRa peer'}")
            self.connection_subtitle_var.set("Secure LoRa link established • messages will send immediately.")
            self.connection_badge_var.set("Connected")
            self.connection_badge.configure(bg=Colors.STATE_SUCCESS)
            self.connection_detail_var.set("Encryption verified via 8-digit PIN")
        elif self.session.device_name:
            self.connection_title_var.set(f"{self.session.device_name} is ready to reconnect")
            self.connection_subtitle_var.set("We remember your last trust relationship. Connect when hardware is nearby.")
            self.connection_badge_var.set("Awaiting reconnection")
            self.connection_badge.configure(bg=Colors.STATE_INFO)
            self.connection_detail_var.set("Tap Pair Device to re-establish link")
        else:
            self.connection_title_var.set("No device paired yet")
            self.connection_subtitle_var.set("Pair your first device to unlock end-to-end encrypted LoRa chat.")
            self.connection_badge_var.set("Disconnected")
            self.connection_badge.configure(bg=Colors.STATE_ERROR)
            self.connection_detail_var.set("Pair via the 8-digit PIN workflow")

    # ------------------------------------------------------------------ #
    def refresh_content(self):
        """Refresh the home tab content when returning to it."""
        self._update_connection_summary()
        self._render_conversation_cards()

    def _on_device_change(self, _info: DeviceInfo):
        self._update_connection_summary()
        self._render_conversation_cards()

    def _on_status_change(self, _status: str, _color: str):
        self._update_connection_summary()

    def destroy(self):
        """Ensure callbacks are cleaned up."""
        try:
            for callback_type, manager, callback in self._registered_callbacks:
                if callback_type == "device":
                    manager.unregister_device_callback(callback)
                elif callback_type == "status":
                    manager.unregister_status_callback(callback)
        except Exception:
            pass
        finally:
            super().destroy()
