"""
Simple UI window acting as the mock device chat interface.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from mock.peer_bridge import get_peer_bridge

_WINDOW_INSTANCE = None


class MockPeerChatWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc):
        super().__init__(master)
        self.title("Mock Device Chat")
        self.configure(bg="#1f242c")
        self.geometry("400x500")
        self.resizable(True, True)
        self._bridge = get_peer_bridge()

        self.log = tk.Text(self, bg="#151920", fg="#f4f4f5", wrap="word", state="disabled")
        self.log.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))

        composer = tk.Frame(self, bg="#1f242c")
        composer.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.msg_var = tk.StringVar()
        entry = ttk.Entry(composer, textvariable=self.msg_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.bind("<Return>", self._send_message)
        ttk.Button(composer, text="Send", command=self._send_message).pack(side=tk.LEFT, padx=(6, 0))

        self._bridge.register_peer_callback(self._handle_incoming)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _handle_incoming(self, sender: str, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert(tk.END, f"{sender}: {text}\n")
        self.log.configure(state="disabled")
        self.log.see(tk.END)

    def _send_message(self, _event=None):
        text = self.msg_var.get().strip()
        if not text:
            return
        self._bridge.send_from_peer(text)
        self._handle_incoming("Mock Device", text)
        self.msg_var.set("")

    def _on_close(self):
        self._bridge.unregister_peer_callback(self._handle_incoming)
        global _WINDOW_INSTANCE
        _WINDOW_INSTANCE = None
        self.destroy()


def ensure_mock_peer_window(master: tk.Misc):
    global _WINDOW_INSTANCE
    if _WINDOW_INSTANCE and _WINDOW_INSTANCE.winfo_exists():
        return _WINDOW_INSTANCE
    _WINDOW_INSTANCE = MockPeerChatWindow(master)
    return _WINDOW_INSTANCE
