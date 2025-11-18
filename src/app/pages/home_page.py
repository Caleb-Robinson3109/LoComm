"""Home page matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, DesignUtils, Spacing, Typography, Space
from ui.helpers import create_scroll_container
from .base_page import BasePage, PageContext


class HomePage(BasePage):
    """Home page with chat style clean, simple design."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.session = context.session if context else None
        self.navigator = context.navigator if context else None

        # Simple scroll container like chat page
        scroll = create_scroll_container(
            self,
            bg=Colors.SURFACE,
            padding=(0, Spacing.LG),
        )
        body = scroll.frame

        self._subtitle_label: tk.Label | None = None

        self._build_title(body)

    def _handle_back(self):
        nav = getattr(self, "navigator", None)
        if not nav:
            return
        if hasattr(nav, "go_back"):
            nav.go_back()
        elif hasattr(nav, "navigate_to"):
            nav.navigate_to("home")

    def _build_title(self, parent):
        """Build simple title section like chat page, with optional back button."""
        # Top back button row
        back_row = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
            pady=Space.XXS,
        )
        back_row.pack(fill=tk.X, pady=(0, Space.XXS))

        back_button = tk.Button(
            back_row,
            text="← Back",
            command=self._handle_back,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=Space.SM,
            pady=int(Space.XS / 2),
            activebackground=Colors.SURFACE,
            activeforeground=Colors.TEXT_PRIMARY,
            cursor="hand2",
        )
        back_button.pack(anchor="w")

        # Main title and action row
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

        # Subtitle label with dynamic wraplength
        subtitle = tk.Label(
            text_wrap,
            text="Secure LoRa messaging for desktop",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,  # initial value; will be updated on resize
            justify="left",
        )
        subtitle.pack(anchor="w", pady=(Space.XXS, 0))
        self._subtitle_label = subtitle

        # Adjust wraplength when the available width changes
        def _on_resize(event):
            if not self._subtitle_label:
                return
            # Leave a bit of horizontal padding so text does not hug the edge
            new_wrap = max(300, event.width - 2 * Spacing.SM)
            self._subtitle_label.configure(wraplength=new_wrap)

        text_wrap.bind("<Configure>", _on_resize)

        DesignUtils.button(
            action_wrap,
            text="Chatroom",
            command=self._go_to_chatroom,
            variant="primary",
        ).pack()

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

    def _go_to_chatroom(self):
        """Navigate to the chatroom modal."""
        if self.app and hasattr(self.app, "show_chatroom_modal"):
            self.app.show_chatroom_modal()

    def destroy(self):
        return super().destroy()
