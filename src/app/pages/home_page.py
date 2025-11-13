"""Home page matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, DesignUtils, Spacing, Typography, Space
from ui.helpers import create_scroll_container
from .base_page import BasePage, PageContext


class HomePage(BasePage):
    """Home page with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.session = context.session if context else None
        self.host = context.navigator if context else None

        # Simple scroll container like chat page
        scroll = create_scroll_container(
            self,
            bg=Colors.SURFACE,
            padding=(0, Spacing.LG)
        )
        body = scroll.frame

        self._build_title(body)

    def _build_title(self, parent):
        """Build simple title section like chat page."""
        title_wrap = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
        )
        title_wrap.pack(fill=tk.X, pady=(0, Space.XS))

        text_wrap = tk.Frame(title_wrap, bg=Colors.SURFACE)
        text_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)

        action_wrap = tk.Frame(title_wrap, bg=Colors.SURFACE)
        action_wrap.pack(side=tk.RIGHT)

        tk.Label(
            text_wrap,
            text="Welcome to Locomm",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")

        tk.Label(
            text_wrap,
            text="Secure LoRa messaging for desktop",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))

        DesignUtils.button(
            action_wrap,
            text="Peers",
            command=self._go_to_chatroom,
            variant="primary",
        ).pack()

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

    def _go_to_chatroom(self):
        """Navigate to the chatroom modal."""
        if self.app and hasattr(self.app, 'show_chatroom_modal'):
            self.app.show_chatroom_modal()

    def destroy(self):
        return super().destroy()
