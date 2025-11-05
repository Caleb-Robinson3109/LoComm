import tkinter as tk
from tkinter import ttk
from utils.status_manager import get_status_manager
from frames.chat_tab import ChatTab
from frames.settings_tab import SettingsTab


class MainFrame(ttk.Frame):
    def __init__(self, master, app, session, transport, on_logout):
        super().__init__(master)
        self.app = app
        self.session = session
        self.transport = transport
        self.on_logout = on_logout

        # ---------- Header with Three Boxes ---------- #
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=8)

        # ---------- Box 1: Paired Devices (Left) ---------- #
        paired_box = ttk.LabelFrame(header, text="Paired Devices", padding=10)
        paired_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self._peer_var = tk.StringVar(value="Not connected")
        ttk.Label(paired_box, text="Current Partner:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ttk.Label(paired_box, textvariable=self._peer_var, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 8))

        status_row = ttk.Frame(paired_box)
        status_row.pack(anchor="w", pady=(0, 8))
        self._status_indicator = tk.Label(status_row, text="●", fg="#d9534f", font=("Segoe UI", 12, "bold"))
        self._status_indicator.pack(side=tk.LEFT, padx=(0, 4))
        self.status_text = tk.StringVar(value="Disconnected")
        ttk.Label(status_row, textvariable=self.status_text, font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # Unpair button for other device
        ttk.Button(paired_box, text="Unpair Device", command=self._unpair_device).pack(anchor="w")

        # ---------- Box 2: Current Chat (Center) ---------- #
        chat_box = ttk.LabelFrame(header, text="Current Chat", padding=10)
        chat_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Button(chat_box, text="Clear Chat History", command=self.app.clear_chat_history, width=20).pack(pady=5)
        ttk.Separator(chat_box, orient='horizontal').pack(fill=tk.X, pady=5)
        ttk.Button(chat_box, text="Settings", command=lambda: self.show_settings_tab(), width=20).pack(pady=5)

        # ---------- Box 3: My Profile (Right) ---------- #
        profile_box = ttk.LabelFrame(header, text="My Profile", padding=10)
        profile_box.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))

        user_info = ttk.Frame(profile_box)
        user_info.pack(fill=tk.X, expand=True)

        ttk.Label(user_info, text=f"Username:", font=("Segoe UI", 9, "bold")).pack(anchor="center")
        ttk.Label(user_info, text=session.username, font=("Segoe UI", 10)).pack(anchor="center", pady=(0, 8))
        ttk.Label(user_info, text=f"Device ID:", font=("Segoe UI", 9, "bold")).pack(anchor="center")
        ttk.Label(user_info, text=session.device_id or "Not set", font=("Segoe UI", 9)).pack(anchor="center", pady=(0, 12))
        ttk.Button(user_info, text="Logout", command=self.on_logout).pack(anchor="center")

        # ---------- Tabs ---------- #
        self.notebook = ttk.Notebook(self)
        self.chat_tab = ChatTab(self.notebook, transport, session.username, on_disconnect=self.on_logout)
        self.settings_tab = SettingsTab(self.notebook, app, transport)
        self.notebook.add(self.chat_tab, text="Chat")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def show_settings_tab(self):
        if self.notebook:
            index = self.notebook.index(self.settings_tab)
            self.notebook.select(index)

    def update_status(self, text: str):
        self.status_text.set(text)
        # Use centralized status management for color determination
        status_manager = get_status_manager()
        color = status_manager.get_status_color(text)
        self._status_indicator.config(fg=color)
        self.chat_tab.set_status(text)

    def _unpair_device(self):
        """Handle unpairing with the other device."""
        # This would typically stop pairing or disconnect
        # For now, just update the peer display to show disconnection
        self.transport.stop_pairing()
        self.set_peer_name("Not connected")

    def set_peer_name(self, name: str | None):
        display = name if name else "Not connected"
        self._peer_var.set(display)
