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
        self.show_login()

    def _on_receive(self, sender: str, msg: str, ts: float):
        if isinstance(self.current_frame, MainFrame):
            display_name = sender or "Peer"
            self.current_frame.chat_tab.append_line(display_name, msg)

    def _on_status(self, text: str):
        if isinstance(self.current_frame, MainFrame):
            self.current_frame.update_status(text)


if __name__ == "__main__":
    App().mainloop()
