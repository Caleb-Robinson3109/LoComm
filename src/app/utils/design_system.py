"""
Enhanced Design System for Modern LoRa Chat Desktop
Provides comprehensive styling for contemporary messaging applications
"""

import tkinter as tk
from tkinter import ttk

# ==================== ENHANCED COLOR PALETTE ==================== #
class Colors:
    """Modern color palette for contemporary chat applications"""

    # === CORE BACKGROUND COLORS ===
    BG_PRIMARY = "#1e1e1e"           # Main background (Discord dark)
    BG_SECONDARY = "#2d2d30"         # Secondary background
    BG_TERTIARY = "#37373d"          # Tertiary elements
    BG_CHAT_AREA = "#1e1e1e"         # Chat background
    BG_MESSAGE_OWN = "#0e639c"       # Own message bubbles
    BG_MESSAGE_OTHER = "#2d2d30"     # Other message bubbles
    BG_MESSAGE_SYSTEM = "#252526"    # System message bubbles
    BG_INPUT_AREA = "#2d2d30"        # Message input background

    # === TEXT COLORS ===
    TEXT_PRIMARY = "#ffffff"         # Primary text
    TEXT_SECONDARY = "#cccccc"       # Secondary text
    TEXT_MUTED = "#969696"           # Muted text
    TEXT_PLACEHOLDER = "#6a6a6a"     # Placeholder text
    TEXT_TIMESTAMP = "#8a8a8a"       # Timestamp text

    # === MESSAGE COLORS ===
    MESSAGE_OWN_TEXT = "#ffffff"     # Own message text
    MESSAGE_OTHER_TEXT = "#ffffff"   # Other message text
    MESSAGE_SYSTEM_TEXT = "#cccccc"  # System message text
    MESSAGE_ME = "#ffffff"           # "Me" label color
    MESSAGE_OTHER = "#ffffff"        # Other user label color
    MESSAGE_SYSTEM = "#cccccc"       # System message label

    # === STATUS & INDICATOR COLORS ===
    STATUS_CONNECTED = "#23a559"     # Connected status (green)
    STATUS_DISCONNECTED = "#f23f43" # Disconnected status (red)
    STATUS_CONNECTING = "#fea500"   # Connecting status (orange)
    STATUS_PAIRING = "#0078d4"      # Pairing status (blue)

    # === DELIVERY STATUS INDICATORS ===
    STATUS_PENDING = "#fea500"       # Pending (orange)
    STATUS_SENT = "#23a559"          # Sent (green)
    STATUS_DELIVERED = "#23a559"     # Delivered (green)
    STATUS_READ = "#0078d4"          # Read (blue)
    STATUS_FAILED = "#f23f43"        # Failed (red)

    # === UI COMPONENT COLORS ===
    BORDER_PRIMARY = "#3e3e42"       # Primary borders
    BORDER_FOCUS = "#0078d4"         # Focus borders
    BORDER_HOVER = "#484848"         # Hover borders

    # === BUTTON COLORS ===
    BTN_PRIMARY = "#0078d4"          # Primary button
    BTN_PRIMARY_HOVER = "#106ebe"    # Primary hover
    BTN_SUCCESS = "#23a559"          # Success button
    BTN_WARNING = "#fea500"          # Warning button
    BTN_DANGER = "#f23f43"           # Danger button
    BTN_SECONDARY = "#6c757d"        # Secondary button
    BTN_GHOST = "#404040"            # Ghost button
    BTN_INFO = "#0e639c"             # Info button

    # === INPUT COLORS ===
    INPUT_BG = "#2d2d30"             # Input background
    INPUT_BORDER = "#3e3e42"         # Input border
    INPUT_FOCUS = "#0078d4"          # Input focus border
    INPUT_ERROR = "#f23f43"          # Input error border
    INPUT_HOVER = "#3e3e42"          # Input hover

    # === SIDEBAR & NAVIGATION ===
    SIDEBAR_BG = "#1e1e1e"           # Sidebar background
    SIDEBAR_ACTIVE = "#2d2d30"       # Active sidebar item
    SIDEBAR_HOVER = "#37373d"        # Sidebar hover
    TAB_ACTIVE_BG = "#2d2d30"        # Active tab background
    TAB_INACTIVE_BG = "#3e3e42"      # Inactive tab background

    # === SPECIAL COLORS ===
    ACCENT_BLUE = "#0078d4"          # Accent blue
    ACCENT_GREEN = "#23a559"         # Accent green
    ACCENT_ORANGE = "#fea500"        # Accent orange
    ACCENT_RED = "#f23f43"           # Accent red

    # === BACKWARD COMPATIBILITY ===
    CHAT_TEXT_LIGHT = "#ffffff"
    CHAT_TEXT_DARK = "#ffffff"
    CHAT_INPUT_FG = "#ffffff"
    CHAT_INPUT_BG = "#2d2d30"
    BORDER_LIGHT = "#3e3e42"
    BORDER_DARK = "#3e3e42"
    TAB_ACTIVE_FG = "#ffffff"
    TAB_INACTIVE_FG = "#cccccc"
    TAB_ACTIVE_BG = "#2d2d30"
    TAB_INACTIVE_BG = "#3e3e42"
    PRIMARY_BLUE = "#0078d4"
    PRIMARY_BLUE_HOVER = "#106ebe"
    PRIMARY_BLUE_LIGHT = "#005a9e"
    BTN_INFO = "#0e639c"

