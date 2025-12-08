"""Reusable helpers for page scaffolding, scroll containers, dialogs, and keyboard interactions."""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Optional, List, Any, Dict

from ui.theme_tokens import Colors, Spacing, Typography
from ui.theme_manager import ensure_styles_initialized
from ui.components import DesignUtils
from utils.window_sizing import WindowSize


# --------------------------------------------------------------------------- #
# Scroll containers and page scaffold
# --------------------------------------------------------------------------- #


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


# --------------------------------------------------------------------------- #
# Mouse wheel management
# --------------------------------------------------------------------------- #


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
    bg: str | None = None,
) -> PageScaffold:
    """
    For new pages prefer create_page_header directly.
    """
    ensure_styles_initialized()
    resolved_bg = bg or Colors.SURFACE
    root = tk.Frame(parent, bg=resolved_bg)
    root.pack(fill=tk.BOTH, expand=True)

    if use_scroll:
        scroll = create_scroll_container(root, bg=resolved_bg, padding=padding)
        body = scroll.frame
    else:
        scroll = None
        body = tk.Frame(root, bg=resolved_bg)
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


# --------------------------------------------------------------------------- #
# Sidebar scaffolding
# --------------------------------------------------------------------------- #


def sidebar_container(parent: tk.Misc, *, padding: tuple[int, int] | None = None):
    padding = padding or (Spacing.SM, Spacing.SM)
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
        try:
            btn.configure(anchor="center", justify="center")
        except Exception:
            pass
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


# --------------------------------------------------------------------------- #
# Auto wrapping labels and standard buttons / headers / sections
# --------------------------------------------------------------------------- #


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

        # Default to left alignment unless caller overrides
        if "justify" not in kwargs:
            kwargs["justify"] = "left"
        if "anchor" not in kwargs:
            kwargs["anchor"] = "w"

        super().__init__(parent, *args, **kwargs)
        self._padding_x = padding_x
        self._min_wrap = min_wrap

        # When the label is resized, recompute wraplength
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        # event.width is the allocated width of the label
        target_width = max(self._min_wrap, event.width - self._padding_x)
        # Always set; cost is negligible and avoids Tcl_Obj casting issues
        self.configure(wraplength=target_width)


def create_back_button(parent: tk.Misc, command: Callable[[], None], text: str = "← Back") -> tk.Button:
    """
    Standard back button for all pages.
    Use this everywhere instead of a raw tk.Button.
    """
    ensure_styles_initialized()
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=Colors.SURFACE,
        fg=Colors.TEXT_PRIMARY,
        relief=tk.FLAT,
        padx=Spacing.SM,
        pady=int(Spacing.XS / 2),
        activebackground=Colors.SURFACE,
        activeforeground=Colors.TEXT_PRIMARY,
        cursor="hand2",
        borderwidth=0,
        highlightthickness=0,
        font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
    )
    return btn


def create_page_header(
    parent: tk.Misc,
    *,
    title: str,
    subtitle: str = "",
    show_back: bool = False,
    on_back: Optional[Callable[[], None]] = None,
    actions: Optional[List[dict[str, Any]]] = None,
    action_refs: Optional[Dict[str, tk.Button]] = None,
    padx: int | tuple[int, int] = Spacing.SM,
) -> tk.Frame:
    """
    Standard page header:
    - optional back button row
    - title + subtitle on the left
    - optional actions (buttons) on the right
    - bottom divider
    """
    ensure_styles_initialized()

    # Optional back row
    if show_back and on_back:
        back_row = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=padx,
            pady=Spacing.XXS,
        )
        back_row.pack(fill=tk.X, pady=(0, Spacing.XXS))

        back_btn = create_back_button(back_row, on_back)
        back_btn.pack(anchor="w")

    # Main header row
    header = tk.Frame(
        parent,
        bg=Colors.SURFACE,
        padx=padx,
    )
    header.pack(fill=tk.X, pady=(0, Spacing.XS))

    text_wrap = tk.Frame(header, bg=Colors.SURFACE)
    text_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)

    actions_wrap = tk.Frame(header, bg=Colors.SURFACE)
    actions_wrap.pack(side=tk.RIGHT)

    tk.Label(
        text_wrap,
        text=title,
        bg=Colors.SURFACE,
        fg=Colors.TEXT_PRIMARY,
        font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        anchor="w",
        justify="left",
    ).pack(anchor="w")

    if subtitle:
        AutoWrapLabel(
            text_wrap,
            text=subtitle,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            padding_x=Spacing.SM * 2,
            min_wrap=240,
        ).pack(fill=tk.X, expand=True, pady=(Spacing.XXS, 0))

    # Optional actions (buttons on the right)
    if actions:
        for action in actions:
            btn = DesignUtils.button(
                actions_wrap,
                text=action.get("text", "Action"),
                command=action.get("command"),
                variant=action.get("variant", "primary"),
                width=action.get("width"),
            )
            side = action.get("side", "right")
            pad = action.get("padx", (0, Spacing.XS))
            btn.pack(side=tk.LEFT if side == "left" else tk.RIGHT, padx=pad)
            key = action.get("key")
            if action_refs and key:
                action_refs[key] = btn

    # Divider at bottom of header
    separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
    separator.pack(fill=tk.X, pady=(0, Spacing.SM))

    return header


