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

        # ---------- Header ---------- #
        header = ttk.Frame(self)
        header.pack(fill=tk.X)

        info = ttk.Frame(header)
        info.pack(side=tk.LEFT, padx=10, pady=10)

        ttk.Label(info, text=f"Logged in as {session.username}").pack(anchor="w")
        ttk.Label(info, text="Paired device").pack(anchor="w", pady=(4, 0))
        self._peer_var = tk.StringVar(value="Paired with: Not connected")
        ttk.Label(info, textvariable=self._peer_var).pack(anchor="w")

        # Use tk.Button for hover color effect
        logout_btn = tk.Button(header, text="Logout", bg="lightgray", fg="black", command=on_logout)
        logout_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Hover effects
        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg="red", fg="black"))
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg="lightgray", fg="black"))

        # ---------- Tabs ---------- #
        notebook = ttk.Notebook(self)
        self.chat_tab = ChatTab(notebook, transport, session.username)
        self.settings_tab = SettingsTab(notebook, app, transport)
        notebook.add(self.chat_tab, text="Chat")
        notebook.add(self.settings_tab, text="Settings")
        notebook.pack(fill=tk.BOTH, expand=True)

    def update_status(self, text: str):
        self.chat_tab.set_status(text)

    def set_peer_name(self, name: str | None):
        display = name if name else "Not connected"
        self._peer_var.set(f"Paired with: {display}")
