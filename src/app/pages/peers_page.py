"""Peers page component matching chat-style design."""
from __future__ import annotations

import tkinter as tk
from typing import Optional, Callable

from ui.components import DesignUtils
from ui.theme_tokens import Colors, Spacing, Typography, Space, AppConfig
from utils.state.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from ui.helpers import create_scroll_container, enable_global_mousewheel
from ui.theme_manager import ThemeManager
from .base_page import BasePage, PageContext


class PeersPage(BasePage):
    """Devices page with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext, on_device_paired: Optional[Callable] = None):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.controller = context.controller if context else None
        self.session = context.session if context else None
        self.host = context.navigator if context else None
        self.on_device_paired = on_device_paired

        self.ui_store = get_ui_store()
        # Mock service removed
        self._device_subscription: Optional[Callable[[DeviceStatusSnapshot], None]] = None
        self.is_scanning = False
        self._active_device_name: Optional[str] = None
        self._active_device_id: Optional[str] = None
        self._selected_device_id: Optional[str] = None
        self._device_row_frames: dict[str, tk.Frame] = {}
        self._scan_timer_id: Optional[str] = None
        self._theme_listener = None

        # Simple scroll container like chat page
        self._scroll_container = create_scroll_container(
            self, 
            bg=Colors.SURFACE, 
            padding=(0, Spacing.LG)
        )
        self._body = self._scroll_container.frame

        self._build_title(self._body)
        self._build_devices_section(self._body)

        # Reflect whatever the store currently knows about the connection state
        self._apply_snapshot(self.ui_store.get_device_status())
        
        self._theme_listener = self._apply_theme
        ThemeManager.register_theme_listener(self._theme_listener)
        self._apply_theme()

    def _build_title(self, parent):
        """Build simple title section like chat page."""
        self._title_wrap = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
        )
        self._title_wrap.pack(fill=tk.X, pady=(0, Space.XS))

        self._text_wrap = tk.Frame(self._title_wrap, bg=Colors.SURFACE)
        self._text_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._action_wrap = tk.Frame(self._title_wrap, bg=Colors.SURFACE)
        self._action_wrap.pack(side=tk.RIGHT)

        self._title_label = tk.Label(
            self._text_wrap,
            text="Peers",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        )
        self._title_label.pack(anchor="w")

        self._subtitle_label = tk.Label(
            self._text_wrap,
            text="Manage your peers and device sessions",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        )
        self._subtitle_label.pack(anchor="w", pady=(Space.XXS, 0))

        self._separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        self._separator.pack(fill=tk.X, pady=(0, Space.SM))

        self.refresh_btn = DesignUtils.button(
            self._action_wrap,
            text="Refresh",
            variant="secondary",
            command=self._scan_for_devices,
        )
        self.refresh_btn.pack()

    def _build_devices_section(self, parent):
        """Build clean devices section."""
        self._devices_content = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Space.LG,
            pady=Space.MD,
        )
        self._devices_content.pack(fill=tk.BOTH, expand=True)
        
        # Section title
        self._section_title = tk.Label(
            self._devices_content,
            text="Available Peers",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        )
        self._section_title.pack(anchor="w", pady=(0, Spacing.SM))
        
        # Device list
        self._list_frame = tk.Frame(self._devices_content, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.MD)
        self._list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, Space.SM))
        
        self._build_device_list(self._list_frame)

    def _go_to_chat(self):
        """Open the peer chat window and set status to Connected."""
        if self.controller:
            self.controller.status_manager.update_status(AppConfig.STATUS_CONNECTED)
        from .chat_window import ChatWindow
        local_name = getattr(self.session, "local_device_name", "Orion") if self.session else "Orion"
        ChatWindow(self, peer_name=self._active_device_name, local_device_name=local_name)

    def _handle_chat_action(self, device_id: str):
        """Treat the inline action column as a shortcut to the chat flow."""
        # Mock device lookup removed
        # device = self.device_service.get_device(device_id)
        # if not device:
        #     return
        # self._active_device_id = device.device_id
        # self._active_device_name = device.name
        # self._select_device_row(device.device_id)
        # self._set_stage(DeviceStage.CONNECTED, device.name)
        # self._go_to_chat()
        pass

    def _build_device_list(self, parent):
        """Build simple device list with an action column button."""
        header = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        header.pack(fill=tk.X, pady=(0, Spacing.XXS))
        header.grid_columnconfigure(0, weight=3)
        header.grid_columnconfigure(1, weight=2)
        header.grid_columnconfigure(2, weight=1)

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
        tk.Label(
            header,
            text="Action",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
            anchor="center",
        ).grid(row=0, column=2, sticky="ew")

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

        # Mock devices removed
        devices = []
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

    def _create_device_row(self, device, index: int):
        """Render a single row with a chat action button."""
        row = tk.Frame(self.device_rows_container, bg=Colors.SURFACE_ALT, pady=Spacing.XS)
        row.pack(fill=tk.X, pady=(0, Spacing.XXS), padx=(Spacing.SM, Spacing.SM))
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=2)
        row.grid_columnconfigure(2, weight=1)

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

        chat_btn = DesignUtils.button(
            row,
            text="Chat",
            command=lambda d=device: self._handle_chat_action(d.device_id),
            variant="primary",
            width=10,
        )
        chat_btn.grid(row=0, column=2, sticky="e", padx=(Spacing.SM, Spacing.SM))

        for widget in (row, name_label, device_label):
            widget.bind(
                "<Button-1>",
                lambda event, d=device: self._select_device_row(d.device_id),
            )

        self._device_row_frames[device.device_id] = row

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
        # Mock device lookup removed
        # device = self.device_service.get_device(device_id)
        # if device:
        #     self._active_device_id = device.device_id
        #     self._active_device_name = device.name

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
        # Mock scan removed
        # newly_found = self.device_service.simulate_scan()
        # if not newly_found:
        #     self.device_service.refresh()
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
            # Mock device lookup removed
            # device = self.device_service.get_device(self._active_device_id)
            # if device:
            #     self._select_device_row(device.device_id)
            pass

    # ------------------------------------------------------------------ #
    def on_show(self):
        self.configure(bg=Colors.SURFACE)
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
        if self._theme_listener:
            ThemeManager.unregister_theme_listener(self._theme_listener)
            self._theme_listener = None
        self._cancel_scan_timer()
        self._unsubscribe_from_store()
        return super().destroy()

    def _apply_theme(self):
        surface = Colors.SURFACE
        self.configure(bg=surface)
        
        # Update Scroll Container
        if self._scroll_container:
            if self._scroll_container.wrapper.winfo_exists():
                self._scroll_container.wrapper.configure(bg=surface)
            if self._scroll_container.canvas.winfo_exists():
                self._scroll_container.canvas.configure(bg=surface)
            if self._scroll_container.frame.winfo_exists():
                self._scroll_container.frame.configure(bg=surface)
            if self._scroll_container.scrollbar.winfo_exists():
                self._scroll_container.scrollbar.configure(bg=surface, troughcolor=surface, activebackground=surface)
        
        # Update Title Section
        frames = [self._title_wrap, self._text_wrap, self._action_wrap, self._devices_content]
        for frame in frames:
            if frame and frame.winfo_exists():
                frame.configure(bg=surface)
                
        if self._title_label and self._title_label.winfo_exists():
            self._title_label.configure(bg=surface, fg=Colors.TEXT_PRIMARY)
        if self._subtitle_label and self._subtitle_label.winfo_exists():
            self._subtitle_label.configure(bg=surface, fg=Colors.TEXT_SECONDARY)
        if self._separator and self._separator.winfo_exists():
            self._separator.configure(bg=Colors.DIVIDER)
            
        # Update Devices Section
        if self._section_title and self._section_title.winfo_exists():
            self._section_title.configure(bg=surface, fg=Colors.TEXT_PRIMARY)
        if self._list_frame and self._list_frame.winfo_exists():
            self._list_frame.configure(bg=Colors.SURFACE_ALT)
            
        # Refresh table content to apply theme to rows
        self._refresh_device_table()

    def _cancel_scan_timer(self):
        """Cancel any pending scan timer to avoid callbacks after destruction."""
        if self._scan_timer_id:
            try:
                self.after_cancel(self._scan_timer_id)
            except Exception:
                pass
            self._scan_timer_id = None

PairPage = PeersPage
