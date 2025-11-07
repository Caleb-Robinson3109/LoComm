"""About page with refreshed design."""
from __future__ import annotations

import sys
import tkinter as tk

from utils.design_system import Colors, DesignUtils, Typography, Spacing
from utils.ui_helpers import create_scroll_container


class AboutPage(tk.Frame):
    """About and support information."""

    def __init__(self, master, app, controller, session=None):
        super().__init__(master, bg=Colors.SURFACE)
        self.app = app
        self.controller = controller
        self.session = session

        self.pack(fill=tk.BOTH, expand=True)
        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(Spacing.LG, Spacing.LG))
        body = scroll.frame

        DesignUtils.hero_header(
            body,
            title="About Locomm",
            subtitle="Build 3.0 • Python {}".format(sys.version.split()[0])
        )

        self._build_version_card(body)
        self._build_specs(body)
        self._build_support(body)

    def _build_version_card(self, parent):
        card, content = DesignUtils.card(parent, "Version", "Internal preview build")
        card.pack(fill=tk.X, pady=(0, Spacing.SM))
        info = [
            ("Desktop build", "v2.1 redesign"),
            ("Transport backend", "Mock LoComm API"),
            ("UI theme", "Locomm Aurora"),
        ]
        for label, value in info:
            DesignUtils.create_message_row(content, label, value)

    def _build_specs(self, parent):
        section, body = DesignUtils.section(parent, "Technical specifications", "Stack overview")
        specs = {
            "Transport": "LoCommTransport abstraction + mock backend",
            "UI": "Tkinter + Locomm Design System v3",
            "Authentication": "5-digit PIN pairing",
            "Session storage": "Local session.json cache",
        }
        for key, value in specs.items():
            row = tk.Frame(body, bg=Colors.SURFACE_ALT)
            row.pack(fill=tk.X, pady=(0, Spacing.SM))
            tk.Label(row, text=key, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                     font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w")
            tk.Label(row, text=value, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_PRIMARY,
                     font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR), wraplength=600, justify="left").pack(anchor="w")

    def _build_support(self, parent):
        section, body = DesignUtils.section(parent, "Support", "How to reach the team")
        DesignUtils.button(body, text="View documentation", variant="secondary").pack(anchor="w", pady=(0, Spacing.SM))
        DesignUtils.button(body, text="Open diagnostics", variant="ghost").pack(anchor="w")
