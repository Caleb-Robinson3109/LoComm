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
            subtitle="Locomm Desktop v2.3.0 is a control surface for your LoRa device—login, register, pair, and monitor in one place.",
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
                "Locomm pairs a desktop shell with the underlying device API to simplify secure, low-bandwidth LoRa communication. "
                "The app handles authentication (register + validate), device naming, and session control while keeping the UI lean and responsive."
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
                "Highlights in 2.3.0: refreshed auth flow with in-place registration, simplified pairing modal, theme toggle with live re-render, "
                "and improved status handling across the transport controller."
            ),
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            justify="left",
            padding_x=Spacing.SM * 2,
            min_wrap=260,
        ).pack(fill=tk.X, expand=True, pady=(Spacing.SM, 0))

        AutoWrapLabel(
            content,
            text=(
                "The desktop client intentionally omits in-app chat for now; it focuses on connecting, naming, and monitoring your device. "
                "Chat transport is still wired through the controller for future UI re-enablement."
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
