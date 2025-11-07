"""
PIN Pairing Frame - Replaces traditional login with 5-digit PIN authentication.
Users simply enter a 5-digit PIN to pair and connect devices.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from utils.design_system import Colors, Typography, Spacing, DesignUtils, AppConfig
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
        self.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Main container
        main_container = tk.Frame(self, bg=Colors.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title section
        title_frame = tk.Frame(main_container, bg=Colors.BG_PRIMARY)
        title_frame.pack(pady=(0, Spacing.XL))

        title_label = tk.Label(
            title_frame,
            text="Device Pairing",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XL, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",
            bg=Colors.BG_PRIMARY
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Enter 5-digit PIN to connect",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg="#CCCCCC",
            bg=Colors.BG_PRIMARY
        )
        subtitle_label.pack(pady=(Spacing.SM, 0))

        # PIN Input Section
        pin_frame = ttk.LabelFrame(main_container, text="PIN Authentication", style='Custom.TLabelframe')
        pin_frame.pack(fill=tk.X, pady=(0, Spacing.LG))

        pin_content = tk.Frame(pin_frame, bg=Colors.BG_PRIMARY)
        pin_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # PIN input field
        pin_label = tk.Label(
            pin_content,
            text="Enter 5-digit PIN:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_MEDIUM),
            fg="#FFFFFF",
            bg=Colors.BG_PRIMARY
        )
        pin_label.pack(anchor="w", pady=(0, Spacing.SM))

        # PIN entry with validation
        pin_input_frame = tk.Frame(pin_content, bg=Colors.BG_PRIMARY)
        pin_input_frame.pack(fill=tk.X, pady=(0, Spacing.LG))

        self.pin_var = tk.StringVar()
        self.pin_entry = tk.Entry(
            pin_input_frame,
            textvariable=self.pin_var,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG),
            justify='center',
            width=10,
            relief='flat',
            bd=5,
            bg=Colors.BG_SECONDARY,
            fg="#FFFFFF",
            insertbackground="#FFFFFF"
        )
        self.pin_entry.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        self.pin_entry.bind('<KeyRelease>', self._on_pin_change)
        self.pin_entry.bind('<Return>', self._on_submit_pin)

        # Clear PIN button
        clear_btn = tk.Button(
            pin_input_frame,
            text="Clear",
            command=self._clear_pin,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            bg=Colors.BG_TERTIARY,
            fg="#FFFFFF",
            relief='flat',
            bd=2,
            padx=Spacing.MD,
            pady=Spacing.SM
        )
        clear_btn.pack(side=tk.LEFT)

        # Error message
        self.error_label = tk.Label(
            pin_content,
            text="",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg="#FF6B6B",
            bg=Colors.BG_PRIMARY
        )
        self.error_label.pack(anchor="w")

        # Action buttons
        button_frame = tk.Frame(pin_content, bg=Colors.BG_PRIMARY)
        button_frame.pack(fill=tk.X, pady=(Spacing.LG, 0))

        # Pair button
        self.pair_btn = DesignUtils.create_styled_button(
            button_frame,
            "Pair Device",
            self._on_submit_pin,
            style='Primary.TButton'
        )
        self.pair_btn.pack(fill=tk.X, pady=(0, Spacing.MD))

        # Demo login button
        if self.on_demo_login:
            demo_btn = DesignUtils.create_styled_button(
                button_frame,
                "Demo Access (Skip Pairing)",
                self._on_demo_login,
                style='Secondary.TButton'
            )
            demo_btn.pack(fill=tk.X)

        # Info section
        info_frame = ttk.LabelFrame(main_container, text="How to Pair", style='Custom.TLabelframe')
        info_frame.pack(fill=tk.X, pady=(Spacing.LG, 0))

        info_content = tk.Frame(info_frame, bg=Colors.BG_PRIMARY)
        info_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        info_text = """• Get a 5-digit PIN from another device
• Enter the PIN above to connect
• PIN expires after 10 minutes
• Use demo access for testing"""

        info_label = tk.Label(
            info_content,
            text=info_text,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg="#CCCCCC",
            bg=Colors.BG_PRIMARY,
            justify='left'
        )
        info_label.pack(anchor="w")

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
