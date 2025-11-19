import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable, List

from utils.design_system import AppConfig, Colors, Spacing, Space, Typography, DesignUtils, Palette
from utils.state.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from utils.chatroom_registry import format_chatroom_code, register_chatroom_listener, unregister_chatroom_listener

from .settings_page import SettingsPage
from .home_page import HomePage
from .peers_page import PeersPage
from .about_page import AboutPage
from .help_page import HelpPage
from .chatroom_window import ChatroomWindow
from .sidebar_page import SidebarPage
from .view_manager import ViewManager
from .base_page import PageContext


@dataclass
class RouteConfig:
    route_id: str
    label: str
    factory: Callable[[tk.Frame, PageContext], tk.Widget]
    show_in_sidebar: bool = True


class MainFrame(ttk.Frame):
    """Main application frame with reduced coupling."""

    def __init__(self, master, app, session, controller, on_logout, on_theme_toggle):
        super().__init__(master)

        # Reduce direct coupling by using interface like approach
        self.app = app
        self.session = session
        self.controller = controller
        self.on_logout = on_logout
        self.on_theme_toggle = on_theme_toggle

        # View bookkeeping for lazy loading
        self._view_manager = ViewManager(self)
        self._view_factories: dict[str, Callable[[tk.Frame], tk.Frame]] = {}
        self._view_containers: dict[str, tk.Frame] = {}

        # Navigation context passed into pages
        self._page_context = PageContext(
            app=self.app,
            session=self.session,
            controller=self.controller,
            navigator=self,
        )

        # Simple navigation history for back button
        self._nav_history: list[str] = []
        self._current_route: str | None = None

        self._view_manager.set_protected_views({"home"})
        self.ui_store = get_ui_store()
        self.routes: List[RouteConfig] = self._build_routes()
        self._register_view_factories()

        # Layout and device status subscription
        self._create_layout()
        self.ui_store.subscribe_device_status(self._handle_device_snapshot)

        # Start with home view without pushing history
        self._show_home_view()

    # ------------------------------------------------------------------ #
    # Routing and layout setup
    # ------------------------------------------------------------------ #

    def _register_view_factories(self):
        """Declare view factories for lazy instantiation."""
        self._view_factories = {route.route_id: route.factory for route in self.routes}

    def _build_routes(self) -> List[RouteConfig]:
        ctx = self._page_context
        return [
            RouteConfig("home", "Home", lambda parent, ctx=ctx: HomePage(parent, ctx)),
            RouteConfig(
                "chatroom",
                "Chatroom",
                lambda parent, ctx=ctx: ChatroomWindow(parent, self._handle_chatroom_success),
            ),
            RouteConfig(
                "pair",
                "Peers",
                lambda parent, ctx=ctx: PeersPage(
                    parent,
                    ctx,
                    on_device_paired=self._handle_device_pairing,
                ),
            ),
            RouteConfig("settings", "Settings", lambda parent, ctx=ctx: SettingsPage(parent, ctx)),
            RouteConfig("about", "About", lambda parent, ctx=ctx: AboutPage(parent, ctx)),
            RouteConfig("help", "Help", lambda parent, ctx=ctx: HelpPage(parent, ctx)),
        ]

    def _create_layout(self):
        """Create the main layout with sidebar and content area."""
        self.pack(fill=tk.BOTH, expand=True)

        # Main container - sidebar + content
        main_container = tk.Frame(self, bg=Colors.BG_MAIN)
        main_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=Spacing.SM,
            pady=(int(Spacing.SM / 4), 0),
        )

        self.top_bar = self._build_top_bar(main_container)

        body = tk.Frame(main_container, bg=Colors.BG_MAIN)
        body.pack(fill=tk.BOTH, expand=True)

        # Left sidebar
        nav_items = [(route.route_id, route.label) for route in self.routes if route.show_in_sidebar]
        self.sidebar = SidebarPage(
            body,
            nav_items=nav_items,
            on_nav_select=self.navigate_to,
            on_theme_toggle=self.on_theme_toggle,
            on_back=self.go_back,
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Right content area
        self.content_frame = tk.Frame(body, bg=Colors.BG_MAIN)
        content_pad = int(Spacing.PAGE_PADDING / 2)
        self.content_frame.pack(
            side=tk.RIGHT,
            fill=tk.BOTH,
            expand=True,
            padx=(content_pad, 0),
            pady=(Spacing.PAGE_PADDING, Spacing.PAGE_PADDING),
        )

        self._setup_view_containers()

    def _setup_view_containers(self):
        """Create placeholder containers for each view."""
        pack_opts = {
            "fill": tk.BOTH,
            "expand": True,
            "padx": Spacing.SM,
            "pady": Spacing.SM,
        }
        for route in self.routes:
            container = tk.Frame(self.content_frame, bg=Colors.BG_MAIN, relief="flat", bd=0)
            self._view_containers[route.route_id] = container
            self._view_manager.register_view(route.route_id, container, pack_options=pack_opts.copy())

    def _ensure_view(self, view_name: str):
        """Instantiate a view component the first time it is requested."""
        existing = self._view_manager.get_view_component(view_name)
        if existing:
            return existing

        factory = self._view_factories.get(view_name)
        container = self._view_containers.get(view_name)
        if not factory or not container:
            raise ValueError(f"View '{view_name}' is not registered")

        component = factory(container)
        component.pack(
            fill=tk.BOTH,
            expand=True,
            padx=Spacing.PAGE_PADDING,
            pady=Spacing.PAGE_PADDING,
        )
        self._view_manager.attach_component(view_name, component)
        return component

    def _build_top_bar(self, parent):
        pad_x = Spacing.XS
        pad_y = max(Spacing.XS, int((Spacing.XXS / 1.5) * 1.2 * 1.15))
        bar = tk.Frame(
            parent,
            bg=Colors.BG_ELEVATED,
            padx=pad_x,
            pady=pad_y,
            height=int(Spacing.HEADER_HEIGHT * 1.15),
        )
        bar.pack(fill=tk.X, side=tk.TOP)

        bar.grid_columnconfigure(0, weight=1)
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_columnconfigure(2, weight=0)

        initial_name = getattr(self.session, "local_device_name", "Orion") or "Orion"
        self._default_local_device_name = initial_name

        info_wrap = tk.Frame(bar, bg=Colors.BG_ELEVATED)
        info_wrap.grid(row=0, column=0, sticky="w")

        self.local_device_label = tk.Label(
            info_wrap,
            text=initial_name,
            bg=Colors.BG_ELEVATED,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
        )
        self.local_device_label.pack(side=tk.LEFT, padx=(Space.BASE * 5, Space.XS))

        self._chatroom_listener = None
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

        self.chatroom_label = tk.Label(
            bar,
            text="No Chatrooms Connected",
            bg=Colors.BG_ELEVATED,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        )
        self.chatroom_label.grid(row=0, column=1, sticky="", padx=Space.SM)

        brand_label = tk.Label(
            bar,
            text="Locomm",
            bg=Colors.BG_ELEVATED,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD),
        )
        brand_label.grid(row=0, column=2, sticky="e", padx=(0, Space.BASE * 5))

        self._chatroom_listener = lambda code: self._update_chatroom_label(code)
        register_chatroom_listener(self._chatroom_listener)
        return bar

    # ------------------------------------------------------------------ #
    # Navigation and history
    # ------------------------------------------------------------------ #

    def _show_view(self, view_name: str):
        """Ensure the view exists, then show it."""
        self._ensure_view(view_name)
        self._view_manager.show_view(view_name)

        if hasattr(self.sidebar, "set_active_view"):
            self.sidebar.set_active_view(view_name)
        else:
            self.sidebar.current_view = view_name

    def _set_current_route(self, route_id: str, *, track_history: bool = True):
        """Central place to switch views and optionally record history."""
        if track_history and self._current_route and self._current_route != route_id:
            self._nav_history.append(self._current_route)

        self._show_view(route_id)
        self._current_route = route_id

    def navigate_to(self, route_id: str):
        """Public navigation API used by sidebar and pages."""
        if route_id == "chatroom":
            # Special handling: open chatroom modal like homepage button
            if self.app and hasattr(self.app, "show_chatroom_modal"):
                self.app.show_chatroom_modal()
            return

        if route_id not in self._view_factories:
            return

        self._set_current_route(route_id, track_history=True)

    def go_back(self):
        """Navigate to the previous view, or home if there is no history."""
        while self._nav_history:
            previous = self._nav_history.pop()
            if previous in self._view_factories:
                self._set_current_route(previous, track_history=False)
                return

        if "home" in self._view_factories:
            self._set_current_route("home", track_history=False)

    def _show_home_view(self):
        """Initial load of the home view without recording history."""
        if "home" in self._view_factories:
            self._set_current_route("home", track_history=False)

    def _show_pair_view(self):
        self.navigate_to("pair")

    def _show_settings_view(self):
        self.navigate_to("settings")

    def show_settings_page(self):
        self._show_settings_view()

    def show_home_page(self):
        self.navigate_to("home")

    def show_pair_page(self):
        self.navigate_to("pair")

    # ------------------------------------------------------------------ #
    # Lifecycle and status handling
    # ------------------------------------------------------------------ #

    def destroy(self):
        if self._chatroom_listener:
            unregister_chatroom_listener(self._chatroom_listener)
        try:
            self.ui_store.unsubscribe_device_status(self._handle_device_snapshot)
        except Exception:
            pass
        return super().destroy()

    def _update_chatroom_label(self, code: str | None):
        if not hasattr(self, "chatroom_label"):
            return
        if code:
            formatted = format_chatroom_code(code)
            self.chatroom_label.configure(text=formatted, fg=Colors.TEXT_PRIMARY)
        else:
            self.chatroom_label.configure(text="----- ----- ----- -----", fg=Colors.TEXT_MUTED)

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
            DeviceStage.READY: ("Ready", Colors.STATE_READY),
            DeviceStage.SCANNING: ("Scanning", Colors.STATE_INFO),
            DeviceStage.AWAITING_PIN: ("Awaiting PIN", Colors.STATE_WARNING),
            DeviceStage.CONNECTING: ("Connecting", Colors.STATE_INFO),
            DeviceStage.CONNECTED: ("Connected", Colors.STATE_SUCCESS),
            DeviceStage.DISCONNECTED: ("Disconnected", Colors.STATE_ERROR),
        }
        return mapping.get(stage, ("Status", Colors.STATE_ERROR))

    # ------------------------------------------------------------------ #
    # Other handlers
    # ------------------------------------------------------------------ #

    def _handle_disconnect(self):
        """Handle disconnect request from chat tab."""
        self.controller.stop_session()
        self.controller.status_manager.update_status("Disconnected")
        if hasattr(self.app, "clear_chat_history"):
            self.app.clear_chat_history(confirm=False)

    def set_peer_name(self, name: str):
        """Compatibility stub: peer name is driven by pages now."""
        pass

    # Convenience properties for accessing lazily created pages

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

    # Chatroom and pairing handlers

    def _handle_chatroom_success(self, code: str):
        """Handle successful chatroom connection."""
        self.navigate_to("home")

    def _handle_device_pairing(self, device_id: str, device_name: str):
        """Handle device pairing notifications from PeersPage."""
        if device_id and device_name:
            self.controller.status_manager.update_status(AppConfig.STATUS_CONNECTED)
            self.navigate_to("home")
        else:
            self.controller.status_manager.update_status(AppConfig.STATUS_DISCONNECTED)
