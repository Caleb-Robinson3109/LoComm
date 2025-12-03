"""
Login window for entering password and device name.
"""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from ui.helpers import create_form_row
from utils.window_sizing import get_login_modal_size

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../api')))

from LoCommAPI import *


class LoginWindow:
    """Login interface rendered inside the main Tk window."""

    def __init__(
        self,
        parent: tk.Tk,
        on_login: Callable[[str, str], None],
        on_register: Optional[Callable] = None,
        on_forgot_password: Optional[Callable] = None,
    ):
        self.parent = parent
        self.on_login = on_login
        self.on_register = on_register
        self.on_forgot_password = on_forgot_password

        self.window: Optional[tk.Frame] = None
        self.device_name_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self._is_password_validated = False

        self.password_entry: Optional[tk.Widget] = None
        self.device_name_entry: Optional[tk.Widget] = None
        self.validate_btn: Optional[tk.Widget] = None
        self.login_btn: Optional[tk.Widget] = None

        self._create_window()

    def _create_window(self):
        self.parent.focus_set()
        for child in self.parent.winfo_children():
            child.destroy()

        self.window = tk.Frame(self.parent, bg=Colors.SURFACE)
        self.window.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=Spacing.SM)

        self._build_content()
        self.parent.protocol("WM_DELETE_WINDOW", self._on_close)
        self.window.bind("<Escape>", lambda e: self._on_close())
        self.parent.after(0, self._apply_geometry)

    def _apply_geometry(self):
        if not self.window or not self.window.winfo_exists():
            return

        size = get_login_modal_size()
        self.parent.update_idletasks()

        screen_w = self.parent.winfo_screenwidth()
        screen_h = self.parent.winfo_screenheight()

        width = min(size.width, screen_w)
        height = min(size.height, screen_h)
        width = max(width, size.min_width)
        height = max(height, size.min_height)

        pos_x = max((screen_w - width) // 2, 0)
        pos_y = max((screen_h - height) // 2, 0)

        self.parent.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        self.parent.minsize(size.min_width, size.min_height)

    def _build_content(self):
        assert self.window is not None
        main_container = tk.Frame(self.window, bg=Colors.SURFACE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        header_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        header_frame.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            header_frame,
            text="Locomm",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD),
        ).pack()

        tk.Label(
            header_frame,
            text="Secure Platform",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        ).pack(pady=(0, 2))

        form_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        form_frame.pack(fill=tk.X, pady=(0, 8))

        _, self.password_entry = create_form_row(
            form_frame,
            label="Password",
            widget_factory=lambda parent: DesignUtils.create_chat_entry(
                parent,
                textvariable=self.password_var,
                show="•",
                width=15,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ),
            help_text=None,
        )

        self.validate_btn = DesignUtils.button(
            form_frame,
            text="Validate",
            command=self._on_validate_click,
            variant="primary",
            width=10,
        )
        self.validate_btn.pack(fill=tk.X, pady=(0, 6))

        _, self.device_name_entry = create_form_row(
            form_frame,
            label="Preferred Name",
            widget_factory=lambda parent: DesignUtils.create_chat_entry(
                parent,
                textvariable=self.device_name_var,
                width=15,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ),
            help_text=None,
        )
        self.device_name_entry.configure(state="disabled")

        self.login_btn = DesignUtils.button(
            form_frame,
            text="Login",
            command=self._on_login_click,
            variant="primary",
            width=10,
        )
        self.login_btn.pack(fill=tk.X, pady=(0, 4))
        self.login_btn.configure(state="disabled")

        self.device_name_var.trace_add("write", self._on_device_name_change)

        links_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        links_frame.pack(fill=tk.X)

        self.register_label = tk.Label(
            links_frame,
            text="Register",
            bg=Colors.SURFACE,
            fg=Colors.LINK_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            cursor="hand2",
        )
        self.register_label.pack(side=tk.LEFT, padx=(0, 4))
        self.register_label.bind("<Button-1>", lambda e: self._on_register_click())
        self.register_label.bind("<Enter>", lambda e: self.register_label.configure(fg=Colors.LINK_HOVER))
        self.register_label.bind("<Leave>", lambda e: self.register_label.configure(fg=Colors.LINK_PRIMARY))

        self.forgot_label = tk.Label(
            links_frame,
            text="Forgot Password",
            bg=Colors.SURFACE,
            fg=Colors.LINK_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            cursor="hand2",
        )
        self.forgot_label.pack(side=tk.LEFT)
        self.forgot_label.bind("<Button-1>", lambda e: self._on_forgot_password_click())
        self.forgot_label.bind("<Enter>", lambda e: self.forgot_label.configure(fg=Colors.LINK_HOVER))
        self.forgot_label.bind("<Leave>", lambda e: self.forgot_label.configure(fg=Colors.LINK_PRIMARY))

        self.error_container = tk.Frame(main_container, bg=Colors.SURFACE)
        self.error_container.pack(fill=tk.X, pady=(Spacing.XXS, 0))

        self.window.after(100, self._set_initial_focus)
        self.window.bind("<Return>", self._handle_enter_key)
        self.password_entry.bind("<Return>", self._handle_enter_key)
        self.device_name_entry.bind("<Return>", self._handle_enter_key)
        self.window.bind("<Escape>", lambda e: self._on_close())
    def _set_initial_focus(self):
        if self.password_entry and self.password_entry.winfo_exists():
            self.password_entry.focus_set()
            self.password_entry.icursor(tk.END)

    def _handle_enter_key(self, event):
        if not self._is_password_validated:
            self._on_validate_click()
        else:
            self._on_login_click()
        return "break"

    def _on_validate_click(self):
        password = self.password_var.get().strip()

        if not password:
            self._show_validation_error("Please enter a password")
            return
        if len(password) < 3:
            self._show_validation_error("Password must be at least 3 characters")
            return

        self.validate_btn.configure(state="disabled", text="Validating...")
        if self.login_btn:
            self.login_btn.configure(state="disabled")

        try:
            okay: bool = enter_password(password)
        except Exception:
            self._handle_validation_failure("Unable to validate password. Please try again.")
            return

        if not okay:
            self._handle_validation_failure("Incorrect password. Please try again.")
            return

        if self.window:
            self.window.after(300, self._on_validation_complete)

    def _on_validation_complete(self):
        self.device_name_entry.configure(state="normal")
        self.validate_btn.configure(state="normal", text="Validated ✓")
        self._is_password_validated = True
        self.login_btn.configure(state="normal")

        if self.window and self.device_name_entry.winfo_exists():
            self.window.after(50, self.device_name_entry.focus_set)
            self.window.after(80, lambda: self.device_name_entry.icursor(tk.END))

    def _on_device_name_change(self, *args):
        if self._is_password_validated:
            self.login_btn.configure(state="normal")
        else:
            self.login_btn.configure(state="disabled")

    def _on_login_click(self):
        if not self._is_password_validated:
            self._show_validation_error("Please validate your password first")
            return

        device_name = self.device_name_var.get().strip() or "Orion"

        self.login_btn.configure(state="disabled", text="Logging in...")

        if self.on_login:
            self.on_login(device_name, "validated_password")

        if self.window and self.login_btn.winfo_exists():
            self.window.after(1000, lambda: self.login_btn.configure(state="normal", text="Login"))

    def _on_register_click(self):
        if self.on_register:
            self.on_register()

    def _on_forgot_password_click(self):
        if self.on_forgot_password:
            self.on_forgot_password()

    def _handle_validation_failure(self, message: str):
        self._is_password_validated = False
        if self.validate_btn and self.validate_btn.winfo_exists():
            self.validate_btn.configure(state="normal", text="Validate")
        if self.device_name_entry and self.device_name_entry.winfo_exists():
            self.device_name_entry.configure(state="disabled")
        if self.login_btn and self.login_btn.winfo_exists():
            self.login_btn.configure(state="disabled", text="Login")
        self.password_var.set("")
        self._show_validation_error(message)
        if self.password_entry and self.password_entry.winfo_exists() and self.window:
            self.window.after(50, self.password_entry.focus_set)

    def _show_validation_error(self, message: str):
        target_parent = self.error_container if hasattr(self, "error_container") and self.error_container else self.window
        pack_opts = {"fill": tk.X, "pady": (Spacing.XXS, 0)}
        error_label = tk.Label(
            target_parent,
            text=message,
            bg=Colors.STATE_ERROR,
            fg=Colors.SURFACE,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            padx=Spacing.SM,
            pady=Spacing.XXS,
        )
        if pack_opts:
            error_label.pack(**pack_opts)
        else:
            error_label.pack(fill=tk.X, pady=(Spacing.XXS, 0))

        if target_parent:
            target_parent.after(3000, error_label.destroy)

    def _on_close(self):
        from tkinter import messagebox

        result = messagebox.askyesno(
            "Confirm Exit",
            "Are you sure you want to close Locomm?",
            parent=self.parent,
        )
        if result:
            self.parent.destroy()

    def close_modal(self):
        """Compatibility helper for existing code paths."""
        if self.window and self.window.winfo_exists():
            self.window.destroy()

    # (Remaining methods identical to previous LoginModal implementation…)
