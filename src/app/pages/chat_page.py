"""Signal-style chat experience."""
from __future__ import annotations

import tkinter as tk
import time
from typing import Callable, Optional

from utils.design_system import Colors, Typography, DesignUtils, Space, Spacing
from utils.status_manager import get_status_manager
from utils.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from utils.ui_helpers import enable_global_mousewheel
from .base_page import BasePage, PageContext


class ChatPage(BasePage):
    """Modern chat UI with fixed composer and scrollable history."""

    def __init__(self, master, context: PageContext, on_disconnect=None):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.controller = context.controller if context else None
        self.session = context.session if context else None
        self.host = context.navigator if context else None
        self.on_disconnect = on_disconnect
        self._connected = False
        self.ui_store = get_ui_store()
        self._device_subscription: Optional[Callable[[DeviceStatusSnapshot], None]] = None

        # Status manager still gates message sending
        self.status_manager = get_status_manager()

        wrapper = tk.Frame(self, bg=Colors.SURFACE, padx=Space.XL, pady=Space.XL)
        wrapper.pack(fill=tk.BOTH, expand=True)

        self.shell = tk.Frame(
            wrapper,
            bg=Colors.SURFACE_ALT,
            highlightbackground=Colors.BORDER,
            highlightthickness=1,
            bd=0,
        )
        self.shell.pack(fill=tk.BOTH, expand=True)
        self.shell.grid_rowconfigure(1, weight=1)
        self.shell.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_history()
        self._build_composer()

        self._message_counter = 0
        self._setup_chat_history()
        self._apply_snapshot(self.ui_store.get_device_status())

    # ------------------------------------------------------------------ header
    def _build_header(self):
        header = tk.Frame(
            self.shell,
            bg=Colors.SURFACE_HEADER,
            padx=Space.LG,
            pady=Space.MD,
        )
        header.grid(row=0, column=0, sticky="ew")

        self.connection_badge = tk.Label(
            header,
            text="Disconnected",
            bg=Colors.STATE_ERROR,
            fg=Colors.SURFACE,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_12,
                Typography.WEIGHT_BOLD,
            ),
            padx=Space.MD,
            pady=int(Space.XS / 2),
        )
        self.connection_badge.pack(side=tk.LEFT, padx=(0, Space.SM))

        self.name_label = tk.Label(
            header,
            text="Chat",
            bg=Colors.SURFACE_HEADER,
            fg=Colors.TEXT_PRIMARY,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_18,
                Typography.WEIGHT_BOLD,
            ),
        )
        self.name_label.pack(side=tk.LEFT, expand=True, padx=Space.LG)

        self.disconnect_button = DesignUtils.button(
            header,
            text="Disconnect",
            command=self._handle_disconnect,
            variant="secondary",
            width=16,
        )
        self.disconnect_button.pack(side=tk.RIGHT, padx=(0, Space.SM))

        clear_btn = DesignUtils.button(
            header,
            text="Clear Chat",
            command=self._handle_clear_chat,
            variant="secondary",
            width=12,
        )
        clear_btn.pack(side=tk.RIGHT, padx=(0, Space.SM))

    # ---------------------------------------------------------------- history area
    def _build_history(self):
        container = tk.Frame(self.shell, bg=Colors.SURFACE_ALT)
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._history_canvas = tk.Canvas(
            container,
            bg=Colors.SURFACE_ALT,
            highlightthickness=0,
            bd=0,
        )
        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=self._history_canvas.yview,
        )
        self._history_canvas.configure(yscrollcommand=scrollbar.set)

        self._history_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Frame that will contain all message bubbles
        self.history_frame = tk.Frame(self._history_canvas, bg=Colors.SURFACE_ALT)

        # Keep scrollregion updated when contents change
        self.history_frame.bind(
            "<Configure>",
            lambda e: self._history_canvas.configure(
                scrollregion=self._history_canvas.bbox("all")
            ),
        )

        # Embed the frame into the canvas and remember the window ID
        self._history_window = self._history_canvas.create_window(
            (0, 0),
            window=self.history_frame,
            anchor="nw",
        )

        # IMPORTANT:
        # Make the embedded history_frame always match the canvas width,
        # so right-aligned bubbles go all the way to the right edge.
        def _resize_inner(event):
            self._history_canvas.itemconfig(
                self._history_window,
                width=event.width,
            )

        self._history_canvas.bind("<Configure>", _resize_inner)

        enable_global_mousewheel(self._history_canvas)

    # --------------------------------------------------------------- composer
    def _build_composer(self):
        composer = tk.Frame(
            self.shell,
            bg=Colors.SURFACE_RAISED,
            padx=Space.LG,
            pady=Space.SM,
        )
        composer.grid(row=2, column=0, sticky="ew")
        composer.grid_columnconfigure(0, weight=1)

        self.msg_var = tk.StringVar()
        self.entry = DesignUtils.create_chat_entry(
            composer,
            textvariable=self.msg_var,
        )
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", self._send_message)

        self.send_button = DesignUtils.button(
            composer,
            text="Send",
            command=self._send_message,
            width=10,
        )
        self.send_button.grid(row=0, column=1, padx=(Space.SM, 0))

    # ---------------------------------------------------------------- helpers
    def _setup_chat_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        self._message_counter = 0
        self._add_message(
            "System",
            "Welcome to Locomm Desktop! This is a secure chat interface.",
            is_system=True,
        )

    def _scroll_to_bottom(self):
        self._history_canvas.update_idletasks()
        self._history_canvas.yview_moveto(1.0)

    def _add_message(
        self,
        sender: str,
        message: str,
        is_system: bool = False,
        timestamp: Optional[float] = None,
    ):
        if timestamp is None:
            timestamp = time.time()

        bubble_row = tk.Frame(self.history_frame, bg=Colors.SURFACE_ALT)
        # symmetric horizontal padding so right-align has breathing room
        bubble_row.pack(
            fill=tk.X,
            expand=True,
            pady=(Space.XXS, 0),
            padx=(Space.MD, Space.MD),
        )
        bubble_row.grid_columnconfigure(0, weight=1)

        is_self = sender == self._get_local_device_name() and not is_system

        bubble_bg = (
            Colors.MESSAGE_BUBBLE_SYSTEM_BG
            if is_system
            else Colors.BUTTON_PRIMARY_BG
            if is_self
            else Colors.STATE_SUCCESS
        )
        fg = (
            Colors.TEXT_PRIMARY
            if is_system
            else Colors.SURFACE
            if is_self
            else Colors.SURFACE
        )

        pad_x = max(4, int(Space.MD * 0.7))
        pad_y = max(2, int(Space.XS * 0.7))

        # Dynamic wrap length based on canvas width, with fallback
        canvas_width = self._history_canvas.winfo_width()
        wrap_length = (
            max(300, int(canvas_width * 0.7)) if canvas_width > 1 else 360
        )

        bubble = tk.Frame(bubble_row, bg=bubble_bg, padx=pad_x, pady=pad_y)

        if is_self:
            bubble.grid(
                row=0,
                column=0,
                sticky="e",
                padx=(0, 0),
                pady=(0, 0),
            )
        else:
            bubble.grid(
                row=0,
                column=0,
                sticky="w",
                padx=(Spacing.LG, 0),
                pady=(0, 0),
            )

        caption_fg = Colors.SURFACE if is_self else Colors.TEXT_MUTED
        sender_anchor = "e" if is_self else "w"
        tk.Label(
            bubble,
            text=sender,
            bg=bubble_bg,
            fg=caption_fg,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_12,
                Typography.WEIGHT_MEDIUM,
            ),
        ).pack(anchor=sender_anchor)

        msg_anchor = "e" if is_self else "w"
        msg_justify = "right" if is_self else "left"
        tk.Label(
            bubble,
            text=message,
            bg=bubble_bg,
            fg=fg if not is_system else Colors.TEXT_SECONDARY,
            wraplength=wrap_length,
            justify=msg_justify,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_14,
                Typography.WEIGHT_REGULAR,
            ),
        ).pack(anchor=msg_anchor, pady=(Space.XXS, 0))

        timestamp_fg = Colors.SURFACE if is_self else Colors.TEXT_MUTED
        tk.Label(
            bubble,
            text=time.strftime("%H:%M", time.localtime(timestamp)),
            bg=bubble_bg,
            fg=timestamp_fg,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_12,
                Typography.WEIGHT_REGULAR,
            ),
        ).pack(anchor=msg_anchor)

        # Update scroll region and scroll to bottom
        self._history_canvas.configure(
            scrollregion=self._history_canvas.bbox("all")
        )
        self._scroll_to_bottom()

        if not is_system:
            self._message_counter += 1

    # ---------------------------------------------------------------- actions
    def _handle_disconnect(self):
        if self.on_disconnect:
            self.on_disconnect()

    def _handle_connect(self):
        # Placeholder for connect action - implement based on controller
        pass

    def _handle_clear_chat(self):
        self.clear_history()

    def _handle_attach(self):
        # Placeholder for future file picker
        pass

    def _send_message(self, event=None):
        """Send message - use consolidated status manager to check connectivity."""
        if not self.status_manager.can_send_messages() or not self._connected:
            return "break"

        message = self.msg_var.get().strip()
        if not message:
            return "break"

        if self.controller:
            try:
                self.controller.send_message(message)
                # Connection state is managed by _apply_snapshot, not here
            except Exception as e:
                print(f"Send error: {e}")
                return "break"
        else:
            print("Warning: No controller available for sending message")
            return "break"

        self._add_message(self._get_local_device_name(), message, timestamp=time.time())
        self.msg_var.set("")
        return "break"

    # ---------------------------------------------------------------- API hooks
    def append_line(
        self,
        sender: str,
        message: str,
        timestamp: Optional[float] = None,
    ):
        self._add_message(sender, message, timestamp=timestamp)

    def sync_session_info(self):
        if self.session:
            contact = getattr(self.session, "device_name", None) or "None"
        else:
            contact = "None"
        self.name_label.configure(text=contact)

    def set_status(self, text: str):
        """Set status using the consolidated status manager for consistency."""
        self.connection_badge.configure(text=text)

    def clear_history(self):
        self._setup_chat_history()

    def get_history_lines(self) -> list[str]:
        lines = []
        for bubble in self.history_frame.winfo_children():
            for child in bubble.winfo_children():
                if isinstance(child, tk.Frame):
                    for inner in child.winfo_children():
                        if isinstance(inner, tk.Label):
                            lines.append(inner.cget("text"))
        return lines

    def _get_local_device_name(self) -> str:
        return getattr(self.session, "local_device_name", "Orion") or "Orion"

    # ------------------------------------------------------------------ lifecycle & store
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

        badge_text, badge_color = self._badge_style_for_stage(snapshot.stage)
        self.connection_badge.configure(
            text=badge_text,
            bg=badge_color,
            fg=Colors.SURFACE,
        )

        is_connected = snapshot.stage == DeviceStage.CONNECTED
        self._connected = is_connected

        if hasattr(self, "disconnect_button"):
            self.disconnect_button.configure(
                text="Disconnect" if is_connected else "Connect",
                command=(
                    self._handle_disconnect
                    if is_connected
                    else self._handle_connect
                ),
            )

        entry_state = tk.NORMAL if is_connected else tk.DISABLED
        self.entry.configure(state=entry_state)

        if self.send_button:
            self.send_button.configure(
                state="normal" if is_connected else "disabled"
            )

        remote_label = (
            snapshot.device_name
            if is_connected and snapshot.device_name
            else "None"
        )
        self.name_label.configure(text=remote_label)

    @staticmethod
    def _badge_style_for_stage(stage: DeviceStage) -> tuple[str, str]:
        mapping = {
            DeviceStage.READY: ("Ready", Colors.STATE_INFO),
            DeviceStage.SCANNING: ("Scanning", Colors.STATE_INFO),
            DeviceStage.AWAITING_PIN: ("Awaiting PIN", Colors.STATE_WARNING),
            DeviceStage.CONNECTING: ("Connecting", Colors.STATE_INFO),
            DeviceStage.CONNECTED: ("Connected", Colors.STATE_SUCCESS),
            DeviceStage.DISCONNECTED: ("Disconnected", Colors.STATE_ERROR),
        }
        return mapping.get(stage, mapping[DeviceStage.READY])

    def destroy(self):
        self._unsubscribe_from_store()
        return super().destroy()
