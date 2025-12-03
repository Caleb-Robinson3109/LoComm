"""Utility UI package grouping theme helpers and reusable widgets."""
from __future__ import annotations

from .theme_tokens import Colors, Palette, Spacing, Space, Typography, AppConfig
from .theme_manager import ThemeManager, ensure_styles_initialized
from .components import DesignUtils
from .helpers import create_scroll_container, create_page_scaffold, enable_global_mousewheel, ScrollContainer, PageScaffold

__all__ = [
    "Colors",
    "Palette",
    "Space",
    "Spacing",
    "Typography",
    "AppConfig",
    "ThemeManager",
    "ensure_styles_initialized",
    "DesignUtils",
    "create_scroll_container",
    "create_page_scaffold",
    "enable_global_mousewheel",
    "ScrollContainer",
    "PageScaffold",
]
