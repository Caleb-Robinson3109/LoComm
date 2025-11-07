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
    def __init__(self, master, app, session, controller, on_logout):
        super().__init__(master)
        self.app = app
        self.session = session
        self.controller = controller
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
        main_container = tk.Frame(self, bg=Colors.SURFACE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.XL, pady=Spacing.XL)

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
    # Header actions
    def _on_pair_click(self):
        self._show_pair_view()
        if hasattr(self.sidebar, "_update_active_button"):
            self.sidebar._update_active_button("pair")

    def update_status(self, text: str):
        """Update status in both chat tab and sidebar."""
        # Only update if components exist
        if hasattr(self, 'chat_page'):
            self.chat_page.set_status(text)
        if hasattr(self, 'sidebar'):
            self.sidebar.set_status(text)
        self._last_status = text
        self._update_status_display()

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

    # ========== INLINE HEADER METHODS ==========

    def _create_inline_header(self):
        """Create the inline header UI directly in main frame."""
        self.header_frame = tk.Frame(self, bg=Colors.SURFACE_HEADER)
        self.header_frame.pack(fill=tk.X, padx=Spacing.MD, pady=(Spacing.MD, 0))

        left = tk.Frame(self.header_frame, bg=Colors.SURFACE_HEADER)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.status_badge = DesignUtils.pill(left, "Disconnected", variant="danger")
        self.status_badge.pack(anchor="w")

        self.status_title = tk.Label(left, text="Awaiting connection", bg=Colors.SURFACE_HEADER,
                                     fg=Colors.TEXT_PRIMARY,
                                     font=(Typography.FONT_UI, Typography.SIZE_20, Typography.WEIGHT_BOLD))
        self.status_title.pack(anchor="w", pady=(Spacing.XXS, 0))

        self.status_subtitle = tk.Label(left, text="Pair a device to start chatting", bg=Colors.SURFACE_HEADER,
                                        fg=Colors.TEXT_SECONDARY,
                                        font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR))
        self.status_subtitle.pack(anchor="w")

        right = tk.Frame(self.header_frame, bg=Colors.SURFACE_HEADER)
        right.pack(side=tk.RIGHT)

        self.primary_action = DesignUtils.button(right, text="Pair Device", command=self._on_pair_click, variant="primary")
        self.primary_action.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        self.logout_btn = DesignUtils.button(right, text="Disconnect", command=self._handle_logout, variant="ghost")
        self.logout_btn.pack(side=tk.RIGHT)

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
            device_name = device_info['name']
            device_id = device_info['id']
            self.status_badge.configure(text="Connected", bg=Colors.STATE_SUCCESS, fg=Colors.SURFACE)
            self.status_title.configure(text=f"Paired with {device_name}")
            self.status_subtitle.configure(text=f"Device ID {device_id}")
        else:
            self.status_badge.configure(text="Disconnected", bg=Colors.STATE_ERROR, fg=Colors.SURFACE)
            self.status_title.configure(text="Awaiting connection")
            self.status_subtitle.configure(text="Pair a device to start chatting")

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
        if hasattr(self, 'chat_page'):
            self.after(0, self.chat_page.sync_session_info)

    def _on_device_info_change(self, device_info: Optional[dict]):
        """Handle device info changes from centralized manager."""
        # Update UI on main thread
        self.after(0, self._update_status_display)
        if hasattr(self, 'chat_page'):
            self.after(0, self.chat_page.sync_session_info)

    def _on_status_change(self, status_text: str, status_color: str):
        """Handle status changes from status manager."""
        # Update UI on main thread
        self.after(0, self._update_status_display)
