"""
Chatroom Pairing Frame - Similar to PINPairingFrame but for 20-digit chatroom code.
Creates a modal dialog interface for entering chatroom pairing codes.
"""
import tkinter as tk
from typing import Callable, Optional
from tkinter import messagebox

from utils.design_system import AppConfig, Colors, Typography, Spacing, DesignUtils, Space
from utils.state.status_manager import get_status_manager


class ChatroomPairingFrame(tk.Frame):
    """Chatroom pairing interface for 20-digit codes."""

    def __init__(self, master, on_chatroom_success: Callable[[str], None]):
        super().__init__(master, bg=Colors.SURFACE)
        self.on_chatroom_success = on_chatroom_success
        self.chatroom_vars: list[tk.StringVar] = []
        self.chatroom_entries: list[tk.Entry] = []

        self._create_ui()

    def _create_ui(self):
        """Create the chatroom pairing interface."""
        content = tk.Frame(self, bg=Colors.SURFACE, padx=Spacing.SM, pady=Spacing.SM)
        content.pack(fill=tk.BOTH, expand=True)

        header_frame = tk.Frame(content, bg=Colors.SURFACE)
        header_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        self.title_label = tk.Label(
            header_frame,
            text="Enter Chatroom",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            font=(Typography.FONT_UI, Typography.SIZE_24, Typography.WEIGHT_BOLD),
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            header_frame,
            text="Enter the 20-digit chatroom code.",
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            font=(Typography.FONT_UI, Typography.SIZE_14, Typography.WEIGHT_REGULAR),
        )
        self.subtitle_label.pack(anchor="w", pady=(Spacing.XXS, Spacing.SM))

        inputs_row = tk.Frame(content, bg=Colors.SURFACE, padx=Spacing.SM, pady=Spacing.SM)
        inputs_row.pack(fill=tk.X, pady=(0, Spacing.SM))
        self._build_chatroom_inputs(inputs_row)

        button_frame = tk.Frame(content, bg=Colors.SURFACE)
        button_frame.pack(fill=tk.X, pady=(Spacing.SM, 0))

        self.clear_btn = DesignUtils.button(
            button_frame,
            text="Clear",
            command=self._clear_chatroom_code,
            variant="secondary",
        )
        self.clear_btn.pack(fill=tk.X, pady=(0, Spacing.XXS))

        self.enter_btn = DesignUtils.button(
            button_frame,
            text="Enter Chatroom",
            command=self._on_submit_chatroom_code,
            variant="primary",
        )
        self.enter_btn.pack(fill=tk.X, pady=(0, Spacing.XXS))

        

        # Set initial focus after widgets are laid out
        self.after(100, self.focus_input)

    def focus_input(self):
        """Focus the first chatroom input box."""
        if self.chatroom_entries:
            self._focus_box(0)

    def _build_chatroom_inputs(self, parent: tk.Frame):
        """Build 20-digit chatroom input as 2 rows of 10 digits each with visual separator."""
        self.chatroom_vars.clear()
        self.chatroom_entries.clear()
        
        # Create 2 rows of 10 digits each with visual separator after 5th digit
        for row_idx in range(2):
            row_frame = tk.Frame(parent, bg=Colors.SURFACE)
            row_frame.pack(fill=tk.X, pady=Spacing.XXS)  # Spacing between rows
            
            for digit_idx in range(10):
                var = tk.StringVar()
                entry = DesignUtils.create_pin_entry(
                    row_frame,
                    textvariable=var,
                    justify="center",
                    width=2,  # Reduced from 3 to 2 (33% reduction, rounded to practical minimum)
                    font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_BOLD),  # Reduced from SIZE_14 to SIZE_10
                )
                entry.pack(side=tk.LEFT, padx=1, pady=0)  # Reduced padding from (2,1) to (1,0)
                
                # Add visual separator after 5th box in each row
                if digit_idx == 4:
                    separator = tk.Label(
                        row_frame,
                        text="–",
                        bg=Colors.SURFACE,
                        fg=Colors.TEXT_MUTED,
                        font=(Typography.FONT_UI, Typography.SIZE_10, Typography.WEIGHT_BOLD)  # Reduced from SIZE_14 to SIZE_10
                    )
                    separator.pack(side=tk.LEFT, padx=(2, 1), pady=0)  # Reduced padding from (4,2,1) to (2,1,0)
                
                # Calculate global index for proper navigation
                global_index = row_idx * 10 + digit_idx
                
                entry.bind("<KeyRelease>", lambda e, i=global_index: self._handle_digit_key(e, i))
                entry.bind("<KeyPress>", lambda e, i=global_index: self._handle_digit_press(e, i))
                entry.bind("<Return>", self._on_submit_chatroom_code)
                
                self.chatroom_vars.append(var)
                self.chatroom_entries.append(entry)

    def _handle_digit_press(self, event, index: int):
        """Handle key press events for navigation."""
        if event.keysym == "Left" and index > 0:
            self._focus_box(index - 1)
            return "break"
        if event.keysym == "Right" and index < len(self.chatroom_entries) - 1:
            self._focus_box(index + 1)
            return "break"
        if event.keysym == "Up" and index >= 10:
            # Move to same column in previous row
            self._focus_box(index - 10)
            return "break"
        if event.keysym == "Down" and index < 10:
            # Move to same column in next row
            self._focus_box(index + 10)
            return "break"
        return None

    def _handle_digit_key(self, event, index: int):
        """Handle digit entry and auto-navigation."""
        if not self.chatroom_entries:
            return
        
        value = self.chatroom_vars[index].get()
        keys_to_ignore = {"Shift_L", "Shift_R", "Tab"}
        if event.keysym in keys_to_ignore:
            return

        if event.keysym == "BackSpace":
            if value:
                self.chatroom_vars[index].set("")
            elif index > 0:
                self.chatroom_vars[index - 1].set("")
                self._focus_box(index - 1)
            # Update button state
            self._update_enter_button_state()
            return

        if len(value) > 1:
            self._apply_paste(value, index)
            return

        if not value:
            return

        if not value.isalnum():
            self.chatroom_vars[index].set("")
            return

        self.chatroom_vars[index].set(value)
        
        # Auto-advance to next field (handle wrap-around between rows)
        if index < len(self.chatroom_entries) - 1:
            if index == 9:  # End of first row, move to start of second row
                self._focus_box(10)
            else:
                self._focus_box(index + 1)
        # Update button state
        self._update_enter_button_state()

    def _apply_paste(self, text: str, start_index: int):
        """Handle paste operation with digits only."""
        digits = [c for c in text if c.isalnum()]
        if not digits:
            self.chatroom_vars[start_index].set("")
            return
        idx = start_index
        for digit in digits:
            if idx >= len(self.chatroom_entries):
                break
            self.chatroom_vars[idx].set(digit)
            idx += 1
        if idx < len(self.chatroom_entries):
            self._focus_box(idx)
        else:
            self.chatroom_entries[-1].focus_set()
        
        # Update button state after paste
        self._update_enter_button_state()

    def _collect_chatroom_code(self) -> str:
        """Collect all entered digits into a single 20-digit code."""
        return "".join(var.get() for var in self.chatroom_vars)

    def _focus_box(self, index: int):
        """Focus the specified input box."""
        entry = self.chatroom_entries[index]
        entry.focus_set()
        entry.icursor(tk.END)

    def _update_enter_button_state(self):
        """Update the Enter button state based on whether all 20 digits are entered."""
        chatroom_code = self._collect_chatroom_code().strip()
        if len(chatroom_code) == 20:
            self.enter_btn.configure(state="normal")
        else:
            self.enter_btn.configure(state="disabled")

    def _on_submit_chatroom_code(self, event=None):
        """Handle chatroom code submission."""
        chatroom_code = self._collect_chatroom_code().strip()
        get_status_manager().update_status(AppConfig.STATUS_AWAITING_PEER)
        
        if len(chatroom_code) != 20:
            self._show_error("Please enter all 20 digits")
            return
        
        # For now, bypass validation and proceed directly
        # In the future, this could validate against a server
        self._set_waiting(True)
        
        # Simulate processing delay
        self.after(1000, lambda: self._on_chatroom_success(chatroom_code))

    def _on_chatroom_success(self, chatroom_code):
        """Handle successful chatroom code entry."""
        self._set_waiting(False)
        
        if self.on_chatroom_success:
            self.on_chatroom_success(chatroom_code)
            get_status_manager().update_status(AppConfig.STATUS_READY)

    

    def _clear_chatroom_code(self):
        """Clear all entered digits."""
        for var in self.chatroom_vars:
            var.set("")
        # Update button state after clearing
        self._update_enter_button_state()
        # Focus back to first input
        self.focus_input()

    def _show_error(self, message):
        """Show error message."""
        get_status_manager().update_status(AppConfig.STATUS_CONNECTION_FAILED)
        messagebox.showerror("Chatroom Entry Failed", message)

    def _set_waiting(self, waiting):
        """Set waiting state for UI elements."""
        if waiting:
            self.enter_btn.configure(state="disabled", text="Entering...")
            for entry in self.chatroom_entries:
                entry.configure(state="disabled")
        else:
            self.enter_btn.configure(state="normal", text="Enter Chatroom")
            for entry in self.chatroom_entries:
                entry.configure(state="normal")
            self.focus_input()
