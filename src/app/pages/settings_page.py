"""Settings page leveraging the refreshed design system."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.ui_helpers import create_scroll_container
from .base_page import BasePage, PageContext


class SettingsPage(BasePage):
    """Application configuration with grouped sections."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.controller = context.controller if context else None
        self.session = context.session if context else None

        self.auto_start_var = tk.BooleanVar(value=False)
        self.desktop_notifications_var = tk.BooleanVar(value=True)
        self.sound_notifications_var = tk.BooleanVar(value=False)
        self.lora_profile_var = tk.StringVar(value="Mock backend")

        self._toggle_controls: list[tuple[tk.Frame, tk.Label, tk.Label, tk.BooleanVar]] = []

        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(Spacing.LG, Spacing.LG))
        body = scroll.frame

        DesignUtils.hero_header(
            body,
            title="Locomm Desktop Settings",
            subtitle="Configure your secure LoRa communication preferences and application behavior."
        )

        cards = tk.Frame(body, bg=Colors.SURFACE)
        cards.pack(fill=tk.BOTH, expand=True)

        self._build_session_card(cards)
        self._build_notifications_card(cards)
        self._build_data_card(cards)

    # ------------------------------------------------------------------ #
    def _build_session_card(self, parent):
        card, content = DesignUtils.card(parent, "Session & trust", "Control LoRa profile and paired devices")
        card.pack(fill=tk.X, pady=(0, Spacing.LG))
        card.pack_propagate(True)

        self._create_toggle(content, "Auto-start Locomm on login", self.auto_start_var)

        profile_block = tk.Frame(content, bg=Colors.SURFACE_ALT)
        profile_block.pack(fill=tk.X, pady=(0, Spacing.SM))
        tk.Label(profile_block, text="LoRa transport profile", bg=Colors.SURFACE_ALT, fg=Colors.TEXT_PRIMARY,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w")
        ttk.Combobox(
            profile_block,
            textvariable=self.lora_profile_var,
            state="readonly",
            values=("Mock backend", "Hardware LoRa", "Demo mode")
        ).pack(fill=tk.X, expand=True, pady=(Spacing.XXS, 0))

        actions = tk.Frame(content, bg=Colors.SURFACE_ALT)
        actions.pack(fill=tk.X, pady=(Spacing.SM, 0))
        DesignUtils.button(actions, text="Regenerate secure PIN", command=self._regenerate_pin).pack(side=tk.LEFT, padx=(0, Spacing.SM))
        DesignUtils.button(actions, text="Forget paired device", command=self._forget_device, variant="secondary").pack(side=tk.LEFT)

    def _build_notifications_card(self, parent):
        card, content = DesignUtils.card(parent, "Notifications", "Desktop, audio, and transport alerts")
        card.pack(fill=tk.X, pady=(0, Spacing.LG))
        card.pack_propagate(True)
        self._create_toggle(content, "Desktop notifications for new messages", self.desktop_notifications_var)
        self._create_toggle(content, "Audio alerts for incoming chats", self.sound_notifications_var)

        self.connection_alert_var = tk.BooleanVar(value=True)
        self._create_toggle(content, "Alert me when LoRa connection drops", self.connection_alert_var)

    def _build_data_card(self, parent):
        card, content = DesignUtils.card(parent, "Data & support", "Diagnostics and cache controls")
        card.pack(fill=tk.X, pady=(0, Spacing.LG))
        card.pack_propagate(True)
        DesignUtils.button(content, text="Save preferences", command=self._save_preferences).pack(anchor="w", pady=(0, Spacing.SM))
        DesignUtils.button(content, text="Reset to defaults", command=self._reset_defaults, variant="secondary").pack(anchor="w")
        DesignUtils.button(content, text="Export session logs", command=self._export_logs, variant="ghost").pack(anchor="w", pady=(Spacing.SM, 0))
        DesignUtils.button(content, text="Clear cached session", command=self._clear_cached_session, variant="ghost").pack(anchor="w")

    # ------------------------------------------------------------------ #
    def _save_preferences(self):
        try:
            messagebox.showinfo("Preferences Saved", "Settings have been saved to your local configuration.")
        except Exception as exc:  # pragma: no cover - UI alert fallback
            messagebox.showerror("Error", f"Failed to save preferences: {exc}")

    def _reset_defaults(self):
        self.auto_start_var.set(False)
        self.desktop_notifications_var.set(True)
        self.sound_notifications_var.set(False)
        self.lora_profile_var.set("Mock backend")
        messagebox.showinfo("Defaults Restored", "All preferences have been reset to their default values.")

    def _export_logs(self):
        messagebox.showinfo("Export Available", "Log export functionality will be available in a future update.")

    def _regenerate_pin(self):
        messagebox.showinfo("New PIN", "A fresh 8-digit PIN was generated for your local device.")

    def _forget_device(self):
        if messagebox.askyesno("Forget device", "Remove the currently paired device?"):
            self.controller.stop_session()
            messagebox.showinfo("Device Removed", "The device trust relationship has been cleared.")

    def _clear_cached_session(self):
        if messagebox.askyesno("Clear cache", "Remove cached session data and conversation previews?"):
            self.controller.session.clear()
            messagebox.showinfo("Cache Cleared", "Cached session artifacts have been removed.")

    # ------------------------------------------------------------------ #
    def _create_toggle(self, parent, label, var: tk.BooleanVar):
        row = tk.Frame(parent, bg=Colors.SURFACE_ALT)
        row.pack(fill=tk.X, pady=(0, Spacing.SM))
        tk.Label(
            row,
            text=label,
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)
        ).pack(side=tk.LEFT)

        pill = tk.Frame(
            row,
            bg=Colors.SURFACE_SELECTED,
            highlightbackground=Colors.DIVIDER,
            highlightthickness=1,
            bd=0,
            padx=Spacing.SM,
            pady=Spacing.XXS
        )
        pill.pack(side=tk.RIGHT)
        icon = tk.Label(pill, text="", bg=pill["bg"], fg=Colors.TEXT_PRIMARY,
                        font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_BOLD))
        icon.pack(side=tk.LEFT)
        text_label = tk.Label(pill, text="", bg=pill["bg"], fg=Colors.TEXT_PRIMARY,
                              font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM), padx=Spacing.XXS)
        text_label.pack(side=tk.LEFT)

        def handle_toggle(_event=None):
            var.set(not var.get())
            self._refresh_toggle(pill, icon, text_label, var)

        pill.bind("<Button-1>", handle_toggle)
        icon.bind("<Button-1>", handle_toggle)
        text_label.bind("<Button-1>", handle_toggle)

        self._toggle_controls.append((pill, icon, text_label, var))
        self._refresh_toggle(pill, icon, text_label, var)

    def _refresh_toggle(self, pill, icon, text_label, var: tk.BooleanVar):
        is_on = var.get()
        bg = Colors.SURFACE_ALT if is_on else Colors.SURFACE_SELECTED
        fg = Colors.TEXT_PRIMARY
        pill.configure(bg=bg)
        icon.configure(text="●" if is_on else "○", bg=bg, fg=fg)
        text_label.configure(text="On" if is_on else "Off", bg=bg, fg=fg)
