"""Modernized Home page built on the refreshed design system."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, DesignUtils, Spacing, Typography
from utils.ui_helpers import create_scroll_container


class HomePage(tk.Frame):
    """Landing surface with hero, stats, and feature callouts."""

    def __init__(self, master, app, session, host):
        super().__init__(master, bg=Colors.SURFACE)
        self.app = app
        self.session = session
        self.host = host

        self.pack(fill=tk.BOTH, expand=True)
        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(Spacing.LG, Spacing.LG))
        body = scroll.frame

        DesignUtils.hero_header(
            body,
            title="Design-forward Locomm Desktop",
            subtitle="Pair LoRa devices, monitor live status, and chat securely across the fleet.",
            actions=[{"text": "Start Pairing", "command": host.show_pair_page},
                     {"text": "Open Chat", "command": host.show_chat_page, "variant": "secondary"}]
        )

        self._build_stat_row(body)
        self._build_quick_actions(body)
        self._build_feature_section(body)
        self._build_getting_started(body)

    # ------------------------------------------------------------------ #
    def _build_stat_row(self, parent):
        stat_row = tk.Frame(parent, bg=Colors.SURFACE)
        stat_row.pack(fill=tk.X, pady=(0, Spacing.LG))
        stats = [
            ("Paired Devices", self.session.device_name or "0", "Most recent pairing" if self.session.device_name else "No device active"),
            ("Chat Sessions", "Unlimited", "Encrypted LoRa communication"),
            ("Network Mode", "Mock Backend", "Swap once hardware arrives"),
        ]
        for label, value, helper in stats:
            card, content = DesignUtils.card(stat_row, label, helper)
            card.configure(width=240, height=120)
            DesignUtils.stat_block(content, label, value, helper)
            card.pack(side=tk.LEFT, padx=(0, Spacing.MD))

    def _build_quick_actions(self, parent):
        section, body = DesignUtils.section(parent, "Quick actions", "Launch common workflows in one click")
        actions = [
            ("🔗 Pair devices", "Connect using a 5-digit PIN", self.host.show_pair_page),
            ("💬 Open conversations", "Jump straight into the chat interface", self.host.show_chat_page),
            ("🧪 Demo mode", "Explore the UI using mock data", self.app._handle_demo_login),
        ]
        for text, desc, handler in actions:
            row = tk.Frame(body, bg=Colors.SURFACE_ALT)
            row.pack(fill=tk.X, pady=(0, Spacing.SM))
            tk.Label(row, text=text, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_PRIMARY,
                     font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM)).pack(anchor="w")
            tk.Label(row, text=desc, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                     font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="w")
            DesignUtils.button(row, text="Launch", command=handler, variant="secondary").pack(anchor="e", pady=(Spacing.XXS, 0))

    def _build_feature_section(self, parent):
        section, body = DesignUtils.section(parent, "Platform highlights", "Why teams adopt Locomm")
        features = [
            ("Unified pairing", "Device discovery plus PIN entry in a single flow."),
            ("Live transport monitor", "Status pills reflect the controller and backend state in real time."),
            ("Modular UI", "Shared components keep future features visually consistent."),
            ("Accessibility", "Keyboard-friendly navigation, focus outlines, and color contrast."),
        ]
        for icon, copy in features:
            DesignUtils.create_message_row(body, icon, copy)

    def _build_getting_started(self, parent):
        section, body = DesignUtils.section(parent, "Getting started", "Configure hardware, run diagnostics, or invite teammates")
        cards = [
            {
                "title": "1. Connect hardware",
                "subtitle": "Install latest firmware, plug LoComm bridge, confirm drivers.",
                "actions": [{"text": "View guide", "variant": "secondary", "command": self.host.show_about_page}]
            },
            {
                "title": "2. Pair devices",
                "subtitle": "Use the Pair tab to scan, select, and enter the short-lived PIN.",
                "actions": [{"text": "Open Pairing", "command": self.host.show_pair_page}]
            },
            {
                "title": "3. Chat + monitor",
                "subtitle": "Switch to Chat to validate transport messages and mock demos.",
                "actions": [{"text": "Go to Chat", "command": self.host.show_chat_page}]
            },
        ]
        for cfg in cards:
            card, content = DesignUtils.card(body, cfg["title"], cfg["subtitle"], cfg.get("actions"))
            card.pack(fill=tk.X, pady=(0, Spacing.SM))

    def refresh_content(self):
        """Refresh the home tab content when returning to it."""
        # Could be extended to show recent device stats; currently static.
        pass
