import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from utils.chat_history_manager import get_chat_history_manager


class SettingsTab(ttk.Frame):
    def __init__(self, master, app, transport):
        super().__init__(master)
        self.app = app
        self.transport = transport

        ttk.Label(self, text="Device Controls", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(14, 6))
        device_frame = ttk.Frame(self)
        device_frame.pack(fill=tk.X, padx=14)

        ttk.Button(device_frame, text="Pair Devices", command=self._pair_devices).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(device_frame, text="Stop Pairing", command=self._stop_pair).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(device_frame, text="Reset Device Password", command=self._reset_password).grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(device_frame, text="Set New Password", command=self._set_password).grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(device_frame, text="Delete Keys", command=self._delete_keys).grid(row=2, column=0, padx=4, pady=4, sticky="ew")

        for i in range(2):
            device_frame.columnconfigure(i, weight=1)

        ttk.Separator(self).pack(fill=tk.X, padx=14, pady=12)

        ttk.Label(self, text="History & Notifications", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(0, 6))
        history_frame = ttk.Frame(self)
        history_frame.pack(fill=tk.X, padx=14)

        ttk.Button(history_frame, text="Clear Chat History", command=self._clear_history).grid(row=0, column=0, sticky="ew", padx=4, pady=4)

        history_frame.columnconfigure(0, weight=1)

        ttk.Label(self, text="Enable system chime on new messages from peers.").pack(anchor="w", padx=18, pady=(4, 0))

    def _require_connection(self) -> bool:
        if not self.transport.running:
            messagebox.showinfo("Device Action", "Connect to a LoComm device before using this action.")
            return False
        return True

    def _pair_devices(self):
        if not self._require_connection():
            return
        ok = self.transport.pair_devices()
        message = "Pairing initiated." if ok else "Pairing could not be started."
        messagebox.showinfo("Pair Devices", message)

    def _stop_pair(self):
        if not self._require_connection():
            return
        ok = self.transport.stop_pairing()
        message = "Pairing stopped." if ok else "Device did not respond."
        messagebox.showinfo("Stop Pairing", message)

    def _reset_password(self):
        if not self._require_connection():
            return
        new_pw = simpledialog.askstring("Reset Device Password", "Enter new password:", show="•")
        if not new_pw:
            return
        ok = self.transport.reset_device_password(new_pw)
        messagebox.showinfo("Reset Password", "Password reset successful." if ok else "Password reset failed.")

    def _set_password(self):
        if not self._require_connection():
            return
        old = simpledialog.askstring("Set New Password", "Current password:", show="•")
        if not old:
            return
        new = simpledialog.askstring("Set New Password", "New password:", show="•")
        if not new:
            return
        ok = self.transport.set_device_password(old, new)
        messagebox.showinfo("Set Password", "Password updated." if ok else "Password update failed.")

    def _delete_keys(self):
        if not self._require_connection():
            return
        if not messagebox.askyesno("Delete Keys", "Delete all keys on the device? This cannot be undone.", icon="warning"):
            return
        ok = self.transport.delete_device_keys()
        messagebox.showinfo("Delete Keys", "Keys deleted." if ok else "Key deletion failed.")

    def _clear_history(self):
        """Clear chat history using centralized manager"""
        chat_history_manager = get_chat_history_manager()
        if hasattr(self.app.current_frame, "chat_tab"):
            chat_history_manager.clear_chat_history(self.app.current_frame.chat_tab, self)
        else:
            messagebox.showinfo("Clear Chat", "Open the chat screen to clear history.")
