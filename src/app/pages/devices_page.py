"""Pair page component for managing paired devices with modern layout."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.connection_manager import get_connection_manager
from utils.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from utils.ui_helpers import create_scroll_container
from mock.device_service import get_mock_device_service, MockDevice
from .base_page import BasePage, PageContext
from .pin_pairing_frame import PINPairingFrame


class DevicesPage(BasePage):
    """Devices page for managing device connections, PIN entry, and trust verification."""

    def __init__(self, master, context: PageContext, on_device_paired: Optional[Callable] = None):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.controller = context.controller if context else None
        self.session = context.session if context else None
        self.host = context.navigator if context else None
        self.on_device_paired = on_device_paired

        self.connection_manager = get_connection_manager()
        self.ui_store = get_ui_store()
        self.device_service = get_mock_device_service()
        self._device_subscription: Optional[Callable[[DeviceStatusSnapshot], None]] = None
        self.is_scanning = False
        self.connection_state = tk.StringVar(value="Ready to pair")
        self.status_var = tk.StringVar(value="No device paired yet. Select a device to get started.")
        self.selected_device_var = tk.StringVar(value="No device selected")
        self._active_device_name: Optional[str] = None
        self._active_device_id: Optional[str] = None
        self._pin_modal: Optional[tk.Toplevel] = None
        self._pin_modal_frame: Optional[PINPairingFrame] = None

        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(0, Spacing.LG))
        self.main_body = scroll.frame

        DesignUtils.hero_header(
            self.main_body,
            title="Devices",
            subtitle="Pair LoRa hardware, confirm PINs face-to-face, and monitor secure sessions."
        )
        self._build_body()
        self._apply_snapshot(self.ui_store.get_device_status())
        self._set_stage(DeviceStage.READY)

    def _build_body(self):
        body = tk.Frame(self.main_body, bg=Colors.SURFACE)
        body.pack(fill=tk.BOTH, expand=True)

        self._build_device_card(body)
        self._refresh_device_table()

    def _build_device_card(self, parent):
        card, content = DesignUtils.card(parent, "Scan & select hardware", "Choose the device you want to pair")
        card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.LG))
        card.pack_propagate(True)
        header_bar = tk.Frame(content, bg=Colors.SURFACE_ALT)
        header_bar.pack(fill=tk.X, pady=(0, Spacing.SM))
        tk.Label(
            header_bar,
            text="Available devices",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        ).pack(side=tk.LEFT)
        DesignUtils.button(
            header_bar,
            text="Scan",
            command=self._scan_for_devices,
            variant="primary"
        ).pack(side=tk.RIGHT)

        columns = ("Name", "Device ID", "Status")
        style = ttk.Style()
        style.configure(
            "Devices.Treeview",
            background=Colors.SURFACE_ALT,
            fieldbackground=Colors.SURFACE_ALT,
            foreground=Colors.TEXT_PRIMARY,
            rowheight=30,
            bordercolor=Colors.SURFACE_ALT,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        )
        style.configure(
            "Devices.Treeview.Heading",
            background=Colors.SURFACE_HEADER,
            foreground=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
        )
        style.map(
            "Devices.Treeview",
            background=[("selected", Colors.SURFACE_HEADER)],
            foreground=[("selected", Colors.TEXT_PRIMARY)],
        )

        self.device_tree = ttk.Treeview(
            content,
            columns=columns,
            show="headings",
            height=10,
            style="Devices.Treeview",
        )
        for col, width in zip(columns, (220, 180, 140)):
            self.device_tree.heading(col, text=col, anchor="w")
            self.device_tree.column(col, anchor="w", width=width, stretch=True)
        self.device_tree.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=(Spacing.SM, 0))
        self.device_tree.bind("<<TreeviewSelect>>", self._on_device_select)

        controls = tk.Frame(content, bg=Colors.SURFACE_ALT)
        controls.pack(fill=tk.X, pady=(Spacing.SM, 0))
        button_group = tk.Frame(controls, bg=Colors.SURFACE_ALT)
        button_group.pack(side=tk.RIGHT)
        self.disconnect_btn = DesignUtils.button(button_group, text="Disconnect", command=self._disconnect_device, variant="danger")
        self.disconnect_btn.pack(side=tk.RIGHT, padx=(Spacing.XS, 0))
        self.disconnect_btn.configure(state="disabled")
        self.connect_btn = DesignUtils.button(button_group, text="Connect", command=self._connect_selected_device, variant="secondary")
        self.connect_btn.pack(side=tk.RIGHT)
        self.connect_btn.configure(state="disabled")

    def _refresh_device_table(self):
        if not hasattr(self, "device_tree"):
            return
        for row in self.device_tree.get_children():
            self.device_tree.delete(row)
        devices = self.device_service.list_devices()
        for device in devices:
            self.device_tree.insert("", tk.END, iid=device.device_id, values=device.to_table_row())
        if not devices:
            self.status_var.set("No mock devices defined. Edit mock/data/devices.json to add entries.")

    # ------------------------------------------------------------------ #
    def _scan_for_devices(self):
        if self.is_scanning:
            return
        self.is_scanning = True
        self._set_stage(DeviceStage.SCANNING)
        self.after(2000, self._finish_scan)  # TODO: Make scan duration configurable

    def _finish_scan(self):
        newly_found = self.device_service.simulate_scan()
        if not newly_found:
            self.device_service.refresh()
        self._refresh_device_table()
        if newly_found:
            self.status_var.set(f"Discovered {len(newly_found)} new devices.")
        self._set_stage(DeviceStage.READY)
        self.is_scanning = False

    def _connect_selected_device(self):
        selected = self.device_tree.selection()
        if not selected:
            self._set_stage(DeviceStage.READY)
            return
        node_id = selected[0]
        device = self.device_service.get_device(node_id)
        if not device:
            return
        device_id = device.device_id
        name = device.name
        self._active_device_name = name
        self._active_device_id = device_id
        self.selected_device_var.set(f"{name} ({device_id})")

        self._set_stage(DeviceStage.AWAITING_PIN, name)
        self._open_pin_modal(device_id, name)

    def _handle_pin_pair_success(self, device_id: str, device_name: str):
        self._set_stage(DeviceStage.CONNECTING, device_name)
        if self.app:
            self.app.start_transport_session(device_id, device_name)
        self._set_stage(DeviceStage.CONNECTED, device_name)
        self._close_pin_modal()
        if self.on_device_paired:
            self.on_device_paired(device_id, device_name)
        navigator = getattr(self, "navigator", None)
        if navigator and hasattr(navigator, "show_chat_page"):
            navigator.show_chat_page()

    def _disconnect_device(self):
        if not self.connection_manager.is_connected():
            self.status_var.set("No device connected")
            return
        if self.controller:
            self.controller.stop_session()
        if self.app:
            self.app.clear_chat_history()
        self.connection_manager.disconnect_device()
        last_device = self.selected_device_var.get()
        label = last_device if last_device != "No device selected" else None
        self._set_stage(DeviceStage.DISCONNECTED, label)

    def _handle_demo_login(self):
        self._set_stage(DeviceStage.CONNECTING, "Demo Device")
        if self.app:
            self.app.start_transport_session("demo-device", "Demo Device", mode="demo")
        self._set_stage(DeviceStage.CONNECTED, "Demo Device")
        self._close_pin_modal()
        if self.on_device_paired:
            self.on_device_paired("demo-device", "Demo Device")

    def _on_device_select(self, _event):
        if not self.device_tree.selection():
            self.connect_btn.configure(state="disabled")
            return
        selection = self.device_tree.selection()[0]
        device = self.device_service.get_device(selection)
        if not device:
            return
        self.selected_device_var.set(f"{device.name} ({device.device_id})")
        self.connect_btn.configure(state="normal")

    def _open_pin_modal(self, device_id: str, device_name: str):
        self._close_pin_modal()
        modal = tk.Toplevel(self)
        modal.title(f"Pair {device_name}")
        modal.configure(bg=Colors.SURFACE)
        modal.geometry("720x640")
        modal.resizable(True, True)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()
        modal.protocol("WM_DELETE_WINDOW", self._close_pin_modal)
        self._pin_modal = modal

        pin_frame = PINPairingFrame(
            modal,
            lambda d_id, d_name: self._handle_pin_pair_success(d_id, d_name),
            self._handle_demo_login
        )
        pin_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.MD, pady=Spacing.MD)
        if hasattr(pin_frame, "set_pending_device"):
            pin_frame.set_pending_device(device_name, device_id)
        if hasattr(pin_frame, "focus_input"):
            pin_frame.focus_input()
        self._pin_modal_frame = pin_frame

    def _close_pin_modal(self):
        self._pin_modal_frame = None
        if self._pin_modal and self._pin_modal.winfo_exists():
            try:
                self._pin_modal.destroy()
            except Exception:
                pass
        self._pin_modal = None

    def _set_stage(self, stage: DeviceStage, device_name: Optional[str] = None):
        """Update local labels and push consolidated status via the UI store."""
        label = device_name or self._active_device_name
        self.ui_store.set_pairing_stage(stage, label)
        snapshot = self.ui_store.get_device_status()
        self._apply_snapshot(snapshot)
        if label:
            self.selected_device_var.set(label)
            self._active_device_name = label
        if stage == DeviceStage.READY:
            self.selected_device_var.set("No device selected")
            self._active_device_name = None
            self._active_device_id = None
        if hasattr(self, "disconnect_btn"):
            self.disconnect_btn.configure(state="normal" if stage == DeviceStage.CONNECTED else "disabled")
        if self._active_device_id:
            device = self.device_service.get_device(self._active_device_id)
            if device:
                self.selected_device_var.set(f"{device.name} ({device.device_id})")

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
        if not snapshot:
            return
        self.connection_state.set(snapshot.title)
        detail_text = snapshot.detail or snapshot.subtitle or ""
        self.status_var.set(detail_text)
        if snapshot.stage == DeviceStage.READY:
            self.selected_device_var.set("No device selected")
            self._active_device_name = None
        elif snapshot.device_name:
            self.selected_device_var.set(snapshot.device_name)
            self._active_device_name = snapshot.device_name

        # Update disconnect button state based on connection status
        is_connected = snapshot.stage == DeviceStage.CONNECTED
        if hasattr(self, "disconnect_btn"):
            self.disconnect_btn.configure(state="normal" if is_connected else "disabled")

    def destroy(self):
        self._unsubscribe_from_store()
        return super().destroy()


# Backwards compatibility
PairPage = DevicesPage
