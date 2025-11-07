"""Enhanced Home tab with welcome message, features info, and device pairing access."""
import tkinter as tk
from tkinter import ttk
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class HomePage(tk.Frame):
    """Enhanced home page with welcome, features, and quick access to device pairing."""

    def __init__(self, master, app, session):
        super().__init__(master, bg=Colors.BG_PRIMARY)
        self.app = app
        self.session = session

        # Configure frame styling
        self.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        # Create scrollable frame for all content
        canvas = tk.Canvas(self, bg=Colors.BG_PRIMARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_PRIMARY)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_to_mousewheel)
        canvas.bind("<Leave>", _unbind_from_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------- Title Section ---------- #
        title_section = tk.Frame(scrollable_frame, bg=Colors.BG_PRIMARY)
        title_section.pack(fill=tk.X, pady=(0, Spacing.XL))

        title_frame = tk.Frame(title_section, bg=Colors.BG_PRIMARY)
        title_frame.pack(anchor="center")

        title_label = tk.Label(
            title_frame,
            text="Locomm Desktop",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XXL, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",
            bg=Colors.BG_PRIMARY
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Secure Device-to-Device Communication",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG),
            fg="#CCCCCC",
            bg=Colors.BG_PRIMARY
        )
        subtitle_label.pack(pady=(Spacing.SM, 0))

        # ---------- Welcome Section with Box Border ---------- #
        welcome_section = tk.Frame(scrollable_frame, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        welcome_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        # Welcome section header
        welcome_header = tk.Label(welcome_section, text="Welcome", bg=Colors.BG_SECONDARY,
                                fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        welcome_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        welcome_content = tk.Frame(welcome_section, bg=Colors.BG_SECONDARY)
        welcome_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # Welcome text with features (updated terminology)
        welcome_text = """Welcome to Locomm Desktop!

This application allows you to connect and communicate securely with other LoRa-enabled devices using simple 5-digit PIN authentication.

Features:
• Secure 5-digit PIN pairing
• Real-time device communication
• Simple and user-friendly interface
• Credential-free pairing experience
• Professional LoRa communication platform"""

        welcome_label = tk.Label(
            welcome_content,
            text=welcome_text,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY,
            justify='left',
            wraplength=400
        )
        welcome_label.pack(pady=(0, Spacing.LG))


        # ---------- Application Features Section with Box Border ---------- #
        features_section = tk.Frame(scrollable_frame, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        features_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.MD, Spacing.LG))

        # Features section header
        features_header = tk.Label(features_section, text="Application Features", bg=Colors.BG_SECONDARY,
                                 fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        features_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        features_content = tk.Frame(features_section, bg=Colors.BG_SECONDARY)
        features_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # Application benefits
        features_text = """Locomm provides a unified platform for secure LoRa communication:

• PIN-based authentication system
• Streamlined device management
• Professional messaging interface
• Real-time communication capabilities
• Secure device pairing and connection management"""

        features_label = tk.Label(
            features_content,
            text=features_text,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY,
            justify='left',
            wraplength=400
        )
        features_label.pack(pady=(0, Spacing.LG))

        # ---------- Footer ---------- #
        footer_frame = tk.Frame(scrollable_frame, bg=Colors.BG_PRIMARY)
        footer_frame.pack(fill=tk.X, pady=(Spacing.LG, 0))

        footer_label = tk.Label(
            footer_frame,
            text="Use the sidebar to navigate between Home, Chat, Device Management, Settings, and About",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg="#888888",
            bg=Colors.BG_PRIMARY
        )
        footer_label.pack()

        # Store reference to parent for navigation
        self.parent_frame = master  # This should be the MainFrame


    def refresh_content(self):
        """Refresh the home tab content (called when returning to home tab)."""
        # Display-friendly device name can be updated here if needed.
        device_name = getattr(self.session, 'device_name', None) or "Device"
        # Labels are currently static; hook into this method when dynamic text is required.
