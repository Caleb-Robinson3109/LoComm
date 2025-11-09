import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable, List

from utils.design_system import Colors, Spacing, Space, Typography, DesignUtils
from utils.ui_store import DeviceStage, DeviceStatusSnapshot

from .chat_page import ChatPage
from .settings_page import SettingsPage
from .home_page import HomePage
from .devices_page import DevicesPage
from .about_page import AboutPage
from .help_page import HelpPage
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
        self._view_cache_order: list[str] = []
        self._max_cached_views = 3
        self.ui_store = get_ui_store()
        self.routes: List[RouteConfig] = self._build_routes()
        self._register_view_factories()

        # Pre-register factories so we can lazy-load heavy views
        # ---------- Modern Sidebar Layout ---------- #
        self._create_layout()
        self.ui_store.subscribe_device_status(self._handle_device_snapshot)

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
            RouteConfig("settings", "Settings", lambda parent, ctx=ctx: SettingsPage(parent, ctx)),
            RouteConfig("about", "About", lambda parent, ctx=ctx: AboutPage(parent, ctx)),
            RouteConfig("help", "Help", lambda parent, ctx=ctx: HelpPage(parent, ctx)),
        ]
        return routes

    def _create_layout(self):
        """Create the main layout with sidebar and content area."""
        # Configure main frame
        self.pack(fill=tk.BOTH, expand=True)

        # Main container - sidebar + content
        main_container = tk.Frame(self, bg=Colors.SURFACE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=(int(Spacing.SM / 4), 0))

        self.top_bar = self._build_top_bar(main_container)

        body = tk.Frame(main_container, bg=Colors.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, pady=(int(Spacing.SM / 4), 0))

        # ---------- Left Sidebar ---------- #
        nav_items = [(route.route_id, route.label) for route in self.routes if route.show_in_sidebar]
        self.sidebar = Sidebar(
            body,
            nav_items=nav_items,
            on_nav_select=self.navigate_to,
            on_theme_toggle=self.on_theme_toggle
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # ---------- Right Content Area ---------- #
        self.content_frame = tk.Frame(body, bg=Colors.SURFACE)
        content_pad = int(Spacing.PAGE_PADDING / 2)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(content_pad, 0), pady=(Spacing.PAGE_PADDING, Spacing.PAGE_PADDING))

        # Initialize view containers
        self._setup_view_containers()


    def _setup_view_containers(self):
        """Create placeholder containers for each view."""
        pack_opts = {"fill": tk.BOTH, "expand": True, "padx": Spacing.SM, "pady": Spacing.SM}
        for route in self.routes:
            container = tk.Frame(self.content_frame, bg=Colors.SURFACE, relief="flat", bd=0)
            self._view_containers[route.route_id] = container
            self._view_manager.register_view(route.route_id, container, pack_options=pack_opts.copy())

    def _ensure_view(self, view_name: str):
        """Instantiate a view component the first time it is requested."""
        if view_name in self._view_instances:
            self._record_view_usage(view_name)
            return self._view_instances[view_name]
        factory = self._view_factories.get(view_name)
        container = self._view_containers.get(view_name)
        if not factory or not container:
            raise ValueError(f"View '{view_name}' is not registered")
        component = factory(container)
        component.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAGE_PADDING, pady=Spacing.PAGE_PADDING)
        self._view_manager.attach_component(view_name, component)
        self._view_instances[view_name] = component
        self._record_view_usage(view_name)
        self._trim_view_cache()
        return component

    def _build_top_bar(self, parent):
        pad_x = Spacing.XS
        pad_y = max(Spacing.XS, int((Spacing.XXS / 1.5) * 1.2 * 1.15))
        bar = tk.Frame(parent, bg=Colors.SURFACE_SIDEBAR, padx=pad_x, pady=pad_y, height=int(Spacing.HEADER_HEIGHT * 1.15))
        bar.pack(fill=tk.X, side=tk.TOP, pady=(0, int(Spacing.XXS / 2)))

        bar.grid_columnconfigure(0, weight=1)
        bar.grid_columnconfigure(1, weight=0)

        initial_name = getattr(self.session, "local_device_name", "Orion") or "Orion"
        self._default_local_device_name = initial_name

        info_wrap = tk.Frame(bar, bg=Colors.SURFACE_HEADER)
        info_wrap.grid(row=0, column=0, sticky="w")

        self.local_device_label = tk.Label(
            info_wrap,
            text=initial_name,
            bg=Colors.SURFACE_HEADER,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
        )
        self.local_device_label.pack(side=tk.LEFT, padx=(0, Space.XS))

        self.status_badge = tk.Label(
            info_wrap,
            text="Disconnected",
            bg=Colors.STATE_ERROR,
            fg=Colors.SURFACE,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
            padx=Spacing.SM,
            pady=int(Spacing.XS / 2),
        )
        self.status_badge.pack(side=tk.LEFT, padx=(0, Space.SM))

        brand_label = tk.Label(
            bar,
            text="Locomm",
            bg=Colors.SURFACE_HEADER,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD),
        )
        brand_label.grid(row=0, column=1, sticky="e")
        return bar

    def _show_view(self, view_name: str):
        """Ensure the view exists, then show it."""
        target = self._ensure_view(view_name)
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

    def destroy(self):
        try:
            self.ui_store.unsubscribe_device_status(self._handle_device_snapshot)
        except Exception:
            pass
        try:
            self._view_manager.cleanup_all()
        except Exception:
            pass
        return super().destroy()

    # ------------------------------------------------------------------ #
    def _handle_device_snapshot(self, snapshot: DeviceStatusSnapshot):
        if not snapshot:
            return
        badge_text, badge_color = self._badge_style_for_stage(snapshot.stage)
        self.status_badge.configure(text=badge_text, bg=badge_color, fg=Colors.SURFACE)
        local_name = getattr(self.session, "local_device_name", None) or self._default_local_device_name
        self.local_device_label.configure(text=local_name)

    @staticmethod
    def _badge_style_for_stage(stage: DeviceStage) -> tuple[str, str]:
        mapping = {
            DeviceStage.READY: ("Ready", Colors.STATE_INFO),
            DeviceStage.SCANNING: ("Scanning", Colors.STATE_INFO),
            DeviceStage.AWAITING_PIN: ("Awaiting PIN", Colors.STATE_WARNING),
            DeviceStage.CONNECTING: ("Connecting", Colors.STATE_INFO),
            DeviceStage.CONNECTED: ("Connected", Colors.STATE_SUCCESS),
            DeviceStage.DISCONNECTED: ("Disconnected", Colors.STATE_ERROR),
        }
        return mapping.get(stage, ("Status", Colors.STATE_ERROR))

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
        if hasattr(self.app, "clear_chat_history"):
            self.app.clear_chat_history(confirm=False)

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

    def _record_view_usage(self, view_name: str):
        if view_name in self._view_cache_order:
            self._view_cache_order.remove(view_name)
        self._view_cache_order.append(view_name)

    def _trim_view_cache(self):
        while len(self._view_cache_order) > self._max_cached_views:
            candidates = [
                v for v in self._view_cache_order
                if v not in {self._view_manager.active_view, "home"}
            ]
            if not candidates:
                break
            target = candidates[0]
            self._view_cache_order.remove(target)
            self._unload_view(target)

    def _unload_view(self, view_name: str):
        if view_name in self._view_cache_order:
            self._view_cache_order.remove(view_name)
        component = self._view_instances.pop(view_name, None)
        if component:
            try:
                component.destroy()
            except Exception:
                pass
        self._view_manager.detach_component(view_name)
