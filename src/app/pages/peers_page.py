"""Peers page component matching chat-style design (production ready, no mock devices)."""
from __future__ import annotations

import tkinter as tk
from typing import Optional, Callable

from tkinter import messagebox
import threading
import sys
import os

from utils.design_system import AppConfig, Colors, Typography, Spacing, DesignUtils
from ui.helpers import (
    create_scroll_container,
    create_page_header,
    create_standard_section,
    AutoWrapLabel,
)
from .base_page import BasePage, PageContext
from .chat_window import ChatWindow


from .manual_pair_window import ManualPairingWindow
from utils.chatroom_registry import get_active_code, register_chatroom_listener, unregister_chatroom_listener

# Ensure API module path is available
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api")))
try:
    from LoCommAPI import locomm_api_scan as scan_for_devices
except Exception:
    scan_for_devices = None

class PeersPage(BasePage):
    """Devices page with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext, on_device_paired: Optional[Callable] = None):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.controller = context.controller if context else None
        self.session = context.session if context else None
        self.navigator = context.navigator if context else None
        self.on_device_paired = on_device_paired

        self.is_scanning = False
        self._scan_timer_id: Optional[str] = None
        self._manual_pairing_window: Optional[ManualPairingWindow] = None
        self._chatroom_listener: Optional[Callable[[str | None], None]] = None
        self._chatroom_code: Optional[str] = get_active_code()

        self.devices: dict[str, dict] = {}  # Map of normalized id -> metadata
        self.device_list_container: Optional[tk.Frame] = None
        self._enter_binding_id: Optional[str] = None

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
        # Local binding so Enter works when focus is within this page
        self.bind("<Return>", self._handle_enter_key, add="+")

        self._register_chatroom_listener()

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
                "text": "Manual",
                "command": self._show_manual_pairing_modal,
                "variant": "primary",
                "width": 6,
                "padx": (0, Spacing.XS),
            },
            {
                "text": "Scan",
                "command": self._scan_for_devices,
                "variant": "secondary",
                "width": 6,
            }
        ]

        create_page_header(
            parent,
            title="Peers",
            subtitle="Chat with your peers",
            actions=actions,
            padx=Spacing.LG,
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
        row = tk.Frame(self.device_list_container, bg=Colors.SURFACE_ALT, padx=Spacing.SM, pady=Spacing.XS)
        row.pack(fill=tk.X, pady=(0, Spacing.SM))

        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)
        row.grid_columnconfigure(2, weight=0)

        name_label = tk.Label(
            row,
            text=device["name"],
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
        )
        name_label.grid(row=0, column=0, sticky="w")

        id_label = tk.Label(
            row,
            text=device['display_id'],
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        )
        id_label.grid(row=0, column=1, sticky="w", padx=(Spacing.SM, 0))

        chat_btn = DesignUtils.button(
            row,
            text="Chat",
            command=lambda d=device: self._chat_with_device(d),
            variant="primary",
            width=6,
        )
        chat_btn.grid(row=0, column=2, sticky="e", padx=(Spacing.SM, 0))

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
        # Only repopulate peers when a chatroom is active
        if not get_active_code():
            self.devices.clear()
            self._render_device_list()
            return

        session_device_id = getattr(self.session, "device_id", None) if self.session else None
        session_device_name = getattr(self.session, "device_name", None) if self.session else None
        if session_device_id and session_device_name:
            self._upsert_device(
                session_device_name,
                session_device_id,
                status="Connected",
                source="session",
                render=False,
            )
            info = None
        else:
            controller = getattr(self, "controller", None)
            connection_manager = getattr(controller, "connection_manager", None) if controller else None
            info = None
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

        if not get_active_code():
            messagebox.showinfo("Chatroom Required", "Join or create a chatroom before pairing with peers.")
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

        # Avoid tearing down an existing transport; reuse if already connected
        try:
            self.controller.start_session(device["id"], device["name"], callback=_callback)
        except Exception:
            self._update_device_status(device["raw_id"], "Available")


    def _chat_with_device(self, device: dict):
        session_device = getattr(self.session, "device_id", None) if self.session else None
        normalized_session = self._normalize_device_identifier(session_device or "")
        if normalized_session and normalized_session == device["raw_id"]:
            self._open_chat_window(device)
        else:
            self._connect_and_chat(device)

    def _open_chat_window(self, device: dict):
        master = self.winfo_toplevel()
        local_name = ""
        if self.session:
            local_name = getattr(self.session, "local_device_name", "") or getattr(self.session, "device_name", "") or ""
        receiver_id = device.get("raw_id")
        
        def on_peer_name_changed(new_name: str):
            device["name"] = new_name
            self._render_device_list()
        
        ChatWindow(
            master,
            peer_name=device["name"],
            peer_id=device.get("raw_id"),
            local_device_name=local_name,
            on_close_callback=lambda raw=device["raw_id"]: self._handle_chat_closed(raw),
            on_send_callback=lambda text, rid=receiver_id: self._send_chat_message(text, rid),
            on_peer_name_changed=on_peer_name_changed,
        )

    def _handle_chat_closed(self, raw_id: Optional[str] = None):
        # Keep transport alive and retain device entry; mark as available
        if raw_id:
            normalized = self._normalize_device_identifier(raw_id)
            if normalized in self.devices:
                self._update_device_status(normalized, "Available")

    def _send_chat_message(self, text: str, receiver_id: str | None = None) -> bool:
        """Relay chat message through controller transport."""
        if self.controller:
            try:
                self.controller.send_message(text, receiver_id)
                return True
            except Exception:
                messagebox.showerror("Send Failed", "Unable to send message to device.", parent=self.winfo_toplevel())
                return False
        return False

    # ------------------------------------------------------------------ #
    # Scan / device-stage logic (UI-only, no mock data)
    # ------------------------------------------------------------------ #

    def _show_manual_pairing_modal(self):
        if not get_active_code():
            messagebox.showinfo("Chatroom Required", "Join or create a chatroom before pairing with peers.")
            return
        if self._manual_pairing_window:
            scaffold = getattr(self._manual_pairing_window, "window_scaffold", None)
            if scaffold and getattr(scaffold, "toplevel", None) and scaffold.toplevel.winfo_exists():
                scaffold.toplevel.lift()
                scaffold.toplevel.focus_force()
                return

        def _clear_window():
            self._manual_pairing_window = None

        self._manual_pairing_window = ManualPairingWindow(
            self.winfo_toplevel(),
            on_pair=self._handle_manual_pair,
            on_close=_clear_window,
        )

    def _handle_manual_pair(self, name: str, device_id: str):
        if not get_active_code():
            return
        entry = self._upsert_device(name, device_id, status="Available", source="manual")
        if entry:
            self._connect_and_chat(entry)

    def _scan_for_devices(self):
        """Trigger a scan. In production this should call the real transport."""
        if self.is_scanning:
            return

        if not get_active_code():
            messagebox.showinfo("Chatroom Required", "Join or create a chatroom before scanning for peers.")
            return

        if scan_for_devices is None:
            messagebox.showinfo("Scan Unavailable", "Device scan API is not available in this build.", parent=self.winfo_toplevel())
            return

        self.is_scanning = True

        if self.controller:
            self.controller.status_manager.update_status("Scanning…")

        def _worker():
            try:
                print("Calling scan_for_devices")
                devices = scan_for_devices() or []
                print("Finished scan_for_devices call")
            except Exception as e:
                print("exception occured with scan_for_devices call")
                print(e)
                devices = []
            self.after(0, lambda: self._finish_scan(devices))

        threading.Thread(target=_worker, daemon=True).start()

    def _finish_scan(self, devices: list[tuple[str, int]] | None = None):
        """Complete scan and populate device list."""
        devices = devices or []
        print(f"Finished Scan, devices = {devices}")

        # Get normalized device IDs from scan results
        scanned_ids = [str(device_id) for name, device_id in devices]
        
        # Keep only entries that match scanned device IDs
        print(f"scanned IDs: {scanned_ids}")
        print(f"already existing IDs: {[v['id'] for k, v, in self.devices.items()]}")
        #print(scanned_ids[0] == self.devices.items()[0][1]['id'])
        #print(f"{scanned_ids[0]}, {self.devices.items()[0][1]['id']}")
        self.devices = {k: v for k, v in self.devices.items() if str(v['id']) in scanned_ids}
        self._render_device_list()
        
        # Add/update scan results
        alreadyExistingIds = list([str(v['id']) for k, v, in self.devices.items()])
        print(f"already existing IDS before upsert: {alreadyExistingIds}")
        for name, device_id in devices:
            if str(device_id) == "255": continue
            if str(device_id) in alreadyExistingIds:
                print("found duplicate id")
                continue
            else:
                print("found new id")
            print(f"Inserting device with name {name}")
            self._upsert_device(name, str(device_id), status="Available", source="scan", render=False)

        self._render_device_list()

        self.is_scanning = False

        if self.controller:
            self.controller.status_manager.update_status(AppConfig.STATUS_READY)

        self._scan_timer_id = None
        #self._refresh_from_session()

    def _register_chatroom_listener(self):
        if self._chatroom_listener is not None:
            return

        def _listener(code: str | None):
            # Clear peers whenever chatroom is cleared or changed
            normalized_new = (code or "").strip()
            if normalized_new != (self._chatroom_code or ""):
                self._chatroom_code = normalized_new or None
                self.devices.clear()
                self._render_device_list()
                # Also close any open manual pairing window when chatroom changes
                if self._manual_pairing_window:
                    try:
                        self._manual_pairing_window.close()
                    except Exception:
                        pass
                    self._manual_pairing_window = None

        self._chatroom_listener = _listener
        register_chatroom_listener(self._chatroom_listener)

    # Lifecycle hooks to manage key bindings
    def on_show(self):
        """Bind Enter key to open manual pairing when this page is visible."""
        toplevel = self.winfo_toplevel()
        if self._enter_binding_id is None and toplevel:
            self._enter_binding_id = toplevel.bind("<Return>", self._handle_enter_key, add="+")

    def on_hide(self):
        """Unbind page-specific shortcuts when hidden."""
        toplevel = self.winfo_toplevel()
        if self._enter_binding_id and toplevel:
            try:
                toplevel.unbind("<Return>", self._enter_binding_id)
            except Exception:
                pass
            self._enter_binding_id = None

    def _handle_enter_key(self, event=None):
        """Open manual pairing modal when Enter is pressed on this page."""
        # Only act if this page is currently visible
        if not self.winfo_ismapped():
            return
        self._show_manual_pairing_modal()

    def destroy(self):
        self._cancel_scan_timer()
        if self._chatroom_listener:
            unregister_chatroom_listener(self._chatroom_listener)
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
