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
                            padding: tuple[int, int] = (Spacing.TAB_PADDING, Spacing.TAB_PADDING)) -> ScrollContainer:
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


def _bind_mousewheel(canvas: tk.Canvas) -> None:
    """Attach consistent mousewheel handlers to a canvas."""

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_to_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbind_from_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", _bind_to_mousewheel)
    canvas.bind("<Leave>", _unbind_from_mousewheel)
