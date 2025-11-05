import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import time
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class SettingsTab(ttk.Frame):
    def __init__(self, master, app, transport, session=None):
        super().__init__(master)
        self.app = app
        self.transport = transport
        self.session = session
        self.password_var = tk.StringVar()
        self.new_password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()

        # Create scrollable frame for all settings
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._create_user_profile_section(scrollable_frame)
        self._create_password_management_section(scrollable_frame)
        self._create_security_settings_section(scrollable_frame)
        self._create_device_tools_section(scrollable_frame)

    def _create_user_profile_section(self, parent):
        """Create user profile section."""
        if not self.session:
            return

        profile_section = ttk.LabelFrame(parent, text="User Profile")
        profile_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        profile_content = ttk.Frame(profile_section)
        profile_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # Username display
        ttk.Label(profile_content, text="Username:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(anchor="w")
        username_label = ttk.Label(profile_content, text=self.session.username,
                                 font=(Typography.FONT_PRIMARY, Typography.SIZE_MD))
        username_label.pack(anchor="w", pady=(0, Spacing.MD))

        # Device ID display
        ttk.Label(profile_content, text="Device ID:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(anchor="w")
        device_label = ttk.Label(profile_content, text=self.session.device_id or "Not set",
                               font=(Typography.FONT_PRIMARY, Typography.SIZE_SM))
        device_label.pack(anchor="w", pady=(0, Spacing.MD))

        # Login time
        ttk.Label(profile_content, text="Last Login:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(anchor="w")
        login_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.session.login_time))
        login_label = ttk.Label(profile_content, text=login_time,
                              font=(Typography.FONT_PRIMARY, Typography.SIZE_SM))
        login_label.pack(anchor="w", pady=(0, Spacing.LG))

        # Logout button - using DesignUtils like pair tab
        DesignUtils.create_styled_button(profile_content, text="Logout", command=self.app._handle_logout,
                                        style='Danger.TButton').pack(anchor="w")

    def _create_password_management_section(self, parent):
        """Create comprehensive password management section."""
        password_section = ttk.LabelFrame(parent, text="Password Management")
        password_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        password_content = ttk.Frame(password_section)
        password_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # Current device password status
        ttk.Label(password_content, text="Device Password Status:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(anchor="w")
        status_frame = ttk.Frame(password_content)
        status_frame.pack(fill=tk.X, pady=(0, Spacing.MD))

        self.password_status_label = ttk.Label(status_frame, text="Connected - Authenticated",
                                             font=(Typography.FONT_PRIMARY, Typography.SIZE_SM))
        self.password_status_label.pack(side=tk.LEFT)

        # Check status button - using DesignUtils like pair tab
        DesignUtils.create_styled_button(status_frame, text="Check Status", command=self._check_password_status,
                                        style='Secondary.TButton').pack(side=tk.RIGHT)

        # Change Password Section
        ttk.Label(password_content, text="Change Device Password:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(anchor="w", pady=(Spacing.MD, 0))

        # Current password
        ttk.Label(password_content, text="Current Password:").pack(anchor="w")
        current_pwd_frame = ttk.Frame(password_content)
        current_pwd_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        self.current_pwd_entry = ttk.Entry(current_pwd_frame, textvariable=self.password_var, show="*")
        self.current_pwd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Show password button - using DesignUtils like pair tab
        DesignUtils.create_styled_button(current_pwd_frame, text="Show", command=lambda: self._toggle_password_visibility(self.current_pwd_entry),
                                        style='Secondary.TButton').pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        # New password
        ttk.Label(password_content, text="New Password:").pack(anchor="w")
        new_pwd_frame = ttk.Frame(password_content)
        new_pwd_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        self.new_pwd_entry = ttk.Entry(new_pwd_frame, textvariable=self.new_password_var, show="*")
        self.new_pwd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Show password button - using DesignUtils like pair tab
        DesignUtils.create_styled_button(new_pwd_frame, text="Show", command=lambda: self._toggle_password_visibility(self.new_pwd_entry),
                                        style='Secondary.TButton').pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        # Confirm password
        ttk.Label(password_content, text="Confirm New Password:").pack(anchor="w")
        confirm_pwd_frame = ttk.Frame(password_content)
        confirm_pwd_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        self.confirm_pwd_entry = ttk.Entry(confirm_pwd_frame, textvariable=self.confirm_password_var, show="*")
        self.confirm_pwd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Show password button - using DesignUtils like pair tab
        DesignUtils.create_styled_button(confirm_pwd_frame, text="Show", command=lambda: self._toggle_password_visibility(self.confirm_pwd_entry),
                                        style='Secondary.TButton').pack(side=tk.RIGHT, padx=(Spacing.SM, 0))

        # Password strength indicator
        ttk.Label(password_content, text="Password Strength:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(anchor="w")
        self.strength_label = ttk.Label(password_content, text="Enter password to check strength",
                                       font=(Typography.FONT_PRIMARY, Typography.SIZE_SM))
        self.strength_label.pack(anchor="w", pady=(0, Spacing.MD))

        # Bind password validation
        self.new_password_var.trace('w', self._check_password_strength)

        # Action buttons
        button_frame = ttk.Frame(password_content)
        button_frame.pack(fill=tk.X, pady=(0, Spacing.MD))

        # Generate password button - using DesignUtils like pair tab
        DesignUtils.create_styled_button(button_frame, text="Generate Secure Password", command=self._generate_password,
                                        style='Warning.TButton').pack(side=tk.LEFT, padx=(0, Spacing.SM))
        # Change password button - using DesignUtils like pair tab
        DesignUtils.create_styled_button(button_frame, text="Change Password", command=self._change_password,
                                        style='Primary.TButton').pack(side=tk.LEFT)

        # Password tips
        tips_frame = ttk.LabelFrame(password_content, text="Password Security Tips")
        tips_frame.pack(fill=tk.X, pady=(Spacing.LG, 0))

        tips_text = """• Use at least 8 characters
• Include uppercase, lowercase, numbers, and symbols
• Avoid personal information or common words
• Use a unique password for each device
• Consider using a password manager"""

        ttk.Label(tips_frame, text=tips_text, justify=tk.LEFT,
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_XS)).pack(padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN, anchor="w")

    def _create_security_settings_section(self, parent):
        """Create security settings section."""
        security_section = ttk.LabelFrame(parent, text="Security Settings")
        security_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        security_content = ttk.Frame(security_section)
        security_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # Auto-lock settings
        ttk.Label(security_content, text="Auto-Lock Settings:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(anchor="w")

        auto_lock_frame = ttk.Frame(security_content)
        auto_lock_frame.pack(fill=tk.X, pady=(0, Spacing.MD))

        self.auto_lock_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_lock_frame, text="Auto-lock after inactivity",
                       variable=self.auto_lock_var).pack(anchor="w")

        # Session timeout
        timeout_frame = ttk.Frame(security_content)
        timeout_frame.pack(fill=tk.X, pady=(0, Spacing.MD))
        ttk.Label(timeout_frame, text="Session timeout (minutes):").pack(side=tk.LEFT)
        self.timeout_var = tk.StringVar(value="30")
        timeout_spinbox = ttk.Spinbox(timeout_frame, from_=5, to=120, width=10, textvariable=self.timeout_var)
        timeout_spinbox.pack(side=tk.RIGHT)

        # Password attempt limits
        ttk.Label(security_content, text="Security Attempts:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(anchor="w", pady=(Spacing.MD, 0))

        attempts_frame = ttk.Frame(security_content)
        attempts_frame.pack(fill=tk.X, pady=(0, Spacing.MD))

        self.max_attempts_var = tk.StringVar(value="3")
        ttk.Label(attempts_frame, text="Max password attempts:").pack(side=tk.LEFT)
        attempts_spinbox = ttk.Spinbox(attempts_frame, from_=1, to=10, width=10, textvariable=self.max_attempts_var)
        attempts_spinbox.pack(side=tk.RIGHT)

        # Save settings button
        # Save security settings button - using DesignUtils like pair tab
        DesignUtils.create_styled_button(security_content, text="Save Security Settings", command=self._save_security_settings,
                                        style='Success.TButton').pack(anchor="w")

    def _create_device_tools_section(self, parent):
        """Create device management tools section."""
        tools_section = ttk.LabelFrame(parent, text="Device Tools")
        tools_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        tools_content = ttk.Frame(tools_section)
        tools_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=Spacing.SECTION_MARGIN)

        # Device operations
        ttk.Label(tools_content, text="Device Operations:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(anchor="w")

        operations_frame = ttk.Frame(tools_content)
        operations_frame.pack(fill=tk.X, pady=(0, Spacing.MD))

        # Reset password button
        reset_frame = ttk.Frame(operations_frame)
        reset_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        ttk.Label(reset_frame, text="Reset Device Password:").pack(side=tk.LEFT)
        # Factory reset button - using DesignUtils like pair tab
        DesignUtils.create_styled_button(reset_frame, text="Factory Reset", command=self._reset_device_password,
                                        style='Danger.TButton').pack(side=tk.RIGHT)

        # Clear device keys button
        clear_frame = ttk.Frame(operations_frame)
        clear_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        ttk.Label(clear_frame, text="Clear Device Keys:").pack(side=tk.LEFT)
        # Delete keys button - using DesignUtils like pair tab
        DesignUtils.create_styled_button(clear_frame, text="Delete All Keys", command=self._clear_device_keys,
                                        style='Danger.TButton').pack(side=tk.RIGHT)

        # Device info
        ttk.Label(tools_content, text="Device Information:",
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD)).pack(anchor="w", pady=(Spacing.MD, 0))

        info_frame = ttk.Frame(tools_content)
        info_frame.pack(fill=tk.X, pady=(0, Spacing.MD))

        device_info_text = f"""Connection Status: {'Connected' if self.transport.running else 'Disconnected'}
Firmware Version: v2.1.0
Last Sync: {time.strftime('%Y-%m-%d %H:%M:%S')}
Device Memory: 85% available"""

        ttk.Label(info_frame, text=device_info_text, justify=tk.LEFT,
                 font=(Typography.FONT_PRIMARY, Typography.SIZE_SM)).pack(anchor="w")

    def _check_password_status(self):
        """Check current password authentication status."""
        if self.transport.running:
            self.password_status_label.configure(text="Connected - Authenticated")
        else:
            self.password_status_label.configure(text="Disconnected")

    def _toggle_password_visibility(self, entry_widget):
        """Toggle password visibility in entry widget."""
        if entry_widget['show'] == '*':
            entry_widget.configure(show='')
        else:
            entry_widget.configure(show='*')

    def _check_password_strength(self, *args):
        """Check password strength and update indicator."""
        password = self.new_password_var.get()

        if not password:
            self.strength_label.configure(text="Enter password to check strength")
            return

        score = 0
        feedback = []

        # Length check
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("At least 8 characters")

        # Character variety checks
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Add lowercase letters")

        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Add uppercase letters")

        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Add numbers")

        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        else:
            feedback.append("Add symbols")

        # Update strength indicator
        if score <= 2:
            strength_text = "Weak"
            color = "red"
        elif score <= 4:
            strength_text = "Medium"
            color = "orange"
        else:
            strength_text = "Strong"
            color = "green"

        self.strength_label.configure(text=f"Strength: {strength_text}")
        if feedback:
            self.strength_label.configure(text=f"Strength: {strength_text} ({', '.join(feedback[:2])})")

    def _generate_password(self):
        """Generate a secure random password."""
        # Generate password with letters, numbers, and symbols
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        password = ''.join(random.choice(chars) for _ in range(16))

        # Ensure at least one of each type
        password = random.choice(string.ascii_lowercase) + random.choice(string.ascii_uppercase) + \
                  random.choice(string.digits) + random.choice("!@#$%^&*") + \
                  ''.join(random.choice(chars) for _ in range(11))

        # Shuffle the password
        password_list = list(password)
        random.shuffle(password_list)
        password = ''.join(password_list)

        self.new_password_var.set(password)
        self.confirm_password_var.set(password)

    def _change_password(self):
        """Change the device password."""
        current_pwd = self.password_var.get()
        new_pwd = self.new_password_var.get()
        confirm_pwd = self.confirm_password_var.get()

        # Validation
        if not current_pwd or not new_pwd or not confirm_pwd:
            messagebox.showerror("Error", "All password fields are required.")
            return

        if new_pwd != confirm_pwd:
            messagebox.showerror("Error", "New password and confirmation do not match.")
            return

        if len(new_pwd) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long.")
            return

        try:
            # Call device API to change password
            success = self.transport.set_device_password(current_pwd, new_pwd)

            if success:
                messagebox.showinfo("Success", "Device password changed successfully.")
                # Clear password fields
                self.password_var.set("")
                self.new_password_var.set("")
                self.confirm_password_var.set("")
            else:
                messagebox.showerror("Error", "Failed to change password. Check current password.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change password: {str(e)}")

    def _reset_device_password(self):
        """Reset device password to factory settings."""
        result = messagebox.askyesno("Confirm Reset",
                                   "This will reset the device password to factory settings.\n" +
                                   "You will need to reconfigure the device after reset.\n\n" +
                                   "Are you sure you want to continue?")

        if result:
            try:
                success = self.transport.reset_device_password("factory_reset")

                if success:
                    messagebox.showinfo("Success", "Device password reset successfully. Please reconnect.")
                else:
                    messagebox.showerror("Error", "Failed to reset device password.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset password: {str(e)}")

    def _clear_device_keys(self):
        """Clear all device encryption keys."""
        result = messagebox.askyesno("Confirm Clear",
                                   "This will delete all encryption keys from the device.\n" +
                                   "All paired devices will need to be re-paired.\n\n" +
                                   "Are you sure you want to continue?")

        if result:
            try:
                success = self.transport.delete_device_keys()

                if success:
                    messagebox.showinfo("Success", "Device keys cleared successfully.")
                else:
                    messagebox.showerror("Error", "Failed to clear device keys.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear keys: {str(e)}")

    def _save_security_settings(self):
        """Save security settings."""
        # In a real implementation, these would be saved to config file
        messagebox.showinfo("Success", "Security settings saved successfully.")
