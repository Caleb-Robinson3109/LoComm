import tkinter as tk
from tkinter import ttk
from frames.chat_tab import ChatTab
from frames.settings_tab import SettingsTab


class MainFrame(ttk.Frame):
    def __init__(self, master, app, session, transport, on_logout):
        super().__init__(master)
        self.app = app
        self.session = session
        self.transport = transport
        self.status_var = tk.StringVar(value="Disconnected")

        # ---------- Header ---------- #
        header = ttk.Frame(self)
        header.pack(fill=tk.X)

        info = ttk.Frame(header, style="TFrame")
        info.pack(side=tk.LEFT, padx=12, pady=12)
        self.info_frame = info

        ttk.Label(info, text=f"Logged in as {session.username}", style="Section.TLabel").pack(anchor="w")
        self.status_label = ttk.Label(info, textvariable=self.status_var, foreground="#5cb85c")
        self.status_label.pack(anchor="w", pady=(4, 0))
        self._peer_var = tk.StringVar(value="Paired with: Not connected")
        ttk.Label(info, textvariable=self._peer_var).pack(anchor="w", pady=(4, 0))

        # Use tk.Button for hover color effect
        self.logout_btn = tk.Button(header, text="Logout", relief="flat", command=on_logout, cursor="hand2")
        self.logout_btn.pack(side=tk.RIGHT, padx=12, pady=12)

        # Hover effects
        self.logout_btn.bind("<Enter>", lambda _e: self.logout_btn.config(bg="#c0392b", fg="white"))
        self.logout_btn.bind("<Leave>", lambda _e: self.logout_btn.config(bg=self._logout_bg, fg="white"))

        # ---------- Tabs ---------- #
        notebook = ttk.Notebook(self)
        self.chat_tab = ChatTab(notebook, transport, session.username, app)
        self.settings_tab = SettingsTab(notebook, app, transport)
        notebook.add(self.chat_tab, text="Chat")
        notebook.add(self.settings_tab, text="Settings")
        notebook.pack(fill=tk.BOTH, expand=True)

        self.app.register_theme_listener(self.apply_theme)
        self.apply_theme()

    def update_status(self, text: str):
        self.chat_tab.set_status(text)
        self.status_var.set(text)
        lowered = text.lower()
        if "ready" in lowered or "connected" in lowered:
            self.status_label.config(foreground="#5cb85c")
        elif "verifying" in lowered:
            self.status_label.config(foreground="#f0ad4e")
        else:
            self.status_label.config(foreground="#d9534f")

    def set_peer_name(self, name: str | None):
        display = name if name else "Not connected"
        self._peer_var.set(f"Paired with: {display}")

    def apply_theme(self):
        colors = self.app.get_theme_colors()
        self._logout_bg = colors["button_bg"]
        self.logout_btn.config(
            bg=self._logout_bg,
            fg="white",
            activebackground=self._logout_bg,
            activeforeground="white",
            font=self.app.get_font("bold"),
        )
        self.update_status(self.status_var.get())
