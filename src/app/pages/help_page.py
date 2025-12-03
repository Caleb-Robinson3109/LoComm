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
            subtitle="Quick guidance for logging in, registering a password, and staying connected with your LoRa device.",
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
                "1) Open the app and click Register to set/confirm the device password (3–32 chars).\n"
                "2) Validate the password; the Preferred Name field unlocks.\n"
                "3) Enter your display name and Login. The app sends the name to the device and loads the main shell.\n"
                "4) Use Peers/Pair to manage pairing codes; the chat UI is currently disabled but transport remains active."
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
                "Password not accepted: confirm length 3–32 and retry Validate. If still blocked, open Register to reset the password on-device "
                "and validate again."
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
                "Device not detected or pairing stalls: reconnect hardware, then restart the app to re-init transport. Keep the Register modal closed "
                "if the UI appears locked—modals hold focus until dismissed."
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
