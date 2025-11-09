"""Settings page leveraging the refreshed design system."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, Spacing, DesignUtils
from utils.ui_helpers import create_scroll_container
from .base_page import BasePage, PageContext


class SettingsPage(BasePage):
    """Minimal page announcing that settings live here."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(0, Spacing.LG))
        body = scroll.frame

        DesignUtils.hero_header(
            body,
            title="Locomm Desktop Settings",
            subtitle="Settings are handled elsewhere for now."
        )
