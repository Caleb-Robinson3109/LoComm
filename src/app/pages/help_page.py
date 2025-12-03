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

        # Header with auto wrapping subtitle
        create_page_header(
            body,
            title="Help and Support",
            subtitle="Quick tips and guidance for using Locomm on your desktop.",
        )

        # Getting started section
        _, getting_started = create_standard_section(
            body,
            title="Getting Started",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=True,
        )

        AutoWrapLabel(
            getting_started,
            text=(
                "1. Log in with your device name. This is how you will appear to peers.\n"
                "2. Use the Peers section to connect to other devices.\n"
                "3. Once connected, you can start secure LoRa chats."
            ),
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            justify="left",
            padding_x=Spacing.SM * 2,
            min_wrap=260,
        ).pack(fill=tk.X, expand=True)

        # Troubleshooting section
        _, troubleshooting = create_standard_section(
            body,
            title="Troubleshooting",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=True,
        )

        AutoWrapLabel(
            troubleshooting,
            text=(
                "If you cannot see peers after refreshing, verify radios are powered "
                "and configured correctly. Check that you are on the same LoRa "
                "frequency and channel as your peers."
            ),
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            justify="left",
            padding_x=Spacing.SM * 2,
            min_wrap=260,
        ).pack(fill=tk.X, expand=True)

        AutoWrapLabel(
            troubleshooting,
            text=(
                "If issues persist, restart the application and re pair your device. "
                "Future releases will include more detailed diagnostics."
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
