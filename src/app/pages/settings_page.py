"""Settings page matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, Spacing, DesignUtils, ThemeManager, Typography, Space
from utils.user_settings import get_user_settings, save_user_settings
from ui.helpers import (
    create_scroll_container,
    create_page_header,
    create_standard_section,
    AutoWrapLabel,
)
from .base_page import BasePage, PageContext


class SettingsPage(BasePage):
    """Settings page with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.context = context
        self.navigator = context.navigator if context else None

        self.user_settings = get_user_settings()
        self._toggle_vars: dict[str, tk.BooleanVar] = {}
        self._toggle_buttons: dict[str, tk.Widget] = {}
        self._theme_button: tk.Widget | None = None

        # Simple scroll container like chat page
        scroll = create_scroll_container(
            self,
            bg=Colors.SURFACE,
            padding=(0, Spacing.LG),
        )
        body = scroll.frame

        # Standard header with AutoWrap subtitle and back button
        create_page_header(
            body,
            title="Settings",
            subtitle="Configure your Locomm experience.",
            show_back=True,
            on_back=self._handle_back,
        )

        self._build_appearance_section(body)
        self._build_settings_section(body)

    def _handle_back(self):
        nav = getattr(self, "navigator", None)
        if not nav:
            return
        if hasattr(nav, "go_back"):
            nav.go_back()
        elif hasattr(nav, "navigate_to"):
            nav.navigate_to("home")

    def _build_appearance_section(self, parent):
        """Build clean appearance section with standard section helper."""
        _, section_body = create_standard_section(
            parent,
            title="Appearance",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=False,
        )

        # Theme setting card
        setting_frame = tk.Frame(section_body, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.SM)
        setting_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        tk.Label(
            setting_frame,
            text="Dark Mode",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")

        AutoWrapLabel(
            setting_frame,
            text="Use dark theme for better battery life and reduced eye strain.",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            justify="left",
            padding_x=Spacing.SM * 2,
            min_wrap=260,
        ).pack(anchor="w", fill=tk.X, expand=True, pady=(Space.XXS, 0))

        # Toggle button
        self.theme_var = tk.BooleanVar(value=self.user_settings.theme_mode == "dark")
        toggle_btn = DesignUtils.button(
            setting_frame,
            text="On" if self.theme_var.get() else "Off",
            variant="secondary",
            command=self._toggle_theme,
        )
        toggle_btn.pack(side=tk.RIGHT)
        self._theme_button = toggle_btn
        self._sync_theme_button()

    def _build_settings_section(self, parent):
        """Build simple settings section with standard helpers."""
        _, section_body = create_standard_section(
            parent,
            title="Notifications & Diagnostics",
            bg=Colors.SURFACE,
            inner_bg=Colors.SURFACE,
            with_card=False,
        )

        self._build_toggle_setting(section_body, "Desktop notifications", "notifications_enabled", True)
        self._build_toggle_setting(section_body, "Sound alerts", "sound_alerts_enabled", False)

    def _build_toggle_setting(self, parent, label: str, attr: str, initial: bool):
        """Build a simple toggle setting card."""
        setting_frame = tk.Frame(parent, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.SM)
        setting_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        tk.Label(
            setting_frame,
            text=label,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")

        current_value = getattr(self.user_settings, attr, initial)
        var = tk.BooleanVar(master=self, value=current_value)
        btn = DesignUtils.button(
            setting_frame,
            text="On" if current_value else "Off",
            variant="ghost",
            width=8,
        )
        btn.pack(side=tk.RIGHT)

        def toggle_setting():
            var.set(not var.get())
            btn.configure(text="On" if var.get() else "Off")
            setattr(self.user_settings, attr, var.get())
            save_user_settings(self.user_settings)

        btn.configure(command=toggle_setting)
        self._toggle_vars[attr] = var
        self._toggle_buttons[attr] = btn

    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        new_value = not self.theme_var.get()
        self.theme_var.set(new_value)
        self._sync_theme_button(new_value)

        # Only call app.toggle_theme if available
        app = getattr(self.context, "app", None)
        if app and hasattr(app, "toggle_theme"):
            app.toggle_theme(new_value)

        self.user_settings.theme_mode = "dark" if new_value else "light"
        save_user_settings(self.user_settings)

    def _cycle_accent_color(self):
        """Cycle through accent colors."""
        current = ThemeManager.get_current_accent_name()
        accents = ["blue", "purple", "green", "orange", "pink", "red"]
        current_index = accents.index(current) if current in accents else 0
        next_index = (current_index + 1) % len(accents)
        next_accent = accents[next_index]

        ThemeManager.set_accent_color(next_accent)

        if hasattr(self, "accent_preview_label"):
            self.accent_preview_label.configure(text=f"● Current: {next_accent.title()}")

    def on_show(self):
        self.user_settings = get_user_settings()
        current = self.user_settings.theme_mode == "dark"
        if hasattr(self, "theme_var"):
            self.theme_var.set(current)
            self._sync_theme_button(current)
        for attr, btn in self._toggle_buttons.items():
            value = getattr(self.user_settings, attr, False)
            var = self._toggle_vars.get(attr)
            if var:
                var.set(value)
            btn.configure(text="On" if value else "Off")

    def destroy(self):
        return super().destroy()

    def _sync_theme_button(self, value: bool | None = None):
        if not self._theme_button:
            return
        if value is None and hasattr(self, "theme_var"):
            value = self.theme_var.get()
        if value is None:
            value = False
        self._theme_button.configure(text="On" if value else "Off")
