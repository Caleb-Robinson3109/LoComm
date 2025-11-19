"""
Simplified theme manager that only focuses on a reliable light/dark toggle.
"""
from __future__ import annotations

from typing import Dict

import tkinter as tk
from tkinter import ttk

from ui.theme_tokens import Colors, Palette, Spacing, Typography


_BASE_THEMES: Dict[str, Dict[str, str]] = {
    "dark": {
        "BG_MAIN": "#1E1E1E",
        "BG_ELEVATED": "#252526",
        "BG_ELEVATED_2": "#2D2D2D",
        "BG_STRIP": "#323233",
        "BG_SOFT": "#2D2D2D",
        "SURFACE": "#1E1E1E",
        "SURFACE_ALT": "#252526",
        "SURFACE_RAISED": "#252526",
        "SURFACE_HEADER": "#252526",
        "SURFACE_SIDEBAR": "#252526",
        "SURFACE_SELECTED": "#2D2D2D",
        "BORDER": "#3C3C3C",
        "DIVIDER": "#2D2D2D",
        "HERO_PANEL_BG": "#252526",
        "HERO_PANEL_TEXT": "#F3F4F6",
        "CARD_PANEL_BG": "#252526",
        "CARD_PANEL_BORDER": "#3C3C3C",
        "PANEL_BG": "#252526",
        "PANEL_BORDER": "#3C3C3C",
        "MAIN_FRAME_BG": "#1E1E1E",
        "BACKDROP_BG": "#252526",
        "TEXT_PRIMARY": "#F3F4F6",
        "TEXT_SECONDARY": "#F3F4F6",
        "TEXT_MUTED": "#9CA3AF",
        "TEXT_ACCENT": Palette.PRIMARY,
        "STATE_SUCCESS": Palette.SIGNAL_TEAL,
        "STATE_WARNING": "#F2A93B",
        "STATE_ERROR": "#C63C3C",
        "STATE_INFO": "#2389FF",
        "STATE_READY": "#2389FF",
        "STATE_TRANSPORT_ERROR": "#6E3FEF",
        "BUTTON_PRIMARY_BG": Palette.PRIMARY,
        "BUTTON_PRIMARY_HOVER": Palette.PRIMARY_HOVER,
        "BUTTON_SECONDARY_BG": "#2D2D2D",
        "BUTTON_GHOST_BG": "#1E1E1E",
        "BUTTON_DANGER_HOVER": "#B23535",
        "BUTTON_DANGER_ACTIVE": "#B23535",
        "BUTTON_SUCCESS_HOVER": "#3FD6C0",
        "BUTTON_SUCCESS_ACTIVE": "#2EC2AD",
        "BUTTON_WARNING_HOVER": "#FFA724",
        "BUTTON_WARNING_ACTIVE": "#F28D1A",
        "ACCENT_PRIMARY": Palette.PRIMARY,
        "ACCENT_PRIMARY_HOVER": Palette.PRIMARY_HOVER,
        "ACCENT_SECONDARY": "#B19CD9",
        "BG_CHAT_AREA": "#1E1E1E",
        "BG_MESSAGE_OWN": Palette.PRIMARY,
        "BG_MESSAGE_OTHER": "#252526",
        "BG_MESSAGE_SYSTEM": "#252526",
        "BG_INPUT_AREA": "#252526",
        "TEXT_PLACEHOLDER": "#9CA3AF",
        "TEXT_TIMESTAMP": "#9CA3AF",
        "MESSAGE_SYSTEM_TEXT": "#9CA3AF",
        "MESSAGE_BUBBLE_OWN_BG": Palette.PRIMARY,
        "MESSAGE_BUBBLE_OTHER_BG": "#252526",
        "MESSAGE_BUBBLE_SYSTEM_BG": "#252526",
        "CHAT_SHELL_BG": "#1E1E1E",
        "CHAT_HISTORY_BG": "#1E1E1E",
        "CHAT_COMPOSER_BG": "#252526",
        "CHAT_HEADER_BG": "#252526",
        "CHAT_HEADER_TEXT": "#F3F4F6",
        "CHAT_BADGE_BG": "#3C3C3C",
        "CHAT_TEXTURE": "#252526",
        "CHAT_BUBBLE_SELF_BG": Palette.PRIMARY,
        "CHAT_BUBBLE_OTHER_BG": "#252526",
        "CHAT_BUBBLE_SYSTEM_BG": "#252526",
        "CHAT_BUBBLE_SELF_TEXT": "#FFFFFF",
        "CHAT_BUBBLE_OTHER_TEXT": "#F3F4F6",
        "CHAT_BUBBLE_SYSTEM_TEXT": "#9CA3AF",
        "NAV_BUTTON_BG": "#252526",
        "NAV_BUTTON_HOVER": "#2D2D2D",
        "NAV_BUTTON_ACTIVE_BG": "#0B7CFF",
        "NAV_BUTTON_ACTIVE_FG": "#FFFFFF",
        "NAV_BUTTON_BORDER": "#2F2F2F",
        "SCROLLBAR_TRACK": "#1E1E1E",
        "SCROLLBAR_THUMB": "#3C3C3C",
        "SCROLLBAR_THUMB_HOVER": "#4B4B4B",
        "LINK_PRIMARY": Palette.PRIMARY,
        "LINK_HOVER": Palette.PRIMARY_HOVER,
    },
    "light": {
        "BG_MAIN": Palette.WHITE,
        "BG_ELEVATED": Palette.CLOUD_050,
        "BG_ELEVATED_2": Palette.CLOUD_100,
        "BG_STRIP": Palette.CLOUD_200,
        "BG_SOFT": Palette.CLOUD_100,
        "SURFACE": Palette.WHITE,
        "SURFACE_ALT": Palette.CLOUD_050,
        "SURFACE_RAISED": Palette.CLOUD_100,
        "SURFACE_HEADER": Palette.CLOUD_050,
        "SURFACE_SIDEBAR": Palette.CLOUD_050,
        "SURFACE_SELECTED": Palette.CLOUD_100,
        "BORDER": Palette.CLOUD_200,
        "DIVIDER": Palette.CLOUD_200,
        "HERO_PANEL_BG": Palette.CLOUD_050,
        "HERO_PANEL_TEXT": Palette.SLATE_900,
        "CARD_PANEL_BG": Palette.CLOUD_050,
        "CARD_PANEL_BORDER": Palette.CLOUD_100,
        "PANEL_BG": Palette.CLOUD_100,
        "PANEL_BORDER": Palette.CLOUD_100,
        "MAIN_FRAME_BG": Palette.WHITE,
        "BACKDROP_BG": Palette.CLOUD_050,
        "TEXT_PRIMARY": Palette.SLATE_900,
        "TEXT_SECONDARY": Palette.SLATE_900,
        "TEXT_MUTED": "#6B7280",
        "TEXT_ACCENT": Palette.PRIMARY,
        "STATE_SUCCESS": Palette.SIGNAL_TEAL,
        "STATE_WARNING": "#F2A93B",
        "STATE_ERROR": "#C63C3C",
        "STATE_INFO": "#0B7CFF",
        "STATE_READY": "#0B7CFF",
        "STATE_TRANSPORT_ERROR": "#6E3FEF",
        "BUTTON_PRIMARY_BG": Palette.PRIMARY,
        "BUTTON_PRIMARY_HOVER": Palette.PRIMARY_HOVER,
        "BUTTON_SECONDARY_BG": Palette.CLOUD_100,
        "BUTTON_GHOST_BG": Palette.WHITE,
        "BUTTON_DANGER_HOVER": "#B23535",
        "BUTTON_DANGER_ACTIVE": "#B23535",
        "BUTTON_SUCCESS_HOVER": "#3FD6C0",
        "BUTTON_SUCCESS_ACTIVE": "#2EC2AD",
        "BUTTON_WARNING_HOVER": "#FFA724",
        "BUTTON_WARNING_ACTIVE": "#F28D1A",
        "ACCENT_PRIMARY": Palette.PRIMARY,
        "ACCENT_PRIMARY_HOVER": Palette.PRIMARY_HOVER,
        "ACCENT_SECONDARY": "#1E293B",
        "BG_CHAT_AREA": Palette.WHITE,
        "BG_MESSAGE_OWN": Palette.PRIMARY,
        "BG_MESSAGE_OTHER": Palette.CLOUD_050,
        "BG_MESSAGE_SYSTEM": Palette.CLOUD_100,
        "BG_INPUT_AREA": Palette.CLOUD_050,
        "TEXT_PLACEHOLDER": "#6B7280",
        "TEXT_TIMESTAMP": "#6B7280",
        "MESSAGE_SYSTEM_TEXT": "#6B7280",
        "MESSAGE_BUBBLE_OWN_BG": Palette.PRIMARY,
        "MESSAGE_BUBBLE_OTHER_BG": Palette.CLOUD_050,
        "MESSAGE_BUBBLE_SYSTEM_BG": Palette.CLOUD_100,
        "CHAT_SHELL_BG": Palette.WHITE,
        "CHAT_HISTORY_BG": Palette.WHITE,
        "CHAT_COMPOSER_BG": Palette.CLOUD_050,
        "CHAT_HEADER_BG": Palette.CLOUD_050,
        "CHAT_HEADER_TEXT": Palette.SLATE_900,
        "CHAT_BADGE_BG": Palette.CLOUD_200,
        "CHAT_TEXTURE": Palette.CLOUD_050,
        "CHAT_BUBBLE_SELF_BG": Palette.PRIMARY,
        "CHAT_BUBBLE_OTHER_BG": Palette.CLOUD_050,
        "CHAT_BUBBLE_SYSTEM_BG": Palette.CLOUD_100,
        "CHAT_BUBBLE_SELF_TEXT": "#FFFFFF",
        "CHAT_BUBBLE_OTHER_TEXT": Palette.SLATE_900,
        "CHAT_BUBBLE_SYSTEM_TEXT": "#6B7280",
        "NAV_BUTTON_BG": Palette.CLOUD_050,
        "NAV_BUTTON_HOVER": Palette.CLOUD_200,
        "NAV_BUTTON_ACTIVE_BG": Palette.PRIMARY,
        "NAV_BUTTON_ACTIVE_FG": Palette.WHITE,
        "NAV_BUTTON_BORDER": Palette.CLOUD_200,
        "SCROLLBAR_TRACK": Palette.CLOUD_050,
        "SCROLLBAR_THUMB": Palette.CLOUD_200,
        "SCROLLBAR_THUMB_HOVER": Palette.CLOUD_300,
        "LINK_PRIMARY": Palette.PRIMARY,
        "LINK_HOVER": Palette.PRIMARY_HOVER,
    },
}

