"""
Design System for LoRa Chat Desktop
Centralized constants for colors, typography, and spacing
"""

import tkinter as tk
from tkinter import ttk

# ==================== COLOR PALETTE ==================== #
class Colors:
    """Minimal color palette - only white text and default colors"""

    # All text is white, everything else uses system defaults (no bg color specified = system default)
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#FFFFFF"
    TEXT_MUTED = "#FFFFFF"

    # Status colors - all white
    STATUS_CONNECTED = "#FFFFFF"
    STATUS_DISCONNECTED = "#FFFFFF"
    STATUS_WARNING = "#FFFFFF"
    STATUS_AUTHENTICATED = "#FFFFFF"

    # Chat colors - all white text
    CHAT_TEXT_LIGHT = "#FFFFFF"
    CHAT_TEXT_DARK = "#FFFFFF"
    CHAT_ME = "#FFFFFF"
    CHAT_OTHER = "#FFFFFF"
    CHAT_SYSTEM = "#FFFFFF"
    CHAT_INPUT_FG = "#FFFFFF"

    # Tab colors - white text only
    TAB_ACTIVE_FG = "#FFFFFF"
    TAB_INACTIVE_FG = "#FFFFFF"

    # For compatibility, but these should not be used for bg colors
    BG_PRIMARY = "#FFFFFF"  # Keep for compatibility, but should be omitted in actual use
    BG_SECONDARY = "#FFFFFF"
    BG_DARK = "#FFFFFF"
    BG_CHAT_LIGHT = "#FFFFFF"
    CHAT_INPUT_BG = "#FFFFFF"
    BORDER_LIGHT = "#FFFFFF"
    BORDER_DARK = "#FFFFFF"
    PRIMARY_BLUE = "#FFFFFF"
    PRIMARY_BLUE_HOVER = "#FFFFFF"
    PRIMARY_BLUE_LIGHT = "#FFFFFF"
    BTN_SUCCESS = "#FFFFFF"
    BTN_WARNING = "#FFFFFF"
    BTN_DANGER = "#FFFFFF"
    BTN_SECONDARY = "#FFFFFF"
    BTN_INFO = "#FFFFFF"
    BG_CHAT_DARK = "#FFFFFF"
    TAB_ACTIVE_BG = "#FFFFFF"
    TAB_INACTIVE_BG = "#FFFFFF"

# ==================== TYPOGRAPHY ==================== #
class Typography:
    """Typography system for consistent text styling"""

    # Font Families
    FONT_PRIMARY = "Segoe UI"
    FONT_MONO = "Consolas"

    # Font Sizes
    SIZE_XS = 8
    SIZE_SM = 10
    SIZE_MD = 12
    SIZE_LG = 14
    SIZE_XL = 16
    SIZE_XXL = 18

    # Font Weights
    WEIGHT_NORMAL = "normal"
    WEIGHT_BOLD = "bold"
    WEIGHT_MEDIUM = "normal"  # Changed from "medium" to "normal" for Tkinter compatibility

# ==================== SPACING ==================== #
class Spacing:
    """Consistent spacing system"""

    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32

    # Component-specific spacing
    HEADER_PADDING = 10
    TAB_PADDING = 8
    BUTTON_PADDING = 6
    SECTION_MARGIN = 14

# ==================== COMPONENT STYLES ==================== #
class ComponentStyles:
    """Pre-defined styles for consistent UI components"""

    @staticmethod
    def create_styles():
        """Create and register all component styles"""
        style = ttk.Style()

        # Configure Ttk theme
        if 'clam' not in style.theme_names():
            style.theme_use('clam')

        # Custom styles
        style.configure('Header.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        style.configure('SubHeader.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM))
        style.configure('Body.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD))
        style.configure('Small.TLabel',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_SM))

        # Button styles
        style.configure('Primary.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM))

        style.configure('Success.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM))

        style.configure('Warning.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM))

        style.configure('Danger.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM))

        style.configure('Secondary.TButton',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_SM))

        # LabelFrame styles
        style.configure('Custom.TLabelframe',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD),
                       borderwidth=2)

        style.configure('Custom.TLabelframe.Label',
                       font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))

# ==================== UTILITY FUNCTIONS ==================== #
class DesignUtils:
    """Utility functions for design system implementation"""

    @staticmethod
    def get_status_color(status_text: str) -> str:
        """Get appropriate color for status text - all white now"""
        # All status colors are white
        return "#FFFFFF"

    @staticmethod
    def create_styled_button(parent, text, command, style='Primary.TButton', **kwargs):
        """Create a styled button with consistent appearance"""
        btn = ttk.Button(parent, text=text, command=command, style=style, **kwargs)
        return btn

    @staticmethod
    def create_styled_label(parent, text, style='Body.TLabel', **kwargs):
        """Create a styled label with consistent appearance"""
        label = ttk.Label(parent, text=text, style=style, **kwargs)
        return label

    @staticmethod
    def create_header_frame(parent, title, **kwargs):
        """Create a styled header frame"""
        frame = ttk.LabelFrame(parent, text=title, style='Custom.TLabelframe', **kwargs)
        return frame

# Initialize styles on import
ComponentStyles.create_styles()
