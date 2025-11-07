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


    def refresh_content(self):
        """Refresh the home tab content when returning to it."""
        # Could be extended to show recent device stats; currently static.
        pass
