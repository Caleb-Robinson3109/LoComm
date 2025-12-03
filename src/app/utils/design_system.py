"""Backwards compatible façade that exposes the new UI package primitives."""
from __future__ import annotations

from ui.theme_tokens import (
    AppConfig,
    Colors,
    Palette,
    Space,
    Spacing,
    Typography,
)
from ui.theme_manager import ThemeManager, ensure_styles_initialized
# DesignUtils imported lazily to avoid circular imports
from ui.custom_themes import CustomTheme, CustomThemeManager
# get_custom_theme_manager imported lazily to avoid circular imports
from ui.context_themes import (
    ThemeContext, 
    ContextThemeResolver, 
    ThemedButton, 
    ThemedFrame,
    register_default_context_themes
)

__all__ = [
    "AppConfig",
    "Colors",
    "Palette",
    "Space",
    "Spacing",
    "Typography",
    "ThemeManager",
    "ensure_styles_initialized",
    "DesignUtils",
    # Custom themes
    "CustomTheme",
    "CustomThemeManager",
    # get_custom_theme_manager added lazily to avoid circular imports
    "get_design_utils",
    # Context-aware theming
    "ThemeContext",
    "ContextThemeResolver",
    "ThemedButton",
    "ThemedFrame",
    "register_default_context_themes",
    # Accessibility
    "AccessibilityValidator",
    # Theme validation and utilities
    "validate_contrast_ratio",
    "check_wcag_compliance",
    "simulate_colorblindness",
    "get_accessibility_summary",
]

STATUS_CONNECTED_KEYWORDS = AppConfig.STATUS_CONNECTED_KEYWORDS
STATUS_DISCONNECTED_KEYWORDS = AppConfig.STATUS_DISCONNECTED_KEYWORDS
STATUS_ERROR_KEYWORDS = AppConfig.STATUS_ERROR_KEYWORDS
STATUS_READY_KEYWORDS = AppConfig.STATUS_READY_KEYWORDS
STATUS_TRANSPORT_ERROR_KEYWORDS = AppConfig.STATUS_TRANSPORT_ERROR_KEYWORDS
STATUS_DISCONNECTED = AppConfig.STATUS_DISCONNECTED
STATUS_CONNECTED = AppConfig.STATUS_CONNECTED
STATUS_CONNECTION_FAILED = AppConfig.STATUS_CONNECTION_FAILED
STATUS_INVALID_PIN = AppConfig.STATUS_INVALID_PIN
STATUS_CONNECTION_DEVICE_FAILED = AppConfig.STATUS_CONNECTION_DEVICE_FAILED
STATUS_AWAITING_PEER = AppConfig.STATUS_AWAITING_PEER
STATUS_NOT_CONNECTED = AppConfig.STATUS_NOT_CONNECTED
STATUS_READY = AppConfig.STATUS_READY

# Accessibility and theme validation functions
def validate_contrast_ratio(foreground: str, background: str) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    return ThemeManager.validate_contrast_ratio(foreground, background)

def check_wcag_compliance(foreground: str, background: str, level: str = "AA") -> dict:
    """Check WCAG compliance for color contrast."""
    return ThemeManager.check_wcag_compliance(foreground, background, level)

def simulate_colorblindness(color: str, type_: str = "deuteranopia") -> str:
    """Simulate how a color appears to people with different types of colorblindness."""
    return ThemeManager.simulate_colorblindness(color, type_)

def get_custom_theme_manager():
    """Get the global custom theme manager instance (lazy import to avoid circular imports)."""
    from ui.custom_themes import get_custom_theme_manager as _get_manager
    return _get_manager()

def get_design_utils():
    """Get DesignUtils (lazy import to avoid circular imports)."""
    from ui.components import DesignUtils
    return DesignUtils

def get_accessibility_summary() -> dict:
    """Get a comprehensive accessibility summary for the current theme."""
    return ThemeManager.get_accessibility_summary()

# Alias for backwards compatibility
AccessibilityValidator = ThemeManager

STATUS_TRANSPORT_ERROR = AppConfig.STATUS_TRANSPORT_ERROR

# Alias for backwards compatibility
AccessibilityValidator = ThemeManager

STATUS_TRANSPORT_ERROR = AppConfig.STATUS_TRANSPORT_ERROR

# DesignUtils compatibility alias (lazy loading to avoid circular imports)
class _DesignUtilsProxy:
    """Proxy class for DesignUtils to avoid circular imports."""
    def __getattr__(self, name):
        return getattr(get_design_utils(), name)

DesignUtils = _DesignUtilsProxy()