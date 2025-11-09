"""Pair page component for managing paired devices with modern layout."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.connection_manager import get_connection_manager
from utils.ui_helpers import create_scroll_container
from utils.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from mock.device_service import get_mock_device_service, MockDevice
from mock.network_simulator import LoRaNetworkSimulator
from .base_page import BasePage, PageContext
from .pin_pairing_frame import PINPairingFrame


class DevicesPage(BasePage):
    """Devices page for managing device connections, PIN entry, and trust verification."""

    def __init__(self, master, context: PageContext, on_device_paired: Optional[Callable] = None):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.controller = context.controller if context else None
        self.session = context.session if context else None
        self.on_device_paired = on_device_paired

        self.connection_manager = get_connection_manager()
        self.ui_store = get_ui_store()
        self.device_service = get_mock_device_service()
        self.scenario_data = LoRaNetworkSimulator().scenario_summary()
        self._device_subscription: Optional[Callable[[DeviceStatusSnapshot], None]] = None
        self.is_scanning = False
        self.connection_state = tk.StringVar(value="Ready to pair")
        self.status_var = tk.StringVar(value="No device paired yet. Select a device to get started.")
        self.selected_device_var = tk.StringVar(value="No device selected")
        self.scenario_var = tk.StringVar(value=self.session.mock_scenario or "default")
        self.scenario_description_var = tk.StringVar(value=self._scenario_description(self.scenario_var.get()))
        self.telemetry_vars = {
            "rssi": tk.StringVar(value="–"),
            "snr": tk.StringVar(value="–"),
            "battery": tk.StringVar(value="–"),
        }
        self.detail_vars = {
            "name": tk.StringVar(value="No device selected"),
            "firmware": tk.StringVar(value="—"),
            "region": tk.StringVar(value="—"),
            "last_seen": tk.StringVar(value="—"),
        }
        self._active_device_name: Optional[str] = None
        self._active_device_id: Optional[str] = None
        self._pin_modal: Optional[tk.Toplevel] = None
        self._pin_modal_frame: Optional[PINPairingFrame] = None

        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(Spacing.LG, Spacing.LG))
        self.main_body = scroll.frame

        DesignUtils.hero_header(
            self.main_body,
            title="Devices & Trust",
            subtitle="Pair LoRa hardware, confirm PINs face-to-face, and monitor secure sessions.",
            actions=[{"text": "Scan", "command": self._scan_for_devices}]
        )

        self._build_status_strip()
        self._build_body()
        self._apply_snapshot(self.ui_store.get_device_status())
        self._set_stage(DeviceStage.READY)

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
        self.scenario_label = tk.Label(
            labels_frame,
            textvariable=self.scenario_description_var,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=360,
            justify="left"
        )
        self.scenario_label.pack(anchor="w", pady=(Spacing.XXS, 0))

        action_row = tk.Frame(body, bg=Colors.SURFACE_ALT)
        action_row.pack(fill=tk.X, pady=(Spacing.SM, 0))
        self.scan_btn = DesignUtils.button(action_row, text="Scan for devices", command=self._scan_for_devices, variant="secondary")
        self.scan_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self.disconnect_btn = DesignUtils.button(action_row, text="Disconnect", command=self._disconnect_device, variant="ghost")
        self.disconnect_btn.pack(side=tk.LEFT)
        self.disconnect_btn.configure(state="disabled")
        scenario_row = tk.Frame(body, bg=Colors.SURFACE_ALT)
        scenario_row.pack(fill=tk.X, pady=(Spacing.SM, 0))
        tk.Label(
            scenario_row,
            text="Mock network scenario",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)
        ).pack(anchor="w")
        scenario_combo = ttk.Combobox(
            scenario_row,
            values=list(self.scenario_data.keys()),
            textvariable=self.scenario_var,
            state="readonly"
        )
        scenario_combo.pack(fill=tk.X, expand=True, pady=(Spacing.XXS, 0))
        scenario_combo.bind("<<ComboboxSelected>>", lambda _e: self._apply_scenario())

    def _build_body(self):
        body = tk.Frame(self.main_body, bg=Colors.SURFACE)
        body.pack(fill=tk.BOTH, expand=True)

        self._build_device_card(body)
        self._refresh_device_table()

    def _build_device_card(self, parent):
        card, content = DesignUtils.card(parent, "Scan & select hardware", "Choose the device you want to pair")
        card.pack(fill=tk.X, pady=(0, Spacing.LG))
        card.pack_propagate(True)

        if not hasattr(self, "detail_vars"):
            self.detail_vars = {
                "name": tk.StringVar(value="No device selected"),
                "firmware": tk.StringVar(value="—"),
                "region": tk.StringVar(value="—"),
                "last_seen": tk.StringVar(value="—"),
            }

        columns = ("Device ID", "Name", "Status", "Last Seen")
        self.device_tree = ttk.Treeview(content, columns=columns, show="headings", height=10)
        for col in columns:
            self.device_tree.heading(col, text=col)
            self.device_tree.column(col, anchor="w", width=140)
        self.device_tree.pack(fill=tk.BOTH, expand=True)
        self.device_tree.bind("<<TreeviewSelect>>", self._on_device_select)

        controls = tk.Frame(content, bg=Colors.SURFACE_ALT)
        controls.pack(fill=tk.X, pady=(Spacing.SM, 0))
        DesignUtils.button(controls, text="Scan", command=self._scan_for_devices, variant="primary").pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self.connect_btn = DesignUtils.button(controls, text="Connect", command=self._connect_selected_device, variant="secondary")
        self.connect_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
        self.connect_btn.configure(state="disabled")
        self.disconnect_btn = DesignUtils.button(controls, text="Disconnect", command=self._disconnect_device, variant="danger")
        self.disconnect_btn.pack(side=tk.LEFT)
        self.disconnect_btn.configure(state="disabled")

        telemetry = tk.Frame(content, bg=Colors.SURFACE_ALT)
        telemetry.pack(fill=tk.X, pady=(Spacing.SM, 0))
        tk.Label(
            telemetry,
            text="Live telemetry",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, Spacing.XXS))
        self._add_telemetry_field(telemetry, "RSSI", self.telemetry_vars["rssi"], 1, 0)
        self._add_telemetry_field(telemetry, "SNR", self.telemetry_vars["snr"], 1, 1)
        self._add_telemetry_field(telemetry, "Battery", self.telemetry_vars["battery"], 1, 2)

        detail_card, detail_body = DesignUtils.card(parent, "Selected device details", "Firmware + region details")
        detail_card.pack(fill=tk.X, pady=(0, Spacing.LG))
        detail_body.columnconfigure(1, weight=1)
        self._add_detail_row(detail_body, "Name", self.detail_vars["name"], 0)
        self._add_detail_row(detail_body, "Firmware", self.detail_vars["firmware"], 1)
        self._add_detail_row(detail_body, "Region", self.detail_vars["region"], 2)
        self._add_detail_row(detail_body, "Last seen", self.detail_vars["last_seen"], 3)

    def _add_telemetry_field(self, parent, label: str, var: tk.StringVar, row: int, col: int):
        wrapper = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        wrapper.grid(row=row, column=col, padx=Spacing.MD, pady=(Spacing.XXS, 0), sticky="w")
        tk.Label(wrapper, text=label, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w")
        tk.Label(wrapper, textvariable=var, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_PRIMARY,
                 font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD)).pack(anchor="w")

    def _add_detail_row(self, parent, label: str, var: tk.StringVar, row: int):
        tk.Label(parent, text=label, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).grid(row=row, column=0, sticky="w", pady=(0, Spacing.XXS))
        tk.Label(parent, textvariable=var, bg=Colors.SURFACE_ALT, fg=Colors.TEXT_PRIMARY,
                 font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR)).grid(row=row, column=1, sticky="w")

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
        self._update_telemetry_panel(None)

    # ------------------------------------------------------------------ #
    def _scan_for_devices(self):
        if self.is_scanning:
            return
        self.is_scanning = True
        self._set_stage(DeviceStage.SCANNING)
        self.after(2000, self._finish_scan)

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

        transport = getattr(self.controller, "transport", None)
        if transport and getattr(transport, "is_mock", False):
            self._set_stage(DeviceStage.CONNECTING, name)
            if getattr(self.controller, "start_mock_session", None):
                success = self.controller.start_mock_session(device_id, name)
            else:
                success = False
            if success:
                self._set_stage(DeviceStage.CONNECTED, name)
                if self.on_device_paired:
                    self.on_device_paired(device_id, name)
                if self.host and hasattr(self.host, "show_chat_page"):
                    self.host.show_chat_page()
            else:
                messagebox.showerror("Mock Connection Failed", "Unable to connect to mock device.")
                self._set_stage(DeviceStage.DISCONNECTED, name)
            return

        self._set_stage(DeviceStage.AWAITING_PIN, name)
        self._open_pin_modal(device_id, name)

    def _handle_pin_pair_success(self, device_id: str, device_name: str):
        self._set_stage(DeviceStage.CONNECTING, device_name)
        self.app.start_transport_session(device_id, device_name)
        self._set_stage(DeviceStage.CONNECTED, device_name)
        self._close_pin_modal()
        if self.on_device_paired:
            self.on_device_paired(device_id, device_name)
        if self.host and hasattr(self.host, "show_chat_page"):
            self.host.show_chat_page()

    def _disconnect_device(self):
        if not self.connection_manager.is_connected():
            self.status_var.set("No device connected")
            return
        self.controller.stop_session()
        self.connection_manager.disconnect_device()
        last_device = self.selected_device_var.get()
        label = last_device if last_device != "No device selected" else None
        self._set_stage(DeviceStage.DISCONNECTED, label)

    def _handle_demo_login(self):
        self._set_stage(DeviceStage.CONNECTING, "Demo Device")
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
        self._update_telemetry_panel(device)
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
            self._update_telemetry_panel(device)
        else:
            self._update_telemetry_panel(None)

    def _apply_scenario(self):
        scenario = self.scenario_var.get() or "default"
        if hasattr(self.controller, "set_mock_scenario"):
            self.controller.set_mock_scenario(scenario)
        self.session.mock_scenario = scenario
        desc = self._scenario_description(scenario)
        self.scenario_description_var.set(desc)
        self.status_var.set(f"Scenario: {scenario} • {desc}")

    def _scenario_description(self, scenario: str) -> str:
        info = self.scenario_data.get(scenario)
        if not info:
            return "Custom mock scenario"
        return info.get("description", "Mock network simulation profile.")

    def _update_telemetry_panel(self, device: MockDevice | None):
        if not device:
            for var in self.telemetry_vars.values():
                var.set("–")
            self.detail_vars["name"].set("No device selected")
            self.detail_vars["firmware"].set("—")
            self.detail_vars["region"].set("—")
            self.detail_vars["last_seen"].set("—")
            return
        telemetry = device.telemetry or {}
        self.telemetry_vars["rssi"].set(f"{telemetry.get('rssi', '–')} dBm")
        self.telemetry_vars["snr"].set(f"{telemetry.get('snr', '–')} dB")
        battery = telemetry.get("battery")
        self.telemetry_vars["battery"].set(f"{battery}%" if battery is not None else "–")
        self.detail_vars["name"].set(device.name)
        self.detail_vars["firmware"].set(device.metadata.get("firmware", "—"))
        self.detail_vars["region"].set(device.metadata.get("region", "—"))
        self.detail_vars["last_seen"].set(device.last_seen)

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
