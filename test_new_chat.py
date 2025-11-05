"""Test script for the new ChatTab architecture."""
import sys
import tkinter as tk
from tkinter import ttk

# Add the app directory to the path so we can import our modules
sys.path.insert(0, 'src/app')

from frames.new_chat_tab import ChatTab
from lora_transport_locomm import LoCommTransport


class TestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChatTab Redesign Test")
        self.geometry("800x600")

        # Create a mock transport for testing
        self.transport = LoCommTransport(self)

        # Create the new chat tab
        self.chat_tab = ChatTab(
            self,
            transport=self.transport,
            username="TestUser",
            on_disconnect=self._on_disconnect
        )

        # Add some test messages
        self._add_test_messages()

        # Start test status updates
        self._start_status_test()

    def _add_test_messages(self):
        """Add some test messages to demonstrate the UI."""
        self.chat_tab.append_line("System", "Welcome to the new ChatTab!")
        self.chat_tab.append_line("Peer", "Hello! This is a test message from another user.")
        self.chat_tab.append_line("Me", "This is my message with status tracking.")
        self.chat_tab.append_line("System", "All messages now have enhanced styling and organization.")

    def _start_status_test(self):
        """Simulate status changes for testing."""
        def update_status():
            import time
            statuses = [
                "Disconnected",
                "Connecting to device...",
                "Connected to device, verifying password...",
                "Authenticated and ready",
                "Connected (mock)"
            ]

            for status in statuses:
                self.chat_tab.set_status(status)
                self.update()
                time.sleep(2)

            # Repeat
            self.after(1000, update_status)

        self.after(2000, update_status)

    def _on_disconnect(self):
        """Handle disconnect for testing."""
        print("Disconnect requested!")
        self.chat_tab.append_line("System", "Disconnected from device.")


if __name__ == "__main__":
    app = TestApp()
    app.mainloop()
