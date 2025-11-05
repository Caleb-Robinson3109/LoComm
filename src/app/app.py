import tkinter as tk
from tkinter import messagebox
import time
import threading

from lora_transport_locomm import LoCommTransport
from utils.session import Session
from frames.login_frame import LoginFrame
from frames.main_frame import MainFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LoRa Chat Desktop")
        self.geometry("640x520")

        self.session = Session()
        self.transport = LoCommTransport(self)
        self.transport.on_receive = self._on_receive
        self.transport.on_status = self._on_status

        self._last_status: str = "Disconnected"
        self._pending_messages: list[tuple[str, str, float]] = []
        self._current_peer: str = ""

        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self, self._handle_login)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_main(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainFrame(self, self.session, self.transport, self._handle_logout)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        if self._last_status:
            self.current_frame.update_status(self._last_status)
        self._refresh_peer_label()

        if self._pending_messages:
            for sender, msg, ts in self._pending_messages:
                display_name = sender or "Peer"
                self.current_frame.chat_tab.append_line(display_name, msg)
            self._pending_messages.clear()

    def _handle_login(self, username: str, password_bytes: bytearray):
        self.session.username = username
        self.session.password_bytes = password_bytes
        self.session.login_time = time.time()
        pw = password_bytes.decode("utf-8")

        def finish_login(success: bool):
            if success:
                self.show_main()
            else:
                messagebox.showerror("Login Failed", "Connection or password invalid.")
                self.session.clear()
                if isinstance(self.current_frame, LoginFrame):
                    self.current_frame.set_waiting(False)

        def worker():
            ok = self.transport.start(pw)
            self.after(0, lambda: finish_login(ok))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_logout(self):
        self.transport.stop()
        self.session.clear()
        self._pending_messages.clear()
        self._last_status = "Disconnected"
        self._current_peer = ""
        self.show_login()

    def _on_receive(self, sender: str, msg: str, ts: float):
        if isinstance(self.current_frame, MainFrame):
            display_name = sender or "Peer"
            self.current_frame.chat_tab.append_line(display_name, msg)
        else:
            self._pending_messages.append((sender, msg, ts))
        if sender:
            self._current_peer = sender
            self._refresh_peer_label()

    def _on_status(self, text: str):
        self._last_status = text
        lowered = text.lower()
        if any(keyword in lowered for keyword in ("disconnected", "connection failed", "invalid device password")):
            self._current_peer = ""
        elif any(keyword in lowered for keyword in ("authenticated and ready", "connected (mock)")):
            if not self._current_peer:
                self._current_peer = "Awaiting peer"
        if isinstance(self.current_frame, MainFrame):
            self.current_frame.update_status(text)
        self._refresh_peer_label()

    def _refresh_peer_label(self):
        if isinstance(self.current_frame, MainFrame):
            name = self._current_peer if self._current_peer else ("Awaiting peer" if self.transport.running else "Not connected")
            self.current_frame.set_peer_name(name if name else None)


if __name__ == "__main__":
    App().mainloop()
