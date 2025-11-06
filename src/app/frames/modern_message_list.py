"""Modern message list component with search, threading, and performance optimization."""
import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable, Dict
import re
from datetime import datetime, timedelta
from .chat_models import ChatMessage, MessageManager, MessageType
from .modern_message_bubble import ModernMessageBubble
from utils.design_system import Colors, Typography, Spacing, DesignUtils


class SearchBar(ttk.Frame):
    """Modern search bar for message filtering."""

    def __init__(self, master, on_search: Optional[Callable[[str], None]] = None):
        super().__init__(master)
        self.on_search = on_search
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        self.is_searching = False

        self._create_search_bar()

    def _create_search_bar(self):
        """Create the search bar UI."""
        # Search container
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=Spacing.MD, pady=Spacing.SM)

        # Search icon
        search_icon = tk.Label(
            search_frame,
            text="🔍",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_PRIMARY
        )
        search_icon.pack(side=tk.LEFT, padx=(0, Spacing.SM))

        # Search entry
        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            style='ChatEntry.TEntry',
            font=(Typography.FONT_PRIMARY, Typography.SIZE_MD)
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Clear search button
        self.clear_btn = ttk.Button(
            search_frame,
            text="✕",
            command=self._clear_search,
            style='Ghost.TButton',
            width=3
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        self.clear_btn.pack_forget()  # Hidden by default

        # Search results label
        self.results_label = tk.Label(
            search_frame,
            text="",
            font=(Typography.FONT_PRIMARY, Typography.SIZE_SM),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_PRIMARY
        )
        self.results_label.pack(side=tk.LEFT, padx=(Spacing.SM, 0))

        # Bind keyboard shortcuts
        self.search_entry.bind('<Escape>', lambda e: self._clear_search())
        self.search_entry.bind('<Control-f>', self._focus_search)
        self.search_entry.bind('<Control-a>', lambda e: self.search_entry.select_range(0, tk.END) or 'break')

    def _on_search_change(self, *args):
        """Handle search text change."""
        search_text = self.search_var.get().strip()

        # Show/hide clear button
        if search_text:
            self.clear_btn.pack(side=tk.RIGHT, padx=(Spacing.SM, 0))
        else:
            self.clear_btn.pack_forget()

        # Update search
        if self.on_search:
            self.on_search(search_text)

    def _clear_search(self):
        """Clear the search and reset results."""
        self.search_var.set("")
        self.results_label.config(text="")
        if self.on_search:
            self.on_search("")

    def _focus_search(self, event=None):
        """Focus the search entry."""
        self.search_entry.focus_set()
        return "break"

    def set_results_count(self, count: int, total: int):
        """Update search results display."""
        if count == 0:
            self.results_label.config(text="No results")
        elif count == total:
            self.results_label.config(text=f"{count} messages")
        else:
            self.results_label.config(text=f"{count} of {total} messages")

    def get_search_text(self) -> str:
        """Get current search text."""
        return self.search_var.get()

    def focus(self):
        """Focus the search entry."""
        self.search_entry.focus_set()


class MessageGroup(ttk.Frame):
    """Container for grouped messages (same sender, consecutive)."""

    def __init__(self, master, sender: str, is_own: bool = False):
        super().__init__(master)
        self.sender = sender
        self.is_own = is_own
        self.messages: List[ModernMessageBubble] = []

        # Configure frame
        self.configure(style='ChatFrame.TFrame')

        # Create group layout
        self._create_group_layout()

    def _create_group_layout(self):
        """Create the group layout."""
        # Main container
        container = ttk.Frame(self)
        container.pack(fill=tk.X, expand=True)

        # Message bubbles will be added here
        self.bubbles_container = ttk.Frame(container)
        self.bubbles_container.pack(fill=tk.X, expand=True)

    def add_message(self, message: ChatMessage, message_bubble: ModernMessageBubble):
        """Add a message to this group."""
        self.messages.append(message_bubble)
        message_bubble.pack(fill=tk.X, pady=(Spacing.SM, 0))

    def clear_messages(self):
        """Clear all messages from the group."""
        for message_bubble in self.messages:
            message_bubble.destroy()
        self.messages.clear()


class ModernMessageList(ttk.Frame):
    """Enhanced message list with modern chat features."""

    def __init__(self, master, message_manager: MessageManager):
        super().__init__(master)
        self.message_manager = message_manager
        self.message_widgets: Dict[str, ModernMessageBubble] = {}
        self.message_groups: Dict[str, MessageGroup] = {}
        self.filtered_messages: List[ChatMessage] = []
        self.search_results: List[ChatMessage] = []
        self.current_highlight = None

        # Performance optimization
        self.max_visible_messages = 100
        self.virtual_scroll_enabled = True

        # Register for message updates
        self.message_manager.on_message_update(self._on_message_update)
        self.message_manager.on_history_update(self._on_history_update)

        # Create UI
        self._create_ui()

        # Load initial messages
        self._load_existing_messages()

    def _create_ui(self):
        """Create the message list UI."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Search bar
        self.search_bar = SearchBar(main_frame, self._on_search_change)
        self.search_bar.pack(fill=tk.X, side=tk.TOP)

        # Scrollable message area
        self._create_scrollable_area(main_frame)

        # Keyboard shortcuts
        self._bind_keyboard_shortcuts()

    def _create_scrollable_area(self, parent):
        """Create the scrollable message area."""
        # Canvas and scrollbar
        self.canvas = tk.Canvas(
            parent,
            bg=Colors.BG_CHAT_AREA,
            highlightthickness=0,
            cursor="arrow"
        )
        self.scrollbar = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=self.canvas.yview
        )

        # Scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.configure(style='ChatFrame.TFrame')

        # Configure canvas
        self.canvas.configure(yscrollcommand=self._on_scroll)

        # Pack scroll components
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Create window
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            tags=("frame_window",)
        )

        # Bind events
        self._bind_scrollable_events()

        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

    def _bind_scrollable_events(self):
        """Bind scrolling and mouse events."""
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")

        self.canvas.bind("<Enter>", _bind_to_mousewheel)
        self.canvas.bind("<Leave>", _unbind_from_mousewheel)

        # Canvas resize
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Smooth scrolling for trackpads
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_canvas_configure(self, event):
        """Handle canvas resize."""
        # Update the canvas window width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _on_scroll(self, *args):
        """Handle scroll events."""
        self.canvas.yview(*args)

        # Update virtual scrolling if enabled
        if self.virtual_scroll_enabled:
            self._update_virtual_display()

    def _bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts for power users."""
        def on_key_press(event):
            # Ctrl+F - Focus search
            if event.state & 0x4 and event.keysym.lower() == 'f':
                self.search_bar.focus()
                return "break"

            # Ctrl+A - Select all messages
            elif event.state & 0x4 and event.keysym.lower() == 'a':
                self._select_all_messages()
                return "break"

            # Arrow keys for navigation
            elif event.keysym == "Up":
                self._navigate_message(-1)
                return "break"
            elif event.keysym == "Down":
                self._navigate_message(1)
                return "break"

            # Enter - Open selected message actions
            elif event.keysym == "Return":
                if self.current_highlight:
                    self._open_message_actions(self.current_highlight.message)
                return "break"

        self.canvas.bind("<KeyPress>", on_key_press)
        self.canvas.focus_set()

    def _on_message_update(self, message: ChatMessage):
        """Handle new message or message update."""
        if not any(widget.message.id == message.id for widget in self.message_widgets.values()):
            # New message
            self._add_message_widget(message)
        else:
            # Update existing message
            self._update_message_widget(message)

    def _on_history_update(self):
        """Handle history clearing."""
        self._clear_all_messages()

    def _load_existing_messages(self):
        """Load existing messages from message manager."""
        messages = self.message_manager.get_recent_messages(self.max_visible_messages)
        for message in messages:
            self._add_message_widget(message)

    def _add_message_widget(self, message: ChatMessage):
        """Add a new message bubble."""
        # Create message bubble
        message_bubble = ModernMessageBubble(
            self.scrollable_frame,
            message,
            show_username=self._should_show_username(message),
            on_message_action=self._on_message_action
        )

        # Store reference
        self.message_widgets[message.id] = message_bubble

        # Add to appropriate group
        self._add_to_message_group(message, message_bubble)

        # Auto-scroll to bottom if not searching
        if not self.search_bar.get_search_text():
            self._scroll_to_bottom()

    def _update_message_widget(self, message: ChatMessage):
        """Update an existing message widget."""
        if message.id in self.message_widgets:
            widget = self.message_widgets[message.id]
            widget.update_status(message.status)

    def _add_to_message_group(self, message: ChatMessage, message_bubble: ModernMessageBubble):
        """Add message to appropriate group for better layout."""
        group_key = f"{message.sender}_{message_bubble.is_own}"

        if group_key not in self.message_groups:
            group = MessageGroup(
                self.scrollable_frame,
                message.sender,
                message_bubble.is_own
            )
            group.pack(fill=tk.X, pady=(Spacing.SM, 0))
            self.message_groups[group_key] = group
        else:
            group = self.message_groups[group_key]

        group.add_message(message, message_bubble)

    def _should_show_username(self, message: ChatMessage) -> bool:
        """Determine if username should be shown for this message."""
        # Always show username for system messages and first message in conversation
        if message.sender.lower() == "system":
            return True

        # Check if this is the first message from this sender
        for existing_message in self.message_widgets.values():
            if (existing_message.message.sender == message.sender and
                existing_message.message.timestamp < message.timestamp):
                # Not first message from this sender
                return False

        return True

    def _on_message_action(self, message: ChatMessage, action: str, *args):
        """Handle message action events."""
        if action == "action_copy":
            message_bubble = self.message_widgets.get(message.id)
            if message_bubble:
                message_bubble.copy_to_clipboard()
                message_bubble.show_copy_feedback()
        elif action == "click":
            self._select_message(message)
        elif action == "double_click":
            self._open_message_details(message)

    def _on_search_change(self, search_text: str):
        """Handle search text changes."""
        if not search_text:
            self._clear_search_results()
        else:
            self._perform_search(search_text)

    def _perform_search(self, search_text: str):
        """Perform search across all messages."""
        self.search_results.clear()
        all_messages = list(self.message_widgets.keys())

        # Simple text search (could be enhanced with regex, date filters, etc.)
        pattern = re.escape(search_text.lower())

        for message_id in all_messages:
            message_bubble = self.message_widgets[message_id]
            if re.search(pattern, message_bubble.message.content.lower()):
                self.search_results.append(message_bubble.message)

        # Update results display
        self.search_bar.set_results_count(len(self.search_results), len(all_messages))

        # Highlight search results
        self._highlight_search_results()

    def _clear_search_results(self):
        """Clear search results and highlighting."""
        self.search_results.clear()
        self._clear_message_highlighting()
        self.search_bar.set_results_count(0, len(self.message_widgets))

    def _highlight_search_results(self):
        """Highlight search results in the message list."""
        self._clear_message_highlighting()

        # Highlight search result messages
        for message in self.search_results:
            if message.id in self.message_widgets:
                widget = self.message_widgets[message.id]
                # Add subtle highlight (could be enhanced with borders, backgrounds, etc.)
                widget.configure(relief="solid", borderwidth=1)

    def _clear_message_highlighting(self):
        """Clear all message highlighting."""
        for widget in self.message_widgets.values():
            widget.configure(relief="flat", borderwidth=0)

    def _scroll_to_bottom(self):
        """Scroll to show the latest message."""
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _scroll_to_message(self, message: ChatMessage):
        """Scroll to a specific message."""
        if message.id in self.message_widgets:
            widget = self.message_widgets[message.id]
            # Calculate position and scroll to it
            widget.update_idletasks()
            widget.update()
            widget.focus_set()

    def _select_message(self, message: ChatMessage):
        """Select a message."""
        # Remove previous selection
        if self.current_highlight:
            self.current_highlight.configure(relief="solid", borderwidth=2)

        # Highlight current message
        if message.id in self.message_widgets:
            widget = self.message_widgets[message.id]
            widget.configure(relief="raised", borderwidth=3)
            self.current_highlight = widget

    def _select_all_messages(self):
        """Select all messages (for search/filter operations)."""
        for widget in self.message_widgets.values():
            widget.select_text()

    def _open_message_details(self, message: ChatMessage):
        """Open detailed view for a message."""
        # This could open a modal dialog with message details, editing options, etc.
        print(f"Opening details for message: {message.content}")

    def _open_message_actions(self, message: ChatMessage):
        """Open actions menu for a message."""
        # This could open a context menu with actions like reply, edit, delete, etc.
        print(f"Opening actions for message: {message.content}")

    def _navigate_message(self, direction: int):
        """Navigate between messages using arrow keys."""
        messages = list(self.message_widgets.values())
        if not messages:
            return

        if self.current_highlight:
            current_index = messages.index(self.current_highlight)
            new_index = current_index + direction

            # Wrap around if needed
            if new_index < 0:
                new_index = len(messages) - 1
            elif new_index >= len(messages):
                new_index = 0

            target_widget = messages[new_index]
        else:
            # Start from first or last message
            target_widget = messages[0] if direction > 0 else messages[-1]

        # Select and scroll to target message
        target_message = target_widget.message
        self._select_message(target_message)
        self._scroll_to_message(target_message)

    def _update_virtual_display(self):
        """Update virtual scrolling for performance with large message lists."""
        # Implementation for virtual scrolling to only show visible messages
        # This would improve performance with very large message histories
        pass

    def _clear_all_messages(self):
        """Clear all messages from display."""
        # Clear message widgets
        for widget in self.message_widgets.values():
            widget.destroy()
        self.message_widgets.clear()

        # Clear message groups
        for group in self.message_groups.values():
            group.destroy()
        self.message_groups.clear()

        # Reset search state
        self.current_highlight = None
        self.search_results.clear()

    def get_visible_messages(self) -> List[ChatMessage]:
        """Get currently visible messages."""
        return [widget.message for widget in self.message_widgets.values()]

    def export_messages(self, format_type: str = "txt") -> str:
        """Export visible messages in specified format."""
        if format_type == "txt":
            return "\n".join(self.message_manager.get_history_text())
        elif format_type == "json":
            import json
            messages_data = [
                {
                    "id": widget.message.id,
                    "sender": widget.message.sender,
                    "content": widget.message.content,
                    "timestamp": widget.message.timestamp,
                    "status": widget.message.status.value
                }
                for widget in self.message_widgets.values()
            ]
            return json.dumps(messages_data, indent=2)
        else:
            return ""

    def filter_by_date(self, date_filter: str):
        """Filter messages by date."""
        # Implementation for date-based filtering
        # Could support formats like "today", "yesterday", "week", "month", or specific dates
        pass

    def filter_by_sender(self, sender_filter: str):
        """Filter messages by sender."""
        # Implementation for sender-based filtering
        pass
