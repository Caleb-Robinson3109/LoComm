"""Home tab component showing welcome message with username."""
import tkinter as tk
from tkinter import ttk
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class HomeTab(ttk.Frame):
    """Home/welcome tab displaying user information and welcome message."""

    def __init__(self, master, app, session):
        super().__init__(master)
        self.app = app
        self.session = session

        # ---------- Welcome Section with Box Border ---------- #
        welcome_section = ttk.LabelFrame(self, text="Welcome", style='Custom.TLabelframe')
        welcome_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        welcome_content = ttk.Frame(welcome_section)
        welcome_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # ---------- Main Welcome Message ---------- #
        # Welcome title
        welcome_title = tk.Label(
            welcome_content,
            text="Welcome to LoRa Chat",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG, Typography.WEIGHT_BOLD),
            fg="#FFFFFF"  # White text
        )
        welcome_title.pack(anchor="w", pady=(0, Spacing.MD))

        # Username display
        username = self.session.username if hasattr(self.session, 'username') and self.session.username else "User"
        username_label = tk.Label(
            welcome_content,
            text=f"Hello, {username}!",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
            fg="#FFFFFF"  # White text
        )
        username_label.pack(anchor="w", pady=(0, Spacing.LG))

        # ---------- User Info Section with Box Border ---------- #
        info_section = ttk.LabelFrame(self, text="Account Information", style='Custom.TLabelframe')
        info_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.MD, Spacing.LG))

        info_content = ttk.Frame(info_section)
        info_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # Username info
        username_info_label = ttk.Label(
            info_content,
            text="Username:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
            foreground="#FFFFFF"
        )
        username_info_label.pack(anchor="w", pady=(0, Spacing.XS))

        username_value_label = ttk.Label(
            info_content,
            text=username,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD)
        )
        username_value_label.pack(anchor="w", pady=(0, Spacing.MD))

        # Device ID info
        device_id_info_label = ttk.Label(
            info_content,
            text="Device ID:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
            foreground="#FFFFFF"
        )
        device_id_info_label.pack(anchor="w", pady=(0, Spacing.XS))

        device_id = getattr(self.session, 'device_id', None)
        device_id_value = device_id if device_id else "Not configured"
        device_id_value_label = ttk.Label(
            info_content,
            text=device_id_value,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD)
        )
        device_id_value_label.pack(anchor="w", pady=(0, Spacing.MD))

        # Connection status info
        status_info_label = ttk.Label(
            info_content,
            text="Connection:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
            foreground="#FFFFFF"
        )
        status_info_label.pack(anchor="w", pady=(0, Spacing.XS))

        connection_status = "Ready" if hasattr(self.app, 'transport') and self.app.transport.running else "Disconnected"
        status_value_label = ttk.Label(
            info_content,
            text=connection_status,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD)
        )
        status_value_label.pack(anchor="w")

    def refresh_content(self):
        """Refresh the home tab content (called when returning to home tab)."""
        # Update username if it changed
        username = self.session.username if hasattr(self.session, 'username') and self.session.username else "User"
        # In a real implementation, you'd update the labels here
        # For now, the labels are set once during initialization
