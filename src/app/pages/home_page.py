"""Home page matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, DesignUtils, Spacing, Typography, Space
from ui.helpers import create_scroll_container
from utils.state.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from .base_page import BasePage, PageContext


class HomePage(BasePage):
    """Home page with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.session = context.session if context else None
        self.host = context.navigator if context else None
        self.ui_store = get_ui_store()
        self._device_subscription = None

        self.connection_title_var = tk.StringVar(value="No device paired")
        self.connection_subtitle_var = tk.StringVar(value="Start by pairing a LoRa contact to open a secure chat.")
        self.connection_detail_var = tk.StringVar(value="Awaiting secure PIN handoff")

        # Simple scroll container like chat page
        scroll = create_scroll_container(
            self, 
            bg=Colors.SURFACE, 
            padding=(0, Spacing.LG)
        )
        body = scroll.frame

        self._build_title(body)
        self._build_status_section(body)
        self._build_action_section(body)
        
        # Apply the latest snapshot immediately so the UI reflects the current store state.
        self._apply_snapshot(self.ui_store.get_device_status())

    def _build_title(self, parent):
        """Build simple title section like chat page."""
        title_wrap = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
        )
        title_wrap.pack(fill=tk.X, pady=(0, Space.XS))

        tk.Label(
            title_wrap,
            text="Welcome to Locomm",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")

        tk.Label(
            title_wrap,
            text="Secure LoRa messaging for desktop",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

    def _build_status_section(self, parent):
        """Build simple content area like chat page."""
        content = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Space.LG,
            pady=Space.MD,
        )
        content.pack(fill=tk.BOTH, expand=True)
    
    def _build_status_section(self, parent):
        """Build clean status section."""
        status_frame = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        status_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        
        # Status title
        tk.Label(
            status_frame,
            text="Connection Status",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
            padx=Space.MD,
            pady=Space.SM,
        ).pack(anchor="w")
        
        # Status content
        content_frame = tk.Frame(status_frame, bg=Colors.SURFACE_ALT)
        content_frame.pack(fill=tk.X, padx=Space.MD, pady=(0, Space.MD))
        
        tk.Label(
            content_frame,
            textvariable=self.connection_title_var,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")
        
        tk.Label(
            content_frame,
            textvariable=self.connection_subtitle_var,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))
        
        tk.Label(
            content_frame,
            textvariable=self.connection_detail_var,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            justify="left",
        ).pack(anchor="w")
    
    def _build_action_section(self, parent):
        """Build simple action section."""
        action_frame = tk.Frame(parent, bg=Colors.SURFACE)
        action_frame.pack(fill=tk.X, pady=(0, Space.LG))
        
        # Action button
        DesignUtils.button(
            action_frame,
            text="Start Pairing",
            command=self._go_to_devices,
            variant="primary",
        ).pack(anchor="w", pady=(Space.SM, 0))

    def _go_to_devices(self):
        if self.host and hasattr(self.host, "show_pair_page"):
            self.host.show_pair_page()

    def on_show(self):
        """Start listening to store updates when the page is visible."""
        self._subscribe_to_store()

    def on_hide(self):
        """Stop expensive updates when the page is hidden."""
        self._unsubscribe_from_store()

    # ------------------------------------------------------------------ #
    def _subscribe_to_store(self):
        if self._device_subscription is not None:
            return

        def _callback(snapshot: DeviceStatusSnapshot):
            self._handle_device_snapshot(snapshot)

        self._device_subscription = _callback
        self.ui_store.subscribe_device_status(_callback)

    def _unsubscribe_from_store(self):
        if self._device_subscription is None:
            return
        self.ui_store.unsubscribe_device_status(self._device_subscription)
        self._device_subscription = None

    def _handle_device_snapshot(self, snapshot: DeviceStatusSnapshot):
        self._apply_snapshot(snapshot)

    def _apply_snapshot(self, snapshot: DeviceStatusSnapshot | None):
        if snapshot is None:
            return
        
        self.connection_title_var.set(snapshot.title or "No device paired")
        self.connection_subtitle_var.set(snapshot.subtitle or "Start by pairing a LoRa contact to open a secure chat.")
        self.connection_detail_var.set(snapshot.detail or "Awaiting secure PIN handoff")

    def destroy(self):
        self._unsubscribe_from_store()
        return super().destroy()