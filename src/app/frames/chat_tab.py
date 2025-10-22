import tkinter as tk
from tkinter import ttk
import time
from lora_transport_locomm import LoCommTransport


class ChatTab(ttk.Frame):
    def __init__(self, master, transport: LoCommTransport, username: str):
        super().__init__(master)
        self.transport = transport
        self.username = username

        # Status label
        self.status_var = tk.StringVar(value="Disconnected")
        ttk.Label(self, textvariable=self.status_var).pack(anchor="w", padx=8, pady=(8, 0))

        # ---------------- Chat history area ---------------- #
        self.history = tk.Text(
            self,
            state="disabled",
            height=20,
            wrap="word",
            bg="black",          # background color
            fg="white",          # text color
            insertbackground="white",  # caret color
        )
        self.history.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # ---------------- Input row ---------------- #
        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, padx=8, pady=(5,10))

        # Message entry (white background, black text)
        self.msg_var = tk.StringVar()
        entry = tk.Entry(bottom, textvariable=self.msg_var, bg="white", fg="black")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12)
        entry.bind("<Return>", lambda e: self._send())

        # Send button — blue background with black text
        send_btn = tk.Button(bottom, text="Send", bg="light blue", fg="black", command=self._send)
        send_btn.pack(side=tk.LEFT, padx=6)

    # ------------------------------------------------------ #
    def append_line(self, who: str, msg: str):
        self.history.config(state="normal")
        t = time.strftime("%H:%M:%S")
        self.history.insert("end", f"[{t}] {who}: {msg}\n")
        self.history.see("end")
        self.history.config(state="disabled")

    def _send(self):
        msg = self.msg_var.get().strip()
        if not msg:
            return
        self.append_line("Me", msg)
        self.transport.send(self.username, msg)
        self.msg_var.set("")

    def set_status(self, text: str):
        self.status_var.set(text)