_ACCENTS = {
    "blue": {"primary": Palette.PRIMARY, "hover": Palette.PRIMARY_HOVER},
    "purple": {"primary": "#7C3AED", "hover": "#6D28D9"},
    "green": {"primary": "#059669", "hover": "#047857"},
    "orange": {"primary": "#F97316", "hover": "#EA580C"},
    "pink": {"primary": "#DB2777", "hover": "#BE185D"},
    "red": {"primary": "#DC2626", "hover": "#B91C1C"},
}


_AVAILABLE_MODES = list(_BASE_THEMES.keys())


def get_theme_definition(name: str) -> Dict[str, str] | None:
    theme = _BASE_THEMES.get(name)
    if theme is None:
        return None
    return dict(theme)


def register_custom_theme_definition(name: str, colors: Dict[str, str]) -> None:
    _BASE_THEMES[name] = dict(colors)
    if name not in _AVAILABLE_MODES:
        _AVAILABLE_MODES.append(name)


def unregister_custom_theme_definition(name: str) -> None:
    if name in _BASE_THEMES:
        del _BASE_THEMES[name]
    if name in _AVAILABLE_MODES:
        _AVAILABLE_MODES.remove(name)


def _update_theme_colors(theme: Dict[str, str]) -> None:
    for key, value in theme.items():
        if hasattr(Colors, key):
            setattr(Colors, key, value)
    _update_status_colors()


