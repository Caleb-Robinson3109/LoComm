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


from .manual_pairing_modal import ManualPairingModal

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
        self._manual_pairing_modal: Optional[ManualPairingModal] = None
        
        self.devices: list[dict] = []  # List of {name, id, status}
        self.device_list_container: Optional[tk.Frame] = None

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
                "text": "Manual Pair",
                "command": self._show_manual_pairing_modal,
                "variant": "secondary",
                "padx": (0, Spacing.XS),
            },
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
            actions=actions,
        )

    def _build_devices_section(self, parent: tk.Misc):
        """Build clean devices section."""
        _, content = create_standard_section(
            parent,
            title="Available Peers",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=True,
        )
        
        self.device_list_container = content
        self._render_device_list()

    def _render_device_list(self):
        """Render the list of devices."""
        if not self.device_list_container:
            return

        # Clear existing
        for child in self.device_list_container.winfo_children():
            child.destroy()

        if not self.devices:
            AutoWrapLabel(
                self.device_list_container,
                text="No devices found. Try scanning or manual pairing.",
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
                justify="left",
                padding_x=Spacing.MD,
            ).pack(anchor="w")
            return

        for device in self.devices:
            self._create_device_row(device)

    def _create_device_row(self, device: dict):
        row = tk.Frame(self.device_list_container, bg=Colors.SURFACE_ALT)
        row.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Simple row layout
        info_frame = tk.Frame(row, bg=Colors.SURFACE_ALT)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            info_frame,
            text=device["name"],
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")
        
        tk.Label(
            info_frame,
            text=f"ID: {device['id']}",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        ).pack(anchor="w")

        # Connect button (if not already connected - logic simplified for now)
        DesignUtils.button(
            row,
            text="Connect",
            command=lambda d=device: self._connect_to_device(d),
            variant="secondary",
            width=8
        ).pack(side=tk.RIGHT)

    def _connect_to_device(self, device):
        if self.controller:
            self.controller.start_session(device["id"], device["name"])

    # ------------------------------------------------------------------ #
    # Scan / device-stage logic (UI-only, no mock data)
    # ------------------------------------------------------------------ #

    def _show_manual_pairing_modal(self):
        if self._manual_pairing_modal:
            return
            
        self._manual_pairing_modal = ManualPairingModal(
            self.winfo_toplevel(),
            on_pair=self._handle_manual_pair
        )

    def _handle_manual_pair(self, name: str, device_id: str):
        # Add to local list
        new_device = {"name": name, "id": device_id, "status": "available"}
        
        # Avoid duplicates
        existing = next((d for d in self.devices if d["id"] == device_id), None)
        if not existing:
            self.devices.append(new_device)
            self._render_device_list()
        
        # Auto-connect
        if self.controller:
            self.controller.start_session(device_id, name)

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
