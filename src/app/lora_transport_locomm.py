"""
LoRa transport adapter for GUI communication.
Provides unified interface for real and mock LoCommAPI implementations.
"""
import sys
import os
import threading
import time
import tkinter as tk
from typing import Callable, Optional

DEBUG = False  # Set to True for debug output


# Import real LoCommAPI or use mock implementation
def _get_lora_api():
    """Import LoCommAPI with fallback to mock implementation."""
    try:
        # Add API path to Python path
        api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api"))
        if api_path not in sys.path:
            sys.path.insert(0, api_path)

        import LoCommAPI  # type: ignore
        if DEBUG:
            print(f"[LoRaTransport] Imported real LoCommAPI from {api_path}")
        return LoCommAPI
    except Exception as e:
        if DEBUG:
            print(f"[LoRaTransport] Using mock LoCommAPI: {repr(e)}")

        # Mock implementation for development/demo
        class MockLoCommAPI:
            def __init__(self):
                self._connected = False

            def connect_to_device(self) -> bool:
                self._connected = True
                return True

            def disconnect_from_device(self) -> bool:
                self._connected = False
                return True

            def enter_password(self, password: str) -> bool:
                return bool(password)

            def send_message(self, name: str, message: str) -> bool:
                return True

            def receive_message(self) -> tuple[str, str]:
                time.sleep(0.2)
                return ("", "")

            def pair_devices(self) -> bool:
                return True

            def stop_pair(self) -> bool:
                return True

            def delete_keys(self) -> bool:
                return True

        return MockLoCommAPI()


# Get LoCommAPI instance
LoCommAPI = _get_lora_api()


class LoCommTransport:
    """Transport adapter for LoRa communication with unified interface."""

    def __init__(self, ui_root: tk.Misc):
        self.root = ui_root
        self.on_receive: Optional[Callable[[str, str, float], None]] = None
        self.on_status: Optional[Callable[[str], None]] = None
        self.running = False
        self._rx_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self, password: str) -> bool:
        """Connect and authenticate device."""
        try:
            if DEBUG:
                print(f"[LoRaTransport] Starting connection")

            # Connect to device
            if hasattr(LoCommAPI, "connect_to_device"):
                success = LoCommAPI.connect_to_device()
            else:
                success = False

            if not success and LoCommAPI.__class__.__name__ == "MockLoCommAPI":
                # Mock always succeeds
                if self.on_status:
                    self.on_status("Connected (demo mode)")
                self.running = True
                self._start_rx_thread()
                return True

            if success:
                if self.on_status:
                    self.on_status("Connected")
                self.running = True
                self._start_rx_thread()
                return True
            else:
                if self.on_status:
                    self.on_status("Connection failed")
                return False

        except Exception as e:
            if DEBUG:
                print(f"[LoRaTransport] Connection error: {repr(e)}")
            if self.on_status:
                self.on_status(f"Connection error: {str(e)}")
            return False

    def _start_rx_thread(self):
        """Start background receive thread."""
        self._stop_event.clear()
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        self._rx_thread.start()

    def stop(self):
        """Stop communication and disconnect device."""
        self.running = False
        self._stop_event.set()

        try:
            if hasattr(LoCommAPI, "disconnect_from_device"):
                LoCommAPI.disconnect_from_device()
        except Exception:
            pass  # Ignore disconnect errors

        if self.on_status:
            self.on_status("Disconnected")

    def send(self, name: str, text: str):
        """Send message to connected device."""
        if not self.running:
            if self.on_status:
                self.on_status("Not connected")
            return

        try:
            if hasattr(LoCommAPI, "send_message"):
                success = LoCommAPI.send_message(name, text)
                if not success and self.on_status:
                    self.on_status("Send failed")
            else:
                if self.on_status:
                    self.on_status("Send not supported")
        except Exception as e:
            if DEBUG:
                print(f"[LoRaTransport] Send error: {repr(e)}")
            if self.on_status:
                self.on_status("Send error")

    def pair_devices(self) -> bool:
        """Start device pairing."""
        try:
            if hasattr(LoCommAPI, "pair_devices"):
                return LoCommAPI.pair_devices()
        except Exception as e:
            if DEBUG:
                print(f"[LoRaTransport] Pairing error: {repr(e)}")
        return False

    def stop_pairing(self) -> bool:
        """Stop device pairing."""
        try:
            if hasattr(LoCommAPI, "stop_pair"):
                return LoCommAPI.stop_pair()
        except Exception as e:
            if DEBUG:
                print(f"[LoRaTransport] Stop pairing error: {repr(e)}")
        return False

    def _rx_loop(self):
        """Background receive loop for incoming messages."""
        while not self._stop_event.is_set():
            try:
                if hasattr(LoCommAPI, "receive_message"):
                    sender, msg = LoCommAPI.receive_message()
                else:
                    sender, msg = ("", "")

                if sender and msg and self.on_receive:
                    timestamp = time.time()
                    self.root.after(0, lambda: self.on_receive(sender, msg, timestamp))

            except Exception as e:
                if DEBUG:
                    print(f"[LoRaTransport] Receive error: {repr(e)}")

            time.sleep(0.2)  # Keep loop responsive
