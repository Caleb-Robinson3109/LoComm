import tkinter as tk
from tkinter import ttk
import time
from lora_transport_locomm import LoCommTransport


class ChatTab(ttk.Frame):
    def __init__(self, master, transport: LoCommTransport, username: str, app):
        super().__init__(master, style="ChatFrame.TFrame")
        self.transport = transport
        self.username = username
        self.app = app
        self.history_buffer: list[str] = []

        # Status banner
        self.status_var = tk.StringVar(value="Disconnected")
        status_frame = ttk.Frame(self, style="StatusBar.TFrame")
        status_frame.pack(fill=tk.X, padx=16, pady=(16, 10))
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)

        # ---------------- Chat history area ---------------- #
        self.history = tk.Text(
            self,
            state="disabled",
            height=18,
            wrap="word",
            borderwidth=0,
            relief="flat",
            padx=12,
            pady=12,
        )
        self.history.pack(fill=tk.BOTH, expand=True, padx=16, pady=6)

        self.history.tag_configure(
            "me",
            justify="right",
            lmargin1=120,
            lmargin2=120,
            rmargin=16,
            spacing1=6,
            spacing3=6,
        )
        self.history.tag_configure(
            "me_meta",
            justify="right",
            lmargin1=120,
            lmargin2=120,
            rmargin=16,
            spacing1=0,
            spacing3=10,
        )
        self.history.tag_configure(
            "other",
            justify="left",
            lmargin1=16,
            lmargin2=16,
            rmargin=120,
            spacing1=6,
            spacing3=6,
        )
        self.history.tag_configure(
            "other_meta",
            justify="left",
            lmargin1=16,
            lmargin2=16,
            rmargin=120,
            spacing1=0,
            spacing3=10,
        )
        self.history.tag_configure(
            "system",
            justify="center",
            spacing1=4,
            spacing3=4,
        )
        self.history.tag_configure(
            "system_meta",
            justify="center",
            spacing1=0,
            spacing3=10,
        )

        # ---------------- Input row ---------------- #
        bottom = ttk.Frame(self, style="ChatFrame.TFrame")
        bottom.pack(fill=tk.X, padx=16, pady=(8, 18))

        self.msg_var = tk.StringVar()
        self.msg_var.trace_add("write", lambda *_: self._on_text_change())
        self.placeholder = "Type a message..."
        self.placeholder_active = False

        self.entry = tk.Entry(bottom, textvariable=self.msg_var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 12))
        self.entry.bind("<Return>", lambda e: self._send())
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)

        self.send_btn = ttk.Button(bottom, text="Send", style="Accent.TButton", command=self._send)
        self.send_btn.pack(side=tk.LEFT)

        # Start in a disabled state until we know the transport is ready.
        self._connected = False
        self._set_input_state(False)
        self._restore_placeholder()

        self.app.register_theme_listener(self.apply_theme)

    # ------------------------------------------------------ #
    def append_line(self, who: str, msg: str):
        timestamp = time.strftime("%H:%M:%S")
        snapshot = f"[{timestamp}] {who}: {msg}"
        self.history_buffer.append(snapshot)

        self.history.config(state="normal")
        tag = "system"
        if who == "Me":
            tag = "me"
        elif who != "System":
            tag = "other"

        if tag == "system":
            self.history.insert("end", msg + "\n", "system")
            self.history.insert("end", f"{timestamp}\n", "system_meta")
        else:
            self.history.insert("end", msg + "\n", tag)
            meta_tag = "me_meta" if tag == "me" else "other_meta"
            self.history.insert("end", f"{timestamp}\n", meta_tag)

        self.history.see("end")
        self.history.config(state="disabled")

    def get_history_lines(self) -> list[str]:
        return list(self.history_buffer)

    def clear_history(self):
        self.history_buffer.clear()
        self.history.config(state="normal")
        self.history.delete("1.0", "end")
        self.history.config(state="disabled")

    def _send(self):
        if not self._connected:
            return
        msg = self.msg_var.get().strip()
        if not msg:
            return
        self.append_line("Me", msg)
        self.transport.send(self.username, msg)
        self.msg_var.set("")
        self._restore_placeholder()

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
        self._apply_status_color(lowered)

    def apply_theme(self):
        colors = self.app.get_theme_colors()
        self.configure(style="ChatFrame.TFrame")
        base_font = self.app.get_font("base")
        timestamp_font = self.app.get_font("timestamp")
        self.history.configure(
            bg=colors["chat_bg"],
            fg=colors["chat_fg"],
            insertbackground=colors["chat_fg"],
            font=base_font,
            highlightthickness=1,
            highlightbackground=colors["border"]
        )
        self.entry.configure(
            bg=colors["input_bg"],
            fg=colors["input_fg"],
            insertbackground=colors["input_fg"],
            font=base_font,
            highlightthickness=1,
            highlightbackground=colors["border"],
            highlightcolor=colors["accent"],
            relief="flat",
            bd=0
        )
        self.history.tag_configure("me", background=colors["bubble_me_bg"], foreground=colors["bubble_me_fg"])
        self.history.tag_configure("me_meta", foreground=colors["timestamp_fg"], font=timestamp_font)
        self.history.tag_configure("other", background=colors["bubble_other_bg"], foreground=colors["bubble_other_fg"])
        self.history.tag_configure("other_meta", foreground=colors["timestamp_fg"], font=timestamp_font)
        self.history.tag_configure("system", foreground=colors["system_fg"], font=self.app.get_font("system"))
        self.history.tag_configure("system_meta", foreground=colors["timestamp_fg"], font=timestamp_font)
        self.status_label.configure(font=self.app.get_font("status"))
        self._apply_status_color(self.status_var.get().lower())

        if self.placeholder_active:
            self.entry.configure(fg=colors["placeholder_fg"])

    def _apply_status_color(self, lowered: str):
        colors = self.app.get_theme_colors()
        if "authenticated" in lowered or "ready" in lowered or "connected" in lowered:
            color = colors["accent"]
        elif "disconnected" in lowered or "failed" in lowered or "invalid" in lowered:
            color = colors["danger"]
        elif "verifying" in lowered or "waiting" in lowered:
            color = colors["warning"]
        else:
            color = colors["accent"]
        self.status_label.configure(foreground=color)

    def _set_input_state(self, enabled: bool):
        if enabled:
            self.entry.config(state="normal")
            if not self.msg_var.get().strip():
                self._restore_placeholder()
            self.send_btn.state(("disabled",))
            self._on_text_change()
        else:
            self.entry.config(state="normal")
            self.msg_var.set("")
            self._restore_placeholder()
            self.entry.config(state="disabled")
            self.send_btn.state(("disabled",))

    def _on_text_change(self):
        if self.placeholder_active:
            self.send_btn.state(("disabled",))
            return
        msg = self.msg_var.get().strip()
        if msg and self._connected:
            self.send_btn.state(("!disabled",))
        else:
            self.send_btn.state(("disabled",))

    def _clear_placeholder(self, _event=None):
        if self.placeholder_active:
            self.placeholder_active = False
            self.msg_var.set("")
            colors = self.app.get_theme_colors()
            self.entry.configure(fg=colors["input_fg"])

    def _restore_placeholder(self, _event=None):
        if self.msg_var.get().strip():
            self.placeholder_active = False
            return
        self.placeholder_active = True
        self.send_btn.state(("disabled",))
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        colors = self.app.get_theme_colors()
        self.entry.configure(fg=colors["placeholder_fg"])