# ==================== ENHANCED TYPOGRAPHY ==================== #
class Typography:
    """Modern typography system for contemporary chat applications"""

    # === FONT FAMILIES ===
    FONT_PRIMARY = "Segoe UI"         # Primary UI font
    FONT_MONO = "Consolas"            # Monospace font for code
    FONT_CHAT = "Segoe UI"            # Chat-specific font

    # === FONT SIZES ===
    SIZE_XXS = 9                      # Smallest text
    SIZE_XS = 10                      # Extra small
    SIZE_SM = 11                      # Small
    SIZE_MD = 12                      # Medium (base size)
    SIZE_LG = 13                      # Large
    SIZE_XL = 14                      # Extra large
    SIZE_XXL = 16                     # Double extra large
    SIZE_XXXL = 18                    # Triple extra large

    # === CHAT-SPECIFIC SIZES ===
    CHAT_TIMESTAMP = SIZE_XS
    CHAT_USERNAME = SIZE_SM
    CHAT_MESSAGE = SIZE_MD
    CHAT_SYSTEM = SIZE_SM
    CHAT_STATUS = SIZE_XS

    # === FONT WEIGHTS ===
    WEIGHT_LIGHT = "light"
    WEIGHT_NORMAL = "normal"
    WEIGHT_MEDIUM = "normal"          # Tkinter compatibility
    WEIGHT_BOLD = "bold"
    WEIGHT_HEAVY = "heavy"

# ==================== ENHANCED SPACING ==================== #
class Spacing:
    """Comprehensive spacing system for modern chat UI"""

    # === BASE SPACING ===
    XS = 4                            # Extra small
    SM = 8                            # Small
    MD = 12                           # Medium
    LG = 16                           # Large
    XL = 20                           # Extra large
    XXL = 24                          # Double extra large
    XXXL = 32                         # Triple extra large

    # === COMPONENT-SPECIFIC SPACING ===
    MESSAGE_BUBBLE_PADDING = (12, 8)  # Message bubble padding (horizontal, vertical)
    MESSAGE_GROUP_GAP = 2             # Gap between message groups
    MESSAGE_MARGIN = (8, 4)           # Margin around message bubbles
    CHAT_AREA_PADDING = 12            # Padding inside chat area
    SIDEBAR_WIDTH = 240               # Sidebar width
    HEADER_HEIGHT = 56                # Header area height

    # === LEGACY COMPATIBILITY ===
    HEADER_PADDING = 20
    TAB_PADDING = 16
    BUTTON_PADDING = 8
    SECTION_MARGIN = 20

