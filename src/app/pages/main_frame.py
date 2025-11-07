import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.status_manager import get_status_manager, DeviceInfo

from .chat_page import ChatPage
from .settings_page import SettingsPage
from .about_page import AboutPage
from .home_page import HomePage
from .pair_page import PairPage
from .sidebar import Sidebar
from .view_manager import ViewManager


class MainFrame(ttk.Frame):
    """
    Main application frame with reduced coupling.
    Uses composition pattern instead of deep inheritance.
    """
    def __init__(self, master, app, session, controller, on_logout, on_theme_toggle):
        super().__init__(master)
        # Reduce direct coupling by using interface-like approach
        self.app = app
        self.session = session
        self.controller = controller
        self.on_logout = on_logout
        self.on_theme_toggle = on_theme_toggle

        # Use consolidated status manager for consistent status display
        self.status_manager = get_status_manager()
        self.status_manager.register_device_callback(self._on_device_change)
        self.status_manager.register_connection_callback(self._on_connection_change)

        # ---------- Modern Sidebar Layout ---------- #
        self._create_layout()

        # Start with home view
        self._show_home_view()

    def _create_layout(self):
        """Create the main layout with sidebar and content area."""
        # Configure main frame
        self.pack(fill=tk.BOTH, expand=True)

        # Initialize view manager
        self._view_manager = ViewManager(self)

        # Initialize status manager
        self.status_manager = get_status_manager()

        # Register for status updates
        self.status_manager.register_status_callback(self._on_status_change)

        # Main container - sidebar + content
        main_container = tk.Frame(self, bg=Colors.SURFACE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=Spacing.XL)

        # ---------- Left Sidebar ---------- #
        self.sidebar = Sidebar(
            main_container,
            on_home_click=self._show_home_view,
            on_chat_click=self._show_chat_view,
            on_pair_click=self._show_pair_view,
            on_settings_click=self._show_settings_view,
            on_about_click=self._show_about_view,
            on_theme_toggle=self.on_theme_toggle
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # ---------- Right Content Area ---------- #
        self.content_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(Spacing.TAB_PADDING, 0), pady=(0, Spacing.TAB_PADDING))

        # Initialize view containers
        self._create_views()

    def _create_views(self):
        """Create all view containers."""
        # Home view container
        self.home_container = tk.Frame(self.content_frame, bg=Colors.SURFACE, relief="flat", bd=0)
        self.home_container.pack(fill=tk.BOTH, expand=True)

        # Chat view container
        self.chat_container = tk.Frame(self.content_frame, bg=Colors.SURFACE, relief="flat", bd=0)
        self.chat_container.pack(fill=tk.BOTH, expand=True)

        # Pair/Device management view container
        self.pair_container = tk.Frame(self.content_frame, bg=Colors.SURFACE, relief="flat", bd=0)
        self.pair_container.pack(fill=tk.BOTH, expand=True)

        # Settings view container (simplified - app config only)
        self.settings_container = tk.Frame(self.content_frame, bg=Colors.SURFACE, relief="flat", bd=0)
        self.settings_container.pack(fill=tk.BOTH, expand=True)

        # About view container
        self.about_container = tk.Frame(self.content_frame, bg=Colors.SURFACE, relief="flat", bd=0)
        self.about_container.pack(fill=tk.BOTH, expand=True)

        # Create the actual components and pack them
        self.home_page = HomePage(self.home_container, self.app, self.session, self)
        self.home_page.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.chat_page = ChatPage(
            self.chat_container,
            self.controller,
            self.session,
            on_disconnect=self._handle_disconnect
        )
        self.chat_page.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.pair_page = PairPage(self.pair_container, self.app, self.controller, self.session,
                              on_device_paired=self._handle_device_pairing)
        self.pair_page.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.settings_page = SettingsPage(self.settings_container, self.app, self.controller, self.session)
        self.settings_page.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.about_page = AboutPage(self.about_container, self.app, self.controller, self.session)
        self.about_page.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

    def _show_home_view(self):
        """Switch to the home view."""
        # Register views if not already done
        if not hasattr(self, '_views_initialized'):
            self._view_manager.register_view("home", self.home_container, self.home_page)
            self._view_manager.register_view("chat", self.chat_container, self.chat_page)
            self._view_manager.register_view("pair", self.pair_container, self.pair_page)
            self._view_manager.register_view("settings", self.settings_container, self.settings_page)
            self._view_manager.register_view("about", self.about_container, self.about_page)
            self._views_initialized = True

        # Show home view
        self._view_manager.show_view("home")

        # Update sidebar state
        self.sidebar.current_view = "home"

    def _show_chat_view(self):
        """Switch to the chat view."""
        self._view_manager.show_view("chat")
        self.sidebar.current_view = "chat"

    def _show_pair_view(self):
        """Switch to the pair view."""
        self._view_manager.show_view("pair")
        self.sidebar.current_view = "pair"

    def _show_settings_view(self):
        """Switch to the settings view."""
        self._view_manager.show_view("settings")
        self.sidebar.current_view = "settings"

    def _show_about_view(self):
        """Switch to the about view."""
        self._view_manager.show_view("about")
        self.sidebar.current_view = "about"

    def show_settings_page(self):
        """Show the settings page."""
        self._show_settings_view()

    def show_home_page(self):
        """Show the home page."""
        self._show_home_view()

    def show_chat_page(self):
        """Show the chat page."""
        self._show_chat_view()

    def show_pair_page(self):
        """Show the pair page."""
        self._show_pair_view()

    def show_about_page(self):
        """Show the about page."""
        self._show_about_view()

    # ------------------------------------------------------------------ #
    def update_status(self, text: str):
        """Update status in both chat tab and sidebar."""
        # Only update if components exist
        if hasattr(self, 'chat_page'):
            self.chat_page.set_status(text)
        if hasattr(self, 'sidebar'):
            self.sidebar.set_status(text)
        self._last_status = text

    def _handle_disconnect(self):
        """Handle disconnect request from chat tab."""
        self.controller.stop_session()
        self.update_status("Disconnected")

    def set_peer_name(self, name: str):
        """Set the peer name (for compatibility with existing code)."""
        # The new ChatPage handles this internally, but we keep this for compatibility
        pass

    def _handle_device_pairing(self, device_id: str, device_name: str):
        """Handle device pairing notifications from PairPage."""
        if device_id and device_name:
            # Device is connected
            self.update_status(f"Connected to {device_name}")
        else:
            # Device is disconnected
            self.update_status("Device disconnected")

    # ========== CONSOLIDATED STATUS CALLBACKS ==========

    def _on_device_change(self, device_info: DeviceInfo):
        """Handle device information changes from consolidated status manager."""
        # Update all child components with consolidated status
        if hasattr(self, 'chat_page'):
            # Update chat page status
            status_text = device_info.get_status_summary()
            self.chat_page.set_status(status_text)

        if hasattr(self, 'sidebar'):
            # Update sidebar status
            status_color = self.status_manager.get_current_status_color()
            self.sidebar.status_value.configure(
                text=device_info.get_status_summary(),
                fg=status_color
            )

    def _on_connection_change(self, is_connected: bool, device_id: str, device_name: str):
        """Handle connection state changes from consolidated status manager."""
        # Update local state
        self._current_device_id = device_id
        self._current_device_name = device_name

        # Update UI on main thread
        if hasattr(self, 'chat_page'):
            self.after(0, self.chat_page.sync_session_info)

    def _on_status_change(self, status_text: str, status_color: str):
        """Handle status changes from status manager."""
        # Status managed by sidebar and chat components
        pass
