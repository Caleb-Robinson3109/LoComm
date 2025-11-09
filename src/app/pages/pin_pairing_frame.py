"""
PIN Pairing Frame - Replaces traditional login with secure PIN authentication.
Users enter an 8-digit PIN to pair and connect devices with rate limiting protection.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from utils.design_system import Colors, Typography, Spacing, DesignUtils, AppConfig
from utils.ui_helpers import create_scroll_container
from utils.pin_authentication import generate_pairing_pin, verify_pairing_pin, validate_pin_format, get_pin_auth, get_security_status


class PINPairingFrame(tk.Frame):
    """PIN-based device pairing interface."""

    def __init__(self, master, on_pair_success: Callable[[str, str], None], on_demo_login: Optional[Callable] = None):
        super().__init__(master, bg=Colors.SURFACE)
        self.on_pair_success = on_pair_success
        self.on_demo_login = on_demo_login
        self.pin_auth = get_pin_auth()
        self.device_context_var = tk.StringVar(value="Select a device to begin")

        self._create_ui()

    def _create_ui(self):
        """Create the PIN pairing interface."""
        from utils.ui_helpers import create_scroll_container

        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(0, Spacing.LG))
        content = scroll.frame

        DesignUtils.hero_header(
            content,
            title="Device pairing",
            subtitle="Enter the 8-digit secure PIN shared by your peer to begin a protected session."
        )

        tk.Label(
            content,
            textvariable=self.device_context_var,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)
        ).pack(anchor="w", pady=(0, Spacing.SM))

        section, body = DesignUtils.section(content, "Secure PIN authentication", "Codes expire after 10 minutes, max 5 attempts")

        # PIN input field
        pin_label = tk.Label(
            body,
            text="Enter 8-digit PIN",
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
            width=12  # Increased width for 8 digits
        )
        self.pin_entry.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        self.pin_entry.bind('<KeyRelease>', self._on_pin_change)
        self.pin_entry.bind('<Return>', self._on_submit_pin)

        clear_btn = DesignUtils.button(pin_input_frame, text="Clear", command=self._clear_pin, variant="ghost")
        clear_btn.pack(side=tk.LEFT)

        # Security status display
        self.security_label = tk.Label(
            body,
            text="",
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
            fg=Colors.STATE_INFO,
            bg=Colors.SURFACE_ALT
        )
        self.security_label.pack(anchor="w", pady=(0, Spacing.XS))

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
        # Set initial focus
        self.after(100, lambda: self.pin_entry.focus_set())

        # Update security status display
        self._update_security_status()

    def set_pending_device(self, device_name: str, device_id: str | None = None):
        """Expose context to the host pairing page."""
        label = device_name
        if device_id:
            label = f"{device_name} ({device_id})"
        self.device_context_var.set(f"Pairing with {label}")

    def focus_input(self):
        """Focus the PIN entry field."""
        self.pin_entry.focus_set()

    def _update_security_status(self):
        """CRITICAL FIX: Update security status display."""
        try:
            status = get_security_status("desktop-client")
            if status['is_locked']:
                minutes_remaining = int(status['lockout_remaining_seconds'] // 60)
                self.security_label.configure(
                    text=f"🔒 Account locked for {minutes_remaining} more minutes",
                    fg=Colors.STATE_ERROR
                )
            elif status['recent_failed_attempts'] > 0:
                remaining = status['attempts_remaining']
                self.security_label.configure(
                    text=f"⚠️ {status['recent_failed_attempts']} failed attempts. {remaining} remaining.",
                    fg=Colors.STATE_WARNING
                )
            else:
                self.security_label.configure(
                    text="🔐 Secure 8-digit PIN authentication",
                    fg=Colors.STATE_INFO
                )
        except Exception:
            self.security_label.configure(text="")

    def _on_pin_change(self, event):
        """Handle PIN input changes with validation."""
        pin = self.pin_var.get()

        # CRITICAL FIX: Limit to 8 digits
        if len(pin) > 8:
            self.pin_var.set(pin[:8])

        # Validate format
        if len(pin) == 8:
            if not validate_pin_format(pin):
                self._show_error("PIN must be 8 digits only")
            else:
                self._clear_error()
        else:
            self._clear_error()

    def _on_submit_pin(self, event=None):
        """CRITICAL FIX: Handle PIN submission with security measures."""
        pin = self.pin_var.get().strip()

        if not pin:
            self._show_error("Please enter a PIN")
            return

        # CRITICAL FIX: Validate 8-digit format
        if len(pin) != 8:
            self._show_error("PIN must be exactly 8 digits")
            return

        if not validate_pin_format(pin):
            self._show_error("PIN must contain only numbers")
            return

        # Check security status before allowing attempt
        security_status = get_security_status("desktop-client")
        if security_status['is_locked']:
            minutes_remaining = int(security_status['lockout_remaining_seconds'] // 60)
            self._show_error(f"Account locked for {minutes_remaining} more minutes")
            return

        # Verify PIN
        self._set_waiting(True)
        self._clear_error()

        # Verify PIN in background with security tracking
        def verify_worker():
            try:
                device_info, error_message, wait_time = verify_pairing_pin(pin, "desktop-client")

                if device_info:
                    # Success - notify callback
                    self.after(0, lambda: self._on_pair_success(device_info))
                else:
                    # Failed - show error and update security status
                    self.after(0, lambda em=error_message, wt=wait_time: self._on_pair_failed(em, wt))

            except Exception as e:
                self.after(0, lambda: self._on_pair_failed(f"Pairing error: {str(e)}"))
            finally:
                # Always update security status display
                self.after(0, self._update_security_status)

        import threading
        threading.Thread(target=verify_worker, daemon=True).start()

    def _on_pair_success(self, device_info):
        """Handle successful PIN pairing."""
        self._set_waiting(False)
        device_id = device_info['id']
        device_name = device_info['name']

        if self.on_pair_success:
            self.on_pair_success(device_id, device_name)

    def _on_pair_failed(self, error_msg, wait_time=0.0):
        """CRITICAL FIX: Handle failed PIN pairing with security measures."""
        self._set_waiting(False)
        self._show_error(error_msg)
        self._update_security_status()  # Update security display

        if wait_time > 0:
            # If there's a wait time, disable the button temporarily
            wait_seconds = int(wait_time)
            self.pair_btn.configure(state="disabled", text=f"Wait {wait_seconds}s...")
            self.after(int(wait_time * 1000), lambda: self._set_waiting(False))

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
