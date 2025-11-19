"""
Modal Login Page - initial application interface with form fields and links.
Responsive to window size so all elements fit when the app opens.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from ui.helpers import create_form_row

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../api')))

from LoCommAPI import *

class LoginModal:
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

        # Modal state
        self.modal_window: Optional[tk.Frame] = None
        self.device_name_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self._is_password_validated = False

        self.password_entry: Optional[tk.Widget] = None
        self.device_name_entry: Optional[tk.Widget] = None
        self.validate_btn: Optional[tk.Widget] = None
        self.login_btn: Optional[tk.Widget] = None

        self._create_login_page()

    # ------------------------------------------------------------------ #
    # Layout / window sizing helpers
    # ------------------------------------------------------------------ #

    def _create_login_page(self):
        """Create the login page as the main window content."""
        self.parent.focus_set()

        # Clear any existing children on the root (safety)
        for child in self.parent.winfo_children():
            child.destroy()

        # Root frame for login UI
        self.modal_window = tk.Frame(self.parent, bg=Colors.SURFACE)
        self.modal_window.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=Spacing.SM)

        self._build_content()

        # Hook close
        self.parent.protocol("WM_DELETE_WINDOW", self._on_close)
        self.modal_window.bind("<Escape>", lambda e: self._on_close())

        # After layout is computed, make sure outer window is big enough
        self.parent.after(0, self._ensure_window_fits_content)

    def _ensure_window_fits_content(self):
        """Ensure the main window is at least as big as the login content."""
        if not self.modal_window or not self.modal_window.winfo_exists():
            return

        self.parent.update_idletasks()

        req_w = self.modal_window.winfo_reqwidth() + 2 * Spacing.SM
        req_h = self.modal_window.winfo_reqheight() + 2 * Spacing.SM

        cur_w = max(self.parent.winfo_width(), 1)
        cur_h = max(self.parent.winfo_height(), 1)

        new_w = max(cur_w, req_w)
        new_h = max(cur_h, req_h)

        if new_w != cur_w or new_h != cur_h:
            screen_w = self.parent.winfo_screenwidth()
            screen_h = self.parent.winfo_screenheight()
            pos_x = max((screen_w - new_w) // 2, 0)
            pos_y = max((screen_h - new_h) // 2, 0)
            self.parent.geometry(f"{new_w}x{new_h}+{pos_x}+{pos_y}")

        # Prevent shrinking below the content
        self.parent.minsize(new_w, new_h)

    # ------------------------------------------------------------------ #
    # Content and interactions
    # ------------------------------------------------------------------ #

    def _build_content(self):
        """Build the login form."""
        assert self.modal_window is not None

        main_container = tk.Frame(self.modal_window, bg=Colors.SURFACE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Header
        header_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        header_frame.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            header_frame,
            text="LoRa Chat",
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

        # Form container
        form_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        form_frame.pack(fill=tk.X, pady=(0, 8))

        # Password row (using helpers.create_form_row)
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

        # Validate button
        self.validate_btn = DesignUtils.button(
            form_frame,
            text="Validate",
            command=self._on_validate_click,
            variant="primary",
            width=10,
        )
        self.validate_btn.pack(fill=tk.X, pady=(0, 6))

        # Preferred name row
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

        # Initially disabled until password validated
        self.device_name_entry.configure(state="disabled")
        

        # Login button
        self.login_btn = DesignUtils.button(
            form_frame,
            text="Login",
            command=self._on_login_click,
            variant="primary",
            width=10,
        )
        self.login_btn.pack(fill=tk.X, pady=(0, 4))
        self.login_btn.configure(state="disabled")

        # Device name change -> enable/disable login (after validation)
        self.device_name_var.trace_add("write", self._on_device_name_change)

        # Action links
        links_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        links_frame.pack(fill=tk.X)

        register_label = tk.Label(
            links_frame,
            text="Register",
            bg=Colors.SURFACE,
            fg=Colors.LINK_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            cursor="hand2",
        )
        register_label.pack(side=tk.LEFT, padx=(0, 4))
        register_label.bind("<Button-1>", lambda e: self._on_register_click())
        register_label.bind("<Enter>", lambda e: register_label.configure(fg=Colors.LINK_HOVER))
        register_label.bind("<Leave>", lambda e: register_label.configure(fg=Colors.LINK_PRIMARY))

        forgot_label = tk.Label(
            links_frame,
            text="Forgot Password",
            bg=Colors.SURFACE,
            fg=Colors.LINK_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            cursor="hand2",
        )
        forgot_label.pack(side=tk.LEFT)
        forgot_label.bind("<Button-1>", lambda e: self._on_forgot_password_click())
        forgot_label.bind("<Enter>", lambda e: forgot_label.configure(fg=Colors.LINK_HOVER))
        forgot_label.bind("<Leave>", lambda e: forgot_label.configure(fg=Colors.LINK_PRIMARY))

        # Focus and key bindings
        self.modal_window.after(100, self._set_initial_focus)

        self.modal_window.bind("<Return>", self._handle_enter_key)
        self.password_entry.bind("<Return>", self._handle_enter_key)
        self.device_name_entry.bind("<Return>", self._handle_enter_key)
        self.modal_window.bind("<Escape>", lambda e: self._on_close())

    # ------------------------------------------------------------------ #
    # Interaction logic
    # ------------------------------------------------------------------ #

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

        okay: bool = enter_password(password)
        if not okay:
            self._show_validation_error("password failed on device")
            return 

        if self.modal_window:
            self.modal_window.after(300, self._on_validation_complete)

    def _on_validation_complete(self):
        self.device_name_entry.configure(state="normal")
        self.validate_btn.configure(state="normal", text="Validated ✓")
        self._is_password_validated = True
        self.login_btn.configure(state="normal")

        if self.modal_window and self.device_name_entry.winfo_exists():
            self.modal_window.after(50, self.device_name_entry.focus_set)
            self.modal_window.after(80, lambda: self.device_name_entry.icursor(tk.END))

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

        if self.modal_window and self.login_btn.winfo_exists():
            self.modal_window.after(1000, lambda: self.login_btn.configure(state="normal", text="Login"))

    def _on_register_click(self):
        if self.on_register:
            self.on_register()

    def _on_forgot_password_click(self):
        if self.on_forgot_password:
            self.on_forgot_password()

    def _show_validation_error(self, message: str):
        error_label = tk.Label(
            self.modal_window,
            text=message,
            bg=Colors.STATE_ERROR,
            fg=Colors.SURFACE,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            padx=Spacing.SM,
            pady=Spacing.XXS,
        )
        error_label.pack(pady=(Spacing.XXS, 0))

        if self.modal_window:
            self.modal_window.after(3000, error_label.destroy)

    def _on_close(self):
        from tkinter import messagebox

        result = messagebox.askyesno(
            "Confirm Exit",
            "Are you sure you want to close LoRa Chat?",
            parent=self.parent,
        )
        if result:
            self.parent.destroy()

    # ------------------------------------------------------------------ #
    # External helpers
    # ------------------------------------------------------------------ #

    def close_modal(self):
        """Close the login UI and clean up."""
        try:
            if self.modal_window:
                self.modal_window.destroy()
                self.modal_window = None
        except tk.TclError:
            pass

    def show_modal(self):
        """Bring the login UI to the front (for API compatibility)."""
        if self.modal_window:
            self.modal_window.lift()
            self.modal_window.focus_set()

    def destroy(self):
        """Compatibility cleanup hook."""
        self.close_modal()
