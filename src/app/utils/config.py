"""
Centralized configuration constants for the LoRa Chat application.
"""
import os

# ------------------------- Debug Configuration ------------------------- #
DEBUG = False  # Set to True to see debug prints


# ------------------------- UI Configuration ------------------------- #
# Window settings
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 520

# Fonts
FONT_PRIMARY = ("Segoe UI", 16, "bold")
FONT_HEADER = ("Segoe UI", 12, "bold")
FONT_LABEL = ("Segoe UI", 11, "bold")
FONT_ENTRY = ("Segoe UI", 10)

# Colors
COLOR_PRIMARY = "#4a90e2"
COLOR_SUCCESS = "#5cb85c"
COLOR_WARNING = "#f0ad4e"
COLOR_DANGER = "#d9534f"
COLOR_INFO = "#66CCFF"

# Status indicator colors
STATUS_DISCONNECTED_COLOR = COLOR_DANGER
STATUS_CONNECTED_COLOR = COLOR_SUCCESS
STATUS_WARNING_COLOR = COLOR_WARNING

# Entry field configuration
ENTRY_WIDTH = 30
PASSWORD_CHAR = "•"

# Progress bar configuration
PROGRESSBAR_LENGTH = 220
PROGRESSBAR_MODE = "indeterminate"


# ------------------------- Status Messages ------------------------- #
STATUS_DISCONNECTED = "Disconnected"
STATUS_CONNECTED = "Connected"
STATUS_AUTHENTICATED = "Authenticated and ready"
STATUS_CONNECTED_MOCK = "Connected (mock)"
STATUS_CONNECTION_FAILED = "Connection failed"
STATUS_INVALID_PASSWORD = "Invalid device password"
STATUS_CONNECTION_DEVICE_FAILED = "Connection failed (device not found)"
STATUS_AUTHENTICATING = "Connected to device, verifying password..."
STATUS_AWAITING_PEER = "Awaiting peer"
STATUS_NOT_CONNECTED = "Not connected"


# ------------------------- Status Keywords ------------------------- #
# Keywords that indicate connected/ready state
STATUS_CONNECTED_KEYWORDS = {"ready", "authenticated", "connected (mock)", "message from"}

# Keywords that indicate disconnected/failed state
STATUS_DISCONNECTED_KEYWORDS = {"disconnected", "connection failed", "invalid device password"}

# Keywords that indicate error state
STATUS_ERROR_KEYWORDS = {"failed", "error", "invalid"}


# ------------------------- Application Constants ------------------------- #
APP_TITLE = "LoRa Chat Desktop"


# ------------------------- File Configuration ------------------------- #
# Users file path (relative to utils directory)
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


# ------------------------- Validation Configuration ------------------------- #
MAX_CRED_LEN = 32
ASCII_RANGE = set(range(0x20, 0x7F))


# ------------------------- Timing Configuration ------------------------- #
# Progress indicator delay for status updates
STATUS_UPDATE_DELAY = 2000  # milliseconds

# Background thread polling interval
RX_THREAD_SLEEP_INTERVAL = 0.2  # seconds

# Mock API sleep interval
MOCK_API_SLEEP_INTERVAL = 0.2  # seconds


# ------------------------- Device Configuration ------------------------- #
# Device pairing and password operations
PAIR_DEVICES_TIMEOUT = 30  # seconds (if needed in future)
PASSWORD_MAX_LENGTH = 32  # characters
PASSWORD_MIN_LENGTH = 1   # characters


# ------------------------- Chat History Configuration ------------------------- #
# Default filename pattern for chat exports
CHAT_EXPORT_FILENAME_PATTERN = "locomm_chat_{username}.txt"


# ------------------------- Notification Configuration ------------------------- #
# Default notification message pattern
NOTIFICATION_MESSAGE_PATTERN = "Message from {sender}"
