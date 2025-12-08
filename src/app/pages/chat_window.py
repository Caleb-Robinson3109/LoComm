"""
Modern chat window with beautiful UI design.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import threading
import sys
import os

# Ensure API path is available for receive_message
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api")))
try:
    from LoCommAPI import receive_message
except Exception:
    receive_message = None
import time

# Mock bridge removed
from ui.components import DesignUtils
from ui.theme_tokens import Colors, Spacing, Typography
from ui.theme_manager import ensure_styles_initialized
from utils.design_system import AppConfig
from utils.state.status_manager import get_status_manager
from utils.state.connection_manager import get_connection_manager
from utils.window_sizing import get_chat_window_size
from utils.app_logger import get_logger


class ChatWindow(tk.Toplevel):
    """Modern chat window with beautiful UI design."""

    _open_windows: dict[str, 'ChatWindow'] = {}
    _listeners: list[Callable[[bool], None]] = []

    def __init__(
        self,
        master: tk.Misc,
        peer_name: str | None = None,
        peer_id: str | None = None,
        local_device_name: str | None = None,
        on_close_callback: Callable[[], None] | None = None,
        on_send_callback: Optional[Callable[[str], Optional[bool]]] = None,
    ):
        # Check if window already open for this peer
        if peer_name and peer_name in self._open_windows:
            existing = self._open_windows[peer_name]
            if existing.winfo_exists():
                existing.lift()
                existing.focus_set()
                return
            else:
                # Window was destroyed, remove from dict
                del self._open_windows[peer_name]

        super().__init__(master)
        ensure_styles_initialized()
        self.peer_name = peer_name or "Peer"
        self.peer_id = peer_id or ""
        self.local_device_name = local_device_name or ""
        self._on_close_callback = on_close_callback
        self._on_send_callback = on_send_callback
        self._stop_event = threading.Event()
        self._logger = get_logger("chat_window")
        self._receive_supports_timeout: bool | None = None
        self._chat_thread = threading.Thread(target=self._chat_loop, daemon=True)
        self.title("Chat")
        self._apply_default_geometry()
        self.resizable(True, True)
        self.configure(bg=Colors.SURFACE)
        self.configure(bg=Colors.SURFACE)
        # Mock bridge removed
        # self._bridge = get_peer_bridge()

        self._build_ui()
        # self._bridge.register_peer_callback(self._handle_incoming)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.entry.focus_set()

        ChatWindow._open_windows[self.peer_name] = self
        self._has_history = False
        self._chat_thread.start()
        self._notify_global_listeners()

    def _apply_default_geometry(self):
        size = get_chat_window_size()
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = min(size.width, screen_w)
        height = min(size.height, screen_h)
        width = max(width, size.min_width)
        height = max(height, size.min_height)
        pos_x = max((screen_w - width) // 2, 0)
        pos_y = max((screen_h - height) // 2, 0)
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        self.minsize(size.min_width, size.min_height)

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # Main container with modern styling
        self.main_container = tk.Frame(self, bg=Colors.SURFACE, padx=Spacing.LG, pady=Spacing.LG)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Modern header with gradient-like effect
        self.header = tk.Frame(
            self.main_container,
            bg=Colors.SURFACE_HEADER,
            padx=Spacing.LG,
            pady=Spacing.MD,
            relief="flat"
        )
        self.header.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Header content
        header_content = tk.Frame(self.header, bg=Colors.SURFACE_HEADER)
        header_content.pack(fill=tk.X)
        header_content.grid_columnconfigure(0, weight=1)
        header_content.grid_columnconfigure(1, weight=1)

        # Device ID + name
        self.header_id_label = tk.Label(
            header_content,
            text=self.peer_id,
            bg=Colors.SURFACE_HEADER,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_MONO, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
        )
        self.header_id_label.grid(row=0, column=0, sticky="w", padx=(0, Spacing.XXS))

        self.header_name_label = tk.Label(
            header_content,
            text=self.peer_name,
            bg=Colors.SURFACE_HEADER,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        )
        self.header_name_label.grid(row=0, column=1, sticky="w")

        # Chat area with modern styling
        chat_frame = tk.Frame(
            self.main_container,
            bg=Colors.SURFACE_ALT,
            relief="flat",
            bd=0,
        )
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(Spacing.SM, Spacing.SM))

        # Chat history area
        self.history_container = tk.Frame(chat_frame, bg=Colors.SURFACE_ALT)
        self.history_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.SM, pady=Spacing.SM)

        self.history_canvas = tk.Canvas(
            self.history_container,
            highlightthickness=0,
            bd=0,
            bg=Colors.SURFACE_ALT
        )
        scrollbar = tk.Scrollbar(
            self.history_container,
            orient="vertical",
            command=self.history_canvas.yview,
        )
        self.history_canvas.configure(yscrollcommand=scrollbar.set)
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_frame = tk.Frame(self.history_canvas, bg=Colors.SURFACE_ALT)
        self.history_frame.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(
                scrollregion=self.history_canvas.bbox("all")
            ),
        )
        self._history_window = self.history_canvas.create_window(
            (0, 0),
            window=self.history_frame,
            anchor="nw",
        )
        self.history_canvas.bind(
            "<Configure>",
            lambda e: self.history_canvas.itemconfig(
                self._history_window, width=e.width
            ),
        )
        from ui.helpers import enable_global_mousewheel
        enable_global_mousewheel(self.history_canvas)

        # Message composer with modern design
        composer_frame = tk.Frame(
            self.main_container,
            bg=Colors.SURFACE,
            padx=0,
            pady=Spacing.SM,
        )
        composer_frame.pack(fill=tk.X)

        # Input area
        input_frame = tk.Frame(composer_frame, bg=Colors.SURFACE_ALT, padx=Spacing.SM, pady=Spacing.SM)
        input_frame.pack(fill=tk.X)

        self.msg_var = tk.StringVar()
        self.entry = DesignUtils.create_chat_entry(input_frame, textvariable=self.msg_var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._send_message)

        self.send_btn = DesignUtils.button(
            input_frame,
            text="Send",
            command=self._send_message,
            variant="primary",
            width=4,
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

    def _apply_theme(self):
        """Apply theme colors to all components."""
        surface = Colors.SURFACE
        header_bg = Colors.SURFACE_HEADER
        accent = Colors.STATE_SUCCESS

        self.configure(bg=surface)
        self.main_container.configure(bg=surface)
        self.header.configure(bg=header_bg)
        self.header_name_label.configure(bg=header_bg, fg=Colors.TEXT_PRIMARY)
        self.connection_badge.configure(bg=header_bg, fg=accent)
        self.history_container.configure(bg=Colors.SURFACE_ALT)
        self.history_canvas.configure(bg=Colors.SURFACE_ALT)
        self.history_frame.configure(bg=Colors.SURFACE_ALT)

    # ------------------------------------------------------------------ chat rendering
    def _add_message(self, text: str, *, sender: str, is_self: bool):
        if not self._widgets_alive():
            return

        # Modern message bubble container
        bubble_container = tk.Frame(self.history_frame, bg=Colors.SURFACE_ALT)
        bubble_container.pack(fill=tk.X, expand=True, pady=Spacing.XS, padx=Spacing.SM)

        # Determine alignment and colors
        col = 1 if is_self else 0
        anchor = "e" if is_self else "w"
        name_color = Colors.TEXT_MUTED if is_self else Colors.TEXT_PRIMARY
        bubble_bg = Colors.CHAT_BUBBLE_SELF_BG if is_self else Colors.CHAT_BUBBLE_OTHER_BG
        text_color = Colors.CHAT_BUBBLE_SELF_TEXT if is_self else Colors.CHAT_BUBBLE_OTHER_TEXT
        bubble_padx = (Spacing.LG, 0) if is_self else (0, Spacing.LG)

        # Sender name
        tk.Label(
            bubble_container,
            text=sender,
            fg=name_color,
            bg=Colors.SURFACE_ALT,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_BOLD),
        ).pack(anchor=anchor, padx=bubble_padx)

        # Message bubble with modern styling
        bubble = tk.Frame(
            bubble_container,
            bg=bubble_bg,
            padx=Spacing.MD,
            pady=Spacing.SM,
            relief="flat"
        )
        bubble.pack(anchor=anchor, padx=bubble_padx)

        # Calculate wrap length for better text flow
        wrap_length = max(300, int(self.history_canvas.winfo_width() * 0.7))

        # Message text
        tk.Label(
            bubble,
            text=text,
            bg=bubble_bg,
            fg=text_color,
            justify="right" if is_self else "left",
            wraplength=wrap_length,
            font=(Typography.FONT_UI, Typography.SIZE_14),
        ).pack()

        # Timestamp
        timestamp = time.strftime("%H:%M")
        tk.Label(
            bubble_container,
            text=timestamp,
            fg=Colors.TEXT_MUTED,
            bg=Colors.SURFACE_ALT,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
        ).pack(anchor=anchor, padx=bubble_padx, pady=(Spacing.XXS, 0))

        # Auto-scroll to bottom
        self.history_canvas.update_idletasks()
        self.history_canvas.yview_moveto(1.0)

    def _handle_incoming(self, sender: str, text: str) -> None:
        if not self._widgets_alive():
            return
        sender = sender or "Peer"
        self._has_history = True
        self._add_message(text, sender=sender, is_self=False)

    def _send_message(self, _event=None):
        text = self.msg_var.get().strip()
        if not text:
            return
        if self._on_send_callback:
            try:
                result = self._on_send_callback(text)
                if result is False:
                    return
            except Exception:
                messagebox.showerror("Send Failed", "Unable to send message.", parent=self)
                return

        self._has_history = True
        self._add_message(text, sender=self.local_device_name, is_self=True)
        self.msg_var.set("")


    def _on_close(self):
        if self._has_history:
            result = messagebox.askyesno(
                "Close chat",
                "Closing this window will destroy the chat history. Continue?",
                parent=self,
            )
            if not result:
                return

        # Closing a chat should not disconnect the device; just update status
        get_status_manager().update_status("Chat closed")
        self._stop_event.set()
        if self._chat_thread and self._chat_thread.is_alive():
            self._chat_thread.join(timeout=2.0)
        if self._on_close_callback:
            try:
                self._on_close_callback()
            except Exception:
                pass
        # self._bridge.unregister_peer_callback(self._handle_incoming)
        if self.peer_name in self._open_windows and self._open_windows[self.peer_name] is self:
            del self._open_windows[self.peer_name]
        self._notify_global_listeners()
        self.destroy()

    def set_peer_name(self, name: str | None):
        self.peer_name = name or "Peer"
        if hasattr(self, "header_name_label"):
            self.header_name_label.configure(text=self.peer_name)
        self.title("Chat")

    def set_status(self, text: str, *, color: str = "#1f7a4f"):
        if hasattr(self, "connection_badge"):
            self.connection_badge.configure(text=f"● {text}", fg=color)

    # Global tracking helpers ------------------------------------------------
    @classmethod
    def register_window_listener(cls, callback: Callable[[bool], None]):
        if callback not in cls._listeners:
            cls._listeners.append(callback)
            callback(bool(cls._open_windows))

    @classmethod
    def unregister_window_listener(cls, callback: Callable[[bool], None]):
        if callback in cls._listeners:
            cls._listeners.remove(callback)

    def _notify_global_listeners(self):
        open_state = bool(self._open_windows)
        for cb in list(self._listeners):
            try:
                cb(open_state)
            except Exception:
                pass

    def _chat_loop(self):
        """Lightweight thread tied to this chat window; polls for inbound messages."""
        while not self._stop_event.is_set():
            if self._stop_event.wait(timeout=0.1):
                break

            try:
                sender, payload, senderID = self._receive_with_timeout()
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("Failed to receive message: %s", exc)
                self._stop_event.wait(timeout=0.5)
                continue

            if self._stop_event.is_set():
                break

            # Ignore message if senderID doesn't match this chat window's peer_id
            if senderID and senderID != self.peer_id:
                self._stop_event.wait(timeout=0.25)
                continue

            if sender and payload:
                self._add_message(payload, sender=sender, is_self=False)
            else:
                self._stop_event.wait(timeout=0.25)

        self._logger.info("Chat loop exited for peer %s", self.peer_name)

    def _receive_with_timeout(self, timeout: float = 1.0):
        """Call receive_message with timeout awareness to avoid blocking shutdown."""
        if receive_message is None:
            self._stop_event.wait(timeout)
            return None, None, None

        # First attempt: use native timeout parameter if available
        if self._receive_supports_timeout is not False:
            try:
                result = receive_message(timeout=timeout)
                self._receive_supports_timeout = True
                return result
            except TypeError:
                self._receive_supports_timeout = False
            except Exception:
                raise

        # Fallback: run receive_message in a worker and bound wait time
        container = {"result": (None, None)}

        def _worker():
            try:
                container["result"] = receive_message()
            except Exception as exc:  # noqa: BLE001
                container["result"] = (None, None, None)
                self._logger.warning("receive_message failed: %s", exc)

        worker = threading.Thread(target=_worker, daemon=True)
        worker.start()
        worker.join(timeout)
        if worker.is_alive():
            self._logger.warning("receive_message exceeded %.1fs; skipping result", timeout)
            return None, None, None

        result = container.get("result", (None, None, None))
        if not isinstance(result, tuple) or len(result) != 3:
            return None, None, None
        return result

    def _widgets_alive(self) -> bool:
        try:
            return bool(self.history_frame.winfo_exists())
        except Exception:
            return False
