"""
PIN Pairing Frame - Replaces traditional login with secure PIN authentication.
Users enter an 8-digit PIN to pair and connect devices with rate limiting protection.
"""
import tkinter as tk
from typing import Callable, Optional

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.ui_helpers import create_scroll_container
from utils.pin_authentication import (
    generate_pairing_pin,
    verify_pairing_pin,
    validate_pin_format,
    get_pin_auth,
    get_security_status,
)


class PINPairingFrame(tk.Frame):
    """PIN-based device pairing interface."""

    def __init__(self, master, on_pair_success: Callable[[str, str], None], on_demo_login: Optional[Callable] = None):
        super().__init__(master, bg=Colors.SURFACE)
        self.on_pair_success = on_pair_success
        self.on_demo_login = on_demo_login
        self.pin_auth = get_pin_auth()
        self.device_context_var = tk.StringVar(value="Select a device to begin")
        self.pin_vars: list[tk.StringVar] = []
        self.pin_entries: list[tk.Entry] = []

        self._create_ui()

    def _create_ui(self):
        """Create the PIN pairing interface."""
        scroll = create_scroll_container(
            self,
            bg=Colors.SURFACE,
            padding=(Spacing.MD, Spacing.LG),
        )
        content = scroll.frame

        DesignUtils.hero_header(
            content,
            title="Device pairing",
            subtitle="",
        )

        tk.Label(
            content,
            textvariable=self.device_context_var,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM)
        ).pack(anchor="w", pady=(0, Spacing.SM))

        section, body = DesignUtils.section(
            content,
            "Secure PIN entry",
            "Codes expire in 10 minutes. Five attempts max.",
        )

        inputs_row = tk.Frame(body, bg=Colors.SURFACE_ALT)
        inputs_row.pack(anchor="w", pady=(Spacing.XS, Spacing.SM))
        self._build_pin_inputs(inputs_row)

        DesignUtils.button(
            body,
            text="Clear PIN",
            command=self._clear_pin,
            variant="ghost",
        ).pack(anchor="w", pady=(0, Spacing.SM))

        self.security_label = tk.Label(
            body,
            text="",
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_MEDIUM),
            fg=Colors.STATE_INFO,
            bg=Colors.SURFACE_ALT,
        )
        self.security_label.pack(anchor="w", pady=(0, Spacing.XXS))

        self.error_label = tk.Label(
            body,
            text="",
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR),
            fg=Colors.STATE_ERROR,
            bg=Colors.SURFACE_ALT,
        )
        self.error_label.pack(anchor="w", pady=(0, Spacing.XXS))

        button_frame = tk.Frame(body, bg=Colors.SURFACE_ALT)
        button_frame.pack(fill=tk.X, pady=(Spacing.MD, 0))

        self.pair_btn = DesignUtils.button(
            button_frame,
            text="Pair device",
            command=self._on_submit_pin,
        )
        self.pair_btn.pack(fill=tk.X, pady=(0, Spacing.SM))

        if self.on_demo_login:
            DesignUtils.button(
                button_frame,
                text="Mock",
                command=self._on_demo_login,
                variant="secondary",
            ).pack(fill=tk.X)

        # Set initial focus after widgets are laid out
        self.after(100, self.focus_input)

        # Update security status display
        self._update_security_status()

    def set_pending_device(self, device_name: str, device_id: str | None = None):
        """Expose context to the host pairing page."""
        label = device_name
        if device_id:
            label = f"{device_name} ({device_id})"
        self.device_context_var.set(f"Pairing with {label}")

    def focus_input(self):
        """Focus the first PIN box."""
        if self.pin_entries:
            self._focus_box(0)

    def _build_pin_inputs(self, parent: tk.Frame):
        self.pin_vars.clear()
        self.pin_entries.clear()
        for idx in range(8):
            var = tk.StringVar()
            entry = tk.Entry(
                parent,
                width=2,
                textvariable=var,
                justify="center",
                font=(Typography.FONT_UI, Typography.SIZE_18, Typography.WEIGHT_BOLD),
                bg=Colors.SURFACE,
                fg=Colors.TEXT_PRIMARY,
                relief="flat",
                highlightthickness=1,
                highlightbackground=Colors.BORDER,
                highlightcolor=Colors.BUTTON_PRIMARY_BG,
                insertwidth=0,
            )
            entry.pack(side=tk.LEFT, padx=(Spacing.XXS, Spacing.XXS), pady=(0, Spacing.XXS))
            entry.bind("<KeyRelease>", lambda e, i=idx: self._handle_digit_key(e, i))
            entry.bind("<KeyPress>", lambda e, i=idx: self._handle_digit_press(e, i))
            entry.bind("<Return>", self._on_submit_pin)
            self.pin_vars.append(var)
            self.pin_entries.append(entry)

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

    def _handle_digit_press(self, event, index: int):
        if event.keysym == "Left" and index > 0:
            self._focus_box(index - 1)
            return "break"
        if event.keysym == "Right" and index < len(self.pin_entries) - 1:
            self._focus_box(index + 1)
            return "break"
        return None

    def _handle_digit_key(self, event, index: int):
        if not self.pin_entries:
            return
        value = self.pin_vars[index].get()
        keys_to_ignore = {"Shift_L", "Shift_R", "Tab"}
        if event.keysym in keys_to_ignore:
            return

        if event.keysym == "BackSpace":
            if value:
                self.pin_vars[index].set("")
            elif index > 0:
                self.pin_vars[index - 1].set("")
                self._focus_box(index - 1)
            return

        if len(value) > 1:
            self._apply_paste(value, index)
            return

        if not value:
            return

        if not value.isdigit():
            self.pin_vars[index].set("")
            return

        self.pin_vars[index].set(value)
        if index < len(self.pin_entries) - 1:
            self._focus_box(index + 1)

    def _apply_paste(self, text: str, start_index: int):
        digits = [c for c in text if c.isdigit()]
        if not digits:
            self.pin_vars[start_index].set("")
            return
        idx = start_index
        for digit in digits:
            if idx >= len(self.pin_entries):
                break
            self.pin_vars[idx].set(digit)
            idx += 1
        if idx < len(self.pin_entries):
            self._focus_box(idx)
        else:
            self.pin_entries[-1].focus_set()

    def _collect_pin(self) -> str:
        return "".join(var.get() for var in self.pin_vars)

    def _focus_box(self, index: int):
        entry = self.pin_entries[index]
        entry.focus_set()
        entry.icursor(tk.END)

    def _on_submit_pin(self, event=None):
        """CRITICAL FIX: Handle PIN submission with security measures."""
        pin = self._collect_pin().strip()

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

        self.focus_input()

    def _on_demo_login(self):
        """Handle demo login button."""
        if self.on_demo_login:
            self.on_demo_login()

    def _clear_pin(self):
        """Clear the PIN input field."""
        for var in self.pin_vars:
            var.set("")
        self._clear_error()
        self.focus_input()

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
            for entry in self.pin_entries:
                entry.configure(state="disabled")
        else:
            self.pair_btn.configure(state="normal", text="Pair device")
            for entry in self.pin_entries:
                entry.configure(state="normal")
            self.focus_input()

    def generate_new_pin(self):
        """Generate a new PIN for display (for debugging/testing)."""
        import uuid
        device_id = str(uuid.uuid4())[:8]
        device_name = f"Device-{device_id}"
        pin = generate_pairing_pin(device_id, device_name)
        return pin, device_id, device_name
