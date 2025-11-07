"""
About Page - Redesigned to match ChatPage's design excellence.
Contains application information and device details with ChatPage's scrollable layout and styling.
"""
import tkinter as tk
from tkinter import messagebox, ttk
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class AboutPage(tk.Frame):
    """About page for application information (redesigned with ChatPage excellence)."""

    def __init__(self, master, app, controller, session=None):
        super().__init__(master, bg=Colors.BG_PRIMARY)
        self.app = app
        self.controller = controller
        self.session = session

        # Configure frame styling (matching ChatPage)
        self.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        # Create scrollable frame for all content (matching ChatPage)
        canvas = tk.Canvas(self, bg=Colors.BG_PRIMARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_PRIMARY)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel scrolling (matching ChatPage)
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

        # ---------- Title Section (matching ChatPage) ---------- #
        title_section = tk.Frame(scrollable_frame, bg=Colors.BG_PRIMARY)
        title_section.pack(fill=tk.X, pady=(0, Spacing.XL))

        title_frame = tk.Frame(title_section, bg=Colors.BG_PRIMARY)
        title_frame.pack(anchor="center")

        title_label = tk.Label(
            title_frame,
            text="About Locomm",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XXL, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",
            bg=Colors.BG_PRIMARY
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Professional LoRa Communication Platform",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG),
            fg="#CCCCCC",
            bg=Colors.BG_PRIMARY
        )
        subtitle_label.pack(pady=(Spacing.SM, 0))

        # ---------- Welcome Section with Box Border (Version Information) ---------- #
        welcome_section = tk.Frame(scrollable_frame, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        welcome_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        # Welcome section header (matching ChatPage style)
        welcome_header = tk.Label(welcome_section, text="Application Version", bg=Colors.BG_SECONDARY,
                                fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        welcome_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        welcome_content = tk.Frame(welcome_section, bg=Colors.BG_SECONDARY)
        welcome_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # Version info frame with ChatPage styling
        version_frame = tk.Frame(welcome_content, bg=Colors.BG_SECONDARY)
        version_frame.pack(fill=tk.X)

        # App version
        app_version_label = tk.Label(
            version_frame,
            text="Application Version: 2.0.0",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        app_version_label.pack(anchor="w")

        # Architecture version
        arch_version_label = tk.Label(
            version_frame,
            text="Architecture: Unified Device Management",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        arch_version_label.pack(anchor="w", pady=(Spacing.SM, 0))

        # Python version
        import sys
        python_version = f"Python {sys.version.split()[0]}"
        python_label = tk.Label(
            version_frame,
            text=f"Runtime Environment: {python_version}",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        python_label.pack(anchor="w", pady=(Spacing.SM, 0))

        # ---------- Application Features Section with Box Border (Technical Details) ---------- #
        features_section = tk.Frame(scrollable_frame, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        features_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.MD, Spacing.LG))

        # Features section header (matching ChatPage style)
        features_header = tk.Label(features_section, text="Technical Specifications", bg=Colors.BG_SECONDARY,
                                 fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        features_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        features_content = tk.Frame(features_section, bg=Colors.BG_SECONDARY)
        features_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # Technical specifications with ChatPage styling
        tech_specs = {
            'Communication Protocol': 'LoRa Radio',
            'Authentication System': '5-digit PIN',
            'Session Management': 'In-memory',
            'Transport Layer': 'Asynchronous',
            'UI Framework': 'Tkinter',
            'Architecture Pattern': 'Unified Device Management'
        }

        for key, value in tech_specs.items():
            frame = tk.Frame(features_content, bg=Colors.BG_SECONDARY)
            frame.pack(fill=tk.X, pady=(Spacing.SM, 0))

            key_label = tk.Label(
                frame,
                text=f"{key}:",
                font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD),
                fg="#FFFFFF",
                bg=Colors.BG_SECONDARY
            )
            key_label.pack(side=tk.LEFT)

            value_label = tk.Label(
                frame,
                text=str(value),
                font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
                fg="#FFFFFF",
                bg=Colors.BG_SECONDARY
            )
            value_label.pack(side=tk.LEFT, padx=(Spacing.SM, 0))

        # ---------- Footer (matching ChatPage) ---------- #
        footer_frame = tk.Frame(scrollable_frame, bg=Colors.BG_PRIMARY)
        footer_frame.pack(fill=tk.X, pady=(Spacing.LG, 0))

        footer_label = tk.Label(
            footer_frame,
            text="For technical support, refer to the application documentation",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg="#888888",
            bg=Colors.BG_PRIMARY,
            justify='center',
            wraplength=400
        )
        footer_label.pack()

    def update_connection_status(self, status_text: str):
        """Update the connection status display (delegated to persistent header)."""
        # This method is kept for backward compatibility but status is now handled by persistent header
        pass
