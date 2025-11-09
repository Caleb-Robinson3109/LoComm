import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable, List

from utils.design_system import Colors, Spacing

from .chat_page import ChatPage
from .settings_page import SettingsPage
from .home_page import HomePage
from .devices_page import DevicesPage, PairPage
from .mock_page import MockPage
from .sidebar import Sidebar
from .view_manager import ViewManager
from .base_page import PageContext
from utils.ui_store import get_ui_store


@dataclass
class RouteConfig:
    route_id: str
    label: str
    factory: Callable[[tk.Frame, PageContext], tk.Widget]
    show_in_sidebar: bool = True


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

        # View bookkeeping for lazy loading
        self._view_manager = ViewManager(self)
        self._view_factories: dict[str, Callable[[tk.Frame], tk.Frame]] = {}
        self._view_instances: dict[str, tk.Frame] = {}
        self._view_containers: dict[str, tk.Frame] = {}
        self._page_context = PageContext(
            app=self.app,
            session=self.session,
            controller=self.controller,
            navigator=self
        )
        self.ui_store = get_ui_store()
        self.routes: List[RouteConfig] = self._build_routes()
        self._register_view_factories()

        # Pre-register factories so we can lazy-load heavy views
        # ---------- Modern Sidebar Layout ---------- #
        self._create_layout()

        # Start with home view
        self._show_home_view()

    def _register_view_factories(self):
        """Declare view factories for lazy instantiation."""
        self._view_factories = {route.route_id: route.factory for route in self.routes}

    def _build_routes(self) -> List[RouteConfig]:
        ctx = self._page_context
        routes = [
            RouteConfig("home", "Home", lambda parent, ctx=ctx: HomePage(parent, ctx)),
            RouteConfig("chat", "Chat", lambda parent, ctx=ctx: ChatPage(parent, ctx,
                                                                        on_disconnect=self._handle_disconnect)),
            RouteConfig("pair", "Devices", lambda parent, ctx=ctx: DevicesPage(parent, ctx,
                                                                              on_device_paired=self._handle_device_pairing)),
            RouteConfig("mock", "Mock", lambda parent, ctx=ctx: MockPage(parent, ctx,
                                                                        on_disconnect=self._handle_disconnect)),
            RouteConfig("settings", "Settings", lambda parent, ctx=ctx: SettingsPage(parent, ctx)),
        ]
        return routes

    def _create_layout(self):
        """Create the main layout with sidebar and content area."""
        # Configure main frame
        self.pack(fill=tk.BOTH, expand=True)

        # Main container - sidebar + content
        main_container = tk.Frame(self, bg=Colors.SURFACE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAGE_MARGIN, pady=Spacing.PAGE_MARGIN)

        # ---------- Left Sidebar ---------- #
        nav_items = [(route.route_id, route.label) for route in self.routes if route.show_in_sidebar]
        self.sidebar = Sidebar(
            main_container,
            nav_items=nav_items,
            on_nav_select=self.navigate_to,
            on_theme_toggle=self.on_theme_toggle
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # ---------- Right Content Area ---------- #
        self.content_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(Spacing.TAB_PADDING, 0), pady=(0, Spacing.TAB_PADDING))

        # Initialize view containers
        self._setup_view_containers()

    def _setup_view_containers(self):
        """Create placeholder containers for each view."""
        pack_opts = {"fill": tk.BOTH, "expand": True, "padx": Spacing.PAGE_PADDING, "pady": Spacing.PAGE_PADDING}
        for route in self.routes:
            container = tk.Frame(self.content_frame, bg=Colors.SURFACE, relief="flat", bd=0)
            self._view_containers[route.route_id] = container
            self._view_manager.register_view(route.route_id, container, pack_options=pack_opts.copy())

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

    def navigate_to(self, route_id: str):
        if route_id not in self._view_factories:
            return
        self._show_view(route_id)

    def _show_home_view(self):
        """Switch to the home view."""
        self.navigate_to("home")

    def _show_chat_view(self):
        """Switch to the chat view."""
        self.navigate_to("chat")

    def _show_pair_view(self):
        """Switch to the pair view."""
        self.navigate_to("pair")

    def _show_settings_view(self):
        """Switch to the settings view."""
        self.navigate_to("settings")

    def show_settings_page(self):
        """Show the settings page."""
        self._show_settings_view()

    def show_home_page(self):
        """Show the home page."""
        self.navigate_to("home")

    def show_chat_page(self):
        """Show the chat page."""
        self.navigate_to("chat")

    def show_pair_page(self):
        """Show the pair page."""
        self.navigate_to("pair")

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
    def mock_page(self):
        return self._ensure_view("mock")

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
