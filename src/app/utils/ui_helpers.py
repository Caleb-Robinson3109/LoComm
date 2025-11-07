"""
Shared UI helper utilities for consistent layouts.
"""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Callable

from .design_system import Colors, Spacing


@dataclass
class ScrollContainer:
    wrapper: tk.Frame
    canvas: tk.Canvas
    frame: tk.Frame
    scrollbar: tk.Scrollbar


def create_scroll_container(parent: tk.Misc, *,
                            bg: str = Colors.BG_PRIMARY,
                            padding: tuple[int, int] = (Spacing.XL, Spacing.XL)) -> ScrollContainer:
    """Create a vertical scroll container with unified styling."""
    wrapper = tk.Frame(parent, bg=bg)
    wrapper.pack(fill=tk.BOTH, expand=True, padx=padding[0], pady=padding[1])

    canvas = tk.Canvas(wrapper, bg=bg, highlightthickness=0)
    scrollbar = tk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    _bind_mousewheel(canvas)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return ScrollContainer(wrapper=wrapper, canvas=canvas, frame=scrollable_frame, scrollbar=scrollbar)


class GlobalMousewheelManager:
    """CRITICAL FIX: Global mousewheel manager to prevent scrolling conflicts."""

    _instance = None
    _active_canvas = None
    _canvas_handlers = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GlobalMousewheelManager()
        return cls._instance

    def register_canvas(self, canvas: tk.Canvas) -> None:
        """Register a canvas for mousewheel scrolling."""
        def _on_mousewheel(event):
            if self._active_canvas == canvas:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_enter(event):
            self._active_canvas = canvas
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _on_leave(event):
            if self._active_canvas == canvas:
                self._active_canvas = None
                canvas.unbind_all("<MouseWheel>")

        # Store handlers to prevent garbage collection
        self._canvas_handlers[canvas] = {
            'mousewheel': _on_mousewheel,
            'enter': _on_enter,
            'leave': _on_leave
        }

        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)

    def unregister_canvas(self, canvas: tk.Canvas) -> None:
        """Unregister a canvas from mousewheel scrolling."""
        if canvas in self._canvas_handlers:
            del self._canvas_handlers[canvas]
            if self._active_canvas == canvas:
                self._active_canvas = None
                canvas.unbind_all("<MouseWheel>")


def _bind_mousewheel(canvas: tk.Canvas) -> None:
    """Attach consistent mousewheel handlers to a canvas."""
    manager = GlobalMousewheelManager.get_instance()
    manager.register_canvas(canvas)
