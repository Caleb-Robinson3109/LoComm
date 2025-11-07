"""
Centralized chat history management for the LoRa Chat application.
Provides consistent export and clear operations.
"""
import os
import time
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import List, Optional


class ChatHistoryManager:
    """
    Centralized chat history management system that handles export and clear operations.
    """

    def __init__(self):
        pass

    def export_chat_history(self, chat_tab, session, parent_widget: Optional[tk.Misc] = None) -> bool:
        """
        Export chat history to a file.

        Args:
            chat_tab: ChatPage instance with get_history_lines() method
            session: Session instance containing username
            parent_widget: Parent widget for dialog boxes

        Returns:
            True if export was successful, False otherwise
        """
        if not chat_tab:
            messagebox.showinfo("Export History", "Open the chat screen to export history.")
            return False

        lines = chat_tab.get_history_lines()
        if not lines:
            messagebox.showinfo("Export History", "No messages to export yet.")
            return False

        # Generate default filename
        username = session.username or 'session'
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        default_name = f"locomm_chat_{username}_{timestamp}.txt"

        # Open save dialog
        path = filedialog.asksaveasfilename(
            title="Save chat history",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            parent=parent_widget
        )

        if not path:
            return False

        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines))
            messagebox.showinfo("Export History", f"Saved chat history to {path}")
            return True
        except OSError as exc:
            messagebox.showerror("Export Failed", f"Could not save chat history:\n{exc}")
            return False

    def clear_chat_history(self, chat_tab, parent_widget: Optional[tk.Misc] = None) -> bool:
        """
        Clear chat history.

        Args:
            chat_tab: ChatPage instance with clear_history() method
            parent_widget: Parent widget for dialog boxes

        Returns:
            True if clear was successful, False otherwise
        """
        if not chat_tab:
            messagebox.showinfo("Clear Chat", "Open the chat screen to clear history.")
            return False

        if parent_widget:
            if not messagebox.askyesno("Clear Chat", "Are you sure you want to clear the current chat log?", parent=parent_widget):
                return False
        else:
            if not messagebox.askyesno("Clear Chat", "Are you sure you want to clear the current chat log?"):
                return False

        try:
            chat_tab.clear_history()
            messagebox.showinfo("Chat History", "Chat history cleared.")
            return True
        except Exception as exc:
            messagebox.showerror("Clear Failed", f"Could not clear chat history:\n{exc}")
            return False

    def get_chat_statistics(self, chat_tab) -> dict:
        """
        Get statistics about the chat history.

        Args:
            chat_tab: ChatPage instance

        Returns:
            Dictionary with statistics
        """
        if not chat_tab:
            return {"messages": 0, "words": 0, "chars": 0}

        try:
            lines = chat_tab.get_history_lines()
            total_messages = len(lines)
            total_words = sum(len(line.split()) for line in lines)
            total_chars = sum(len(line) for line in lines)

            return {
                "messages": total_messages,
                "words": total_words,
                "chars": total_chars
            }
        except Exception:
            return {"messages": 0, "words": 0, "chars": 0}


# Global chat history manager instance
_chat_history_manager: Optional[ChatHistoryManager] = None


def get_chat_history_manager() -> ChatHistoryManager:
    """Get the global chat history manager instance."""
    global _chat_history_manager
    if _chat_history_manager is None:
        _chat_history_manager = ChatHistoryManager()
    return _chat_history_manager


def export_chat_history(chat_tab, session, parent_widget=None) -> bool:
    """Convenience function to export chat history."""
    return get_chat_history_manager().export_chat_history(chat_tab, session, parent_widget)


def clear_chat_history(chat_tab, parent_widget=None) -> bool:
    """Convenience function to clear chat history."""
    return get_chat_history_manager().clear_chat_history(chat_tab, parent_widget)


def get_chat_statistics(chat_tab) -> dict:
    """Convenience function to get chat statistics."""
    return get_chat_history_manager().get_chat_statistics(chat_tab)
