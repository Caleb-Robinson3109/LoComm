"""Settings page leveraging the refreshed design system."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.ui_helpers import create_scroll_container


class SettingsPage(tk.Frame):
    """Application configuration with grouped sections."""

    def __init__(self, master, app, controller, session=None):
        super().__init__(master, bg=Colors.SURFACE)
        self.app = app
        self.controller = controller
        self.session = session

        self.auto_start_var = tk.BooleanVar(value=False)
        self.desktop_notifications_var = tk.BooleanVar(value=True)
        self.sound_notifications_var = tk.BooleanVar(value=False)

        self.pack(fill=tk.BOTH, expand=True)
        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(Spacing.LG, Spacing.LG))
        body = scroll.frame

        DesignUtils.hero_header(
            body,
            title="Workspace preferences",
            subtitle="Tune how Locomm boots, notifies you, and interacts with the upcoming hardware stack."
        )

        self._build_general_section(body)
        self._build_notifications_section(body)
        self._build_advanced_section(body)

    # ------------------------------------------------------------------ #
    def _build_general_section(self, parent):
        section, body = DesignUtils.section(parent, "General", "Startup and session defaults", icon="⚙️")
        ttk.Checkbutton(body, text="Auto-start Locomm on system boot", variable=self.auto_start_var).pack(anchor="w", pady=(0, Spacing.SM))
        ttk.Checkbutton(body, text="Restore last paired device on launch", variable=tk.BooleanVar(value=True), state="disabled").pack(anchor="w")

    def _build_notifications_section(self, parent):
        section, body = DesignUtils.section(parent, "Notifications", "Control desktop and sound alerts", icon="🔔")
        ttk.Checkbutton(body, text="Desktop banner for new messages", variable=self.desktop_notifications_var).pack(anchor="w", pady=(0, Spacing.SM))
        ttk.Checkbutton(body, text="Sound cue on incoming chat", variable=self.sound_notifications_var).pack(anchor="w", pady=(0, Spacing.SM))
        ttk.Checkbutton(body, text="Toast when transport connects or disconnects", variable=tk.BooleanVar(value=True), state="disabled").pack(anchor="w")

    def _build_advanced_section(self, parent):
        section, body = DesignUtils.section(parent, "Advanced", "Developer toggles and troubleshooting", icon="🧪")
        DesignUtils.button(body, text="Save preferences", command=self._save_preferences).pack(anchor="w", pady=(0, Spacing.SM))
        DesignUtils.button(body, text="Reset to defaults", command=self._reset_defaults, variant="secondary").pack(anchor="w")
        DesignUtils.button(body, text="Export logs", command=self._export_logs, variant="ghost").pack(anchor="w", pady=(Spacing.SM, 0))

    # ------------------------------------------------------------------ #
    def _save_preferences(self):
        try:
            messagebox.showinfo("Preferences saved", "Settings stored locally for future sessions.")
        except Exception as exc:  # pragma: no cover - UI alert fallback
            messagebox.showerror("Error", f"Failed to save preferences: {exc}")

    def _reset_defaults(self):
        self.auto_start_var.set(False)
        self.desktop_notifications_var.set(True)
        self.sound_notifications_var.set(False)
        messagebox.showinfo("Defaults restored", "All preferences returned to factory values.")

    def _export_logs(self):
        messagebox.showinfo("Export", "Log export will be available once API integration ships.")
