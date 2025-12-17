import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable, List

from utils.design_system import AppConfig, Colors, Spacing, Space, Typography
from utils.chatroom_registry import (
    format_chatroom_code,
    register_chatroom_listener,
    unregister_chatroom_listener,
    get_active_code,
)

from .settings_page import SettingsPage
from .home_page import HomePage
from .peers_page import PeersPage
from .about_page import AboutPage
from .help_page import HelpPage
from .chatroom_page import ChatroomPage
from .sidebar import Sidebar
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
        self._sidebar_min = Spacing.SIDEBAR_WIDTH
        self._sidebar_max = Spacing.SIDEBAR_WIDTH

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
        self.routes: List[RouteConfig] = self._build_routes()
        self._register_view_factories()

        # Layout and device status subscription
        self._create_layout()
        self._status_callback_registered = False
        self._register_status_listener()

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
                lambda parent, ctx=ctx: ChatroomPage(parent, self._handle_chatroom_success),
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

        # Fixed layout: sidebar + content
        self.main_container = tk.Frame(self, bg=Colors.BG_MAIN, highlightthickness=0, bd=0)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.top_bar = self._build_top_bar(self.main_container)

        body = tk.Frame(self.main_container, bg=Colors.BG_MAIN)
        body.pack(fill=tk.BOTH, expand=True, pady=(Spacing.XXS, 0))
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)

        # Left sidebar
        nav_items = [(route.route_id, route.label) for route in self.routes if route.show_in_sidebar]
        self.sidebar = Sidebar(
            body,
            nav_items=nav_items,
            on_nav_select=self.navigate_to,
            on_theme_toggle=self.on_theme_toggle,
            on_back=self.go_back,
            width=Spacing.SIDEBAR_WIDTH,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.configure(width=Spacing.SIDEBAR_WIDTH)

        # Right content area
        self.content_frame = tk.Frame(body, bg=Colors.BG_MAIN)
        content_pad = 0
        self.content_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(content_pad, 0),
            pady=(0, 0),
        )

        self._setup_view_containers()
        self._register_top_listeners()

    def _setup_view_containers(self):
        """Create placeholder containers for each view."""
        pack_opts = {
            "fill": tk.BOTH,
            "expand": True,
            "padx": 0,
            "pady": 0,
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

        bar.grid_columnconfigure(0, weight=0)
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_columnconfigure(2, weight=0)

        initial_name = getattr(self.session, "local_device_name", "") or "Set name"
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
        self.local_device_label.grid(row=0, column=0, sticky="w", padx=(Space.BASE * 5, Space.XS))

        self._chatroom_listener = None

        center_wrap = tk.Frame(bar, bg=Colors.BG_ELEVATED)
        center_wrap.grid(row=0, column=1, sticky="nsew")
        center_wrap.grid_columnconfigure(0, weight=1)

        self.chatroom_label = tk.Label(
            center_wrap,
            text="No Chatroom",
            bg=Colors.BG_ELEVATED,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
            anchor="center",
            justify="center",
        )
        self.chatroom_label.grid(row=0, column=0, sticky="ew", pady=(Space.XXS, 0))

        # Status badge (Connected / Not Connected) now sits on the right edge
        status_column = tk.Frame(bar, bg=Colors.BG_ELEVATED)
        status_column.grid(row=0, column=2, sticky="e", padx=(0, Space.BASE * 5))
        status_column.grid_columnconfigure(0, weight=1)

        self.status_badge = tk.Label(
            status_column,
            text="Not Connected",
            bg=Colors.STATE_WARNING,
            fg=Colors.SURFACE,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_BOLD),
            padx=Spacing.SM,
            pady=int(Spacing.XS / 2),
        )
        self.status_badge.grid(row=0, column=0, sticky="e")

        self._chatroom_listener = lambda code: self._update_chatroom_label(code)
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
        if route_id not in self._view_factories:
            return

        # When navigating to chatroom, only set Awaiting status if there is no
        # active chatroom code. Previously this unconditionally set awaiting
        # state and caused peers to be disabled even when a chatroom existed.
        if route_id == "chatroom" and hasattr(self, "controller") and self.controller:
            if not get_active_code():
                self.controller.status_manager.update_status(AppConfig.STATUS_AWAITING_PEER)

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
        if getattr(self, "_status_callback_registered", False) and hasattr(self.controller, "status_manager"):
            try:
                self.controller.status_manager.unregister_status_callback(self._handle_status_update)  # type: ignore[attr-defined]
            except Exception:
                pass
        return super().destroy()

    def _clamp_sidebar_width(self, *_):
        """No-op; sidebar is fixed width."""
        return

    def _update_chatroom_label(self, code: str | None):
        if not hasattr(self, "chatroom_label"):
            return
        if code:
            formatted = format_chatroom_code(code)
            self.chatroom_label.configure(text=formatted, fg=Colors.TEXT_PRIMARY)
        else:
            self.chatroom_label.configure(text="No Chatroom", fg=Colors.TEXT_MUTED)
        # Disable peers when no chatroom
        if hasattr(self.sidebar, "_update_peer_access"):
            self.sidebar._update_peer_access(bool(code))

    def _handle_status_update(self, status_text: str, color: str):
        """Handle status updates; gate peers when not ready."""
        connected = False
        if status_text:
            lowered = status_text.lower()
            if any(keyword in lowered for keyword in AppConfig.STATUS_CONNECTED_KEYWORDS):
                connected = True
        badge_text = "Connected" if connected else "Not Connected"
        badge_bg = Colors.STATE_SUCCESS if connected else Colors.STATE_WARNING
        if hasattr(self, "status_badge") and self.status_badge.winfo_exists():
            self.status_badge.configure(text=badge_text, bg=badge_bg, fg=Colors.SURFACE)
        if hasattr(self.sidebar, "_update_peer_access") and status_text:
            is_ready = status_text.lower() in (kw.lower() for kw in AppConfig.STATUS_READY_KEYWORDS)
            has_chatroom = hasattr(self.sidebar, "_peers_enabled") and self.sidebar._peers_enabled
            self.sidebar._update_peer_access(is_ready and has_chatroom)

    def _register_top_listeners(self):
        """Register chat/chatroom listeners after layout creation."""
        if self._chatroom_listener:
            register_chatroom_listener(self._chatroom_listener)
        # Already registered status callback in layout creation

    def _register_status_listener(self):
        """Subscribe to status updates so the badge and peers react to transport changes."""
        if (
            getattr(self, "_status_callback_registered", False)
            or not hasattr(self, "controller")
            or not getattr(self.controller, "status_manager", None)
        ):
            return
        try:
            self.controller.status_manager.register_status_callback(self._handle_status_update)  # type: ignore[attr-defined]
            self._status_callback_registered = True
        except Exception:
            pass

    def refresh_header_info(self):
        """Refresh header labels from the current session (e.g., after name change)."""
        try:
            name = getattr(self.session, "local_device_name", "") or getattr(self.session, "device_name", "") or "Set name"
            if hasattr(self, "local_device_label") and self.local_device_label.winfo_exists():
                self.local_device_label.configure(text=name)
        except Exception:
            pass

    def apply_theme(self, *, prev_bg: dict | None = None, prev_fg: dict | None = None):
        """Refresh top-level theme without rebuilding the frame."""
        try:
            self.configure(bg=Colors.BG_MAIN)
            self.app.configure(bg=Colors.BG_MAIN)
        except Exception:
            pass

        for container in [self.content_frame, self.sidebar, getattr(self, "top_bar", None)]:
            if container:
                try:
                    container.configure(bg=Colors.BG_ELEVATED if container is self.top_bar else Colors.BG_MAIN)
                except Exception:
                    pass

        for container in self._view_containers.values():
            try:
                container.configure(bg=Colors.BG_MAIN)
            except Exception:
                pass

        if hasattr(self.sidebar, "refresh_theme"):
            self.sidebar.refresh_theme()
        try:
            from utils.chatroom_registry import get_active_code
            self._update_chatroom_label(get_active_code())
        except Exception:
            pass

        # Repaint existing widgets to new palette
        self._repaint_widget_tree(self, prev_bg or {}, prev_fg or {})

    def _repaint_widget_tree(self, widget, prev_bg: dict, prev_fg: dict):
        """Walk widget tree and update bg/fg when they match previous theme colors."""
        bg_map = {
            k: v
            for k, v in {
                prev_bg.get("BG_MAIN"): Colors.BG_MAIN,
                prev_bg.get("SURFACE"): Colors.SURFACE,
                prev_bg.get("SURFACE_ALT"): Colors.SURFACE_ALT,
                prev_bg.get("BG_ELEVATED"): Colors.BG_ELEVATED,
                prev_bg.get("BG_ELEVATED_2"): Colors.BG_ELEVATED_2,
            }.items()
            if k is not None
        }
        fg_map = {
            k: v
            for k, v in {
                prev_fg.get("TEXT_PRIMARY"): Colors.TEXT_PRIMARY,
                prev_fg.get("TEXT_SECONDARY"): Colors.TEXT_SECONDARY,
                prev_fg.get("TEXT_MUTED"): Colors.TEXT_MUTED,
            }.items()
            if k is not None
        }

        def _update_colors(target):
            # Skip ttk widgets that often reject direct bg/fg
            cls_name = target.winfo_class()
            if cls_name.startswith("T"):
                return
            try:
                current_bg = target.cget("bg")
                if current_bg in bg_map and bg_map[current_bg]:
                    target.configure(bg=bg_map[current_bg])
            except Exception:
                pass
            try:
                current_fg = target.cget("fg")
                if current_fg in fg_map and fg_map[current_fg]:
                    target.configure(fg=fg_map[current_fg])
            except Exception:
                pass

        _update_colors(widget)
        for child in widget.winfo_children():
            _update_colors(child)
            try:
                self._repaint_widget_tree(child, prev_bg, prev_fg)
            except Exception:
                continue

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
        if self.controller and getattr(self.controller, "status_manager", None):
            self.controller.status_manager.update_status(AppConfig.STATUS_READY)
        self.navigate_to("pair")

    def _handle_device_pairing(self, device_id: str, device_name: str):
        """Handle device pairing notifications from PeersPage."""
        if device_id and device_name:
            self.controller.status_manager.update_status(AppConfig.STATUS_CONNECTED)
            self.navigate_to("home")
        else:
            self.controller.status_manager.update_status(AppConfig.STATUS_DISCONNECTED)
