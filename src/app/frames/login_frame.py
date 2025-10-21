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
    def __init__(self, master, on_login):
        super().__init__(master)
        self.on_login = on_login

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        ttk.Label(self, text="LoRa Chat Login", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))

        frame_u = ttk.Frame(self)
        frame_u.pack(pady=5)
        ttk.Label(frame_u, text="Username:").pack(side=tk.LEFT, padx=5)
        entry_u = ttk.Entry(frame_u, textvariable=self.username_var, width=30)
        entry_u.pack(side=tk.LEFT)

        frame_p = ttk.Frame(self)
        frame_p.pack(pady=5)
        ttk.Label(frame_p, text="Password:").pack(side=tk.LEFT, padx=5)
        entry_p = ttk.Entry(frame_p, textvariable=self.password_var, show="•", width=30)
        entry_p.pack(side=tk.LEFT)

        entry_u.bind("<Return>", lambda e: self._try_login())
        entry_p.bind("<Return>", lambda e: self._try_login())

        # Buttons frame
        btns = ttk.Frame(self)
        btns.pack(pady=(15, 10))

        ttk.Button(btns, text="Login", command=self._try_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="New User", command=self._new_user_dialog).pack(side=tk.LEFT, padx=5)

        # Enforce ASCII limit
        self.username_var.trace_add("write", lambda *_: enforce_ascii_and_limit(self.username_var))
        self.password_var.trace_add("write", lambda *_: enforce_ascii_and_limit(self.password_var))

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
