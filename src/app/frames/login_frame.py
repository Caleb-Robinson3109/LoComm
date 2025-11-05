import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from utils.user_store import register_user, validate_login
from utils.validation import validate_credentials, enforce_ascii_and_limit
from utils.design_system import Colors, Typography, Spacing, DesignUtils

MAX_CRED_LEN = 32
ASCII_RANGE = set(range(0x20, 0x7F))


def is_printable_ascii(s: str) -> bool:
    from utils.validation import is_printable_ascii
    return is_printable_ascii(s)


class LoginFrame(ttk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master)
        self.on_login = on_login

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # ---------- Enhanced Header ---------- #
        header_label = DesignUtils.create_styled_label(self, "LoRa Chat Login", style='Header.TLabel')
        header_label.pack(pady=(Spacing.XXL, Spacing.LG))

        # ---------- Login Form Container with Box Border ---------- #
        form_section = ttk.LabelFrame(self, text="Authentication", style='Custom.TLabelframe')
        form_section.pack(padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD), fill=tk.X)

        form_container = ttk.Frame(form_section)
        form_container.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # Username section
        username_section = ttk.Frame(form_container)
        username_section.pack(fill=tk.X, pady=(Spacing.LG, Spacing.MD))

        DesignUtils.create_styled_label(username_section, "Username", style='SubHeader.TLabel').pack(anchor="w", pady=(0, Spacing.XS))

        self.username_entry = tk.Entry(username_section, textvariable=self.username_var,
                                     fg="#FFFFFF",  # White text
                                     font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
                                     relief="flat", bd=0)
        self.username_entry.pack(fill=tk.X, pady=Spacing.XS, ipady=Spacing.SM)

        # Password section
        password_section = ttk.Frame(form_container)
        password_section.pack(fill=tk.X, pady=(Spacing.MD, Spacing.LG))

        DesignUtils.create_styled_label(password_section, "Password", style='SubHeader.TLabel').pack(anchor="w", pady=(0, Spacing.XS))

        self.password_entry = tk.Entry(password_section, textvariable=self.password_var, show="*",
                                     fg="#FFFFFF",  # White text
                                     font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
                                     relief="flat", bd=0)
        self.password_entry.pack(fill=tk.X, pady=Spacing.XS, ipady=Spacing.SM)

        self.username_entry.bind("<Return>", lambda e: self._try_login())
        self.password_entry.bind("<Return>", lambda e: self._try_login())

        # ---------- Action Buttons ---------- #
        btns = ttk.Frame(self)
        btns.pack(pady=(Spacing.LG, Spacing.MD))

        self.login_btn = DesignUtils.create_styled_button(btns, "Login", self._try_login,
                                                        style='Primary.TButton')
        self.login_btn.pack(side=tk.LEFT, padx=Spacing.SM)

        # Add bypass button for testing
        self.bypass_btn = DesignUtils.create_styled_button(btns, "Demo Login", self._demo_login,
                                                        style='Success.TButton')
        self.bypass_btn.pack(side=tk.LEFT, padx=Spacing.SM)

        self.new_user_btn = DesignUtils.create_styled_button(btns, "New User", self._new_user_dialog,
                                                           style='Secondary.TButton')
        self.new_user_btn.pack(side=tk.LEFT, padx=Spacing.SM)

        # ---------- Progress Indicator ---------- #
        self.progress = ttk.Progressbar(self, mode="indeterminate", length=200)
        self.progress_shown = False

        # ---------- Input Validation (only basic length checks) ---------- #
        # Removed ASCII filtering that was interfering with input
        # Basic validation is handled by the ttk widgets automatically

    def _try_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        # Debug output to see what's happening
        print(f"DEBUG: Username: '{username}', Length: {len(username)}")
        print(f"DEBUG: Password: '{password}', Length: {len(password)}")

        if not username:
            print("DEBUG: Username is empty!")
            messagebox.showerror("Error", "Username is required.")
            return

        if not password:
            print("DEBUG: Password is empty!")
            messagebox.showerror("Error", "Password is required.")
            return

        # Use centralized validation
        is_valid, error_msg = validate_credentials(username, password)
        if not is_valid:
            print(f"DEBUG: Validation failed: {error_msg}")
            messagebox.showerror("Error", error_msg)
            return

        # Validate from user store
        if not validate_login(username, password):
            print("DEBUG: Login validation failed!")
            messagebox.showerror("Login Failed", "Incorrect username or password.")
            return

        print("DEBUG: Login successful, proceeding...")
        self.set_waiting(True)
        self.on_login(username, bytearray(password, "utf-8"))

    def _demo_login(self):
        """Demo login that bypasses user store validation for testing."""
        print("DEBUG: Demo login activated")
        # Clear any existing values
        self.username_var.set("")
        self.password_var.set("")

        # Set test values directly
        self.username_var.set("admin")
        self.password_var.set("admin")

        # Force the login
        print("DEBUG: Setting demo credentials and attempting login...")
        self.set_waiting(True)
        self.on_login("admin", bytearray("admin", "utf-8"))

    def _new_user_dialog(self):
        """Opens a modal dialog to register a new user."""
        dialog = tk.Toplevel(self)
        dialog.title("New User Registration")
        dialog.geometry("350x400")
        dialog.grab_set()  # modal window

        # ---------- Registration Form Container with Box Border ---------- #
        form_section = ttk.LabelFrame(dialog, text="Account Details", style='Custom.TLabelframe')
        form_section.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        dialog_frame = ttk.Frame(form_section)
        dialog_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # Header
        DesignUtils.create_styled_label(dialog_frame, "Create New Account", style='Header.TLabel').pack(pady=(0, Spacing.LG))

        # Username section
        username_section = ttk.Frame(dialog_frame)
        username_section.pack(fill=tk.X, pady=(0, Spacing.MD))
        DesignUtils.create_styled_label(username_section, "Username", style='SubHeader.TLabel').pack(anchor="w", pady=(0, Spacing.XS))
        username_var = tk.StringVar()
        username_entry = tk.Entry(username_section, textvariable=username_var,
                                fg="#FFFFFF",  # White text
                                font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
                                relief="flat", bd=0)
        username_entry.pack(fill=tk.X, ipady=Spacing.SM)

        # Password section
        password_section = ttk.Frame(dialog_frame)
        password_section.pack(fill=tk.X, pady=(0, Spacing.MD))
        DesignUtils.create_styled_label(password_section, "Password", style='SubHeader.TLabel').pack(anchor="w", pady=(0, Spacing.XS))
        password_var = tk.StringVar()
        password_entry = tk.Entry(password_section, textvariable=password_var, show="*",
                                fg="#FFFFFF",  # White text
                                font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
                                relief="flat", bd=0)
        password_entry.pack(fill=tk.X, ipady=Spacing.SM)

        # Confirm password section
        confirm_section = ttk.Frame(dialog_frame)
        confirm_section.pack(fill=tk.X, pady=(0, Spacing.LG))
        DesignUtils.create_styled_label(confirm_section, "Confirm Password", style='SubHeader.TLabel').pack(anchor="w", pady=(0, Spacing.XS))
        confirm_var = tk.StringVar()
        confirm_entry = tk.Entry(confirm_section, textvariable=confirm_var, show="*",
                               fg="#FFFFFF",  # White text
                               font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
                               relief="flat", bd=0)
        confirm_entry.pack(fill=tk.X, ipady=Spacing.SM)

        def submit():
            u = username_var.get().strip()
            p = password_var.get().strip()
            c = confirm_var.get().strip()

            if not u or not p or not c:
                messagebox.showerror("Error", "All fields are required.", parent=dialog)
                return

            # Use centralized validation for username and password
            is_valid, error_msg = validate_credentials(u, p)
            if not is_valid:
                messagebox.showerror("Error", error_msg, parent=dialog)
                return

            if p != c:
                messagebox.showerror("Error", "Passwords do not match.", parent=dialog)
                return

            success, msg = register_user(u, p)
            if success:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        DesignUtils.create_styled_button(dialog_frame, "Register", submit, style='Primary.TButton').pack(pady=Spacing.MD)

        # Accessibility: Focus management
        username_entry.focus_set()
        username_entry.bind("<Return>", lambda e: password_entry.focus_set())
        password_entry.bind("<Return>", lambda e: confirm_entry.focus_set())
        confirm_entry.bind("<Return>", lambda e: submit())

    def set_waiting(self, waiting: bool):
        state = "disabled" if waiting else "normal"
        self.login_btn.config(state=state)
        self.new_user_btn.config(state=state)
        self.username_entry.config(state=state)
        self.password_entry.config(state=state)
        if waiting and not self.progress_shown:
            self.progress.pack(pady=(10, 0))
            self.progress.start(10)
            self.progress_shown = True
        elif not waiting and self.progress_shown:
            self.progress.stop()
            self.progress.pack_forget()
            self.progress_shown = False
            self.username_entry.focus_set()
