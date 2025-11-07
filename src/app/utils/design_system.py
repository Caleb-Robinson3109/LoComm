"""
Locomm Design System v3
Provides a layered token/component-based styling toolkit for the desktop app.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# DESIGN TOKENS
# ---------------------------------------------------------------------------
class Palette:
    """Foundational color palette."""

    NIGHT_1000 = "#05070A"
    NIGHT_950 = "#0B0E13"
    NIGHT_900 = "#10141C"
    NIGHT_850 = "#141925"
    NIGHT_800 = "#1B2030"
    NIGHT_700 = "#212738"
    NIGHT_600 = "#2C3448"
    NIGHT_500 = "#343C52"
    CLOUD_300 = "#9AA2B1"
    CLOUD_200 = "#B7C0D4"
    CLOUD_100 = "#D3DCEA"
    CLOUD_050 = "#F5F6FA"

    ACCENT_BLUE = "#6CC1FF"
    ACCENT_PURPLE = "#9A7BFF"
    ACCENT_TEAL = "#2DE1C2"
    ACCENT_AMBER = "#FFB347"
    ACCENT_RED = "#FF6B6B"
    ACCENT_GREEN = "#3DD598"


class Colors:
    """Semantic color mapping used throughout the UI."""

    SURFACE = Palette.NIGHT_900
    SURFACE_ALT = Palette.NIGHT_850
    SURFACE_RAISED = Palette.NIGHT_800
    SURFACE_HEADER = Palette.NIGHT_950
    SURFACE_SIDEBAR = Palette.NIGHT_950
    SURFACE_SELECTED = Palette.NIGHT_800

    BORDER = Palette.NIGHT_600
    DIVIDER = Palette.NIGHT_600

    TEXT_PRIMARY = Palette.CLOUD_050
    TEXT_SECONDARY = Palette.CLOUD_200
    TEXT_MUTED = Palette.CLOUD_300
    TEXT_ACCENT = Palette.ACCENT_BLUE

    STATE_SUCCESS = Palette.ACCENT_GREEN
    STATE_WARNING = Palette.ACCENT_AMBER
    STATE_ERROR = Palette.ACCENT_RED
    STATE_INFO = Palette.ACCENT_BLUE
    STATUS_CONNECTED = STATE_SUCCESS
    STATUS_DISCONNECTED = STATE_ERROR
    STATUS_CONNECTING = STATE_INFO
    STATUS_PAIRING = STATE_INFO

    BUTTON_PRIMARY_BG = Palette.ACCENT_BLUE
    BUTTON_PRIMARY_HOVER = "#54A3DB"
    BUTTON_SECONDARY_BG = Palette.NIGHT_700
    BUTTON_GHOST_BG = "#00000000"

    # Backwards compatibility aliases
    BG_PRIMARY = SURFACE
    BG_SECONDARY = SURFACE_ALT
    BG_TERTIARY = SURFACE_RAISED
    BG_CHAT_AREA = SURFACE
    BG_MESSAGE_OWN = Palette.ACCENT_BLUE
    BG_MESSAGE_OTHER = SURFACE_ALT
    BG_MESSAGE_SYSTEM = SURFACE_RAISED
    BG_INPUT_AREA = SURFACE_RAISED
    TEXT_PLACEHOLDER = TEXT_MUTED
    TEXT_TIMESTAMP = TEXT_MUTED
    MESSAGE_SYSTEM_TEXT = TEXT_SECONDARY


class Typography:
    """Typography scale (8pt grid)."""

    FONT_UI = "SF Pro Display"
    FONT_MONO = "JetBrains Mono"

    SIZE_12 = 12
    SIZE_14 = 14
    SIZE_16 = 16
    SIZE_18 = 18
    SIZE_20 = 20
    SIZE_24 = 24
    SIZE_32 = 32

    WEIGHT_REGULAR = "normal"
    WEIGHT_MEDIUM = "normal"  # Tkinter does not support "medium"
    WEIGHT_BOLD = "bold"


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
    HEADER_PADDING = Space.XL
    BUTTON_PADDING = Space.SM
    SECTION_MARGIN = Space.LG
    MESSAGE_BUBBLE_PADDING = (Space.LG, Space.SM)
    MESSAGE_GROUP_GAP = Space.XXS
    MESSAGE_MARGIN = (Space.SM, Space.XXS)
    CHAT_AREA_PADDING = Space.MD
    SIDEBAR_WIDTH = 260
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
        if "clam" in style.theme_names():
            style.theme_use("clam")

        default_font = (Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR)
        style.configure("TLabel", background=Colors.SURFACE, foreground=Colors.TEXT_PRIMARY, font=default_font)
        style.configure("TFrame", background=Colors.SURFACE)

        # Buttons -----------------------------------------------------------------
        cls._register_button(style, "Locomm.Primary.TButton", Colors.BUTTON_PRIMARY_BG, Colors.BUTTON_PRIMARY_HOVER, Colors.SURFACE)
        cls._register_button(style, "Locomm.Secondary.TButton", Colors.BUTTON_SECONDARY_BG, Palette.NIGHT_600, Colors.TEXT_PRIMARY)
        cls._register_button(style, "Locomm.Ghost.TButton", Colors.BUTTON_GHOST_BG, Palette.NIGHT_800, Colors.TEXT_PRIMARY, border=0)
        cls._register_button(style, "Locomm.Danger.TButton", Palette.ACCENT_RED, "#CC4C4C", Colors.SURFACE)
        cls._register_button(style, "Locomm.Success.TButton", Palette.ACCENT_GREEN, "#2FB67C", Colors.SURFACE)

        # Navigation buttons (flat, left aligned)
        style.configure(
            "Locomm.Nav.TButton",
            background=Colors.SURFACE,
            foreground=Colors.TEXT_SECONDARY,
            relief="flat",
            anchor="w",
            padding=(Space.MD, Space.SM),
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM)
        )
        style.map(
            "Locomm.Nav.TButton",
            background=[("active", Colors.SURFACE_SELECTED)],
            foreground=[("active", Colors.TEXT_PRIMARY)]
        )
        style.configure(
            "Locomm.NavActive.TButton",
            background=Colors.SURFACE_SELECTED,
            foreground=Colors.TEXT_PRIMARY,
            relief="flat",
            anchor="w",
            padding=(Space.MD, Space.SM),
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD)
        )

        # Entry / input fields
        style.configure(
            "Locomm.Input.TEntry",
            fieldbackground=Colors.SURFACE_RAISED,
            foreground=Colors.TEXT_PRIMARY,
            insertcolor=Colors.TEXT_PRIMARY,
            padding=(Space.SM, int(Space.XS / 1.5)),
            bordercolor=Colors.BORDER
        )
        style.map(
            "Locomm.Input.TEntry",
            fieldbackground=[("focus", Colors.SURFACE_SELECTED)],
            foreground=[("disabled", Colors.TEXT_MUTED)]
        )

        # Labels ------------------------------------------------------------------
        style.configure("Locomm.H1.TLabel", font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD))
        style.configure("Locomm.H2.TLabel", font=(Typography.FONT_UI, Typography.SIZE_20, Typography.WEIGHT_BOLD))
        style.configure("Locomm.H3.TLabel", font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_MEDIUM))
        style.configure("Locomm.Caption.TLabel", font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM), foreground=Colors.TEXT_MUTED)
        # Legacy style aliases
        style.configure('Header.TLabel', font=(Typography.FONT_UI, Typography.SIZE_20, Typography.WEIGHT_BOLD), foreground=Colors.TEXT_PRIMARY, background=Colors.SURFACE)
        style.configure('SubHeader.TLabel', font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_MEDIUM), foreground=Colors.TEXT_SECONDARY, background=Colors.SURFACE)
        style.configure('Body.TLabel', font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR), foreground=Colors.TEXT_PRIMARY, background=Colors.SURFACE)
        style.configure('Small.TLabel', font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR), foreground=Colors.TEXT_MUTED, background=Colors.SURFACE)

        # Cards / sections
        style.configure(
            "Locomm.Card.TFrame",
            background=Colors.SURFACE_ALT,
            bordercolor=Colors.BORDER,
            relief="flat",
            borderwidth=1
        )
        style.configure(
            "Locomm.Section.TFrame",
            background=Colors.SURFACE_ALT,
            bordercolor=Colors.BORDER,
            relief="flat",
            borderwidth=1
        )

        # Badges
        style.configure(
            "Locomm.Badge.Info.TLabel",
            background=Colors.BUTTON_SECONDARY_BG,
            foreground=Colors.TEXT_PRIMARY,
            padding=(Space.SM, int(Space.XS)),
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)
        )

        # Backwards compatibility styles (legacy names)
        style.configure("Primary.TButton", background=Colors.BUTTON_PRIMARY_BG, foreground=Colors.SURFACE)
        style.configure("Secondary.TButton", background=Colors.BUTTON_SECONDARY_BG, foreground=Colors.TEXT_PRIMARY)

        cls._initialized = True

    @staticmethod
    def _register_button(style: ttk.Style, style_name: str, bg: str, hover_bg: str, fg: str, border: int = 0):
        style.configure(
            style_name,
            background=bg,
            foreground=fg,
            padding=(Space.MD, Space.SM),
            borderwidth=border,
            focusthickness=0,
            focuscolor=bg,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM)
        )
        style.map(
            style_name,
            background=[("active", hover_bg), ("disabled", Colors.BUTTON_SECONDARY_BG)],
            foreground=[("disabled", Colors.TEXT_MUTED)]
        )


def ensure_styles_initialized():
    ThemeManager.ensure()


# ---------------------------------------------------------------------------
# COMPONENT FACTORY
# ---------------------------------------------------------------------------
class DesignUtils:
    """Factory helpers that return styled widgets."""

    @staticmethod
    def button(parent, text: str, command=None, variant: str = "primary", width: int | None = None):
        ThemeManager.ensure()
        style_name = ThemeManager.BUTTON_STYLES.get(variant, "Locomm.Primary.TButton")
        return ttk.Button(parent, text=text, command=command, style=style_name, width=width)

    @staticmethod
    def pill(parent, text: str, variant: str = "info"):
        ThemeManager.ensure()
        variant_map = {
            "info": (Colors.BUTTON_SECONDARY_BG, Colors.TEXT_PRIMARY),
            "success": (Palette.ACCENT_GREEN, Colors.SURFACE),
            "warning": (Palette.ACCENT_AMBER, Colors.SURFACE),
            "danger": (Palette.ACCENT_RED, Colors.SURFACE),
        }
        bg, fg = variant_map.get(variant, variant_map["info"])
        label = tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
            padx=Space.SM,
            pady=int(Space.XS / 2)
        )
        label.configure(relief="flat")
        return label

    @staticmethod
    def card(parent, title: str, subtitle: str = "", actions: list | None = None):
        ThemeManager.ensure()
        frame = tk.Frame(parent, bg=Colors.SURFACE_ALT, highlightbackground=Colors.BORDER, highlightthickness=1, bd=0)
        frame.pack_propagate(False)

        header = tk.Frame(frame, bg=Colors.SURFACE_ALT)
        header.pack(fill=tk.X, pady=(Space.SM, 0), padx=Space.MD)

        tk.Label(header, text=title, bg=Colors.SURFACE_ALT,
                 fg=Colors.TEXT_PRIMARY,
                 font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD)).pack(anchor="w")
        if subtitle:
            tk.Label(header, text=subtitle, bg=Colors.SURFACE_ALT,
                     fg=Colors.TEXT_MUTED,
                     font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="w", pady=(Space.XXS, 0))

        if actions:
            actions_frame = tk.Frame(frame, bg=Colors.SURFACE_ALT)
            actions_frame.pack(fill=tk.X, padx=Space.MD, pady=(Space.XS, Space.SM))
            for action in actions:
                btn = DesignUtils.button(actions_frame, **action)
                btn.pack(side=tk.LEFT, padx=(0, Space.SM))

        body = tk.Frame(frame, bg=Colors.SURFACE_ALT)
        body.pack(fill=tk.BOTH, expand=True, padx=Space.MD, pady=(0, Space.MD))
        return frame, body

    @staticmethod
    def section(parent, title: str, description: str = "", icon: str | None = None):
        ThemeManager.ensure()
        container = tk.Frame(parent, bg=Colors.SURFACE_ALT, highlightbackground=Colors.DIVIDER, highlightthickness=1, bd=0)
        container.pack(fill=tk.X, pady=(0, Space.LG))

        header = tk.Frame(container, bg=Colors.SURFACE_ALT)
        header.pack(fill=tk.X, padx=Space.LG, pady=(Space.MD, Space.SM))

        title_text = title if not icon else f"{icon} {title}"
        tk.Label(header, text=title_text, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_PRIMARY,
                 font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD)).pack(anchor="w")
        if description:
            tk.Label(header, text=description, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                     font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="w", pady=(Space.XXS, 0))

        body = tk.Frame(container, bg=Colors.SURFACE_ALT)
        body.pack(fill=tk.X, padx=Space.LG, pady=(0, Space.LG))
        return container, body

    @staticmethod
    def stat_block(parent, label: str, value: str, helper: str = ""):
        block = tk.Frame(parent, bg=Colors.SURFACE_RAISED)
        block.pack(fill=tk.X, padx=0, pady=(0, Space.SM))
        tk.Label(block, text=label.upper(), bg=Colors.SURFACE_RAISED, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w")
        tk.Label(block, text=value, bg=Colors.SURFACE_RAISED, fg=Colors.TEXT_PRIMARY,
                 font=(Typography.FONT_UI, Typography.SIZE_20, Typography.WEIGHT_BOLD)).pack(anchor="w", pady=(Space.XXS, 0))
        if helper:
            tk.Label(block, text=helper, bg=Colors.SURFACE_RAISED, fg=Colors.TEXT_SECONDARY,
                     font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="w")
        return block

    @staticmethod
    def hero_header(parent, title: str, subtitle: str, actions: list | None = None):
        container = tk.Frame(parent, bg=Colors.SURFACE, pady=Space.LG)
        container.pack(fill=tk.X, pady=(0, Space.LG))
        text_wrap = tk.Frame(container, bg=Colors.SURFACE)
        text_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(text_wrap, text=title, bg=Colors.SURFACE, fg=Colors.TEXT_PRIMARY,
                 font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD)).pack(anchor="w")
        tk.Label(text_wrap, text=subtitle, bg=Colors.SURFACE, fg=Colors.TEXT_SECONDARY,
                 font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR)).pack(anchor="w", pady=(Space.XS, 0))

        if actions:
            action_frame = tk.Frame(container, bg=Colors.SURFACE)
            action_frame.pack(side=tk.RIGHT, anchor="e")
            for action in actions:
                btn = DesignUtils.button(action_frame, **action)
                btn.pack(side=tk.LEFT, padx=(0, Space.SM))

        return container

    @staticmethod
    def create_styled_button(parent, text: str, command=None, style: str = 'Locomm.Primary.TButton'):
        """Backwards-compatible helper."""
        ThemeManager.ensure()
        return ttk.Button(parent, text=text, command=command, style=style)

    @staticmethod
    def create_styled_label(parent, text: str, style: str = 'Body.TLabel', **kwargs):
        ThemeManager.ensure()
        return ttk.Label(parent, text=text, style=style, **kwargs)

    @staticmethod
    def create_chat_entry(parent, **kwargs):
        ThemeManager.ensure()
        return ttk.Entry(parent, style="Locomm.Input.TEntry", **kwargs)

    @staticmethod
    def create_nav_button(parent, text: str, command=None):
        ThemeManager.ensure()
        return ttk.Button(parent, text=text, command=command, style="Locomm.Nav.TButton")

    @staticmethod
    def create_message_row(parent, title: str, value: str):
        row = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        row.pack(fill=tk.X, pady=(0, Space.SM))
        tk.Label(row, text=title, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w")
        tk.Label(row, text=value, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_PRIMARY,
                 font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_MEDIUM)).pack(anchor="w")
        return row


# ---------------------------------------------------------------------------
# APP CONFIG (unchanged values re-exported)
# ---------------------------------------------------------------------------
class AppConfig:
    """Application-wide configuration constants"""

    DEBUG = False
    STATUS_CONNECTED_KEYWORDS = {"ready", "connected (mock)", "message from"}
    STATUS_DISCONNECTED_KEYWORDS = {"disconnected", "connection failed", "invalid pairing code"}
    STATUS_ERROR_KEYWORDS = {"failed", "error", "invalid"}

    STATUS_DISCONNECTED = "Disconnected"
    STATUS_CONNECTED = "Connected"
    STATUS_CONNECTED_MOCK = "Connected (mock)"
    STATUS_CONNECTION_FAILED = "Connection failed"
    STATUS_INVALID_PIN = "Invalid pairing code"
    STATUS_CONNECTION_DEVICE_FAILED = "Connection failed (device not found)"
    STATUS_AWAITING_PEER = "Awaiting peer"
    STATUS_NOT_CONNECTED = "Not connected"

    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 720
    APP_TITLE = "LoRa Chat Desktop"

    STATUS_UPDATE_DELAY = 2000
    RX_THREAD_SLEEP_INTERVAL = 0.2
    MOCK_API_SLEEP_INTERVAL = 0.2
    PIN_FOCUS_DELAY = 100
    STATUS_UPDATE_DELAY_SHORT = 500
    PAIR_DEVICES_TIMEOUT = 30

    CHAT_EXPORT_FILENAME_PATTERN = "locomm_chat_{device}.txt"
    NOTIFICATION_MESSAGE_PATTERN = "Message from {sender}"


# Legacy exports for compatibility
DEBUG = AppConfig.DEBUG
STATUS_CONNECTED_KEYWORDS = AppConfig.STATUS_CONNECTED_KEYWORDS
STATUS_DISCONNECTED_KEYWORDS = AppConfig.STATUS_DISCONNECTED_KEYWORDS
STATUS_ERROR_KEYWORDS = AppConfig.STATUS_ERROR_KEYWORDS
APP_TITLE = AppConfig.APP_TITLE
WINDOW_WIDTH = AppConfig.WINDOW_WIDTH
WINDOW_HEIGHT = AppConfig.WINDOW_HEIGHT
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

import os
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
