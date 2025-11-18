"""
Modal Login Page - Initial application interface with form fields and links.
Designed to cover 25% of screen dimensions with centered positioning.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from ui.components import DesignUtils
from ui.theme_tokens import AppConfig, Colors, Spacing, Typography, Space


class LoginPage:
    """Modal popup login interface that covers 25% of screen dimensions."""

    def __init__(self, parent: tk.Tk, on_login: Callable[[str, str], None],
                 on_register: Optional[Callable] = None, 
                 on_forgot_password: Optional[Callable] = None):
        self.parent = parent
        self.on_login = on_login
        self.on_register = on_register
        self.on_forgot_password = on_forgot_password
        
        # Modal state
        self.modal_window = None
        self.overlay = None
        self.device_name_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self._is_password_validated = False
        
        self._create_login_page()

    def _create_login_page(self):
        """Create the login page as the main window content."""
        # Make main window focus on login
        self.parent.focus_set()
        
        # Create login content directly in parent window
        self.modal_window = tk.Frame(self.parent, bg=Colors.SURFACE)
        self.modal_window.pack(fill=tk.BOTH, expand=True, padx=int(Spacing.SM), pady=int(Spacing.SM))
        
        # Create main content
        self._build_content()
        
        # Handle close button click
        self.parent.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Also bind Escape key to close
        self.modal_window.bind('<Escape>', lambda e: self._on_close())

    def _handle_enter_key(self, event):
        """Handle Enter key press based on current validation state."""
        if not self._is_password_validated:
            # If password is not validated, trigger validation
            self._on_validate_click()
        else:
            # If password is validated, trigger login
            self._on_login_click()
        return "break"  # Prevent default behavior

    def _build_content(self):
        """Build the modal content with form fields and interactive elements."""
        # Main container
        main_container = tk.Frame(self.modal_window, bg=Colors.SURFACE)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Header section
        header_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        header_frame.pack(fill=tk.X, pady=(0, 4))
        
        # Application title (larger font)
        title_label = tk.Label(
            header_frame,
            text="LoRa Chat",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_16, Typography.WEIGHT_BOLD)
        )
        title_label.pack()
        
        # Subtitle (larger font)
        subtitle_label = tk.Label(
            header_frame,
            text="Secure Platform",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_12, Typography.WEIGHT_REGULAR)
        )
        subtitle_label.pack(pady=(0, 2))
        
        # Form container
        form_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        form_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Password field (first)
        password_label = tk.Label(
            form_frame,
            text="Password",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_MEDIUM)
        )
        password_label.pack(anchor="w", pady=(0, 2))
        
        self.password_entry = DesignUtils.create_chat_entry(
            form_frame,
            textvariable=self.password_var,
            show="•",  # Password masking
            width=15,
            font=(Typography.FONT_UI, Typography.SIZE_12)
        )
        self.password_entry.pack(fill=tk.X, pady=(0, 2))
        
        # Validate button
        self.validate_btn = DesignUtils.button(
            form_frame,
            text="Validate",
            command=self._on_validate_click,
            variant="primary",
            width=10
        )
        self.validate_btn.pack(fill=tk.X, pady=(0, 6))
        
        # Device Name field (second, now labeled "Preferred Name")
        device_name_label = tk.Label(
            form_frame,
            text="Preferred Name",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_MEDIUM)
        )
        device_name_label.pack(anchor="w", pady=(0, 2))
        
        self.device_name_entry = DesignUtils.create_chat_entry(
            form_frame,
            textvariable=self.device_name_var,
            width=15,
            font=(Typography.FONT_UI, Typography.SIZE_12)
        )
        self.device_name_entry.pack(fill=tk.X, pady=(0, 4))
        
        # Initially disable device name field
        self.device_name_entry.configure(state="disabled")

        # Login button
        self.login_btn = DesignUtils.button(
            form_frame,
            text="Login",
            command=self._on_login_click,
            variant="primary",
            width=10
        )
        self.login_btn.pack(fill=tk.X, pady=(0, 4))
        
        # Initially disable login button
        self.login_btn.configure(state="disabled")
        
        # Bind text changes to enable/disable login button
        self.device_name_var.trace_add('write', self._on_device_name_change)
        
        # Action links container
        links_frame = tk.Frame(main_container, bg=Colors.SURFACE)
        links_frame.pack(fill=tk.X)
        
        # Register link
        register_label = tk.Label(
            links_frame,
            text="Register",
            bg=Colors.SURFACE,
            fg=Colors.LINK_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            cursor="hand2"
        )
        register_label.pack(side=tk.LEFT, padx=(0, 4))
        register_label.bind("<Button-1>", lambda e: self._on_register_click())
        register_label.bind("<Enter>", lambda e: register_label.configure(fg=Colors.LINK_HOVER))
        register_label.bind("<Leave>", lambda e: register_label.configure(fg=Colors.LINK_PRIMARY))
        
        # Forgot Password link
        forgot_label = tk.Label(
            links_frame,
            text="Forgot Password",
            bg=Colors.SURFACE,
            fg=Colors.LINK_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            cursor="hand2"
        )
        forgot_label.pack(side=tk.LEFT)
        forgot_label.bind("<Button-1>", lambda e: self._on_forgot_password_click())
        forgot_label.bind("<Enter>", lambda e: forgot_label.configure(fg=Colors.LINK_HOVER))
        forgot_label.bind("<Leave>", lambda e: forgot_label.configure(fg=Colors.LINK_PRIMARY))
        
        # Deviceless Mode Link
        deviceless_label = tk.Label(
            links_frame,
            text="Continue without Device",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            cursor="hand2"
        )
        deviceless_label.pack(side=tk.RIGHT)
        deviceless_label.bind("<Button-1>", lambda e: self._on_deviceless_click())
        deviceless_label.bind("<Enter>", lambda e: deviceless_label.configure(fg=Colors.TEXT_PRIMARY))
        deviceless_label.bind("<Leave>", lambda e: deviceless_label.configure(fg=Colors.TEXT_SECONDARY))

        # Set focus to password input after UI is fully built
        self.modal_window.after(100, lambda: self._set_initial_focus())

        # Bind Enter key to validate/login based on current state
        # Bind to both modal_window and entry widgets to ensure it works
        self.modal_window.bind('<Return>', self._handle_enter_key)
        self.password_entry.bind('<Return>', self._handle_enter_key)
        self.device_name_entry.bind('<Return>', self._handle_enter_key)
        self.modal_window.bind('<Escape>', lambda e: self._on_close())

    def _set_initial_focus(self):
        """Set initial focus to the password entry field."""
        if self.password_entry:
            self.password_entry.focus_set()
            self.password_entry.icursor(tk.END)  # Move cursor to end

    def _handle_enter_key(self, event):
        """Handle Enter key press based on current validation state."""
        if not self._is_password_validated:
            # If password is not validated, trigger validation
            self._on_validate_click()
        else:
            # If password is validated, trigger login
            self._on_login_click()
        return "break"  # Prevent default behavior

    def _on_validate_click(self):
        """Handle validate button click."""
        password = self.password_var.get().strip()
        
        # Basic password validation
        if not password:
            self._show_validation_error("Please enter a password")
            return
        
        if len(password) < 3:
            self._show_validation_error("Password must be at least 3 characters")
            return
        
        # Disable validate button and show loading state
        self.validate_btn.configure(state="disabled", text="Validating...")
        
        # Simulate validation (in real app, this would validate against a server)
        if self.modal_window:
            self.modal_window.after(1000, lambda: self._on_validation_complete())

    def _on_validation_complete(self):
        """Handle password validation completion."""
        # Enable device name field
        self.device_name_entry.configure(state="normal")
        self.validate_btn.configure(state="normal", text="Validated ✓")
        
        # Set validation flag
        self._is_password_validated = True

        # Enable login button
        self.login_btn.configure(state="normal")

        # Focus on device name field
        if self.modal_window:
            self.modal_window.after(100, lambda: self.device_name_entry.focus_set() if self.modal_window else None)
            self.modal_window.after(150, lambda: self.device_name_entry.icursor(tk.END) if self.modal_window else None)  # Move cursor to end

    def _on_device_name_change(self, *args):
        """Enable/disable login button based on validation state."""
        if self._is_password_validated:
            self.login_btn.configure(state="normal")
        else:
            self.login_btn.configure(state="disabled")

    def _on_login_click(self):
        """Handle login button click."""
        if not self._is_password_validated:
            self._show_validation_error("Please validate your password first")
            return
            
        device_name = self.device_name_var.get().strip() or "Orion"
        
        # Disable button and show loading state
        self.login_btn.configure(state="disabled", text="Logging in...")
        
        # Call login callback
        if self.on_login:
            self.on_login(device_name, "validated_password")
        
        # Re-enable button after a short delay (in case of error)
        if self.modal_window and self.login_btn:
            self.modal_window.after(1000, lambda: self.login_btn.configure(state="normal", text="Login"))

    def _on_register_click(self):
        """Handle register link click."""
        if self.on_register:
            self.on_register()

    def _on_forgot_password_click(self):
        """Handle forgot password link click."""
        if self.on_forgot_password:
            self.on_forgot_password()

    def _on_deviceless_click(self):
        """Handle continue without device click."""
        if self.on_login:
            # Use a special indicator for deviceless mode
            self.on_login("Guest", "deviceless_mode")

    def _show_validation_error(self, message: str):
        """Show validation error message."""
        # Create temporary error label
        error_label = tk.Label(
            self.modal_window,
            text=message,
            bg=Colors.STATE_ERROR,
            fg=Colors.SURFACE,
            font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_REGULAR),
            padx=Spacing.SM,
            pady=Spacing.XXS
        )
        error_label.pack(pady=(Spacing.XXS, 0))
        
        # Remove error after 3 seconds
        if self.modal_window:
            self.modal_window.after(3000, error_label.destroy)

    def _on_close(self):
        """Handle close button click with confirmation."""
        from tkinter import messagebox
        
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Confirm Exit", 
            "Are you sure you want to close LoRa Chat?",
            parent=self.parent
        )
        
        if result:
            # Close the entire application
            self.parent.destroy()

    def close_modal(self):
        """Close the login page and clean up."""
        try:
            if self.modal_window:
                self.modal_window.destroy()
                self.modal_window = None
        except tk.TclError:
            pass  # Window already destroyed

    def show_modal(self):
        """Show the modal dialog."""
        if self.modal_window:
            self.modal_window.lift()
            self.modal_window.focus_set()
            
    def destroy(self):
        """Clean up resources."""
        self.close_modal()