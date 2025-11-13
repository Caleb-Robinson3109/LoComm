"""Settings page matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, Spacing, DesignUtils, ThemeManager, Typography, Space
from utils.user_settings import get_user_settings, save_user_settings
from ui.helpers import create_scroll_container
from .base_page import BasePage, PageContext


class SettingsPage(BasePage):
    """Settings page with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.user_settings = get_user_settings()
        self._toggle_vars: dict[str, tk.BooleanVar] = {}
        self._toggle_buttons: dict[str, tk.Widget] = {}
        self._theme_button: tk.Widget | None = None
        
        # Simple scroll container like chat page
        scroll = create_scroll_container(
            self, 
            bg=Colors.SURFACE, 
            padding=(0, Spacing.LG)
        )
        body = scroll.frame

        self._build_title(body)
        self._build_appearance_section(body)
        self._build_settings_section(body)

    def _build_title(self, parent):
        """Build simple title section like chat page."""
        title_wrap = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
        )
        title_wrap.pack(fill=tk.X, pady=(0, Space.XS))

        tk.Label(
            title_wrap,
            text="Settings",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")

        tk.Label(
            title_wrap,
            text="Configure your Locomm experience",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

    def _build_appearance_section(self, parent):
        """Build clean appearance section."""
        section = tk.Frame(parent, bg=Colors.SURFACE, padx=Space.LG, pady=Space.MD)
        section.pack(fill=tk.BOTH, expand=True)
        
        # Section title
        tk.Label(
            section,
            text="Appearance",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        ).pack(anchor="w", pady=(0, Spacing.SM))
        
        # Theme setting
        self._build_theme_setting(section)
        
        # Accent color setting removed for simplicity
    
    def _build_settings_section(self, parent):
        """Build simple settings section."""
        section = tk.Frame(parent, bg=Colors.SURFACE, padx=Space.LG, pady=Space.MD)
        section.pack(fill=tk.BOTH, expand=True)
        
        # Section title
        tk.Label(
            section,
            text="Notifications & Diagnostics",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        ).pack(anchor="w", pady=(0, Spacing.SM))
        
        # Settings toggles
        self._build_toggle_setting(section, "Desktop notifications", "notifications_enabled", True)
        self._build_toggle_setting(section, "Sound alerts", "sound_alerts_enabled", False)

    def _build_theme_setting(self, parent):
        """Build theme setting with simple layout."""
        setting_frame = tk.Frame(parent, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.SM)
        setting_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Setting label
        tk.Label(
            setting_frame,
            text="Dark Mode",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")
        
        # Description
        tk.Label(
            setting_frame,
            text="Use dark theme for better battery life and reduced eye strain",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        ).pack(anchor="w", pady=(Space.XXS, 0))
        
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

    def _build_accent_color_setting(self, parent):
        """Build accent color setting."""
        setting_frame = tk.Frame(parent, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.SM)
        setting_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Setting label
        tk.Label(
            setting_frame,
            text="Accent Color",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")
        
        # Description
        tk.Label(
            setting_frame,
            text="Choose your preferred accent color theme",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        ).pack(anchor="w", pady=(Space.XXS, 0))
        
        # Color preview
        preview_frame = tk.Frame(setting_frame, bg=Colors.SURFACE_ALT)
        preview_frame.pack(anchor="w", pady=(Space.SM, 0))
        
        # Show current accent color
        tk.Label(
            preview_frame,
            text="● Current: " + ThemeManager.get_current_accent_name(),
            bg=Colors.SURFACE_ALT,
            fg=Colors.STATE_INFO,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
        ).pack(anchor="w")
        
        # Accent color cycling button
        DesignUtils.button(
            setting_frame,
            text="Change Color",
            command=self._cycle_accent_color,
            variant="ghost",
            width=15,
        ).pack(side=tk.RIGHT)

    def _build_toggle_setting(self, parent, label: str, attr: str, initial: bool):
        """Build a simple toggle setting."""
        setting_frame = tk.Frame(parent, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.SM)
        setting_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Setting label
        tk.Label(
            setting_frame,
            text=label,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM),
        ).pack(anchor="w")
        
        # Toggle button
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
        if self.context and hasattr(self.context.app, "toggle_theme"):
            self.context.app.toggle_theme(new_value)
        self.user_settings.theme_mode = "dark" if new_value else "light"
        save_user_settings(self.user_settings)

    def _cycle_accent_color(self):
        """Cycle through accent colors."""
        current = ThemeManager.get_current_accent_name()
        accents = ['blue', 'purple', 'green', 'orange', 'pink', 'red']
        current_index = accents.index(current) if current in accents else 0
        next_index = (current_index + 1) % len(accents)
        next_accent = accents[next_index]
        
        # Set the new accent color
        ThemeManager.set_accent_color(next_accent)
        
        # Update the preview
        if hasattr(self, 'accent_preview_label'):
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
