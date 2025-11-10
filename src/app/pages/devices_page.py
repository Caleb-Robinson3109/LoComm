"""Pair page component matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from utils.design_system import Colors, Typography, Spacing, DesignUtils, Space
from utils.state.connection_manager import get_connection_manager
from utils.state.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from ui.helpers import create_scroll_container
from utils.window_sizing import scale_dimensions
from mock.device_service import get_mock_device_service, MockDevice
from .base_page import BasePage, PageContext
from .pin_pairing_frame import PINPairingFrame


class DevicesPage(BasePage):
    """Devices page with chat-style clean, simple design."""

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
        self.selected_device_var = tk.StringVar(value="No device selected")
        self._active_device_name: Optional[str] = None
        self._active_device_id: Optional[str] = None
        self._pin_modal: Optional[tk.Toplevel] = None
        self._pin_modal_frame: Optional[PINPairingFrame] = None
        self._suppress_selection_event = False
        self._last_selected_id: Optional[str] = None

        # Simple scroll container like chat page
        scroll = create_scroll_container(
            self, 
            bg=Colors.SURFACE, 
            padding=(0, Spacing.LG)
        )
        body = scroll.frame

        self._build_title(body)
        self._build_devices_section(body)

        # Reflect whatever the store currently knows about the connection state
        self._apply_snapshot(self.ui_store.get_device_status())

    def _build_title(self, parent):
        """Build simple title section like chat page."""
        title_wrap = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
        )
        title_wrap.pack(fill=tk.X, pady=(0, Space.XS))

        text_wrap = tk.Frame(title_wrap, bg=Colors.SURFACE)
        text_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)

        action_wrap = tk.Frame(title_wrap, bg=Colors.SURFACE)
        action_wrap.pack(side=tk.RIGHT)

        tk.Label(
            text_wrap,
            text="Devices",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")

        tk.Label(
            text_wrap,
            text="Pair LoRa hardware, confirm PINs face-to-face",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

        DesignUtils.button(
            action_wrap,
            text="Scan",
            variant="primary",
            command=self._scan_for_devices,
        ).pack()

    def _build_devices_section(self, parent):
        """Build clean devices section."""
        content = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Space.LG,
            pady=Space.MD,
        )
        content.pack(fill=tk.BOTH, expand=True)
        
        # Section title
        tk.Label(
            content,
            text="Available Devices",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        ).pack(anchor="w", pady=(0, Spacing.SM))
        
        # Device list
        list_frame = tk.Frame(content, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.MD)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, Space.SM))
        
        self._build_device_list(list_frame)
        
        # Action buttons
        self._build_action_buttons(content)

    def _build_device_list(self, parent):
        """Build simple device list."""
        # Configure treeview style
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

        # Create treeview
        columns = ("Name", "Device ID", "Status")
        self.device_tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            height=8,
            style="Devices.Treeview",
        )
        column_width = 180
        column_minwidth = 140
        for col in columns:
            self.device_tree.heading(col, text=col, anchor="center")
            self.device_tree.column(
                col,
                anchor="center",
                width=column_width,
                minwidth=column_minwidth,
                stretch=True,
            )
        self.device_tree.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, Spacing.SM))
        self.device_tree.bind("<<TreeviewSelect>>", self._on_device_select)
        
        # Populate devices
        self._refresh_device_table()

    def _build_action_buttons(self, parent):
        """Build simple action buttons."""
        button_frame = tk.Frame(parent, bg=Colors.SURFACE)
        button_frame.pack(fill=tk.X)
        spacer = tk.Frame(button_frame, bg=Colors.SURFACE)
        spacer.pack(side=tk.LEFT, expand=True, fill=tk.X)

        btn_width = 12
        self.connect_btn = DesignUtils.button(
            button_frame,
            text="Connect",
            command=self._connect_selected_device,
            variant="secondary",
            width=btn_width,
        )
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
        if devices:
            # Re-select previous device if still present
            target = self._last_selected_id if self._last_selected_id in self.device_tree.get_children() else devices[0].device_id
            self._select_device_in_tree(target)

    # ------------------------------------------------------------------ #
    def _scan_for_devices(self):
        if self.is_scanning:
            return
        self.is_scanning = True
        if hasattr(self, "scan_btn"):
            self.scan_btn.configure(state="disabled", text="Scanning…")
        self._set_stage(DeviceStage.SCANNING)
        self.after(2000, self._finish_scan)  # TODO: Make scan duration configurable

    def _finish_scan(self):
        newly_found = self.device_service.simulate_scan()
        if not newly_found:
            self.device_service.refresh()
        self._refresh_device_table()
        self._set_stage(DeviceStage.READY)
        self.is_scanning = False
        if hasattr(self, "scan_btn"):
            self.scan_btn.configure(state="normal", text="Scan for Devices")

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
        self._close_pin_modal()

    def _disconnect_device(self):
        if not self.connection_manager.is_connected():
            return
        if self.controller:
            self.controller.stop_session()
        if self.app:
            self.app.clear_chat_history(confirm=False)
        self.connection_manager.disconnect_device()
        last_device = self.selected_device_var.get()
        label = last_device if last_device != "No device selected" else None
        self._set_stage(DeviceStage.DISCONNECTED, label)

    def _handle_demo_login(self):
        label = self._active_device_name or self.selected_device_var.get()
        if label == "No device selected" or not label:
            label = "Demo Device"
        self._set_stage(DeviceStage.CONNECTING, label)
        if self.app:
            self.app.start_transport_session("demo-device", label, mode="demo")
        self._set_stage(DeviceStage.CONNECTED, label)
        self._close_pin_modal()
        if self.on_device_paired:
            self.on_device_paired("demo-device", label)

    def _on_device_select(self, _event=None):
        if self._suppress_selection_event:
            return
        if not self.device_tree.selection():
            self.connect_btn.configure(state="disabled")
            return
        selection = self.device_tree.selection()[0]
        device = self.device_service.get_device(selection)
        if not device:
            return
        self.selected_device_var.set(f"{device.name} ({device.device_id})")
        self._active_device_name = device.name
        self._active_device_id = device.device_id
        self._last_selected_id = device.device_id
        self._sync_connect_button_state()

    def _open_pin_modal(self, device_id: str, device_name: str):
        self._close_pin_modal()
        modal = tk.Toplevel(self)
        modal.title(f"Pair {device_name} - {device_id}")
        modal.configure(bg=Colors.SURFACE)
        base_width, base_height = scale_dimensions(432, 378, 0.93, 0.75)
        width = max(int(base_width * 1.08), 320)
        height = max(int(base_height * 1.06), 340)
        modal.geometry(f"{width}x{height}")
        modal.minsize(width, height)
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
            if not self._last_selected_id:
                self.selected_device_var.set("No device selected")
            self._active_device_name = None
            self._active_device_id = None
        self._sync_connect_button_state()
        if stage in (DeviceStage.DISCONNECTED, DeviceStage.READY):
            if self._last_selected_id:
                self._select_device_in_tree(self._last_selected_id)
        if self._active_device_id:
            device = self.device_service.get_device(self._active_device_id)
            if device:
                self.selected_device_var.set(f"{device.name} ({device.device_id})")
                self._select_device_in_tree(device.device_id)

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
        if snapshot.stage == DeviceStage.READY:
            self.selected_device_var.set("No device selected")
            self._active_device_name = None
        elif snapshot.device_name:
            self.selected_device_var.set(snapshot.device_name)
            self._active_device_name = snapshot.device_name

        # Update disconnect button state based on connection status
        is_connected = snapshot.stage == DeviceStage.CONNECTED
        self._sync_connect_button_state()

    def _sync_connect_button_state(self):
        if not hasattr(self, "connect_btn"):
            return
        if not hasattr(self, "device_tree"):
            self.connect_btn.configure(state="disabled")
            return
        selection = self.device_tree.selection()
        if not selection:
            self.connect_btn.configure(state="disabled")
            return
        self.connect_btn.configure(state="normal")

    def _select_device_in_tree(self, device_id: str | None):
        if not device_id or not hasattr(self, "device_tree"):
            return
        if not self.device_tree.exists(device_id):
            return
        current = self.device_tree.selection()
        if current and current[0] == device_id:
            return
        self._suppress_selection_event = True
        self.device_tree.selection_set(device_id)
        self.device_tree.focus(device_id)
        self.device_tree.see(device_id)

        def _release_and_notify():
            self._suppress_selection_event = False
            if self.device_tree.selection():
                self._on_device_select()

        self.after_idle(_release_and_notify)

    def destroy(self):
        self._unsubscribe_from_store()
        return super().destroy()

PairPage = DevicesPage
