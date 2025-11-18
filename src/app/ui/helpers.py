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


def create_scroll_container(
    parent: tk.Misc,
    *,
    bg: str | None = None,
    padding: tuple[int, int] = (0, Spacing.LG),
) -> ScrollContainer:
    """
    Create a vertical scrollable area that resizes with the window.

    Use the returned ScrollContainer.frame as the content container.
    """
    ensure_styles_initialized()
    resolved_bg = bg or Colors.PANEL_BG

    # Outer wrapper that resizes with parent
    wrapper = tk.Frame(parent, bg=resolved_bg)
    wrapper.pack(fill=tk.BOTH, expand=True, padx=padding[0], pady=padding[1])

    # Canvas plus vertical scrollbar
    canvas = tk.Canvas(wrapper, bg=resolved_bg, highlightthickness=0, bd=0)
    scrollbar = tk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Inner frame that holds real content
    scrollable_frame = tk.Frame(canvas, bg=resolved_bg)
    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Keep scrollregion updated based on content height
    def _on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", _on_frame_configure)

    # Match inner width to canvas width, do not constrain height
    def _on_canvas_configure(event):
        canvas.itemconfigure(window_id, width=event.width)

    canvas.bind("<Configure>", _on_canvas_configure)

    # Global mouse wheel handling
    manager = _bind_mousewheel(canvas)

    def _on_destroy(_event):
        manager.unregister_canvas(canvas)

    wrapper.bind("<Destroy>", _on_destroy, add="+")

    return ScrollContainer(
        wrapper=wrapper,
        canvas=canvas,
        frame=scrollable_frame,
        scrollbar=scrollbar,
        window_id=window_id,
    )


def create_page_section(
    parent: tk.Misc,
    *,
    bg: str | None = None,
    padx: int = Spacing.LG,
    pady: tuple[int, int] | int = (Spacing.LG, Spacing.LG),
) -> tk.Frame:
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
    _instance: "GlobalMousewheelManager" | None = None
    _active_canvas: tk.Canvas | None = None
    _canvas_handlers: dict[tk.Canvas, dict[str, Callable]] = {}

    @classmethod
    def get_instance(cls) -> "GlobalMousewheelManager":
        if cls._instance is None:
            cls._instance = GlobalMousewheelManager()
        return cls._instance

    def register_canvas(self, canvas: tk.Canvas) -> None:
        def _on_mousewheel(event: tk.Event):
            if self._active_canvas == canvas:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_enter(event: tk.Event):
            self._active_canvas = canvas
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _on_leave(event: tk.Event):
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
            if self._active_canvas == canvas:
                self._active_canvas = None
                canvas.unbind_all("<MouseWheel>")
            del self._canvas_handlers[canvas]


def _bind_mousewheel(canvas: tk.Canvas) -> GlobalMousewheelManager:
    manager = GlobalMousewheelManager.get_instance()
    manager.register_canvas(canvas)
    return manager


def enable_global_mousewheel(canvas: tk.Canvas) -> None:
    """
    Enable mouse wheel scrolling for the given canvas.

    Only active while the mouse is over this canvas.
    """

    def _on_mousewheel(event: tk.Event):
        if event.delta != 0:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind(event: tk.Event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbind(event: tk.Event):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", _bind)
    canvas.bind("<Leave>", _unbind)


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


def sidebar_nav_section(
    parent: tk.Misc,
    items: list[tuple[str, str]],
    click_handler: Callable[[str], None],
    register_button: Callable[[str, tk.Widget], None] | None = None,
):
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
class AutoWrapLabel(tk.Label):
    """
    Label that automatically adjusts wraplength to its actual width.

    Use this for any paragraph / bullet text so it reflows on window resize.
    """
    def __init__(
        self,
        parent,
        *args,
        padding_x: int = 0,
        min_wrap: int = 240,
        **kwargs,
    ):
        # Do not pass wraplength here, we set it dynamically
        kwargs.pop("wraplength", None)
        super().__init__(parent, *args, **kwargs)
        self._padding_x = padding_x
        self._min_wrap = min_wrap

        # When the label is resized, recompute wraplength
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        target_width = max(self._min_wrap, event.width - self._padding_x)
        if self.cget("wraplength") != target_width:
            self.configure(wraplength=target_width)
