"""
Simple UI window acting as the mock device chat interface.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import time

from mock.peer_bridge import get_peer_bridge

_WINDOW_INSTANCE = None


class MockPeerChatWindow(tk.Toplevel):
    """Modernized mock peer UI with chat bubbles."""

    def __init__(self, master: tk.Misc, peer_name: str | None = None, on_disconnect=None):
        super().__init__(master)
        self.peer_name = peer_name or "Mock Device"
        self.title(self.peer_name)
        self.configure(bg="#0f141c")
        self.geometry("460x520")
        self.minsize(420, 480)
        self.resizable(True, True)
        self._bridge = get_peer_bridge()
        self._on_disconnect = on_disconnect

        self._build_ui()
        self._bridge.register_peer_callback(self._handle_incoming)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        wrapper = tk.Frame(self, bg="#0f141c", padx=16, pady=16)
        wrapper.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(wrapper, bg="#151b24", padx=14, pady=10)
        header.pack(fill=tk.X, pady=(0, 12))
        self.connection_badge = tk.Label(
            header,
            text="Connected",
            font=("SF Pro Display", 11, "bold"),
            fg="#ffffff",
            bg="#1f7a4f",
            padx=10,
            pady=2,
        )
        self.connection_badge.pack(side=tk.LEFT)

        self.header_name_label = tk.Label(
            header,
            text=self.peer_name,
            font=("SF Pro Display", 14, "bold"),
            fg="#f5f6f8",
            bg="#151b24",
        )
        self.header_name_label.pack(side=tk.LEFT, padx=(8, 0), expand=True)
        ttk.Button(header, text="Disconnect", command=self._trigger_disconnect).pack(side=tk.RIGHT)

        # History area
        history_container = tk.Frame(wrapper, bg="#0f141c")
        history_container.pack(fill=tk.BOTH, expand=True)
        self.history_canvas = tk.Canvas(
            history_container,
            bg="#0f141c",
            highlightthickness=0,
            bd=0,
        )
        scrollbar = tk.Scrollbar(
            history_container,
            orient="vertical",
            command=self.history_canvas.yview,
        )
        self.history_canvas.configure(yscrollcommand=scrollbar.set)
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_frame = tk.Frame(self.history_canvas, bg="#0f141c")
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

        # Composer
        composer = tk.Frame(wrapper, bg="#0f141c")
        composer.pack(fill=tk.X, pady=(12, 0))
        self.msg_var = tk.StringVar()
        entry = ttk.Entry(composer, textvariable=self.msg_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.bind("<Return>", self._send_message)
        ttk.Button(composer, text="Send", command=self._send_message).pack(
            side=tk.LEFT, padx=(8, 0)
        )

    # ------------------------------------------------------------------ chat rendering
    def _add_message(self, text: str, *, sender: str, is_self: bool):
        if not self._widgets_alive():
            return
        bubble_row = tk.Frame(self.history_frame, bg="#0f141c")
        bubble_row.pack(fill=tk.X, expand=True, pady=4, padx=4)
        bubble_row.grid_columnconfigure(0, weight=1)
        bubble_row.grid_columnconfigure(1, weight=1)

        col = 1 if is_self else 0
        anchor = "e" if is_self else "w"
        name_color = "#8f9bb3" if is_self else "#f5f6f8"
        bubble_bg = "#2f7dff" if is_self else "#1d2430"
        text_color = "#ffffff" if is_self else "#e2e5ec"
        pad = (0, 32) if is_self else (32, 0)

        tk.Label(
            bubble_row,
            text=sender,
            fg=name_color,
            bg="#0f141c",
            font=("SF Pro Display", 11, "bold"),
        ).grid(row=0, column=col, sticky=anchor, padx=pad)

        bubble = tk.Frame(
            bubble_row,
            bg=bubble_bg,
            padx=12,
            pady=8,
        )
        bubble.grid(row=1, column=col, sticky=anchor, padx=pad)
        wrap_length = max(220, int(self.history_canvas.winfo_width() * 0.6))

        tk.Label(
            bubble,
            text=text,
            bg=bubble_bg,
            fg=text_color,
            justify="left" if not is_self else "right",
            wraplength=wrap_length,
            font=("SF Pro Display", 11),
        ).pack()

        timestamp = time.strftime("%H:%M")
        tk.Label(
            bubble_row,
            text=timestamp,
            fg="#556075",
            bg="#0f141c",
            font=("SF Pro Display", 9),
        ).grid(row=2, column=col, sticky=anchor, padx=pad, pady=(2, 0))

        self.history_canvas.update_idletasks()
        self.history_canvas.yview_moveto(1.0)

    def _handle_incoming(self, sender: str, text: str) -> None:
        if not self._widgets_alive():
            return
        sender = sender or "Desktop"
        self._add_message(text, sender=sender, is_self=False)

    def _send_message(self, _event=None):
        text = self.msg_var.get().strip()
        if not text:
            return
        self._bridge.send_from_peer(text)
        self._add_message(text, sender=self.peer_name, is_self=True)
        self.msg_var.set("")

    def _trigger_disconnect(self):
        if callable(self._on_disconnect):
            self._on_disconnect()
        self._on_close()

    def _on_close(self):
        self._bridge.unregister_peer_callback(self._handle_incoming)
        global _WINDOW_INSTANCE
        _WINDOW_INSTANCE = None
        self.destroy()


    def set_peer_name(self, name: str | None):
        self.peer_name = name or "Mock Device"
        if hasattr(self, "header_name_label"):
            self.header_name_label.configure(text=self.peer_name)
        self.title(self.peer_name)

    def set_status(self, text: str, *, color: str = "#1f7a4f"):
        if hasattr(self, "connection_badge"):
            self.connection_badge.configure(text=text, bg=color)

    def _widgets_alive(self) -> bool:
        try:
            return bool(self.history_frame.winfo_exists())
        except Exception:
            return False


def ensure_mock_peer_window(master: tk.Misc, peer_name: str | None = None, on_disconnect=None):
    global _WINDOW_INSTANCE
    if _WINDOW_INSTANCE and _WINDOW_INSTANCE.winfo_exists():
        if peer_name:
            _WINDOW_INSTANCE.set_peer_name(peer_name)
            _WINDOW_INSTANCE.set_status("Connected")
        if on_disconnect:
            _WINDOW_INSTANCE._on_disconnect = on_disconnect
        return _WINDOW_INSTANCE
    _WINDOW_INSTANCE = MockPeerChatWindow(master, peer_name=peer_name, on_disconnect=on_disconnect)
    _WINDOW_INSTANCE.set_status("Connected")
    return _WINDOW_INSTANCE


def close_mock_peer_window():
    global _WINDOW_INSTANCE
    if _WINDOW_INSTANCE and _WINDOW_INSTANCE.winfo_exists():
        try:
            _WINDOW_INSTANCE.destroy()
        except Exception:
            pass
    _WINDOW_INSTANCE = None
