import sys
import os
import threading
import time
import tkinter as tk
from typing import Callable, Optional

DEBUG = False  # Set True to see debug prints


# ---------------- Attempt to import real LoCommAPI ----------------- #
LoCommAPI = None
try:
    # ensure path to ../api is available (app/ is current file dir)
    api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api"))
    if api_path not in sys.path:
        sys.path.insert(0, api_path)
    import LoCommAPI  # type: ignore
    if DEBUG:
        print("[lora_transport_locomm] Imported real LoCommAPI from", api_path)
except Exception as e:
    # If import fails (e.g. No module named 'serial'), create a mock object
    print("[lora_transport_locomm] Warning: could not import LoCommAPI (running in mock/demo mode).")
    if DEBUG:
        print("[lora_transport_locomm] Import error:", repr(e))

    # --- Minimal mock LoCommAPI implementation for UI/demo purposes --- #
    class _MockLoCommAPI:
        def __init__(self):
            self._connected = False

        def connect_to_device(self) -> bool:
            # Simulate successful connection with minimal delay
            self._connected = True
            if DEBUG:
                print("[MockLoCommAPI] connect_to_device -> True")
            return True

        def disconnect_from_device(self) -> bool:
            self._connected = False
            if DEBUG:
                print("[MockLoCommAPI] disconnect_from_device -> True")
            return True

        def enter_password(self, password: str) -> bool:
            # Accept any non-empty password in mock mode with minimal delay
            ok = bool(password)
            if DEBUG:
                print(f"[MockLoCommAPI] enter_password('{password[:4]}...') -> {ok}")
            return ok

        def set_password(self, old: str, new: str) -> bool:
            if DEBUG:
                print(f"[MockLoCommAPI] set_password -> True")
            return True

        def reset_password(self, password: str) -> bool:
            if DEBUG:
                print(f"[MockLoCommAPI] reset_password -> True")
            return True

        def send_message(self, name: str, message: str) -> bool:
            # pretend send succeeded
            if DEBUG:
                print(f"[MockLoCommAPI] send_message('{name}', '{message[:30]}...') -> True")
            return True

        def receive_message(self) -> tuple[str, str]:
            # Mock receives: block briefly then return nothing (simulate no incoming)
            # To simulate an incoming message periodically, sleep and return a message.
            time.sleep(0.2)
            # By default no message - return empty strings
            return ("", "")

        def pair_devices(self) -> bool:
            return True
        def stop_pair(self) -> bool:
            return True
        def delete_keys(self) -> bool:
            return True

    LoCommAPI = _MockLoCommAPI()


