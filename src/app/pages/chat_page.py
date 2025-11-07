import tkinter as tk
from tkinter import ttk
import time
from utils.design_system import Colors, Typography, Spacing, DesignUtils
from lora_transport_locomm import LoCommTransport


class ChatPage(tk.Frame):
    def __init__(self, master, transport: LoCommTransport, username: str, on_disconnect=None):
        super().__init__(master, bg=Colors.BG_PRIMARY)
        self.master = master  # Reference to parent for communication
        self.on_disconnect = on_disconnect  # Callback for disconnect action
        self.transport = transport
        self.username = username
        self.history_buffer: list[str] = []

        # Start in a disabled state until we know the transport is ready.
        self._connected = False

        # Message input variables
        self.msg_var = tk.StringVar()

        # Configure frame styling
        self.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        # Create scrollable frame for all content
        canvas = tk.Canvas(self, bg=Colors.BG_PRIMARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_PRIMARY)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_to_mousewheel)
        canvas.bind("<Leave>", _unbind_from_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------- Title Section ---------- #
        title_section = tk.Frame(scrollable_frame, bg=Colors.BG_PRIMARY)
        title_section.pack(fill=tk.X, pady=(0, Spacing.XL))

        title_frame = tk.Frame(title_section, bg=Colors.BG_PRIMARY)
        title_frame.pack(anchor="center")

        title_label = tk.Label(
            title_frame,
            text="Chat Interface",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XXL, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",
            bg=Colors.BG_PRIMARY
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Secure Device-to-Device Communication",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG),
            fg="#CCCCCC",
            bg=Colors.BG_PRIMARY
        )
        subtitle_label.pack(pady=(Spacing.SM, 0))

        # Status label with enhanced styling
        self.status_var = tk.StringVar(value="Disconnected")
        status_label = tk.Label(title_section, textvariable=self.status_var,
                               font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_MEDIUM),
                               fg="#CCCCCC", bg=Colors.BG_PRIMARY)
        status_label.pack(anchor="center", pady=(Spacing.SM, 0))

        # Enhanced device information section
        device_frame = ttk.LabelFrame(scrollable_frame, text="Device Information", style='Custom.TLabelframe')
        device_frame.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(0, Spacing.LG))

        # Device info content container
        info_frame = ttk.Frame(device_frame)
        info_frame.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, 0))

        # Your device information
        your_device_frame = ttk.Frame(info_frame)
        your_device_frame.pack(fill=tk.X, pady=(0, Spacing.MD))

        ttk.Label(your_device_frame, text="Your Device:", style='Small.TLabel').pack(anchor="w")
        self.your_device_id_label = ttk.Label(your_device_frame, text="001", style='Body.TLabel')
        self.your_device_id_label.pack(anchor="w")

        # Connected device information
        peer_device_frame = ttk.Frame(info_frame)
        peer_device_frame.pack(fill=tk.X)

        ttk.Label(peer_device_frame, text="Connected Device:", style='Small.TLabel').pack(anchor="w")
        self.peer_device_name_label = ttk.Label(peer_device_frame, text="Not connected", style='Body.TLabel')
        self.peer_device_name_label.pack(anchor="w")

        # ---------- Chat Messages Section ---------- #
        messages_frame = ttk.LabelFrame(scrollable_frame, text="Messages", style='Custom.TLabelframe')
        messages_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.HEADER_PADDING, pady=(0, Spacing.LG))

        # Messages container
        messages_container = ttk.Frame(messages_frame)
        messages_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.SECTION_MARGIN))

        # Chat history display
        self.history_frame = tk.Frame(messages_container, bg=Colors.BG_CHAT_AREA)
        self.history_frame.pack(fill=tk.BOTH, expand=True)

        # Message input section
        input_frame = ttk.Frame(messages_frame)
        input_frame.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, 0))

        # Message input
        self.msg_entry = DesignUtils.create_styled_label(input_frame, "Message:", style='Small.TLabel')
        self.msg_entry.pack(anchor="w")

        self.entry = DesignUtils.create_chat_entry(input_frame, textvariable=self.msg_var, width=50)
        self.entry.pack(fill=tk.X, pady=(Spacing.XS, Spacing.MD))
        self.entry.bind("<Return>", self._send_message)

        # Send button
        self.send_btn = DesignUtils.create_styled_button(input_frame, "Send Message", self._send_message, style='Send.TButton')
        self.send_btn.pack(anchor="e")

        # Initialize chat history
        self._setup_chat_history()

        # ---------- Connection Controls Section ---------- #
        connection_frame = ttk.LabelFrame(scrollable_frame, text="Connection Controls", style='Custom.TLabelframe')
        connection_frame.pack(fill=tk.X, padx=Spacing.HEADER_PADDING)

        # Connection controls content
        connection_content = ttk.Frame(connection_frame)
        connection_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, 0))

        # Disconnect button
        if self.on_disconnect:
            disconnect_btn = DesignUtils.create_styled_button(connection_content, "Disconnect", self.on_disconnect, style='Danger.TButton')
            disconnect_btn.pack(anchor="w")

    def _setup_chat_history(self):
        """Setup the chat history display."""
        # Clear any existing widgets
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        # Add welcome message
        welcome_msg = f"Welcome {self.username}! This is a secure chat interface."
        self._add_message("System", welcome_msg, is_system=True)

    def _add_message(self, sender: str, message: str, is_system: bool = False):
        """Add a message to the chat history."""
        message_frame = tk.Frame(self.history_frame, bg=Colors.BG_CHAT_AREA)
        message_frame.pack(fill=tk.X, padx=Spacing.SM, pady=(Spacing.XS, 0))

        # Sender name (bold for emphasis)
        sender_label = tk.Label(
            message_frame,
            text=f"{sender}: " if not is_system else "",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD),
            fg=Colors.MESSAGE_SYSTEM_TEXT if is_system else Colors.MESSAGE_OTHER_TEXT,
            bg=Colors.BG_CHAT_AREA,
            anchor="w"
        )
        sender_label.pack(anchor="w")

        # Message text
        message_label = tk.Label(
            message_frame,
            text=message,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_CHAT_AREA,
            anchor="w",
            wraplength=400,
            justify="left"
        )
        message_label.pack(anchor="w", fill=tk.X)

        # Timestamp
        timestamp_label = tk.Label(
            message_frame,
            text=time.strftime("%H:%M"),
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XS),
            fg=Colors.TEXT_TIMESTAMP,
            bg=Colors.BG_CHAT_AREA,
            anchor="e"
        )
        timestamp_label.pack(anchor="e")

    def _send_message(self, event=None):
        """Send a message through the transport."""
        if not self._connected:
            self.status_var.set("Not connected - cannot send")
            return

        message = self.msg_var.get().strip()
        if not message:
            return

        # Send via transport
        if hasattr(self.transport, 'send') and self.transport.send:
            self.transport.send(self.username, message)

        # Add to local history
        self._add_message(self.username, message)

        # Clear input
        self.msg_var.set("")
        self.entry.focus()

    def append_line(self, sender: str, message: str):
        """Append a line to the chat history (called by transport callbacks)."""
        self._add_message(sender, message)

    def set_status(self, text: str):
        """Set the status display."""
        self.status_var.set(text)
        if "connected" in text.lower():
            self._connected = True
        else:
            self._connected = False

    def clear_history(self):
        """Clear the chat history."""
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        self._setup_chat_history()

    def get_history_lines(self) -> list[str]:
        """Get all lines from the chat history for export."""
        lines = []
        for widget in self.history_frame.winfo_children():
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and child.cget('text'):
                        lines.append(child.cget('text'))
        return lines