def create_standard_section(
    parent: tk.Misc,
    *,
    title: Optional[str] = None,
    bg: str = Colors.SURFACE,
    inner_bg: str = Colors.SURFACE_ALT,
    with_card: bool = True,
) -> tuple[tk.Frame, tk.Frame]:
    """
    Standard content section:
    - outer section with page padding
    - optional title
    - inner card frame for content
    Returns (section_frame, content_frame).
    """
    ensure_styles_initialized()

    section = tk.Frame(parent, bg=bg, padx=Spacing.LG, pady=Spacing.MD)
    section.pack(fill=tk.BOTH, expand=True)

    if title:
        tk.Label(
            section,
            text=title,
            bg=bg,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
            anchor="w",
            justify="left",
        ).pack(anchor="w", pady=(0, Spacing.SM))

    if with_card:
        content = tk.Frame(section, bg=inner_bg, padx=Spacing.MD, pady=Spacing.MD)
        content.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.SM))
    else:
        content = section

    return section, content


# --------------------------------------------------------------------------- #
# Modal / dialog scaffolding for things like login box
# --------------------------------------------------------------------------- #


@dataclass
class ModalScaffold:
    toplevel: tk.Toplevel
    root: tk.Frame
    body: tk.Frame
    header: Optional[tk.Frame]


def create_centered_modal(
    parent: tk.Misc,
    *,
    title: str,
    width_ratio: float = 0.4,
    height_ratio: float = 0.4,
    min_width: int = 400,
    min_height: int = 280,
    bg: str | None = None,
    use_scroll: bool = False,
    padding: tuple[int, int] = (Spacing.LG, Spacing.LG),
    window_size: WindowSize | None = None,
) -> ModalScaffold:
    """
    Create a responsive centered modal suitable for login, pairing, etc.

    - Sizes relative to the parent screen
    - Contents laid out in a root frame that fills the window
    - Optional internal scroll container so content always fits
    """
    ensure_styles_initialized()
    resolved_bg = bg or Colors.SURFACE

    # Create modal window
    modal = tk.Toplevel(parent)
    modal.title(title)
    modal.configure(bg=resolved_bg)

    modal.update_idletasks()
    screen_w = modal.winfo_screenwidth()
    screen_h = modal.winfo_screenheight()

    if window_size:
        target_w = min(window_size.width, screen_w)
        target_h = min(window_size.height, screen_h)
        modal_min_width = min(window_size.min_width, screen_w)
        modal_min_height = min(window_size.min_height, screen_h)
        target_w = max(target_w, modal_min_width)
        target_h = max(target_h, modal_min_height)
    else:
        target_w = max(int(screen_w * width_ratio), min_width)
        target_h = max(int(screen_h * height_ratio), min_height)
        modal_min_width = min_width
        modal_min_height = min_height

    pos_x = (screen_w - target_w) // 2
    pos_y = (screen_h - target_h) // 2

    modal.geometry(f"{target_w}x{target_h}+{pos_x}+{pos_y}")
    modal.minsize(modal_min_width, modal_min_height)
    modal.resizable(True, True)
    modal.transient(parent.winfo_toplevel())
    modal.grab_set()

    # Root content frame
    root = tk.Frame(modal, bg=resolved_bg)
    root.pack(fill=tk.BOTH, expand=True)

    # Optional scroll inside modal so content is never cut off
    if use_scroll:
        scroll = create_scroll_container(root, bg=resolved_bg, padding=padding)
        body = scroll.frame
    else:
        scroll = None
        body = tk.Frame(root, bg=resolved_bg)
        body.pack(fill=tk.BOTH, expand=True, padx=padding[0], pady=padding[1])

    # Simple header row for modal title
    header = tk.Frame(body, bg=resolved_bg, padx=Spacing.SM, pady=Spacing.SM)
    header.pack(fill=tk.X, pady=(0, Spacing.SM))

    tk.Label(
        header,
        text=title,
        bg=resolved_bg,
        fg=Colors.TEXT_PRIMARY,
        font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        anchor="w",
        justify="left",
    ).pack(anchor="w")

    separator = tk.Frame(body, bg=Colors.DIVIDER, height=1)
    separator.pack(fill=tk.X, pady=(0, Spacing.SM))

    return ModalScaffold(toplevel=modal, root=root, body=body, header=header)


def create_form_row(
    parent: tk.Misc,
    *,
    label: str,
    widget_factory: Callable[[tk.Misc], tk.Widget],
    help_text: str | None = None,
) -> tuple[tk.Frame, tk.Widget]:
    """
    Standard responsive form row for dialogs and settings.

    - Label on top
    - Entry / widget below
    - Optional AutoWrapLabel help text under the control
    """
    ensure_styles_initialized()

    row = tk.Frame(parent, bg=Colors.SURFACE)
    row.pack(fill=tk.X, pady=(0, Spacing.SM))

    tk.Label(
        row,
        text=label,
        bg=Colors.SURFACE,
        fg=Colors.TEXT_PRIMARY,
        font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        anchor="w",
        justify="left",
    ).pack(fill=tk.X, anchor="w")

    field_wrap = tk.Frame(row, bg=Colors.SURFACE)
    field_wrap.pack(fill=tk.X, pady=(Spacing.XXS, 0))

    widget = widget_factory(field_wrap)
    widget.pack(fill=tk.X, expand=True)

    if help_text:
        AutoWrapLabel(
            row,
            text=help_text,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            padding_x=Spacing.SM * 2,
            min_wrap=200,
        ).pack(fill=tk.X, anchor="w", pady=(Spacing.XXS, 0))

    return row, widget
