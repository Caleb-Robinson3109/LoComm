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
        bottom.pack(fill=tk.X, padx=8, pady=(5, 10))

        # Message entry (white background, black text)
        self.msg_var = tk.StringVar()
        self.entry = tk.Entry(bottom, textvariable=self.msg_var, bg="white", fg="black")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12)
        self.entry.bind("<Return>", lambda e: self._send())

        # Send button — blue background with black text
        self.send_btn = tk.Button(bottom, text="Send", bg="light blue", fg="black", command=self._send)
        self.send_btn.pack(side=tk.LEFT, padx=6)

        # Start in a disabled state until we know the transport is ready.
        self._connected = False
        self._set_input_state(False)

    # ------------------------------------------------------ #
    def append_line(self, who: str, msg: str):
        self.history.config(state="normal")
        t = time.strftime("%H:%M:%S")
        self.history.insert("end", f"[{t}] {who}: {msg}\n")
        self.history.see("end")
        self.history.config(state="disabled")

    def _send(self):
        msg = self.msg_var.get().strip()
        if not self._connected:
            return
        if not msg:
            return
        self.append_line("Me", msg)
        self.transport.send(self.username, msg)
        self.msg_var.set("")

    def set_status(self, text: str):
        self.status_var.set(text)

        lowered = text.lower()
        if "authenticated" in lowered or "ready" in lowered:
            if not self._connected:
                self.append_line("System", "Connected to LoComm device.")
            self._connected = True
            self._set_input_state(True)
        elif "connected (mock)" in lowered:
            if not self._connected:
                self.append_line("System", "Connected (mock mode).")
            self._connected = True
            self._set_input_state(True)
        elif any(keyword in lowered for keyword in ("disconnected", "connection failed", "invalid device password", "not connected")):
            if self._connected or "connection failed" in lowered or "invalid device password" in lowered:
                self.append_line("System", text)
            self._connected = False
            self._set_input_state(False)
        elif "send failed" in lowered:
            self.append_line("System", text)
        elif "verifying" in lowered:
            self._set_input_state(False)

    def _set_input_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.entry.config(state=state)
        self.send_btn.config(state=state)
        if not enabled:
            self.msg_var.set("")
