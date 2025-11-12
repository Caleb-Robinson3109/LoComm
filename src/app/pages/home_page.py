"""Home page matching chat page's clean, simple design."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, DesignUtils, Spacing, Typography, Space
from ui.helpers import create_scroll_container
from mock.device_service import get_mock_device_service
from .base_page import BasePage, PageContext
from .chat_window import ChatWindow


class HomePage(BasePage):
    """Home page with chat-style clean, simple design."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.session = context.session if context else None
        self.host = context.navigator if context else None
        self.device_service = get_mock_device_service()
        # Simple scroll container like chat page
        scroll = create_scroll_container(
            self,
            bg=Colors.SURFACE,
            padding=(0, Spacing.LG)
        )
        body = scroll.frame

        self._build_title(body)
        self._build_devices_section(body)

    def _build_title(self, parent):
        """Build simple title section like chat page."""
        title_wrap = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Spacing.SM,
        )
        title_wrap.pack(fill=tk.X, pady=(0, Space.XS))

        text_wrap = tk.Frame(title_wrap, bg=Colors.SURFACE)
        text_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True)

        action_wrap = tk.Frame(title_wrap, bg=Colors.SURFACE)
        action_wrap.pack(side=tk.RIGHT)

        tk.Label(
            text_wrap,
            text="Welcome to Locomm",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        ).pack(anchor="w")

        tk.Label(
            text_wrap,
            text="Secure LoRa messaging for desktop",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(Space.XXS, 0))

        DesignUtils.button(
            action_wrap,
            text="Enter Chatroom",
            command=self._go_to_chatroom,
            variant="primary",
        ).pack()

        separator = tk.Frame(parent, bg=Colors.DIVIDER, height=1)
        separator.pack(fill=tk.X, pady=(0, Space.SM))

    def _build_devices_section(self, parent):
        """Build devices section with chat buttons."""
        content = tk.Frame(
            parent,
            bg=Colors.SURFACE,
            padx=Space.LG,
            pady=Space.MD,
        )
        content.pack(fill=tk.BOTH, expand=True)

        # Section title
        tk.Label(
            content,
            text="Incoming Peers",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
        ).pack(anchor="w", pady=(0, Spacing.SM))

        # Device list
        list_frame = tk.Frame(content, bg=Colors.SURFACE_ALT, padx=Space.MD, pady=Space.MD)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self._build_device_list(list_frame)

    def _build_device_list(self, parent):
        """Build list of devices with chat buttons."""
        devices = self.device_service.list_devices()
        if not devices:
            tk.Label(
                parent,
                text="No devices available",
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_SECONDARY,
                font=(Typography.FONT_UI, Typography.SIZE_12),
            ).pack(pady=Space.MD)
            return

        for device in devices:
            device_frame = tk.Frame(parent, bg=Colors.SURFACE_ALT, pady=Space.XS)
            device_frame.pack(fill=tk.X)

            # Device name
            tk.Label(
                device_frame,
                text=device.name,
                bg=Colors.SURFACE_ALT,
                fg=Colors.TEXT_PRIMARY,
                font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_BOLD),
                anchor="w",
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Chat button
            DesignUtils.button(
                device_frame,
                text="Chat",
                command=lambda d=device: self._open_chat(d),
                variant="secondary",
                width=8,
            ).pack(side=tk.RIGHT)

    def _open_chat(self, device):
        """Open chat window for the device."""
        local_name = getattr(self.session, "local_device_name", "Orion") if self.session else "Orion"
        ChatWindow(self, peer_name=device.name, local_device_name=local_name)

    def _go_to_chatroom(self):
        """Navigate to the chatroom modal."""
        if self.app and hasattr(self.app, 'show_chatroom_modal'):
            self.app.show_chatroom_modal()

    def destroy(self):
        return super().destroy()
