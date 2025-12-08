"""Unified chatroom pairing UI with a single entry and inline generation."""
from __future__ import annotations

import os
import sys
import tkinter as tk
from typing import Callable, Dict, Optional

from utils.chatroom_registry import clear_chatroom, get_active_members, set_active_chatroom
from utils.design_system import AppConfig, Colors, DesignUtils, Spacing, Typography
from utils.pin_authentication import generate_chatroom_code
from utils.state.status_manager import get_status_manager
from ui.helpers import create_page_header, create_scroll_container

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api")))
from LoCommAPI import enter_pairing_key  # noqa: E402


class ChatroomPage(tk.Frame):
    """Single-pane chatroom pairing UI."""

    def __init__(self, master, on_chatroom_success: Callable[[str], None]):
        super().__init__(master, bg=Colors.SURFACE)
        self.on_chatroom_success = on_chatroom_success
        self._entry_var = tk.StringVar()
        self._error_label: Optional[tk.Label] = None
        self._waiting = False
        self._current_chatroom_code: Optional[str] = None
        self.entry_widget: Optional[tk.Entry] = None
        self.enter_btn: Optional[tk.Button] = None
        self.generate_btn: Optional[tk.Button] = None
        self.disconnect_btn: Optional[tk.Button] = None
        self._chatroom_connected = False

        self._create_ui()

    def _create_ui(self):
        scroll = create_scroll_container(
            self,
            bg=Colors.SURFACE,
            padding=(0, Spacing.LG),
        )
        layout = scroll.frame

        header_action_refs: Dict[str, tk.Button] = {}
        create_page_header(
            layout,
            title="Chatroom",
            subtitle="Enter a chatroom with a 20-digit code.",
            actions=[
                {
                    "key": "disconnect",
                    "text": "Disconnect",
                    "variant": "secondary",
                    "command": self._disconnect_from_chatroom,
                    "width": 10,
                    "padx": (Spacing.XXS, 0),
                }
            ],
            action_refs=header_action_refs,
            padx=Spacing.LG,
        )
        self.disconnect_btn = header_action_refs.get("disconnect")
        self._update_disconnect_button_style()
        if self.disconnect_btn:
            # Align with header controls
            self.disconnect_btn.configure(anchor="center")

        body = tk.Frame(layout, bg=Colors.SURFACE)
        body.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=(Spacing.SM, Spacing.LG))

        entry_row = tk.Frame(body, bg=Colors.SURFACE)
        entry_row.pack(fill=tk.X, pady=(Spacing.MD, Spacing.SM))

        self.entry_widget = DesignUtils.create_chat_entry(
            entry_row,
            textvariable=self._entry_var,
            font=(Typography.FONT_MONO, Typography.SIZE_16, Typography.WEIGHT_BOLD),
            justify="center",
            width=28,
        )
        self.entry_widget.pack(fill=tk.X)
        self.entry_widget.bind("<KeyRelease>", self._on_code_key)
        self.entry_widget.bind("<Return>", self._on_submit_chatroom_code)
        self.entry_widget.focus_set()

        button_row = tk.Frame(body, bg=Colors.SURFACE)
        button_row.pack(fill=tk.X, pady=(Spacing.SM, Spacing.SM))
        for idx in range(3):
            button_row.columnconfigure(idx, weight=1)

        btn_width = 12

        self.generate_btn = DesignUtils.button(
            button_row,
            text="Generate",
            variant="secondary",
            width=btn_width,
            command=self._create_chatroom_code,
        )
        self.generate_btn.grid(row=0, column=0, sticky="ew", padx=(0, Spacing.SM))

        self.clear_btn = DesignUtils.button(
            button_row,
            text="Clear",
            variant="secondary",
            width=btn_width,
            command=lambda: self._entry_var.set(""),
        )
        self.clear_btn.grid(row=0, column=1, sticky="ew", padx=(0, Spacing.SM))

        self.enter_btn = DesignUtils.button(
            button_row,
            text="Enter",
            variant="primary",
            width=btn_width,
            command=self._on_submit_chatroom_code,
        )
        self.enter_btn.grid(row=0, column=2, sticky="ew")
        self.enter_btn.configure(state="disabled")

        self._error_label = tk.Label(
            body,
            text="",
            bg=Colors.SURFACE,
            fg=Colors.STATE_ERROR,
            font=(Typography.FONT_UI, Typography.SIZE_10),
        )
        self._error_label.pack(fill=tk.X, pady=(Spacing.XS, 0))

    def _on_code_key(self, event):
        raw = "".join(ch for ch in self._entry_var.get() if ch.isalnum())[:20]
        formatted = "-".join(raw[i : i + 5] for i in range(0, len(raw), 5)).upper()
        if formatted != self._entry_var.get():
            self._entry_var.set(formatted)
        self._error_label.configure(text="")
        if self.enter_btn:
            self.enter_btn.configure(state="normal" if len(raw) == 20 else "disabled")

    def _on_submit_chatroom_code(self, event=None):
        if self._waiting:
            return
        code = "".join(ch for ch in self._entry_var.get() if ch.isalnum()).upper()
        if len(code) != 20:
            self._show_error("Please enter all 20 alphanumeric characters.")
            return
        self._set_waiting(True)
        status_mgr = get_status_manager()
        status_mgr.update_status("Connecting…")
        try:
            result = enter_pairing_key(code)
        except Exception:
            self._show_error("Unable to send chatroom code to device. Please try again.")
            return

        if result is False:
            self._show_error("Pairing code rejected by device. Please verify and retry.")
            return

        self._complete_success(code)

    def _complete_success(self, code: str):
        self._set_waiting(False)
        if self.on_chatroom_success:
            get_status_manager().update_status(AppConfig.STATUS_READY)
            set_active_chatroom(code, get_active_members())
            self._chatroom_connected = True
            self._update_disconnect_button_style()
            self.on_chatroom_success(code)

    def focus_input(self):
        self.entry_widget and self.entry_widget.focus_set()
        self._entry_var.set("")
        if self.enter_btn:
            self.enter_btn.configure(state="disabled")

    def _create_chatroom_code(self):
        code = generate_chatroom_code()
        formatted = self._format_code(code)
        self._current_chatroom_code = formatted
        self._entry_var.set(formatted)
        if self.entry_widget:
            self.entry_widget.focus_set()
        if self.enter_btn:
            self.enter_btn.configure(state="normal")
        self._error_label and self._error_label.configure(text="")

    def _disconnect_from_chatroom(self):
        clear_chatroom()
        get_status_manager().update_status(AppConfig.STATUS_DISCONNECTED)
        self._current_chatroom_code = None
        self._entry_var.set("")
        if self.enter_btn:
            self.enter_btn.configure(state="disabled")
        if self.generate_btn:
            self.generate_btn.configure(state="normal")
        if self.entry_widget:
            self.entry_widget.focus_set()
        self._chatroom_connected = False
        self._update_disconnect_button_style()

    def _format_code(self, code: str) -> str:
        clean = "".join(ch for ch in code if ch.isalnum()).upper()
        return "-".join(clean[i : i + 5] for i in range(0, len(clean), 5))

    def _show_error(self, message: str):
        if self._error_label:
            self._error_label.configure(text=message)
        get_status_manager().update_status(AppConfig.STATUS_CONNECTION_FAILED)
        self._set_waiting(False)

    def _set_waiting(self, waiting: bool):
        self._waiting = waiting
        state = "disabled" if waiting else "normal"
        if self.enter_btn:
            self.enter_btn.configure(state=state, text="Entering…" if waiting else "Enter")
        if self.generate_btn:
            self.generate_btn.configure(state=state)

    def _update_disconnect_button_style(self):
        if not self.disconnect_btn:
            return
        if self._chatroom_connected:
            # Active chatroom: show danger styling
            self.disconnect_btn.configure(
                state="normal",
                style="Locomm.Danger.TButton",
                cursor="hand2",
                takefocus=False,
            )
        else:
            # No chatroom: neutral styling and disabled
            self.disconnect_btn.configure(
                state="disabled",
                style="TButton",
                cursor="arrow",
                takefocus=False,
            )
