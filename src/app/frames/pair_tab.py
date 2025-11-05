"""Pair tab component for managing paired devices and scanning for new devices."""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class PairTab(ttk.Frame):
    """Pair tab for managing device connections and scanning."""

    def __init__(self, master, app, transport, session, on_device_paired: Optional[Callable] = None):
        super().__init__(master)
        self.app = app
        self.transport = transport
        self.session = session
        self.on_device_paired = on_device_paired

        # Mock paired devices list (in real implementation, this would come from transport/API)
        self.paired_devices = []
        self.is_scanning = False
        self.current_device = None
        self.current_device_id = None
        self.current_device_name = None
        self.current_device_status = None
        self.current_device_last_seen = None
        self.is_connected = False

        # ---------- Paired Devices Section with Box Border ---------- #
        devices_section = ttk.LabelFrame(self, text="Paired Devices", style='Custom.TLabelframe')
        devices_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        devices_content = ttk.Frame(devices_section)
        devices_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # ---------- Device List ---------- #
        # List header
        list_header = ttk.Frame(devices_content)
        list_header.pack(fill=tk.X, pady=(0, Spacing.MD))

        devices_label = ttk.Label(
            list_header,
            text="Available Devices:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
            foreground="#FFFFFF"
        )
        devices_label.pack(anchor="w")

        # Device list with scrollbar
        list_frame = ttk.Frame(devices_content)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))

        # Create Treeview for device list
        columns = ("Device ID", "Name", "Status", "Last Seen")
        self.device_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=6)

        # Configure columns
        self.device_tree.heading("Device ID", text="Device ID")
        self.device_tree.heading("Name", text="Name")
        self.device_tree.heading("Status", text="Status")
        self.device_tree.heading("Last Seen", text="Last Seen")

        self.device_tree.column("Device ID", width=120)
        self.device_tree.column("Name", width=120)
        self.device_tree.column("Status", width=100)
        self.device_tree.column("Last Seen", width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=scrollbar.set)

        self.device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ---------- Action Buttons Section ---------- #
        buttons_frame = ttk.Frame(devices_content)
        buttons_frame.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Scan button (takes full width)
        self.scan_btn = DesignUtils.create_styled_button(
            buttons_frame,
            "Scan for Devices",
            self._scan_for_devices,
            style='Primary.TButton'
        )
        self.scan_btn.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Row of action buttons
        action_buttons_frame = ttk.Frame(buttons_frame)
        action_buttons_frame.pack(fill=tk.X)

        # Connect/Disconnect button (replaces Pair/Unpair)
        self.connect_btn = DesignUtils.create_styled_button(
            action_buttons_frame,
            "Connect to Device",
            self._connect_selected_device,
            style='Success.TButton'
        )
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))

        # Disconnect button
        self.disconnect_btn = DesignUtils.create_styled_button(
            action_buttons_frame,
            "Disconnect Device",
            self._disconnect_device,
            style='Danger.TButton'
        )
        self.disconnect_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(Spacing.SM, 0))

        # Update button states based on connection status
        self._update_button_states()

        # ---------- Status Section with Box Border ---------- #
        status_section = ttk.LabelFrame(self, text="Scanning Status", style='Custom.TLabelframe')
        status_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.MD, Spacing.LG))

        status_content = ttk.Frame(status_section)
        status_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # Status display
        self.status_label = ttk.Label(
            status_content,
            text="Ready to scan",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            foreground="#FFFFFF"
        )
        self.status_label.pack(anchor="w")

        # ---------- Device Details Section (appears when device selected) ---------- #
        details_section = ttk.LabelFrame(self, text="Device Details", style='Custom.TLabelframe')
        details_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.MD, 0))

        details_content = ttk.Frame(details_section)
        details_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # Selected device info
        self.selected_device_info = ttk.Label(
            details_content,
            text="No device selected",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            foreground="#FFFFFF"
        )
        self.selected_device_info.pack(anchor="w")

        # Bind selection event
        self.device_tree.bind("<<TreeviewSelect>>", self._on_device_select)

        # Load initial data
        self._load_paired_devices()

    def _load_paired_devices(self):
        """Load paired devices into the list."""
        # Clear existing items
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)

        # Add mock devices (in real implementation, load from transport)
        mock_devices = [
            ("DEV001", "Device Alpha", "Available", "Just now"),
            ("DEV002", "Device Beta", "Available", "5 min ago"),
            ("DEV003", "Device Gamma", "Available", "1 hour ago"),
        ]

        for device_id, name, status, last_seen in mock_devices:
            self.device_tree.insert("", tk.END, values=(device_id, name, status, last_seen))

    def _scan_for_devices(self):
        """Start scanning for available devices."""
        if self.is_scanning:
            return

        self.is_scanning = True
        self.status_label.configure(text="Scanning for devices...")
        self.scan_btn.configure(state="disabled")

        # In real implementation, this would call transport.pair_devices()
        # For demo, we'll simulate scanning
        self._simulate_scan()

    def _simulate_scan(self):
        """Simulate device scanning (demo mode)."""
        import time
        import threading

        def scan_worker():
            # Simulate scan time
            time.sleep(2)

            # Add mock discovered devices
            mock_discovered = [
                ("DEV004", "New Device Delta", "Available", "Just found"),
                ("DEV005", "New Device Epsilon", "Available", "Just found"),
            ]

            # Update UI in main thread
            self.app.after(0, lambda: self._add_discovered_devices(mock_discovered))

        threading.Thread(target=scan_worker, daemon=True).start()

    def _add_discovered_devices(self, discovered_devices):
        """Add discovered devices to the list."""
        for device_id, name, status, last_seen in discovered_devices:
            self.device_tree.insert("", tk.END, values=(device_id, name, status, last_seen))

        self.status_label.configure(text=f"Found {len(discovered_devices)} new devices")
        self.scan_btn.configure(state="normal")
        self.is_scanning = False

    def _connect_selected_device(self):
        """Connect to the selected device."""
        selected = self.device_tree.selection()
        if not selected:
            self.status_label.configure(text="Please select a device to connect")
            return

        item = self.device_tree.item(selected[0])
        device_id, name, status, _ = item['values']

        self.status_label.configure(text=f"Connecting to {name}...")

        # Store device info for connection management
        self.current_device_id = device_id
        self.current_device_name = name
        self.current_device_status = "Connected"
        self.current_device_last_seen = "Just now"
        self.is_connected = True

        # Update UI to show connected
        self.device_tree.item(selected[0], values=(device_id, name, "Connected", "Just now"))
        self.status_label.configure(text=f"Connected to {name}")

        # Update button states
        self._update_button_states()

        # Notify MainFrame that a device is paired/connected
        if self.on_device_paired:
            self.on_device_paired(device_id, name)

    def _disconnect_device(self):
        """Disconnect from current device."""
        if not self.is_connected:
            self.status_label.configure(text="No device is currently connected")
            return

        self.status_label.configure(text=f"Disconnecting from {self.current_device_name}...")

        # Update device status in the list
        if self.current_device_id:
            # Find and update the device in the tree
            for item in self.device_tree.get_children():
                item_values = self.device_tree.item(item)['values']
                if item_values[0] == self.current_device_id:  # device_id matches
                    device_id, name, _, _ = item_values
                    self.device_tree.item(item, values=(device_id, name, "Available", "Just now"))
                    break

        # Clear connection state
        self.is_connected = False
        self.current_device = None
        self.current_device_id = None
        self.current_device_name = None
        self.current_device_status = None
        self.current_device_last_seen = None

        self.status_label.configure(text="Device disconnected")

        # Update button states
        self._update_button_states()

        # Notify MainFrame that device is disconnected
        if self.on_device_paired:
            self.on_device_paired(None, None)

    def _update_button_states(self):
        """Update button states based on current connection status."""
        if self.is_connected:
            self.connect_btn.configure(state="disabled", text="Connected")
            self.disconnect_btn.configure(state="normal", text="Disconnect")
        else:
            self.connect_btn.configure(state="normal", text="Connect to Device")
            self.disconnect_btn.configure(state="disabled", text="Disconnect")

    def _on_device_select(self, event):
        """Handle device selection change."""
        selected = self.device_tree.selection()
        if selected:
            item = self.device_tree.item(selected[0])
            device_id, name, status, last_seen = item['values']
            self.selected_device_info.configure(text=f"Selected: {name} ({device_id}) - Status: {status}")

            # Update button states based on selection and connection status
            if self.is_connected and device_id == self.current_device_id:
                # Currently connected to this device
                self.connect_btn.configure(state="disabled", text="Connected")
                self.disconnect_btn.configure(state="normal", text="Disconnect")
            elif status == "Connected":
                # Device is connected but not to this one
                self.connect_btn.configure(state="disabled", text="Connected to Another")
                self.disconnect_btn.configure(state="disabled", text="Disconnect")
            else:
                # Device is available to connect
                self._update_button_states()
        else:
            self.selected_device_info.configure(text="No device selected")

    def get_connected_device_info(self):
        """Get information about currently connected device."""
        if self.is_connected and self.current_device_name:
            return {
                'id': self.current_device_id,
                'name': self.current_device_name,
                'status': self.current_device_status,
                'last_seen': self.current_device_last_seen
            }
        return None

    def refresh_devices(self):
        """Refresh the device list."""
        self._load_paired_devices()
        self._update_button_states()
