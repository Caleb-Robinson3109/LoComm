import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import tkinter.font as tkfont
import time
import threading
from typing import Callable

from lora_transport_locomm import LoCommTransport
from utils.session import Session
from frames.login_frame import LoginFrame
from frames.main_frame import MainFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LoRa Chat Desktop")
        self.geometry("700x560")

        self.session = Session()
        self.transport = LoCommTransport(self)
        self.transport.on_receive = self._on_receive
        self.transport.on_status = self._on_status

        self._last_status: str = "Disconnected"
        self._pending_messages: list[tuple[str, str, float]] = []
        self._current_peer: str = ""

        self.style = ttk.Style()
        self.theme = "dark"
        self.font_size = 12
        self._theme_listeners: list[Callable[[], None]] = []
        self._init_fonts()
        self._apply_theme()

        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self, self._handle_login, self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_main(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainFrame(self, self, self.session, self.transport, self._handle_logout)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        if self._last_status:
            self.current_frame.update_status(self._last_status)
        self._refresh_peer_label()

        if self._pending_messages:
            for sender, msg, ts in self._pending_messages:
                display_name = sender or "Peer"
                self.current_frame.chat_tab.append_line(display_name, msg)
                if sender:
                    self._current_peer = sender
            self._pending_messages.clear()
            self._refresh_peer_label()

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
        if sender and sender != self.session.username:
            self.notify_incoming_message(sender, msg)

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

    # ---------------- Theme & Accessibility ---------------- #
    def register_theme_listener(self, callback: Callable[[], None]):
        self._theme_listeners.append(callback)
        callback()

    def set_theme(self, theme: str):
        if theme not in ("dark", "light"):
            return
        self.theme = theme
        self._apply_theme()

    def toggle_theme(self):
        self.set_theme("light" if self.theme == "dark" else "dark")

    def set_font_size(self, size: int):
        self.font_size = max(10, min(18, size))
        self._update_fonts()
        self._apply_theme()

    def get_font(self, role: str = "base"):
        return self._fonts.get(role, self._fonts["base"])

    def get_theme_colors(self) -> dict[str, str]:
        if self.theme == "light":
            return {
                "background": "#f5f5f5",
                "surface": "#ffffff",
                "text": "#1f1f1f",
                "chat_bg": "#ffffff",
                "chat_fg": "#111111",
                "input_bg": "#ffffff",
                "input_fg": "#111111",
                "placeholder_fg": "#7f7f7f",
                "bubble_me_bg": "#d1f5d3",
                "bubble_me_fg": "#1f441e",
                "bubble_other_bg": "#e4e7ff",
                "bubble_other_fg": "#1e255b",
                "system_fg": "#3a7bd5",
                "button_bg": "#3a7bd5",
            }
        return {
            "background": "#161b22",
            "surface": "#1f2530",
            "text": "#e6edf3",
            "chat_bg": "#0d1117",
            "chat_fg": "#e6edf3",
            "input_bg": "#1f2530",
            "input_fg": "#e6edf3",
            "placeholder_fg": "#6c7683",
            "bubble_me_bg": "#214d2e",
            "bubble_me_fg": "#b9f2c0",
            "bubble_other_bg": "#2b3a67",
            "bubble_other_fg": "#d0dcff",
            "system_fg": "#62b0ff",
            "button_bg": "#238636",
        }

    def _init_fonts(self):
        self._fonts: dict[str, tkfont.Font] = {
            "base": tkfont.Font(family="Segoe UI", size=self.font_size),
            "bold": tkfont.Font(family="Segoe UI", size=self.font_size, weight="bold"),
            "heading": tkfont.Font(family="Segoe UI", size=self.font_size + 4, weight="bold"),
            "status": tkfont.Font(family="Segoe UI", size=self.font_size + 1, weight="bold"),
            "system": tkfont.Font(family="Segoe UI", size=max(self.font_size - 1, 8), slant="italic"),
        }

    def _update_fonts(self):
        base = self.font_size
        self._fonts["base"].configure(size=base)
        self._fonts["bold"].configure(size=base, weight="bold")
        self._fonts["heading"].configure(size=base + 4, weight="bold")
        self._fonts["status"].configure(size=base + 1, weight="bold")
        self._fonts["system"].configure(size=max(base - 1, 8), slant="italic")

    def _apply_theme(self):
        colors = self.get_theme_colors()
        self.configure(bg=colors["background"])
        self.style.theme_use("clam")
        self.style.configure("TFrame", background=colors["surface"])
        self.style.configure("ChatFrame.TFrame", background=colors["surface"])
        self.style.configure("TLabel", background=colors["surface"], foreground=colors["text"], font=self.get_font("base"))
        self.style.configure("TButton", font=self.get_font("base"))
        self.style.configure("Header.TLabel", background=colors["surface"], foreground=colors["text"], font=self.get_font("heading"))
        self.style.configure("Status.TLabel", background=colors["surface"], foreground=colors["text"], font=self.get_font("status"))
        self.style.configure("Section.TLabel", background=colors["surface"], foreground=colors["text"], font=self.get_font("bold"))
        self.style.configure("TNotebook", background=colors["surface"])
        self.style.configure("TNotebook.Tab", padding=(12, 6))
        self.style.map("TNotebook.Tab", background=[("selected", colors["background"])])
        stale: list[Callable[[], None]] = []
        for callback in self._theme_listeners:
            try:
                callback()
            except tk.TclError:
                stale.append(callback)
        for callback in stale:
            if callback in self._theme_listeners:
                self._theme_listeners.remove(callback)

    # ---------------- Notifications & History ---------------- #
    def notify_incoming_message(self, sender: str, msg: str):
        self.bell()
        if isinstance(self.current_frame, MainFrame):
            self.current_frame.chat_tab.status_var.set(f"Message from {sender}")
            self.after(2000, lambda: self.current_frame.update_status(self._last_status))

    def export_chat_history(self):
        if not isinstance(self.current_frame, MainFrame):
            messagebox.showinfo("Export History", "Open the chat screen to export history.")
            return
        lines = self.current_frame.chat_tab.get_history_lines()
        if not lines:
            messagebox.showinfo("Export History", "No messages to export yet.")
            return
        default_name = f"locomm_chat_{self.session.username or 'session'}.txt"
        path = filedialog.asksaveasfilename(
            title="Save chat history",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines))
            messagebox.showinfo("Export History", f"Saved chat history to {path}")
        except OSError as exc:
            messagebox.showerror("Export Failed", f"Could not save chat history:\n{exc}")


if __name__ == "__main__":
    App().mainloop()
