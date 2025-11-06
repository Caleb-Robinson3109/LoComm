import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import threading


class SimpleLoginFrame(ttk.Frame):
    """
    Simplified login frame with basic validation and user feedback.
    Addresses critical issues:
    - Input visibility
    - Connection feedback
    - Basic error handling
    """

    def __init__(self, parent, on_login):
        super().__init__(parent)
        self.on_login = on_login
        self.is_waiting = False

        self.setup_ui()

        # Auto-focus password field for better UX
        self.password_entry.focus()

    def setup_ui(self):
        """Set up the login UI components."""
        # Title
        title_label = ttk.Label(self, text="LoRa Chat Desktop", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(20, 30))

        # Login form container
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20, padx=40, fill='x')

        # Username field
        ttk.Label(form_frame, text="Username:").pack(anchor='w', pady=(0, 5))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, width=25)
        self.username_entry.pack(fill='x', pady=(0, 15))

        # Password field
        ttk.Label(form_frame, text="Device Password:").pack(anchor='w', pady=(0, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show='*', width=25)
        self.password_entry.pack(fill='x', pady=(0, 20))

        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        show_password_cb = ttk.Checkbutton(form_frame, text="Show password",
                                         variable=self.show_password_var,
                                         command=self.toggle_password_visibility)
        show_password_cb.pack(anchor='w', pady=(0, 20))

        # Login button
        self.login_button = ttk.Button(form_frame, text="Connect to Device",
                                     command=self.handle_login_attempt)
        self.login_button.pack(fill='x', pady=(0, 10))

        # Status label
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(form_frame, textvariable=self.status_var,
                                    foreground='blue')
        self.status_label.pack()

        # Bind Enter key to login
        self.password_entry.bind('<Return>', lambda e: self.handle_login_attempt())
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())

        # Focus username field initially
        self.username_entry.focus()

    def toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')

    def set_waiting(self, waiting):
        """Set the waiting state for login."""
        self.is_waiting = waiting
        if waiting:
            self.login_button.config(state='disabled', text='Connecting...')
            self.status_var.set("Connecting to device...")
        else:
            self.login_button.config(state='normal', text='Connect to Device')
            self.status_var.set("")

    def validate_inputs(self):
        """Validate user inputs before login attempt."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username:
            messagebox.showerror("Validation Error", "Username is required.")
            self.username_entry.focus()
            return False

        if not password:
            messagebox.showerror("Validation Error", "Device password is required.")
            self.password_entry.focus()
            return False

        if len(username) > 50:
            messagebox.showerror("Validation Error", "Username must be 50 characters or less.")
            self.username_entry.focus()
            return False

        if len(password) > 100:
            messagebox.showerror("Validation Error", "Password must be 100 characters or less.")
            self.password_entry.focus()
            return False

        return True

    def handle_login_attempt(self):
        """Handle the login attempt."""
        if self.is_waiting:
            return

        # Validate inputs
        if not self.validate_inputs():
            return

        # Get credentials
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        password_bytes = bytearray(password, 'utf-8')

        # Set waiting state
        self.set_waiting(True)

        # Call the login handler
        self.on_login(username, password_bytes)

    def show_connection_status(self, status, is_error=False):
        """Show connection status message."""
        if is_error:
            self.status_var.set(f"Error: {status}")
            self.status_label.config(foreground='red')
        else:
            self.status_var.set(status)
            self.status_label.config(foreground='blue')

    def clear_status(self):
        """Clear the status message."""
        self.status_var.set("")
        self.status_label.config(foreground='blue')
