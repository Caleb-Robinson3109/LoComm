"""Signal-style chat experience."""
from __future__ import annotations

import tkinter as tk
import time
from services import AppController
from utils.session import Session
from utils.design_system import Colors, Typography, DesignUtils, Space


class ChatPage(tk.Frame):
    """Modern chat UI with fixed composer and scrollable history."""

    def __init__(self, master, controller: AppController, session: Session, on_disconnect=None):
        super().__init__(master, bg=Colors.SURFACE)
        self.controller = controller
        self.session = session
        self.on_disconnect = on_disconnect
        self._connected = False

        wrapper = tk.Frame(self, bg=Colors.SURFACE, padx=Space.XL, pady=Space.XL)
        wrapper.pack(fill=tk.BOTH, expand=True)

        self.shell = tk.Frame(wrapper, bg=Colors.SURFACE_ALT, highlightbackground=Colors.BORDER,
                              highlightthickness=1, bd=0)
        self.shell.pack(fill=tk.BOTH, expand=True)
        self.shell.grid_rowconfigure(1, weight=1)
        self.shell.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_history()
        self._build_composer()

        self._message_counter = 0
        self._setup_chat_history()

    # ------------------------------------------------------------------ header
    def _build_header(self):
        header = tk.Frame(self.shell, bg=Colors.SURFACE_HEADER, padx=Space.LG, pady=Space.MD)
        header.grid(row=0, column=0, sticky="ew")

        left = tk.Frame(header, bg=Colors.SURFACE_HEADER)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        contact = self.session.device_name or "Chat"
        self.name_label = tk.Label(left, text=contact, bg=Colors.SURFACE_HEADER, fg=Colors.TEXT_PRIMARY,
                                   font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD))
        self.name_label.pack(anchor="w")
        self.status_badge = DesignUtils.pill(left, "Disconnected", variant="danger")
        self.status_badge.pack(anchor="w", pady=(Space.XXS, 0))

        actions = tk.Frame(header, bg=Colors.SURFACE_HEADER)
        actions.pack(side=tk.RIGHT, anchor="e")
        DesignUtils.button(actions, text="Clear chat", variant="ghost", command=self.clear_history).pack(side=tk.LEFT, padx=(0, Space.SM))
        self.connection_btn = DesignUtils.button(actions, text="Connect", variant="secondary", command=self._handle_connection_button)
        self.connection_btn.pack(side=tk.LEFT)

    # ---------------------------------------------------------------- history area
    def _build_history(self):
        container = tk.Frame(self.shell, bg=Colors.SURFACE_ALT)
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._history_canvas = tk.Canvas(container, bg=Colors.SURFACE_ALT, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self._history_canvas.yview)
        self._history_canvas.configure(yscrollcommand=scrollbar.set)
        self._history_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.history_frame = tk.Frame(self._history_canvas, bg=Colors.SURFACE_ALT)
        self.history_frame.bind("<Configure>", lambda e: self._history_canvas.configure(scrollregion=self._history_canvas.bbox("all")))
        self._history_canvas.create_window((0, 0), window=self.history_frame, anchor="nw")
        self._history_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    # --------------------------------------------------------------- composer
    def _build_composer(self):
        composer = tk.Frame(self.shell, bg=Colors.SURFACE_RAISED, padx=Space.LG, pady=Space.SM)
        composer.grid(row=2, column=0, sticky="ew")
        composer.grid_columnconfigure(0, weight=1)

        self.msg_var = tk.StringVar()
        self.entry = DesignUtils.create_chat_entry(composer, textvariable=self.msg_var)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", self._send_message)

        DesignUtils.button(composer, text="Send", command=self._send_message).grid(row=0, column=1, padx=(Space.SM, 0))

    # ---------------------------------------------------------------- helpers
    def _setup_chat_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        self._message_counter = 0
        self._add_message("System", "Welcome to Locomm Desktop! This is a secure chat interface.", is_system=True)

    def _scroll_to_bottom(self):
        self._history_canvas.update_idletasks()
        self._history_canvas.yview_moveto(1.0)

    def _add_message(self, sender: str, message: str, is_system: bool = False):
        bubble_row = tk.Frame(self.history_frame, bg=Colors.SURFACE_ALT)
        bubble_row.pack(fill=tk.X, pady=(Space.XXS, 0), padx=Space.MD)
        bubble_row.grid_columnconfigure(0, weight=1)
        bubble_row.grid_columnconfigure(1, weight=1)

        is_self = sender in (self.session.device_name, "This Device") and not is_system
        if is_system:
            bubble_bg = Colors.MESSAGE_BUBBLE_SYSTEM_BG
            fg = Colors.TEXT_PRIMARY
        elif is_self or (not is_self and not is_system):
            bubble_bg = Colors.MESSAGE_BUBBLE_OWN_BG
            fg = Colors.SURFACE
        else:
            bubble_bg = Colors.MESSAGE_BUBBLE_OTHER_BG
            fg = Colors.TEXT_PRIMARY

        col = 1 if is_self else 0
        sticky = "e" if is_self else "w"
        bubble = tk.Frame(bubble_row, bg=bubble_bg, padx=Space.MD, pady=Space.XS)
        bubble.grid(row=0, column=col, sticky=sticky)
        tk.Label(bubble, text=sender, bg=bubble_bg, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w")
        tk.Label(bubble, text=message, bg=bubble_bg, fg=fg if not is_system else Colors.TEXT_SECONDARY,
                 wraplength=520, justify="left",
                 font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR)).pack(anchor="w", pady=(Space.XXS, 0))
        tk.Label(bubble, text=time.strftime("%H:%M"), bg=bubble_bg, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="e")

        self._scroll_to_bottom()
        if not is_system:
            self._message_counter += 1

    def _on_mousewheel(self, event):
        self._history_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ---------------------------------------------------------------- actions
    def _handle_disconnect(self):
        if self.on_disconnect:
            self.on_disconnect()

    def _handle_attach(self):
        pass  # Placeholder for future file picker

    def _handle_connection_button(self):
        if self._connected:
            self._handle_disconnect()
        else:
            if hasattr(self.master, "show_pair_page"):
                self.master.show_pair_page()

    def _send_message(self, event=None):
        if not self._connected:
            self.status_badge.configure(text="Not connected", bg=Colors.STATE_WARNING, fg=Colors.SURFACE)
            return
        message = self.msg_var.get().strip()
        if not message:
            return
        try:
            self.controller.send_message(message)
        except Exception:
            self.status_badge.configure(text="Send failed", bg=Colors.STATE_ERROR, fg=Colors.SURFACE)
            return
        self._add_message(self._get_local_device_name(), message)
        self.msg_var.set("")

    # ---------------------------------------------------------------- API hooks
    def append_line(self, sender: str, message: str):
        self._add_message(sender, message)

    def sync_session_info(self):
        contact = self.session.device_name or "Conversation"
        self.name_label.configure(text=contact)

    def set_status(self, text: str):
        lowered = text.lower()
        if "connected" in lowered:
            bg = Colors.STATE_SUCCESS
            fg = Colors.SURFACE
            self._connected = True
        elif "connecting" in lowered or "pairing" in lowered:
            bg = Colors.STATE_INFO
            fg = Colors.SURFACE
            self._connected = False
        else:
            bg = Colors.STATE_ERROR
            fg = Colors.SURFACE
            self._connected = False
        self.status_badge.configure(text=text, bg=bg, fg=fg)
        if hasattr(self, "connection_btn"):
            self.connection_btn.configure(text="Disconnect" if self._connected else "Connect")

    def clear_history(self):
        self._setup_chat_history()

    def get_history_lines(self) -> list[str]:
        lines = []
        for bubble in self.history_frame.winfo_children():
            for child in bubble.winfo_children():
                if isinstance(child, tk.Frame):
                    for inner in child.winfo_children():
                        if isinstance(inner, tk.Label):
                            lines.append(inner.cget("text"))
        return lines

    def _get_local_device_name(self) -> str:
        return getattr(self.session, "device_name", None) or "This Device"