# ---------------- Transport class (same external API) ---------------- #
class LoCommTransport:
    """
    Transport adapter used by GUI. start(password) connects/authenticates.
    If LoCommAPI is mocked, this runs in demo mode but keeps the same behavior.
    """
    def __init__(self, ui_root: tk.Misc):
        self.root = ui_root
        self.on_receive: Optional[Callable[[str, str, float], None]] = None
        self.on_status: Optional[Callable[[str], None]] = None
        self.running = False
        self._rx_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    # ---------------- Connection control ---------------- #
    def start(self, password: str) -> bool:
        """
        Connect and authenticate. Returns True on success.
        In demo/mock mode this will always succeed for non-empty password.
        """
        # Try to use LoCommAPI.connect_to_device() if available
        try:
            if hasattr(LoCommAPI, "connect_to_device"):
                ok = LoCommAPI.connect_to_device()
            else:
                # If import succeeded but API missing function, fail
                ok = False
        except Exception as e:
            if DEBUG:
                print("[LoCommTransport] connect_to_device raised:", repr(e))
            ok = False

        if not ok:
            # If real API failed, but it's the injected mock we used above,
            # attempt to treat it as ok. Otherwise signal failure.
            # We already replaced LoCommAPI with a mock in import-time failure,
            # so this branch mostly helps in strange cases.
            if LoCommAPI is not None and LoCommAPI.__class__.__name__.startswith("_Mock"):
                if self.on_status:
                    self.on_status("Connected (mock)")
                self.running = True
                self._start_rx_thread()
                return True

            if self.on_status:
                self.on_status("Connection failed (device not found)")
            return False

        if self.on_status:
            self.on_status("Connected to device, verifying password...")

        # Authenticate
        try:
            auth_ok = LoCommAPI.enter_password(password)
        except Exception as e:
            if DEBUG:
                print("[LoCommTransport] enter_password error:", repr(e))
            auth_ok = False

        if not auth_ok:
            if self.on_status:
                self.on_status("Invalid device password")
            try:
                LoCommAPI.disconnect_from_device()
            except Exception:
                pass
            return False

        if self.on_status:
            self.on_status("Authenticated and ready")
        self.running = True
        self._start_rx_thread()
        return True

    def _start_rx_thread(self):
        self._stop_event.clear()
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        self._rx_thread.start()
        if DEBUG:
            print("[LoCommTransport] RX thread started")

    def stop(self):
        """Stop background receive and disconnect device."""
        self.running = False
        self._stop_event.set()
        try:
            if hasattr(LoCommAPI, "disconnect_from_device"):
                LoCommAPI.disconnect_from_device()
        except Exception:
            pass
        if self.on_status:
            self.on_status("Disconnected")
        if DEBUG:
            print("[LoCommTransport] stopped")

    # ---------------- Send ---------------- #
    def send(self, name: str, text: str):
        if not self.running:
            if self.on_status:
                self.on_status("Not connected")
            return
        try:
            if hasattr(LoCommAPI, "send_message"):
                success = LoCommAPI.send_message(name, text)
            else:
                success = False
        except Exception as e:
            if DEBUG:
                print("[LoCommTransport] send raised:", repr(e))
            success = False

        if not success:
            if self.on_status:
                self.on_status("Send failed")

    # ---------------- Device utilities ---------------- #
    def pair_devices(self) -> bool:
        if hasattr(LoCommAPI, "pair_devices"):
            try:
                ok = LoCommAPI.pair_devices()
            except Exception as e:
                if DEBUG:
                    print("[LoCommTransport] pair_devices error:", repr(e))
                ok = False
        else:
            ok = False
        if not ok and self.on_status:
            self.on_status("Pairing request failed")
        return ok

    def stop_pairing(self) -> bool:
        if hasattr(LoCommAPI, "stop_pair"):
            try:
                ok = LoCommAPI.stop_pair()
            except Exception as e:
                if DEBUG:
                    print("[LoCommTransport] stop_pair error:", repr(e))
                ok = False
        else:
            ok = False
        if not ok and self.on_status:
            self.on_status("Stop pairing failed")
        return ok

    def reset_device_password(self, new_password: str) -> bool:
        if hasattr(LoCommAPI, "reset_password"):
            try:
                ok = LoCommAPI.reset_password(new_password)
            except Exception as e:
                if DEBUG:
                    print("[LoCommTransport] reset_password error:", repr(e))
                ok = False
        else:
            ok = False
        if not ok and self.on_status:
            self.on_status("Reset password failed")
        return ok

    def set_device_password(self, old: str, new: str) -> bool:
        if hasattr(LoCommAPI, "set_password"):
            try:
                ok = LoCommAPI.set_password(old, new)
            except Exception as e:
                if DEBUG:
                    print("[LoCommTransport] set_password error:", repr(e))
                ok = False
        else:
            ok = False
        if not ok and self.on_status:
            self.on_status("Set password failed")
        return ok

    def delete_device_keys(self) -> bool:
        if hasattr(LoCommAPI, "delete_keys"):
            try:
                ok = LoCommAPI.delete_keys()
            except Exception as e:
                if DEBUG:
                    print("[LoCommTransport] delete_keys error:", repr(e))
                ok = False
        else:
            ok = False
        if not ok and self.on_status:
            self.on_status("Delete keys failed")
        return ok

    # ---------------- Background receive loop ---------------- #
    def _rx_loop(self):
        """
        Poll LoCommAPI.receive_message(). If it returns a non-empty
        (sender, msg), schedule a callback to the UI thread.
        """
        if DEBUG:
            print("[LoCommTransport] entering rx loop")
        while not self._stop_event.is_set():
            try:
                if hasattr(LoCommAPI, "receive_message"):
                    sender, msg = LoCommAPI.receive_message()
                else:
                    sender, msg = ("", "")
            except Exception as e:
                if DEBUG:
                    print("[LoCommTransport] receive_message error:", repr(e))
                sender, msg = ("", "")
            if sender and msg:
                if self.on_receive:
                    ts = time.time()
                    # Schedule on UI thread to keep thread-safe interaction with Tk
                    def safe_callback():
                        try:
                            self.on_receive(sender, msg, ts)
                        except Exception as e:
                            if DEBUG:
                                print("[LoCommTransport] Callback error:", repr(e))

                    self.root.after(0, safe_callback)
            # keep loop responsive
            time.sleep(0.2)
        if DEBUG:
            print("[LoCommTransport] exiting rx loop")
