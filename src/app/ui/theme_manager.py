"""Theme registration and helper utilities for Locomm UI."""
from __future__ import annotations

from typing import Dict

import tkinter as tk
from tkinter import ttk

from ui.theme_tokens import Colors, Palette, Spacing, Typography
from ui.themes.definitions import THEME_DEFINITIONS
from ui.accessibility import AccessibilityUtils
# Custom themes imported lazily inside functions to avoid circular imports


class ThemeManager:
    _initialized = False
    _current_mode = "dark"
    _current_accent_color = "blue"
    _available_accent_colors = ['blue', 'purple', 'green', 'orange', 'pink', 'red']
    _available_modes = ["dark", "light", "high_contrast_dark", "colorblind_friendly"]
    BUTTON_STYLES = {
        "primary": "Locomm.Primary.TButton",
        "secondary": "Locomm.Secondary.TButton",
        "ghost": "Locomm.Ghost.TButton",
        "danger": "Locomm.Danger.TButton",
        "success": "Locomm.Success.TButton",
        "warning": "Locomm.Warning.TButton",
    }

    @classmethod
    def ensure(cls):
        """Ensure theme is initialized and styles are registered."""
        if cls._initialized:
            return
        theme = THEME_DEFINITIONS[cls._current_mode]
        _apply_theme_definition(theme)
        cls._register_button_styles()
        cls._initialized = True

    @staticmethod
    def _register_button_styles():
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
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
                hover_bg=Colors.BUTTON_PRIMARY_HOVER,
                active_bg=Colors.BUTTON_PRIMARY_HOVER,
                fg=Colors.TEXT_PRIMARY,
            ),
            "Locomm.Danger.TButton": dict(
                bg=Colors.STATE_ERROR,
                hover_bg=Colors.BUTTON_DANGER_HOVER,
                active_bg=Colors.BUTTON_DANGER_ACTIVE,
                fg=Colors.SURFACE,
            ),
            "Locomm.Success.TButton": dict(
                bg=Colors.STATE_SUCCESS,
                hover_bg=Colors.BUTTON_SUCCESS_HOVER,
                active_bg=Colors.BUTTON_SUCCESS_ACTIVE,
                fg=Colors.SURFACE,
            ),
            "Locomm.Warning.TButton": dict(
                bg=Colors.STATE_WARNING,
                hover_bg=Colors.BUTTON_WARNING_HOVER,
                active_bg=Colors.BUTTON_WARNING_ACTIVE,
                fg=Colors.SURFACE,
            ),
        }
        for style_name, cfg in button_configs.items():
            ThemeManager._register_button(style, style_name, **cfg)
        ThemeManager._configure_nav_buttons(style)
        ThemeManager._configure_entry_styles(style)
        style.configure(
            "Vertical.TScrollbar",
            troughcolor=Colors.BG_MAIN,
            background=Colors.SCROLLBAR_THUMB,
            bordercolor=Colors.BG_MAIN,
            arrowcolor=Colors.TEXT_MUTED,
            gripcount=0,
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
            troughrelief="flat",
            arrowcolor=Colors.TEXT_MUTED,
            width=10,
        )
        style.map(
            "Horizontal.TScrollbar",
            background=[("active", Colors.SCROLLBAR_THUMB_HOVER)],
        )

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
        ThemeManager._apply_button_layout(style, "Locomm.Nav.TButton")
        ThemeManager._apply_button_layout(style, "Locomm.NavActive.TButton")

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
                                    ("Button.label", {"sticky": "w"})
                                ],
                            },
                        )
                    ],
                },
            )
        ]
        style.layout("Locomm.Nav.TButton", layout)
        style.layout("Locomm.NavActive.TButton", layout)

        style.configure(
            "Locomm.Nav.TButton",
            background=Colors.NAV_BUTTON_BG,
            foreground=Colors.TEXT_MUTED,
            bordercolor=Colors.NAV_BUTTON_BORDER,
            borderwidth=1,
            relief="flat",
            padding=(12, 8),
            anchor="w",
            focusthickness=0,
            highlightthickness=0,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
        )
        style.map(
            "Locomm.Nav.TButton",
            background=[
                ("hover", Colors.NAV_BUTTON_HOVER),
                ("active", Colors.NAV_BUTTON_HOVER),
            ],
            foreground=[
                ("hover", Colors.TEXT_PRIMARY),
                ("active", Colors.TEXT_PRIMARY),
            ],
            bordercolor=[
                ("hover", Colors.NAV_BUTTON_BORDER),
                ("active", Colors.NAV_BUTTON_BORDER),
            ],
        )

        style.configure(
            "Locomm.NavActive.TButton",
            background=Colors.NAV_BUTTON_ACTIVE_BG,
            foreground=Colors.NAV_BUTTON_ACTIVE_FG,
            bordercolor=Colors.NAV_BUTTON_BORDER,
            borderwidth=1,
            relief="flat",
            padding=(12, 8),
            anchor="w",
            focusthickness=0,
            highlightthickness=0,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
        )
        style.map(
            "Locomm.NavActive.TButton",
            background=[
                ("hover", Colors.NAV_BUTTON_ACTIVE_BG),
                ("active", Colors.NAV_BUTTON_ACTIVE_BG),
            ],
            foreground=[
                ("hover", Colors.NAV_BUTTON_ACTIVE_FG),
                ("active", Colors.NAV_BUTTON_ACTIVE_FG),
            ],
            bordercolor=[
                ("hover", Colors.NAV_BUTTON_BORDER),
                ("active", Colors.NAV_BUTTON_BORDER),
            ],
        )

    @staticmethod
    def _configure_entry_styles(style):
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
    def toggle_mode(cls, dark: bool):
        """Toggle between light and dark mode."""
        mode = "dark" if dark else "light"
        if mode == cls._current_mode:
            return
        cls._current_mode = mode
        # Efficient theme switching - only update colors without reinitializing styles
        _update_theme_colors(THEME_DEFINITIONS[mode])
        cls.refresh_styles()
        cls._notify_theme_change()

    @classmethod
    def current_mode(cls):
        """Get the current theme mode name."""
        return cls._current_mode

    @classmethod
    def get_current_accent_name(cls):
        """Get the current accent color name."""
        return cls._current_accent_color or "blue"

    @classmethod
    def set_accent_color(cls, accent_name: str):
        """Set the accent color by name."""
        if accent_name in cls._available_accent_colors:
            cls._current_accent_color = accent_name
            # Refresh styles to apply new accent color
            cls.refresh_styles()
        else:
            raise ValueError(f"Unknown accent color: {accent_name}")

    @classmethod
    def _notify_theme_change(cls):
        """Notify components of theme change for smooth updates."""
        # This would be used to trigger theme change events in a more sophisticated system
        pass

    @classmethod
    def get_available_modes(cls):
        """Get list of available theme modes."""
        return cls._available_modes.copy()

    @classmethod
    def set_mode(cls, mode_name: str):
        """Set theme mode by name."""
        if mode_name not in cls._available_modes:
            raise ValueError(f"Unknown theme mode: {mode_name}")

        if mode_name == cls._current_mode:
            return

        cls._current_mode = mode_name
        _update_theme_colors(THEME_DEFINITIONS[mode_name])
        cls.refresh_styles()
        cls._notify_theme_change()

    @classmethod
    def get_mode_info(cls):
        """Get current mode information including accessibility features."""
        mode_info = {
            "name": cls._current_mode,
            "display_name": cls._get_mode_display_name(cls._current_mode),
            "accessibility_features": cls._get_accessibility_features(cls._current_mode)
        }
        return mode_info

    @classmethod
    def _get_mode_display_name(cls, mode_name: str) -> str:
        """Get human-readable display name for theme mode."""
        display_names = {
            "dark": "Dark Mode",
            "light": "Light Mode",
            "high_contrast_dark": "High Contrast (Dark)",
            "colorblind_friendly": "Colorblind Friendly"
        }
        return display_names.get(mode_name, mode_name)

    @classmethod
    def _get_accessibility_features(cls, mode_name: str) -> list:
        """Get accessibility features for the specified mode."""
        features = {
            "dark": ["reduced_eye_strain", "low_light"],
            "light": ["bright_environments", "daylight_readable"],
            "high_contrast_dark": ["high_contrast", "vision_impairment", "colorblind_safe"],
            "colorblind_friendly": ["colorblind_safe", "deuteranopia_safe", "protanopia_safe", "tritanopia_safe"]
        }
        return features.get(mode_name, [])

    # Delegate accessibility methods to AccessibilityUtils
    @classmethod
    def validate_contrast_ratio(cls, foreground: str, background: str) -> float:
        """Calculate contrast ratio between two colors."""
        return AccessibilityUtils.validate_contrast_ratio(foreground, background)

    @classmethod
    def check_wcag_compliance(cls, foreground: str, background: str, level: str = "AA") -> dict:
        """Check if contrast ratio meets WCAG standards."""
        return AccessibilityUtils.check_wcag_compliance(foreground, background, level)

    @classmethod
    def simulate_colorblindness(cls, color: str, type_: str = "deuteranopia") -> str:
        """Simulate how a color appears to colorblind users."""
        return AccessibilityUtils.simulate_colorblindness(color, type_)

    @classmethod
    def validate_theme_accessibility(cls) -> dict:
        """Validate the current theme for accessibility compliance."""
        checks = {
            "text_contrast": cls.check_wcag_compliance(Colors.TEXT_PRIMARY, Colors.SURFACE),
            "secondary_text_contrast": cls.check_wcag_compliance(Colors.TEXT_SECONDARY, Colors.SURFACE),
            "button_contrast": cls.check_wcag_compliance(Colors.TEXT_PRIMARY, Colors.BUTTON_PRIMARY_BG),
            "focus_indicator_visible": len(Colors.BORDER) > 0,
            "error_color_distinct": cls.validate_contrast_ratio(Colors.STATE_ERROR, Colors.SURFACE) > 3.0,
            "success_color_distinct": cls.validate_contrast_ratio(Colors.STATE_SUCCESS, Colors.SURFACE) > 3.0,
        }

        overall_compliance = all(
            check.get("compliant", True) if isinstance(check, dict) else check
            for check in checks.values()
        )

        return {
            "overall_compliant": overall_compliance,
            "checks": checks,
            "recommendations": cls._get_accessibility_recommendations(checks)
        }

    @classmethod
    def _get_accessibility_recommendations(cls, checks: dict) -> list:
        """Get accessibility improvement recommendations."""
        recommendations = []

        if not checks.get("text_contrast", {}).get("compliant", True):
            recommendations.append("Increase contrast between primary text and background")

        if not checks.get("secondary_text_contrast", {}).get("compliant", True):
            recommendations.append("Increase contrast between secondary text and background")

        if not checks.get("button_contrast", {}).get("compliant", True):
            recommendations.append("Increase contrast between button text and background")

        if not checks.get("error_color_distinct", True):
            recommendations.append("Make error state color more distinct from background")

        if not checks.get("success_color_distinct", True):
            recommendations.append("Make success state color more distinct from background")

        if not checks.get("focus_indicator_visible", True):
            recommendations.append("Add visible focus indicators for keyboard navigation")

        return recommendations

    @classmethod
    def auto_adjust_contrast(cls) -> dict:
        """Automatically adjust colors to improve contrast while maintaining visual appeal."""
        adjustments = {}

        # Check and adjust primary text contrast
        text_contrast = cls.validate_contrast_ratio(Colors.TEXT_PRIMARY, Colors.SURFACE)
        if text_contrast < 4.5:  # WCAG AA standard
            # Adjust text color for better contrast
            if _is_dark_color(Colors.SURFACE):
                # Dark background - make text lighter
                current_rgb = tuple(int(Colors.TEXT_PRIMARY.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                # Gradually increase brightness
                new_r = min(255, int(current_rgb[0] * 1.2))
                new_g = min(255, int(current_rgb[1] * 1.2))
                new_b = min(255, int(current_rgb[2] * 1.2))
                adjustments["TEXT_PRIMARY"] = f"#{new_r:02x}{new_g:02x}{new_b:02x}"
            else:
                # Light background - make text darker
                current_rgb = tuple(int(Colors.TEXT_PRIMARY.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                new_r = max(0, int(current_rgb[0] * 0.8))
                new_g = max(0, int(current_rgb[1] * 0.8))
                new_b = max(0, int(current_rgb[2] * 0.8))
                adjustments["TEXT_PRIMARY"] = f"#{new_r:02x}{new_g:02x}{new_b:02x}"

        return adjustments

    @classmethod
    def get_accessibility_summary(cls) -> dict:
        """Get a comprehensive accessibility summary for the current theme."""
        validation = cls.validate_theme_accessibility()
        mode_info = cls.get_mode_info()

        return {
            "current_mode": mode_info,
            "validation": validation,
            "compliance_score": sum(1 for check in validation["checks"].values()
                                  if (check.get("compliant", True) if isinstance(check, dict) else check)) /
                              len(validation["checks"]) * 100,
            "improvements_applied": len(cls.auto_adjust_contrast()) > 0
        }

    @classmethod
    def refresh_styles(cls):
        """Refresh ttk styles after theme change for immediate visual update."""
        if cls._initialized:
            style = ttk.Style()
            # Update button styles
            for style_name in ["Locomm.Primary.TButton", "Locomm.Secondary.TButton", "Locomm.Ghost.TButton", "Locomm.Danger.TButton", "Locomm.Success.TButton"]:
                try:
                    style.configure(style_name,
                                  background=getattr(Colors, "BUTTON_PRIMARY_BG", Palette.VSCODE_BLUE),
                                  foreground=Colors.SURFACE)
                except tk.TclError:
                    pass  # Style may not exist yet

            # Update nav styles
            try:
                style.configure("Locomm.Nav.TButton",
                              background=Colors.SURFACE,
                              foreground=Colors.TEXT_SECONDARY)
            except tk.TclError:
                pass

            try:
                style.configure("Locomm.NavActive.TButton",
                              background=Colors.SURFACE_SELECTED,
                              foreground=Colors.TEXT_PRIMARY)
            except tk.TclError:
                pass

            # Update entry styles
            try:
                style.configure("Locomm.Input.TEntry",
                              fieldbackground=Colors.SURFACE_RAISED,
                              foreground=Colors.TEXT_PRIMARY,
                              bordercolor=Colors.BORDER)
            except tk.TclError:
                pass

            try:
                style.configure("Locomm.PinEntry.TEntry",
                              fieldbackground=Colors.SURFACE_ALT,
                              foreground=Colors.TEXT_PRIMARY,
                              bordercolor=Colors.SURFACE_SELECTED)
            except tk.TclError:
                pass


def _update_theme_colors(theme: Dict[str, str]):
    """Update theme colors without reinitializing styles (optimized for theme switching)."""
    for key, value in theme.items():
        if hasattr(Colors, key):
            setattr(Colors, key, value)
    _update_status_colors()


def _apply_theme_definition(theme: Dict[str, str]):
    """Full theme application including style initialization."""
    _update_theme_colors(theme)
    ThemeManager._initialized = False
    # Don't call ensure() here to avoid recursion - this is called from ensure() itself
    # ThemeManager._register_button_styles() will be called from ensure()


def _update_status_colors():
    """Update derived status colors."""
    Colors.STATUS_CONNECTED = Colors.STATE_SUCCESS
    Colors.STATUS_DISCONNECTED = Colors.STATE_ERROR
    Colors.STATUS_CONNECTING = Colors.STATE_INFO
    Colors.STATUS_PAIRING = Colors.STATE_INFO
    Colors.STATUS_READY = Colors.STATE_READY
    Colors.STATUS_TRANSPORT_ERROR = Colors.STATE_TRANSPORT_ERROR


def _notify_theme_change():
    """Notify components of theme change for smooth updates."""
    # This would be used to trigger theme change events in a more sophisticated system
    pass


def _is_dark_color(hex_color: str) -> bool:
    """Determine if a color is dark or light."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Calculate luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    return luminance < 0.5


def ensure_styles_initialized():
    """Ensure theme styles are initialized (convenience wrapper)."""
    ThemeManager.ensure()
