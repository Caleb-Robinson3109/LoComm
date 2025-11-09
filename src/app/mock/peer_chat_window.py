"""
Simple UI window acting as the mock device chat interface.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import time

from mock.peer_bridge import get_peer_bridge
from utils.design_system import Colors

_WINDOW_INSTANCE = None


class MockPeerChatWindow(tk.Toplevel):
    """Modernized mock peer UI with chat bubbles."""

    def __init__(self, master: tk.Misc, peer_name: str | None = None, on_disconnect=None):
        super().__init__(master)
        self.peer_name = peer_name or "Mock Device"
        self.title(self.peer_name)
        self.geometry("460x520")
        self.minsize(420, 480)
        self.resizable(True, True)
        self._bridge = get_peer_bridge()
        self._on_disconnect = on_disconnect

        self._build_ui()
        self._bridge.register_peer_callback(self._handle_incoming)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._apply_theme()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        self.wrapper = tk.Frame(self, padx=16, pady=16)
        self.wrapper.pack(fill=tk.BOTH, expand=True)

        self.header = tk.Frame(self.wrapper, padx=14, pady=10)
        self.header.pack(fill=tk.X, pady=(0, 12))
        self.connection_badge = tk.Label(
            self.header,
            text="Connected",
            font=("SF Pro Display", 11, "bold"),
            padx=10,
            pady=2,
        )
        self.connection_badge.pack(side=tk.LEFT)

        self.header_name_label = tk.Label(
            self.header,
            text=self.peer_name,
            font=("SF Pro Display", 14, "bold"),
        )
        self.header_name_label.pack(side=tk.LEFT, padx=(8, 0), expand=True)
        self.disconnect_btn = ttk.Button(self.header, text="Disconnect", command=self._trigger_disconnect)
        self.disconnect_btn.pack(side=tk.RIGHT)

        # History area
        self.history_container = tk.Frame(self.wrapper)
        self.history_container.pack(fill=tk.BOTH, expand=True)
        self.history_canvas = tk.Canvas(
            self.history_container,
            highlightthickness=0,
            bd=0,
        )
        scrollbar = tk.Scrollbar(
            self.history_container,
            orient="vertical",
            command=self.history_canvas.yview,
        )
        self.history_canvas.configure(yscrollcommand=scrollbar.set)
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_frame = tk.Frame(self.history_canvas)
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
        self.composer = tk.Frame(self.wrapper)
        self.composer.pack(fill=tk.X, pady=(12, 0))
        self.msg_var = tk.StringVar()
        self.entry = ttk.Entry(self.composer, textvariable=self.msg_var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._send_message)
        self.send_btn = ttk.Button(self.composer, text="Send", command=self._send_message)
        self.send_btn.pack(side=tk.LEFT, padx=(8, 0))

    def _apply_theme(self):
        surface = Colors.SURFACE
        header_bg = Colors.SURFACE_HEADER
        accent = Colors.STATE_SUCCESS

        self.configure(bg=surface)
        self.wrapper.configure(bg=surface)
        self.header.configure(bg=header_bg)
        self.connection_badge.configure(bg=accent, fg=Colors.SURFACE)
        self.header_name_label.configure(bg=header_bg, fg=Colors.TEXT_PRIMARY)
        self.history_container.configure(bg=surface)
        self.history_canvas.configure(bg=surface)
        self.history_frame.configure(bg=surface)
        self.composer.configure(bg=surface)

    # ------------------------------------------------------------------ chat rendering
    def _add_message(self, text: str, *, sender: str, is_self: bool):
        if not self._widgets_alive():
            return
        bubble_row = tk.Frame(self.history_frame, bg=Colors.SURFACE)
        bubble_row.pack(fill=tk.X, expand=True, pady=4, padx=4)
        bubble_row.grid_columnconfigure(0, weight=1)
        bubble_row.grid_columnconfigure(1, weight=1)

        col = 1 if is_self else 0
        anchor = "e" if is_self else "w"
        name_color = Colors.TEXT_MUTED if is_self else Colors.TEXT_PRIMARY
        bubble_bg = Colors.BUTTON_PRIMARY_BG if is_self else Colors.MESSAGE_BUBBLE_OTHER_BG
        text_color = Colors.SURFACE if is_self else Colors.TEXT_PRIMARY
        pad = (0, 32) if is_self else (32, 0)

        tk.Label(
            bubble_row,
            text=sender,
            fg=name_color,
            bg=Colors.SURFACE,
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
            fg=Colors.TEXT_MUTED,
            bg=Colors.SURFACE,
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
            _WINDOW_INSTANCE._apply_theme()
        if on_disconnect:
            _WINDOW_INSTANCE._on_disconnect = on_disconnect
        return _WINDOW_INSTANCE
    _WINDOW_INSTANCE = MockPeerChatWindow(master, peer_name=peer_name, on_disconnect=on_disconnect)
    _WINDOW_INSTANCE.set_status("Connected")
    _WINDOW_INSTANCE._apply_theme()
    return _WINDOW_INSTANCE


def close_mock_peer_window():
    global _WINDOW_INSTANCE
    if _WINDOW_INSTANCE and _WINDOW_INSTANCE.winfo_exists():
        try:
            _WINDOW_INSTANCE.destroy()
        except Exception:
            pass
    _WINDOW_INSTANCE = None


def refresh_mock_peer_window_theme():
    if _WINDOW_INSTANCE and _WINDOW_INSTANCE.winfo_exists():
        _WINDOW_INSTANCE._apply_theme()
