import tkinter as tk
from tkinter import ttk
import time
from utils.design_system import Colors, Typography, Spacing, DesignUtils
from lora_transport_locomm import LoCommTransport


class ChatTab(ttk.Frame):
    def __init__(self, master, transport: LoCommTransport, username: str, on_disconnect=None):
        super().__init__(master)
        self.master = master  # Reference to parent for communication
        self.on_disconnect = on_disconnect  # Callback for disconnect action
        self.transport = transport
        self.username = username
        self.history_buffer: list[str] = []

        # Status label with enhanced styling
        self.status_var = tk.StringVar(value="Disconnected")
        status_label = ttk.Label(self, textvariable=self.status_var,
                               font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM))
        status_label.pack(anchor="w", padx=Spacing.TAB_PADDING, pady=(Spacing.MD, Spacing.SM))

        # ---------------- Top control area (right side) ---------------- #
        top_controls = ttk.Frame(self)
        top_controls.pack(fill=tk.X, padx=Spacing.TAB_PADDING, pady=(0, Spacing.SM))

        # Empty frame to push controls to the right
        ttk.Frame(top_controls).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Control buttons area (top right corner) with modern styling
        control_buttons = ttk.Frame(top_controls)
        control_buttons.pack(side=tk.RIGHT)

        # Clear chat button with warning styling
        self.clear_btn = tk.Button(control_buttons, text="Clear Chat",
                                 bg=Colors.BTN_WARNING, fg=Colors.CHAT_TEXT_DARK,
                                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
                                 relief="flat", bd=0, command=self._clear_chat)
        self.clear_btn.pack(side=tk.TOP, padx=Spacing.XS, pady=(0, Spacing.XS))

        # Disconnect button with warning styling (matching clear button)
        self.disconnect_btn = tk.Button(control_buttons, text="Disconnect",
                                      bg=Colors.BTN_WARNING, fg=Colors.CHAT_TEXT_DARK,
                                      font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
                                      relief="flat", bd=0, command=self._disconnect_device)
        self.disconnect_btn.pack(side=tk.TOP, padx=Spacing.XS, pady=(0, Spacing.XS))

        # ---------------- Chat history area ---------------- #
        # Create a frame for the chat area with border
        chat_frame = ttk.Frame(self)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=(0, Spacing.MD))

        # Add a border frame for the chat area
        border_frame = tk.Frame(chat_frame, bg=Colors.BORDER_LIGHT, bd=1, relief="solid")
        border_frame.pack(fill=tk.BOTH, expand=True)

        self.history = tk.Text(
            border_frame,
            state="disabled",
            height=18,
            wrap="word",
            bg=Colors.CHAT_BG_DARK,
            fg=Colors.CHAT_TEXT_LIGHT,
            insertbackground=Colors.CHAT_TEXT_LIGHT,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            relief="flat",
            bd=0,
            padx=Spacing.MD,
            pady=Spacing.MD
        )
        self.history.pack(fill=tk.BOTH, expand=True)

        # Configure enhanced message styling
        self.history.tag_configure("me",
                                 justify="right",
                                 lmargin1=0,
                                 lmargin2=0,
                                 rmargin=Spacing.MD,
                                 foreground=Colors.CHAT_ME,
                                 font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_NORMAL))

        self.history.tag_configure("other",
                                 justify="left",
                                 lmargin1=Spacing.MD,
                                 lmargin2=Spacing.MD,
                                 rmargin=0,
                                 foreground=Colors.CHAT_OTHER,
                                 font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_NORMAL))

        self.history.tag_configure("system",
                                 justify="left",
                                 lmargin1=Spacing.SM,
                                 lmargin2=Spacing.SM,
                                 foreground=Colors.CHAT_SYSTEM,
                                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM))

        # ---------------- Enhanced Input row ---------------- #
        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, padx=Spacing.TAB_PADDING, pady=(Spacing.MD, Spacing.LG))

        # Input area with modern styling
        input_frame = tk.Frame(bottom, bg=Colors.BG_PRIMARY, relief="flat", bd=1)
        input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)

        # Message entry with modern styling
        self.msg_var = tk.StringVar()
        self.entry = tk.Entry(input_frame, textvariable=self.msg_var,
                            bg=Colors.CHAT_INPUT_BG, fg=Colors.CHAT_INPUT_FG,
                            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
                            relief="flat", bd=0, highlightthickness=0)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=Spacing.MD, padx=Spacing.SM)
        self.entry.bind("<Return>", lambda e: self._send())

        # Send button with primary styling (blue background, light text)
        self.send_btn = tk.Button(input_frame, text="Send",
                                bg=Colors.PRIMARY_BLUE, fg=Colors.CHAT_TEXT_LIGHT,
                                font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
                                relief="flat", bd=0, command=self._send)
        self.send_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0), pady=Spacing.XS)

        # Start in a disabled state until we know the transport is ready.
        self._connected = False
        self._set_input_state(False)

    # ------------------------------------------------------ #
    def append_line(self, who: str, msg: str):
        self.history.config(state="normal")
        t = time.strftime("%H:%M:%S")
        line = f"[{t}] {who}: {msg}"
        tag = "system"
        if who == "Me":
            tag = "me"
        elif who != "System":
            tag = "other"
        self.history.insert("end", line + "\n", tag)
        self.history.see("end")
        self.history.config(state="disabled")
        self.history_buffer.append(line)

    def _send(self):
        msg = self.msg_var.get().strip()
        if not self._connected:
            return
        if not msg:
            return
        self.append_line("Me", msg)
        self.transport.send(self.username, msg)
        self.msg_var.set("")

    def set_status(self, text: str):
        self.status_var.set(text)

        lowered = text.lower()
        if "authenticated" in lowered or "ready" in lowered:
            if not self._connected:
                self.append_line("System", "Connected to LoComm device.")
            self._connected = True
            self._set_input_state(True)
        elif "connected (mock)" in lowered:
            if not self._connected:
                self.append_line("System", "Connected (mock mode).")
            self._connected = True
            self._set_input_state(True)
        elif any(keyword in lowered for keyword in ("disconnected", "connection failed", "invalid device password", "not connected")):
            if self._connected or "connection failed" in lowered or "invalid device password" in lowered:
                self.append_line("System", text)
            self._connected = False
            self._set_input_state(False)
        elif "send failed" in lowered:
            self.append_line("System", text)
        elif "verifying" in lowered:
            self._set_input_state(False)

    def _set_input_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.entry.config(state=state)
        self.send_btn.config(state=state)
        if not enabled:
            self.msg_var.set("")

    def get_history_lines(self) -> list[str]:
        return list(self.history_buffer)

    def clear_history(self):
        self.history_buffer.clear()
        self.history.config(state="normal")
        self.history.delete("1.0", "end")
        self.history.config(state="disabled")

    def _clear_chat(self):
        """Clear the chat history."""
        self.clear_history()
        self.append_line("System", "Chat history cleared.")

    def _disconnect_device(self):
        """Handle disconnect button click - only disconnect from device, not logout."""
        # Stop the transport connection only
        self.transport.stop()
        self.append_line("System", "Disconnected from device.")

        # Update connection status
        self._connected = False
        self._set_input_state(False)