# ==================== MODERN COMPONENT STYLES ==================== #
class ComponentStyles:
    """Enhanced component styles for contemporary chat UI"""

    _initialized = False

    @classmethod
    def initialize(cls):
        """Create and register comprehensive component styles once."""
        if cls._initialized:
            return

        style = ttk.Style()

        # Configure Ttk theme for modern appearance
        if 'clam' not in style.theme_names():
            style.theme_use('clam')

        # === LABEL STYLES ===
        style.configure('Header.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_XL, Typography.WEIGHT_BOLD),
                       foreground=Colors.TEXT_PRIMARY,
                       background=Colors.BG_PRIMARY)

        style.configure('SubHeader.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
                       foreground=Colors.TEXT_SECONDARY,
                       background=Colors.BG_PRIMARY)

        style.configure('Body.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
                       foreground=Colors.TEXT_PRIMARY,
                       background=Colors.BG_PRIMARY)

        style.configure('Small.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
                       foreground=Colors.TEXT_MUTED,
                       background=Colors.BG_PRIMARY)

        style.configure('Timestamp.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_XS),
                       foreground=Colors.TEXT_TIMESTAMP,
                       background=Colors.BG_PRIMARY)

        # === CHAT-SPECIFIC LABEL STYLES ===
        style.configure('ChatUsername.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD),
                       foreground=Colors.MESSAGE_OTHER_TEXT,
                       background=Colors.BG_CHAT_AREA)

        style.configure('ChatMessage.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
                       foreground=Colors.MESSAGE_OTHER_TEXT,
                       background=Colors.BG_CHAT_AREA,
                       wraplength=600)

        style.configure('ChatSystem.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
                       foreground=Colors.MESSAGE_SYSTEM_TEXT,
                       background=Colors.BG_CHAT_AREA)

        # === BUTTON STYLES ===
        style.configure('Primary.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
                       foreground=Colors.TEXT_PRIMARY,
                       background=Colors.BTN_PRIMARY,
                       borderwidth=0,
                       focuscolor='none')

        style.map('Primary.TButton',
                 background=[('active', Colors.BTN_PRIMARY_HOVER)])

        style.configure('Success.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
                       foreground=Colors.TEXT_PRIMARY,
                       background=Colors.BTN_SUCCESS,
                       borderwidth=0,
                       focuscolor='none')

        style.configure('Warning.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
                       foreground=Colors.TEXT_PRIMARY,
                       background=Colors.BTN_WARNING,
                       borderwidth=0,
                       focuscolor='none')

        style.configure('Danger.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
                       foreground=Colors.TEXT_PRIMARY,
                       background=Colors.BTN_DANGER,
                       borderwidth=0,
                       focuscolor='none')

        style.configure('Secondary.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
                       foreground=Colors.TEXT_SECONDARY,
                       background=Colors.BTN_SECONDARY,
                       borderwidth=1,
                       focuscolor='none')

        style.configure('Ghost.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
                       foreground=Colors.TEXT_SECONDARY,
                       background=Colors.BTN_GHOST,
                       borderwidth=0,
                       focuscolor='none')

        # === CHAT BUTTON STYLES ===
        style.configure('Send.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
                       foreground=Colors.TEXT_PRIMARY,
                       background=Colors.BTN_PRIMARY,
                       borderwidth=0,
                       focuscolor='none')

        style.configure('MessageAction.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_XS),
                       foreground=Colors.TEXT_MUTED,
                       background=Colors.BG_TERTIARY,
                       borderwidth=0,
                       focuscolor='none')

        # === ENTRY STYLES ===
        style.configure('ChatEntry.TEntry',
                       font=(Typography.FONT_CHAT, Typography.SIZE_MD),
                       foreground=Colors.TEXT_PRIMARY,
                       background=Colors.INPUT_BG,
                       bordercolor=Colors.INPUT_BORDER,
                       focuscolor=Colors.INPUT_FOCUS,
                       selectforeground=Colors.TEXT_PRIMARY,
                       selectbackground=Colors.BTN_PRIMARY)

        style.map('ChatEntry.TEntry',
                 bordercolor=[('focus', Colors.INPUT_FOCUS)],
                 background=[('hover', Colors.INPUT_HOVER)])

        # === LABELFRAME STYLES ===
        style.configure('Custom.TLabelframe',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD),
                       borderwidth=2,
                       relief='solid',
                       bordercolor=Colors.BORDER_PRIMARY,
                       background=Colors.BG_PRIMARY,
                       labelanchor='nw')

        style.configure('Custom.TLabelframe.Label',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD),
                       foreground=Colors.TEXT_PRIMARY,
                       background=Colors.BG_PRIMARY)

        # === FRAME STYLES ===
        style.configure('ChatFrame.TFrame',
                       background=Colors.BG_CHAT_AREA,
                       relief='flat')

        style.configure('MessageBubbleOwn.TFrame',
                       background=Colors.BG_MESSAGE_OWN,
                       relief='flat',
                       borderwidth=0)

        style.configure('MessageBubbleOther.TFrame',
                       background=Colors.BG_MESSAGE_OTHER,
                       relief='flat',
                       borderwidth=0)

        style.configure('MessageBubbleSystem.TFrame',
                       background=Colors.BG_MESSAGE_SYSTEM,
                       relief='flat',
                       borderwidth=0)

        cls._initialized = True

