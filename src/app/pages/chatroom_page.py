"""Tabbed chatroom pairing UI with join/create sections and chatroom summary."""
from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from ui.components import DesignUtils
from ui.theme_tokens import AppConfig, Colors, Spacing, Typography, Space
from ui.theme_manager import ThemeManager
from services.auth_service import get_auth_service, generate_chatroom_code
from utils.chatroom_registry import set_active_chatroom, add_member, get_active_members
from utils.state.status_manager import get_status_manager


class ChatroomPage(tk.Frame):
    """Tabbed join/create chatroom view."""

    def __init__(self, master, on_chatroom_success: Callable[[str], None]):
        super().__init__(master, bg=Colors.SURFACE)
        self.on_chatroom_success = on_chatroom_success
        self._entry_var = tk.StringVar()
        self._error_label: Optional[tk.Label] = None
        self._waiting = False
        self._current_chatroom_code: Optional[str] = None
        self._code_display: Optional[tk.Label] = None
        self._tab_buttons: dict[str, tk.Button] = {}
        self._content_frame: Optional[tk.Frame] = None
        self._join_frame: Optional[tk.Frame] = None
        self._create_frame: Optional[tk.Frame] = None
        self.entry_widget: Optional[tk.Entry] = None
        self._create_var = tk.StringVar()
        self._mode = "join"
        self._surface_widgets: list[tk.Widget] = []
        self._label_targets: list[tuple[tk.Label, str]] = []
        self._theme_listener = None
        self._track_surface(self)

        self._create_ui()
        self._theme_listener = self._apply_theme
        ThemeManager.register_theme_listener(self._theme_listener)
        self._apply_theme()

    def _create_ui(self):
        layout = tk.Frame(self, bg=Colors.SURFACE, padx=Spacing.SM, pady=Spacing.SM)
        self._track_surface(layout)
        layout.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(
            layout,
            text="Chatroom",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        )
        title_label.pack(anchor="center", pady=(0, Spacing.LG))
        self._track_label(title_label, "TEXT_PRIMARY")


        self._build_tab_strip(layout)
        self._content_frame = tk.Frame(layout, bg=Colors.SURFACE)
        self._track_surface(self._content_frame)
        self._content_frame.pack(fill=tk.BOTH, expand=True)

        self._build_join_content()
        self._build_create_content()
        self._switch_mode("join")

        self._error_label = tk.Label(
            layout,
            text="",
            bg=Colors.SURFACE,
            fg=Colors.STATE_ERROR,
            font=(Typography.FONT_UI, Typography.SIZE_10),
        )
        self._error_label.pack(fill=tk.X, pady=(Spacing.XXS, 0))
        self._track_label(self._error_label, "STATE_ERROR")


    def _build_tab_strip(self, parent: tk.Frame):
        strip = tk.Frame(parent, bg=Colors.SURFACE, pady=Spacing.SM)
        self._track_surface(strip)
        strip.pack(fill=tk.X)

        for key, label in (("join", "Join"), ("create", "Create Chatroom")):
            btn = DesignUtils.button(
                strip,
                text=label,
                variant="ghost",
                command=lambda k=key: self._switch_mode(k),
                width=16,
            )
            btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))
            self._tab_buttons[key] = btn

    def _build_join_content(self):
        frame = tk.Frame(self._content_frame, bg=Colors.SURFACE)
        self._track_surface(frame)
        frame.pack(fill=tk.BOTH, expand=True)
        self._join_frame = frame

        self.entry_widget = DesignUtils.create_chat_entry(
            frame,
            textvariable=self._entry_var,
            font=(Typography.FONT_MONO, Typography.SIZE_16, Typography.WEIGHT_BOLD),
            justify="center",
            width=20,
        )
        self.entry_widget.pack(fill=tk.X, pady=(0, Spacing.XS))
        self.entry_widget.bind("<KeyRelease>", self._on_code_key)
        self.entry_widget.bind("<Return>", self._on_submit_chatroom_code)
        self.entry_widget.focus_set()

        helper = tk.Label(
            frame,
            text="Format: ABCDE-FGHIJ-KLMNO-PQRST",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_10),
        )
        helper.pack(anchor="w", pady=(0, Spacing.XXS))
        self._track_label(helper, "TEXT_MUTED")

        actions = tk.Frame(frame, bg=Colors.SURFACE)
        self._track_surface(actions)
        actions.pack(fill=tk.X, pady=(Spacing.SM, 0))

        self.clear_btn = DesignUtils.button(
            actions,
            text="Clear",
            variant="secondary",
            width=12,
            command=self._clear_entry,
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        
        self.enter_btn = DesignUtils.button(
            actions,
            text="Enter",
            variant="primary",
            width=12,
            command=self._on_submit_chatroom_code,
        )
        self.enter_btn.pack(side=tk.RIGHT)
        self.enter_btn.configure(state="disabled")
        
        disconnect_actions = tk.Frame(frame, bg=Colors.SURFACE)
        self._track_surface(disconnect_actions)
        disconnect_actions.pack(fill=tk.X, pady=(Spacing.MD, 0))
        
        self.disconnect_btn = DesignUtils.button(
            disconnect_actions,
            text="Disconnect",
            variant="danger",
            width=12,
            command=self._disconnect_from_chatroom,
        )
        self.disconnect_btn.pack(side=tk.RIGHT)

    def _build_create_content(self):
        frame = tk.Frame(self._content_frame, bg=Colors.SURFACE)
        self._track_surface(frame)
        frame.pack(fill=tk.BOTH, expand=True)
        self._create_frame = frame

        create_entry = DesignUtils.create_chat_entry(
            frame,
            textvariable=self._create_var,
            font=(Typography.FONT_MONO, Typography.SIZE_16, Typography.WEIGHT_BOLD),
            justify="center",
            width=20,
            state="readonly",
        )
        create_entry.pack(fill=tk.X, pady=(0, Spacing.XS))
        helper2 = tk.Label(
            frame,
            text="Format: ABCDE-FGHIJ-KLMNO-PQRST",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_MUTED,
            font=(Typography.FONT_UI, Typography.SIZE_10),
        )
        helper2.pack(anchor="w", pady=(0, Spacing.XXS))
        self._track_label(helper2, "TEXT_MUTED")
        actions = tk.Frame(frame, bg=Colors.SURFACE)
        self._track_surface(actions)
        actions.pack(fill=tk.X, pady=(Spacing.SM, 0))

        self.create_btn = DesignUtils.button(
            actions,
            text="Create",
            variant="secondary",
            width=12,
            command=self._create_chatroom_code,
        )
        self.create_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        
        self.enter_btn_create = DesignUtils.button(
            actions,
            text="Enter",
            variant="primary",
            width=12,
            command=self._on_submit_create_chatroom_code,
        )
        self.enter_btn_create.pack(side=tk.RIGHT)
        self.enter_btn_create.configure(state="disabled")
        
        disconnect_actions = tk.Frame(frame, bg=Colors.SURFACE)
        self._track_surface(disconnect_actions)
        disconnect_actions.pack(fill=tk.X, pady=(Spacing.MD, 0))
        
        self.disconnect_btn_create = DesignUtils.button(
            disconnect_actions,
            text="Disconnect",
            variant="danger",
            width=12,
            command=self._disconnect_from_chatroom,
        )
        self.disconnect_btn_create.pack(side=tk.RIGHT)

    def _track_surface(self, widget: tk.Misc | None):
        if widget and widget not in self._surface_widgets:
            self._surface_widgets.append(widget)

    def _track_label(self, widget: tk.Label | None, fg_attr: str):
        if widget:
            self._label_targets.append((widget, fg_attr))

    def _apply_theme(self):
        surface = Colors.SURFACE
        for widget in list(self._surface_widgets):
            if widget and widget.winfo_exists():
                widget.configure(bg=surface)
        for label, attr in list(self._label_targets):
            if label and label.winfo_exists():
                kwargs = {"bg": surface}
                if attr and hasattr(Colors, attr):
                    kwargs["fg"] = getattr(Colors, attr)
                label.configure(**kwargs)

    def _switch_mode(self, mode: str):
        self._mode = mode
        for key, button in self._tab_buttons.items():
            button.configure(style="Locomm.Ghost.TButton")
            if key == mode:
                button.configure(style="Locomm.Primary.TButton")
        if self._join_frame and self._create_frame:
            self._join_frame.pack_forget()
            self._create_frame.pack_forget()
            if mode == "join":
                self._join_frame.pack(fill=tk.BOTH, expand=True)
            else:
                self._create_frame.pack(fill=tk.BOTH, expand=True)

    def _on_code_key(self, event):
        raw = ''.join(ch for ch in self._entry_var.get() if ch.isalnum())[:20]
        formatted = '-'.join(raw[i:i+5] for i in range(0, len(raw), 5))
        formatted = formatted.upper()
        if formatted != self._entry_var.get():
            self._entry_var.set(formatted)
        self._error_label.configure(text="")
        self.enter_btn.configure(state="normal" if len(raw) == 20 else "disabled")

    def _on_submit_chatroom_code(self, event=None):
        if self._mode != "join":
            return
        code = ''.join(ch for ch in self._entry_var.get() if ch.isalnum()).upper()
        if len(code) != 20:
            self._show_error("Please enter all 20 alphanumeric characters.")
            return
        if self._waiting:
            return
        self._set_waiting(True)
        get_status_manager().update_status("Connecting…")
        self.after(300, lambda: self._complete_success(code))

    def _complete_success(self, code: str):
        self._set_waiting(False)
        if self.on_chatroom_success:
            auth = get_auth_service()
            get_status_manager().update_status(AppConfig.STATUS_READY)
            set_active_chatroom(code, get_active_members())
            self.on_chatroom_success(code)

    def _clear_entry(self):
        self._entry_var.set("")
        self.enter_btn.configure(state="disabled")

    def focus_input(self):
        self._entry_var.set("")
        self.enter_btn.configure(state="disabled")
        self.after(50, lambda: self.entry_widget.focus_set() if self.entry_widget else None)

    def _create_chatroom_code(self):
        if self._mode != "create":
            self._switch_mode("create")
        code = generate_chatroom_code()
        formatted = self._format_code(code)
        self._current_chatroom_code = formatted
        self._create_var.set(formatted)
        if self._code_display:
            self._code_display.configure(text=formatted)
        # Enable the Enter button now that we have a chatroom code
        if hasattr(self, 'enter_btn_create') and self.enter_btn_create:
            self.enter_btn_create.configure(state="normal")
        # Don't set as active chatroom or update status until Enter is pressed

    def _disconnect_from_chatroom(self):
        # Clear any current chatroom connection
        from utils.chatroom_registry import set_active_chatroom, get_active_members
        set_active_chatroom("", get_active_members())
        get_status_manager().update_status("Disconnected")
        # Reset UI state
        self._current_chatroom_code = None
        self._create_var.set("")
        self._entry_var.set("")
        self.enter_btn.configure(state="disabled")
        if hasattr(self, 'enter_btn_create') and self.enter_btn_create:
            self.enter_btn_create.configure(state="disabled")
        if hasattr(self, 'entry_widget') and self.entry_widget:
            self.entry_widget.focus_set()

    def _on_submit_create_chatroom_code(self, event=None):
        if self._mode != "create":
            return
        if not self._current_chatroom_code:
            self._create_chatroom_code()
        if self._waiting:
            return
        if not self._current_chatroom_code:
            self._show_error("Failed to create chatroom code.")
            return
        self._set_waiting(True)
        get_status_manager().update_status("Connecting…")
        code = ''.join(ch for ch in self._current_chatroom_code if ch.isalnum())
        self.after(300, lambda: self._complete_success(code))

    def _format_code(self, code: str) -> str:
        clean = ''.join(ch for ch in code if ch.isalnum()).upper()
        return '-'.join(clean[i:i+5] for i in range(0, len(clean), 5))

    def _show_error(self, message: str):
        self._error_label.configure(text=message)
        get_status_manager().update_status(AppConfig.STATUS_CONNECTION_FAILED)
        self._set_waiting(False)

    def _set_waiting(self, waiting: bool):
        self._waiting = waiting
        state = "disabled" if waiting else "normal"
        if self.enter_btn:
            self.enter_btn.configure(state=state, text="Entering…" if waiting else "Enter Chatroom")

    def destroy(self):
        if self._theme_listener:
            ThemeManager.unregister_theme_listener(self._theme_listener)
            self._theme_listener = None
        return super().destroy()
