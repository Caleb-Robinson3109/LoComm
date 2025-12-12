"""Help page using standardized header and auto wrapping text."""
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


class HelpPage(BasePage):
    """Help page with standardized layout and responsive text."""

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
            title="Help",
            subtitle="Find quick guidance and support.",
            padx=Spacing.LG,
        )
        self._build_quick_fixes(body)
        self._build_faq(body)
        self._build_support(body)

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

    def _build_quick_fixes(self, parent: tk.Misc):
        _, content = create_standard_section(
            parent,
            title="Quick fixes",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=True,
        )
        tips = [
            "Cannot connect: ensure you’re in a chatroom, then retry pairing.",
            "Peers disabled: join or create a chatroom first, then rescan.",
            "No messages: check status badge; if not connected, disconnect and reconnect.",
            "Audio/notifications: toggle in Settings > Appearance.",
        ]
        for tip in tips:
            AutoWrapLabel(
                content,
                text=f"• {tip}",
                bg=Colors.SURFACE,
                fg=Colors.TEXT_PRIMARY,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ).pack(fill=tk.X, anchor="w", pady=(0, Spacing.XXS))

    def _build_faq(self, parent: tk.Misc):
        _, content = create_standard_section(
            parent,
            title="FAQ",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=True,
        )
        qa = [
            ("Why is Peers disabled?", "Peers unlock after you enter a chatroom code so only members can pair."),
            ("Where are logs stored?", "Diagnostics live at ~/.locomm/diagnostics.log; delete them anytime."),
            ("How do I change my name?", "Go to Settings and update your device name; the header refreshes automatically."),
        ]
        for question, answer in qa:
            AutoWrapLabel(
                content,
                text=question,
                bg=Colors.SURFACE,
                fg=Colors.TEXT_PRIMARY,
                font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
            ).pack(fill=tk.X, anchor="w", pady=(Spacing.XXS, 0))
            AutoWrapLabel(
                content,
                text=answer,
                bg=Colors.SURFACE,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ).pack(fill=tk.X, anchor="w", pady=(0, Spacing.SM))

    def _build_support(self, parent: tk.Misc):
        _, content = create_standard_section(
            parent,
            title="Need more help?",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE_ALT,
            with_card=True,
        )
        AutoWrapLabel(
            content,
            text="Export diagnostics (Settings or ~/.locomm/diagnostics.log) and share with support. Make sure your device is powered and within range when pairing.",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12),
        ).pack(fill=tk.X, pady=(Spacing.XXS, 0))