def _update_status_colors() -> None:
    Colors.STATUS_CONNECTED = Colors.STATE_SUCCESS
    Colors.STATUS_DISCONNECTED = Colors.STATE_ERROR
    Colors.STATUS_CONNECTING = Colors.STATE_INFO
    Colors.STATUS_PAIRING = Colors.STATE_INFO
    Colors.STATUS_READY = Colors.STATE_READY
    Colors.STATUS_TRANSPORT_ERROR = Colors.STATE_TRANSPORT_ERROR


def _apply_accent(accent: str) -> None:
    data = _ACCENTS.get(accent, _ACCENTS["blue"])
    Colors.ACCENT_PRIMARY = data["primary"]
    Colors.ACCENT_PRIMARY_HOVER = data["hover"]
    Colors.ACCENT_SECONDARY = data["hover"]
    Colors.BUTTON_PRIMARY_BG = data["primary"]
    Colors.BUTTON_PRIMARY_HOVER = data["hover"]
    Colors.LINK_PRIMARY = data["primary"]
    Colors.LINK_HOVER = data["hover"]
    Colors.BG_MESSAGE_OWN = data["primary"]
    Colors.MESSAGE_BUBBLE_OWN_BG = data["primary"]
    Colors.CHAT_BUBBLE_SELF_BG = data["primary"]


