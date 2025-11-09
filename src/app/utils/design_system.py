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
from ui.components import DesignUtils

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
STATUS_TRANSPORT_ERROR = AppConfig.STATUS_TRANSPORT_ERROR
