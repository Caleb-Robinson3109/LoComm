"""Slim chatroom pairing UI that accepts a single dashed 20-character code."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from utils.design_system import AppConfig, Colors, DesignUtils, Spacing, Typography, Space
from utils.pin_authentication import generate_chatroom_code
from utils.chatroom_registry import set_active_chatroom
from utils.state.status_manager import get_status_manager


class ChatroomWindow(tk.Frame):
    """Single-entry chatroom pairing interface with a "My Chatroom" section."""

    def __init__(self, master, on_chatroom_success: Callable[[str], None]):
        super().__init__(master, bg=Colors.SURFACE)
        self.on_chatroom_success = on_chatroom_success
        self._entry_var = tk.StringVar()
        self._error_label: Optional[tk.Label] = None
        self._waiting = False
        self._current_chatroom_code: Optional[str] = None
        self._code_display: Optional[tk.Label] = None

        self._create_ui()

    def _create_ui(self):
        layout = tk.Frame(self, bg=Colors.SURFACE, padx=Spacing.SM, pady=Spacing.SM)
        layout.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            layout,
            text="Chatroom",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="center")

        tk.Label(
            layout,
            text="Join Chatroom",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD),
        ).pack(anchor="e", fill=tk.X)

        tk.Label(
            layout,
            text="Paste or type the 20-character code below.",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12),
        ).pack(anchor="w", pady=(Spacing.XXS, Spacing.SM))

        self.entry_widget = DesignUtils.create_chat_entry(
            layout,
            textvariable=self._entry_var,
            font=(Typography.FONT_MONO, Typography.SIZE_16, Typography.WEIGHT_BOLD),
            justify="center",
            width=20,
        )
        self.entry_widget.pack(fill=tk.X, pady=(0, Spacing.XS))
        self.entry_widget.bind("<KeyRelease>", self._on_code_key)
        self.entry_widget.bind("<Return>", self._on_submit_chatroom_code)
        self.entry_widget.focus_set()

        helper = tk.Label(
            layout,
            text="Format: ABCDE-FGHIJ-KLMNO-PQRST",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_10),
        )
        helper.pack(anchor="w", pady=(0, Spacing.XXS))

        actions = tk.Frame(layout, bg=Colors.SURFACE)
        actions.pack(fill=tk.X, pady=(Spacing.SM, 0))

        self.clear_btn = DesignUtils.button(
            actions,
            text="Clear",
            variant="secondary",
            width=12,
            command=self._clear_entry,
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        self.enter_btn = DesignUtils.button(
            actions,
            text="Join",
            variant="primary",
            width=14,
            command=self._on_submit_chatroom_code,
        )
        self.enter_btn.pack(side=tk.RIGHT)
        self.enter_btn.configure(state="disabled")

        self._error_label = tk.Label(
            layout,
            text="",
            bg=Colors.SURFACE,
            fg=Colors.STATE_ERROR,
            font=(Typography.FONT_UI, Typography.SIZE_10),
        )
        self._error_label.pack(fill=tk.X, pady=(Spacing.XXS, 0))

        self._build_my_chatroom_section(layout)

    def _build_my_chatroom_section(self, parent: tk.Frame):
        section = tk.Frame(parent, bg=Colors.SURFACE, pady=Spacing.SM)
        section.pack(fill=tk.X)

        tk.Label(
            section,
            text="My Chatroom",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD),
        ).pack(anchor="e", fill=tk.X)

        self._code_display = tk.Label(
            section,
            text="No chatroom created yet.",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_ACCENT or Colors.STATE_INFO,
            font=(Typography.FONT_MONO, Typography.SIZE_14),
        )
        self._code_display.pack(anchor="w", pady=(Spacing.XXS, 0))

        create_btn = DesignUtils.button(
            section,
            text="Create",
            variant="primary",
            width=20,
            command=self._create_chatroom_code,
        )
        create_btn.pack(anchor="e", pady=(Spacing.SM, 0))

    def _on_code_key(self, event):
        raw = ''.join(ch for ch in self._entry_var.get() if ch.isalnum())[:20]
        formatted = '-'.join(raw[i:i+5] for i in range(0, len(raw), 5))
        formatted = formatted.upper()
        if formatted != self._entry_var.get():
            self._entry_var.set(formatted)
        self._error_label.configure(text="")
        self.enter_btn.configure(state="normal" if len(raw) == 20 else "disabled")

    def _on_submit_chatroom_code(self, event=None):
        code = ''.join(ch for ch in self._entry_var.get() if ch.isalnum()).upper()
        if len(code) != 20:
            self._show_error("Please enter all 20 alphanumeric characters.")
            return
        if self._waiting:
            return
        self._set_waiting(True)
        get_status_manager().update_status("Connecting…")
        self.after(300, lambda: self._complete_success(code))

    def _complete_success(self, code: str):
        self._set_waiting(False)
        if self.on_chatroom_success:
            get_status_manager().update_status(AppConfig.STATUS_READY)
            self.on_chatroom_success(code)

    def _clear_entry(self):
        self._entry_var.set("")
        self.enter_btn.configure(state="disabled")

    def focus_input(self):
        self._entry_var.set("")
        self.enter_btn.configure(state="disabled")
        self.after(50, lambda: self.entry_widget.focus_set())

    def _create_chatroom_code(self):
        code = generate_chatroom_code()
        formatted = self._format_code(code)
        self._current_chatroom_code = formatted
        if self._code_display:
            self._code_display.configure(text=formatted)
        set_active_chatroom(code, [])
        get_status_manager().update_status(AppConfig.STATUS_READY)

    def _format_code(self, code: str) -> str:
        clean = ''.join(ch for ch in code if ch.isalnum()).upper()
        return '-'.join(clean[i:i+5] for i in range(0, len(clean), 5))

    def _show_error(self, message: str):
        self._error_label.configure(text=message)
        get_status_manager().update_status(AppConfig.STATUS_CONNECTION_FAILED)
        self._set_waiting(False)

    def _set_waiting(self, waiting: bool):
        self._waiting = waiting
        state = "disabled" if waiting else "normal"
        self.enter_btn.configure(state=state, text="Entering…" if waiting else "Enter Chatroom")
