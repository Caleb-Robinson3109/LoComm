"""
Window for manually pairing with a device by entering Name and ID.
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from ui.helpers import create_centered_modal, create_form_row
from utils.window_sizing import get_manual_pair_modal_size


class ManualPairingWindow:
    """Window dialog for manual device pairing."""

    def __init__(
        self,
        parent: tk.Misc,
        on_pair: Callable[[str, str], None],
        on_close: Optional[Callable[[], None]] = None,
    ):
        self.parent = parent
        self.on_pair = on_pair
        self.on_close = on_close

        self.device_name_var = tk.StringVar()
        self.device_id_var = tk.StringVar()

        self.window_scaffold = None
        self.pair_btn: Optional[tk.Widget] = None
        self.device_name_entry: Optional[tk.Entry] = None
        self.device_id_entry: Optional[tk.Entry] = None

        self._create_window()

    def _create_window(self):
        self.window_scaffold = create_centered_modal(
            self.parent,
            title="Manual Pair",
            window_size=get_manual_pair_modal_size(),
        )
        self.window_scaffold.toplevel.protocol("WM_DELETE_WINDOW", self.close)

        content_frame = self.window_scaffold.body

        # Device Name Input
        _, self.device_name_entry = create_form_row(
            content_frame,
            label="Device Name",
            widget_factory=lambda p: DesignUtils.create_chat_entry(
                p,
                textvariable=self.device_name_var,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ),
            help_text="Enter a friendly name for this device."
        )

        # Device ID Input
        _, self.device_id_entry = create_form_row(
            content_frame,
            label="Device ID",
            widget_factory=lambda p: DesignUtils.create_chat_entry(
                p,
                textvariable=self.device_id_var,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ),
            help_text="Enter the unique ID of the device."
        )

        # Buttons
        btn_frame = tk.Frame(content_frame, bg=Colors.SURFACE)
        btn_frame.pack(fill=tk.X, pady=(Spacing.LG, 0))

        DesignUtils.button(
            btn_frame,
            text="Cancel",
            command=self.close,
            variant="secondary",
            width=9
        ).pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        self.pair_btn = DesignUtils.button(
            btn_frame,
            text="Pair",
            command=self._on_pair_click,
            variant="primary",
            width=9
        )
        self.pair_btn.pack(side=tk.RIGHT)

        # Bind Enter key
        self.window_scaffold.toplevel.bind("<Return>", lambda e: self._on_pair_click())
        self.window_scaffold.toplevel.bind("<Escape>", lambda e: self.close())
        # Focus first field immediately
        self.window_scaffold.toplevel.after(0, self._focus_name)
        self._bind_entry_navigation()

    def _focus_name(self):
        try:
            if self.device_name_entry and self.device_name_entry.winfo_exists():
                self.device_name_entry.focus_set()
                self.device_name_entry.icursor(tk.END)
        except Exception:
            pass

    def _focus_device_id(self):
        """Move focus to the device ID entry."""
        try:
            if self.device_id_entry and self.device_id_entry.winfo_exists():
                self.device_id_entry.focus_set()
                self.device_id_entry.icursor(tk.END)
        except Exception:
            pass

    def _bind_entry_navigation(self):
        """Bind Return to move from name -> id, then id -> pair."""
        try:
            if self.device_name_entry and self.device_name_entry.winfo_exists():
                self.device_name_entry.bind("<Return>", lambda e: (self._focus_device_id(), "break")[1])
            if self.device_id_entry and self.device_id_entry.winfo_exists():
                self.device_id_entry.bind("<Return>", lambda e: (self._on_pair_click(), "break")[1])
        except Exception:
            pass

    def _on_pair_click(self):
        name = self.device_name_var.get().strip()
        device_id = self.device_id_var.get().strip()

        if not name or not device_id:
            # Simple validation feedback (could be improved with a toast/label)
            return

        self.on_pair(name, device_id)
        self.close()

    def close(self):
        if self.window_scaffold and self.window_scaffold.toplevel:
            self.window_scaffold.toplevel.destroy()
            self.window_scaffold = None
        if self.on_close:
            try:
                self.on_close()
            except Exception:
                pass
