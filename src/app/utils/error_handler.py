"""Centralized error handling and user feedback system."""
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional, Any
import traceback
import sys


class ErrorHandler:
    """
    Centralized error handling system that provides consistent error messages
    and user-friendly feedback across the application.
    """

    def __init__(self):
        self.error_callbacks: list[Callable[[str, Exception], None]] = []
        self.debug_mode = False

    def register_error_callback(self, callback: Callable[[str, Exception], None]):
        """Register a callback for error notifications."""
        self.error_callbacks.append(callback)

    def handle_error(self, error: Exception, context: str = "", user_message: str = "") -> bool:
        """
        Handle an error with appropriate logging and user feedback.

        Args:
            error: The exception that occurred
            context: Context where the error occurred
            user_message: User-friendly error message (optional)

        Returns:
            True if error was handled, False if it should be re-raised
        """
        error_msg = str(error)
        full_error = f"{context}: {error_msg}" if context else error_msg

        # Log to console
        if self.debug_mode:
            print(f"ERROR: {full_error}")
            traceback.print_exc()

        # Notify callbacks
        for callback in self.error_callbacks:
            try:
                callback(context, error)
            except Exception:
                pass  # Ignore callback errors

        # Show user-friendly message if provided
        if user_message:
            messagebox.showerror("Error", user_message)
        else:
            # Provide default error message based on error type
            default_message = self._get_default_error_message(error)
            messagebox.showerror("Error", default_message)

        return True

    def safe_execute(self, func: Callable, *args, context: str = "", **kwargs) -> Optional[Any]:
        """
        Safely execute a function and handle any errors.

        Args:
            func: Function to execute
            *args: Arguments for the function
            context: Context description for error reporting
            **kwargs: Keyword arguments for the function

        Returns:
            Function result or None if error occurred
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_error(e, context)
            return None

    def _get_default_error_message(self, error: Exception) -> str:
        """Get a default error message based on error type."""
        error_type = type(error).__name__

        message_map = {
            "ConnectionError": "Unable to connect to device. Please check your connection.",
            "TimeoutError": "Operation timed out. Please try again.",
            "PermissionError": "Insufficient permissions for this operation.",
            "FileNotFoundError": "Required file not found.",
            "ValueError": "Invalid input provided.",
            "TypeError": "Invalid data type provided.",
        }

        return message_map.get(error_type, f"An error occurred: {error_type}")

    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode for detailed error logging."""
        self.debug_mode = enabled


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def safe_execute(func: Callable, *args, context: str = "", **kwargs) -> Optional[Any]:
    """Convenience function for safe execution."""
    return get_error_handler().safe_execute(func, *args, context=context, **kwargs)


def handle_error(error: Exception, context: str = "", user_message: str = "") -> bool:
    """Convenience function for error handling."""
    return get_error_handler().handle_error(error, context, user_message)


def register_error_callback(callback: Callable[[str, Exception], None]):
    """Convenience function for registering error callbacks."""
    get_error_handler().register_error_callback(callback)
