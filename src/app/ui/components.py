"""Reusable UI components that rely on the theme tokens."""
from __future__ import annotations

import time
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Any

from ui.theme_tokens import Colors, Spacing, Typography
from ui.theme_manager import ThemeManager
from utils.app_logger import get_logger

logger = get_logger("design_utils")


class DesignUtils:
    """Factory helpers that return styled widgets."""

    @staticmethod
    def button(parent, text: str, command=None, variant: str = "primary", width: int | None = None):
        """Create a styled button with modern flat design."""
        ThemeManager.ensure()
        style_name = ThemeManager.BUTTON_STYLES.get(variant, "Locomm.Primary.TButton")
        
        # Configure styles dynamically if needed (though usually done in ThemeManager)
        # Here we rely on the theme manager having set up the styles correctly.
        
        kwargs = {"text": text, "style": style_name, "cursor": "pointinghand"}
        if command is not None:
            kwargs["command"] = command
        if width is not None:
            kwargs["width"] = width
        return ttk.Button(parent, **kwargs)

    @staticmethod
    def pill(parent, text: str, variant: str = "info"):
        """Create a styled pill/badge label with rounded look."""
        ThemeManager.ensure()
        variant_map = {
            "info": (Colors.BUTTON_SECONDARY_BG, Colors.TEXT_PRIMARY),
            "success": (Colors.STATE_SUCCESS, Colors.SURFACE),
            "warning": (Colors.STATE_WARNING, Colors.SURFACE),
            "danger": (Colors.STATE_ERROR, Colors.SURFACE),
        }
        bg, fg = variant_map.get(variant, variant_map["info"])
        label = tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_BOLD),
            padx=Spacing.SM,
            pady=2,
        )
        label.configure(relief="flat")
        return label

    @staticmethod
    def hero_header(parent, title: str, subtitle: str, actions: List[dict[str, Any]] | None = None):
        """Create a hero header with title, subtitle, and optional actions."""
        ThemeManager.ensure()
        container = tk.Frame(parent, bg=Colors.BG_MAIN, padx=Spacing.MD, pady=Spacing.SM)
        container.pack(fill=tk.X, padx=0, pady=(0, Spacing.SM))
        
        text_wrap = tk.Frame(container, bg=Colors.BG_MAIN)
        text_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            text_wrap,
            text=title,
            bg=Colors.BG_MAIN,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")
        
        tk.Label(
            text_wrap,
            text=subtitle,
            bg=Colors.BG_MAIN,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR),
        ).pack(anchor="w", pady=(Spacing.XS, 0))
        
        if actions:
            action_frame = tk.Frame(container, bg=Colors.BG_MAIN)
            action_frame.pack(side=tk.RIGHT, anchor="e")
            for action in actions:
                btn = DesignUtils.button(action_frame, **action)
                btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        return container

    @staticmethod
    def create_nav_button(parent, text: str, command: Callable | None = None):
        """Create a navigation button with subtle hover."""
        ThemeManager.ensure()
        kwargs = {"text": text, "style": "Locomm.Nav.TButton", "cursor": "pointinghand"}
        if command is not None:
            kwargs["command"] = command
        return ttk.Button(parent, **kwargs)

    @staticmethod
    def create_chat_entry(parent, **kwargs):
        """Create a styled entry for chat input."""
        ThemeManager.ensure()
        style = ttk.Style()
        entry_style = "Locomm.Input.TEntry"
        return ttk.Entry(parent, style=entry_style, **kwargs)

    @staticmethod
    def create_compact_entry(parent, **kwargs):
        """Create an entry with reduced internal padding for tighter spacing."""
        ThemeManager.ensure()
        style = ttk.Style()
        compact_style = "Locomm.Compact.TEntry"
        return ttk.Entry(parent, style=compact_style, **kwargs)

    @staticmethod
    def create_pin_entry(parent, **kwargs):
        """Create a styled entry for PIN input."""
        ThemeManager.ensure()
        style = ttk.Style()
        entry_style = "Locomm.PinEntry.TEntry"
        return ttk.Entry(parent, style=entry_style, **kwargs)

    @staticmethod
    def create_message_row(parent, title: str, value: str):
        """Create a read-only row displaying a label and value."""
        row = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        row.pack(fill=tk.X, pady=(0, Spacing.SM))
        tk.Label(
            row,
            text=title.upper(),
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")
        tk.Label(
            row,
            text=value,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")
        return row

    @staticmethod
    def create_message_bubble(parent: tk.Frame, *, sender: str, message: str, timestamp: float, is_self: bool, wraplength: int):
        """Create a chat message bubble."""
        container = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        container.pack(fill=tk.X, expand=True, pady=0, padx=(Spacing.MD, Spacing.MD))

        content = tk.Frame(container, bg=Colors.SURFACE_ALT)
        content.pack(fill=tk.X, expand=True, anchor="e" if is_self else "w")

        anchor = "e" if is_self else "w"
        bubble_bg = Colors.CHAT_BUBBLE_SELF_BG if is_self else Colors.CHAT_BUBBLE_OTHER_BG
        text_fg = Colors.CHAT_BUBBLE_SELF_TEXT if is_self else Colors.CHAT_BUBBLE_OTHER_TEXT
        name_fg = Colors.TEXT_MUTED
        bubble_padx = (0, Spacing.MD) if is_self else (Spacing.MD, 0)

        name_label = tk.Label(
            content,
            text=sender or "Peer",
            fg=name_fg,
            bg=Colors.SURFACE_ALT,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
        )
        name_label.pack(anchor=anchor, padx=bubble_padx)

        bubble = tk.Frame(
            content,
            bg=bubble_bg,
            padx=12,
            pady=8,
        )
        bubble.pack(anchor=anchor, padx=bubble_padx)
        tk.Label(
            bubble,
            text=message,
            bg=bubble_bg,
            fg=text_fg,
            wraplength=wraplength,
            justify="right" if is_self else "left",
            font=(Typography.FONT_UI, Typography.SIZE_14),
        ).pack()

        timestamp_label = tk.Label(
            content,
            text=time.strftime("%H:%M", time.localtime(timestamp)),
            fg=Colors.TEXT_MUTED,
            bg=Colors.SURFACE_ALT,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
        )
        timestamp_label.pack(anchor=anchor, padx=bubble_padx, pady=(2, 0))

    @staticmethod
    def card(parent, title: str, subtitle: str = "", actions: List[dict[str, Any]] | None = None):
        """Create a card container with header and body."""
        ThemeManager.ensure()
        frame = tk.Frame(parent, bg=Colors.CARD_PANEL_BG, highlightbackground=Colors.CARD_PANEL_BORDER, highlightthickness=1, bd=0)
        frame.pack_propagate(False)
        header = tk.Frame(frame, bg=Colors.CARD_PANEL_BG)
        header.pack(fill=tk.X, pady=(Spacing.SM, 0), padx=Spacing.MD)
        tk.Label(
            header,
            text=title,
            bg=Colors.CARD_PANEL_BG,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                header,
                text=subtitle,
                bg=Colors.CARD_PANEL_BG,
                fg=Colors.TEXT_MUTED,
                font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            ).pack(anchor="w", pady=(Spacing.XXS, 0))
        if actions:
            actions_frame = tk.Frame(frame, bg=Colors.CARD_PANEL_BG)
            actions_frame.pack(fill=tk.X, padx=Spacing.MD, pady=(Spacing.XS, Spacing.SM))
            for action in actions:
                btn = DesignUtils.button(actions_frame, **action)
                btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        body = tk.Frame(frame, bg=Colors.CARD_PANEL_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=(0, Spacing.MD))
        return frame, body

    @staticmethod
    def section(parent, title: str, description: str = "", icon: str | None = None):
        """Create a section with title and optional description."""
        ThemeManager.ensure()
        container = tk.Frame(parent, bg=Colors.SURFACE_ALT, highlightbackground=Colors.DIVIDER, highlightthickness=1, bd=0)
        container.pack(fill=tk.X, pady=(0, Spacing.MD))
        header = tk.Frame(container, bg=Colors.SURFACE_ALT)
        header.pack(fill=tk.X, padx=Spacing.MD, pady=(Spacing.SM, 0))
        tk.Label(
            header,
            text=title,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")
        if description:
            tk.Label(
                container,
                text=description,
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
                wraplength=640,
                justify="left",
            ).pack(fill=tk.X, padx=Spacing.MD, pady=(Spacing.XXS, Spacing.SM))
        return container
