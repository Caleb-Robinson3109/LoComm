import tkinter as tk
from tkinter import ttk
from utils.design_system import Colors, Typography, Spacing, DesignUtils
from .simple_chat_tab import SimpleChatTab
from .settings_tab import SettingsTab
from .home_tab import HomeTab
from .pair_tab import PairTab
from .sidebar import Sidebar
from .view_manager import ViewManager


class MainFrame(ttk.Frame):
    def __init__(self, master, app, session, transport, on_logout):
        super().__init__(master)
        self.app = app
        self.session = session
        self.transport = transport
        self.on_logout = on_logout

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

        # Main container - sidebar + content
        main_container = tk.Frame(self, bg=Colors.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True)

        # ---------- Left Sidebar ---------- #
        self.sidebar = Sidebar(
            main_container,
            on_home_click=self._show_home_view,
            on_chat_click=self._show_chat_view,
            on_pair_click=self._show_pair_view,
            on_settings_click=self._show_settings_view
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # ---------- Right Content Area ---------- #
        self.content_frame = tk.Frame(main_container, bg=Colors.BG_PRIMARY)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

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

        # Pair view container
        self.pair_container = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY, relief="flat", bd=0)
        self.pair_container.pack(fill=tk.BOTH, expand=True)

        # Settings view container
        self.settings_container = tk.Frame(self.content_frame, bg=Colors.BG_PRIMARY, relief="flat", bd=0)
        self.settings_container.pack(fill=tk.BOTH, expand=True)

        # Create the actual components and pack them
        self.home_tab = HomeTab(self.home_container, self.app, self.session)
        self.home_tab.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.chat_tab = SimpleChatTab(self.chat_container, self.transport, self.session.username,
                              on_disconnect=self._handle_disconnect)
        self.chat_tab.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.pair_tab = PairTab(self.pair_container, self.app, self.transport, self.session,
                              on_device_paired=self._handle_device_connection)
        self.pair_tab.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        self.settings_tab = SettingsTab(self.settings_container, self.app, self.transport, self.session)
        self.settings_tab.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

    def _show_home_view(self):
        """Switch to the home view."""
        # Register views if not already done
        if not hasattr(self, '_views_initialized'):
            self._view_manager.register_view("home", self.home_container, self.home_tab)
            self._view_manager.register_view("chat", self.chat_container, self.chat_tab)
            self._view_manager.register_view("pair", self.pair_container, self.pair_tab)
            self._view_manager.register_view("settings", self.settings_container, self.settings_tab)
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

    def show_settings_tab(self):
        """Show the settings view (legacy compatibility)."""
        self._show_settings_view()

    def show_home_tab(self):
        """Show the home view."""
        self._show_home_view()

    def show_pair_tab(self):
        """Show the pair view."""
        self._show_pair_view()

    def update_status(self, text: str):
        """Update status in both chat tab and sidebar."""
        # Only update if components exist
        if hasattr(self, 'chat_tab'):
            self.chat_tab.update_status(text)
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
        # The new ChatTab handles this internally, but we keep this for compatibility
        pass

    def _handle_device_connection(self, device_id: str, device_name: str):
        """Handle device pairing/connection notifications from PairTab."""
        # Update status for simple chat tab
        if device_id and device_name:
            # Device is connected
            self.update_status(f"Connected to {device_name}")
        else:
            # Device is disconnected
            self.update_status("No device connected")
