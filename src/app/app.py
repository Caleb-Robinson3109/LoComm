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
        self.geometry("720x580")
        self.minsize(720, 560)

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
        self.after(100, lambda: self.eval("tk::PlaceWindow . center"))

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
                "background": "#f3f4f6",
                "surface": "#ffffff",
                "surface_alt": "#eef2ff",
                "surface_alt_hover": "#e0e7ff",
                "text": "#0f172a",
                "muted_text": "#475569",
                "chat_bg": "#f8fafc",
                "chat_fg": "#0f172a",
                "input_bg": "#ffffff",
                "input_fg": "#0f172a",
                "placeholder_fg": "#94a3b8",
                "bubble_me_bg": "#2563eb",
                "bubble_me_fg": "#ffffff",
                "bubble_other_bg": "#e2e8f0",
                "bubble_other_fg": "#1f2937",
                "system_fg": "#2563eb",
                "timestamp_fg": "#64748b",
                "border": "#d0d7e2",
                "accent": "#2563eb",
                "accent_hover": "#1d4ed8",
                "accent_text": "#ffffff",
                "danger": "#dc2626",
                "danger_hover": "#b91c1c",
                "warning": "#f59e0b",
                "button_bg": "#2563eb",
            }
        return {
            "background": "#0f172a",
            "surface": "#111c2f",
            "surface_alt": "#152238",
            "surface_alt_hover": "#1b2d49",
            "text": "#e2e8f0",
            "muted_text": "#94a3b8",
            "chat_bg": "#0b1220",
            "chat_fg": "#e2e8f0",
            "input_bg": "#152238",
            "input_fg": "#e2e8f0",
            "placeholder_fg": "#6b728c",
            "bubble_me_bg": "#2563eb",
            "bubble_me_fg": "#ffffff",
            "bubble_other_bg": "#1f2937",
            "bubble_other_fg": "#e2e8f0",
            "system_fg": "#38bdf8",
            "timestamp_fg": "#7c8aa8",
            "border": "#24344f",
            "accent": "#38bdf8",
            "accent_hover": "#0ea5e9",
            "accent_text": "#041026",
            "danger": "#f87171",
            "danger_hover": "#ef4444",
            "warning": "#fbbf24",
            "button_bg": "#38bdf8",
        }

    def _init_fonts(self):
        self._fonts: dict[str, tkfont.Font] = {
            "base": tkfont.Font(family="Segoe UI", size=self.font_size),
            "bold": tkfont.Font(family="Segoe UI", size=self.font_size, weight="bold"),
            "heading": tkfont.Font(family="Segoe UI", size=self.font_size + 4, weight="bold"),
            "status": tkfont.Font(family="Segoe UI", size=self.font_size + 1, weight="bold"),
            "system": tkfont.Font(family="Segoe UI", size=max(self.font_size - 1, 8), slant="italic"),
            "headline": tkfont.Font(family="Segoe UI Semibold", size=self.font_size + 6),
            "timestamp": tkfont.Font(family="Segoe UI", size=max(self.font_size - 2, 8)),
        }

    def _update_fonts(self):
        base = self.font_size
        self._fonts["base"].configure(size=base)
        self._fonts["bold"].configure(size=base, weight="bold")
        self._fonts["heading"].configure(size=base + 4, weight="bold")
        self._fonts["status"].configure(size=base + 1, weight="bold")
        self._fonts["system"].configure(size=max(base - 1, 8), slant="italic")
        self._fonts["headline"].configure(size=base + 6)
        self._fonts["timestamp"].configure(size=max(base - 2, 8))

    def _apply_theme(self):
        colors = self.get_theme_colors()
        self.configure(bg=colors["background"])
        self.style.theme_use("clam")
        self.style.configure("TFrame", background=colors["surface"])
        self.style.configure("Surface.TFrame", background=colors["surface"])
        self.style.configure("SurfaceAlt.TFrame", background=colors["surface_alt"])
        self.style.configure("ChatFrame.TFrame", background=colors["surface"])
        self.style.configure("TLabel", background=colors["surface"], foreground=colors["text"], font=self.get_font("base"))
        self.style.configure("Body.TLabel", background=colors["surface"], foreground=colors["muted_text"], font=self.get_font("base"))
        self.style.configure("Header.TLabel", background=colors["surface_alt"], foreground=colors["text"], font=self.get_font("heading"))
        self.style.configure("Headline.TLabel", background=colors["surface"], foreground=colors["text"], font=self.get_font("headline"))
        self.style.configure("Status.TLabel", background=colors["surface_alt"], foreground=colors["text"], font=self.get_font("status"))
        self.style.configure("Section.TLabel", background=colors["surface"], foreground=colors["text"], font=self.get_font("bold"))
        self.style.configure("HeadlineAlt.TLabel", background=colors["surface_alt"], foreground=colors["text"], font=self.get_font("headline"))
        self.style.configure("BodyAlt.TLabel", background=colors["surface_alt"], foreground=colors["muted_text"], font=self.get_font("base"))
        self.style.configure("SectionAlt.TLabel", background=colors["surface_alt"], foreground=colors["text"], font=self.get_font("bold"))
        self.style.configure("Accent.TButton",
                             background=colors["accent"],
                             foreground=colors["accent_text"],
                             padding=(16, 8),
                             relief="flat",
                             borderwidth=0,
                             focusthickness=0)
        self.style.map("Accent.TButton",
                       background=[("pressed", colors["accent_hover"]), ("active", colors["accent_hover"])],
                       foreground=[("disabled", colors["placeholder_fg"])])
        self.style.configure("Secondary.TButton",
                             background=colors["surface_alt"],
                             foreground=colors["text"],
                             padding=(14, 8),
                             relief="flat",
                             borderwidth=0)
        self.style.map("Secondary.TButton",
                       background=[("active", colors["surface_alt_hover"]), ("pressed", colors["surface_alt_hover"])],
                       foreground=[("disabled", colors["placeholder_fg"])])
        self.style.configure("Danger.TButton",
                             background=colors["danger"],
                             foreground="#ffffff",
                             padding=(16, 8),
                             relief="flat",
                             borderwidth=0)
        self.style.map("Danger.TButton",
                       background=[("active", colors["danger_hover"]), ("pressed", colors["danger_hover"])],
                       foreground=[("disabled", colors["placeholder_fg"])])
        self.style.configure("StatusBar.TFrame", background=colors["surface_alt"])
        self.style.configure("TNotebook", background=colors["surface"], borderwidth=0, padding=0)
        self.style.layout("TNotebook", [("Notebook.client", {"sticky": "nswe"})])
        self.style.configure("TNotebook.Tab",
                             padding=(16, 8),
                             background=colors["surface_alt"],
                             foreground=colors["muted_text"],
                             borderwidth=0)
        self.style.map("TNotebook.Tab",
                       background=[("selected", colors["surface"]), ("active", colors["surface_alt_hover"])],
                       foreground=[("selected", colors["text"])])
        self.style.configure("TCombobox",
                             fieldbackground=colors["input_bg"],
                             background=colors["input_bg"],
                             foreground=colors["text"])
        self.style.map("TCombobox",
                       fieldbackground=[("readonly", colors["input_bg"])])
        self.style.configure("Horizontal.TScale",
                             troughcolor=colors["surface_alt"],
                             background=colors["surface"])
        self.style.configure("TProgressbar",
                             troughcolor=colors["surface_alt"],
                             background=colors["accent"],
                             bordercolor=colors["surface_alt"])
        self.style.configure("Accent.Horizontal.TProgressbar",
                             troughcolor=colors["surface_alt"],
                             background=colors["accent"],
                             bordercolor=colors["surface_alt"])
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
