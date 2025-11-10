"""
Theme primitives for Locomm UI (VS Code-inspired palette, tokens, shared constants).
"""
from __future__ import annotations

from dataclasses import dataclass


class Palette:
    """User custom blue palette + VS Code-inspired palette."""

    # User Custom Blue Color Scheme
    CUSTOM_BLUE_DARK = "#0C2B4E"       # Deep dark blue (primary background)
    CUSTOM_BLUE_MEDIUM = "#1A3D64"     # Darker blue (secondary background)
    CUSTOM_BLUE_LIGHT = "#1D546C"      # Medium blue (tertiary background)
    CUSTOM_TEXT_LIGHT = "#F4F4F4"      # Light gray/white (text)
    
    # Custom neutral palette
    NEUTRAL_1 = "#016B61"  # darkest shade
    NEUTRAL_2 = "#70B2B2"
    NEUTRAL_3 = "#9ECFD4"
    NEUTRAL_4 = "#E5E9C5"
    STEEL = "#B49C83"
    STEEL_LIGHT = "#D9CFC7"
    NAVY = "#332A22"
    NAVY_LIGHT = "#4A3D33"
    MAIN_BROWN = "#0A1F3C"
    
    # VS Code Core Colors
    WHITE = "#FFFFFF"
    
    # VS Code Dark Theme Backgrounds
    VSCODE_BG_PRIMARY = "#1e1e1e"      # Main background (editor area)
    VSCODE_BG_SECONDARY = "#252526"    # Sidebar background
    VSCODE_BG_TERTIARY = "#2d2d30"     # Panel background
    VSCODE_BG_QUATERNARY = "#3c3c3c"   # Input background
    VSCODE_BG_ACTIVE = "#094771"       # Active selection background
    
    # VS Code Text Colors
    VSCODE_TEXT_PRIMARY = "#ffffff"     # Primary text
    VSCODE_TEXT_SECONDARY = "#cccccc"   # Secondary text  
    VSCODE_TEXT_MUTED = "#969696"       # Muted text
    VSCODE_TEXT_DISABLED = "#6c6c6c"    # Disabled text
    
    # VS Code Accent Colors
    VSCODE_BLUE = "#0078d4"            # VS Code blue
    VSCODE_BLUE_LIGHT = "#1ba1e2"      # Light blue
    VSCODE_BLUE_DARK = "#005a9e"       # Dark blue
    VSCODE_PURPLE = "#bf5af2"          # VS Code purple
    VSCODE_PURPLE_LIGHT = "#c77dff"    # Light purple
    VSCODE_PURPLE_DARK = "#7c3aed"     # Dark purple
    
    # VS Code Status Colors
    VSCODE_GREEN = "#4caf50"           # Success green
    VSCODE_RED = "#f85149"             # Error red  
    VSCODE_ORANGE = "#ffa724"          # Warning orange
    VSCODE_YELLOW = "#ffcc02"          # Info yellow
    
    # VS Code Border Colors
    VSCODE_BORDER = "#3c3c3c"          # Primary border
    VSCODE_BORDER_LIGHT = "#484848"    # Light border
    VSCODE_BORDER_ACTIVE = "#0078d4"   # Active border
    
    # VS Code Interactive Colors
    VSCODE_HOVER = "#2a2d2e"           # Hover background
    VSCODE_SELECTED = "#37373d"        # Selected background
    VSCODE_FOCUS = "#0078d4"           # Focus ring color


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
    
    # Button hover and active states
    BUTTON_DANGER_HOVER = ""
    BUTTON_DANGER_ACTIVE = ""
    BUTTON_SUCCESS_HOVER = ""
    BUTTON_SUCCESS_ACTIVE = ""
    
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

    FONT_UI = "Segoe UI"
    FONT_MONO = "Consolas"

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
