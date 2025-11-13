"""Test page component matching peers page design."""
from __future__ import annotations

import tkinter as tk
from typing import Optional, Callable

from utils.design_system import AppConfig, Colors, Typography, Spacing, DesignUtils, Space
from utils.state.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from ui.helpers import create_scroll_container, enable_global_mousewheel
from mock.device_service import get_mock_device_service, MockDevice
from .base_page import BasePage, PageContext


class TestPage(BasePage):
    """Test page with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext, on_device_paired: Optional[Callable] = None):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.controller = context.controller if context else None
        self.session = context.session if context else None
        self.host = context.navigator if context else None
        self.on_device_paired = on_device_paired

        self.ui_store = get_ui_store()
        self.device_service = get_mock_device_service()
        self._device_subscription: Optional[Callable[[DeviceStatusSnapshot], None]] = None
        self.is_scanning = False
        self._active_device_name: Optional[str] = None
        self._active_device_id: Optional[str] = None
        self._selected_device_id: Optional[str] = None
        self._device_row_frames: dict[str, tk.Frame] = {}
        self._scan_timer_id: Optional[str] = None

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
            text="Test Page",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")

        tk.Label(
            text_wrap,
            text="Test your peers and device sessions",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

        self.refresh_btn = DesignUtils.button(
            action_wrap,
            text="Refresh",
            variant="secondary",
            command=self._scan_for_devices,
        )
        self.refresh_btn.pack()

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
            text="Test Items",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        ).pack(anchor="w", pady=(0, Spacing.SM))

        # Device list
        list_frame = tk.Frame(content, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.MD)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, Space.SM))

        self._build_device_list(list_frame)
        # Chat button below the table
        chat_btn = DesignUtils.button(
            content,
            text="Chat",
            command=self._handle_global_chat,
            variant="primary",
        )
        chat_btn.pack(anchor="w", pady=(Spacing.SM, 0))
    def _build_device_list(self, parent):
        """Build simple device list."""
        header = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        header.pack(fill=tk.X, pady=(0, Spacing.XXS))
        header.grid_columnconfigure(0, weight=3)
        header.grid_columnconfigure(1, weight=2)

        tk.Label(
            header,
            text="Name",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
            anchor="center",
        ).grid(row=0, column=0, sticky="ew")
        tk.Label(
            header,
            text="Device ID",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
            anchor="center",
        ).grid(row=0, column=1, sticky="ew")

        scroll_wrapper = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        scroll_wrapper.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(
            scroll_wrapper,
            bg=Colors.SURFACE_ALT,
            highlightthickness=0,
        )
        scrollbar = tk.Scrollbar(scroll_wrapper, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.device_rows_container = tk.Frame(canvas, bg=Colors.SURFACE_ALT)
        self._device_icon_canvas_window = canvas.create_window((0, 0), window=self.device_rows_container, anchor="nw")
        canvas.bind(
            "<Configure>",
            lambda event, canvas=canvas: canvas.itemconfigure(self._device_icon_canvas_window, width=event.width),
        )
        self.device_rows_container.bind(
            "<Configure>",
            lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        enable_global_mousewheel(canvas)
        self._refresh_device_table()

    def _refresh_device_table(self):
        if not hasattr(self, "device_rows_container"):
            return
        for child in self.device_rows_container.winfo_children():
            child.destroy()
        self._device_row_frames.clear()

        devices = self.device_service.list_devices()
        prev_selected = self._selected_device_id
        device_ids = []
        for idx, device in enumerate(devices):
            self._create_device_row(device, idx)
            device_ids.append(device.device_id)

        if prev_selected and prev_selected in device_ids:
            self._selected_device_id = None
            self._select_device_row(prev_selected)
        elif devices:
            self._select_device_row(devices[0].device_id)
        else:
            self._clear_device_selection()

    def _create_device_row(self, device: MockDevice, index: int):
        """Render a single row."""
        row = tk.Frame(self.device_rows_container, bg=Colors.SURFACE_ALT, pady=Spacing.XS)
        row.pack(fill=tk.X, pady=(0, Spacing.XXS), padx=(Spacing.SM, Spacing.SM))
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=2)

        name_label = tk.Label(
            row,
            text=device.name,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
            anchor="center",
            justify="center",
        )
        name_label.grid(row=0, column=0, sticky="ew", padx=(Spacing.SM, 0))

        device_label = tk.Label(
            row,
            text=device.device_id,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            anchor="center",
            justify="center",
        )
        device_label.grid(row=0, column=1, sticky="ew", padx=(Spacing.SM, 0))

        for widget in (row, name_label, device_label):
            widget.bind(
                "<Button-1>",
                lambda event, d=device: self._select_device_row(d.device_id),
            )

        self._device_row_frames[device.device_id] = row

    def _go_to_chat(self):
        """Open the peer chat window and set status to Connected."""
        if self.controller:
            self.controller.status_manager.update_status(AppConfig.STATUS_CONNECTED)
        from .chat_window import ChatWindow
        local_name = getattr(self.session, "local_device_name", "Orion") if self.session else "Orion"
        ChatWindow(self, peer_name=self._active_device_name, local_device_name=local_name)

    def _handle_chat_action(self, device_id: str):
        """Treat the inline action column as a shortcut to the chat flow."""
        device = self.device_service.get_device(device_id)
        if not device:
            return
        self._active_device_id = device.device_id
        self._active_device_name = device.name
        self._select_device_row(device.device_id)
        self._set_stage(DeviceStage.CONNECTED, device.name)
        self._go_to_chat()

    def _handle_global_chat(self):
        """Chat with the currently selected device."""
        if self._selected_device_id:
            self._handle_chat_action(self._selected_device_id)

    def _select_device_row(self, device_id: Optional[str]):
        """Highlight the selected device row and keep it in sync with the action button."""
        if not device_id:
            return
        previous = self._selected_device_id
        if previous and previous in self._device_row_frames:
            self._device_row_frames[previous].configure(bg=Colors.SURFACE_ALT)
        row = self._device_row_frames.get(device_id)
        if row:
            row.configure(bg=Colors.SURFACE_SELECTED)
        self._selected_device_id = device_id
        device = self.device_service.get_device(device_id)
        if device:
            self._active_device_id = device.device_id
            self._active_device_name = device.name

    def _clear_device_selection(self):
        """Clear the visual selection state from the list."""
        if self._selected_device_id and self._selected_device_id in self._device_row_frames:
            self._device_row_frames[self._selected_device_id].configure(bg=Colors.SURFACE_ALT)
        self._selected_device_id = None
        self._active_device_name = None
        self._active_device_id = None

    # ------------------------------------------------------------------ #
    def _scan_for_devices(self):
        if self.is_scanning:
            return
        self.is_scanning = True
        if hasattr(self, "refresh_btn"):
            self.refresh_btn.configure(state="disabled", text="Refreshing…")
        if self.controller:
            self.controller.status_manager.update_status("Scanning…")
        self._set_stage(DeviceStage.SCANNING)
        self._cancel_scan_timer()
        self._scan_timer_id = self.after(2000, self._finish_scan)  # TODO: Make scan duration configurable

    def _finish_scan(self):
        newly_found = self.device_service.simulate_scan()
        if not newly_found:
            self.device_service.refresh()
        self._refresh_device_table()
        self._set_stage(DeviceStage.READY)
        self.is_scanning = False
        if hasattr(self, "refresh_btn"):
            self.refresh_btn.configure(state="normal", text="Refresh")
        if self.controller:
            self.controller.status_manager.update_status(AppConfig.STATUS_READY)
        self._scan_timer_id = None

    def _set_stage(self, stage: DeviceStage, device_name: Optional[str] = None):
        """Update local labels and push consolidated status via the UI store."""
        label = device_name or self._active_device_name
        self.ui_store.set_pairing_stage(stage, label)
        snapshot = self.ui_store.get_device_status()
        self._apply_snapshot(snapshot)
        if label:
            self._active_device_name = label
        if stage == DeviceStage.READY:
            self._active_device_name = None
            self._active_device_id = None
            self._clear_device_selection()
        if self._active_device_id:
            device = self.device_service.get_device(self._active_device_id)
            if device:
                self._select_device_row(device.device_id)

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
            self._clear_device_selection()
            self._active_device_name = None
            self._active_device_id = None
        elif snapshot.device_name:
            self._active_device_name = snapshot.device_name

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