"""Guided help page covering the entire desktop experience."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.ui_helpers import create_scroll_container
from .base_page import BasePage, PageContext


class HelpPage(BasePage):
    """Step-by-step navigation and feature guide."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(0, Spacing.LG))
        body = scroll.frame

        DesignUtils.hero_header(
            body,
            title="Help & Navigation",
            subtitle="Everything you need to know about Locomm Desktop in one place."
        )
        self._build_master_help_card(body)

    def _build_master_help_card(self, parent):
        card, content = DesignUtils.card(parent, "Complete guide", "")
        card.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
        content.configure(padx=Spacing.LG, pady=Spacing.MD)

        sections = [
            ("Getting started", [
                "Use the left sidebar to switch between Home, Chat, Devices, Settings, About, and Help.",
                "The top bar shows your local device name and current connection status. It updates as soon as a device connects or disconnects."
            ]),
            ("Chat basics", [
                "Messages appear in colored bubbles: your messages on the right, peer messages on the left.",
                "Disconnect ends the current session and clears the chat automatically."
            ]),
            ("Devices & pairing", [
                "Open the Devices page to scan for LoRa hardware and click Connect on a selected device.",
                "Use Disconnect to stop the session; the app routes you back to Devices from Home automatically."
            ]),
            ("Settings, About, Help", [
                "Settings hosts placeholder toggles for notifications and diagnostics.",
                "About lists build information and support links. Help (this page) summarizes navigation details."
            ])
        ]

        for title, bullets in sections:
            tk.Label(
                content,
                text=title,
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_PRIMARY,
                font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_BOLD),
            ).pack(anchor="w", pady=(Spacing.SM, Spacing.XXS))
            for bullet in bullets:
                tk.Label(
                    content,
                    text=f"• {bullet}",
                    bg=Colors.SURFACE_ALT,
                    fg=Colors.TEXT_SECONDARY,
                    font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
                    wraplength=720,
                    justify="left",
                ).pack(anchor="w")
