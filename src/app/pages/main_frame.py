import tkinter as tk
from tkinter import ttk
from typing import Callable

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.status_manager import get_status_manager, DeviceInfo

from .chat_page import ChatPage
from .settings_page import SettingsPage
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

        # CRITICAL FIX: Track registered callbacks for cleanup
        self._registered_callbacks = [
            ("device", self.status_manager, self._on_device_change),
            ("connection", self.status_manager, self._on_connection_change),
        ]

        # View bookkeeping for lazy loading
        self._view_manager = ViewManager(self)
        self._view_factories: dict[str, Callable[[tk.Frame], tk.Widget]] = {}
        self._view_instances: dict[str, tk.Widget] = {}
        self._view_containers: dict[str, tk.Frame] = {}

        # Pre-register factories so we can lazy-load heavy views
        self._register_view_factories()

        # ---------- Modern Sidebar Layout ---------- #
        self._create_layout()

        # Start with home view
        self._show_home_view()

    def _register_view_factories(self):
        """Declare view factories for lazy instantiation."""
        self._view_factories = {
            "home": lambda parent: HomePage(parent, self.app, self.session, self),
            "chat": lambda parent: ChatPage(parent, self.controller, self.session,
                                            on_disconnect=self._handle_disconnect),
            "pair": lambda parent: PairPage(parent, self.app, self.controller, self.session,
                                            on_device_paired=self._handle_device_pairing),
            "settings": lambda parent: SettingsPage(parent, self.app, self.controller, self.session),
        }

    def _create_layout(self):
        """Create the main layout with sidebar and content area."""
        # Configure main frame
        self.pack(fill=tk.BOTH, expand=True)

        # Main container - sidebar + content
        main_container = tk.Frame(self, bg=Colors.SURFACE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAGE_MARGIN, pady=Spacing.PAGE_MARGIN)

        # ---------- Left Sidebar ---------- #
        self.sidebar = Sidebar(
            main_container,
            on_home_click=self._show_home_view,
            on_chat_click=self._show_chat_view,
            on_pair_click=self._show_pair_view,
            on_settings_click=self._show_settings_view,
            on_theme_toggle=self.on_theme_toggle
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # ---------- Right Content Area ---------- #
        self.content_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(Spacing.TAB_PADDING, 0), pady=(0, Spacing.TAB_PADDING))

        # Initialize view containers
        self._setup_view_containers()

    def _setup_view_containers(self):
        """Create placeholder containers for each view."""
        pack_opts = {"fill": tk.BOTH, "expand": True, "padx": Spacing.PAGE_PADDING, "pady": Spacing.PAGE_PADDING}
        for view_name in ("home", "chat", "pair", "settings"):
            container = tk.Frame(self.content_frame, bg=Colors.SURFACE, relief="flat", bd=0)
            self._view_containers[view_name] = container
            self._view_manager.register_view(view_name, container, pack_options=pack_opts.copy())

    def _ensure_view(self, view_name: str):
        """Instantiate a view component the first time it is requested."""
        if view_name in self._view_instances:
            return self._view_instances[view_name]
        factory = self._view_factories.get(view_name)
        container = self._view_containers.get(view_name)
        if not factory or not container:
            raise ValueError(f"View '{view_name}' is not registered")
        component = factory(container)
        component.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAGE_PADDING, pady=Spacing.PAGE_PADDING)
        self._view_manager.attach_component(view_name, component)
        self._view_instances[view_name] = component
        return component

    def _show_view(self, view_name: str):
        """Ensure the view exists, then show it."""
        self._ensure_view(view_name)
        self._view_manager.show_view(view_name)
        if hasattr(self.sidebar, "set_active_view"):
            self.sidebar.set_active_view(view_name)
        else:
            self.sidebar.current_view = view_name

    def _show_home_view(self):
        """Switch to the home view."""
        self._show_view("home")

    def _show_chat_view(self):
        """Switch to the chat view."""
        self._show_view("chat")

    def _show_pair_view(self):
        """Switch to the pair view."""
        self._show_view("pair")

    def _show_settings_view(self):
        """Switch to the settings view."""
        self._show_view("settings")

    def _show_about_view(self):
        """Switch to the about view."""
        self._show_view("about")

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
        chat_page = self._view_instances.get("chat")
        if chat_page:
            chat_page.set_status(text)
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

    # Compatibility properties to access lazily-created pages -----------------
    @property
    def chat_page(self):
        return self._ensure_view("chat")

    @property
    def home_page(self):
        return self._ensure_view("home")

    @property
    def pair_page(self):
        return self._ensure_view("pair")

    @property
    def settings_page(self):
        return self._ensure_view("settings")

    @property
    def about_page(self):
        return self._ensure_view("about")

    def _handle_device_pairing(self, device_id: str, device_name: str):
        """Handle device pairing notifications from PairPage."""
        if device_id and device_name:
            # Device is connected
            self.update_status(f"Connected to {device_name}")
            self._show_chat_view()
            self.chat_page.sync_session_info()
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
        chat_page = self._view_instances.get("chat")
        if chat_page:
            self.after(0, chat_page.sync_session_info)

    def _on_status_change(self, status_text: str, status_color: str):
        """Handle status changes from status manager."""
        # Status managed by sidebar and chat components
        pass

    def destroy(self):
        """CRITICAL FIX: Clean up registered callbacks to prevent memory leaks."""
        try:
            # Unregister all callbacks to prevent memory leaks
            for callback_type, manager, callback in self._registered_callbacks:
                if callback_type == "device" and hasattr(manager, 'unregister_device_callback'):
                    manager.unregister_device_callback(callback)
                elif callback_type == "connection" and hasattr(manager, 'unregister_connection_callback'):
                    manager.unregister_connection_callback(callback)
        except Exception as e:
            print(f"Error cleaning up main frame callbacks: {e}")
        finally:
            super().destroy()
