"""Pair page component for managing paired devices with modern layout."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.connection_manager import get_connection_manager
from utils.ui_helpers import create_scroll_container

MOCK_DEVICE_ENTRIES = [
    ("DEV001", "Device Alpha", "Available", "Just now"),
    ("DEV002", "Device Beta", "Available", "5 min ago"),
    ("DEV003", "Device Gamma", "Available", "1 hour ago"),
]


class PairPage(tk.Frame):
    """Pair page for managing device connections and scanning."""

    def __init__(self, master, app, controller, session, on_device_paired: Optional[Callable] = None):
        super().__init__(master, bg=Colors.SURFACE)
        self.app = app
        self.controller = controller
        self.session = session
        self.on_device_paired = on_device_paired

        self.connection_manager = get_connection_manager()
        self.is_scanning = False

        self.pack(fill=tk.BOTH, expand=True)
        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(Spacing.LG, Spacing.LG))
        self.main_body = scroll.frame

        DesignUtils.hero_header(
            self.main_body,
            title="Device management",
            subtitle="Scan for LoRa hardware, enter the 5-digit PIN, and monitor connection state.",
            actions=[{"text": "Scan now", "command": self._scan_for_devices}]
        )

        self._build_device_section()
        self._build_controls_section()

    # ------------------------------------------------------------------ #
    def _build_device_section(self):
        section, body = DesignUtils.section(self.main_body, "Available devices", "Select a device to begin pairing")
        columns = ("Device ID", "Name", "Status", "Last Seen")
        self.device_tree = ttk.Treeview(body, columns=columns, show="headings", height=8)
        for col in columns:
            self.device_tree.heading(col, text=col)
            self.device_tree.column(col, anchor="w", width=150)
        self.device_tree.pack(fill=tk.BOTH, expand=True)
        self.device_tree.bind("<<TreeviewSelect>>", self._on_device_select)

        for row in MOCK_DEVICE_ENTRIES:
            self.device_tree.insert("", tk.END, values=row)

        scrollbar = ttk.Scrollbar(body, orient=tk.VERTICAL, command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_controls_section(self):
        section, body = DesignUtils.section(self.main_body, "Actions", "Pairing controls and PIN entry")
        action_row = tk.Frame(body, bg=Colors.SURFACE_ALT)
        action_row.pack(fill=tk.X, pady=(0, Spacing.SM))
        DesignUtils.button(action_row, text="Scan for devices", command=self._scan_for_devices).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self.connect_btn = DesignUtils.button(action_row, text="Connect", command=self._connect_selected_device, variant="secondary")
        self.connect_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self.connect_btn.configure(state="disabled")

        self.disconnect_btn = DesignUtils.button(action_row, text="Disconnect", command=self._disconnect_device, variant="ghost")
        self.disconnect_btn.pack(side=tk.LEFT)
        self.disconnect_btn.configure(state="disabled")

        self.status_var = tk.StringVar(value="Ready to pair")
        tk.Label(body, textvariable=self.status_var, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="w")

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
        self._show_pin_pairing_interface(device_id, name)

    def _show_pin_pairing_interface(self, device_id, device_name):
        # Import at the top of the function to avoid circular imports
        from .pin_pairing_frame import PINPairingFrame

        self.main_body.pack_forget()
        self.pairing_container = tk.Frame(self, bg=Colors.SURFACE)
        self.pairing_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        back = DesignUtils.button(self.pairing_container, text="← Back to devices", command=self._return_to_device_list, variant="ghost")
        back.pack(anchor="w")

        self.pin_pairing_frame = PINPairingFrame(
            self.pairing_container,
            lambda d_id, d_name: self._handle_pin_pair_success(d_id, d_name),
            self._handle_demo_login
        )
        self.pin_pairing_frame.pack(fill=tk.BOTH, expand=True)

        self.status_var.set(f"Enter PIN for {device_name}")

    def _return_to_device_list(self):
        if hasattr(self, 'pairing_container') and self.pairing_container:
            self.pairing_container.destroy()
        self.main_body.pack(fill=tk.BOTH, expand=True)
        self.status_var.set("Ready to pair")

    def _handle_pin_pair_success(self, device_id, device_name):
        self.status_var.set("Connecting…")
        self.app.start_transport_session(device_id, device_name)
        self._return_to_device_list()

    def _disconnect_device(self):
        if not self.connection_manager.is_connected():
            self.status_var.set("No device connected")
            return
        self.controller.stop_session()
        self.connection_manager.disconnect_device()
        self.status_var.set("Device disconnected")
        self.disconnect_btn.configure(state="disabled")

    def _handle_demo_login(self):
        self.status_var.set("Connecting to Demo Device…")
        self.app.start_transport_session("demo-device", "Demo Device", mode="demo")
        self._return_to_device_list()

    def _on_device_select(self, _event):
        self.connect_btn.configure(state="normal")
        if self.connection_manager.is_connected():
            self.disconnect_btn.configure(state="normal")
        else:
            self.disconnect_btn.configure(state="disabled")
