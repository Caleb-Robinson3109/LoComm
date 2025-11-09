"""
Locomm Design System v3
Provides a layered token/component-based styling toolkit for the desktop app.
(Buttons tuned for a slightly old-school desktop look.)
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
import os
import time
from typing import Callable


# ---------------------------------------------------------------------------
# DESIGN TOKENS
# ---------------------------------------------------------------------------
class Palette:
    """Signal-inspired palette."""

    WHITE = "#FFFFFF"
    CLOUD_050 = "#F7F9FC"
    CLOUD_100 = "#EDF1F7"
    CLOUD_200 = "#E0E6F0"
    CLOUD_300 = "#CBD3E1"
    CLOUD_500 = "#94A3B8"

    SLATE_700 = "#3F4A5A"
    SLATE_800 = "#2B323C"
    SLATE_900 = "#1C1F26"

    SIGNAL_BLUE = "#0B7CFF"
    SIGNAL_BLUE_DARK = "#075AC6"
    SIGNAL_BLUE_LIGHT = "#3AA0FF"
    SIGNAL_TEAL = "#00C7B1"
    SIGNAL_RED = "#FF5A5F"


class Colors:
    """Runtime theme values (populated at runtime)."""

    SURFACE = ""
    SURFACE_ALT = ""
    SURFACE_RAISED = ""
    SURFACE_HEADER = ""
    SURFACE_SIDEBAR = ""
    SURFACE_SELECTED = ""
    BORDER = ""
    DIVIDER = ""
    TEXT_PRIMARY = ""
    TEXT_SECONDARY = ""
    TEXT_MUTED = ""
    TEXT_ACCENT = ""
    STATE_SUCCESS = ""
    STATE_WARNING = ""
    STATE_ERROR = ""
    STATE_INFO = ""
    BUTTON_PRIMARY_BG = ""
    BUTTON_PRIMARY_HOVER = ""
    BUTTON_SECONDARY_BG = ""
    BUTTON_GHOST_BG = ""
    BG_PRIMARY = ""
    BG_SECONDARY = ""
    BG_TERTIARY = ""
    BG_CHAT_AREA = ""
    BG_MESSAGE_OWN = ""
    BG_MESSAGE_OTHER = ""
    BG_MESSAGE_SYSTEM = ""
    BG_INPUT_AREA = ""
    TEXT_PLACEHOLDER = ""
    TEXT_TIMESTAMP = ""
    MESSAGE_SYSTEM_TEXT = ""
    MESSAGE_BUBBLE_OWN_BG = ""
    MESSAGE_BUBBLE_OTHER_BG = ""
    MESSAGE_BUBBLE_SYSTEM_BG = ""

    # Status-specific colors
    STATUS_CONNECTED = ""
    STATUS_DISCONNECTED = ""
    STATUS_CONNECTING = ""
    STATUS_PAIRING = ""


_THEME_DEFINITIONS = {
    "dark": {
        "SURFACE": Palette.SLATE_900,
        "SURFACE_ALT": "#252B36",
        "SURFACE_RAISED": "#2F3542",
        "SURFACE_HEADER": "#1A1F29",
        "SURFACE_SIDEBAR": "#181D26",
        "SURFACE_SELECTED": "#3A4252",
        "BORDER": "#2C3442",
        "DIVIDER": "#2A3240",
        "TEXT_PRIMARY": Palette.CLOUD_050,
        "TEXT_SECONDARY": Palette.CLOUD_300,
        "TEXT_MUTED": Palette.CLOUD_500,
        "TEXT_ACCENT": Palette.SIGNAL_BLUE,
        "STATE_SUCCESS": Palette.SIGNAL_TEAL,
        "STATE_WARNING": "#F2A93B",
        "STATE_ERROR": Palette.SIGNAL_RED,
        "STATE_INFO": Palette.SIGNAL_BLUE,
        "BUTTON_PRIMARY_BG": Palette.SIGNAL_BLUE,
        "BUTTON_PRIMARY_HOVER": Palette.SIGNAL_BLUE_DARK,
        "BUTTON_SECONDARY_BG": "#3F4758",
        "BUTTON_GHOST_BG": "#262C34",
        "BG_PRIMARY": Palette.SLATE_900,
        "BG_SECONDARY": Palette.SLATE_800,
        "BG_TERTIARY": Palette.SLATE_700,
        "BG_CHAT_AREA": Palette.SLATE_900,
        "BG_MESSAGE_OWN": Palette.SIGNAL_BLUE,
        "BG_MESSAGE_OTHER": "#2E3544",
        "BG_MESSAGE_SYSTEM": "#262C37",
        "BG_INPUT_AREA": Palette.SLATE_800,
        "TEXT_PLACEHOLDER": Palette.CLOUD_500,
        "TEXT_TIMESTAMP": Palette.CLOUD_500,
        "MESSAGE_SYSTEM_TEXT": Palette.CLOUD_500,
        "MESSAGE_BUBBLE_OWN_BG": Palette.SIGNAL_BLUE,
        "MESSAGE_BUBBLE_OTHER_BG": Palette.SLATE_800,
        "MESSAGE_BUBBLE_SYSTEM_BG": Palette.SLATE_800,
    },
    "light": {
        "SURFACE": Palette.WHITE,
        "SURFACE_ALT": Palette.CLOUD_050,
        "SURFACE_RAISED": Palette.CLOUD_100,
        "SURFACE_HEADER": Palette.WHITE,
        "SURFACE_SIDEBAR": Palette.CLOUD_050,
        "SURFACE_SELECTED": Palette.CLOUD_200,
        "BORDER": Palette.CLOUD_200,
        "DIVIDER": Palette.CLOUD_200,
        "TEXT_PRIMARY": Palette.SLATE_900,
        "TEXT_SECONDARY": Palette.SLATE_700,
        "TEXT_MUTED": Palette.CLOUD_500,
        "TEXT_ACCENT": Palette.SIGNAL_BLUE,
        "STATE_SUCCESS": Palette.SIGNAL_TEAL,
        "STATE_WARNING": "#F2A93B",
        "STATE_ERROR": Palette.SIGNAL_RED,
        "STATE_INFO": Palette.SIGNAL_BLUE,
        "BUTTON_PRIMARY_BG": Palette.SIGNAL_BLUE,
        "BUTTON_PRIMARY_HOVER": Palette.SIGNAL_BLUE_DARK,
        "BUTTON_SECONDARY_BG": Palette.CLOUD_200,
        "BUTTON_GHOST_BG": Palette.CLOUD_100,
        "BG_PRIMARY": Palette.WHITE,
        "BG_SECONDARY": Palette.CLOUD_050,
        "BG_TERTIARY": Palette.CLOUD_100,
        "BG_CHAT_AREA": Palette.CLOUD_050,
        "BG_MESSAGE_OWN": Palette.SIGNAL_BLUE,
        "BG_MESSAGE_OTHER": Palette.CLOUD_100,
        "BG_MESSAGE_SYSTEM": Palette.CLOUD_050,
        "BG_INPUT_AREA": Palette.CLOUD_100,
        "TEXT_PLACEHOLDER": Palette.CLOUD_500,
        "TEXT_TIMESTAMP": Palette.CLOUD_500,
        "MESSAGE_SYSTEM_TEXT": Palette.CLOUD_500,
        "MESSAGE_BUBBLE_OWN_BG": Palette.SIGNAL_BLUE,
        "MESSAGE_BUBBLE_OTHER_BG": Palette.CLOUD_100,
        "MESSAGE_BUBBLE_SYSTEM_BG": Palette.CLOUD_050,
    },
}


def _apply_theme_definition(mode: str):
    theme = _THEME_DEFINITIONS[mode]
    for key, value in theme.items():
        setattr(Colors, key, value)
    Colors.STATUS_CONNECTED = Colors.STATE_SUCCESS
    Colors.STATUS_DISCONNECTED = Colors.STATE_ERROR
    Colors.STATUS_CONNECTING = Colors.STATE_INFO
    Colors.STATUS_PAIRING = Colors.STATE_INFO


_apply_theme_definition("dark")


class Typography:
    """Typography scale (8pt grid) with system fallbacks."""

    FONT_UI = "SF Pro Display"
    FONT_MONO = "JetBrains Mono"

    SIZE_10 = 10
    SIZE_12 = 12
    SIZE_14 = 14
    SIZE_16 = 16
    SIZE_18 = 18
    SIZE_20 = 20
    SIZE_24 = 24
    SIZE_32 = 32

    WEIGHT_REGULAR = "normal"
    WEIGHT_MEDIUM = "normal"
    WEIGHT_BOLD = "bold"

    @staticmethod
    def font_ui(size: int, weight: str = "normal"):
        return (Typography.FONT_UI, size, weight)

    @staticmethod
    def font_mono(size: int, weight: str = "normal"):
        return (Typography.FONT_MONO, size, weight)


class Space:
    """Spacing tokens based on an 8px unit."""

    BASE = 8
    XXXS = int(BASE * 0.5)
    XXS = BASE
    XS = BASE * 1
    SM = BASE * 1.5
    MD = BASE * 2
    LG = BASE * 3
    XL = BASE * 4
    XXL = BASE * 5
    XXXL = BASE * 6


class Spacing:
    """Legacy spacing aliases used across existing widgets."""

    TAB_PADDING = Space.LG
    PAGE_MARGIN = Space.MD
    PAGE_PADDING = Space.SM
    HEADER_PADDING = Space.XL
    BUTTON_PADDING = Space.SM
    SECTION_MARGIN = Space.LG
    MESSAGE_BUBBLE_PADDING = (Space.LG, Space.SM)
    MESSAGE_GROUP_GAP = Space.XXS
    MESSAGE_MARGIN = (Space.SM, Space.XXS)
    CHAT_AREA_PADDING = Space.MD
    SIDEBAR_WIDTH = int(260 * 0.85 * 0.9 * 0.92)
    HEADER_HEIGHT = 64
    XXS = Space.XXS
    XS = Space.XXS
    SM = Space.XS
    MD = Space.MD
    LG = Space.LG
    XL = Space.XL
    XXL = Space.XXL
    XXXL = Space.XXXL


class Radii:
    CARD = 14
    PANEL = 18
    CHIP = 999


class Shadows:
    LEVEL_1 = (0, 8, 24)
    LEVEL_2 = (0, 16, 32)


# ---------------------------------------------------------------------------
# THEME MANAGER
# ---------------------------------------------------------------------------
class ThemeManager:
    """Registers ttk styles for the application."""

    _initialized = False
    _current_mode = "dark"
    BUTTON_STYLES = {
        "primary": "Locomm.Primary.TButton",
        "secondary": "Locomm.Secondary.TButton",
        "ghost": "Locomm.Ghost.TButton",
        "danger": "Locomm.Danger.TButton",
        "success": "Locomm.Success.TButton",
        "nav": "Locomm.Nav.TButton",
    }

    @classmethod
    def ensure(cls):
        if cls._initialized:
            return

        style = ttk.Style()
        # Clam is fine and supports borders; keeps things consistent.
        if "clam" in style.theme_names():
            style.theme_use("clam")

        default_font = (
            Typography.FONT_UI,
            Typography.SIZE_14,
            Typography.WEIGHT_REGULAR,
        )
        style.configure(
            "TLabel",
            background=Colors.SURFACE,
            foreground=Colors.TEXT_PRIMARY,
            font=default_font,
        )
        style.configure("TFrame", background=Colors.SURFACE)

        # ------------------------------------------------------------------
        # BUTTONS: classic / old-school desktop look
        # ------------------------------------------------------------------
        # Square corners, visible borders, raised, with pressed "sunken" effect.
        button_configs = {
            "Locomm.Primary.TButton": dict(
                bg=Colors.BUTTON_PRIMARY_BG,
                hover_bg=Colors.BUTTON_PRIMARY_HOVER,
                fg=Colors.SURFACE,
                border=2,
            ),
            "Locomm.Secondary.TButton": dict(
                bg=Colors.BUTTON_SECONDARY_BG,
                hover_bg=Colors.SURFACE_SELECTED,
                fg=Colors.TEXT_PRIMARY,
                border=2,
            ),
            "Locomm.Ghost.TButton": dict(
                bg=Colors.BUTTON_GHOST_BG,
                hover_bg=Colors.SURFACE_SELECTED,
                fg=Colors.TEXT_PRIMARY,
                border=2,
            ),
            "Locomm.Danger.TButton": dict(
                bg=Colors.STATE_ERROR,
                hover_bg="#E1464B",
                fg=Colors.SURFACE,
                border=2,
            ),
            "Locomm.Success.TButton": dict(
                bg=Colors.STATE_SUCCESS,
                hover_bg="#00B398",
                fg=Colors.SURFACE,
                border=2,
            ),
        }
        for style_name, cfg in button_configs.items():
            cls._register_button(style, style_name, **cfg)

        # Navigation buttons (slightly flatter, left-aligned; keep simple)
        style.configure(
            "Locomm.Nav.TButton",
            background=Colors.SURFACE,
            foreground=Colors.TEXT_SECONDARY,
            relief="flat",
            anchor="w",
            padding=(Space.MD, Space.SM),
            font=(
                Typography.FONT_UI,
                Typography.SIZE_14,
                Typography.WEIGHT_MEDIUM,
            ),
        )
        style.map(
            "Locomm.Nav.TButton",
            background=[("active", Colors.SURFACE_SELECTED)],
            foreground=[("active", Colors.TEXT_PRIMARY)],
        )
        style.configure(
            "Locomm.NavActive.TButton",
            background=Colors.SURFACE_SELECTED,
            foreground=Colors.TEXT_PRIMARY,
            relief="flat",
            anchor="w",
            padding=(Space.MD, Space.SM),
            font=(
                Typography.FONT_UI,
                Typography.SIZE_14,
                Typography.WEIGHT_BOLD,
            ),
        )

        # Entry / input fields
        style.configure(
            "Locomm.Input.TEntry",
            fieldbackground=Colors.SURFACE_RAISED,
            foreground=Colors.TEXT_PRIMARY,
            insertcolor=Colors.TEXT_PRIMARY,
            padding=(Space.SM, int(Space.XS / 1.5)),
            bordercolor=Colors.BORDER,
            borderwidth=1,
            relief="solid",
        )
        style.map(
            "Locomm.Input.TEntry",
            fieldbackground=[("focus", Colors.SURFACE_SELECTED)],
            foreground=[("disabled", Colors.TEXT_MUTED)],
        )
        style.configure(
            "Locomm.PinEntry.TEntry",
            fieldbackground=Colors.SURFACE_ALT,
            foreground=Colors.TEXT_PRIMARY,
            insertcolor=Colors.TEXT_PRIMARY,
            padding=(2, 2),
            bordercolor=Colors.SURFACE_SELECTED,
            borderwidth=1,
            relief="solid",
        )
        style.map(
            "Locomm.PinEntry.TEntry",
            fieldbackground=[("focus", Colors.SURFACE_SELECTED)],
        )

        # Labels
        style.configure(
            "Locomm.H1.TLabel",
            font=(
                Typography.FONT_UI,
                Typography.SIZE_24,
                Typography.WEIGHT_BOLD,
            ),
        )
        style.configure(
            "Locomm.H2.TLabel",
            font=(
                Typography.FONT_UI,
                Typography.SIZE_20,
                Typography.WEIGHT_BOLD,
            ),
        )
        style.configure(
            "Locomm.H3.TLabel",
            font=(
                Typography.FONT_UI,
                Typography.SIZE_16,
                Typography.WEIGHT_MEDIUM,
            ),
        )
        style.configure(
            "Locomm.Caption.TLabel",
            font=(
                Typography.FONT_UI,
                Typography.SIZE_12,
                Typography.WEIGHT_MEDIUM,
            ),
            foreground=Colors.TEXT_MUTED,
        )
        # Legacy aliases
        style.configure(
            "Header.TLabel",
            font=(
                Typography.FONT_UI,
                Typography.SIZE_20,
                Typography.WEIGHT_BOLD,
            ),
            foreground=Colors.TEXT_PRIMARY,
            background=Colors.SURFACE,
        )
        style.configure(
            "SubHeader.TLabel",
            font=(
                Typography.FONT_UI,
                Typography.SIZE_16,
                Typography.WEIGHT_MEDIUM,
            ),
            foreground=Colors.TEXT_SECONDARY,
            background=Colors.SURFACE,
        )
        style.configure(
            "Body.TLabel",
            font=(
                Typography.FONT_UI,
                Typography.SIZE_14,
                Typography.WEIGHT_REGULAR,
            ),
            foreground=Colors.TEXT_PRIMARY,
            background=Colors.SURFACE,
        )
        style.configure(
            "Small.TLabel",
            font=(
                Typography.FONT_UI,
                Typography.SIZE_12,
                Typography.WEIGHT_REGULAR,
            ),
            foreground=Colors.TEXT_MUTED,
            background=Colors.SURFACE,
        )

        # Card / section frames
        style.configure(
            "Locomm.Card.TFrame",
            background=Colors.SURFACE_ALT,
            bordercolor=Colors.BORDER,
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "Locomm.Section.TFrame",
            background=Colors.SURFACE_ALT,
            bordercolor=Colors.BORDER,
            relief="solid",
            borderwidth=1,
        )

        # Badges
        style.configure(
            "Locomm.Badge.Info.TLabel",
            background=Colors.BUTTON_SECONDARY_BG,
            foreground=Colors.TEXT_PRIMARY,
            padding=(Space.SM, int(Space.XS)),
            font=(
                Typography.FONT_UI,
                Typography.SIZE_12,
                Typography.WEIGHT_MEDIUM,
            ),
        )

        # Backwards compatibility styles
        style.configure(
            "Primary.TButton",
            background=Colors.BUTTON_PRIMARY_BG,
            foreground=Colors.SURFACE,
        )
        style.configure(
            "Secondary.TButton",
            background=Colors.BUTTON_SECONDARY_BG,
            foreground=Colors.TEXT_PRIMARY,
        )

        cls._initialized = True

    @classmethod
    def current_mode(cls) -> str:
        return cls._current_mode

    @staticmethod
    def _register_button(
        style: ttk.Style,
        style_name: str,
        bg: str,
        hover_bg: str,
        fg: str,
        border: int = 2,
    ):
        """
        Old-school desktop style buttons:
        - visible solid border
        - raised by default
        - sunken when pressed
        - square corners (ttk doesn't support radius; we keep it simple)
        """
        style.configure(
            style_name,
            background=bg,
            foreground=fg,
            padding=(Space.MD, Space.XXS),
            borderwidth=border,
            relief="raised",
            focusthickness=1,
            focuscolor=Colors.BORDER,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_14,
                Typography.WEIGHT_MEDIUM,
            ),
        )
        style.map(
            style_name,
            background=[
                ("active", hover_bg),
                ("pressed", hover_bg),
                ("disabled", Colors.SURFACE_ALT),
            ],
            foreground=[("disabled", Colors.TEXT_MUTED)],
            relief=[("pressed", "sunken"), ("!pressed", "raised")],
        )

    @classmethod
    def toggle_mode(cls, dark: bool):
        mode = "dark" if dark else "light"
        if mode == cls._current_mode:
            return
        cls._current_mode = mode
        _apply_theme_definition(mode)
        cls._initialized = False
        cls.ensure()


def ensure_styles_initialized():
    ThemeManager.ensure()


# ---------------------------------------------------------------------------
# COMPONENT FACTORY
# ---------------------------------------------------------------------------
class DesignUtils:
    """Factory helpers that return styled widgets."""

    @staticmethod
    def button(
        parent,
        text: str,
        command=None,
        variant: str = "primary",
        width: int | None = None,
    ):
        ThemeManager.ensure()
        style_name = ThemeManager.BUTTON_STYLES.get(
            variant, "Locomm.Primary.TButton"
        )
        kwargs = {"text": text, "style": style_name}
        if command is not None:
            kwargs["command"] = command
        if width is not None:
            kwargs["width"] = width
        return ttk.Button(parent, **kwargs)

    @staticmethod
    def pill(parent, text: str, variant: str = "info"):
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
            font=(
                Typography.FONT_UI,
                Typography.SIZE_12,
                Typography.WEIGHT_MEDIUM,
            ),
            padx=Space.SM,
            pady=int(Space.XS / 2),
        )
        label.configure(relief="flat")
        return label

    @staticmethod
    def card(parent, title: str, subtitle: str = "", actions: list | None = None):
        ThemeManager.ensure()
        frame = tk.Frame(
            parent,
            bg=Colors.SURFACE_ALT,
            highlightbackground=Colors.BORDER,
            highlightthickness=1,
            bd=0,
        )
        frame.pack_propagate(False)

        header = tk.Frame(frame, bg=Colors.SURFACE_ALT)
        header.pack(fill=tk.X, pady=(Space.SM, 0), padx=Space.MD)

        tk.Label(
            header,
            text=title,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_16,
                Typography.WEIGHT_BOLD,
            ),
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                header,
                text=subtitle,
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_MUTED,
                font=(
                    Typography.FONT_UI,
                    Typography.SIZE_12,
                    Typography.WEIGHT_REGULAR,
                ),
            ).pack(anchor="w", pady=(Space.XXS, 0))

        if actions:
            actions_frame = tk.Frame(frame, bg=Colors.SURFACE_ALT)
            actions_frame.pack(
                fill=tk.X, padx=Space.MD, pady=(Space.XS, Space.SM)
            )
            for action in actions:
                btn = DesignUtils.button(actions_frame, **action)
                btn.pack(side=tk.LEFT, padx=(0, Space.SM))

        body = tk.Frame(frame, bg=Colors.SURFACE_ALT)
        body.pack(
            fill=tk.BOTH, expand=True, padx=Space.MD, pady=(0, Space.MD)
        )
        return frame, body

    @staticmethod
    def section(
        parent,
        title: str,
        description: str = "",
        icon: str | None = None,
    ):
        ThemeManager.ensure()
        container = tk.Frame(
            parent,
            bg=Colors.SURFACE_ALT,
            highlightbackground=Colors.DIVIDER,
            highlightthickness=1,
            bd=0,
        )
        container.pack(fill=tk.X, pady=(0, Space.LG))

        header = tk.Frame(container, bg=Colors.SURFACE_ALT)
        header.pack(fill=tk.X, padx=Space.LG, pady=(Space.MD, Space.SM))

        title_text = title if not icon else f"{icon} {title}"
        tk.Label(
            header,
            text=title_text,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_18,
                Typography.WEIGHT_BOLD,
            ),
        ).pack(anchor="w")
        if description:
            tk.Label(
                header,
                text=description,
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_SECONDARY,
                font=(
                    Typography.FONT_UI,
                    Typography.SIZE_12,
                    Typography.WEIGHT_REGULAR,
                ),
            ).pack(anchor="w", pady=(Space.XXS, 0))

        body = tk.Frame(container, bg=Colors.SURFACE_ALT)
        body.pack(fill=tk.X, padx=Space.LG, pady=(0, Space.LG))
        return container, body

    @staticmethod
    def stat_block(parent, label: str, value: str, helper: str = ""):
        block = tk.Frame(parent, bg=Colors.SURFACE_RAISED)
        block.pack(fill=tk.X, padx=0, pady=(0, Space.SM))
        tk.Label(
            block,
            text=label.upper(),
            bg=Colors.SURFACE_RAISED,
            fg=Colors.TEXT_MUTED,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_12,
                Typography.WEIGHT_MEDIUM,
            ),
        ).pack(anchor="w")
        tk.Label(
            block,
            text=value,
            bg=Colors.SURFACE_RAISED,
            fg=Colors.TEXT_PRIMARY,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_20,
                Typography.WEIGHT_BOLD,
            ),
        ).pack(anchor="w", pady=(Space.XXS, 0))
        if helper:
            tk.Label(
                block,
                text=helper,
                bg=Colors.SURFACE_RAISED,
                fg=Colors.TEXT_SECONDARY,
                font=(
                    Typography.FONT_UI,
                    Typography.SIZE_12,
                    Typography.WEIGHT_REGULAR,
                ),
            ).pack(anchor="w")
        return block

    @staticmethod
    def hero_header(
        parent,
        title: str,
        subtitle: str,
        actions: list | None = None,
    ):
        container = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
            pady=Spacing.XXS,
        )
        container.pack(
            fill=tk.X, padx=Spacing.SM, pady=(0, Spacing.XXS)
        )
        text_wrap = tk.Frame(container, bg=Colors.SURFACE)
        text_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            text_wrap,
            text=title,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_24,
                Typography.WEIGHT_BOLD,
            ),
        ).pack(anchor="w")
        tk.Label(
            text_wrap,
            text=subtitle,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_14,
                Typography.WEIGHT_REGULAR,
            ),
        ).pack(anchor="w", pady=(Space.XS, 0))

        if actions:
            action_frame = tk.Frame(container, bg=Colors.SURFACE)
            action_frame.pack(side=tk.RIGHT, anchor="e")
            for action in actions:
                btn = DesignUtils.button(action_frame, **action)
                btn.pack(side=tk.LEFT, padx=(0, Space.SM))

        return container

    @staticmethod
    def create_styled_button(
        parent,
        text: str,
        command=None,
        style: str = "Locomm.Primary.TButton",
    ):
        """Backwards-compatible helper."""
        ThemeManager.ensure()
        kwargs = {"text": text, "style": style}
        if command is not None:
            kwargs["command"] = command
        return ttk.Button(parent, **kwargs)

    @staticmethod
    def create_styled_label(
        parent,
        text: str,
        style: str = "Body.TLabel",
        **kwargs,
    ):
        ThemeManager.ensure()
        return ttk.Label(parent, text=text, style=style, **kwargs)

    @staticmethod
    def create_chat_entry(parent, **kwargs):
        ThemeManager.ensure()
        return ttk.Entry(parent, style="Locomm.Input.TEntry", **kwargs)

    @staticmethod
    def create_pin_entry(parent, **kwargs):
        ThemeManager.ensure()
        return ttk.Entry(parent, style="Locomm.PinEntry.TEntry", **kwargs)

    @staticmethod
    def create_nav_button(parent, text: str, command=None):
        ThemeManager.ensure()
        kwargs = {"text": text, "style": "Locomm.Nav.TButton"}
        if command is not None:
            kwargs["command"] = command
        return ttk.Button(parent, **kwargs)

    @staticmethod
    def sidebar_container(parent, padding: int = Spacing.MD):
        container = tk.Frame(parent, bg=Colors.SURFACE_SIDEBAR)
        container.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
        return container

    @staticmethod
    def sidebar_nav_section(
        parent,
        items: list[tuple[str, str]],
        click_handler: Callable[[str], None],
        register_button: Callable[[str, ttk.Button], None] | None = None,
    ):
        section = tk.Frame(parent, bg=Colors.SURFACE_SIDEBAR)
        for key, label in items:
            btn = DesignUtils.create_nav_button(section, label, lambda k=key: click_handler(k))
            btn.pack(fill=tk.X, pady=(0, Spacing.SM))
            if register_button:
                register_button(key, btn)
        return section

    @staticmethod
    def sidebar_footer(parent, version_label: str):
        footer = tk.Frame(parent, bg=Colors.SURFACE_SIDEBAR)
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(Spacing.XS, Spacing.XS))
        tk.Label(
            footer,
            text=version_label,
            bg=Colors.SURFACE_SIDEBAR,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w", padx=Spacing.MD, pady=(0, Spacing.XXS))
        return footer

    @staticmethod
    def create_message_row(parent, title: str, value: str):
        row = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        row.pack(fill=tk.X, pady=(0, Space.SM))
        tk.Label(
            row,
            text=title,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_MUTED,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_12,
                Typography.WEIGHT_MEDIUM,
            ),
        ).pack(anchor="w")
        tk.Label(
            row,
            text=value,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_16,
                Typography.WEIGHT_MEDIUM,
            ),
        ).pack(anchor="w")
        return row

    @staticmethod
    def create_message_bubble(
        parent: tk.Frame,
        *,
        sender: str,
        message: str,
        timestamp: float,
        is_self: bool,
        wraplength: int,
    ):
        """Render a chat bubble (self or peer)."""
        container = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        container.pack(fill=tk.X, expand=True, pady=(Space.XXS, Space.XXS), padx=(Space.MD, Space.MD))

        content = tk.Frame(container, bg=Colors.SURFACE_ALT)
        content.pack(fill=tk.X, expand=True, anchor="e" if is_self else "w")

        if is_self:
            anchor = "e"
            bubble_bg = Colors.BUTTON_PRIMARY_BG
            text_fg = Colors.SURFACE
            name_fg = Colors.TEXT_MUTED
            name_padx = (0, Space.MD)
            bubble_padx = (0, Space.MD)
            msg_justify = "right"
            timestamp_fg = Colors.TEXT_MUTED
        else:
            anchor = "w"
            bubble_bg = Colors.STATE_SUCCESS
            text_fg = Colors.SURFACE
            name_fg = Colors.TEXT_PRIMARY
            name_padx = (Spacing.LG, 0)
            bubble_padx = (Spacing.LG, 0)
            msg_justify = "left"
            timestamp_fg = Colors.TEXT_MUTED

        tk.Label(
            content,
            text=sender,
            bg=Colors.SURFACE_ALT,
            fg=name_fg,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        ).pack(anchor=anchor, padx=name_padx, pady=(0, 1))

        bubble = tk.Frame(content, bg=bubble_bg, padx=int(Space.MD * 0.75), pady=int(Space.XS * 0.8))
        bubble.pack(anchor=anchor, padx=bubble_padx)

        tk.Label(
            bubble,
            text=message,
            bg=bubble_bg,
            fg=text_fg,
            justify=msg_justify,
            wraplength=wraplength,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        ).pack()

        tk.Label(
            content,
            text=time.strftime("%H:%M", time.localtime(timestamp)),
            bg=Colors.SURFACE_ALT,
            fg=timestamp_fg,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        ).pack(anchor=anchor, padx=name_padx, pady=(2, 0))

    @staticmethod
    def create_system_message(parent: tk.Frame, message: str, timestamp: float):
        row = tk.Frame(parent, bg=Colors.MESSAGE_BUBBLE_SYSTEM_BG, padx=Space.LG, pady=Space.XS)
        row.pack(fill=tk.X, padx=Space.MD, pady=(Space.SM, Space.XXS))

        tk.Label(
            row,
            text=message,
            bg=Colors.MESSAGE_BUBBLE_SYSTEM_BG,
            fg=Colors.TEXT_SECONDARY,
            wraplength=720,
            justify="center",
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        ).pack(fill=tk.X, pady=(0, Space.XXS))

        tk.Label(
            row,
            text=time.strftime("%H:%M", time.localtime(timestamp)),
            bg=Colors.MESSAGE_BUBBLE_SYSTEM_BG,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        ).pack(fill=tk.X)
        return row


# ---------------------------------------------------------------------------
# APP CONFIG (unchanged values re-exported)
# ---------------------------------------------------------------------------
class AppConfig:
    """Application-wide configuration constants"""

    DEBUG = False
    STATUS_CONNECTED_KEYWORDS = {
        "ready",
        "connected",
        "connected to",
        "connected (mock)",
        "message from",
    }
    STATUS_DISCONNECTED_KEYWORDS = {
        "disconnected",
        "connection failed",
        "invalid pairing code",
    }
    STATUS_ERROR_KEYWORDS = {"failed", "error", "invalid"}

    STATUS_DISCONNECTED = "Disconnected"
    STATUS_CONNECTED = "Connected"
    STATUS_CONNECTED_MOCK = "Connected (mock)"
    STATUS_CONNECTION_FAILED = "Connection failed"
    STATUS_INVALID_PIN = "Invalid pairing code"
    STATUS_CONNECTION_DEVICE_FAILED = "Connection failed (device not found)"
    STATUS_AWAITING_PEER = "Awaiting peer"
    STATUS_NOT_CONNECTED = "Not connected"

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 820
    MIN_WINDOW_WIDTH = 848
    MIN_WINDOW_HEIGHT = 648
    APP_TITLE = "Locomm"

    STATUS_UPDATE_DELAY = 2000
    RX_THREAD_SLEEP_INTERVAL = 0.2
    MOCK_API_SLEEP_INTERVAL = 0.2
    PIN_FOCUS_DELAY = 100
    STATUS_UPDATE_DELAY_SHORT = 500
    PAIR_DEVICES_TIMEOUT = 30

    CHAT_EXPORT_FILENAME_PATTERN = "locomm_chat_{device}.txt"
    NOTIFICATION_MESSAGE_PATTERN = "Message from {sender}"
    WINDOW_WIDTH_RATIO = 0.595502
    WINDOW_HEIGHT_RATIO = 0.817938


# Legacy exports for compatibility
DEBUG = AppConfig.DEBUG
STATUS_CONNECTED_KEYWORDS = AppConfig.STATUS_CONNECTED_KEYWORDS
STATUS_DISCONNECTED_KEYWORDS = AppConfig.STATUS_DISCONNECTED_KEYWORDS
STATUS_ERROR_KEYWORDS = AppConfig.STATUS_ERROR_KEYWORDS
APP_TITLE = AppConfig.APP_TITLE
WINDOW_WIDTH = AppConfig.WINDOW_WIDTH
WINDOW_HEIGHT = AppConfig.WINDOW_HEIGHT
MIN_WINDOW_WIDTH = AppConfig.MIN_WINDOW_WIDTH
MIN_WINDOW_HEIGHT = AppConfig.MIN_WINDOW_HEIGHT
PAIR_DEVICES_TIMEOUT = AppConfig.PAIR_DEVICES_TIMEOUT
STATUS_DISCONNECTED = AppConfig.STATUS_DISCONNECTED
STATUS_CONNECTED = AppConfig.STATUS_CONNECTED
STATUS_CONNECTED_MOCK = AppConfig.STATUS_CONNECTED_MOCK
STATUS_CONNECTION_FAILED = AppConfig.STATUS_CONNECTION_FAILED
STATUS_INVALID_PIN = AppConfig.STATUS_INVALID_PIN
STATUS_CONNECTION_DEVICE_FAILED = AppConfig.STATUS_CONNECTION_DEVICE_FAILED
STATUS_AWAITING_PEER = AppConfig.STATUS_AWAITING_PEER
STATUS_NOT_CONNECTED = AppConfig.STATUS_NOT_CONNECTED
CHAT_EXPORT_FILENAME_PATTERN = AppConfig.CHAT_EXPORT_FILENAME_PATTERN
NOTIFICATION_MESSAGE_PATTERN = AppConfig.NOTIFICATION_MESSAGE_PATTERN
