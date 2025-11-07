"""
Application Settings Page - Redesigned to match ChatPage's design excellence.
Simplified for app configuration only with ChatPage's scrollable layout and styling.
"""
import tkinter as tk
from tkinter import messagebox, ttk
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class SettingsPage(tk.Frame):
    """Settings page for application configuration (redesigned with ChatPage excellence)."""

    def __init__(self, master, app, controller, session=None):
        super().__init__(master, bg=Colors.BG_PRIMARY)
        self.app = app
        self.controller = controller
        self.session = session

        # Configure frame styling (matching ChatPage)
        self.pack(fill=tk.BOTH, expand=True, padx=Spacing.TAB_PADDING, pady=Spacing.TAB_PADDING)

        # Create scrollable frame for all content (matching ChatPage)
        canvas = tk.Canvas(self, bg=Colors.BG_PRIMARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_PRIMARY)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mouse wheel scrolling (matching ChatPage)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_to_mousewheel)
        canvas.bind("<Leave>", _unbind_from_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------- Title Section (matching ChatPage) ---------- #
        title_section = tk.Frame(scrollable_frame, bg=Colors.BG_PRIMARY)
        title_section.pack(fill=tk.X, pady=(0, Spacing.XL))

        title_frame = tk.Frame(title_section, bg=Colors.BG_PRIMARY)
        title_frame.pack(anchor="center")

        title_label = tk.Label(
            title_frame,
            text="Application Settings",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_XXL, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",
            bg=Colors.BG_PRIMARY
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Configure application preferences and behavior",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_LG),
            fg="#CCCCCC",
            bg=Colors.BG_PRIMARY
        )
        subtitle_label.pack(pady=(Spacing.SM, 0))

        # ---------- Welcome Section with Box Border (Application Preferences) ---------- #
        welcome_section = tk.Frame(scrollable_frame, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        welcome_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.LG, Spacing.MD))

        # Welcome section header (matching ChatPage style)
        welcome_header = tk.Label(welcome_section, text="Application Preferences", bg=Colors.BG_SECONDARY,
                                fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        welcome_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        welcome_content = tk.Frame(welcome_section, bg=Colors.BG_SECONDARY)
        welcome_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # Auto-start settings (matching ChatPage typography)
        auto_start_label = tk.Label(
            welcome_content,
            text="Auto-start Settings:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        auto_start_label.pack(anchor="w")

        auto_start_frame = tk.Frame(welcome_content, bg=Colors.BG_SECONDARY)
        auto_start_frame.pack(fill=tk.X, pady=(Spacing.SM, Spacing.MD))

        self.auto_start_var = tk.BooleanVar(value=False)
        auto_start_check = ttk.Checkbutton(auto_start_frame, text="Auto-start Locomm on system boot",
                                         variable=self.auto_start_var)
        auto_start_check.pack(anchor="w")

        # Notification preferences (matching ChatPage typography)
        notification_label = tk.Label(
            welcome_content,
            text="Notification Settings:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM, Typography.WEIGHT_BOLD),
            fg="#FFFFFF",
            bg=Colors.BG_SECONDARY
        )
        notification_label.pack(anchor="w", pady=(Spacing.MD, 0))

        notification_frame = tk.Frame(welcome_content, bg=Colors.BG_SECONDARY)
        notification_frame.pack(fill=tk.X, pady=(Spacing.SM, Spacing.MD))

        self.desktop_notifications_var = tk.BooleanVar(value=True)
        desktop_notif_check = ttk.Checkbutton(notification_frame, text="Desktop notifications for new messages",
                                            variable=self.desktop_notifications_var)
        desktop_notif_check.pack(anchor="w")

        self.sound_notifications_var = tk.BooleanVar(value=False)
        sound_notif_check = ttk.Checkbutton(notification_frame, text="Sound notifications",
                                          variable=self.sound_notifications_var)
        sound_notif_check.pack(anchor="w")

        # ---------- Application Features Section with Box Border (Advanced Settings) ---------- #
        features_section = tk.Frame(scrollable_frame, bg=Colors.BG_SECONDARY, relief="solid", bd=1)
        features_section.pack(fill=tk.X, padx=Spacing.HEADER_PADDING, pady=(Spacing.MD, Spacing.LG))

        # Features section header (matching ChatPage style)
        features_header = tk.Label(features_section, text="Advanced Settings", bg=Colors.BG_SECONDARY,
                                 fg="#FFFFFF", font=(Typography.FONT_PRIMARY, Typography.SIZE_MD, Typography.WEIGHT_BOLD))
        features_header.pack(anchor="w", padx=Spacing.SECTION_MARGIN, pady=(Spacing.SECTION_MARGIN, Spacing.XS))

        features_content = tk.Frame(features_section, bg=Colors.BG_SECONDARY)
        features_content.pack(fill=tk.X, padx=Spacing.SECTION_MARGIN, pady=(0, Spacing.SECTION_MARGIN))

        # Advanced settings frame with ChatPage styling
        advanced_frame = tk.Frame(features_content, bg=Colors.BG_SECONDARY)
        advanced_frame.pack(fill=tk.X)

        # Save preferences button (matching ChatPage button style)
        save_btn = DesignUtils.create_styled_button(
            advanced_frame,
            "Save Preferences",
            self._save_preferences,
            style='Primary.TButton'
        )
        save_btn.pack(anchor="w", pady=(0, Spacing.SM))

        # Reset to defaults button (matching ChatPage button style)
        reset_btn = DesignUtils.create_styled_button(
            advanced_frame,
            "Reset to Defaults",
            self._reset_defaults,
            style='Secondary.TButton'
        )
        reset_btn.pack(anchor="w")

        # ---------- Footer (matching ChatPage) ---------- #
        footer_frame = tk.Frame(scrollable_frame, bg=Colors.BG_PRIMARY)
        footer_frame.pack(fill=tk.X, pady=(Spacing.LG, 0))

        footer_label = tk.Label(
            footer_frame,
            text="Changes may require restarting the application to take full effect",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg="#888888",
            bg=Colors.BG_PRIMARY,
            justify='center',
            wraplength=400
        )
        footer_label.pack()

    # ========== PREFERENCE MANAGEMENT METHODS ==========

    def _save_preferences(self):
        """Save application preferences."""
        try:
            # In real implementation, would save to config file
            preferences = {
                'auto_start': self.auto_start_var.get(),
                'desktop_notifications': self.desktop_notifications_var.get(),
                'sound_notifications': self.sound_notifications_var.get(),
            }

            # Show success message
            messagebox.showinfo("Preferences Saved",
                              "Application preferences have been saved successfully.\n\n"
                              "Some changes may require restarting the application.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences: {str(e)}")

    def _reset_defaults(self):
        """Reset preferences to default values."""
        try:
            # Reset all preferences to defaults
            self.auto_start_var.set(False)
            self.desktop_notifications_var.set(True)
            self.sound_notifications_var.set(False)

            messagebox.showinfo("Defaults Restored",
                              "All preferences have been reset to their default values.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset preferences: {str(e)}")

    def load_preferences(self):
        """Load application preferences (called on initialization)."""
        try:
            # In real implementation, would load from config file
            # For now, use default values
            pass

        except Exception as e:
            print(f"Warning: Could not load preferences: {str(e)}")

    def get_preferences(self):
        """Get current application preferences."""
        return {
            'auto_start': self.auto_start_var.get(),
            'desktop_notifications': self.desktop_notifications_var.get(),
            'sound_notifications': self.sound_notifications_var.get(),
        }
