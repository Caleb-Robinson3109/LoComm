"""Theme registration and helper utilities for Locomm UI."""
from __future__ import annotations

from typing import Dict

import tkinter as tk
from tkinter import ttk

from ui.theme_tokens import Colors, Palette, Spacing, Typography
# Custom themes imported lazily inside functions to avoid circular imports


_THEME_DEFINITIONS = {
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
        "NAV_BUTTON_ACTIVE": "#0B7CFF",
        "SCROLLBAR_TRACK": "#1E1E1E",
        "SCROLLBAR_THUMB": "#3C3C3C",
        "SCROLLBAR_THUMB_HOVER": "#4B4B4B",
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
        "STATE_INFO": "#2389FF",
        "STATE_READY": "#2389FF",
        "STATE_TRANSPORT_ERROR": "#6E3FEF",
        "BUTTON_PRIMARY_BG": Palette.PRIMARY,
        "BUTTON_PRIMARY_HOVER": Palette.PRIMARY_HOVER,
        "BUTTON_SECONDARY_BG": "#F3F4F6",
        "BUTTON_GHOST_BG": Palette.WHITE,
        "BUTTON_DANGER_HOVER": "#B23535",
        "BUTTON_DANGER_ACTIVE": "#B23535",
        "BUTTON_SUCCESS_HOVER": "#3FD6C0",
        "BUTTON_SUCCESS_ACTIVE": "#2EC2AD",
        "BUTTON_WARNING_HOVER": "#FFA724",
        "BUTTON_WARNING_ACTIVE": "#F28D1A",
        "ACCENT_PRIMARY": Palette.PRIMARY,
        "ACCENT_PRIMARY_HOVER": Palette.PRIMARY_HOVER,
        "ACCENT_SECONDARY": "#B19CD9",
        "BG_CHAT_AREA": Palette.CLOUD_050,
        "BG_MESSAGE_OWN": Palette.PRIMARY,
        "BG_MESSAGE_OTHER": Palette.CLOUD_100,
        "BG_MESSAGE_SYSTEM": Palette.CLOUD_050,
        "BG_INPUT_AREA": Palette.CLOUD_100,
        "TEXT_PLACEHOLDER": "#9CA3AF",
        "TEXT_TIMESTAMP": "#9CA3AF",
        "MESSAGE_SYSTEM_TEXT": "#9CA3AF",
        "MESSAGE_BUBBLE_OWN_BG": Palette.PRIMARY,
        "MESSAGE_BUBBLE_OTHER_BG": Palette.CLOUD_100,
        "MESSAGE_BUBBLE_SYSTEM_BG": Palette.CLOUD_050,
        "CHAT_SHELL_BG": Palette.CLOUD_050,
        "CHAT_HISTORY_BG": Palette.CLOUD_050,
        "CHAT_COMPOSER_BG": Palette.CLOUD_100,
        "CHAT_HEADER_BG": Palette.CLOUD_100,
        "CHAT_HEADER_TEXT": Palette.SLATE_900,
        "CHAT_BADGE_BG": Palette.CLOUD_200,
        "CHAT_TEXTURE": Palette.CLOUD_100,
        "CHAT_BUBBLE_SELF_BG": Palette.PRIMARY,
        "CHAT_BUBBLE_OTHER_BG": Palette.CLOUD_100,
        "CHAT_BUBBLE_SYSTEM_BG": Palette.CLOUD_050,
        "CHAT_BUBBLE_SELF_TEXT": Palette.WHITE,
        "CHAT_BUBBLE_OTHER_TEXT": Palette.SLATE_900,
        "CHAT_BUBBLE_SYSTEM_TEXT": Palette.SLATE_700,
        "NAV_BUTTON_BG": Palette.CLOUD_050,
        "NAV_BUTTON_HOVER": Palette.CLOUD_100,
        "NAV_BUTTON_ACTIVE": Palette.PRIMARY,
        "SCROLLBAR_TRACK": Palette.WHITE,
        "SCROLLBAR_THUMB": "#D1D5DB",
        "SCROLLBAR_THUMB_HOVER": "#4B4B4B",
    },
}
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
        if cls._initialized:
            return
        theme = _THEME_DEFINITIONS[cls._current_mode]
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
        def _configure(name: str, font_weight: str):
            style.configure(
                name,
                background=Colors.NAV_BUTTON_BG,
                foreground=Colors.TEXT_MUTED,
                relief="flat",
                anchor="center",
                padding=(Spacing.MD, Spacing.SM),
                font=(Typography.FONT_UI, Typography.SIZE_14, font_weight),
                borderwidth=0,
                highlightthickness=0,
                focusthickness=1,
                focuscolor=Colors.NAV_BUTTON_ACTIVE,
            )
            style.map(
                name,
                background=[
                    ("active", Colors.NAV_BUTTON_ACTIVE),
                    ("pressed", Colors.NAV_BUTTON_HOVER),
                ],
                foreground=[
                    ("active", Colors.TEXT_PRIMARY),
                ],
            )

        _configure("Locomm.Nav.TButton", Typography.WEIGHT_MEDIUM)
        _configure("Locomm.NavActive.TButton", Typography.WEIGHT_BOLD)

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
        mode = "dark" if dark else "light"
        if mode == cls._current_mode:
            return
        cls._current_mode = mode
        # Efficient theme switching - only update colors without reinitializing styles
        _update_theme_colors(_THEME_DEFINITIONS[mode])
        cls.refresh_styles()
        cls._notify_theme_change()

    @classmethod
    def current_mode(cls):
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
        # For now, we'll use the optimized approach to refresh mock windows and other components
        try:
            from mock.peer_chat_window import refresh_mock_peer_window_theme
            refresh_mock_peer_window_theme()
        except ImportError:
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
        _update_theme_colors(_THEME_DEFINITIONS[mode_name])
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
    
    @classmethod
    def validate_contrast_ratio(cls, foreground: str, background: str) -> float:
        """Calculate WCAG contrast ratio between two colors."""
        def get_luminance(color: str) -> float:
            # Handle empty or invalid colors
            if not color or not isinstance(color, str):
                return 0.5  # Return mid-gray luminance for invalid colors
            
            # Remove # if present
            color = color.lstrip('#')
            
            # Ensure we have exactly 6 characters
            if len(color) != 6:
                return 0.5  # Return mid-gray for invalid format
            
            try:
                # Convert to RGB
                r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            except ValueError:
                return 0.5  # Return mid-gray for invalid hex values
            
            # Calculate relative luminance
            def linearize(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else pow((c + 0.055) / 1.055, 2.4)
            
            r_lin = linearize(r)
            g_lin = linearize(g)
            b_lin = linearize(b)
            
            return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
        
        l1 = get_luminance(foreground)
        l2 = get_luminance(background)
        
        # Ensure l1 is the lighter color
        if l1 < l2:
            l1, l2 = l2, l1
        
        # Calculate contrast ratio
        return (l1 + 0.05) / (l2 + 0.05)
    
    @classmethod
    def check_wcag_compliance(cls, foreground: str, background: str, level: str = "AA") -> dict:
        """Check WCAG compliance for color contrast."""
        ratio = cls.validate_contrast_ratio(foreground, background)
        
        # WCAG thresholds
        thresholds = {
            "AA": {"normal": 4.5, "large": 3.0},
            "AAA": {"normal": 7.0, "large": 4.5}
        }
        
        if level not in thresholds:
            level = "AA"
        
        thresholds = thresholds[level]
        
        return {
            "ratio": round(ratio, 2),
            "aa_normal": ratio >= thresholds["normal"],
            "aa_large": ratio >= thresholds["large"],
            "aaa_normal": ratio >= thresholds.get("normal", 4.5) * 7.0/4.5,
            "aaa_large": ratio >= thresholds.get("large", 3.0) * 4.5/3.0,
            "compliant": ratio >= thresholds["normal"]
        }
    
    @classmethod
    def simulate_colorblindness(cls, color: str, type_: str = "deuteranopia") -> str:
        """Simulate how a color appears to people with different types of colorblindness."""
        # Remove # if present
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # Color blindness simulation matrices (simplified)
        matrices = {
            "protanopia": [
                [0.567, 0.433, 0.000],
                [0.558, 0.442, 0.000],
                [0.000, 0.242, 0.758]
            ],
            "deuteranopia": [
                [0.625, 0.375, 0.000],
                [0.700, 0.300, 0.000],
                [0.000, 0.300, 0.700]
            ],
            "tritanopia": [
                [0.950, 0.050, 0.000],
                [0.000, 0.433, 0.567],
                [0.000, 0.475, 0.525]
            ]
        }
        
        if type_ not in matrices:
            type_ = "deuteranopia"
        
        matrix = matrices[type_]
        
        # Apply transformation
        new_r = int(r * matrix[0][0] + g * matrix[0][1] + b * matrix[0][2])
        new_g = int(r * matrix[1][0] + g * matrix[1][1] + b * matrix[1][2])
        new_b = int(r * matrix[2][0] + g * matrix[2][1] + b * matrix[2][2])
        
        # Ensure values are in range
        new_r = max(0, min(255, new_r))
        new_g = max(0, min(255, new_g))
        new_b = max(0, min(255, new_b))
        
        return f"#{new_r:02x}{new_g:02x}{new_b:02x}"
    
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
    # For now, we'll use the optimized approach to refresh mock windows and other components
    try:
        from mock.peer_chat_window import refresh_mock_peer_window_theme
        refresh_mock_peer_window_theme()
    except ImportError:
        pass


def _is_dark_color(hex_color: str) -> bool:
    """Determine if a color is dark or light."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Calculate luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    return luminance < 0.5


def ensure_styles_initialized():
    ThemeManager.ensure()
