"""
Modern chat window with beautiful UI design.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
import time

from mock.peer_bridge import get_peer_bridge
from utils.design_system import Colors, ensure_styles_initialized, DesignUtils, Typography, Spacing


class ChatWindow(tk.Toplevel):
    """Modern chat window with beautiful UI design."""

    _open_windows: dict[str, 'ChatWindow'] = {}

    def __init__(self, master: tk.Misc, peer_name: str | None = None, local_device_name: str | None = None):
        # Check if window already open for this peer
        if peer_name and peer_name in self._open_windows:
            existing = self._open_windows[peer_name]
            if existing.winfo_exists():
                existing.lift()
                existing.focus_set()
                return
            else:
                # Window was destroyed, remove from dict
                del self._open_windows[peer_name]

        super().__init__(master)
        ensure_styles_initialized()
        self.peer_name = peer_name or "Peer"
        self.local_device_name = local_device_name or "Orion"
        self.title("Chat")
        self.geometry("387x465")
        self.minsize(387, 465)
        self.resizable(True, True)
        self.configure(bg=Colors.SURFACE)
        self._bridge = get_peer_bridge()

        self._build_ui()
        self._bridge.register_peer_callback(self._handle_incoming)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.entry.focus_set()

        ChatWindow._open_windows[self.peer_name] = self
        self._has_history = False

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # Main container with modern styling
        self.main_container = tk.Frame(self, bg=Colors.SURFACE, padx=Spacing.LG, pady=Spacing.LG)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Modern header with gradient-like effect
        self.header = tk.Frame(
            self.main_container,
            bg=Colors.SURFACE_HEADER,
            padx=Spacing.LG,
            pady=Spacing.MD,
            relief="flat"
        )
        self.header.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Header content
        header_content = tk.Frame(self.header, bg=Colors.SURFACE_HEADER)
        header_content.pack(fill=tk.X)
        header_content.grid_columnconfigure(0, weight=1)
        header_content.grid_columnconfigure(1, weight=0)
        header_content.grid_columnconfigure(2, weight=1)

        # Peer name with modern typography
        self.header_name_label = tk.Label(
            header_content,
            text=self.peer_name,
            bg=Colors.SURFACE_HEADER,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        )
        self.header_name_label.grid(row=0, column=0, sticky="w")

        # Connection status badge
        self.connection_badge = tk.Label(
            header_content,
            text="● Connected",
            bg=Colors.SURFACE_HEADER,
            fg=Colors.STATE_SUCCESS,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        )
        self.connection_badge.grid(row=0, column=2, sticky="e")

        # Chat area with modern styling
        chat_frame = tk.Frame(
            self.main_container,
            bg=Colors.SURFACE_ALT,
            relief="flat",
            bd=0
        )
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.MD))

        # Chat history area
        self.history_container = tk.Frame(chat_frame, bg=Colors.SURFACE_ALT)
        self.history_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=Spacing.SM)

        self.history_canvas = tk.Canvas(
            self.history_container,
            highlightthickness=0,
            bd=0,
            bg=Colors.SURFACE_ALT
        )
        scrollbar = tk.Scrollbar(
            self.history_container,
            orient="vertical",
            command=self.history_canvas.yview,
        )
        self.history_canvas.configure(yscrollcommand=scrollbar.set)
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_frame = tk.Frame(self.history_canvas, bg=Colors.SURFACE_ALT)
        self.history_frame.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(
                scrollregion=self.history_canvas.bbox("all")
            ),
        )
        self._history_window = self.history_canvas.create_window(
            (0, 0),
            window=self.history_frame,
            anchor="nw",
        )
        self.history_canvas.bind(
            "<Configure>",
            lambda e: self.history_canvas.itemconfig(
                self._history_window, width=e.width
            ),
        )

        # Message composer with modern design
        composer_frame = tk.Frame(
            self.main_container,
            bg=Colors.SURFACE,
            padx=0,
            pady=Spacing.SM
        )
        composer_frame.pack(fill=tk.X)

        # Input area
        input_frame = tk.Frame(composer_frame, bg=Colors.SURFACE_ALT, padx=Spacing.SM, pady=Spacing.MD)
        input_frame.pack(fill=tk.X)

        self.msg_var = tk.StringVar()
        self.entry = DesignUtils.create_chat_entry(input_frame, textvariable=self.msg_var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._send_message)

        self.send_btn = DesignUtils.button(
            input_frame,
            text="Send",
            command=self._send_message,
            variant="primary",
            width=10,
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

    def _apply_theme(self):
        """Apply theme colors to all components."""
        surface = Colors.SURFACE
        header_bg = Colors.SURFACE_HEADER
        accent = Colors.STATE_SUCCESS

        self.configure(bg=surface)
        self.main_container.configure(bg=surface)
        self.header.configure(bg=header_bg)
        self.header_name_label.configure(bg=header_bg, fg=Colors.TEXT_PRIMARY)
        self.connection_badge.configure(bg=header_bg, fg=accent)
        self.history_container.configure(bg=Colors.SURFACE_ALT)
        self.history_canvas.configure(bg=Colors.SURFACE_ALT)
        self.history_frame.configure(bg=Colors.SURFACE_ALT)

    # ------------------------------------------------------------------ chat rendering
    def _add_message(self, text: str, *, sender: str, is_self: bool):
        if not self._widgets_alive():
            return

        # Modern message bubble container
        bubble_container = tk.Frame(self.history_frame, bg=Colors.SURFACE_ALT)
        bubble_container.pack(fill=tk.X, expand=True, pady=Spacing.XS, padx=Spacing.SM)

        # Determine alignment and colors
        col = 1 if is_self else 0
        anchor = "e" if is_self else "w"
        name_color = Colors.TEXT_MUTED if is_self else Colors.TEXT_PRIMARY
        bubble_bg = Colors.CHAT_BUBBLE_SELF_BG if is_self else Colors.CHAT_BUBBLE_OTHER_BG
        text_color = Colors.CHAT_BUBBLE_SELF_TEXT if is_self else Colors.CHAT_BUBBLE_OTHER_TEXT
        bubble_padx = (Spacing.LG, 0) if is_self else (0, Spacing.LG)

        # Sender name
        tk.Label(
            bubble_container,
            text=sender,
            fg=name_color,
            bg=Colors.SURFACE_ALT,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_BOLD),
        ).pack(anchor=anchor, padx=bubble_padx)

        # Message bubble with modern styling
        bubble = tk.Frame(
            bubble_container,
            bg=bubble_bg,
            padx=Spacing.MD,
            pady=Spacing.SM,
            relief="flat"
        )
        bubble.pack(anchor=anchor, padx=bubble_padx)

        # Calculate wrap length for better text flow
        wrap_length = max(300, int(self.history_canvas.winfo_width() * 0.7))

        # Message text
        tk.Label(
            bubble,
            text=text,
            bg=bubble_bg,
            fg=text_color,
            justify="right" if is_self else "left",
            wraplength=wrap_length,
            font=(Typography.FONT_UI, Typography.SIZE_14),
        ).pack()

        # Timestamp
        timestamp = time.strftime("%H:%M")
        tk.Label(
            bubble_container,
            text=timestamp,
            fg=Colors.TEXT_MUTED,
            bg=Colors.SURFACE_ALT,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
        ).pack(anchor=anchor, padx=bubble_padx, pady=(Spacing.XXS, 0))

        # Auto-scroll to bottom
        self.history_canvas.update_idletasks()
        self.history_canvas.yview_moveto(1.0)

    def _handle_incoming(self, sender: str, text: str) -> None:
        if not self._widgets_alive():
            return
        sender = sender or "Peer"
        self._has_history = True
        self._add_message(text, sender=sender, is_self=False)

    def _send_message(self, _event=None):
        text = self.msg_var.get().strip()
        if not text:
            return
        self._bridge.send_from_peer(text)
        self._has_history = True
        self._add_message(text, sender=self.local_device_name, is_self=True)
        self.msg_var.set("")


    def _on_close(self):
        if self._has_history:
            result = messagebox.askyesno(
                "Close chat",
                "Closing this window will destroy the chat history. Continue?",
                parent=self,
            )
            if not result:
                return

        self._bridge.unregister_peer_callback(self._handle_incoming)
        if self.peer_name in self._open_windows and self._open_windows[self.peer_name] is self:
            del self._open_windows[self.peer_name]
        self.destroy()

    def set_peer_name(self, name: str | None):
        self.peer_name = name or "Peer"
        if hasattr(self, "header_name_label"):
            self.header_name_label.configure(text=self.peer_name)
        self.title("Chat")

    def set_status(self, text: str, *, color: str = "#1f7a4f"):
        if hasattr(self, "connection_badge"):
            self.connection_badge.configure(text=f"● {text}", fg=color)

    def _widgets_alive(self) -> bool:
        try:
            return bool(self.history_frame.winfo_exists())
        except Exception:
            return False
