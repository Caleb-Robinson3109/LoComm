"""Chat header component for connection status and controls."""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class ChatHeader(ttk.Frame):
    """Header component showing connection status and basic controls."""

    def __init__(self, master, on_disconnect: Optional[Callable] = None):
        super().__init__(master)
        self.on_disconnect = on_disconnect
        self._connected = False

        # ---------- Status Display ---------- #
        status_frame = ttk.Frame(self)
        status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Connection status with enhanced styling
        self.status_var = tk.StringVar(value="Disconnected")
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_NORMAL)
        )
        self.status_label.pack(side=tk.LEFT, anchor="w")

        # Connection indicator (colored dot)
        self.status_indicator = tk.Canvas(
            status_frame, width=12, height=12,
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(Spacing.SM, 0))
        self._draw_status_indicator()

        # ---------- Control Buttons ---------- #
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.RIGHT)

        # Clear chat button
        self.clear_btn = DesignUtils.create_styled_button(
            control_frame, "Clear Chat", self._on_clear_chat,
            style='Warning.TButton'
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=(Spacing.XS, 0))

        # Disconnect button (only show when connected)
        self.disconnect_btn = DesignUtils.create_styled_button(
            control_frame, "Disconnect", self._on_disconnect_click,
            style='Danger.TButton'
        )
        self.disconnect_btn.pack(side=tk.RIGHT, padx=(Spacing.XS, 0))
        self.disconnect_btn.pack_forget()  # Hide initially

    def set_status(self, status_text: str) -> None:
        """Update the connection status and visual indicator."""
        self.status_var.set(status_text)

        # Update visual indicator based on status
        lowered = status_text.lower()
        if any(keyword in lowered for keyword in ("authenticated", "ready")):
            self._set_connected_state(True)
        elif "connected (mock)" in lowered:
            self._set_connected_state(True)
        elif any(keyword in lowered for keyword in ("disconnected", "connection failed", "invalid device password", "not connected")):
            self._set_connected_state(False)
        elif "verifying" in lowered or "connecting" in lowered:
            self._set_status_state("connecting")
        elif "send failed" in lowered:
            self._set_status_state("error")

    def _set_connected_state(self, connected: bool) -> None:
        """Update visual state for connected/disconnected."""
        self._connected = connected

        if connected:
            self._set_status_state("connected")
            self.disconnect_btn.pack(side=tk.RIGHT, padx=(Spacing.XS, 0))
        else:
            self._set_status_state("disconnected")
            self.disconnect_btn.pack_forget()

    def _set_status_state(self, state: str) -> None:
        """Set the status indicator color based on state."""
        # All status indicators use white
        colors = {
            "connected": "#FFFFFF",
            "connecting": "#FFFFFF",
            "disconnected": "#FFFFFF",
            "error": "#FFFFFF"
        }

        color = colors.get(state, "#FFFFFF")
        self._update_indicator_color(color)

    def _update_indicator_color(self, color: str) -> None:
        """Update the color of the status indicator."""
        self.status_indicator.delete("all")
        self._draw_status_indicator(color)

    def _draw_status_indicator(self, color: str = "#FFFFFF") -> None:
        """Draw the status indicator circle."""
        x, y = 6, 6
        radius = 5
        self.status_indicator.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline=color
        )

    def _on_clear_chat(self) -> None:
        """Handle clear chat button click."""
        # This will be connected to the main chat tab's clear method
        if hasattr(self, 'on_clear_chat'):
            self.on_clear_chat()

    def _on_disconnect_click(self) -> None:
        """Handle disconnect button click."""
        if self.on_disconnect:
            self.on_disconnect()

    def set_clear_chat_callback(self, callback: Callable) -> None:
        """Set callback for clear chat functionality."""
        self.on_clear_chat = callback
