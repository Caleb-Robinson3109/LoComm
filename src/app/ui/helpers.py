"""Reusable helpers for page scaffolding, scroll containers, and keyboard interactions."""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Optional, List, Any

from ui.theme_tokens import Colors, Spacing, Typography
from ui.theme_manager import ensure_styles_initialized
from ui.components import DesignUtils


@dataclass
class ScrollContainer:
    wrapper: tk.Frame
    canvas: tk.Canvas
    frame: tk.Frame
    scrollbar: tk.Scrollbar
    window_id: int

    def destroy(self):
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
            self.scroll.destroy()
        if self.root.winfo_exists():
            self.root.destroy()


def create_scroll_container(parent: tk.Misc, *, bg: str | None = None, padding: tuple[int, int] = (0, Spacing.LG)) -> ScrollContainer:
    ensure_styles_initialized()
    resolved_bg = bg or Colors.PANEL_BG
    wrapper = tk.Frame(parent, bg=resolved_bg)
    wrapper.pack(fill=tk.BOTH, expand=True, padx=padding[0], pady=padding[1])

    canvas = tk.Canvas(wrapper, bg=resolved_bg, highlightthickness=0)
    scrollbar = tk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=resolved_bg)

    def _sync_scrollregion(event, target_canvas=canvas):
        target_canvas.configure(scrollregion=target_canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", _sync_scrollregion)

    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    manager = _bind_mousewheel(canvas)

    canvas.pack(side="left", fill="both", expand=True)

    def _resize_inner(event):
        canvas.itemconfig(window_id, width=event.width)

    canvas.bind("<Configure>", _resize_inner)
    scrollbar.pack(side="right", fill="y")

    def _on_destroy(_event):
        manager.unregister_canvas(canvas)

    wrapper.bind("<Destroy>", _on_destroy, add="+")

    return ScrollContainer(wrapper=wrapper, canvas=canvas, frame=scrollable_frame, scrollbar=scrollbar, window_id=window_id)


def create_page_section(parent: tk.Misc, *, bg: str | None = None, padx: int = Spacing.LG, pady: tuple[int, int] | int = (Spacing.LG, Spacing.LG)) -> tk.Frame:
    ensure_styles_initialized()
    resolved_bg = bg or Colors.SURFACE
    if isinstance(pady, tuple):
        pady_top, pady_bottom = pady
    else:
        pady_top = pady_bottom = pady
    frame = tk.Frame(parent, bg=resolved_bg)
    frame.pack(fill=tk.BOTH, expand=True, padx=padx, pady=(pady_top, pady_bottom))
    return frame


class GlobalMousewheelManager:
    _instance = None
    _active_canvas = None
    _canvas_handlers = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GlobalMousewheelManager()
        return cls._instance

    def register_canvas(self, canvas: tk.Canvas) -> None:
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

        self._canvas_handlers[canvas] = {
            "mousewheel": _on_mousewheel,
            "enter": _on_enter,
            "leave": _on_leave,
        }

        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)

    def unregister_canvas(self, canvas: tk.Canvas) -> None:
        if canvas in self._canvas_handlers:
            del self._canvas_handlers[canvas]
            if self._active_canvas == canvas:
                self._active_canvas = None
                canvas.unbind_all("<MouseWheel>")


def _bind_mousewheel(canvas: tk.Canvas) -> GlobalMousewheelManager:
    manager = GlobalMousewheelManager.get_instance()
    manager.register_canvas(canvas)
    return manager


def enable_global_mousewheel(widget: tk.Canvas) -> None:
    _bind_mousewheel(widget)


def create_page_scaffold(parent: tk.Misc, *, title: str, subtitle: str = "", actions: Optional[List[dict[str, Any]]] = None, use_scroll: bool = True, padding: tuple[int, int] = (0, Spacing.LG), bg: str = Colors.SURFACE) -> PageScaffold:
    root = tk.Frame(parent, bg=bg)
    root.pack(fill=tk.BOTH, expand=True)

    if use_scroll:
        scroll = create_scroll_container(root, bg=bg, padding=padding)
        body = scroll.frame
    else:
        scroll = None
        body = tk.Frame(root, bg=bg)
        body.pack(fill=tk.BOTH, expand=True, padx=padding[0], pady=padding[1])

    from ui.components import DesignUtils

    header = DesignUtils.hero_header(body, title=title, subtitle=subtitle, actions=actions)
    return PageScaffold(root=root, body=body, header=header, scroll=scroll)


def create_table_card(parent: tk.Misc, *, padding: int = Spacing.MD):
    card = tk.Frame(
        parent,
        bg=Colors.CARD_PANEL_BG,
        highlightbackground=Colors.CARD_PANEL_BORDER,
        highlightthickness=1,
        bd=0,
    )
    card.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))
    card.pack_propagate(False)
    content = tk.Frame(card, bg=Colors.CARD_PANEL_BG)
    content.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)

    table_wrapper = tk.Frame(content, bg=Colors.CARD_PANEL_BG)
    table_wrapper.pack(fill=tk.BOTH, expand=True)

    footer = tk.Frame(content, bg=Colors.CARD_PANEL_BG)
    footer.pack(fill=tk.X, pady=(Spacing.SM, 0))
    return card, table_wrapper, footer


def sidebar_container(parent: tk.Misc, *, padding: tuple[int, int] | None = None):
    padding = padding or (Spacing.MD, Spacing.MD)
    container = tk.Frame(parent, bg=Colors.BG_ELEVATED)
    container.pack(fill=tk.BOTH, expand=True, padx=padding[0], pady=padding[1])
    return container


def sidebar_nav_section(parent: tk.Misc, items: list[tuple[str, str]], click_handler: Callable[[str], None], register_button: Callable[[str, tk.Widget], None] | None = None):
    section = tk.Frame(parent, bg=Colors.BG_ELEVATED)
    section.pack(fill=tk.X)
    for key, label in items:
        btn = DesignUtils.create_nav_button(section, label, lambda k=key: click_handler(k))
        btn.pack(fill=tk.X, pady=(0, Spacing.SM))
        if register_button:
            register_button(key, btn)
    return section


def sidebar_footer(parent: tk.Misc, version_label: str):
    footer = tk.Frame(parent, bg=Colors.BG_ELEVATED)
    footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(Spacing.XS, Spacing.XS))
    tk.Label(
        footer,
        text=version_label,
        bg=Colors.SURFACE_SIDEBAR,
        fg=Colors.TEXT_MUTED,
        font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
    ).pack(anchor="w", padx=Spacing.MD, pady=(0, Spacing.XXS))
    return footer