class ThemeManager:
    """Minimal theme manager with reliable dark/light toggling."""

    BUTTON_STYLES = {
        "primary": "Locomm.Primary.TButton",
        "secondary": "Locomm.Secondary.TButton",
        "ghost": "Locomm.Ghost.TButton",
        "danger": "Locomm.Danger.TButton",
        "success": "Locomm.Success.TButton",
        "warning": "Locomm.Warning.TButton",
    }

    _current_mode = "light"
    _current_accent = "blue"
    _initialized = False
    _available_modes = _AVAILABLE_MODES

    @classmethod
    def ensure(cls) -> None:
        cls._apply_theme()
        cls._configure_styles()

    @classmethod
    def _apply_theme(cls) -> None:
        theme = _BASE_THEMES.get(cls._current_mode, _BASE_THEMES["light"])
        _update_theme_colors(theme)
        _apply_accent(cls._current_accent)

    @classmethod
    def _configure_styles(cls) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        cls._register_button_styles(style)
        cls._configure_nav_styles(style)
        cls._configure_entry_styles(style)
        cls._configure_scrollbars(style)
        cls._initialized = True

    @classmethod
    def _register_button_styles(cls, style: ttk.Style) -> None:
        config = {
            "Locomm.Primary.TButton": dict(
                bg=Colors.BUTTON_PRIMARY_BG,
                hover=Colors.BUTTON_PRIMARY_HOVER,
                active=Colors.BUTTON_PRIMARY_HOVER,
                fg=Colors.SURFACE,
            ),
            "Locomm.Secondary.TButton": dict(
                bg=Colors.BUTTON_SECONDARY_BG,
                hover=Colors.BUTTON_PRIMARY_BG,
                active=Colors.BUTTON_PRIMARY_BG,
                fg=Colors.TEXT_PRIMARY,
            ),
            "Locomm.Ghost.TButton": dict(
                bg=Colors.BUTTON_GHOST_BG,
                hover=Colors.SURFACE_ALT,
                active=Colors.SURFACE_ALT,
                fg=Colors.TEXT_PRIMARY,
            ),
            "Locomm.Danger.TButton": dict(
                bg=Colors.STATE_ERROR,
                hover=Colors.BUTTON_DANGER_HOVER,
                active=Colors.BUTTON_DANGER_ACTIVE,
                fg=Colors.SURFACE,
            ),
            "Locomm.Success.TButton": dict(
                bg=Colors.STATE_SUCCESS,
                hover=Colors.BUTTON_SUCCESS_HOVER,
                active=Colors.BUTTON_SUCCESS_ACTIVE,
                fg=Colors.SURFACE,
            ),
            "Locomm.Warning.TButton": dict(
                bg=Colors.STATE_WARNING,
                hover=Colors.BUTTON_WARNING_HOVER,
                active=Colors.BUTTON_WARNING_ACTIVE,
                fg=Colors.SURFACE,
            ),
        }

        for style_name, cfg in config.items():
            cls._register_button(style, style_name, **cfg)

    @staticmethod
    def _register_button(style: ttk.Style, style_name: str, *, bg, hover, active, fg) -> None:
        layout = [
            (
                "Button.border",
                {
                    "sticky": "nswe",
                    "children": [
                        (
                            "Button.padding",
                            {
                                "sticky": "nswe",
                                "children": [("Button.label", {"sticky": "nswe"})],
                            },
                        )
                    ],
                },
            )
        ]
        style.layout(style_name, layout)
        style.configure(
            style_name,
            background=bg,
            foreground=fg,
            padding=(Spacing.LG, Spacing.SM),
            borderwidth=0,
            relief="flat",
            focusthickness=1,
            focuscolor=Colors.BORDER,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
        )
        style.map(
            style_name,
            background=[
                ("pressed", active),
                ("active", active),
                ("hover", hover),
            ],
            foreground=[("disabled", Colors.TEXT_MUTED)],
            relief=[("pressed", "flat"), ("!pressed", "flat")],
        )

    @classmethod
    def _configure_nav_styles(cls, style: ttk.Style) -> None:
        for style_name in ("Locomm.Nav.TButton", "Locomm.NavActive.TButton"):
            layout = [
                (
                    "Button.border",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Button.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [("Button.label", {"sticky": "w"})],
                                },
                            )
                        ],
                    },
                )
            ]
            style.layout(style_name, layout)

        style.configure(
            "Locomm.Nav.TButton",
            background=Colors.NAV_BUTTON_BG,
            foreground=Colors.TEXT_MUTED,
            bordercolor=Colors.NAV_BUTTON_BORDER,
            borderwidth=1,
            relief="flat",
            padding=(Spacing.MD, Spacing.SM),
            anchor="w",
            focusthickness=0,
            highlightthickness=0,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
        )
        style.map(
            "Locomm.Nav.TButton",
            background=[("hover", Colors.NAV_BUTTON_HOVER), ("active", Colors.NAV_BUTTON_HOVER)],
            foreground=[("hover", Colors.TEXT_PRIMARY), ("active", Colors.TEXT_PRIMARY)],
        )

        style.configure(
            "Locomm.NavActive.TButton",
            background=Colors.NAV_BUTTON_ACTIVE_BG,
            foreground=Colors.NAV_BUTTON_ACTIVE_FG,
            bordercolor=Colors.NAV_BUTTON_BORDER,
            borderwidth=1,
            relief="flat",
            padding=(Spacing.MD, Spacing.SM),
            anchor="w",
            focusthickness=0,
            highlightthickness=0,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
        )

    @classmethod
    def _configure_entry_styles(cls, style: ttk.Style) -> None:
        style.configure(
            "Locomm.Input.TEntry",
            fieldbackground=Colors.SURFACE_RAISED,
            foreground=Colors.TEXT_PRIMARY,
            insertcolor=Colors.TEXT_PRIMARY,
            padding=(Spacing.LG, Spacing.SM),
            bordercolor=Colors.BORDER,
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Locomm.PinEntry.TEntry",
            fieldbackground=Colors.SURFACE,
            foreground=Colors.TEXT_PRIMARY,
            insertcolor=Colors.TEXT_PRIMARY,
            padding=Spacing.XXS,
            bordercolor=Colors.BORDER,
            borderwidth=1,
            relief="solid",
        )

    @classmethod
    def _configure_scrollbars(cls, style: ttk.Style) -> None:
        try:
            style.configure(
                "Vertical.TScrollbar",
                troughcolor=Colors.BG_MAIN,
                background=Colors.SCROLLBAR_THUMB,
                bordercolor=Colors.BG_MAIN,
                arrowcolor=Colors.TEXT_MUTED,
                width=10,
            )
            style.map(
                "Vertical.TScrollbar",
                background=[("active", Colors.SCROLLBAR_THUMB_HOVER)],
            )
            style.configure(
                "Horizontal.TScrollbar",
                troughcolor=Colors.BG_MAIN,
                background=Colors.SCROLLBAR_THUMB,
                bordercolor=Colors.BG_MAIN,
                arrowcolor=Colors.TEXT_MUTED,
                width=10,
            )
            style.map(
                "Horizontal.TScrollbar",
                background=[("active", Colors.SCROLLBAR_THUMB_HOVER)],
            )
        except tk.TclError:
            pass

    @classmethod
    def toggle_mode(cls, dark: bool) -> None:
        mode = "dark" if dark else "light"
        if mode == cls._current_mode:
            return
        cls._current_mode = mode
        cls._apply_theme()
        if cls._initialized:
            cls._configure_styles()

    @classmethod
    def set_mode(cls, mode: str) -> None:
        if mode not in _AVAILABLE_MODES:
            raise ValueError(f"Unknown theme mode '{mode}'")
        cls._current_mode = mode
        cls._apply_theme()
        if cls._initialized:
            cls._configure_styles()

    @classmethod
    def current_mode(cls) -> str:
        return cls._current_mode

    @classmethod
    def get_available_modes(cls) -> list[str]:
        return list(_AVAILABLE_MODES)

    @classmethod
    def get_current_accent_name(cls) -> str:
        return cls._current_accent

    @classmethod
    def set_accent_color(cls, accent: str) -> None:
        if accent not in _ACCENTS:
            raise ValueError(f"Unknown accent '{accent}'")
        cls._current_accent = accent
        _apply_accent(accent)
        if cls._initialized:
            cls._configure_styles()

    @classmethod
    def refresh_styles(cls) -> None:
        if cls._initialized:
            cls._configure_styles()

    @classmethod
    def validate_contrast_ratio(cls, foreground: str, background: str) -> float:
        def get_luminance(color: str) -> float:
            color = (color or "").lstrip("#")
            if len(color) != 6:
                return 0.5
            try:
                r, g, b = (int(color[i:i + 2], 16) for i in (0, 2, 4))
            except ValueError:
                return 0.5

            def linearize(component: int) -> float:
                c = component / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

            return (
                0.2126 * linearize(r)
                + 0.7152 * linearize(g)
                + 0.0722 * linearize(b)
            )

        l1 = get_luminance(foreground)
        l2 = get_luminance(background)
        if l1 < l2:
            l1, l2 = l2, l1
        return (l1 + 0.05) / (l2 + 0.05)

    @classmethod
    def check_wcag_compliance(cls, foreground: str, background: str, level: str = "AA") -> dict:
        ratio = cls.validate_contrast_ratio(foreground, background)
        thresholds = {
            "AA": {"normal": 4.5, "large": 3.0},
            "AAA": {"normal": 7.0, "large": 4.5},
        }.get(level.upper(), {"normal": 4.5, "large": 3.0})
        return {
            "ratio": round(ratio, 2),
            "aa_normal": ratio >= thresholds["normal"],
            "aa_large": ratio >= thresholds["large"],
            "compliant": ratio >= thresholds["normal"],
        }

    @classmethod
    def simulate_colorblindness(cls, color: str, type_: str = "deuteranopia") -> str:
        matrices = {
            "protanopia": [
                [0.567, 0.433, 0.000],
                [0.558, 0.442, 0.000],
                [0.000, 0.242, 0.758],
            ],
            "deuteranopia": [
                [0.625, 0.375, 0.000],
                [0.700, 0.300, 0.000],
                [0.000, 0.300, 0.700],
            ],
            "tritanopia": [
                [0.950, 0.050, 0.000],
                [0.000, 0.433, 0.567],
                [0.000, 0.475, 0.525],
            ],
        }
        color = (color or "").lstrip("#")
        if len(color) != 6:
            return "#7f7f7f"
        r, g, b = (int(color[i:i + 2], 16) for i in (0, 2, 4))
        matrix = matrices.get(type_, matrices["deuteranopia"])
        new_r = int(r * matrix[0][0] + g * matrix[0][1] + b * matrix[0][2])
        new_g = int(r * matrix[1][0] + g * matrix[1][1] + b * matrix[1][2])
        new_b = int(r * matrix[2][0] + g * matrix[2][1] + b * matrix[2][2])
        new_r = max(0, min(255, new_r))
        new_g = max(0, min(255, new_g))
        new_b = max(0, min(255, new_b))
        return f"#{new_r:02x}{new_g:02x}{new_b:02x}"

    @classmethod
    def get_accessibility_summary(cls) -> dict:
        text_contrast = cls.check_wcag_compliance(Colors.TEXT_PRIMARY, Colors.SURFACE)
        button_contrast = cls.check_wcag_compliance(Colors.SURFACE, Colors.BUTTON_PRIMARY_BG)
        return {
            "mode": cls._current_mode,
            "text_contrast": text_contrast,
            "button_contrast": button_contrast,
        }


def ensure_styles_initialized() -> None:
    ThemeManager.ensure()
