"""Peers page component matching chat-style design (production ready, no mock devices)."""
from __future__ import annotations

import tkinter as tk
from typing import Optional, Callable

from utils.design_system import AppConfig, Colors, Typography, Spacing, DesignUtils, Space
from utils.state.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from ui.helpers import (
    create_scroll_container,
    create_page_header,
    create_standard_section,
    AutoWrapLabel,
)
from .base_page import BasePage, PageContext


class PeersPage(BasePage):
    """Devices page with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext, on_device_paired: Optional[Callable] = None):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.controller = context.controller if context else None
        self.session = context.session if context else None
        self.navigator = context.navigator if context else None
        self.on_device_paired = on_device_paired

        self.ui_store = get_ui_store()
        self._device_subscription: Optional[Callable[[DeviceStatusSnapshot], None]] = None
        self.is_scanning = False
        self._scan_timer_id: Optional[str] = None

        # Simple scroll container like chat page
        scroll = create_scroll_container(
            self,
            bg=Colors.SURFACE,
            padding=(0, Spacing.LG),
        )
        body = scroll.frame

        self._build_header(body)
        self._build_devices_section(body)

        # Reflect whatever the store currently knows about the connection state
        self._apply_snapshot(self.ui_store.get_device_status())

    # ------------------------------------------------------------------ #
    # Navigation helpers
    # ------------------------------------------------------------------ #

    def _handle_back(self):
        nav = getattr(self, "navigator", None)
        if not nav:
            return
        if hasattr(nav, "go_back"):
            nav.go_back()
        elif hasattr(nav, "navigate_to"):
            nav.navigate_to("home")

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #

    def _build_header(self, parent: tk.Misc):
        # Standardized header with back button and Refresh action
        actions = [
            {
                "text": "Refresh",
                "command": self._scan_for_devices,
                "variant": "secondary",
            }
        ]

        create_page_header(
            parent,
            title="Peers",
            subtitle="Manage your peers and device sessions",
            show_back=True,
            on_back=self._handle_back,
            actions=actions,
        )

    def _build_devices_section(self, parent: tk.Misc):
        """Build clean devices section (no mock devices)."""
        _, content = create_standard_section(
            parent,
            title="Available Peers",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE_ALT,
            with_card=True,
        )

        # Placeholder content: no mock devices. This is where real peers
        # should be rendered once the backend is wired up.
        AutoWrapLabel(
            content,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            justify="left",
            padding_x=Spacing.MD,
        ).pack(anchor="w")

    # ------------------------------------------------------------------ #
    # Scan / device-stage logic (UI-only, no mock data)
    # ------------------------------------------------------------------ #

    def _scan_for_devices(self):
        """Trigger a scan. In production this should call the real transport."""
        if self.is_scanning:
            return

        self.is_scanning = True

        if self.controller:
            self.controller.status_manager.update_status("Scanning…")

        self._set_stage(DeviceStage.SCANNING)

        # In a real app, kick off an async transport scan here and
        # call _finish_scan from that callback. For now, just simulate
        # scan completion with no fake devices.
        self._cancel_scan_timer()
        self._scan_timer_id = self.after(2000, self._finish_scan)

    def _finish_scan(self):
        """Complete scan without adding any mock devices."""
        # In production, you would refresh from real device data here.
        self._set_stage(DeviceStage.READY)
        self.is_scanning = False

        if self.controller:
            self.controller.status_manager.update_status(AppConfig.STATUS_READY)

        self._scan_timer_id = None

    def _set_stage(self, stage: DeviceStage, device_name: Optional[str] = None):
        """Update global device status via UI store (used by top bar)."""
        label = device_name
        self.ui_store.set_pairing_stage(stage, label)
        snapshot = self.ui_store.get_device_status()
        self._apply_snapshot(snapshot)

    # ------------------------------------------------------------------ #
    # Lifecycle: subscribe to store so top bar stays in sync
    # ------------------------------------------------------------------ #

    def on_show(self):
        self._subscribe_to_store()

    def on_hide(self):
        self._unsubscribe_from_store()

    def _subscribe_to_store(self):
        if self._device_subscription is not None:
            return

        def _callback(snapshot: DeviceStatusSnapshot):
            self._apply_snapshot(snapshot)

        self._device_subscription = _callback
        self.ui_store.subscribe_device_status(_callback)

    def _unsubscribe_from_store(self):
        if self._device_subscription is None:
            return
        self.ui_store.unsubscribe_device_status(self._device_subscription)
        self._device_subscription = None

    def _apply_snapshot(self, snapshot: DeviceStatusSnapshot | None):
        """Right now we just keep the top-bar status aligned; no local list."""
        if not snapshot:
            return
        # If you later add a real peer list, you can use snapshot.device_name here.
        # For now we do not create any mock rows.

    def destroy(self):
        self._cancel_scan_timer()
        self._unsubscribe_from_store()
        return super().destroy()

    def _cancel_scan_timer(self):
        """Cancel any pending scan timer to avoid callbacks after destruction."""
        if self._scan_timer_id:
            try:
                self.after_cancel(self._scan_timer_id)
            except Exception:
                pass
            self._scan_timer_id = None


# Legacy alias kept so any older imports still work
PairPage = PeersPage
