from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class PageContext:
    """Shared context handed to every page."""

    app: Any
    session: Any
    controller: Any
    navigator: Any  # MainFrame or any object exposing navigation helpers


class BasePage(tk.Frame):
    """Base class for all application pages to keep layout responsibilities centralized."""

    def __init__(self, master, context: Optional[PageContext] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.context = context

    # Hook methods for future lifecycle use
    def on_show(self):
        """Called when the page becomes visible."""
        pass

    def on_hide(self):
        """Called when the page is hidden."""
        pass

    def destroy(self):
        try:
            self.on_hide()
        except Exception:
            pass
        return super().destroy()
