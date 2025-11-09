"""Theme registration and helper utilities for Locomm UI."""
from __future__ import annotations

from typing import Dict

import tkinter as tk
from tkinter import ttk

from ui.theme_tokens import Colors, Palette, Spacing, Typography


_THEME_DEFINITIONS = {
    "dark": {
        "SURFACE": Palette.SLATE_900,
        "SURFACE_ALT": "#1C1F2E",
        "SURFACE_RAISED": "#242A3C",
        "SURFACE_HEADER": "#12162A",
        "SURFACE_SIDEBAR": "#101428",
        "SURFACE_SELECTED": "#2D3564",
        "BORDER": "#2A2E44",
        "DIVIDER": "#232944",
        "TEXT_PRIMARY": Palette.CLOUD_050,
        "TEXT_SECONDARY": Palette.CLOUD_300,
        "TEXT_MUTED": Palette.CLOUD_500,
        "TEXT_ACCENT": Palette.SIGNAL_BLUE,
        "STATE_SUCCESS": Palette.SIGNAL_TEAL,
        "STATE_WARNING": Palette.SIGNAL_WARNING,
        "STATE_ERROR": Palette.SIGNAL_RED,
        "STATE_INFO": Palette.SIGNAL_BLUE,
        "STATE_READY": "#C18DFF",
        "STATE_TRANSPORT_ERROR": "#6E3FEF",
        "BUTTON_PRIMARY_BG": Palette.SIGNAL_BLUE,
        "BUTTON_PRIMARY_HOVER": Palette.SIGNAL_BLUE_LIGHT,
        "BUTTON_SECONDARY_BG": "#2F3251",
        "BUTTON_GHOST_BG": "#1F2236",
        "BG_PRIMARY": Palette.SLATE_900,
        "BG_SECONDARY": "#1F2437",
        "BG_TERTIARY": "#222743",
        "BG_CHAT_AREA": "#171C2C",
        "BG_MESSAGE_OWN": Palette.SIGNAL_BLUE,
        "BG_MESSAGE_OTHER": "#1F233C",
        "BG_MESSAGE_SYSTEM": "#1B1F33",
        "BG_INPUT_AREA": "#1D2337",
        "TEXT_PLACEHOLDER": Palette.CLOUD_500,
        "TEXT_TIMESTAMP": Palette.CLOUD_500,
        "MESSAGE_SYSTEM_TEXT": Palette.CLOUD_500,
        "MESSAGE_BUBBLE_OWN_BG": Palette.SIGNAL_BLUE,
        "MESSAGE_BUBBLE_OTHER_BG": "#1C2038",
        "MESSAGE_BUBBLE_SYSTEM_BG": "#1A1E33",
    },
    "light": {
        "SURFACE": Palette.WHITE,
        "SURFACE_ALT": "#F6F8FF",
        "SURFACE_RAISED": "#EFF2FF",
        "SURFACE_HEADER": "#F8F9FF",
        "SURFACE_SIDEBAR": "#F7F9FF",
        "SURFACE_SELECTED": "#D3E2FF",
        "BORDER": "#E1E5F0",
        "DIVIDER": "#D8DCE4",
        "TEXT_PRIMARY": Palette.SLATE_900,
        "TEXT_SECONDARY": Palette.SLATE_700,
        "TEXT_MUTED": Palette.CLOUD_500,
        "TEXT_ACCENT": Palette.SIGNAL_BLUE,
        "STATE_SUCCESS": Palette.SIGNAL_TEAL,
        "STATE_WARNING": "#FFAF40",
        "STATE_ERROR": Palette.SIGNAL_RED,
        "STATE_INFO": Palette.SIGNAL_BLUE,
        "STATE_READY": "#C18DFF",
        "STATE_TRANSPORT_ERROR": "#6E3FEF",
        "BUTTON_PRIMARY_BG": Palette.SIGNAL_BLUE_LIGHT,
        "BUTTON_PRIMARY_HOVER": Palette.SIGNAL_BLUE,
        "BUTTON_SECONDARY_BG": Palette.CLOUD_200,
        "BUTTON_GHOST_BG": "#FFFFFF",
        "BG_PRIMARY": Palette.WHITE,
        "BG_SECONDARY": Palette.CLOUD_050,
        "BG_TERTIARY": Palette.CLOUD_100,
        "BG_CHAT_AREA": Palette.CLOUD_050,
        "BG_MESSAGE_OWN": Palette.SIGNAL_BLUE_LIGHT,
        "BG_MESSAGE_OTHER": Palette.CLOUD_100,
        "BG_MESSAGE_SYSTEM": Palette.CLOUD_050,
        "BG_INPUT_AREA": Palette.CLOUD_100,
        "TEXT_PLACEHOLDER": Palette.CLOUD_500,
        "TEXT_TIMESTAMP": Palette.CLOUD_500,
        "MESSAGE_SYSTEM_TEXT": Palette.CLOUD_500,
        "MESSAGE_BUBBLE_OWN_BG": Palette.SIGNAL_BLUE_LIGHT,
        "MESSAGE_BUBBLE_OTHER_BG": Palette.CLOUD_100,
        "MESSAGE_BUBBLE_SYSTEM_BG": Palette.CLOUD_050,
    },
}


