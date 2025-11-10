"""Help page mirroring the about layout."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, Typography, Spacing, Space
from ui.helpers import create_scroll_container
from .base_page import BasePage, PageContext


class HelpPage(BasePage):
    """Help page mirroring the About typography, spacing, and background."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)

        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(0, Spacing.LG))
        body = scroll.frame

        self._build_title(body)
        self._build_help_section(body)
        self._build_topics_section(body)

    def _build_title(self, parent):
        title_wrap = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
        )
        title_wrap.pack(fill=tk.X, pady=(0, Space.XS))

        tk.Label(
            title_wrap,
            text="Help & Navigation",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")

        tk.Label(
            title_wrap,
            text="Everything you need to know about Locomm Desktop in one place.",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

    def _build_help_section(self, parent):
        section = tk.Frame(parent, bg=Colors.SURFACE, padx=Space.LG, pady=Space.MD)
        section.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            section,
            text="Navigating Locomm",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        ).pack(anchor="w", pady=(0, Spacing.SM))

        content = tk.Frame(section, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.MD)
        content.pack(fill=tk.X, pady=(0, Spacing.SM))

        paragraphs = [
            "Use the sidebar to switch between Home, Chat, Devices, Settings, About, and Help.",
            "The top bar shows your local device name and connection badge. It updates whenever the transport state changes.",
        ]
        for paragraph in paragraphs:
            tk.Label(
                content,
                text=paragraph,
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
                wraplength=720,
                justify="left",
            ).pack(anchor="w", pady=(0, Spacing.XXS))

    def _build_topics_section(self, parent):
        section = tk.Frame(parent, bg=Colors.SURFACE, padx=Space.LG, pady=Space.MD)
        section.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            section,
            text="Topics Covered",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        ).pack(anchor="w", pady=(0, Spacing.SM))

        content = tk.Frame(section, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.MD)
        content.pack(fill=tk.X)

        topics = [
            "Chat basics: how to read messaging colors, send text, and interpret status badges.",
            "Devices & pairing: scanning, connecting, disconnecting, and demo sessions.",
            "Settings & diagnostics: toggling notifications, toggling dark mode, and viewing build info.",
            "About & support: build information, release notes, and documentation links.",
        ]
        for topic in topics:
            tk.Label(
                content,
                text=f"• {topic}",
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
                wraplength=720,
                justify="left",
            ).pack(anchor="w", pady=(0, Spacing.XXS))
