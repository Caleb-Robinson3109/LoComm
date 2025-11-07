"""Pair page component for managing paired devices with modern layout."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.connection_manager import get_connection_manager
from utils.ui_helpers import create_scroll_container
from .pin_pairing_frame import PINPairingFrame

MOCK_DEVICE_ENTRIES = [
    ("DEV001", "Device Alpha", "Available", "Just now"),
    ("DEV002", "Device Beta", "Available", "5 min ago"),
    ("DEV003", "Device Gamma", "Available", "1 hour ago"),
]


class PairPage(tk.Frame):
    """Pair page for managing device connections, PIN entry, and trust verification."""

    def __init__(self, master, app, controller, session, on_device_paired: Optional[Callable] = None):
        super().__init__(master, bg=Colors.SURFACE)
        self.app = app
        self.controller = controller
        self.session = session
        self.on_device_paired = on_device_paired

        self.connection_manager = get_connection_manager()
        self.is_scanning = False
        self.connection_state = tk.StringVar(value="Not connected")
        self.status_var = tk.StringVar(value="Select a device to get started")
        self.selected_device_var = tk.StringVar(value="No device selected")
        self._pin_modal: Optional[tk.Toplevel] = None
        self._pin_modal_frame: Optional[PINPairingFrame] = None

        self.pack(fill=tk.BOTH, expand=True)
        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(Spacing.LG, Spacing.LG))
        self.main_body = scroll.frame

        DesignUtils.hero_header(
            self.main_body,
            title="Devices & Trust",
            subtitle="Pair LoRa hardware, confirm PINs face-to-face, and monitor secure sessions.",
            actions=[{"text": "Scan now", "command": self._scan_for_devices}]
        )

        self._build_status_strip()
        self._build_body()

    # ------------------------------------------------------------------ #
    def _build_status_strip(self):
        card, body = DesignUtils.card(
            self.main_body,
            "Current session status",
            "Live overview of your hardware link"
        )
        card.pack(fill=tk.X, pady=(0, Spacing.LG))
        labels_frame = tk.Frame(body, bg=Colors.SURFACE_ALT)
        labels_frame.pack(fill=tk.X)

        tk.Label(
            labels_frame,
            textvariable=self.connection_state,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD)
        ).pack(anchor="w")
        tk.Label(
            labels_frame,
            textvariable=self.status_var,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)
        ).pack(anchor="w", pady=(Spacing.XXS, 0))
        tk.Label(
            labels_frame,
            textvariable=self.selected_device_var,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)
        ).pack(anchor="w")

        action_row = tk.Frame(body, bg=Colors.SURFACE_ALT)
        action_row.pack(fill=tk.X, pady=(Spacing.SM, 0))
        DesignUtils.button(action_row, text="Scan for devices", command=self._scan_for_devices).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        DesignUtils.button(action_row, text="Disconnect", command=self._disconnect_device, variant="ghost").pack(side=tk.LEFT)

    def _build_body(self):
        body = tk.Frame(self.main_body, bg=Colors.SURFACE)
        body.pack(fill=tk.BOTH, expand=True)

        self._build_device_card(body)

    def _build_device_card(self, parent):
        card, content = DesignUtils.card(parent, "Scan & select hardware", "Choose the device you want to pair")
        card.pack(fill=tk.X, pady=(0, Spacing.LG))
        card.pack_propagate(True)

        columns = ("Device ID", "Name", "Status", "Last Seen")
        self.device_tree = ttk.Treeview(content, columns=columns, show="headings", height=10)
        for col in columns:
            self.device_tree.heading(col, text=col)
            self.device_tree.column(col, anchor="w", width=140)
        self.device_tree.pack(fill=tk.BOTH, expand=True)
        self.device_tree.bind("<<TreeviewSelect>>", self._on_device_select)

        for row in MOCK_DEVICE_ENTRIES:
            self.device_tree.insert("", tk.END, values=row)

        controls = tk.Frame(content, bg=Colors.SURFACE_ALT)
        controls.pack(fill=tk.X, pady=(Spacing.SM, 0))
        DesignUtils.button(controls, text="Scan again", command=self._scan_for_devices, variant="ghost").pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self.connect_btn = DesignUtils.button(controls, text="Use selected", command=self._connect_selected_device, variant="secondary")
        self.connect_btn.pack(side=tk.LEFT)
        self.connect_btn.configure(state="disabled")

    # ------------------------------------------------------------------ #
    def _scan_for_devices(self):
        if self.is_scanning:
            return
        self.is_scanning = True
        self.status_var.set("Scanning for devices…")
        self.after(2000, self._finish_scan)

    def _finish_scan(self):
        mock_discovered = [
            ("DEV004", "New Device Delta", "Available", "Just found"),
            ("DEV005", "New Device Epsilon", "Available", "Just found"),
        ]
        for row in mock_discovered:
            self.device_tree.insert("", tk.END, values=row)
        self.status_var.set(f"Found {len(mock_discovered)} new devices")
        self.is_scanning = False

    def _connect_selected_device(self):
        selected = self.device_tree.selection()
        if not selected:
            self.status_var.set("Select a device to pair")
            return
        device_id, name, *_ = self.device_tree.item(selected[0])["values"]
        self.selected_device_var.set(f"{name} ({device_id})")
        self.status_var.set(f"Ready to pair {name}")
        self._open_pin_modal(device_id, name)

    def _handle_pin_pair_success(self, device_id: str, device_name: str):
        self.status_var.set("Connecting…")
        self.app.start_transport_session(device_id, device_name)
        self.connection_state.set(f"Connected to {device_name}")
        self.status_var.set("Secure LoRa session established")
        self._close_pin_modal()
        if self.on_device_paired:
            self.on_device_paired(device_id, device_name)

    def _disconnect_device(self):
        if not self.connection_manager.is_connected():
            self.status_var.set("No device connected")
            return
        self.controller.stop_session()
        self.connection_manager.disconnect_device()
        self.status_var.set("Device disconnected")
        self.connection_state.set("Not connected")

    def _handle_demo_login(self):
        self.status_var.set("Connecting to Demo Device…")
        self.app.start_transport_session("demo-device", "Demo Device", mode="demo")
        self.connection_state.set("Connected to Demo Device")
        self._close_pin_modal()
        if self.on_device_paired:
            self.on_device_paired("demo-device", "Demo Device")

    def _on_device_select(self, _event):
        if not self.device_tree.selection():
            self.connect_btn.configure(state="disabled")
            return
        device_id, name, *_ = self.device_tree.item(self.device_tree.selection()[0])["values"]
        self.selected_device_var.set(f"{name} ({device_id})")
        self.connect_btn.configure(state="normal")

    def _open_pin_modal(self, device_id: str, device_name: str):
        self._close_pin_modal()
        modal = tk.Toplevel(self)
        modal.title(f"Pair {device_name}")
        modal.configure(bg=Colors.SURFACE)
        modal.geometry("520x560")
        modal.resizable(False, False)
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
