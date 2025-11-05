import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from utils.user_store import register_user, validate_login

MAX_CRED_LEN = 32
ASCII_RANGE = set(range(0x20, 0x7F))


def is_printable_ascii(s: str) -> bool:
    return all(ord(c) in ASCII_RANGE for c in s)


def enforce_ascii_and_limit(var: tk.StringVar):
    val = var.get()
    filtered = ''.join(c for c in val if ord(c) in ASCII_RANGE)[:MAX_CRED_LEN]
    if filtered != val:
        var.set(filtered)


class LoginFrame(ttk.Frame):
    def __init__(self, master, on_login, app):
        super().__init__(master)
        self.configure(style="Surface.TFrame")
        self.on_login = on_login
        self.app = app

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.card = ttk.Frame(self, style="SurfaceAlt.TFrame", padding=(32, 28, 32, 32))
        self.card.grid(row=0, column=0, sticky="nsew", padx=48, pady=48)

        ttk.Label(self.card, text="LoComm Desktop", style="HeadlineAlt.TLabel").pack(anchor="w")
        ttk.Label(
            self.card,
            text="Sign in to secure your LoRa chat session.",
            style="BodyAlt.TLabel"
        ).pack(anchor="w", pady=(6, 18))

        username_block = ttk.Frame(self.card, style="SurfaceAlt.TFrame")
        username_block.pack(fill=tk.X, pady=(0, 14))
        ttk.Label(username_block, text="Username", style="SectionAlt.TLabel").pack(anchor="w")
        entry_u = tk.Entry(username_block, textvariable=self.username_var)
        entry_u.pack(fill=tk.X, pady=(6, 0))
        self.username_entry = entry_u

        password_block = ttk.Frame(self.card, style="SurfaceAlt.TFrame")
        password_block.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(password_block, text="Password", style="SectionAlt.TLabel").pack(anchor="w")
        entry_p = tk.Entry(password_block, textvariable=self.password_var, show="•")
        entry_p.pack(fill=tk.X, pady=(6, 0))
        self.password_entry = entry_p

        entry_u.bind("<Return>", lambda e: self._try_login())
        entry_p.bind("<Return>", lambda e: self._try_login())

        btns = ttk.Frame(self.card, style="SurfaceAlt.TFrame")
        btns.pack(fill=tk.X, pady=(16, 4))

        self.login_btn = ttk.Button(btns, text="Log In", style="Accent.TButton", command=self._try_login)
        self.login_btn.pack(fill=tk.X)

        self.new_user_btn = ttk.Button(
            self.card,
            text="Create new account",
            style="Secondary.TButton",
            command=self._new_user_dialog,
        )
        self.new_user_btn.pack(fill=tk.X, pady=(8, 0))

        self.progress = ttk.Progressbar(self.card, mode="indeterminate", length=220, style="Accent.Horizontal.TProgressbar")
        self.progress_shown = False

        # Enforce ASCII limit
        self.username_var.trace_add("write", lambda *_: enforce_ascii_and_limit(self.username_var))
        self.password_var.trace_add("write", lambda *_: enforce_ascii_and_limit(self.password_var))

        self.app.register_theme_listener(self.apply_theme)
        self.apply_theme()

    def _try_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Username and password required.")
            return
        if not (is_printable_ascii(username) and is_printable_ascii(password)):
            messagebox.showerror("Error", "Only printable ASCII allowed.")
            return

        # ✅ Validate from user store
        if not validate_login(username, password):
            messagebox.showerror("Login Failed", "Incorrect username or password.")
            return

        self.set_waiting(True)
        self.on_login(username, bytearray(password, "utf-8"))

    def _new_user_dialog(self):
        """Opens a modal dialog to register a new user."""
        dialog = tk.Toplevel(self)
        dialog.title("New User Registration")
        dialog.geometry("300x300")
        dialog.grab_set()  # modal window

        tk.Label(dialog, text="Create a New Account", font=("Segoe UI", 12, "bold")).pack(pady=10)

        tk.Label(dialog, text="Username:").pack(anchor="w", padx=15)
        username_var = tk.StringVar()
        tk.Entry(dialog, textvariable=username_var).pack(padx=15, fill=tk.X)

        tk.Label(dialog, text="Password:").pack(anchor="w", padx=15, pady=(8, 0))
        password_var = tk.StringVar()
        tk.Entry(dialog, textvariable=password_var, show="•").pack(padx=15, fill=tk.X)

        tk.Label(dialog, text="Retype Password:").pack(anchor="w", padx=15, pady=(8, 0))
        confirm_var = tk.StringVar()
        tk.Entry(dialog, textvariable=confirm_var, show="•").pack(padx=15, fill=tk.X)

        def submit():
            u = username_var.get().strip()
            p = password_var.get().strip()
            c = confirm_var.get().strip()

            if not u or not p or not c:
                messagebox.showerror("Error", "All fields are required.", parent=dialog)
                return
            if not (is_printable_ascii(u) and is_printable_ascii(p)):
                messagebox.showerror("Error", "Only printable ASCII allowed.", parent=dialog)
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

        tk.Button(dialog, text="Register", command=submit, bg="#66CCFF", fg="black").pack(pady=15)

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

    def apply_theme(self):
        colors = self.app.get_theme_colors()
        self.configure(style="Surface.TFrame")
        self.card.configure(style="SurfaceAlt.TFrame")
        self.login_btn.configure(style="Accent.TButton")
        self.new_user_btn.configure(style="Secondary.TButton")
        self.progress.configure(style="Accent.Horizontal.TProgressbar")
        for entry in (self.username_entry, self.password_entry):
            entry.configure(
                bg=colors["input_bg"],
                fg=colors["input_fg"],
                insertbackground=colors["input_fg"],
                font=self.app.get_font("base"),
                highlightthickness=1,
                highlightbackground=colors["border"],
                highlightcolor=colors["accent"],
                relief="flat",
                bd=0,
            )
