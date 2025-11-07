"""Pair page component for managing paired devices and scanning for new devices."""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.connection_manager import get_connection_manager


class PairPage(tk.Frame):
    """Pair page for managing device connections and scanning (redesigned with ChatPage excellence)."""

    def __init__(self, master, app, transport, session, on_device_paired: Optional[Callable] = None):
        super().__init__(master, bg=Colors.BG_PRIMARY)
        self.app = app
        self.transport = transport
        self.session = session
        self.on_device_paired = on_device_paired

        # Use centralized connection manager
        self.connection_manager = get_connection_manager()

        # Track if PIN pairing is currently showing
        self.showing_pin_pairing = False

        # Register for connection state updates
        self.connection_manager.register_connection_callback(self._on_connection_state_change)
        self.connection_manager.register_device_info_callback(self._on_device_info_change)

        # Mock paired devices list (in real implementation, this would come from transport/API)
        self.paired_devices = []
        self.is_scanning = False

        # Initialize connection state from centralized manager
        device_info = self.connection_manager.get_connected_device_info()
        if device_info:
            self.is_connected = True
            self.current_device_id = device_info['id']
            self.current_device_name = device_info['name']
        else:
            self.is_connected = False
            self.current_device_id = None
            self.current_device_name = None
        self.current_device_status = None
        self.current_device_last_seen = None

        # Configure frame styling (matching ChatPage)
        self.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        # Create scrollable frame for all content (matching ChatPage)
        canvas = tk.Canvas(self, bg=Colors.BG_PRIMARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_PRIMARY)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel scrolling (matching ChatPage)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_to_mousewheel)
        canvas.bind("<Leave>", _unbind_from_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------- Title Section (matching ChatPage) ---------- #
        title_section = tk.Frame(scrollable_frame, bg=Colors.BG_PRIMARY)
        title_section.pack(fill=tk.X, pady=(0, Spacing.XL))

        title_frame = tk.Frame(title_section, bg=Colors.BG_PRIMARY)
        title_frame.pack(anchor="center")

        title_label = tk.Label(
            title_frame,
            text="Device Management",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XXL, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",
            bg=Colors.BG_PRIMARY
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Secure Device-to-Device Communication",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG),
            fg="#CCCCCC",
            bg=Colors.BG_PRIMARY
        )
        subtitle_label.pack(pady=(Spacing.SM, 0))

        # Status label with enhanced styling (matching ChatPage style)
        self.status_var = tk.StringVar(value="Ready to scan")
        status_label = tk.Label(title_section, textvariable=self.status_var,
                               font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
                               fg="#CCCCCC", bg=Colors.BG_PRIMARY)
        status_label.pack(anchor="center", pady=(Spacing.MD, 0))

        # ---------- Welcome Section with Box Border (Device Controls) ---------- #
        welcome_section = tk.Frame(scrollable_frame, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        welcome_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        # Welcome section header (matching ChatPage style)
        welcome_header = tk.Label(welcome_section, text="Device Controls", bg=Colors.BG_SECONDARY,
                                fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        welcome_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        welcome_content = tk.Frame(welcome_section, bg=Colors.BG_SECONDARY)
        welcome_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # Control buttons with ChatPage styling
        button_row = tk.Frame(welcome_content, bg=Colors.BG_SECONDARY)
        button_row.pack(fill=tk.X)

        # Scan button (matching ChatPage button style)
        self.scan_btn = DesignUtils.create_styled_button(
            button_row,
            "Scan for Devices",
            self._scan_for_devices,
            style='Primary.TButton'
        )
        self.scan_btn.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Action buttons row (matching ChatPage layout)
        action_buttons_frame = tk.Frame(welcome_content, bg=Colors.BG_SECONDARY)
        action_buttons_frame.pack(fill=tk.X)

        # Connect button (matching ChatPage button style)
        self.connect_btn = DesignUtils.create_styled_button(
            action_buttons_frame,
            "Connect to Device",
            self._connect_selected_device,
            style='Success.TButton'
        )
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.SM))

        # Disconnect button (matching ChatPage button style)
        self.disconnect_btn = DesignUtils.create_styled_button(
            action_buttons_frame,
            "Disconnect Device",
            self._disconnect_device,
            style='Danger.TButton'
        )
        self.disconnect_btn.pack(side=tk.LEFT, padx=(Spacing.SM, 0))

        # Update button states based on connection status
        self._update_button_states()

        # ---------- Application Features Section with Box Border (Device List) ---------- #
        features_section = tk.Frame(scrollable_frame, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        features_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.MD, Spacing.LG))

        # Features section header (matching ChatPage style)
        features_header = tk.Label(features_section, text="Available Devices", bg=Colors.BG_SECONDARY,
                                 fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        features_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        features_content = tk.Frame(features_section, bg=Colors.BG_SECONDARY)
        features_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # Device list container with enhanced styling (matching ChatPage layout)
        device_frame = tk.Frame(features_content, bg=Colors.BG_SECONDARY)
        device_frame.pack(fill=tk.BOTH, expand=True)

        # Set fixed size for device frame (matching ChatPage proportions)
        device_frame.configure(height=250)  # Appropriate height for device list
        device_frame.pack_propagate(False)  # Prevent expansion

        # Add a border frame for the device list (matching ChatPage style)
        border_frame = tk.Frame(device_frame, bg=Colors.BORDER_LIGHT, bd=1, relief="solid")
        border_frame.pack(fill=tk.BOTH, expand=True)

        # Create Treeview for device list (enhanced with ChatPage styling)
        columns = ("Device ID", "Name", "Status", "Last Seen")
        self.device_tree = ttk.Treeview(border_frame, columns=columns, show="headings", height=10)

        # Configure columns
        self.device_tree.heading("Device ID", text="Device ID")
        self.device_tree.heading("Name", text="Name")
        self.device_tree.heading("Status", text="Status")
        self.device_tree.heading("Last Seen", text="Last Seen")

        self.device_tree.column("Device ID", width=120)
        self.device_tree.column("Name", width=120)
        self.device_tree.column("Status", width=100)
        self.device_tree.column("Last Seen", width=150)

        # Add scrollbar (matching ChatPage style)
        device_scrollbar = tk.Scrollbar(border_frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=device_scrollbar.set)

        self.device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        device_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mouse wheel scrolling to device tree (matching ChatPage)
        def _device_on_mousewheel(event):
            self.device_tree.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        def _bind_device_to_mousewheel(event):
            self.device_tree.bind_all("<MouseWheel>", _device_on_mousewheel)

        def _unbind_device_from_mousewheel(event):
            self.device_tree.unbind_all("<MouseWheel>")

        self.device_tree.bind("<Enter>", _bind_device_to_mousewheel)
        self.device_tree.bind("<Leave>", _unbind_device_from_mousewheel)

        # ---------- Device Details Section with Box Border ---------- #
        details_section = tk.Frame(scrollable_frame, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        details_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.MD, Spacing.LG))

        details_header = tk.Label(details_section, text="Device Details", bg=Colors.BG_SECONDARY,
                              fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        details_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        details_content = tk.Frame(details_section, bg=Colors.BG_SECONDARY)
        details_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # Selected device info (matching ChatPage typography)
        self.selected_device_info = tk.Label(
            details_content,
            text="No device selected",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY,
            justify='left'
        )
        self.selected_device_info.pack(anchor="w")

        # Bind selection event
        self.device_tree.bind("<<TreeviewSelect>>", self._on_device_select)

        # ---------- Footer (matching ChatPage) ---------- #
        footer_frame = tk.Frame(scrollable_frame, bg=Colors.BG_PRIMARY)
        footer_frame.pack(fill=tk.X, pady=(Spacing.LG, 0))

        footer_label = tk.Label(
            footer_frame,
            text="Use the sidebar to navigate between Home, Chat, Settings, and About",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg="#888888",
            bg=Colors.BG_PRIMARY,
            justify='center',
            wraplength=400
        )
        footer_label.pack()

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
        self.status_var.set("Scanning for devices...")
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

        self.status_var.set(f"Found {len(discovered_devices)} new devices")
        self.scan_btn.configure(state="normal")
        self.is_scanning = False

    def _connect_selected_device(self):
        """Show PIN pairing interface instead of directly connecting."""
        selected = self.device_tree.selection()
        if not selected:
            self.status_var.set("Please select a device to connect")
            return

        item = self.device_tree.item(selected[0])
        device_id, name, status, _ = item['values']

        self.status_var.set(f"Preparing to pair with {name}...")

        # Show PIN pairing interface instead of directly connecting
        self._show_pin_pairing_interface(device_id, name)

    def _show_pin_pairing_interface(self, device_id, device_name):
        """Show PIN pairing interface for the selected device."""
        from pages import PINPairingFrame

        # Initialize attributes for PIN pairing
        self.showing_pin_pairing = True
        self.pending_device_id = device_id
        self.pending_device_name = device_name

        # Store current widgets to restore later
        self.original_widgets = self.winfo_children()

        # Create a container for the PIN pairing interface
        self.pairing_container = tk.Frame(self, bg=Colors.BG_PRIMARY)
        self.pairing_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        # Add back button
        back_button_frame = tk.Frame(self.pairing_container, bg=Colors.BG_PRIMARY)
        back_button_frame.pack(anchor="w", pady=(0, Spacing.MD))

        back_btn = DesignUtils.create_styled_button(
            back_button_frame,
            "← Back to Device List",
            self._return_to_device_list,
            style='Secondary.TButton'
        )
        back_btn.pack()

        # Show PIN pairing frame
        self.pin_pairing_frame = PINPairingFrame(
            self.pairing_container,
            lambda device_id, device_name: self._handle_pin_pair_success(device_id, device_name),
            self._handle_demo_login
        )
        self.pin_pairing_frame.pack(fill=tk.BOTH, expand=True)

        # Update status
        self.status_var.set(f"Enter PIN to pair with {device_name}")

    def _return_to_device_list(self):
        """Return to the device list from PIN pairing."""
        # Clear the pairing interface
        if hasattr(self, 'pin_pairing_frame') and self.pin_pairing_frame:
            self.pin_pairing_frame.destroy()
            self.pin_pairing_frame = None

        if hasattr(self, 'pairing_container') and self.pairing_container:
            self.pairing_container.destroy()
            self.pairing_container = None

        self.showing_pin_pairing = False
        self.pending_device_id = None
        self.pending_device_name = None

        # Update status
        self.status_var.set("Ready to pair devices")

    def _handle_pin_pair_success(self, device_id, device_name):
        """Handle successful PIN pairing from the pair tab."""
        # Use centralized connection manager
        success = self.connection_manager.connect_device(device_id, device_name)

        if success:
            # Update UI immediately (connection manager callbacks will handle sync)
            self.status_var.set("Connected")

            # Notify MainFrame that a device is paired/connected
            if self.on_device_paired:
                self.on_device_paired(device_id, device_name)
        else:
            self.status_var.set("Failed to connect to device")

    def _handle_demo_login(self):
        """Handle demo login from the pair tab."""
        # Use centralized connection manager for demo
        success = self.connection_manager.connect_device("demo-device", "Demo Device")

        if success:
            # Update UI immediately
            self.status_var.set("Connected to Demo Device")

            # Notify MainFrame that a device is paired/connected
            if self.on_device_paired:
                self.on_device_paired("demo-device", "Demo Device")
        else:
            self.status_var.set("Failed to connect to demo")

    def _disconnect_device(self):
        """Disconnect from current device using centralized connection manager."""
        if not self.is_connected:
            self.status_var.set("No device is currently connected")
            return

        self.status_var.set("Disconnecting...")

        # Use centralized connection manager
        success = self.connection_manager.disconnect_device()

        if success:
            # Update UI immediately (connection manager callbacks will handle sync)
            self.status_var.set("Device disconnected")

            # Notify MainFrame that device is disconnected
            if self.on_device_paired:
                self.on_device_paired(None, None)
        else:
            self.status_var.set("Failed to disconnect device")

    def _update_button_states(self):
        """Update button states using centralized connection manager."""
        # Use connection manager to determine button states
        self.connection_manager.update_button_states(self.connect_btn, self.disconnect_btn)

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

    # ========== CONNECTION MANAGER CALLBACKS ==========

    def _on_connection_state_change(self, is_connected: bool, device_id: Optional[str], device_name: Optional[str]):
        """Handle connection state changes from centralized manager."""
        self.is_connected = is_connected
        self.current_device_id = device_id
        self.current_device_name = device_name

        # Update UI elements on main thread
        self.app.after(0, lambda: self._update_ui_after_connection_change())

    def _on_device_info_change(self, device_info: Optional[dict]):
        """Handle device info changes from centralized manager."""
        if device_info:
            self.current_device_id = device_info['id']
            self.current_device_name = device_info['name']
        else:
            self.current_device_id = None
            self.current_device_name = None

        # Update UI elements on main thread
        self.app.after(0, lambda: self._update_ui_after_connection_change())

    def _update_ui_after_connection_change(self):
        """Update UI elements after connection state change (called on main thread)."""
        # Update device list to reflect current connection status
        self._update_device_list_connection_status()

        # Update button states
        self._update_button_states()

        # Update status label
        status_text = self.connection_manager.get_connection_status_text()
        self.status_var.set(status_text)

        # Update selected device info if currently connected
        if self.is_connected and self.current_device_name:
            self.selected_device_info.configure(text=f"Connected: {self.current_device_name} ({self.current_device_id})")
        else:
            self.selected_device_info.configure(text="No device selected")

    def _update_device_list_connection_status(self):
        """Update connection status in the device list."""
        for item in self.device_tree.get_children():
            item_values = self.device_tree.item(item)['values']
            device_id = item_values[0]

            if self.is_connected and device_id == self.current_device_id:
                # This device is currently connected
                self.device_tree.item(item, values=(device_id, item_values[1], "Connected", "Just now"))
            else:
                # Reset to available if not connected
                self.device_tree.item(item, values=(device_id, item_values[1], "Available", "Just now"))
