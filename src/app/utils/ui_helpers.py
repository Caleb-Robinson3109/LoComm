"""
Shared UI helper utilities for consistent layouts.
"""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Optional, List, Any

from .design_system import Colors, Spacing, DesignUtils


@dataclass
class ScrollContainer:
    wrapper: tk.Frame
    canvas: tk.Canvas
    frame: tk.Frame
    scrollbar: tk.Scrollbar
    window_id: int

    def destroy(self):
        """Tear down the scroll container and unregister bindings."""
        manager = GlobalMousewheelManager.get_instance()
        manager.unregister_canvas(self.canvas)
        if self.wrapper.winfo_exists():
            self.wrapper.destroy()

@dataclass
class PageScaffold:
    root: tk.Frame
    body: tk.Frame
    header: tk.Frame
    scroll: Optional[ScrollContainer]

    def destroy(self):
        if self.scroll:
            manager = GlobalMousewheelManager.get_instance()
            manager.unregister_canvas(self.scroll.canvas)
            if self.scroll.wrapper.winfo_exists():
                self.scroll.wrapper.destroy()
        if self.root.winfo_exists():
            self.root.destroy()

def create_scroll_container(parent: tk.Misc, *,
                            bg: str = Colors.BG_PRIMARY,
                            padding: tuple[int, int] = (0, Spacing.LG)) -> ScrollContainer:
    """Create a vertical scroll container with unified styling."""
    wrapper = tk.Frame(parent, bg=bg)
    wrapper.pack(fill=tk.BOTH, expand=True, padx=padding[0], pady=padding[1])

    canvas = tk.Canvas(wrapper, bg=bg, highlightthickness=0)
    scrollbar = tk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg)

    def _sync_scrollregion(event, target_canvas=canvas):
        target_canvas.configure(scrollregion=target_canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", _sync_scrollregion)

    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    manager = _bind_mousewheel(canvas)

    canvas.pack(side="left", fill="both", expand=True)

    def _resize_inner(event):
        canvas.itemconfig(window_id, width=event.width, height=event.height)

    canvas.bind("<Configure>", _resize_inner)
    scrollbar.pack(side="right", fill="y")

    def _on_destroy(_event):
        manager.unregister_canvas(canvas)

    wrapper.bind("<Destroy>", _on_destroy, add="+")

    return ScrollContainer(wrapper=wrapper, canvas=canvas, frame=scrollable_frame, scrollbar=scrollbar, window_id=window_id)


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


def _bind_mousewheel(canvas: tk.Canvas) -> GlobalMousewheelManager:
    """Attach consistent mousewheel handlers to a canvas."""
    manager = GlobalMousewheelManager.get_instance()
    manager.register_canvas(canvas)
    return manager


def enable_global_mousewheel(widget: tk.Canvas) -> None:
    """Public helper to enable shared mousewheel behavior on any scrollable canvas."""
    _bind_mousewheel(widget)


def create_page_scaffold(
    parent: tk.Misc,
    *,
    title: str,
    subtitle: str = "",
    actions: Optional[List[dict[str, Any]]] = None,
    use_scroll: bool = True,
    padding: tuple[int, int] = (0, Spacing.LG),
    bg: str = Colors.SURFACE,
) -> PageScaffold:
    """Convenience wrapper that builds a page root, header, and optional scroll body."""
    root = tk.Frame(parent, bg=bg)
    root.pack(fill=tk.BOTH, expand=True)

    if use_scroll:
        scroll = create_scroll_container(root, bg=bg, padding=padding)
        body = scroll.frame
    else:
        scroll = None
        body = tk.Frame(root, bg=bg)
        body.pack(fill=tk.BOTH, expand=True, padx=padding[0], pady=padding[1])

    header = DesignUtils.hero_header(body, title=title, subtitle=subtitle, actions=actions)
    return PageScaffold(root=root, body=body, header=header, scroll=scroll)


def create_table_card(parent: tk.Misc, *, padding: int = Spacing.MD):
    """Builds a bordered card with a table area and footer row."""
    card = tk.Frame(
        parent,
        bg=Colors.SURFACE_ALT,
        highlightbackground=Colors.BORDER,
        highlightthickness=1,
        bd=0,
    )
    card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
    card.pack_propagate(False)
    content = tk.Frame(card, bg=Colors.SURFACE_ALT)
    content.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)

    table_wrapper = tk.Frame(content, bg=Colors.SURFACE_ALT)
    table_wrapper.pack(fill=tk.BOTH, expand=True)

    footer = tk.Frame(content, bg=Colors.SURFACE_ALT)
    footer.pack(fill=tk.X, pady=(Spacing.SM, 0))
    return card, table_wrapper, footer
