"""About page with refreshed design."""
from __future__ import annotations

import sys
import tkinter as tk

from utils.design_system import Colors, DesignUtils, Typography, Spacing
from utils.ui_helpers import create_page_scaffold
from .base_page import BasePage, PageContext


class AboutPage(BasePage):
    """About and support information."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.controller = context.controller if context else None
        self.session = context.session if context else None

        self.scaffold = create_page_scaffold(
            self,
            title="About Locomm",
            subtitle=f"Build 3.0 • Python {sys.version.split()[0]}",
            padding=(0, Spacing.LG),
        )
        body = self.scaffold.body

        card, content = DesignUtils.card(body, "Locomm Desktop overview")
        card.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))

        info = [
            ("Desktop build", "v2.1 redesign"),
            ("Transport backend", "Mock LoComm API"),
            ("UI theme", "Locomm Aurora"),
        ]
        for label, value in info:
            DesignUtils.create_message_row(content, label, value)

        tk.Label(
            content,
            text="Technical specifications",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
        ).pack(anchor="w", pady=(Spacing.MD, Spacing.XXS))

        specs = [
            "Transport: LoCommTransport abstraction + mock backend",
            "UI: Tkinter + Locomm Design System v3",
            "Authentication: 8-digit PIN pairing",
            "Session storage: Local session.json cache",
        ]
        for bullet in specs:
            tk.Label(
                content,
                text=f"• {bullet}",
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
                wraplength=720,
                justify="left",
            ).pack(anchor="w", pady=(0, Spacing.XXS))

    def destroy(self):
        if hasattr(self, "scaffold"):
            self.scaffold.destroy()
        return super().destroy()
