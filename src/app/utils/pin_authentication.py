"""
PIN-based authentication system for the LoRa Chat application.
Replaces traditional username/password authentication with 5-digit PIN pairing.
"""
import random
import string
from typing import Optional, Dict, Set
from datetime import datetime, timedelta
from utils.design_system import Colors


class PINAuthentication:
    """
    Manages PIN-based device authentication and pairing.
    Provides secure 5-digit PIN generation and verification.
    """

    def __init__(self):
        self._active_pins: Dict[str, Dict] = {}  # pin -> {'device_info': dict, 'expires': datetime}
        self._device_pins: Dict[str, str] = {}  # device_id -> pin
        self._connected_devices: Dict[str, Dict] = {}  # device_id -> device_info
        self._pin_timeout_minutes = 10  # PIN expires after 10 minutes

    def generate_pin(self, device_id: str, device_name: str) -> str:
        """
        Generate a new 5-digit PIN for device pairing.

        Args:
            device_id: Device identifier
            device_name: Device display name

        Returns:
            5-digit PIN string
        """
        # Generate unique 5-digit PIN
        while True:
            pin = ''.join(random.choices(string.digits, k=5))
            if pin not in self._active_pins:
                break

        # Store PIN with expiration
        expires = datetime.now() + timedelta(minutes=self._pin_timeout_minutes)
        self._active_pins[pin] = {
            'device_id': device_id,
            'device_name': device_name,
            'created': datetime.now(),
            'expires': expires
        }
        self._device_pins[device_id] = pin

        return pin

    def verify_pin(self, pin: str) -> Optional[Dict]:
        """
        Verify a PIN and return associated device info if valid.

        Args:
            pin: 5-digit PIN to verify

        Returns:
            Device info dict if PIN is valid, None otherwise
        """
        if pin not in self._active_pins:
            return None

        pin_data = self._active_pins[pin]

        # Check if PIN has expired
        if datetime.now() > pin_data['expires']:
            self._cleanup_expired_pin(pin)
            return None

        # Clean up used PIN
        device_info = {
            'id': pin_data['device_id'],
            'name': pin_data['device_name']
        }
        self._cleanup_used_pin(pin)

        return device_info

    def is_pin_expired(self, pin: str) -> bool:
        """Check if a PIN has expired."""
        if pin not in self._active_pins:
            return True
        return datetime.now() > self._active_pins[pin]['expires']

    def get_remaining_pin_time(self, pin: str) -> int:
        """
        Get remaining time for PIN in minutes.

        Args:
            pin: 5-digit PIN

        Returns:
            Minutes remaining before expiry (0 if expired/not found)
        """
        if pin not in self._active_pins:
            return 0

        expires = self._active_pins[pin]['expires']
        remaining = expires - datetime.now()
        return max(0, int(remaining.total_seconds() / 60))

    def cleanup_expired_pins(self):
        """Clean up all expired PINs."""
        current_time = datetime.now()
        expired_pins = []

        for pin, data in self._active_pins.items():
            if current_time > data['expires']:
                expired_pins.append(pin)

        for pin in expired_pins:
            self._cleanup_expired_pin(pin)

    def _cleanup_expired_pin(self, pin: str):
        """Clean up expired PIN."""
        if pin in self._active_pins:
            device_id = self._active_pins[pin]['device_id']
            del self._active_pins[pin]
            if device_id in self._device_pins:
                del self._device_pins[device_id]

    def _cleanup_used_pin(self, pin: str):
        """Clean up used PIN."""
        if pin in self._active_pins:
            device_id = self._active_pins[pin]['device_id']
            del self._active_pins[pin]
            if device_id in self._device_pins:
                del self._device_pins[device_id]

    def list_active_pins(self) -> Dict[str, Dict]:
        """Get all currently active (non-expired) PINs (alias for get_active_pins)."""
        return self.get_active_pins()

    def get_active_pins(self) -> Dict[str, Dict]:
        """Get all currently active (non-expired) PINs."""
        self.cleanup_expired_pins()
        return self._active_pins.copy()

    def revoke_pin(self, device_id: str):
        """Manually revoke a device's PIN."""
        if device_id in self._device_pins:
            pin = self._device_pins[device_id]
            self._cleanup_used_pin(pin)

    def is_device_paired(self, device_id: str) -> bool:
        """Check if a device is currently paired/connected."""
        return device_id in self._connected_devices

    def pair_device(self, device_id: str, device_info: Dict):
        """Mark a device as paired/connected."""
        self._connected_devices[device_id] = device_info

    def unpair_device(self, device_id: str):
        """Remove a device from paired/connected status."""
        if device_id in self._connected_devices:
            del self._connected_devices[device_id]
        self.revoke_pin(device_id)

    def get_paired_devices(self) -> Dict[str, Dict]:
        """Get all currently paired devices."""
        return self._connected_devices.copy()

    def validate_pin_format(self, pin: str) -> bool:
        """
        Validate PIN format (5 digits only).

        Args:
            pin: PIN to validate

        Returns:
            True if PIN is valid format
        """
        return len(pin) == 5 and pin.isdigit()

    def generate_device_name(self) -> str:
        """
        Generate a friendly device name for display.

        Returns:
            Device name string
        """
        # Generate a unique device name using timestamp and random suffix
        timestamp = datetime.now().strftime("%m%d%H%M")
        suffix = ''.join(random.choices(string.ascii_uppercase, k=2))
        return f"Device-{timestamp}-{suffix}"


# Global PIN authentication instance
_pin_auth: Optional[PINAuthentication] = None


def get_pin_auth() -> PINAuthentication:
    """Get the global PIN authentication instance."""
    global _pin_auth
    if _pin_auth is None:
        _pin_auth = PINAuthentication()
    return _pin_auth


# Convenience functions
def generate_pairing_pin(device_id: str, device_name: Optional[str] = None) -> str:
    """Generate a new pairing PIN."""
    auth = get_pin_auth()
    if device_name is None:
        device_name = auth.generate_device_name()
    return auth.generate_pin(device_id, device_name)


def verify_pairing_pin(pin: str) -> Optional[Dict]:
    """Verify a pairing PIN and get device info."""
    auth = get_pin_auth()
    return auth.verify_pin(pin)


def get_active_pairing_pins() -> Dict[str, Dict]:
    """Get all active pairing PINs."""
    return get_pin_auth().get_active_pins()


def pair_device_with_pin(device_id: str, device_info: Dict):
    """Pair a device using verified PIN."""
    get_pin_auth().pair_device(device_id, device_info)


def unpair_device(device_id: str):
    """Unpair a device."""
    get_pin_auth().unpair_device(device_id)


def get_paired_devices() -> Dict[str, Dict]:
    """Get all currently paired devices."""
    return get_pin_auth().get_paired_devices()


def is_device_paired(device_id: str) -> bool:
    """Check if device is currently paired."""
    return get_pin_auth().is_device_paired(device_id)


def validate_pin_format(pin: str) -> bool:
    """Validate PIN format."""
    return get_pin_auth().validate_pin_format(pin)
