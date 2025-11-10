"""
PIN Pairing Frame - Replaces traditional login with secure PIN authentication.
Users enter an 8-digit PIN to pair and connect devices with rate limiting protection.
"""
import tkinter as tk
from typing import Callable, Optional
from tkinter import messagebox

from utils.design_system import Colors, Typography, Spacing, DesignUtils
from utils.pin_authentication import (
    generate_pairing_pin,
    verify_pairing_pin,
)
from utils.pin_pairing_state import PinPairingState


class PINPairingFrame(tk.Frame):
    """PIN-based device pairing interface."""

    def __init__(self, master, on_pair_success: Callable[[str, str], None], on_demo_login: Optional[Callable] = None):
        super().__init__(master, bg=Colors.SURFACE)
        self.on_pair_success = on_pair_success
        self.on_demo_login = on_demo_login
        self.pairing_state = PinPairingState()
        self.pin_vars: list[tk.StringVar] = []
        self.pin_entries: list[tk.Entry] = []

        self._create_ui()

    def _create_ui(self):
        """Create the PIN pairing interface."""
        content = tk.Frame(self, bg=Colors.SURFACE, padx=Spacing.SM, pady=Spacing.SM)
        content.pack(fill=tk.BOTH, expand=True)

        header_frame = tk.Frame(content, bg=Colors.SURFACE)
        header_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        self.title_label = tk.Label(
            header_frame,
            text="Pair with the device",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            header_frame,
            text="Enter the 8-character code shared during pairing.",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR),
        )
        self.subtitle_label.pack(anchor="w", pady=(Spacing.XXS, Spacing.SM))

        inputs_row = tk.Frame(content, bg=Colors.SURFACE_ALT)
        inputs_row.pack(anchor="w", pady=(Spacing.XXS, Spacing.SM))
        inputs_row.pack_propagate(False)
        self._build_pin_inputs(inputs_row)

        control_row = tk.Frame(content, bg=Colors.SURFACE)
        control_row.pack(fill=tk.X, pady=(Spacing.MD, 0))
        control_row.grid_columnconfigure(1, weight=1)
        if self.on_demo_login:
            DesignUtils.button(
                control_row,
                text="Mock",
                command=self._on_demo_login,
                variant="secondary",
            ).grid(row=0, column=0, sticky="w")
        DesignUtils.button(
            control_row,
            text="Clear PIN",
            command=self._clear_pin,
            variant="ghost",
        ).grid(row=0, column=2, sticky="e")

        button_frame = tk.Frame(content, bg=Colors.SURFACE)
        button_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))

        self.pair_btn = DesignUtils.button(
            button_frame,
            text="Pair device",
            command=self._on_submit_pin,
        )
        self.pair_btn.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Set initial focus after widgets are laid out
        self.after(100, self.focus_input)

        # No inline security status label

    def set_pending_device(self, device_name: str, device_id: str | None = None):
        """Expose context to the host pairing page."""
        if device_id:
            label = f"{device_name} - {device_id}"
        else:
            label = device_name
        self.title_label.configure(text=f"Pair {label}")

    def focus_input(self):
        """Focus the first PIN box."""
        if self.pin_entries:
            self._focus_box(0)

    def _build_pin_inputs(self, parent: tk.Frame):
        self.pin_vars.clear()
        self.pin_entries.clear()
        pin_spacing = max(int(Spacing.XXS * 0.95), 1)
        for idx in range(8):
            var = tk.StringVar()
            entry = DesignUtils.create_pin_entry(
                parent,
                textvariable=var,
                justify="center",
                width=2,
                font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD),
            )
            entry.pack(side=tk.LEFT, padx=(pin_spacing, pin_spacing), pady=(0, pin_spacing))
            entry.bind("<KeyRelease>", lambda e, i=idx: self._handle_digit_key(e, i))
            entry.bind("<KeyPress>", lambda e, i=idx: self._handle_digit_press(e, i))
            entry.bind("<Return>", self._on_submit_pin)
            self.pin_vars.append(var)
            self.pin_entries.append(entry)

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

        if not value.isalnum():
            self.pin_vars[index].set("")
            return

        self.pin_vars[index].set(value)
        if index < len(self.pin_entries) - 1:
            self._focus_box(index + 1)

    def _apply_paste(self, text: str, start_index: int):
        digits = [c for c in text if c.isalnum()]
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

        valid, error = self.pairing_state.validate_pin(pin)
        if not valid:
            self._show_error(error)
            return

        locked, lock_msg, _ = self.pairing_state.check_lockout()
        if locked:
            self._show_error(lock_msg)
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
                self.after(0, lambda: None)

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
        # No inline security display anymore

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
        messagebox.showerror("Pairing Failed", message)

    def _clear_error(self):
        """No inline error label—no action required."""
        return

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
