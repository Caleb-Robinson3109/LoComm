"""Signal-style chat experience."""
from __future__ import annotations

import tkinter as tk
import time
from typing import Callable, Optional

from utils.design_system import Colors, Typography, DesignUtils, Space, Spacing
from utils.state.status_manager import get_status_manager
from utils.state.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from ui.helpers import create_scroll_container, enable_global_mousewheel
from utils.app_logger import get_logger
from .base_page import BasePage, PageContext

logger = get_logger(__name__)

class ChatPage(BasePage):
    """Modern chat UI with fixed composer and scrollable history."""

    def __init__(self, master, context: PageContext, on_disconnect=None):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.controller = context.controller if context else None
        self.session = context.session if context else None
        self.host = context.navigator if context else None
        self.on_disconnect = on_disconnect
        self._connected = False
        self.ui_store = get_ui_store()
        self._device_subscription: Optional[Callable[[DeviceStatusSnapshot], None]] = None

        # Status manager still gates message sending
        self.status_manager = get_status_manager()

        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(0, Spacing.LG))
        body = scroll.frame

        self._build_title(body)

        self.shell = tk.Frame(
            body,
            bg=Colors.SURFACE_ALT,
            highlightbackground=Colors.BORDER,
            highlightthickness=1,
            bd=0,
        )
        self.shell.pack(fill=tk.BOTH, expand=True)
        self.shell.grid_rowconfigure(1, weight=1)
        self.shell.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_history()
        self._build_composer()

        self._message_counter = 0
        self._setup_chat_history()
        self._apply_snapshot(self.ui_store.get_device_status())

    # ------------------------------------------------------------------ title
    def _build_title(self, parent):
        """Render the page title plus description and divider."""
        title_wrap = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
        )
        title_wrap.pack(fill=tk.X, pady=(0, Space.XS))

        tk.Label(
            title_wrap,
            text="Chat",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")

        tk.Label(
            title_wrap,
            text="Secure end to end conversations.",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

    # ------------------------------------------------------------------ header
    def _build_header(self):
        header = tk.Frame(
            self.shell,
            bg=Colors.SURFACE_HEADER,
            padx=Space.LG,
            pady=Space.MD,
        )
        header.grid(row=0, column=0, sticky="ew")

        badge_width = 12
        self.connection_badge = tk.Label(
            header,
            text="Disconnected",
            bg=Colors.STATE_ERROR,
            fg=Colors.SURFACE,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_12,
                Typography.WEIGHT_BOLD,
            ),
            padx=Space.MD,
            pady=int(Space.XS / 2),
            width=badge_width,
        )
        self.connection_badge.pack(side=tk.LEFT, padx=(0, Space.SM))

        self.name_label = tk.Label(
            header,
            text="Chat",
            bg=Colors.SURFACE_HEADER,
            fg=Colors.TEXT_PRIMARY,
            font=(
                Typography.FONT_UI,
                Typography.SIZE_18,
                Typography.WEIGHT_BOLD,
            ),
        )
        self.name_label.pack(side=tk.LEFT, expand=True, padx=Space.LG)

        action_wrap = tk.Frame(header, bg=Colors.SURFACE_HEADER)
        action_wrap.pack(side=tk.RIGHT)

        # Only disconnect button remains for safety-critical action
        self.disconnect_button = DesignUtils.button(
            action_wrap,
            text="Disconnect",
            command=self._handle_disconnect,
            variant="danger",
            width=badge_width,
        )
        self.disconnect_button.pack(side=tk.RIGHT, padx=(0, Space.XL))
        self.disconnect_button.configure(state=tk.DISABLED)

    # ---------------------------------------------------------------- history area
    def _build_history(self):
        container = tk.Frame(self.shell, bg=Colors.SURFACE_ALT)
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self._history_canvas = tk.Canvas(
            container,
            bg=Colors.SURFACE_ALT,
            highlightthickness=0,
            bd=0,
        )
        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=self._history_canvas.yview,
        )
        self._history_canvas.configure(yscrollcommand=scrollbar.set)

        self._history_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Frame that will contain all message rows
        self.history_frame = tk.Frame(self._history_canvas, bg=Colors.SURFACE_ALT)

        # Keep scrollregion updated when contents change
        def _sync_scrollregion(event, canvas=self._history_canvas):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        self.history_frame.bind("<Configure>", _sync_scrollregion)

        # Embed the frame into the canvas and remember the window ID
        self._history_window = self._history_canvas.create_window(
            (0, 0),
            window=self.history_frame,
            anchor="nw",
        )

        # Ensure embedded frame always matches canvas width
        def _resize_inner(event):
            self._history_canvas.itemconfig(self._history_window, width=event.width)

        self._history_canvas.bind("<Configure>", _resize_inner)

        enable_global_mousewheel(self._history_canvas)

    # --------------------------------------------------------------- composer
    def _build_composer(self):
        composer = tk.Frame(
            self.shell,
            bg=Colors.SURFACE_RAISED,
            padx=Space.LG,
            pady=Space.SM,
        )
        composer.grid(row=2, column=0, sticky="ew")
        composer.grid_columnconfigure(0, weight=1)

        self.msg_var = tk.StringVar()
        self.entry = DesignUtils.create_chat_entry(
            composer,
            textvariable=self.msg_var,
        )
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", self._send_message)

        self.send_button = DesignUtils.button(
            composer,
            text="Send",
            command=self._send_message,
            width=10,
        )
        self.send_button.grid(row=0, column=1, padx=(Space.SM, 0))

    # ---------------------------------------------------------------- helpers
    def _setup_chat_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        self._message_counter = 0

    def _scroll_to_bottom(self):
        self._history_canvas.update_idletasks()
        self._history_canvas.yview_moveto(1.0)

    def _add_message(
        self,
        sender: str,
        message: str,
        is_system: bool = False,
        timestamp: Optional[float] = None,
    ):
        if timestamp is None:
            timestamp = time.time()
        if sender and sender.lower() == "system":
            is_system = True

        # -------- System messages: full-width bar, centered text ----------
        if is_system:
            row = tk.Frame(
                self.history_frame,
                bg=Colors.MESSAGE_BUBBLE_SYSTEM_BG,
                padx=Space.LG,
                pady=Space.XS,
            )
            row.pack(fill=tk.X, padx=Space.MD, pady=(Space.SM, Space.XXS))

            tk.Label(
                row,
                text=message,
                bg=Colors.MESSAGE_BUBBLE_SYSTEM_BG,
                fg=Colors.TEXT_SECONDARY,
                wraplength=720,
                justify="center",
                font=(
                    Typography.FONT_UI,
                    Typography.SIZE_12,
                    Typography.WEIGHT_REGULAR,
                ),
            ).pack(fill=tk.X, pady=(0, Space.XXS))

            tk.Label(
                row,
                text=time.strftime("%H:%M", time.localtime(timestamp)),
                bg=Colors.MESSAGE_BUBBLE_SYSTEM_BG,
                fg=Colors.TEXT_MUTED,
                anchor="e",
                font=(
                    Typography.FONT_UI,
                    Typography.SIZE_12,
                    Typography.WEIGHT_REGULAR,
                ),
            ).pack(fill=tk.X)

            self._history_canvas.configure(
                scrollregion=self._history_canvas.bbox("all")
            )
            self._scroll_to_bottom()
            return

        # -------- Regular messages (self / peer) --------------------------
        is_self = sender == self._get_local_device_name()

        canvas_width = self._history_canvas.winfo_width()
        if canvas_width > 1:
            wrap_length = int(canvas_width * 0.6)
        else:
            wrap_length = 340
        wrap_length = max(260, min(420, wrap_length))

        DesignUtils.create_message_bubble(
            self.history_frame,
            sender=sender,
            message=message,
            timestamp=timestamp,
            is_self=is_self,
            wraplength=wrap_length,
        )

        self._history_canvas.configure(
            scrollregion=self._history_canvas.bbox("all")
        )
        self._scroll_to_bottom()

        self._message_counter += 1

    # ---------------------------------------------------------------- actions
    def _handle_disconnect(self):
        if self.on_disconnect:
            self.on_disconnect()
        self._clear_chat_contents(confirm=False)

    def _clear_chat_contents(self, *, confirm: bool = True):
        if self.context and hasattr(self.context.app, "clear_chat_history"):
            self.context.app.clear_chat_history(confirm=confirm)
        else:
            self.clear_history()

    def _handle_attach(self):
        # Placeholder for future file picker
        pass

    def _send_message(self, event=None):
        """Send message - use consolidated status manager to check connectivity."""
        if not self.status_manager.can_send_messages() or not self._connected:
            return "break"

        message = self.msg_var.get().strip()
        if not message:
            return "break"

        if self.controller:
            try:
                self.controller.send_message(message)
            except Exception as e:
                logger.error("Send error: %s", e)
                return "break"
        else:
            logger.warning("Warning: No controller available for sending message")
            return "break"

        self._add_message(
            self._get_local_device_name(),
            message,
            timestamp=time.time(),
        )
        self.msg_var.set("")
        return "break"

    # ---------------------------------------------------------------- API hooks
    def append_line(
        self,
        sender: str,
        message: str,
        timestamp: Optional[float] = None,
        *,
        is_system: bool = False,
    ):
        self._add_message(sender, message, is_system=is_system, timestamp=timestamp)

    def sync_session_info(self):
        if self.session:
            contact = getattr(self.session, "device_name", None) or "None"
        else:
            contact = "None"
        self.name_label.configure(text=contact)

    def set_status(self, text: str):
        """Set status using the consolidated status manager for consistency."""
        self.connection_badge.configure(text=text)

    def clear_history(self):
        self._setup_chat_history()

    def get_history_lines(self) -> list[str]:
        lines = []
        for row in self.history_frame.winfo_children():
            for child in row.winfo_children():
                if isinstance(child, tk.Frame):
                    for inner in child.winfo_children():
                        if isinstance(inner, tk.Label):
                            lines.append(inner.cget("text"))
        return lines

    def _get_local_device_name(self) -> str:
        return getattr(self.session, "local_device_name", "Orion") or "Orion"

    # ------------------------------------------------------------------ lifecycle & store
    def on_show(self):
        self._subscribe_to_store()

    def on_hide(self):
        self._unsubscribe_from_store()

    def _subscribe_to_store(self):
        if self._device_subscription is not None:
            return

        def _callback(snapshot: DeviceStatusSnapshot):
            self._apply_snapshot(snapshot)

        self._device_subscription = _callback
        self.ui_store.subscribe_device_status(_callback)

    def _unsubscribe_from_store(self):
        if self._device_subscription is None:
            return
        self.ui_store.unsubscribe_device_status(self._device_subscription)
        self._device_subscription = None

    def _apply_snapshot(self, snapshot: DeviceStatusSnapshot | None):
        if not snapshot:
            return

        badge_text, badge_color = self._badge_style_for_stage(snapshot.stage)
        self.connection_badge.configure(
            text=badge_text,
            bg=badge_color,
            fg=Colors.SURFACE,
        )

        is_connected = snapshot.stage == DeviceStage.CONNECTED
        was_connected = self._connected
        self._connected = is_connected
        if was_connected and not is_connected:
            # Peer disconnected; wipe local transcript automatically.
            self._clear_chat_contents(confirm=False)

        if hasattr(self, "disconnect_button"):
            # Disconnect is available only when connected
            state = tk.NORMAL if is_connected else tk.DISABLED
            self.disconnect_button.configure(state=state)

        entry_state = tk.NORMAL if is_connected else tk.DISABLED
        self.entry.configure(state=entry_state)

        if self.send_button:
            self.send_button.configure(
                state="normal" if is_connected else "disabled"
            )

        remote_label = (
            snapshot.device_name
            if is_connected and snapshot.device_name
            else "None"
        )
        self.name_label.configure(text=remote_label)

    @staticmethod
    def _badge_style_for_stage(stage: DeviceStage) -> tuple[str, str]:
        mapping = {
            DeviceStage.READY: ("Ready", Colors.STATE_INFO),
            DeviceStage.SCANNING: ("Scanning", Colors.STATE_INFO),
            DeviceStage.AWAITING_PIN: ("Awaiting PIN", Colors.STATE_WARNING),
            DeviceStage.CONNECTING: ("Connecting", Colors.STATE_INFO),
            DeviceStage.CONNECTED: ("Connected", Colors.STATE_SUCCESS),
            DeviceStage.DISCONNECTED: ("Disconnected", Colors.STATE_ERROR),
        }
        return mapping.get(stage, mapping[DeviceStage.READY])

    def destroy(self):
        self._unsubscribe_from_store()
        return super().destroy()
