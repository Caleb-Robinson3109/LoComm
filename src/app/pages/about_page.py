"""About page using standardized header and auto wrapping text."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, Spacing, Typography
from ui.helpers import (
    create_scroll_container,
    create_page_header,
    create_standard_section,
    AutoWrapLabel,
)
from .base_page import BasePage, PageContext


class AboutPage(BasePage):
    """About page with standardized layout and responsive text."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.navigator = context.navigator if context else None

        scroll = create_scroll_container(
            self,
            bg=Colors.SURFACE,
            padding=(0, Spacing.LG),
        )
        body = scroll.frame

        create_page_header(
            body,
            title="About",
            subtitle="Learn more about this app.",
            padx=Spacing.LG,
        )
        self._build_intro(body)
        self._build_highlights(body)
        self._build_privacy(body)

    def _handle_back(self):
        nav = getattr(self, "navigator", None)
        if not nav:
            return
        if hasattr(nav, "go_back"):
            nav.go_back()
        elif hasattr(nav, "navigate_to"):
            nav.navigate_to("home")

    def destroy(self):
        return super().destroy()

    def _build_intro(self, parent: tk.Misc):
        _, content = create_standard_section(
            parent,
            title="What is Locomm?",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=True,
        )
        AutoWrapLabel(
            content,
            text="Locomm is a desktop companion for chatting over LoRa hardware. It pairs your device, joins a chatroom, and lets you exchange messages peer-to-peer without servers.",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12),
        ).pack(fill=tk.X, pady=(Spacing.XXS, 0))

    def _build_highlights(self, parent: tk.Misc):
        _, content = create_standard_section(
            parent,
            title="Highlights",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=True,
        )
        bullets = [
            "Hardware-first: pairs directly with your Locomm device.",
            "Chatrooms: gated pairing so only members can connect.",
            "Transport profiles: auto-selects the right backend for your setup.",
            "Lightweight: no accounts, no cloud dependency.",
        ]
        for bullet in bullets:
            AutoWrapLabel(
                content,
                text=f"• {bullet}",
                bg=Colors.SURFACE,
                fg=Colors.TEXT_PRIMARY,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ).pack(fill=tk.X, anchor="w", pady=(0, Spacing.XXS))

    def _build_privacy(self, parent: tk.Misc):
        _, content = create_standard_section(
            parent,
            title="Privacy & Data",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=True,
        )
        AutoWrapLabel(
            content,
            text="No tracking. No collected data. Diagnostics live locally at ~/.locomm/diagnostics.log to help troubleshoot transport issues. You can delete them anytime.",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12),
        ).pack(fill=tk.X, pady=(Spacing.XXS, 0))
