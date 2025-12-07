"""Home page matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, DesignUtils, Spacing, Typography, Space
from ui.helpers import create_scroll_container, create_page_header
from .base_page import BasePage, PageContext


class HomePage(BasePage):
    """Home page with chat style clean, simple design."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.session = context.session if context else None
        self.navigator = context.navigator if context else None

        body = tk.Frame(self, bg=Colors.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Standard header with AutoWrap subtitle and standard back button
        actions = [
            {
                "text": "Chatroom",
                "command": self._go_to_chatroom,
                "variant": "primary",
            }
        ]
        create_page_header(
            body,
            title="Welcome",
            subtitle="Join a chatroom and start chatting",
            actions=actions,
        )
        # No extra content below yet, but body will grow and text will reflow

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
