import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Type
from .simple_login_frame import SimpleLoginFrame


class SimpleFrameManager:
    """
    Simple frame manager for handling frame transitions.
    Provides a clean interface for frame management.
    """

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.current_frame = None

    def show_frame(self, frame_class: Type[tk.Widget], **kwargs):
        """Show a new frame."""
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = frame_class(self.parent, **kwargs)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        return self.current_frame

    def clear(self):
        """Clear the current frame."""
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
