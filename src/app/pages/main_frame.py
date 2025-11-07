import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.connection_manager import get_connection_manager
from utils.status_manager import get_status_manager

from .chat_page import ChatPage
from .settings_page import SettingsPage
from .about_page import AboutPage
from .home_page import HomePage
from .pair_page import PairPage
from .sidebar import Sidebar
from .view_manager import ViewManager


class MainFrame(ttk.Frame):
    def __init__(self, master, app, session, transport, on_logout):
        super().__init__(master)
        self.app = app
        self.session = session
        self.transport = transport
        self.on_logout = on_logout

        # Header attributes
        self._current_device_id = None
        self._current_device_name = "001"  # Default device name
        self._is_connected = False

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

        # Initialize connection and status managers
        self.connection_manager = get_connection_manager()
        self.status_manager = get_status_manager()

        # Register for connection state updates
        self.connection_manager.register_connection_callback(self._on_connection_state_change)
        self.connection_manager.register_device_info_callback(self._on_device_info_change)
        self.status_manager.register_status_callback(self._on_status_change)

        # Create header that spans full width
        self._create_inline_header()

        # Main container - sidebar + content
        main_container = tk.Frame(self, bg=Colors.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True)

        # ---------- Left Sidebar ---------- #
        self.sidebar = Sidebar(
            main_container,
            on_home_click=self._show_home_view,
            on_chat_click=self._show_chat_view,
            on_pair_click=self._show_pair_view,
            on_settings_click=self._show_settings_view,
            on_about_click=self._show_about_view
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # ---------- Right Content Area ---------- #
        self.content_frame = tk.Frame(main_container, bg=Colors.BG_PRIMARY)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(Spacing.TAB_PADDING, 0), pady=(0, Spacing.TAB_PADDING))

        # Initialize view containers
        self._create_views()

    def _create_views(self):
        """Create all view containers."""
        # Home view container
        self.home_container = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY, relief="flat", bd=0)
        self.home_container.pack(fill=tk.BOTH, expand=True)

        # Chat view container
        self.chat_container = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY, relief="flat", bd=0)
        self.chat_container.pack(fill=tk.BOTH, expand=True)

        # Pair/Device management view container
        self.pair_container = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY, relief="flat", bd=0)
        self.pair_container.pack(fill=tk.BOTH, expand=True)

        # Settings view container (simplified - app config only)
        self.settings_container = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY, relief="flat", bd=0)
        self.settings_container.pack(fill=tk.BOTH, expand=True)

        # About view container
        self.about_container = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY, relief="flat", bd=0)
        self.about_container.pack(fill=tk.BOTH, expand=True)

        # Create the actual components and pack them
        self.home_page = HomePage(self.home_container, self.app, self.session)
        self.home_page.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.chat_page = ChatPage(self.chat_container, self.transport, self.session.username,
                              on_disconnect=self._handle_disconnect)
        self.chat_page.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.pair_page = PairPage(self.pair_container, self.app, self.transport, self.session,
                              on_device_paired=self._handle_device_pairing)
        self.pair_page.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.settings_page = SettingsPage(self.settings_container, self.app, self.transport, self.session)
        self.settings_page.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.about_page = AboutPage(self.about_container, self.app, self.transport, self.session)
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

    def show_pair_page(self):
        """Show the pair page."""
        self._show_pair_view()

    def update_status(self, text: str):
        """Update status in both chat tab and sidebar."""
        # Only update if components exist
        if hasattr(self, 'chat_page'):
            self.chat_page.set_status(text)
        if hasattr(self, 'sidebar'):
            self.sidebar.set_status(text)

    def _unpair_device(self):
        """Handle unpairing with the other device."""
        # This would typically stop pairing or disconnect
        if hasattr(self.transport, 'stop_pairing'):
            self.transport.stop_pairing()

    def _handle_disconnect(self):
        """Handle disconnect request from chat tab."""
        # Stop transport connection
        if hasattr(self.transport, 'stop'):
            self.transport.stop()

        # Update status in both components
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

    # ========== INLINE HEADER METHODS ==========

    def _create_inline_header(self):
        """Create the inline header UI directly in main frame."""
        # Create header frame that spans full width
        self.header_frame = tk.Frame(self, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        self.header_frame.pack(fill=tk.X, padx=0, pady=(Spacing.TAB_PADDING, 0))

        # ---------- Left Section: Status Indicator ---------- #
        status_section = tk.Frame(self.header_frame, bg=Colors.BG_SECONDARY)
        status_section.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(Spacing.TAB_PADDING, 0))

        # Status indicator container
        status_container = tk.Frame(status_section, bg=Colors.BG_SECONDARY)
        status_container.pack(side=tk.LEFT, anchor="w")

        # Status dot (colored indicator)
        self.status_dot = tk.Label(
            status_container,
            text="●",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG),
            fg=Colors.STATUS_DISCONNECTED,
            bg=Colors.BG_SECONDARY
        )
        self.status_dot.pack(side=tk.LEFT, padx=(0, Spacing.SM))

        # Device name and status text
        self.status_label = tk.Label(
            status_container,
            text="001 - Disconnected",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        )
        self.status_label.pack(side=tk.LEFT)

        # ---------- Right Section: Device Info and Logout ---------- #
        device_section = tk.Frame(self.header_frame, bg=Colors.BG_SECONDARY)
        device_section.pack(side=tk.RIGHT, anchor="e", padx=(0, Spacing.TAB_PADDING))

        # Device info container
        device_info_frame = tk.Frame(device_section, bg=Colors.BG_SECONDARY)
        device_info_frame.pack(side=tk.RIGHT, padx=(0, Spacing.MD))

        # Device ID display (only shown when connected)
        self.device_id_label = tk.Label(
            device_info_frame,
            text="",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SECONDARY
        )
        self.device_id_label.pack(anchor="e")

        # Device name display (only shown when connected)
        self.device_name_label = tk.Label(
            device_info_frame,
            text="",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY
        )
        self.device_name_label.pack(anchor="e")

        # Disconnect button
        self.logout_btn = DesignUtils.create_styled_button(
            device_section,
            text="Disconnect",
            command=self._handle_logout,
            style='Secondary.TButton'
        )
        self.logout_btn.pack(side=tk.RIGHT)

        # Initial status update
        self._update_status_display()

    def _update_status_display(self):
        """Update the status display based on current connection state."""
        # Get connection status from centralized manager
        connection_status = self.connection_manager.get_connection_status_text()
        is_connected = self.connection_manager.is_connected()
        device_info = self.connection_manager.get_connected_device_info()

        # Update connection state
        self._is_connected = is_connected
        self._current_device_info = device_info

        if is_connected and device_info:
            # Connected state
            device_name = device_info['name']
            device_id = device_info['id']

            # Update status display (always show device name 001)
            self.status_label.configure(text=f"001 - Connected to {device_name}")
            self.status_dot.configure(fg=Colors.STATUS_CONNECTED)

            # Update device info display
            self.device_name_label.configure(text=device_name)
            self.device_id_label.configure(text=f"ID: {device_id}")

            # Show device info elements
            self.device_name_label.pack(anchor="e")
            self.device_id_label.pack(anchor="e")
        else:
            # Disconnected state (always show device name 001)
            self.status_label.configure(text="001 - Disconnected")
            self.status_dot.configure(fg=Colors.STATUS_DISCONNECTED)

            # Hide device info elements
            self.device_name_label.configure(text="")
            self.device_id_label.configure(text="")

    def _handle_logout(self):
        """Handle logout button click."""
        if self.on_logout:
            self.on_logout()

    # ========== CONNECTION MANAGER CALLBACKS ==========

    def _on_connection_state_change(self, is_connected: bool, device_id: Optional[str], device_name: Optional[str]):
        """Handle connection state changes from centralized manager."""
        self._current_device_id = device_id
        self._current_device_name = device_name

        # Update UI on main thread
        self.after(0, self._update_status_display)

    def _on_device_info_change(self, device_info: Optional[dict]):
        """Handle device info changes from centralized manager."""
        # Update UI on main thread
        self.after(0, self._update_status_display)

    def _on_status_change(self, status_text: str, status_color: str):
        """Handle status changes from status manager."""
        # Update UI on main thread
        self.after(0, self._update_status_display)
