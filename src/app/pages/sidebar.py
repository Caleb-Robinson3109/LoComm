"""Sidebar navigation component for modern UI layout."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.connection_manager import get_connection_manager
from utils.status_manager import get_status_manager


class Sidebar(tk.Frame):
    """Left sidebar navigation component."""

    def __init__(self, master, on_home_click: Optional[Callable] = None,
                 on_chat_click: Optional[Callable] = None,
                 on_pair_click: Optional[Callable] = None,
                 on_settings_click: Optional[Callable] = None,
                 on_about_click: Optional[Callable] = None):
        super().__init__(master, width=200, relief="flat", bd=0)
        self.on_home_click = on_home_click
        self.on_chat_click = on_chat_click
        self.on_pair_click = on_pair_click
        self.on_settings_click = on_settings_click
        self.on_about_click = on_about_click
        self.current_view = "home"  # Default to home view

        # Use centralized connection and status managers
        self.connection_manager = get_connection_manager()
        self.status_manager = get_status_manager()

        # Register for connection state updates
        self.connection_manager.register_connection_callback(self._on_connection_state_change)
        self.connection_manager.register_device_info_callback(self._on_device_info_change)
        self.status_manager.register_status_callback(self._on_status_change)

        # Create navigation UI
        self._create_ui()

    def _create_ui(self):
        """Create the sidebar navigation UI."""
        # Main container with padding - no background color
        main_container = tk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)

        # ---------- Header Section ---------- #
        header_frame = tk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, Spacing.XL))

        # App title/logo
        title_label = tk.Label(
            header_frame,
            text="Locomm",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",  # White text only
            # No background color specified
        )
        title_label.pack(anchor="w")

        # ---------- Navigation Section ---------- #
        nav_frame = tk.Frame(main_container)
        nav_frame.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Home navigation button
        self.home_btn = DesignUtils.create_styled_button(
            nav_frame,
            text="Home",
            command=self._on_home_click,
            style='Primary.TButton'
        )
        self.home_btn.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Chat navigation button
        self.chat_btn = DesignUtils.create_styled_button(
            nav_frame,
            text="Chat",
            command=self._on_chat_click,
            style='Secondary.TButton'
        )
        self.chat_btn.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Pair navigation button
        self.pair_btn = DesignUtils.create_styled_button(
            nav_frame,
            text="Pair",
            command=self._on_pair_click,
            style='Secondary.TButton'
        )
        self.pair_btn.pack(fill=tk.X, pady=(0, Spacing.LG))

        # ---------- Secondary Navigation Section (Settings, About) ---------- #
        # Increased spacing by 5x (LG + XXXL + XXXL = 16 + 32 + 32 = 80px)
        secondary_nav_frame = tk.Frame(main_container)
        secondary_nav_frame.pack(fill=tk.X, pady=(0, Spacing.XXXL + Spacing.XXXL + Spacing.LG))

        # Settings navigation button
        self.settings_btn = DesignUtils.create_styled_button(
            secondary_nav_frame,
            text="Settings",
            command=self._on_settings_click,
            style='Secondary.TButton'
        )
        self.settings_btn.pack(fill=tk.X, pady=(0, Spacing.SM))

        # About navigation button
        self.about_btn = DesignUtils.create_styled_button(
            secondary_nav_frame,
            text="About",
            command=self._on_about_click,
            style='Secondary.TButton'
        )
        self.about_btn.pack(fill=tk.X, pady=(0, Spacing.XL))

        # ---------- Version Information Section ---------- #
        version_frame = tk.Frame(main_container)
        version_frame.pack(fill=tk.X, pady=(Spacing.XL, 0), side=tk.BOTTOM)

        # Set fixed size for version container to prevent expansion
        version_frame.configure(width=180, height=40)  # Fixed dimensions
        version_frame.pack_propagate(False)  # Prevent expansion/contraction

        # Version info label in fixed container
        self.version_label = tk.Label(
            version_frame,
            text="v2.0.0",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_PRIMARY
        )
        self.version_label.pack(expand=True, fill=tk.BOTH, anchor="center")

    def _create_nav_button(self, parent, text: str, command: Callable, style='Secondary.TButton') -> ttk.Button:
        """Create a styled navigation button using DesignUtils matching pair tab style."""
        # Use DesignUtils to create styled buttons like in pair tab
        button = DesignUtils.create_styled_button(
            parent,
            text=text,
            command=command,
            style=style
        )

        return button

    def _on_home_click(self):
        """Handle home navigation click."""
        self.current_view = "home"
        self._update_active_button("home")
        if self.on_home_click:
            self.on_home_click()

    def _on_chat_click(self):
        """Handle chat navigation click."""
        self.current_view = "chat"
        self._update_active_button("chat")
        if self.on_chat_click:
            self.on_chat_click()

    def _on_pair_click(self):
        """Handle pair navigation click."""
        self.current_view = "pair"
        self._update_active_button("pair")
        if self.on_pair_click:
            self.on_pair_click()

    def _on_settings_click(self):
        """Handle settings navigation click."""
        self.current_view = "settings"
        self._update_active_button("settings")
        if self.on_settings_click:
            self.on_settings_click()

    def _on_about_click(self):
        """Handle about navigation click."""
        self.current_view = "about"
        self._update_active_button("about")
        if self.on_about_click:
            self.on_about_click()

    def _update_active_button(self, active_view: str):
        """Update which navigation button appears active."""
        # Reset all buttons to inactive style (Secondary.TButton)
        self.home_btn.configure(style='Secondary.TButton')
        self.chat_btn.configure(style='Secondary.TButton')
        self.pair_btn.configure(style='Secondary.TButton')
        self.settings_btn.configure(style='Secondary.TButton')
        self.about_btn.configure(style='Secondary.TButton')

        # Set active style for current view (Primary.TButton)
        if active_view == "home":
            self.home_btn.configure(style='Primary.TButton')
        elif active_view == "chat":
            self.chat_btn.configure(style='Primary.TButton')
        elif active_view == "pair":
            self.pair_btn.configure(style='Primary.TButton')
        elif active_view == "settings":
            self.settings_btn.configure(style='Primary.TButton')
        elif active_view == "about":
            self.about_btn.configure(style='Primary.TButton')

    def set_status(self, status_text: str):
        """Update the status display (delegated to persistent header)."""
        # This method is kept for backward compatibility but status is now handled by persistent header
        pass

    def show_chat(self):
        """Switch to chat view (for external control)."""
        self._on_chat_click()

    # ========== CONNECTION AND STATUS MANAGER CALLBACKS ==========

    def _on_connection_state_change(self, is_connected: bool, device_id: Optional[str], device_name: Optional[str]):
        """Handle connection state changes from centralized manager."""
        # Status is now handled by persistent header - no action needed here

    def _on_device_info_change(self, device_info: Optional[dict]):
        """Handle device info changes from centralized manager."""
        # Status is now handled by persistent header - no action needed here

    def _on_status_change(self, status_text: str, status_color: str):
        """Handle status changes from status manager."""
        # Status is now handled by persistent header - no action needed here

    def show_connection_status(self):
        """Show current connection status (delegated to persistent header)."""
        # This method is kept for backward compatibility but status is now handled by persistent header
        pass

    def show_pair(self):
        """Switch to pair view (for external control)."""
        self._on_pair_click()

    def show_home(self):
        """Switch to home view (for external control)."""
        self._on_home_click()

    def show_settings(self):
        """Switch to settings view (for external control)."""
        self._on_settings_click()
