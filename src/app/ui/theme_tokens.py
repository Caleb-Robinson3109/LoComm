"""
Theme primitives for Locomm UI (VS Code-inspired palette, tokens, shared constants).
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

    SIGNAL_BLUE = "#0B7CFF"
    SIGNAL_BLUE_DARK = "#075AC6"
    SIGNAL_BLUE_LIGHT = "#3AA0FF"
    SIGNAL_TEAL = "#00C7B1"
    SIGNAL_RED = "#FF5A5F"
    PIN_ENTRY_BG = "#228B22"
    PIN_ENTRY_BORDER = "#FFD700"

    # Legacy tokens removed for simplification
    WHITE = "#FFFFFF"

    # Modern UI Colors
    NEUTRAL_50 = "#F9FAFB"
    NEUTRAL_100 = "#F3F4F6"
    NEUTRAL_200 = "#E5E7EB"
    NEUTRAL_300 = "#D1D5DB"
    NEUTRAL_400 = "#9CA3AF"
    NEUTRAL_500 = "#6B7280"
    NEUTRAL_600 = "#4B5563"
    NEUTRAL_700 = "#374151"
    NEUTRAL_800 = "#1F2937"
    NEUTRAL_900 = "#111827"

    PRIMARY_50 = "#EFF6FF"
    PRIMARY_100 = "#DBEAFE"
    PRIMARY_500 = "#3B82F6"
    PRIMARY_600 = "#2563EB"
    PRIMARY_700 = "#1D4ED8"

    # Custom primary/danger variants
    PRIMARY = "#2563EB"  # Modern Blue
    PRIMARY_HOVER = "#1D4ED8"
    PRIMARY_SOFT = "#EFF6FF"
    DANGER = "#EF4444"
    DANGER_HOVER = "#DC2626"
    DANGER_SOFT = "#FEF2F2"


class Colors:
    """Runtime theme values populated via ThemeManager."""

    BG_MAIN = ""
    BG_ELEVATED = ""
    BG_ELEVATED_2 = ""
    BG_STRIP = ""
    BG_SOFT = ""

    SURFACE = ""
    SURFACE_ALT = ""
    SURFACE_RAISED = ""
    SURFACE_HEADER = ""
    SURFACE_SIDEBAR = ""
    SURFACE_SELECTED = ""
    BORDER = ""
    DIVIDER = ""
    HERO_PANEL_BG = ""
    HERO_PANEL_TEXT = ""
    CARD_PANEL_BG = ""
    CARD_PANEL_BORDER = ""
    PANEL_BG = ""
    PANEL_BORDER = ""
    MAIN_FRAME_BG = ""
    BACKDROP_BG = ""
    CHAT_SHELL_BG = ""
    CHAT_HISTORY_BG = ""
    CHAT_COMPOSER_BG = ""
    CHAT_HEADER_BG = ""
    CHAT_HEADER_TEXT = ""
    CHAT_TEXTURE = ""
    CHAT_BADGE_BG = ""
    CHAT_BUBBLE_SELF_BG = ""
    CHAT_BUBBLE_OTHER_BG = ""
    CHAT_BUBBLE_SYSTEM_BG = ""
    CHAT_BUBBLE_SELF_TEXT = ""
    CHAT_BUBBLE_OTHER_TEXT = ""
    CHAT_BUBBLE_SYSTEM_TEXT = ""
    NAV_BUTTON_BG = ""
    NAV_BUTTON_HOVER = ""
    NAV_BUTTON_ACTIVE_BG = ""
    NAV_BUTTON_ACTIVE_FG = ""
    NAV_BUTTON_BORDER = ""
    BORDER_SUBTLE = ""
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
    SCROLLBAR_TRACK = ""
    SCROLLBAR_THUMB = ""
    SCROLLBAR_THUMB_HOVER = ""

    # Link colors for interactive text
    LINK_PRIMARY = ""
    LINK_HOVER = ""

    # Button hover and active states
    BUTTON_DANGER_HOVER = ""
    BUTTON_DANGER_ACTIVE = ""
    BUTTON_SUCCESS_HOVER = ""
    BUTTON_SUCCESS_ACTIVE = ""
    BUTTON_WARNING_HOVER = ""
    BUTTON_WARNING_ACTIVE = ""

    # Accent colors for customization
    ACCENT_PRIMARY = ""
    ACCENT_PRIMARY_HOVER = ""
    ACCENT_SECONDARY = ""
    ACCENT_VARIANTS = []

    STATUS_CONNECTED = ""
    STATUS_DISCONNECTED = ""
    STATUS_CONNECTING = ""
    STATUS_PAIRING = ""
    STATUS_READY = ""
    STATUS_TRANSPORT_ERROR = ""


class Typography:
    """Typography scale (8pt grid)."""

    FONT_UI = ".AppleSystemUIFont"  # macOS system font
    FONT_MONO = "Menlo"             # macOS mono font

    SIZE_10 = 10
    SIZE_12 = 12
    SIZE_13 = 13
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
    SIDEBAR_WIDTH = int(260 * 0.85 * 0.9 * 0.92 * 0.9)
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

    WINDOW_WIDTH = int(1200 * 1.05)
    WINDOW_HEIGHT = int(820 * 1.05)
    MIN_WINDOW_WIDTH = int(848 * 1.05)
    MIN_WINDOW_HEIGHT = int(583 * 1.05)
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
    WINDOW_HEIGHT_RATIO = 0.736144
