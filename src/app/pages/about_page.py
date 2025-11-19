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

        # Header
        create_page_header(
            body,
            title="About Locomm",
            subtitle="Locomm is a desktop client for secure LoRa powered messaging.",
        )

        # Main about section
        _, content = create_standard_section(
            body,
            title="What is Locomm?",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=True,
        )

        AutoWrapLabel(
            content,
            text=(
                "Locomm is designed for low bandwidth, long range communication using "
                "LoRa radios. The desktop client focuses on a clean, modern interface "
                "while keeping configuration and status easy to understand."
            ),
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            justify="left",
            padding_x=Spacing.SM * 2,
            min_wrap=260,
        ).pack(fill=tk.X, expand=True)

        AutoWrapLabel(
            content,
            text=(
                "This application is still evolving. Future releases will add richer "
                "peer management, diagnostics, and multi device support."
            ),
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            justify="left",
            padding_x=Spacing.SM * 2,
            min_wrap=260,
        ).pack(fill=tk.X, expand=True, pady=(Spacing.SM, 0))

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
