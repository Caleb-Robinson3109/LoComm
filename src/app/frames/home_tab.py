"""Home tab component showing welcome message with username."""
import tkinter as tk
from tkinter import ttk
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class HomeTab(tk.Frame):
    """Home/welcome tab displaying user information and welcome message."""

    def __init__(self, master, app, session):
        super().__init__(master, bg=Colors.BG_PRIMARY)
        self.app = app
        self.session = session

        # Configure frame styling
        self.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        # ---------- Welcome Section with Box Border ---------- #
        welcome_section = tk.Frame(self, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        welcome_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        # Welcome section header
        welcome_header = tk.Label(welcome_section, text="Welcome", bg=Colors.BG_SECONDARY,
                                fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        welcome_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        welcome_content = tk.Frame(welcome_section, bg=Colors.BG_SECONDARY)
        welcome_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # ---------- Main Welcome Message ---------- #
        # Welcome title
        welcome_title = tk.Label(
            welcome_content,
            text="Welcome to LoRa Chat",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",  # White text
            bg=Colors.BG_SECONDARY
        )
        welcome_title.pack(anchor="w", pady=(0, Spacing.MD))

        # Username display
        username = self.session.username if hasattr(self.session, 'username') and self.session.username else "User"
        username_label = tk.Label(
            welcome_content,
            text=f"Hello, {username}!",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
            fg="#FFFFFF",  # White text
            bg=Colors.BG_SECONDARY
        )
        username_label.pack(anchor="w", pady=(0, Spacing.LG))

        # ---------- User Info Section with Box Border ---------- #
        info_section = tk.Frame(self, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        info_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.MD, Spacing.LG))

        # Info section header
        info_header = tk.Label(info_section, text="Account Information", bg=Colors.BG_SECONDARY,
                             fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        info_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        info_content = tk.Frame(info_section, bg=Colors.BG_SECONDARY)
        info_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # Username info
        username_info_label = tk.Label(
            info_content,
            text="Username:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        username_info_label.pack(anchor="w", pady=(0, Spacing.XS))

        username_value_label = tk.Label(
            info_content,
            text=username,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        username_value_label.pack(anchor="w", pady=(0, Spacing.MD))

        # Device ID info
        device_id_info_label = tk.Label(
            info_content,
            text="Device ID:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        device_id_info_label.pack(anchor="w", pady=(0, Spacing.XS))

        device_id = getattr(self.session, 'device_id', None)
        device_id_value = device_id if device_id else "Not configured"
        device_id_value_label = tk.Label(
            info_content,
            text=device_id_value,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        device_id_value_label.pack(anchor="w", pady=(0, Spacing.MD))

        # Connection status info
        status_info_label = tk.Label(
            info_content,
            text="Connection:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        status_info_label.pack(anchor="w", pady=(0, Spacing.XS))

        connection_status = "Ready" if hasattr(self.app, 'transport') and self.app.transport.running else "Disconnected"
        status_value_label = tk.Label(
            info_content,
            text=connection_status,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        status_value_label.pack(anchor="w")

    def refresh_content(self):
        """Refresh the home tab content (called when returning to home tab)."""
        # Update username if it changed
        username = self.session.username if hasattr(self.session, 'username') and self.session.username else "User"
        # In a real implementation, you'd update the labels here
        # For now, the labels are set once during initialization
