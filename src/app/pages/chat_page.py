"""Signal-style chat experience."""
from __future__ import annotations

import tkinter as tk
import time
from typing import Callable, Optional

from utils.design_system import Colors, Typography, DesignUtils, Space
from utils.status_manager import get_status_manager
from utils.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
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

        self.shell = tk.Frame(wrapper, bg=Colors.SURFACE_ALT, highlightbackground=Colors.BORDER,
                              highlightthickness=1, bd=0)
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
        header = tk.Frame(self.shell, bg=Colors.SURFACE_HEADER, padx=Space.LG, pady=Space.MD)
        header.grid(row=0, column=0, sticky="ew")

        left = tk.Frame(header, bg=Colors.SURFACE_HEADER)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        contact = "Chat"
        self.name_label = tk.Label(left, text=contact, bg=Colors.SURFACE_HEADER, fg=Colors.TEXT_PRIMARY,
                                   font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD))
        self.name_label.pack(anchor="w")

        right = tk.Frame(header, bg=Colors.SURFACE_HEADER)
        right.pack(side=tk.RIGHT)

        self.connection_badge = tk.Label(
            right,
            text="Disconnected",
            bg=Colors.STATE_ERROR,
            fg=Colors.SURFACE,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
            padx=Space.MD,
            pady=int(Space.XS / 2)
        )
        self.connection_badge.pack(side=tk.RIGHT, padx=(Space.SM, 0))

        button_row = tk.Frame(right, bg=Colors.SURFACE_HEADER)
        button_row.pack(side=tk.RIGHT, padx=(0, Space.SM))
        DesignUtils.button(
            button_row,
            text="Clear Chat",
            command=self._handle_clear_chat,
            variant="ghost",
            width=12
        ).pack(side=tk.RIGHT, padx=(Space.SM, 0))
        DesignUtils.button(
            button_row,
            text="Disconnect",
            command=self._handle_disconnect,
            variant="secondary",
            width=12
        ).pack(side=tk.RIGHT)

    # ---------------------------------------------------------------- history area
    def _build_history(self):
        container = tk.Frame(self.shell, bg=Colors.SURFACE_ALT)
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._history_canvas = tk.Canvas(container, bg=Colors.SURFACE_ALT, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self._history_canvas.yview)
        self._history_canvas.configure(yscrollcommand=scrollbar.set)
        self._history_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.history_frame = tk.Frame(self._history_canvas, bg=Colors.SURFACE_ALT)
        self.history_frame.bind("<Configure>", lambda e: self._history_canvas.configure(scrollregion=self._history_canvas.bbox("all")))
        self._history_canvas.create_window((0, 0), window=self.history_frame, anchor="nw")
        self._history_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._history_canvas.bind("<Button-4>", self._on_mousewheel)
        self._history_canvas.bind("<Button-5>", self._on_mousewheel)

    # --------------------------------------------------------------- composer
    def _build_composer(self):
        composer = tk.Frame(self.shell, bg=Colors.SURFACE_RAISED, padx=Space.LG, pady=Space.SM)
        composer.grid(row=2, column=0, sticky="ew")
        composer.grid_columnconfigure(0, weight=1)

        self.msg_var = tk.StringVar()
        self.entry = DesignUtils.create_chat_entry(composer, textvariable=self.msg_var)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", self._send_message)

        self.send_button = DesignUtils.button(composer, text="Send", command=self._send_message, width=10)
        self.send_button.grid(row=0, column=1, padx=(Space.SM, 0))

    # ---------------------------------------------------------------- helpers
    def _setup_chat_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        self._message_counter = 0
        self._add_message("System", "Welcome to Locomm Desktop! This is a secure chat interface.", is_system=True)

    def _scroll_to_bottom(self):
        self._history_canvas.update_idletasks()
        self._history_canvas.yview_moveto(1.0)

    def _add_message(self, sender: str, message: str, is_system: bool = False):
        bubble_row = tk.Frame(self.history_frame, bg=Colors.SURFACE_ALT)
        bubble_row.pack(fill=tk.X, pady=(Space.XXS, 0), padx=Space.MD)

        is_self = sender == self._get_local_device_name() and not is_system
        if is_system:
            bubble_bg = Colors.MESSAGE_BUBBLE_SYSTEM_BG
            fg = Colors.TEXT_PRIMARY
        elif is_self:
            bubble_bg = Colors.MESSAGE_BUBBLE_OWN_BG
            fg = Colors.SURFACE
        else:
            bubble_bg = Colors.MESSAGE_BUBBLE_OTHER_BG
            fg = Colors.TEXT_PRIMARY
        anchor = "e" if is_self else "w"
        bubble = tk.Frame(bubble_row, bg=Colors.SURFACE_ALT)
        bubble.pack(anchor=anchor, fill=tk.X if is_system else tk.NONE)
        inner = tk.Frame(bubble, bg=bubble_bg, padx=Space.MD, pady=Space.XS)
        inner.pack(anchor=anchor, padx=(0 if is_self else Space.LG, Space.LG if is_self else 0))
        tk.Label(inner, text=sender, bg=bubble_bg, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w")
        tk.Label(inner, text=message, bg=bubble_bg, fg=fg if not is_system else Colors.TEXT_SECONDARY,
                 wraplength=520, justify="left",
                 font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR)).pack(anchor="w", pady=(Space.XXS, 0))
        tk.Label(inner, text=time.strftime("%H:%M"), bg=bubble_bg, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="e")

        self._scroll_to_bottom()
        if not is_system:
            self._message_counter += 1

    def _on_mousewheel(self, event):
        delta = 0
        if hasattr(event, "delta") and event.delta:
            delta = -1 * (event.delta / 120)
        elif event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        self._history_canvas.yview_scroll(int(delta), "units")

    # ---------------------------------------------------------------- actions
    def _handle_disconnect(self):
        if self.on_disconnect:
            self.on_disconnect()

    def _handle_clear_chat(self):
        self.clear_history()

    def _handle_attach(self):
        pass  # Placeholder for future file picker

    def _send_message(self, event=None):
        """Send message - use consolidated status manager to check connectivity."""
        if not self.status_manager.can_send_messages() or not self._connected:
            return "break"

        message = self.msg_var.get().strip()
        if not message:
            return "break"

        try:
            self.controller.send_message(message)
            self._connected = True
        except Exception as e:
            print(f"Send error: {e}")
            return "break"

        self._add_message(self._get_local_device_name(), message)
        self.msg_var.set("")
        return "break"

    # ---------------------------------------------------------------- API hooks
    def append_line(self, sender: str, message: str):
        self._add_message(sender, message)

    def sync_session_info(self):
        contact = self.session.device_name or "Conversation"
        self.name_label.configure(text=contact)

    def set_status(self, text: str):
        """
        Set status using the consolidated status manager for consistency.
        """
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
        return getattr(self.session, "device_name", None) or "This Device"

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
        self.connection_badge.configure(text=badge_text, bg=badge_color, fg=Colors.SURFACE)
        is_connected = snapshot.stage == DeviceStage.CONNECTED
        self._connected = is_connected
        entry_state = tk.NORMAL if is_connected else tk.DISABLED
        self.entry.configure(state=entry_state)
        if self.send_button:
            self.send_button.configure(state="normal" if is_connected else "disabled")

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
