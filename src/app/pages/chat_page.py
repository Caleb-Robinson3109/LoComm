import tkinter as tk
from tkinter import ttk
import time
from utils.design_system import Colors, Typography, DesignUtils, Space
from services import AppController
from utils.session import Session
from utils.ui_helpers import create_scroll_container


class ChatPage(tk.Frame):
    """Chat interface with refreshed layout and info cards."""

    def __init__(self, master, controller: AppController, session: Session, on_disconnect=None):
        super().__init__(master, bg=Colors.SURFACE)
        self.master = master
        self.controller = controller
        self.session = session
        self.on_disconnect = on_disconnect
        self.history_buffer: list[str] = []
        self._connected = False
        self._message_counter = 0

        self.msg_var = tk.StringVar()
        self.pack(fill=tk.BOTH, expand=True)

        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(Space.LG, Space.LG))
        body = scroll.frame

        DesignUtils.hero_header(
            body,
            title="Live Conversations",
            subtitle="Send secure LoRa messages, monitor delivery states, and diagnose transport events.",
            actions=[{"text": "Disconnect", "command": self._handle_disconnect, "variant": "ghost"}]
        )

        self._build_info_row(body)
        self._build_messages_section(body)

    # ------------------------------------------------------------------ #
    def _build_info_row(self, parent):
        info_row = tk.Frame(parent, bg=Colors.SURFACE)
        info_row.pack(fill=tk.X, pady=(0, Space.LG))

        device_card, device_body = DesignUtils.card(info_row, "Local device", "Connection state")
        device_card.pack(side=tk.LEFT, padx=(0, Space.MD), fill=tk.BOTH, expand=True)
        self.device_name_label = tk.Label(device_body, text=self.session.device_name or "Unpaired",
                                          bg=Colors.SURFACE_ALT, fg=Colors.TEXT_PRIMARY,
                                          font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD))
        self.device_name_label.pack(anchor="w")
        self.device_id_label = tk.Label(device_body, text=self.session.device_id or "No ID",
                                        bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                                        font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR))
        self.device_id_label.pack(anchor="w")

        status_card, status_body = DesignUtils.card(info_row, "Session metrics", "Realtime delivery insights")
        status_card.pack(side=tk.LEFT, padx=(0, Space.MD), fill=tk.BOTH, expand=True)
        self.status_label = tk.Label(status_body, text="Disconnected", bg=Colors.SURFACE_ALT,
                                     fg=Colors.STATE_ERROR,
                                     font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD))
        self.status_label.pack(anchor="w")
        self.message_count_label = tk.Label(status_body, text="0 messages this session", bg=Colors.SURFACE_ALT,
                                            fg=Colors.TEXT_SECONDARY,
                                            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR))
        self.message_count_label.pack(anchor="w")

    def _build_messages_section(self, parent):
        section, body = DesignUtils.section(parent, "Conversation", "Messages are retained locally for this session.")
        # History frame
        messages_frame = tk.Frame(body, bg=Colors.SURFACE)
        messages_frame.pack(fill=tk.BOTH, expand=True)
        self.history_frame = tk.Frame(messages_frame, bg=Colors.SURFACE)
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=Space.MD, pady=(Space.SM, Space.MD))

        controls = tk.Frame(body, bg=Colors.SURFACE_ALT)
        controls.pack(fill=tk.X, pady=(Space.SM, 0))
        DesignUtils.create_styled_label(controls, "Message", style='Small.TLabel').pack(anchor="w")
        self.entry = DesignUtils.create_chat_entry(controls, textvariable=self.msg_var)
        self.entry.pack(fill=tk.X, pady=(Space.XXS, Space.XXS))
        self.entry.bind("<Return>", self._send_message)

        actions = tk.Frame(controls, bg=Colors.SURFACE_ALT)
        actions.pack(fill=tk.X, pady=(Space.XXS, 0))
        DesignUtils.button(actions, text="Send message", command=self._send_message).pack(side=tk.RIGHT)

        self._setup_chat_history()

    # ------------------------------------------------------------------ #
    def _setup_chat_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        welcome_msg = "Welcome to Locomm Desktop! This is a secure chat interface."
        self._add_message("System", welcome_msg, is_system=True)

    def _add_message(self, sender: str, message: str, is_system: bool = False):
        wrapper = tk.Frame(self.history_frame, bg=Colors.SURFACE)
        wrapper.pack(fill=tk.X, pady=(Space.XXS, 0))

        is_own_message = sender == getattr(self.session, "device_name", None) or sender == "This Device"
        bubble_bg = Colors.MESSAGE_BUBBLE_OWN_BG if is_own_message else Colors.MESSAGE_BUBBLE_OTHER_BG
        text_color = Colors.SURFACE if is_own_message else Colors.TEXT_PRIMARY

        meta = tk.Frame(wrapper, bg=Colors.SURFACE)
        meta.pack(fill=tk.X)
        tk.Label(meta, text=f"{sender}" if not is_system else sender, bg=Colors.SURFACE,
                 fg=Colors.TEXT_MUTED, font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)).pack(anchor="w")

        bubble_row = tk.Frame(wrapper, bg=Colors.SURFACE)
        bubble_row.pack(fill=tk.X)
        bubble = tk.Frame(bubble_row, bg=bubble_bg, padx=Space.MD, pady=Space.XS)
        bubble.pack(anchor="e" if is_own_message else "w", padx=(Space.LG, 0) if is_own_message else (0, Space.LG))
        tk.Label(bubble, text=message, bg=bubble_bg, wraplength=520,
                 fg=text_color, font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR), justify="left").pack(anchor="w")

        tk.Label(wrapper, text=time.strftime("%H:%M"), bg=Colors.SURFACE, fg=Colors.TEXT_MUTED,
                 font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="e" if is_own_message else "w")
        if not is_system:
            self._message_counter += 1
            self.message_count_label.configure(text=f"{self._message_counter} messages this session")

    # ------------------------------------------------------------------ #
    def _send_message(self, event=None):
        if not self._connected:
            self.status_label.configure(text="Not connected", fg=Colors.STATE_WARNING)
            return

        message = self.msg_var.get().strip()
        if not message:
            return

        try:
            self.controller.send_message(message)
        except Exception:
            self.status_label.configure(text="Send failed", fg=Colors.STATE_ERROR)
            return

        self._add_message(self._get_local_device_name(), message)
        self.msg_var.set("")
        self.entry.focus()

    # ------------------------------------------------------------------ #
    def append_line(self, sender: str, message: str):
        self._add_message(sender, message)

    def sync_session_info(self):
        self.device_name_label.configure(text=self.session.device_name or "Unpaired")
        self.device_id_label.configure(text=self.session.device_id or "No ID")

    def set_status(self, text: str):
        self.status_label.configure(text=text)
        if "connected" in text.lower():
            self._connected = True
            self.status_label.configure(fg=Colors.STATE_SUCCESS)
        else:
            self._connected = False
            self.status_label.configure(fg=Colors.STATE_ERROR)

    def clear_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        self._setup_chat_history()

    def get_history_lines(self) -> list[str]:
        lines = []
        for widget in self.history_frame.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, tk.Label) and child.cget('text'):
                    lines.append(child.cget('text'))
        return lines

    def _get_local_device_name(self) -> str:
        return getattr(self.session, "device_name", None) or "This Device"

    def _handle_disconnect(self):
        if self.on_disconnect:
            self.on_disconnect()