class ThemeManager:
    _initialized = False
    _current_mode = "dark"
    BUTTON_STYLES = {
        "primary": "Locomm.Primary.TButton",
        "secondary": "Locomm.Secondary.TButton",
        "ghost": "Locomm.Ghost.TButton",
        "danger": "Locomm.Danger.TButton",
        "success": "Locomm.Success.TButton",
    }

    @classmethod
    def ensure(cls):
        if cls._initialized:
            return
        theme = _THEME_DEFINITIONS[cls._current_mode]
        _apply_theme_definition(theme)
        cls._register_button_styles()
        cls._initialized = True

    @staticmethod
    def _register_button_styles():
        style = ttk.Style()
        button_configs = {
            "Locomm.Primary.TButton": dict(
                bg=Colors.BUTTON_PRIMARY_BG,
                hover_bg=Colors.BUTTON_PRIMARY_HOVER,
                active_bg=Colors.BUTTON_PRIMARY_HOVER,
                fg=Colors.SURFACE,
            ),
            "Locomm.Secondary.TButton": dict(
                bg=Colors.BUTTON_SECONDARY_BG,
                hover_bg=Colors.BUTTON_PRIMARY_BG,
                active_bg=Colors.BUTTON_PRIMARY_BG,
                fg=Colors.SURFACE,
            ),
            "Locomm.Ghost.TButton": dict(
                bg=Colors.BUTTON_GHOST_BG,
                hover_bg=Colors.SURFACE_SELECTED,
                active_bg=Colors.SURFACE_SELECTED,
                fg=Colors.TEXT_PRIMARY,
            ),
            "Locomm.Danger.TButton": dict(
                bg=Colors.STATE_ERROR,
                hover_bg="#FF8CA8",
                active_bg="#FF769E",
                fg=Colors.SURFACE,
            ),
            "Locomm.Success.TButton": dict(
                bg=Colors.STATE_SUCCESS,
                hover_bg="#3FD6C0",
                active_bg="#2EC2AD",
                fg=Colors.SURFACE,
            ),
        }
        for style_name, cfg in button_configs.items():
            ThemeManager._register_button(style, style_name, **cfg)
        ThemeManager._configure_nav_buttons(style)
        ThemeManager._configure_entry_styles(style)

    @staticmethod
    def _register_button(style, style_name, *, bg, hover_bg, active_bg, fg):
        ThemeManager._apply_button_layout(style, style_name)
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
                ("active", active_bg),
                ("pressed", active_bg),
                ("disabled", Colors.SURFACE_ALT),
            ],
            foreground=[("disabled", Colors.TEXT_MUTED)],
            relief=[("pressed", "flat"), ("!pressed", "flat")],
        )

    @staticmethod
    def _apply_button_layout(style, style_name):
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
                                "children": [
                                    ("Button.label", {"sticky": "nswe"}),
                                ],
                            },
                        )
                    ],
                },
            )
        ]
        style.layout(style_name, layout)

    @staticmethod
    def _configure_nav_buttons(style):
        style.configure(
            "Locomm.Nav.TButton",
            background=Colors.SURFACE,
            foreground=Colors.TEXT_SECONDARY,
            relief="flat",
            anchor="w",
            padding=(Spacing.MD, Spacing.SM),
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
            borderwidth=0,
            highlightthickness=0,
        )
        style.map(
            "Locomm.Nav.TButton",
            background=[("active", Colors.SURFACE_SELECTED), ("pressed", Colors.SURFACE_SELECTED)],
            foreground=[("active", Colors.TEXT_PRIMARY)],
        )
        style.configure(
            "Locomm.NavActive.TButton",
            background=Colors.SURFACE_SELECTED,
            foreground=Colors.TEXT_PRIMARY,
            relief="flat",
            anchor="w",
            padding=(Spacing.MD, Spacing.SM),
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
            borderwidth=0,
        )

    @staticmethod
    def _configure_entry_styles(style):
        style.configure(
            "Locomm.Input.TEntry",
            fieldbackground=Colors.SURFACE_RAISED,
            foreground=Colors.TEXT_PRIMARY,
            insertcolor=Colors.TEXT_PRIMARY,
            padding=(Spacing.SM, int(Spacing.XS / 1.5)),
            bordercolor=Colors.BORDER,
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Locomm.PinEntry.TEntry",
            fieldbackground=Colors.SURFACE_ALT,
            foreground=Colors.TEXT_PRIMARY,
            insertcolor=Colors.TEXT_PRIMARY,
            padding=(Spacing.XXS, Spacing.XXS),
            bordercolor=Colors.SURFACE_SELECTED,
            borderwidth=1,
            relief="solid",
        )

    @classmethod
    def toggle_mode(cls, dark: bool):
        mode = "dark" if dark else "light"
        if mode == cls._current_mode:
            return
        cls._current_mode = mode
        _apply_theme_definition(_THEME_DEFINITIONS[mode])
        cls._initialized = False
        cls.ensure()

    @classmethod
    def current_mode(cls):
        return cls._current_mode


def _apply_theme_definition(theme: Dict[str, str]):
    for key, value in theme.items():
        setattr(Colors, key, value)
    Colors.STATUS_CONNECTED = Colors.STATE_SUCCESS
    Colors.STATUS_DISCONNECTED = Colors.STATE_ERROR
    Colors.STATUS_CONNECTING = Colors.STATE_INFO
    Colors.STATUS_PAIRING = Colors.STATE_INFO
    Colors.STATUS_READY = Colors.STATE_READY
    Colors.STATUS_TRANSPORT_ERROR = Colors.STATE_TRANSPORT_ERROR


def ensure_styles_initialized():
    ThemeManager.ensure()