# ==================== MODERN UTILITY FUNCTIONS ==================== #
class DesignUtils:
    """Enhanced utility functions for modern chat application design"""

    @staticmethod
    def get_status_color(status_text: str) -> str:
        """Get appropriate color for status text based on modern design"""
        status_lower = status_text.lower()

        if any(word in status_lower for word in ['connected', 'ready', 'online']):
            return Colors.STATUS_CONNECTED
        elif any(word in status_lower for word in ['connecting', 'pairing', 'verifying']):
            return Colors.STATUS_CONNECTING
        elif any(word in status_lower for word in ['disconnected', 'offline', 'failed']):
            return Colors.STATUS_DISCONNECTED
        elif any(word in status_lower for word in ['warning', 'error']):
            return Colors.STATUS_CONNECTING
        else:
            return Colors.TEXT_SECONDARY

    @staticmethod
    def get_delivery_status_color(status_text: str) -> str:
        """Get color for message delivery status"""
        status_lower = status_text.lower()

        if 'pending' in status_lower:
            return Colors.STATUS_PENDING
        elif 'sent' in status_lower:
            return Colors.STATUS_SENT
        elif 'delivered' in status_lower:
            return Colors.STATUS_DELIVERED
        elif 'read' in status_lower:
            return Colors.STATUS_READ
        elif 'failed' in status_lower:
            return Colors.STATUS_FAILED
        else:
            return Colors.TEXT_MUTED

    @staticmethod
    def create_styled_button(parent, text, command, style='Primary.TButton', **kwargs):
        """Create a styled button with modern appearance"""
        btn = ttk.Button(parent, text=text, command=command, style=style, **kwargs)
        return btn

    @staticmethod
    def create_styled_label(parent, text, style='Body.TLabel', **kwargs):
        """Create a styled label with modern appearance"""
        label = ttk.Label(parent, text=text, style=style, **kwargs)
        return label

    @staticmethod
    def create_header_frame(parent, title, **kwargs):
        """Create a styled header frame"""
        frame = ttk.LabelFrame(parent, text=title, style='Custom.TLabelframe', **kwargs)
        return frame

    @staticmethod
    def create_message_bubble(parent, is_own: bool = False):
        """Create a styled message bubble frame"""
        style = 'MessageBubbleOwn.TFrame' if is_own else 'MessageBubbleOther.TFrame'
        bubble_frame = ttk.Frame(parent, style=style, padding=Spacing.MESSAGE_BUBBLE_PADDING)
        return bubble_frame

    @staticmethod
    def create_chat_entry(parent, **kwargs):
        """Create a styled chat entry widget"""
        entry = ttk.Entry(parent, style='ChatEntry.TEntry', **kwargs)
        return entry

    @staticmethod
    def create_tooltip_text(widget, text: str, delay: int = 500):
        """Create a tooltip for widgets"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg=Colors.BG_TERTIARY)
            label = tk.Label(tooltip, text=text, bg=Colors.BG_TERTIARY,
                           fg=Colors.TEXT_PRIMARY, font=(Typography.FONT_PRIMARY, Typography.SIZE_XS))
            label.pack()

            x, y, _, _ = widget.bbox("insert") if hasattr(widget, 'bbox') else (0, 0, 0, 0)
            tooltip.wm_geometry(f"+{x+20}+{y-25}")
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    @staticmethod
    def apply_hover_effect(widget, bg_color: str):
        """Apply hover effect to a widget"""
        def on_enter(event):
            if hasattr(widget, 'original_bg'):
                widget.configure(bg=bg_color)
            else:
                widget.original_bg = str(widget.cget('background'))
                widget.configure(background=bg_color)

        def on_leave(event):
            if hasattr(widget, 'original_bg'):
                widget.configure(bg=widget.original_bg)
                del widget.original_bg

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """Format timestamp for chat display"""
        import time
        return time.strftime("%H:%M", time.localtime(timestamp))

    @staticmethod
    def format_relative_time(timestamp: float) -> str:
        """Format timestamp as relative time (e.g., '2 minutes ago')"""
        import time
        import datetime

        now = time.time()
        diff = now - timestamp

        if diff < 60:
            return "just now"
        elif diff < 3600:
            minutes = int(diff / 60)
            return f"{minutes}m ago"
        elif diff < 86400:
            hours = int(diff / 3600)
            return f"{hours}h ago"
        else:
            days = int(diff / 86400)
            return f"{days}d ago"

def ensure_styles_initialized():
    """Public helper to ensure styles are registered after Tk root exists."""
    ComponentStyles.initialize()


# ==================== APPLICATION CONFIGURATION ==================== #
class AppConfig:
    """Application-wide configuration constants"""

    # === DEBUG CONFIGURATION ===
    DEBUG = False  # Set to True to see debug prints

    # === STATUS KEYWORDS ===
    # Keywords that indicate connected/ready state
    STATUS_CONNECTED_KEYWORDS = {"ready", "connected (mock)", "message from"}

    # Keywords that indicate disconnected/failed state
    STATUS_DISCONNECTED_KEYWORDS = {"disconnected", "connection failed", "invalid pairing code"}

    # Keywords that indicate error state
    STATUS_ERROR_KEYWORDS = {"failed", "error", "invalid"}

    # === STATUS MESSAGES ===
    STATUS_DISCONNECTED = "Disconnected"
    STATUS_CONNECTED = "Connected"
    STATUS_CONNECTED_MOCK = "Connected (mock)"
    STATUS_CONNECTION_FAILED = "Connection failed"
    STATUS_INVALID_PIN = "Invalid pairing code"
    STATUS_CONNECTION_DEVICE_FAILED = "Connection failed (device not found)"
    STATUS_AWAITING_PEER = "Awaiting peer"
    STATUS_NOT_CONNECTED = "Not connected"

    # === WINDOW CONFIGURATION ===
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 700

    # === APPLICATION CONSTANTS ===
    APP_TITLE = "LoRa Chat Desktop"

    # === TIMING CONFIGURATION ===
    STATUS_UPDATE_DELAY = 2000  # milliseconds
    RX_THREAD_SLEEP_INTERVAL = 0.2  # seconds
    MOCK_API_SLEEP_INTERVAL = 0.2  # seconds
    PIN_FOCUS_DELAY = 100  # milliseconds
    STATUS_UPDATE_DELAY_SHORT = 500  # milliseconds

    # === DEVICE CONFIGURATION ===
    PAIR_DEVICES_TIMEOUT = 30  # seconds
    PASSWORD_MAX_LENGTH = 32  # characters
    PASSWORD_MIN_LENGTH = 1   # characters

    # === VALIDATION CONFIGURATION ===
    MAX_CRED_LEN = 32
    ASCII_RANGE = set(range(0x20, 0x7F))

    # === ENTRY FIELD CONFIGURATION ===
    ENTRY_WIDTH = 30
    PASSWORD_CHAR = "*"

    # === PROGRESS BAR CONFIGURATION ===
    PROGRESSBAR_LENGTH = 220
    PROGRESSBAR_MODE = "indeterminate"

    # === CHAT HISTORY CONFIGURATION ===
    CHAT_EXPORT_FILENAME_PATTERN = "locomm_chat_{device}.txt"

    # === NOTIFICATION CONFIGURATION ===
    NOTIFICATION_MESSAGE_PATTERN = "Message from {sender}"

    # === LEGACY COMPATIBILITY ===
    # Legacy constants for backward compatibility
    COLOR_PRIMARY = "#4a90e2"
    COLOR_SUCCESS = "#5cb85c"
    COLOR_WARNING = "#f0ad4e"
    COLOR_DANGER = "#d9534f"
    COLOR_INFO = "#66CCFF"

    # Status indicator colors
    STATUS_DISCONNECTED_COLOR = COLOR_DANGER
    STATUS_CONNECTED_COLOR = COLOR_SUCCESS
    STATUS_WARNING_COLOR = COLOR_WARNING


# Legacy constants for backward compatibility
DEBUG = AppConfig.DEBUG
STATUS_CONNECTED_KEYWORDS = AppConfig.STATUS_CONNECTED_KEYWORDS
STATUS_DISCONNECTED_KEYWORDS = AppConfig.STATUS_DISCONNECTED_KEYWORDS
STATUS_ERROR_KEYWORDS = AppConfig.STATUS_ERROR_KEYWORDS
MAX_CRED_LEN = AppConfig.MAX_CRED_LEN
ASCII_RANGE = AppConfig.ASCII_RANGE
APP_TITLE = AppConfig.APP_TITLE
WINDOW_WIDTH = AppConfig.WINDOW_WIDTH
WINDOW_HEIGHT = AppConfig.WINDOW_HEIGHT
ENTRY_WIDTH = AppConfig.ENTRY_WIDTH
PASSWORD_CHAR = AppConfig.PASSWORD_CHAR
PROGRESSBAR_LENGTH = AppConfig.PROGRESSBAR_LENGTH
PROGRESSBAR_MODE = AppConfig.PROGRESSBAR_MODE
STATUS_DISCONNECTED = AppConfig.STATUS_DISCONNECTED
STATUS_CONNECTED = AppConfig.STATUS_CONNECTED
STATUS_CONNECTED_MOCK = AppConfig.STATUS_CONNECTED_MOCK
STATUS_CONNECTION_FAILED = AppConfig.STATUS_CONNECTION_FAILED
STATUS_INVALID_PIN = AppConfig.STATUS_INVALID_PIN
STATUS_CONNECTION_DEVICE_FAILED = AppConfig.STATUS_CONNECTION_DEVICE_FAILED
STATUS_AWAITING_PEER = AppConfig.STATUS_AWAITING_PEER
STATUS_NOT_CONNECTED = AppConfig.STATUS_NOT_CONNECTED
PAIR_DEVICES_TIMEOUT = AppConfig.PAIR_DEVICES_TIMEOUT
PASSWORD_MAX_LENGTH = AppConfig.PASSWORD_MAX_LENGTH
PASSWORD_MIN_LENGTH = AppConfig.PASSWORD_MIN_LENGTH
CHAT_EXPORT_FILENAME_PATTERN = AppConfig.CHAT_EXPORT_FILENAME_PATTERN
NOTIFICATION_MESSAGE_PATTERN = AppConfig.NOTIFICATION_MESSAGE_PATTERN

# File configuration
import os
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
