"""Rebuilt settings page with a fresh, minimal layout."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Callable

from utils.design_system import Colors, Spacing, DesignUtils, Typography
from utils.user_settings import get_user_settings, save_user_settings
from ui.helpers import AutoWrapLabel, create_page_header, create_scroll_container
from .base_page import BasePage, PageContext
from utils.state.status_manager import get_status_manager


class SettingsPage(BasePage):
    """Minimal settings page focused on appearance and preferences."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.context = context
        self.navigator = getattr(context, "navigator", None)
        self.user_settings = get_user_settings()
        self._toggle_widgets: dict[str, tuple[tk.BooleanVar, tk.Widget]] = {}
        self._theme_button: tk.Widget | None = None
        self._status_label: tk.Label | None = None
        self._status_callback = None

        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(0, Spacing.LG))
        body = scroll.frame

        create_page_header(
            body,
            title="Settings",
            subtitle="Choose how Locomm looks and feels for you.",
            padx=Spacing.LG,
        )

        self._build_sections(body)

    # ------------------------------------------------------------------ #
    # Layout helpers
    def _build_sections(self, parent: tk.Misc) -> None:
        self._build_account_section(parent)
        self._build_appearance_section(parent)


    def _create_section(self, parent: tk.Misc, title: str, description: str) -> tk.Frame:
        section = tk.Frame(parent, bg=Colors.SURFACE_ALT, bd=0, relief="flat", padx=Spacing.MD, pady=Spacing.SM)
        section.pack(fill=tk.X, padx=Spacing.LG, pady=(0, Spacing.MD))

        header = tk.Label(
            section,
            text=title,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        )
        header.pack(anchor="w")

        if description:
            AutoWrapLabel(
                section,
                text=description,
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_12),
                padding_x=Spacing.MD,
            ).pack(fill=tk.X, pady=(Spacing.XS, Spacing.SM))

        return section

    # ------------------------------------------------------------------ #
    # Appearance controls
    def _build_appearance_section(self, parent: tk.Misc) -> None:
        section = self._create_section(
            parent,
            "Appearance",
            "",
        )

        self._add_toggle(section, "Dark mode", "theme_mode", is_theme=True)

    def _add_toggle(self, parent: tk.Misc, label: str, attr: str, *, is_theme: bool = False) -> None:
        row = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        row.pack(fill=tk.X, pady=(0, Spacing.XS), padx=(Spacing.SM, 0))

        tk.Label(
            row,
            text=label,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14),
        ).pack(side=tk.LEFT)

        value = self.user_settings.theme_mode == "dark" if is_theme else getattr(self.user_settings, attr, False)
        var = tk.BooleanVar(master=self, value=value)
        btn = DesignUtils.button(
            row,
            text=self._bool_label(value),
            variant="secondary",
            width=8,
        )

        def _command(attr=attr, var=var, widget=btn, is_theme=is_theme):
            self._toggle_setting(attr, var, widget, is_theme=is_theme)

        btn.configure(command=_command)
        btn.pack(side=tk.RIGHT)

        self._toggle_widgets[attr] = (var, btn)

    def _theme_button_label(self) -> str:
        return f"Dark Mode: {'On' if self.user_settings.theme_mode == 'dark' else 'Off'}"

    def _toggle_theme(self) -> None:
        next_mode = "light" if self.user_settings.theme_mode == "dark" else "dark"
        self.user_settings.theme_mode = next_mode
        save_user_settings(self.user_settings)

        app = getattr(self.context, "app", None)
        if app and hasattr(app, "toggle_theme"):
            app.toggle_theme(next_mode == "dark")

        if self._theme_button and self._theme_button.winfo_exists():
            self._theme_button.configure(text=self._theme_button_label())

    def _toggle_setting(self, attr: str, var: tk.BooleanVar, btn: tk.Widget, *, is_theme: bool = False) -> None:
        new_value = not var.get()
        var.set(new_value)
        if is_theme:
            self.user_settings.theme_mode = "dark" if new_value else "light"
            app = getattr(self.context, "app", None)
            if app and hasattr(app, "toggle_theme"):
                app.toggle_theme(new_value)
        else:
            setattr(self.user_settings, attr, new_value)
        save_user_settings(self.user_settings)
        if btn and btn.winfo_exists():
            btn.configure(text=self._bool_label(new_value))

    def _bool_label(self, value: bool) -> str:
        return "On" if value else "Off"

    # ------------------------------------------------------------------ #
    # Lifecycle
    def on_show(self) -> None:
        self.user_settings = get_user_settings()
        if self._theme_button and self._theme_button.winfo_exists():
            self._theme_button.configure(text=self._theme_button_label())
        for attr, (var, btn) in self._toggle_widgets.items():
            current = getattr(self.user_settings, attr, False)
            var.set(current)
            if isinstance(btn, tk.Button):
                btn.configure(text=self._bool_label(current))
        self._refresh_device_info()

    def destroy(self):
        self._unregister_status_listener()
        return super().destroy()

    def _unregister_status_listener(self):
        # Status listener was removed; keep stub for safe destroy
        self._status_callback = None

    # Placeholder handlers for future device change flows
    def _change_device_name(self):
        new_name = simpledialog.askstring("Change Device Name", "Enter a new device name (max 32 chars):", parent=self)
        if new_name is None:
            return
        new_name = new_name.strip()
        if not new_name:
            messagebox.showinfo("Change Device Name", "Name cannot be empty.")
            return
        if len(new_name) > 32:
            messagebox.showinfo("Change Device Name", "Name must be 32 characters or less.")
            return
        session = getattr(self.context, "session", None)
        if session:
            session.local_device_name = new_name
            session.device_name = new_name
        messagebox.showinfo("Change Device Name", "Device name updated locally.")
        navigator = getattr(self.context, "navigator", None)
        if navigator and hasattr(navigator, "refresh_header_info"):
            try:
                navigator.refresh_header_info()
            except Exception:
                pass

    def _change_device_id(self):
        new_id = simpledialog.askstring("Change Device ID", "Enter a new device ID:", parent=self)
        if new_id is None:
            return
        new_id = new_id.strip()
        if not new_id:
            messagebox.showinfo("Change Device ID", "Device ID cannot be empty.")
            return
        session = getattr(self.context, "session", None)
        if session:
            session.local_device_id = new_id
        messagebox.showinfo("Change Device ID", "Device ID updated locally.")
        navigator = getattr(self.context, "navigator", None)
        if navigator and hasattr(navigator, "refresh_header_info"):
            try:
                navigator.refresh_header_info()
            except Exception:
                pass

    def _refresh_device_info(self):
        session = getattr(self.context, "session", None)
        device_name = getattr(session, "local_device_name", "") or "Not available"
        # Update credentials labels to reflect current name
        if hasattr(self, "_account_name_label") and self._account_name_label and self._account_name_label.winfo_exists():
            self._account_name_label.configure(text=f"Name: {device_name}")

    def _build_account_section(self, parent: tk.Misc) -> None:
        container = self._create_section(parent, "Credentials", "")
        session = getattr(self.context, "session", None)
        login_name = getattr(session, "local_device_name", "") or "Not available"

        # Name row
        name_row = tk.Frame(container, bg=Colors.SURFACE_ALT)
        name_row.pack(fill=tk.X, pady=(0, Spacing.SM), padx=(Spacing.SM, 0))
        self._account_name_label = tk.Label(
            name_row,
            text=f"Name: {login_name}",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
        )
        self._account_name_label.pack(side=tk.LEFT, anchor="w")
        DesignUtils.button(
            name_row,
            text="Change",
            command=self._change_device_name,
            variant="secondary",
            width=8,
        ).pack(side=tk.RIGHT)

        # Password row
        pwd_row = tk.Frame(container, bg=Colors.SURFACE_ALT)
        pwd_row.pack(fill=tk.X, padx=(Spacing.SM, 0))
        tk.Label(
            pwd_row,
            text="Password:",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
        ).pack(side=tk.LEFT, anchor="w")
        DesignUtils.button(
            pwd_row,
            text="Change",
            command=self._change_password_placeholder,
            variant="secondary",
            width=8,
        ).pack(side=tk.RIGHT)

        # Logout row aligned to the right under Password
        logout_row = tk.Frame(container, bg=Colors.SURFACE_ALT)
        logout_row.pack(fill=tk.X, pady=(Spacing.SM, 0), padx=(Spacing.SM, 0))
        DesignUtils.button(
            logout_row,
            text="Logout",
            command=self._logout,
            variant="danger",
            width=8,
        ).pack(side=tk.RIGHT)

    def _change_password_placeholder(self):
        # Open the existing register modal from the login window to handle password changes
        try:
            if hasattr(self.context, "app") and getattr(self.context, "app"):
                app = self.context.app
                if hasattr(app, "show_login_modal"):
                    # Open login modal and immediately open register for password change
                    app.show_login_modal()
                    if app.login_modal:
                        app.login_modal.open_register(on_close=None)
                        return
        except Exception:
            pass
        messagebox.showinfo("Change Password", "Password changes are managed on the login screen.")

    def _logout(self):
        proceed = messagebox.askokcancel("Logout", "Are you sure you want to logout?", parent=self.winfo_toplevel())
        if not proceed:
            return
        navigator = getattr(self.context, "navigator", None)
        if navigator and hasattr(navigator, "on_logout") and callable(navigator.on_logout):
            try:
                navigator.on_logout()
            except Exception:
                pass
