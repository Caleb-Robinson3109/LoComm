"""
Login window for entering password and device name.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from ui.helpers import create_form_row
from utils.window_sizing import get_login_modal_size

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../api')))

from LoCommAPI import *
from utils.chatroom_registry import set_active_chatroom


class LoginWindow:
    """Login interface rendered inside the main Tk window."""

    def __init__(
        self,
        parent: tk.Tk,
        on_login: Callable[[str, str], None],
    ):
        self.parent = parent
        self.on_login = on_login

        self.window: Optional[tk.Frame] = None
        self.device_name_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.register_window: Optional[tk.Toplevel] = None
        self._register_password_var = tk.StringVar()
        self._register_confirm_var = tk.StringVar()

        self.password_entry: Optional[tk.Widget] = None
        self.device_name_entry: Optional[tk.Widget] = None
        self.login_btn: Optional[tk.Widget] = None
        self._register_close_callback: Optional[Callable[[bool], None]] = None
        self._register_succeeded = False
        self._register_password_entry: Optional[tk.Widget] = None
        self._register_confirm_entry: Optional[tk.Widget] = None
        self._register_window_size = get_login_modal_size()

        self._create_window()

    def _create_window(self):
        self.parent.focus_set()
        for child in self.parent.winfo_children():
            child.destroy()

        try:
            self.parent.title("Login")
        except Exception:
            pass

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
        header_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        tk.Label(
            header_frame,
            text="Locomm",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD),
        ).pack(pady=(Spacing.LG, 0))
        tk.Label(
            header_frame,
            text="Securely connect to your device to continue.",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12),
        ).pack(pady=(0, 0))

        form_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        form_frame.pack(fill=tk.X, pady=(Spacing.MD, 12))

        _, self.device_name_entry = create_form_row(
            form_frame,
            label="Name",
            widget_factory=lambda parent: DesignUtils.create_chat_entry(
                parent,
                textvariable=self.device_name_var,
                width=15,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ),
            help_text=None,
        )
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
        self.login_btn = DesignUtils.button(
            form_frame,
            text="Login",
            command=self._on_login_click,
            variant="primary",
            width=10,
        )
        self.login_btn.pack(fill=tk.X, pady=(Spacing.MD, 0))

        self.error_container = tk.Frame(main_container, bg=Colors.SURFACE)
        self.error_container.pack(fill=tk.X, pady=(Spacing.XXS, 0))

        self.window.after(100, self._set_initial_focus)
        self.window.bind("<Return>", self._handle_enter_key)
        self.password_entry.bind("<Return>", self._handle_enter_key)
        self.device_name_entry.bind("<Return>", self._focus_password)
        self.window.bind("<Escape>", lambda e: self._on_close())

    def _set_initial_focus(self):
        if self.device_name_entry and self.device_name_entry.winfo_exists():
            self.device_name_entry.focus_set()
            self.device_name_entry.icursor(tk.END)

    def _handle_enter_key(self, event):
        self._on_login_click()
        return "break"

    def _focus_password(self, event):
        if self.password_entry and self.password_entry.winfo_exists():
            self.password_entry.focus_set()
            self.password_entry.icursor(tk.END)
        return "break"

    def _on_login_click(self):
        password = self.password_var.get().strip()
        device_name = self.device_name_var.get().strip()
        if not device_name:
            self._show_validation_error("Please enter a device name")
            if self.device_name_entry and self.device_name_entry.winfo_exists():
                self.window.after(10, self.device_name_entry.focus_set)
            return
        if len(device_name) > 32:
            self._show_validation_error("Device name must be 32 characters or less")
            if self.device_name_entry and self.device_name_entry.winfo_exists():
                self.window.after(10, self.device_name_entry.focus_set)
            return
        if not password:
            self._show_validation_error("Please enter a password")
            if self.password_entry and self.password_entry.winfo_exists():
                self.window.after(10, self.password_entry.focus_set)
            return
        if len(password) < 3:
            self._show_validation_error("Password must be at least 3 characters")
            if self.password_entry and self.password_entry.winfo_exists():
                self.window.after(10, self.password_entry.focus_set)
            return

        if not self.login_btn or not self.login_btn.winfo_exists():
            return
        self.login_btn.configure(state="disabled", text="Logging in...")

        try:
            okay: bool = enter_password(password)
        except Exception:
            self._show_login_failure("Unable to validate password. Please try again.")
            return

        if not okay:
            self._show_login_failure("Incorrect password. Please try again.")
            return

        device_name = self.device_name_var.get().strip()
        if self.on_login:
            self.on_login(device_name, password)

        # After a successful login, ask the device for an existing pairing/chatroom key.
        # If the device already has a pairing key, set it as the active chatroom so
        # UI listeners can update accordingly.
        try:
            pairing_key = None
            try:
                pairing_key = get_pairing_key()
            except Exception:
                pairing_key = None
            if pairing_key:
                try:
                    set_active_chatroom(str(pairing_key), [])
                except Exception:
                    pass
        except Exception:
            pass

        if self.window and self.login_btn.winfo_exists():
            self.window.after(1000, lambda: self.login_btn.configure(state="normal", text="Login"))

    def open_register(self, *, on_close: Callable[[bool], None] | None = None):
        """Expose register helper for external flows."""
        self._register_close_callback = on_close
        self._register_succeeded = False
        self._open_register_modal()

    def _show_login_failure(self, message: str):
        if self.login_btn and self.login_btn.winfo_exists():
            self.login_btn.configure(state="normal", text="Login")
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

    # ------------------------------------------------------------------ #
    # Registration helpers

    def _open_register_modal(self):
        if self.register_window and self.register_window.winfo_exists():
            self.register_window.lift()
            return

        self._register_password_var.set("")
        self._register_confirm_var.set("")

        self.register_window = tk.Toplevel(self.parent)
        self.register_window.title("Register")
        self.register_window.configure(bg=Colors.SURFACE)
        self.register_window.transient(self.parent)
        self.register_window.grab_set()
        self.register_window.resizable(False, False)
        self.register_window.protocol("WM_DELETE_WINDOW", lambda: self._close_register_modal(success=False))
        self._register_succeeded = False

        container = tk.Frame(self.register_window, bg=Colors.SURFACE, padx=Spacing.MD, pady=Spacing.MD)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="Create a password for this device",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD),
            anchor="w",
            justify="left",
        ).pack(fill=tk.X, pady=(0, Spacing.XXS))
        form_frame = tk.Frame(container, bg=Colors.SURFACE)
        form_frame.pack(fill=tk.X)

        _, self._register_password_entry = create_form_row(
            form_frame,
            label="Password",
            widget_factory=lambda parent: DesignUtils.create_chat_entry(
                parent,
                textvariable=self._register_password_var,
                show="•",
                width=18,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ),
            help_text=None,
        )

        _, self._register_confirm_entry = create_form_row(
            form_frame,
            label="Confirm Password",
            widget_factory=lambda parent: DesignUtils.create_chat_entry(
                parent,
                textvariable=self._register_confirm_var,
                show="•",
                width=18,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ),
            help_text=None,
        )

        if self._register_password_entry:
            self._register_password_entry.bind("<Return>", lambda e: self._register_confirm_entry.focus_set() if self._register_confirm_entry else None)
        if self._register_confirm_entry:
            self._register_confirm_entry.bind("<Return>", lambda e: self._submit_registration())

        self.register_status = tk.Label(
            container,
            text="",
            bg=Colors.SURFACE,
            fg=Colors.STATE_ERROR,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            anchor="w",
            justify="left",
        )
        self.register_status.pack(fill=tk.X, pady=(Spacing.XXS, 0))

        btn_frame = tk.Frame(container, bg=Colors.SURFACE)
        btn_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))

        submit_btn = DesignUtils.button(
            btn_frame,
            text="Set Password",
            command=self._submit_registration,
            variant="primary",
            width=12,
        )
        submit_btn.pack(fill=tk.X, pady=(0, Spacing.XXS))

        cancel_btn = DesignUtils.button(
            btn_frame,
            text="Cancel",
            command=lambda: self._close_register_modal(success=False),
            variant="secondary",
            width=12,
        )
        cancel_btn.pack(fill=tk.X)

        self.register_window.bind("<Return>", lambda e: self._submit_registration())
        self.register_window.after(0, self._center_register_window)

    def _center_register_window(self):
        if not self.register_window or not self.register_window.winfo_exists():
            return
        size = self._register_window_size
        parent = getattr(self, "parent", None)
        if parent:
            parent.update_idletasks()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            pos_x = px + max((pw - size.width) // 2, 0)
            pos_y = py + max((ph - size.height) // 2, 0)
        else:
            screen_w = self.register_window.winfo_screenwidth()
            screen_h = self.register_window.winfo_screenheight()
            pos_x = max((screen_w - size.width) // 2, 0)
            pos_y = max((screen_h - size.height) // 2, 0)
        self.register_window.geometry(f"{size.width}x{size.height}+{pos_x}+{pos_y}")

    def _close_register_modal(self, *, success: bool = False):
        if self.register_window and self.register_window.winfo_exists():
            self.register_window.grab_release()
            self.register_window.destroy()
        self.register_window = None
        result = success or self._register_succeeded
        if self._register_close_callback:
            callback = self._register_close_callback
            self._register_close_callback = None
            callback(result)
        self._register_succeeded = False

    def _submit_registration(self):
        password = self._register_password_var.get().strip()
        confirm = self._register_confirm_var.get().strip()
        self._update_register_status("")

        if not password or not confirm:
            self._update_register_status("Please enter and confirm your password.")
            return
        if len(password) < 3:
            self._update_register_status("Password must be at least 3 characters.")
            return
        if len(password) > 32:
            self._update_register_status("Password must be 32 characters or less.")
            return
        if password != confirm:
            self._update_register_status("Passwords do not match.")
            return

        try:
            ok = reset_passoword(password)
        except Exception:
            messagebox.showerror("Registration Failed", "Unable to set password. Please try again.")
            return

        if not ok:
            messagebox.showerror(
                "Registration Failed",
                "Could not set the password on the device. Please try again.",
            )
            return

        self.password_var.set(password)
        self._register_succeeded = True
        self._close_register_modal(success=True)
        messagebox.showinfo("Registration Complete", "Password set. Please log in.")
        if self.password_entry and self.password_entry.winfo_exists() and self.window:
            self.window.after(50, self.password_entry.focus_set)

    def _update_register_status(self, message: str):
        if hasattr(self, "register_status") and self.register_status and self.register_status.winfo_exists():
            self.register_status.configure(text=message)
