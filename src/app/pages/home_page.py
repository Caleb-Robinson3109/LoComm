"""Home page matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, DesignUtils, Spacing, Typography, Space
from utils.chatroom_registry import get_active_code, format_chatroom_code
from ui.helpers import create_scroll_container, create_page_header, create_standard_section, AutoWrapLabel
from .base_page import BasePage, PageContext


class HomePage(BasePage):
    """Home page with chat style clean, simple design."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.session = context.session if context else None
        self.navigator = context.navigator if context else None

        scroll = create_scroll_container(
            self,
            bg=Colors.SURFACE,
            padding=(0, Spacing.LG),
        )
        body = scroll.frame

        # Standard header with AutoWrap subtitle and standard back button
        actions = [
            {
                "text": "Chatroom",
                "command": self._go_to_chatroom,
                "variant": "primary",
                "width": 10,
                "padx": (Spacing.XXS, 0),
            }
        ]
        create_page_header(
            body,
            title="Home",
            subtitle="Join a chatroom and start chatting",
            actions=actions,
            padx=Spacing.LG,
        )
        # Bind Enter key to navigate to chatroom
        self.bind_all("<Return>", lambda e: self._go_to_chatroom())
        self._build_getting_started(body)
        self._build_status(body)

    def _build_status(self, parent: tk.Misc):
        _, content = create_standard_section(
            parent,
            title="Session Status",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE_ALT,
            with_card=True,
        )
        content.grid_columnconfigure(1, weight=1)

        def _row(label_text: str, value_text: str):
            row = tk.Frame(content, bg=Colors.SURFACE_ALT)
            row.pack(fill=tk.X, pady=(Spacing.XXS, 0))
            tk.Label(
                row,
                text=label_text,
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ).pack(side=tk.LEFT)
            tk.Label(
                row,
                text=value_text,
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_PRIMARY,
                font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
            ).pack(side=tk.LEFT, padx=(Spacing.XS, 0))

        session = getattr(self, "session", None)
        name = getattr(session, "local_device_name", "") or getattr(session, "device_name", "") or "Not set"
        device_id = getattr(session, "local_device_id", "") or getattr(session, "device_id", "") or "Not set"
        chatroom = format_chatroom_code(get_active_code())

        _row("Device name:", name)
        _row("Device ID:", device_id)
        _row("Chatroom:", chatroom)

    def _build_getting_started(self, parent: tk.Misc):
        _, content = create_standard_section(
            parent,
            title="Getting Started",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=True,
        )
        steps = [
            "Create or enter a chatroom code to unlock pairing.",
            "Scan or manually add a peer from Peers to start a chat.",
            "Send your first message and keep an eye on the status badge.",
        ]
        for step in steps:
            AutoWrapLabel(
                content,
                text=f"• {step}",
                bg=Colors.SURFACE,
                fg=Colors.TEXT_PRIMARY,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ).pack(fill=tk.X, anchor="w", pady=(0, Spacing.XXS))

    def _navigate(self, route_id: str):
        if self.navigator and hasattr(self.navigator, "navigate_to"):
            self.navigator.navigate_to(route_id)

    def _handle_back(self):
        nav = getattr(self, "navigator", None)
        if not nav:
            return
        if hasattr(nav, "go_back"):
            nav.go_back()
        elif hasattr(nav, "navigate_to"):
            nav.navigate_to("home")

    def _go_to_chatroom(self):
        """Navigate to the chatroom page."""
        if self.navigator and hasattr(self.navigator, "navigate_to"):
            self.navigator.navigate_to("chatroom")

    def destroy(self):
        return super().destroy()
