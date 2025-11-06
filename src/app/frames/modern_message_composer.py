"""Modern message composer with rich text support, emoji picker, and advanced features."""
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from typing import Optional, Callable, List
import re
from datetime import datetime
from .chat_models import ChatMessage, MessageType, MessageStatus
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class EmojiPicker(ttk.Frame):
    """Modern emoji picker with categories and search."""

    def __init__(self, master, on_emoji_select: Callable[[str], None]):
        super().__init__(master)
        self.on_emoji_select = on_emoji_select
        self.categories = {
            "😀": ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇"],
            "😍": ["😍", "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪"],
            "🤗": ["🤗", "🤭", "🤫", "🤔", "🤐", "🤨", "😐", "😑", "😶", "😏"],
            "😢": ["😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥵", "🥶"],
            "👍": ["👍", "👎", "👌", "✨", "🎉", "❤️", "💯", "🔥", "💯", "👀"],
            "🚀": ["🚀", "💡", "⭐", "🌟", "💫", "🎯", "✅", "❌", "⚡", "🎵"]
        }
        self.current_category = "😀"

        self._create_emoji_ui()

    def _create_emoji_ui(self):
        """Create the emoji picker UI."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Category tabs
        self._create_category_tabs(main_frame)

        # Emoji grid
        self._create_emoji_grid(main_frame)

    def _create_category_tabs(self, parent):
        """Create category tab buttons."""
        tabs_frame = ttk.Frame(parent)
        tabs_frame.pack(fill=tk.X, pady=(0, Spacing.SM))

        self.category_buttons = {}
        for emoji, emojis in self.categories.items():
            btn = ttk.Button(
                tabs_frame,
                text=emoji,
                command=lambda e=emoji: self._select_category(e),
                style='Ghost.TButton',
                width=4
            )
            btn.pack(side=tk.LEFT, padx=(Spacing.XS, 0))
            self.category_buttons[emoji] = btn

        # Select first category
        self._select_category(self.current_category)

    def _create_emoji_grid(self, parent):
        """Create the emoji grid display."""
        # Scrollable emoji area
        emoji_frame = ttk.Frame(parent)
        emoji_frame.pack(fill=tk.BOTH, expand=True)

        # Create emoji buttons grid
        self.emoji_buttons_frame = ttk.Frame(emoji_frame)
        self.emoji_buttons_frame.pack(fill=tk.BOTH, expand=True)

        self._update_emoji_display()

    def _select_category(self, category: str):
        """Select an emoji category."""
        self.current_category = category

        # Update button styles
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(style='Primary.TButton')
            else:
                btn.configure(style='Ghost.TButton')

        # Update emoji display
        self._update_emoji_display()

    def _update_emoji_display(self):
        """Update the emoji grid display."""
        # Clear existing emojis
        for widget in self.emoji_buttons_frame.winfo_children():
            widget.destroy()

        # Get emojis for current category
        emojis = self.categories[self.current_category]

        # Create emoji grid (5 columns)
        for i, emoji in enumerate(emojis):
            row = i // 5
            col = i % 5

            btn = ttk.Button(
                self.emoji_buttons_frame,
                text=emoji,
                command=lambda e=emoji: self._select_emoji(e),
                style='Ghost.TButton',
                width=4
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

        # Configure grid weights
        for i in range(5):
            self.emoji_buttons_frame.grid_columnconfigure(i, weight=1)

    def _select_emoji(self, emoji: str):
        """Select an emoji and notify callback."""
        if self.on_emoji_select:
            self.on_emoji_select(emoji)
        # Close picker (parent should handle this)


class AttachmentHandler(ttk.Frame):
    """Modern file attachment interface."""

    def __init__(self, master, on_file_attach: Callable[[str], None]):
        super().__init__(master)
        self.on_file_attach = on_file_attach
        self.attachments: List[dict] = []

        self._create_attachment_ui()

    def _create_attachment_ui(self):
        """Create the attachment interface."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.X)

        # Add attachment button
        self.add_btn = DesignUtils.create_styled_button(
            main_frame,
            "📎 Attach File",
            self._add_attachment,
            style='Ghost.TButton'
        )
        self.add_btn.pack(side=tk.LEFT, padx=(0, Spacing.SM))

        # Preview area for attachments
        self.preview_frame = ttk.Frame(main_frame)
        self.preview_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _add_attachment(self):
        """Add file attachment."""
        file_path = filedialog.askopenfilename(
            title="Select File to Attach",
            filetypes=[
                ("All Files", "*.*"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Documents", "*.txt *.pdf *.doc *.docx"),
                ("Audio", "*.mp3 *.wav *.ogg"),
                ("Video", "*.mp4 *.avi *.mov *.mkv")
            ]
        )

        if file_path and self.on_file_attach:
            self.on_file_attach(file_path)
            self._add_attachment_preview(file_path)

    def _add_attachment_preview(self, file_path: str):
        """Add attachment preview."""
        import os

        # Get file info
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()

        # Determine file icon
        icon_map = {
            '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.bmp': '🖼️',
            '.txt': '📄', '.pdf': '📕', '.doc': '📘', '.docx': '📘',
            '.mp3': '🎵', '.wav': '🎵', '.ogg': '🎵',
            '.mp4': '🎬', '.avi': '🎬', '.mov': '🎬', '.mkv': '🎬'
        }
        icon = icon_map.get(file_ext, '📎')

        # Create preview widget
        preview = ttk.Frame(self.preview_frame)
        preview.pack(side=tk.LEFT, padx=(Spacing.XS, 0))

        # File icon and name
        file_label = tk.Label(
            preview,
            text=f"{icon} {filename[:15]}..." if len(filename) > 18 else f"{icon} {filename}",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY,
            cursor="hand2"
        )
        file_label.pack(side=tk.LEFT, padx=(0, Spacing.XS))

        # Remove button
        remove_btn = ttk.Button(
            preview,
            text="✕",
            command=lambda: self._remove_attachment(preview, file_path),
            style='Ghost.TButton',
            width=2
        )
        remove_btn.pack(side=tk.RIGHT)

        # Store attachment info
        attachment_info = {
            'path': file_path,
            'filename': filename,
            'size': file_size,
            'type': file_ext,
            'widget': preview
        }
        self.attachments.append(attachment_info)

    def _remove_attachment(self, preview_widget: ttk.Frame, file_path: str):
        """Remove an attachment."""
        preview_widget.destroy()
        self.attachments = [att for att in self.attachments if att['path'] != file_path]

    def get_attachments(self) -> List[dict]:
        """Get list of attachments."""
        return self.attachments

    def clear_attachments(self):
        """Clear all attachments."""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        self.attachments.clear()


class ModernMessageComposer(ttk.Frame):
    """Enhanced message composer with rich text, emoji, and file support."""

    def __init__(self, master, on_send: Optional[Callable[[str, List], None]] = None):
        super().__init__(master)
        self.on_send = on_send
        self._connected = False
        self.is_emoji_picker_visible = False
        self.is_attachment_visible = False

        # Rich text formatting
        self.format_stack: List[str] = []

        # Message templates
        self.templates = {
            "code": "```\n\n```",
            "quote": ">",
            "bold": lambda text: f"**{text}**",
            "italic": lambda text: f"*{text}*",
            "code_inline": lambda text: f"`{text}`"
        }

        self._create_composer_ui()

    def _create_composer_ui(self):
        """Create the message composer UI."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.X, expand=True)

        # Top toolbar
        self._create_toolbar(main_frame)

        # Message input area
        self._create_input_area(main_frame)

        # Bottom toolbar
        self._create_bottom_toolbar(main_frame)

        # Character counter
        self._create_char_counter(main_frame)

        # Bind keyboard shortcuts
        self._bind_shortcuts()

    def _create_toolbar(self, parent):
        """Create formatting toolbar."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=Spacing.MD, pady=(Spacing.SM, 0))

        # Text formatting buttons
        format_buttons = [
            ("B", self._format_bold, "Bold"),
            ("I", self._format_italic, "Italic"),
            ("`", self._format_code_inline, "Inline code"),
            ("</>", self._insert_code_block, "Code block"),
            (">", self._insert_quote, "Quote"),
        ]

        for text, command, tooltip in format_buttons:
            btn = ttk.Button(
                toolbar,
                text=text,
                command=command,
                style='Ghost.TButton',
                width=4
            )
            btn.pack(side=tk.LEFT, padx=(0, Spacing.XS))

            # Add tooltip
            DesignUtils.create_tooltip_text(btn, tooltip)

        # Separator
        separator = ttk.Separator(toolbar, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=Spacing.SM)

        # Emoji button
        self.emoji_btn = ttk.Button(
            toolbar,
            text="😀",
            command=self._toggle_emoji_picker,
            style='Ghost.TButton',
            width=4
        )
        self.emoji_btn.pack(side=tk.LEFT, padx=(0, Spacing.XS))

        # Attachment button
        self.attachment_btn = ttk.Button(
            toolbar,
            text="📎",
            command=self._toggle_attachment,
            style='Ghost.TButton',
            width=4
        )
        self.attachment_btn.pack(side=tk.LEFT, padx=(0, Spacing.XS))

    def _create_input_area(self, parent):
        """Create the main message input area."""
        # Input container
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, padx=Spacing.MD, pady=(Spacing.SM, Spacing.MD))

        # Background frame with border
        bg_frame = tk.Frame(
            input_frame,
            bg=Colors.INPUT_BG,
            relief="solid",
            bd=1
        )
        bg_frame.pack(fill=tk.X, ipady=Spacing.SM)

        # Text widget for rich text editing
        self.text_widget = tk.Text(
            bg_frame,
            height=4,
            wrap="word",
            font=(Typography.FONT_CHAT, Typography.SIZE_MD),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.INPUT_BG,
            relief="flat",
            bd=0,
            selectbackground=Colors.BTN_PRIMARY,
            selectforeground=Colors.TEXT_PRIMARY,
            highlightthickness=0,
            undo=True,
            tabs=('1c', '2c', '3c', '4c')
        )
        self.text_widget.pack(fill=tk.X, expand=True, padx=Spacing.SM, pady=Spacing.SM)

        # Bind text changes
        self.text_widget.bind('<KeyRelease>', self._on_text_change)
        self.text_widget.bind('<Button-1>', self._on_text_click)

    def _create_bottom_toolbar(self, parent):
        """Create bottom toolbar with send and additional options."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=Spacing.MD, pady=(0, Spacing.SM))

        # Template dropdown
        template_frame = ttk.Frame(toolbar)
        template_frame.pack(side=tk.LEFT)

        ttk.Label(
            template_frame,
            text="Quick:",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            foreground=Colors.TEXT_MUTED
        ).pack(side=tk.LEFT, padx=(0, Spacing.XS))

        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(
            template_frame,
            textvariable=self.template_var,
            values=list(self.templates.keys()),
            state="readonly",
            width=10,
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM)
        )
        template_combo.pack(side=tk.LEFT)
        template_combo.bind('<<ComboboxSelected>>', self._insert_template)

        # Send button (right side)
        self.send_btn = DesignUtils.create_styled_button(
            toolbar,
            "Send Message",
            self._send_message,
            style='Primary.TButton'
        )
        self.send_btn.pack(side=tk.RIGHT)

        # Connection status
        self.connection_status = ttk.Label(
            toolbar,
            text="Not Connected",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            foreground=Colors.TEXT_MUTED
        )
        self.connection_status.pack(side=tk.RIGHT, padx=(0, Spacing.MD))

    def _create_char_counter(self, parent):
        """Create character counter."""
        self.char_counter = ttk.Label(
            parent,
            text="0/2000",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            foreground=Colors.TEXT_MUTED
        )
        self.char_counter.pack(side=tk.RIGHT, padx=Spacing.MD, pady=(0, Spacing.SM))

        # Set max character limit
        self.max_chars = 2000

    def _bind_shortcuts(self):
        """Bind keyboard shortcuts for power users."""
        def on_key_press(event):
            # Ctrl+Enter = Send message
            if event.keysym == "Return" and event.state & 0x4:
                self._send_message()
                return "break"

            # Ctrl+B = Bold
            elif event.keysym.lower() == 'b' and event.state & 0x4:
                self._format_bold()
                return "break"

            # Ctrl+I = Italic
            elif event.keysym.lower() == 'i' and event.state & 0x4:
                self._format_italic()
                return "break"

            # Ctrl+K = Inline code
            elif event.keysym.lower() == 'k' and event.state & 0x4:
                self._format_code_inline()
                return "break"

            # Tab = Insert template completion
            elif event.keysym == "Tab":
                self._complete_template()
                return "break"

        self.text_widget.bind('<Control-Return>', on_key_press)
        self.text_widget.bind('<Control-b>', on_key_press)
        self.text_widget.bind('<Control-i>', on_key_press)
        self.text_widget.bind('<Control-k>', on_key_press)
        self.text_widget.bind('<Tab>', on_key_press)

    def _on_text_change(self, event=None):
        """Handle text changes for character counting and auto-resize."""
        content = self.text_widget.get("1.0", "end-1c")
        char_count = len(content)

        # Update character counter
        counter_text = f"{char_count}/{self.max_chars}"
        self.char_counter.config(text=counter_text)

        # Color coding based on length
        if char_count > self.max_chars * 0.9:
            self.char_counter.config(foreground=Colors.STATUS_FAILED)
        elif char_count > self.max_chars * 0.7:
            self.char_counter.config(foreground=Colors.STATUS_CONNECTING)
        else:
            self.char_counter.config(foreground=Colors.TEXT_MUTED)

        # Auto-resize text widget
        self._auto_resize()

    def _on_text_click(self, event=None):
        """Handle text widget clicks."""
        # Clear any selection formatting that might interfere
        pass

    def _auto_resize(self):
        """Auto-resize the text widget based on content."""
        lines = self.text_widget.get("1.0", "end-1c").count('\n') + 1
        max_height = min(max(lines, 1), 10)  # Between 1 and 10 lines
        self.text_widget.configure(height=max_height)

    def _format_bold(self):
        """Apply bold formatting to selected text."""
        self._surround_selection("**")

    def _format_italic(self):
        """Apply italic formatting to selected text."""
        self._surround_selection("*")

    def _format_code_inline(self):
        """Apply inline code formatting to selected text."""
        self._surround_selection("`")

    def _insert_code_block(self):
        """Insert a code block."""
        self.text_widget.insert("insert", self.templates["code"])

    def _insert_quote(self):
        """Insert a quote prefix."""
        # Add quote to current line
        current_line_start = self.text_widget.index("insert linestart")
        self.text_widget.insert(current_line_start, "> ")

    def _insert_template(self, event=None):
        """Insert selected template."""
        template_key = self.template_var.get()
        if template_key in self.templates:
            template = self.templates[template_key]
            if callable(template):
                # Template function
                self.text_widget.insert("insert", " ")
            else:
                # Template string
                self.text_widget.insert("insert", template)
        self.template_var.set("")  # Clear selection

    def _complete_template(self):
        """Complete template syntax."""
        # Simple template completion
        content = self.text_widget.get("1.0", "end-1c")
        if content.endswith("```"):
            # Complete code block
            self.text_widget.insert("insert", "\n\n```")
        elif content.endswith("**"):
            # Complete bold
            selected = self.text_widget.get("sel.first", "sel.last") if self.text_widget.tag_ranges("sel") else "text"
            self.text_widget.insert("insert", selected + "**")

    def _surround_selection(self, wrapper: str):
        """Surround selected text with wrapper characters."""
        try:
            # Get current selection
            sel_first = self.text_widget.index("sel.first")
            sel_last = self.text_widget.index("sel.last")
            selected_text = self.text_widget.get(sel_first, sel_last)

            # Replace selection with wrapped text
            self.text_widget.delete(sel_first, sel_last)
            self.text_widget.insert(sel_first, f"{wrapper}{selected_text}{wrapper}")

        except tk.TclError:
            # No selection, just insert wrapper
            self.text_widget.insert("insert", wrapper + wrapper)

    def _toggle_emoji_picker(self):
        """Toggle emoji picker visibility."""
        if self.is_emoji_picker_visible:
            self._hide_emoji_picker()
        else:
            self._show_emoji_picker()

    def _show_emoji_picker(self):
        """Show the emoji picker."""
        self.emoji_picker = EmojiPicker(self, self._insert_emoji)
        self.emoji_picker.pack(fill=tk.X, padx=Spacing.MD, pady=(0, Spacing.SM))
        self.is_emoji_picker_visible = True

    def _hide_emoji_picker(self):
        """Hide the emoji picker."""
        if hasattr(self, 'emoji_picker'):
            self.emoji_picker.destroy()
            delattr(self, 'emoji_picker')
        self.is_emoji_picker_visible = False

    def _insert_emoji(self, emoji: str):
        """Insert emoji at cursor position."""
        self.text_widget.insert("insert", emoji)
        self._hide_emoji_picker()
        self.text_widget.focus_set()

    def _toggle_attachment(self):
        """Toggle attachment interface visibility."""
        if self.is_attachment_visible:
            self._hide_attachment()
        else:
            self._show_attachment()

    def _show_attachment(self):
        """Show the attachment interface."""
        self.attachment_handler = AttachmentHandler(self, self._on_file_attach)
        self.attachment_handler.pack(fill=tk.X, padx=Spacing.MD, pady=(0, Spacing.SM))
        self.is_attachment_visible = True

    def _hide_attachment(self):
        """Hide the attachment interface."""
        if hasattr(self, 'attachment_handler'):
            self.attachment_handler.destroy()
            delattr(self, 'attachment_handler')
        self.is_attachment_visible = False

    def _on_file_attach(self, file_path: str):
        """Handle file attachment."""
        # This could show a preview, process the file, etc.
        print(f"File attached: {file_path}")

    def _send_message(self):
        """Send the current message."""
        if not self._connected:
            return

        content = self.text_widget.get("1.0", "end-1c").strip()
        if not content:
            return

        # Get attachments
        attachments = []
        if hasattr(self, 'attachment_handler'):
            attachments = self.attachment_handler.get_attachments()

        # Clear input
        self.text_widget.delete("1.0", "end")
        self._on_text_change()

        # Hide attachment interface
        if hasattr(self, 'attachment_handler'):
            self.attachment_handler.clear_attachments()

        # Call send callback
        if self.on_send:
            self.on_send(content, attachments)

        # Focus back to input
        self.text_widget.focus_set()

    def set_connection_status(self, connected: bool):
        """Update connection status."""
        self._connected = connected

        if connected:
            self.connection_status.config(
                text="Connected",
                foreground=Colors.STATUS_CONNECTED
            )
            self.send_btn.config(state="normal")
        else:
            self.connection_status.config(
                text="Not Connected",
                foreground=Colors.STATUS_DISCONNECTED
            )
            self.send_btn.config(state="disabled")

    def focus_input(self):
        """Focus the input widget."""
        self.text_widget.focus_set()

    def get_input_text(self) -> str:
        """Get the current input text."""
        return self.text_widget.get("1.0", "end-1c").strip()

    def clear_input(self):
        """Clear the input text."""
        self.text_widget.delete("1.0", "end")
        self._on_text_change()

    def insert_text(self, text: str):
        """Insert text at cursor position."""
        self.text_widget.insert("insert", text)
        self.text_widget.focus_set()

    def get_attachments(self) -> List[dict]:
        """Get current attachments."""
        if hasattr(self, 'attachment_handler'):
            return self.attachment_handler.get_attachments()
        return []

    def enable_rich_text(self, enable: bool = True):
        """Enable or disable rich text features."""
        # This would enable/disable formatting buttons
        pass

    def set_message_templates(self, templates: dict):
        """Set custom message templates."""
        self.templates.update(templates)

    def save_draft(self) -> str:
        """Save current draft."""
        return self.text_widget.get("1.0", "end-1c")

    def load_draft(self, draft: str):
        """Load a draft message."""
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", draft)
        self._on_text_change()
