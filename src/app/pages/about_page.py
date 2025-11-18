"""About page matching chat page's clean, simple design."""
from __future__ import annotations

import sys
import tkinter as tk

from ui.components import DesignUtils
from ui.theme_tokens import Colors, Spacing, Typography, Space
from ui.helpers import create_scroll_container
from .base_page import BasePage, PageContext


class AboutPage(BasePage):
    """About and support information with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.controller = context.controller if context else None
        self.session = context.session if context else None

        # Simple scroll container like chat page
        scroll = create_scroll_container(
            self, 
            bg=Colors.SURFACE, 
            padding=(0, Spacing.LG)
        )
        body = scroll.frame

        self._build_title(body)
        self._build_info_section(body)
        self._build_specs_section(body)

    def _build_title(self, parent):
        """Build simple title section like chat page."""
        title_wrap = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
        )
        title_wrap.pack(fill=tk.X, pady=(0, Space.XS))

        tk.Label(
            title_wrap,
            text="About Locomm",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")

        tk.Label(
            title_wrap,
            text=f"Build 3.0 • Python {sys.version.split()[0]}",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

    def _build_info_section(self, parent):
        """Build clean info section like chat content area."""
        section = tk.Frame(parent, bg=Colors.SURFACE, padx=Space.LG, pady=Space.MD)
        section.pack(fill=tk.BOTH, expand=True)
        
        # Section title
        tk.Label(
            section,
            text="About Locomm Desktop",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        ).pack(anchor="w", pady=(0, Spacing.SM))
        
        # Info content
        content = tk.Frame(section, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.MD)
        content.pack(fill=tk.X, pady=(0, Space.SM))
        
        # Build info
        tk.Label(
            content,
            text="Desktop build",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")
        tk.Label(
            content,
            text="v3.0 - Unified Design",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w", pady=(0, Spacing.SM))
        
        # Transport info
        tk.Label(
            content,
            text="Transport backend",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")
        tk.Label(
            content,
            text="LoComm Transport + Mock API",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w", pady=(0, Spacing.SM))
        
        # Theme info
        tk.Label(
            content,
            text="UI Theme",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")
        tk.Label(
            content,
            text="Locomm Design System v3",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")

    def _build_specs_section(self, parent):
        """Build clean technical specs section."""
        section = tk.Frame(parent, bg=Colors.SURFACE, padx=Space.LG, pady=Space.MD)
        section.pack(fill=tk.BOTH, expand=True)
        
        # Section title
        tk.Label(
            section,
            text="Technical Specifications",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        ).pack(anchor="w", pady=(0, Spacing.SM))
        
        # Specs content
        content = tk.Frame(section, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.MD)
        content.pack(fill=tk.X)
        
        specs = [
            "Transport: LoCommTransport abstraction",
            "UI: Tkinter + Locomm Design System v3",
            "Authentication: 8-digit PIN pairing",
            "Session storage: Local session.json cache",
        ]
        
        for spec in specs:
            tk.Label(
                content,
                text=f"• {spec}",
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
                wraplength=720,
                justify="left",
            ).pack(anchor="w", pady=(0, Space.XXS))

    def destroy(self):
        return super().destroy()
