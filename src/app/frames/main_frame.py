import tkinter as tk
from tkinter import ttk
from utils.design_system import Colors, Typography, Spacing, DesignUtils
from .new_chat_tab import ChatTab
from .settings_tab import SettingsTab
from .home_tab import HomeTab
from .pair_tab import PairTab
from .sidebar import Sidebar


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

        # Main container - sidebar + content (no background color)
        main_container = tk.Frame(self)
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
        self.content_frame = tk.Frame(main_container)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Initialize view containers
        self._create_views()

    def _create_views(self):
        """Create all view containers."""
        # Home view container
        self.home_container = tk.Frame(self.content_frame)

        # Chat view container
        self.chat_container = tk.Frame(self.content_frame)

        # Pair view container
        self.pair_container = tk.Frame(self.content_frame)

        # Settings view container
        self.settings_container = tk.Frame(self.content_frame)

        # Create the actual components (but don't pack them yet)
        self.home_tab = HomeTab(self.home_container, self.app, self.session)
        self.chat_tab = ChatTab(self.chat_container, self.transport, self.session.username,
                              on_disconnect=self._handle_disconnect)
        self.pair_tab = PairTab(self.pair_container, self.app, self.transport, self.session,
                              on_device_paired=self._handle_device_connection)
        self.settings_tab = SettingsTab(self.settings_container, self.app, self.transport, self.session)

    def _show_home_view(self):
        """Switch to the home view."""
        # Hide all other views
        self.chat_container.pack_forget()
        self.chat_tab.pack_forget()
        self.pair_container.pack_forget()
        self.pair_tab.pack_forget()
        self.settings_container.pack_forget()
        self.settings_tab.pack_forget()

        # Show home view
        self.home_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)
        self.home_tab.pack(fill=tk.BOTH, expand=True)

        # Update sidebar state
        self.sidebar.current_view = "home"

    def _show_chat_view(self):
        """Switch to the chat view."""
        # Hide all other views
        self.home_container.pack_forget()
        self.pair_container.pack_forget()
        self.pair_tab.pack_forget()
        self.settings_container.pack_forget()
        self.settings_tab.pack_forget()

        # Show chat view
        self.chat_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)
        self.chat_tab.pack(fill=tk.BOTH, expand=True)

        # Update sidebar state
        self.sidebar.current_view = "chat"

    def _show_pair_view(self):
        """Switch to the pair view."""
        # Hide all other views
        self.home_container.pack_forget()
        self.chat_container.pack_forget()
        self.chat_tab.pack_forget()
        self.settings_container.pack_forget()
        self.settings_tab.pack_forget()

        # Show pair view
        self.pair_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)
        self.pair_tab.pack(fill=tk.BOTH, expand=True)

        # Update sidebar state
        self.sidebar.current_view = "pair"

    def _show_settings_view(self):
        """Switch to the settings view."""
        # Hide all other views
        self.home_container.pack_forget()
        self.chat_container.pack_forget()
        self.chat_tab.pack_forget()
        self.pair_container.pack_forget()
        self.pair_tab.pack_forget()

        # Show settings view
        self.settings_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)
        self.settings_tab.pack(fill=tk.BOTH, expand=True)

        # Update sidebar state
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
            self.chat_tab.set_status(text)
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
        # Forward to ChatTab to handle device connection state
        self.chat_tab.handle_device_connection(device_id, device_name)

        if device_id and device_name:
            # Device is connected
            self.update_status(f"Connected to {device_name}")
        else:
            # Device is disconnected
            self.update_status("No device connected")
