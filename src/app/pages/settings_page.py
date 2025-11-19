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

        # Single Button for Dark Mode
        is_dark = self.user_settings.theme_mode == "dark"
        self.theme_var = tk.BooleanVar(value=is_dark)
        
        toggle_btn = DesignUtils.button(
            section_body,
            text=f"Dark Mode: {'On' if is_dark else 'Off'}",
            variant="secondary",
        )
        toggle_btn.pack(anchor="w", pady=(0, Spacing.SM))
        self._theme_button = toggle_btn

        def _on_toggle():
            # 1. Immediate UI Update
            new_state = not self.theme_var.get()
            self.theme_var.set(new_state)
            toggle_btn.configure(text=f"Dark Mode: {'On' if new_state else 'Off'}")

            # 2. Defer Heavy Lifting
            def _apply_theme_change():
                app = getattr(self.context, "app", None)
                if app and hasattr(app, "toggle_theme"):
                    app.toggle_theme(new_state)
                
                self.user_settings.theme_mode = "dark" if new_state else "light"
                save_user_settings(self.user_settings)

            self.after(10, _apply_theme_change)

        toggle_btn.configure(command=_on_toggle)

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
            # Immediate UI update
            new_val = not var.get()
            var.set(new_val)
            btn.configure(text="On" if new_val else "Off")
            
            # Update settings object
            setattr(self.user_settings, attr, new_val)
            
            # Save in background (or just don't block if possible, but here we just call it)
            # Ideally save_user_settings should be fast or async.
            # For now, we ensure UI updates first.
            self.after(10, lambda: save_user_settings(self.user_settings))

        btn.configure(command=toggle_setting)
        self._toggle_vars[attr] = var
        self._toggle_buttons[attr] = btn


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

