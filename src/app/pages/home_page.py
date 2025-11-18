"""Home page matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk

from ui.components import DesignUtils
from ui.theme_tokens import Colors, Spacing, Typography, Space
from ui.helpers import create_scroll_container
from ui.theme_manager import ThemeManager
from .base_page import BasePage, PageContext


class HomePage(BasePage):
    """Home page with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.session = context.session if context else None
        self.host = context.navigator if context else None
        self._scroll_container = None
        self._body = None
        self._title_wrap = None
        self._text_wrap = None
        self._action_wrap = None
        self._title_label = None
        self._subtitle_label = None
        self._separator = None
        self._theme_listener = None

        # Simple scroll container like chat page
        self._scroll_container = create_scroll_container(
            self,
            bg=Colors.SURFACE,
            padding=(0, Spacing.LG)
        )
        self._body = self._scroll_container.frame

        self._build_title(self._body)
        self._theme_listener = self._apply_theme
        ThemeManager.register_theme_listener(self._theme_listener)
        self._apply_theme()

    def _build_title(self, parent):
        """Build simple title section like chat page."""
        self._title_wrap = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
        )
        self._title_wrap.pack(fill=tk.X, pady=(0, Space.XS))

        self._text_wrap = tk.Frame(self._title_wrap, bg=Colors.SURFACE)
        self._text_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._action_wrap = tk.Frame(self._title_wrap, bg=Colors.SURFACE)
        self._action_wrap.pack(side=tk.RIGHT)

        self._title_label = tk.Label(
            self._text_wrap,
            text="Welcome to Locomm",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        )
        self._title_label.pack(anchor="w")

        self._subtitle_label = tk.Label(
            self._text_wrap,
            text="Secure LoRa messaging for desktop",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        )
        self._subtitle_label.pack(anchor="w", pady=(Space.XXS, 0))

        DesignUtils.button(
            self._action_wrap,
            text="Chatroom",
            command=self._go_to_chatroom,
            variant="primary",
        ).pack()

        self._separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        self._separator.pack(fill=tk.X, pady=(0, Space.SM))

    def _go_to_chatroom(self):
        """Navigate to the chatroom modal."""
        if self.app and hasattr(self.app, 'show_chatroom_modal'):
            self.app.show_chatroom_modal()

    def on_show(self):
        """Refresh colors when showing the page."""
        self._apply_theme()

    def _apply_theme(self):
        surface = Colors.SURFACE
        self.configure(bg=surface)
        if self._scroll_container:
            if self._scroll_container.wrapper.winfo_exists():
                self._scroll_container.wrapper.configure(bg=surface)
            if self._scroll_container.canvas.winfo_exists():
                self._scroll_container.canvas.configure(bg=surface)
            if self._scroll_container.frame.winfo_exists():
                self._scroll_container.frame.configure(bg=surface)
            if self._scroll_container.scrollbar.winfo_exists():
                self._scroll_container.scrollbar.configure(bg=surface, troughcolor=surface, activebackground=surface)
        frames = [self._body, self._title_wrap, self._text_wrap, self._action_wrap]
        for frame in frames:
            if frame and frame.winfo_exists():
                frame.configure(bg=surface)
        if self._title_label and self._title_label.winfo_exists():
            self._title_label.configure(bg=surface, fg=Colors.TEXT_PRIMARY)
        if self._subtitle_label and self._subtitle_label.winfo_exists():
            self._subtitle_label.configure(bg=surface, fg=Colors.TEXT_SECONDARY)
        if self._separator and self._separator.winfo_exists():
            self._separator.configure(bg=Colors.DIVIDER)

    def destroy(self):
        if self._theme_listener:
            ThemeManager.unregister_theme_listener(self._theme_listener)
            self._theme_listener = None
        return super().destroy()
