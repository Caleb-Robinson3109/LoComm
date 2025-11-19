"""Peers page component matching chat-style design (production ready, no mock devices)."""
from __future__ import annotations

import tkinter as tk
from typing import Optional, Callable

from tkinter import messagebox

from utils.design_system import AppConfig, Colors, Typography, Spacing, DesignUtils
from utils.state.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from ui.helpers import (
    create_scroll_container,
    create_page_header,
    create_standard_section,
    AutoWrapLabel,
)
from .base_page import BasePage, PageContext
from .chat_page import ChatWindow


from .manual_pairing_window import ManualPairingWindow

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
        self._manual_pairing_window: Optional[ManualPairingWindow] = None
        
        self.devices: dict[str, dict] = {}  # Map of normalized id -> metadata
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
        self._refresh_from_session()

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
        # Standardized header with back button and Scan action
        actions = [
            {
                "text": "Manual Pair",
                "command": self._show_manual_pairing_modal,
                "variant": "secondary",
                "padx": (0, Spacing.XS),
            },
            {
                "text": "Scan",
                "command": self._scan_for_devices,
                "variant": "secondary",
            }
        ]

        create_page_header(
            parent,
            title="Peers",
            subtitle="Chat with your peers",
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

        devices = sorted(self.devices.values(), key=lambda d: d["name"].lower())
        if not devices:
            AutoWrapLabel(
                self.device_list_container,
                text="No peers yet. Use Scan or Manual Pair to add a device by ID.",
                bg=Colors.SURFACE,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            ).pack(fill=tk.X, pady=Spacing.SM)
            return

        for device in devices:
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
        
        meta_frame = tk.Frame(info_frame, bg=Colors.SURFACE_ALT)
        meta_frame.pack(fill=tk.X)

        tk.Label(
            meta_frame,
            text=f"ID: {device['display_id']}",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        ).pack(side=tk.LEFT, anchor="w")

        button_frame = tk.Frame(row, bg=Colors.SURFACE_ALT)
        button_frame.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        DesignUtils.button(
            button_frame,
            text="Chat",
            command=lambda d=device: self._chat_with_device(d),
            variant="primary",
            width=10,
        ).pack(anchor="e", pady=(0, Spacing.XXS))

    # ------------------------------------------------------------------ #
    # Device list management
    # ------------------------------------------------------------------ #

    def _normalize_device_identifier(self, device_id: str) -> str:
        return ''.join(ch for ch in (device_id or "") if ch.isalnum()).upper()

    def _format_device_identifier(self, device_id: str) -> str:
        normalized = self._normalize_device_identifier(device_id)
        if not normalized:
            return "UNKNOWN"
        return ' '.join(
            normalized[i:i + 4] for i in range(0, len(normalized), 4)
        )

    def _status_variant_for(self, status: str) -> str:
        mapping = {
            "available": "info",
            "connecting": "warning",
            "connected": "success",
            "disconnected": "danger",
        }
        return mapping.get(status.lower(), "info")

    def _upsert_device(self, name: str, device_id: str, *, status: str = "Available", source: str = "scan", render: bool = True) -> Optional[dict]:
        normalized = self._normalize_device_identifier(device_id)
        if not normalized:
            return None

        entry = self.devices.get(normalized)
        if entry is None:
            entry = {"raw_id": normalized}
            self.devices[normalized] = entry

        entry["name"] = (name or "").strip() or entry.get("name") or "Unnamed Device"
        entry["id"] = (device_id or "").strip() or normalized
        entry["raw_id"] = normalized
        entry["display_id"] = self._format_device_identifier(device_id or normalized)
        entry["status"] = status
        entry["status_variant"] = self._status_variant_for(status)
        entry["source"] = source

        if render:
            self._render_device_list()
        return entry

    def _update_device_status(self, device_id: str, status: str):
        normalized = self._normalize_device_identifier(device_id)
        entry = self.devices.get(normalized)
        if not entry:
            return
        entry["status"] = status
        entry["status_variant"] = self._status_variant_for(status)
        self._render_device_list()

    def _refresh_from_session(self):
        if self.session and getattr(self.session, "device_id", None) and getattr(self.session, "device_name", None):
            self._upsert_device(
                self.session.device_name,
                self.session.device_id,
                status="Connected",
                source="session",
                render=False,
            )

        controller = getattr(self, "controller", None)
        connection_manager = getattr(controller, "connection_manager", None) if controller else None
        if connection_manager:
            info = connection_manager.get_connected_device_info()
            if info and info.get("id") and info.get("name"):
                self._upsert_device(
                    info["name"],
                    info["id"],
                    status="Connected" if info.get("is_connected") else "Available",
                    source="session",
                    render=False,
                )

        # Always re-render to ensure placeholder visibility stays in sync
        self._render_device_list()

    def _connect_and_chat(self, device: dict):
        if not self.controller:
            self._open_chat_window(device)
            return

        self._update_device_status(device["raw_id"], "Connecting")

        def _callback(success: bool, error: Optional[str] = None):
            if success:
                self._update_device_status(device["raw_id"], "Connected")
                self._open_chat_window(device)
            elif error:
                self._update_device_status(device["raw_id"], "Available")
                messagebox.showerror("Connection Failed", error, parent=self.winfo_toplevel())
            else:
                self._update_device_status(device["raw_id"], "Available")

        self.controller.start_session(device["id"], device["name"], callback=_callback)

    def _chat_with_device(self, device: dict):
        session_device = getattr(self.session, "device_id", None) if self.session else None
        normalized_session = self._normalize_device_identifier(session_device or "")
        if normalized_session and normalized_session == device["raw_id"]:
            self._open_chat_window(device)
        else:
            self._connect_and_chat(device)

    def _open_chat_window(self, device: dict):
        master = self.winfo_toplevel()
        local_name = getattr(self.session, "local_device_name", "Orion") if self.session else "Orion"
        ChatWindow(
            master,
            peer_name=device["name"],
            local_device_name=local_name,
            on_close_callback=lambda raw=device["raw_id"]: self._handle_chat_closed(raw),
        )

    def _handle_chat_closed(self, raw_id: Optional[str] = None):
        if self.controller:
            self.controller.stop_session()
        if raw_id:
            normalized = self._normalize_device_identifier(raw_id)
            if normalized in self.devices:
                del self.devices[normalized]
                self._render_device_list()

    # ------------------------------------------------------------------ #
    # Scan / device-stage logic (UI-only, no mock data)
    # ------------------------------------------------------------------ #

    def _show_manual_pairing_modal(self):
        if self._manual_pairing_window:
            return
            
        self._manual_pairing_window = ManualPairingWindow(
            self.winfo_toplevel(),
            on_pair=self._handle_manual_pair
        )

    def _handle_manual_pair(self, name: str, device_id: str):
        entry = self._upsert_device(name, device_id, status="Available", source="manual")
        if entry:
            self._connect_and_chat(entry)

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
        self._refresh_from_session()

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
