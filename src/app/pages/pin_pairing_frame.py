"""
PIN Pairing Frame - Replaces traditional login with 5-digit PIN authentication.
Users simply enter a 5-digit PIN to pair and connect devices.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from utils.design_system import Colors, Typography, Spacing, DesignUtils, AppConfig
from utils.ui_helpers import create_scroll_container
from utils.pin_authentication import generate_pairing_pin, verify_pairing_pin, validate_pin_format, get_pin_auth


class PINPairingFrame(tk.Frame):
    """PIN-based device pairing interface."""

    def __init__(self, master, on_pair_success: Callable[[str, str], None], on_demo_login: Optional[Callable] = None):
        super().__init__(master, bg=Colors.BG_PRIMARY)
        self.on_pair_success = on_pair_success
        self.on_demo_login = on_demo_login
        self.pin_auth = get_pin_auth()

        self._create_ui()

    def _create_ui(self):
        """Create the PIN pairing interface."""
        self.pack(fill=tk.BOTH, expand=True)
        from utils.ui_helpers import create_scroll_container

        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(Spacing.XL, Spacing.XL))
        content = scroll.frame

        DesignUtils.hero_header(
            content,
            title="Device pairing",
            subtitle="Enter the 5-digit PIN shared by your peer to begin a secure session."
        )

        section, body = DesignUtils.section(content, "PIN authentication", "Codes expire after 10 minutes")

        # PIN input field
        pin_label = tk.Label(
            body,
            text="Enter 5-digit PIN",
            bg=Colors.SURFACE_ALT,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_MEDIUM)
        )
        pin_label.pack(anchor="w", pady=(0, Spacing.XS))

        # PIN entry with validation
        pin_input_frame = tk.Frame(body, bg=Colors.SURFACE_ALT)
        pin_input_frame.pack(fill=tk.X, pady=(0, Spacing.LG))

        self.pin_var = tk.StringVar()
        self.pin_entry = DesignUtils.create_chat_entry(
            pin_input_frame,
            textvariable=self.pin_var,
            justify='center',
            width=10
        )
        self.pin_entry.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        self.pin_entry.bind('<KeyRelease>', self._on_pin_change)
        self.pin_entry.bind('<Return>', self._on_submit_pin)

        clear_btn = DesignUtils.button(pin_input_frame, text="Clear", command=self._clear_pin, variant="ghost")
        clear_btn.pack(side=tk.LEFT)

        # Error message
        self.error_label = tk.Label(
            body,
            text="",
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            fg=Colors.STATE_ERROR,
            bg=Colors.SURFACE_ALT
        )
        self.error_label.pack(anchor="w")

        # Action buttons
        button_frame = tk.Frame(body, bg=Colors.SURFACE_ALT)
        button_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))

        # Pair button
        self.pair_btn = DesignUtils.button(button_frame, text="Pair device", command=self._on_submit_pin)
        self.pair_btn.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Demo login button
        if self.on_demo_login:
            DesignUtils.button(button_frame, text="Demo access (skip pairing)", command=self._on_demo_login, variant="secondary").pack(fill=tk.X)

        # Info section
        info_section, info_body = DesignUtils.section(content, "How to pair", "Quick steps")
        steps = [
            "Get the 5-digit PIN from a nearby device",
            "Enter the PIN in the field above",
            "Wait for confirmation before chatting",
            "Use demo access if hardware is unavailable"
        ]
        for step in steps:
            tk.Label(info_body, text=f"• {step}", bg=Colors.SURFACE_ALT, fg=Colors.TEXT_SECONDARY,
                     font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)).pack(anchor="w")

        # Set initial focus
        self.after(100, lambda: self.pin_entry.focus_set())

    def _on_pin_change(self, event):
        """Handle PIN input changes with validation."""
        pin = self.pin_var.get()

        # Limit to 5 digits
        if len(pin) > 5:
            self.pin_var.set(pin[:5])

        # Validate format
        if len(pin) == 5:
            if not validate_pin_format(pin):
                self._show_error("PIN must be 5 digits only")
            else:
                self._clear_error()
        else:
            self._clear_error()

    def _on_submit_pin(self, event=None):
        """Handle PIN submission."""
        pin = self.pin_var.get().strip()

        if not pin:
            self._show_error("Please enter a PIN")
            return

        if len(pin) != 5:
            self._show_error("PIN must be exactly 5 digits")
            return

        if not validate_pin_format(pin):
            self._show_error("PIN must contain only numbers")
            return

        # Verify PIN
        self._set_waiting(True)
        self._clear_error()

        # Verify PIN in background
        def verify_worker():
            try:
                device_info = verify_pairing_pin(pin)

                if device_info:
                    # Success - notify callback
                    self.after(0, lambda: self._on_pair_success(device_info))
                else:
                    # Failed - show error
                    self.after(0, lambda: self._on_pair_failed("Invalid or expired PIN"))

            except Exception as e:
                self.after(0, lambda: self._on_pair_failed(f"Pairing error: {str(e)}"))

        import threading
        threading.Thread(target=verify_worker, daemon=True).start()

    def _on_pair_success(self, device_info):
        """Handle successful PIN pairing."""
        self._set_waiting(False)
        device_id = device_info['id']
        device_name = device_info['name']

        if self.on_pair_success:
            self.on_pair_success(device_id, device_name)

    def _on_pair_failed(self, error_msg):
        """Handle failed PIN pairing."""
        self._set_waiting(False)
        self._show_error(error_msg)
        self.pin_entry.focus_set()
        self.pin_entry.select_range(0, tk.END)

    def _on_demo_login(self):
        """Handle demo login button."""
        if self.on_demo_login:
            self.on_demo_login()

    def _clear_pin(self):
        """Clear the PIN input field."""
        self.pin_var.set("")
        self._clear_error()
        self.pin_entry.focus_set()

    def _show_error(self, message):
        """Show error message."""
        self.error_label.configure(text=message)

    def _clear_error(self):
        """Clear error message."""
        self.error_label.configure(text="")

    def _set_waiting(self, waiting):
        """Set waiting state for UI elements."""
        if waiting:
            self.pair_btn.configure(state="disabled", text="Pairing...")
            self.pin_entry.configure(state="disabled")
        else:
            self.pair_btn.configure(state="normal", text="Pair Device")
            self.pin_entry.configure(state="normal")

    def generate_new_pin(self):
        """Generate a new PIN for display (for debugging/testing)."""
        import uuid
        device_id = str(uuid.uuid4())[:8]
        device_name = f"Device-{device_id}"
        pin = generate_pairing_pin(device_id, device_name)
        return pin, device_id, device_name
