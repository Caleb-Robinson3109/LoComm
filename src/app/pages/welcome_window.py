"""Welcome window shown before login to introduce Locomm."""
from __future__ import annotations

import tkinter as tk
from typing import Callable

from utils.design_system import Colors, Spacing, Typography, DesignUtils
from ui.helpers import AutoWrapLabel


class WelcomeWindow(tk.Frame):
    """Lightweight welcome experience shown before authentication."""

    def __init__(self, master, on_login: Callable[[], None], on_signup: Callable[[], None]):
        super().__init__(master, bg=Colors.SURFACE, padx=Spacing.LG, pady=Spacing.LG)
        self.on_login = on_login
        self.on_signup = on_signup

        self._build_content()

    def _build_content(self):
        hero = tk.Frame(self, bg=Colors.SURFACE, pady=Spacing.LG)
        hero.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            hero,
            text="Locomm",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="center")

        tk.Frame(hero, height=Spacing.XL, bg=Colors.SURFACE).pack(fill=tk.X)

        AutoWrapLabel(
            hero,
            text="No tracking. No profiling. Just conversations.",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_14),
            padding_x=0,
        ).pack(fill=tk.X, pady=(Spacing.LG, Spacing.LG))

        action_row = tk.Frame(hero, bg=Colors.SURFACE)
        action_row.pack(fill=tk.X, pady=(Spacing.MD, 0))

        DesignUtils.button(
            action_row,
            text="Sign Up",
            command=self.on_signup,
            variant="secondary",
            width=9,
        ).pack(side=tk.LEFT, padx=(0, Spacing.SM))

        DesignUtils.button(
            action_row,
            text="Login",
            command=self.on_login,
            variant="primary",
            width=9,
        ).pack(side=tk.LEFT)
