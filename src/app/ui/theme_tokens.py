"""
Theme primitives for Locomm UI (palette, tokens, shared constants).
"""
from __future__ import annotations

from dataclasses import dataclass


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

    SIGNAL_BLUE = "#5E8BFF"
    SIGNAL_BLUE_DARK = "#2F5FD8"
    SIGNAL_BLUE_LIGHT = "#A8C6FF"
    SIGNAL_TEAL = "#3AD0B1"
    SIGNAL_RED = "#FF5C8D"
    SIGNAL_WARNING = "#FFAF40"
    SIGNAL_ORANGE = "#FF7F2D"
    SIGNAL_PURPLE = "#B36DFF"


class Colors:
    """Runtime theme values populated via ThemeManager."""

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
    STATE_READY = ""
    STATE_TRANSPORT_ERROR = ""
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

    STATUS_CONNECTED = ""
    STATUS_DISCONNECTED = ""
    STATUS_CONNECTING = ""
    STATUS_PAIRING = ""
    STATUS_READY = ""
    STATUS_TRANSPORT_ERROR = ""


class Typography:
    """Typography scale (8pt grid)."""

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


class AppConfig:
    DEBUG = False
    STATUS_CONNECTED_KEYWORDS = {"connected"}
    STATUS_DISCONNECTED_KEYWORDS = {"disconnected", "connection failed"}
    STATUS_ERROR_KEYWORDS = {"failed", "error", "invalid"}
    STATUS_READY_KEYWORDS = {"ready", "ready to pair", "idle", "standby"}
    STATUS_TRANSPORT_ERROR_KEYWORDS = {
        "transport error",
        "connection error",
        "send error",
        "receive error",
        "transport failure",
    }

    STATUS_DISCONNECTED = "Disconnected"
    STATUS_CONNECTED = "Connected"
    STATUS_CONNECTION_FAILED = "Connection failed"
    STATUS_INVALID_PIN = "Invalid pairing code"
    STATUS_CONNECTION_DEVICE_FAILED = "Connection failed (device not found)"
    STATUS_AWAITING_PEER = "Awaiting peer"
    STATUS_NOT_CONNECTED = "Not connected"
    STATUS_READY = "Ready"
    STATUS_TRANSPORT_ERROR = "Transport error"

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
