import tkinter as tk
from tkinter import ttk

class SettingsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="Settings", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        ttk.Label(self, text="(Future LoRa configuration options here)").pack(anchor="w", padx=15, pady=5)
