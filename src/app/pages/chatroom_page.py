"""Pair page component matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from utils.design_system import Colors, Typography, Spacing, DesignUtils, Space
from utils.state.connection_manager import get_connection_manager
from utils.state.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from ui.helpers import create_scroll_container
from mock.device_service import get_mock_device_service, MockDevice
from .base_page import BasePage, PageContext


class ChatroomPage(BasePage):
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
            text="My Chatroom",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")

        tk.Label(
            text_wrap,
            text="Manage your chatroom devices and connections",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

        self.scan_btn = DesignUtils.button(
            action_wrap,
            text="Scan",
            variant="secondary",
            command=self._scan_for_devices,
        )
        self.scan_btn.pack()

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

    def _go_to_chat(self):
        """Open the peer chat window and set status to Connected."""
        if self.controller:
            from utils.design_system import AppConfig
            self.controller.status_manager.update_status(AppConfig.STATUS_CONNECTED)
        from .chat_window import ChatWindow
        ChatWindow(self, peer_name=self._active_device_name)

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
            background=[("selected", Colors.STATE_INFO)],
            foreground=[("selected", Colors.TEXT_PRIMARY)],
        )

        # Create treeview
        columns = ("Name", "Device ID")
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
            text="Chat",
            command=self._go_to_chat,
            variant="secondary",
            width=btn_width,
        )
        self.connect_btn.pack(side=tk.RIGHT)

    def _refresh_device_table(self):
        if not hasattr(self, "device_tree"):
            return
        for row in self.device_tree.get_children():
            self.device_tree.delete(row)
        devices = self.device_service.list_devices()
        for device in devices:
            self.device_tree.insert("", tk.END, iid=device.device_id, values=device.to_table_row()[:2])
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

PairPage = ChatroomPage
