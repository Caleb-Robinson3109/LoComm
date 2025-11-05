import tkinter as tk
from tkinter import ttk
from frames.chat_tab import ChatTab
from frames.settings_tab import SettingsTab


class MainFrame(ttk.Frame):
    def __init__(self, master, app, session, transport, on_logout):
        super().__init__(master, style="Surface.TFrame")
        self.app = app
        self.session = session
        self.transport = transport
        self.status_var = tk.StringVar(value="Disconnected")

        self.container = ttk.Frame(self, style="Surface.TFrame")
        self.container.pack(fill=tk.BOTH, expand=True, padx=32, pady=28)

        # ---------- Header ---------- #
        header = ttk.Frame(self.container, style="Surface.TFrame")
        header.pack(fill=tk.X, pady=(0, 18))

        info = ttk.Frame(header, style="Surface.TFrame")
        info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(info, text=f"Welcome, {session.username}", style="Headline.TLabel").pack(anchor="w")
        self._peer_var = tk.StringVar(value="Paired with: Not connected")
        ttk.Label(info, textvariable=self._peer_var, style="Body.TLabel").pack(anchor="w", pady=(4, 0))

        self.status_chip = tk.Label(
            info,
            textvariable=self.status_var,
            padx=14,
            pady=4,
            font=self.app.get_font("status"),
            bd=0,
            relief="flat"
        )
        self.status_chip.pack(anchor="w", pady=(10, 0))

        self.logout_btn = ttk.Button(header, text="Log out", style="Danger.TButton", command=on_logout)
        self.logout_btn.pack(side=tk.RIGHT, padx=(12, 0))

        # ---------- Tabs ---------- #
        card = ttk.Frame(self.container, style="Surface.TFrame")
        card.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(card)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.chat_tab = ChatTab(notebook, transport, session.username, app)
        self.settings_tab = SettingsTab(notebook, app, transport)
        notebook.add(self.chat_tab, text="Chat")
        notebook.add(self.settings_tab, text="Settings")

        self.app.register_theme_listener(self.apply_theme)
        self.apply_theme()

    def update_status(self, text: str):
        self.chat_tab.set_status(text)
        self.status_var.set(text)
        colors = self.app.get_theme_colors()
        lowered = text.lower()
        if "ready" in lowered or "connected" in lowered:
            bg, fg = colors["accent"], colors["accent_text"]
        elif "verifying" in lowered or "waiting" in lowered:
            bg, fg = colors["warning"], "#0f172a" if self.app.theme == "light" else colors["surface"]
        else:
            bg, fg = colors["danger"], "#ffffff"
        self.status_chip.configure(bg=bg, fg=fg)

    def set_peer_name(self, name: str | None):
        display = name if name else "Not connected"
        self._peer_var.set(f"Paired with: {display}")

    def apply_theme(self):
        self.update_status(self.status_var.get())
