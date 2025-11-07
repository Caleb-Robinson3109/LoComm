"""
PIN-based authentication system for the LoRa Chat application.
Replaces legacy credential flows with secure authentication.
"""
import random
import string
import secrets
import hashlib
import time
from typing import Optional, Dict, Set, List
from datetime import datetime, timedelta
from utils.design_system import Colors


class SecurityTracker:
    """CRITICAL FIX: Track failed attempts and implement rate limiting/lockout."""

    def __init__(self):
        self.failed_attempts: Dict[str, List[datetime]] = {}  # IP/host -> list of attempt times
        self.locked_accounts: Dict[str, datetime] = {}  # IP/host -> lockout expiry
        self.max_attempts = 5  # Max attempts before lockout
        self.lockout_duration_minutes = 15  # 15-minute lockout
        self.attempt_window_minutes = 10  # Track attempts over 10 minutes
        self.initial_delay_seconds = 1  # Start with 1-second delay
        self.max_delay_seconds = 300  # Max 5-minute delay

    def record_attempt(self, identifier: str) -> tuple[bool, str, float]:
        """
        Record an authentication attempt and return (is_blocked, reason, wait_time).

        Returns:
            is_blocked: True if attempt should be blocked
            reason: Reason for blocking (if any)
            wait_time: Seconds to wait before retrying
        """
        now = datetime.now()

        # Check if account is currently locked
        if identifier in self.locked_accounts:
            lockout_end = self.locked_accounts[identifier]
            if now < lockout_end:
                remaining = (lockout_end - now).total_seconds()
                return True, f"Account locked for {(lockout_end - now).seconds // 60} more minutes", remaining
            else:
                # Lockout expired, remove it
                del self.locked_accounts[identifier]

        # Clean up old attempts
        if identifier in self.failed_attempts:
            # Remove attempts older than the window
            cutoff_time = now - timedelta(minutes=self.attempt_window_minutes)
            self.failed_attempts[identifier] = [
                attempt_time for attempt_time in self.failed_attempts[identifier]
                if attempt_time > cutoff_time
            ]
        else:
            self.failed_attempts[identifier] = []

        # Check if max attempts exceeded
        if len(self.failed_attempts[identifier]) >= self.max_attempts:
            # Lock the account
            lockout_end = now + timedelta(minutes=self.lockout_duration_minutes)
            self.locked_accounts[identifier] = lockout_end
            return True, f"Too many failed attempts. Account locked for {self.lockout_duration_minutes} minutes", 0

        # Add this attempt
        self.failed_attempts[identifier].append(now)

        # Calculate delay based on number of recent failures
        recent_failures = len(self.failed_attempts[identifier])
        delay = min(self.initial_delay_seconds * (2 ** (recent_failures - 1)), self.max_delay_seconds)

        # If we have failures, suggest a delay
        if recent_failures > 0:
            return False, f"Warning: {recent_failures} recent failed attempts", delay

        return False, "OK", 0

    def reset_attempts(self, identifier: str):
        """Reset failed attempts for an identifier after successful login."""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
        if identifier in self.locked_accounts:
            del self.locked_accounts[identifier]


class PINAuthentication:
    """
    CRITICAL FIX: Secure PIN-based device authentication and pairing.
    Implements proper security measures to prevent brute force attacks.
    """

    def __init__(self):
        self._active_pins: Dict[str, Dict] = {}  # pin_hash -> {'device_info': dict, 'expires': datetime, 'created': datetime}
        self._device_pins: Dict[str, str] = {}  # device_id -> pin_hash
        self._connected_devices: Dict[str, Dict] = {}  # device_id -> device_info
        self._pin_timeout_minutes = 10  # PIN expires after 10 minutes
        self._security_tracker = SecurityTracker()

        # CRITICAL FIX: Use longer, more secure PINs
        self._pin_length = 8  # Increased from 5 to 8 digits
        self._pin_charset = string.digits  # Still digits for usability but longer

    def _hash_pin(self, pin: str) -> str:
        """CRITICAL FIX: Hash PINs to prevent storage in plaintext."""
        return hashlib.sha256(pin.encode('utf-8')).hexdigest()[:16]  # Use first 16 chars for storage

    def _generate_secure_pin(self) -> str:
        """CRITICAL FIX: Generate cryptographically secure PIN."""
        # Use secrets module for cryptographic randomness
        return ''.join(secrets.choice(self._pin_charset) for _ in range(self._pin_length))

    def generate_pin(self, device_id: str, device_name: str) -> str:
        """
        CRITICAL FIX: Generate a new secure PIN for device pairing.

        Args:
            device_id: Device identifier
            device_name: Device display name

        Returns:
            Secure PIN string (8 digits)
        """
        # Generate unique secure PIN
        attempts = 0
        while attempts < 1000:  # Prevent infinite loop
            pin = self._generate_secure_pin()
            pin_hash = self._hash_pin(pin)

            if pin_hash not in self._active_pins:
                # Store PIN with expiration
                expires = datetime.now() + timedelta(minutes=self._pin_timeout_minutes)
                self._active_pins[pin_hash] = {
                    'device_id': device_id,
                    'device_name': device_name,
                    'created': datetime.now(),
                    'expires': expires
                }
                self._device_pins[device_id] = pin_hash
                return pin

            attempts += 1

        # If we somehow can't generate a unique PIN, raise an error
        raise RuntimeError("Unable to generate unique PIN after 1000 attempts")

    def verify_pin(self, pin: str, client_identifier: str = "unknown") -> tuple[Optional[Dict], str, float]:
        """
        CRITICAL FIX: Verify a PIN with security measures and rate limiting.

        Args:
            pin: PIN to verify
            client_identifier: Identifier for rate limiting (IP, user agent, etc.)

        Returns:
            Tuple of (device_info dict if valid, error_message, wait_time_seconds)
        """
        # Check security first
        is_blocked, reason, wait_time = self._security_tracker.record_attempt(client_identifier)
        if is_blocked:
            return None, reason, wait_time

        # Validate PIN format
        if not self.validate_pin_format(pin):
            return None, f"PIN must be exactly {self._pin_length} digits", 0

        pin_hash = self._hash_pin(pin)

        # Check if PIN exists
        if pin_hash not in self._active_pins:
            return None, "Invalid PIN", 0

        pin_data = self._active_pins[pin_hash]

        # Check if PIN has expired
        if datetime.now() > pin_data['expires']:
            self._cleanup_expired_pin(pin_hash)
            return None, "PIN has expired", 0

        # Success - reset failed attempts and clean up PIN
        self._security_tracker.reset_attempts(client_identifier)

        device_info = {
            'id': pin_data['device_id'],
            'name': pin_data['device_name']
        }
        self._cleanup_used_pin(pin_hash)

        return device_info, "Success", 0

    def is_pin_expired(self, pin: str) -> bool:
        """Check if a PIN has expired."""
        pin_hash = self._hash_pin(pin)
        if pin_hash not in self._active_pins:
            return True
        return datetime.now() > self._active_pins[pin_hash]['expires']

    def get_remaining_pin_time(self, pin: str) -> int:
        """
        Get remaining time for PIN in minutes.

        Args:
            pin: PIN to check

        Returns:
            Minutes remaining before expiry (0 if expired/not found)
        """
        pin_hash = self._hash_pin(pin)
        if pin_hash not in self._active_pins:
            return 0

        expires = self._active_pins[pin_hash]['expires']
        remaining = expires - datetime.now()
        return max(0, int(remaining.total_seconds() / 60))

    def cleanup_expired_pins(self):
        """Clean up all expired PINs."""
        current_time = datetime.now()
        expired_pins = []

        for pin_hash, data in self._active_pins.items():
            if current_time > data['expires']:
                expired_pins.append(pin_hash)

        for pin_hash in expired_pins:
            self._cleanup_expired_pin(pin_hash)

    def _cleanup_expired_pin(self, pin_hash: str):
        """Clean up expired PIN."""
        if pin_hash in self._active_pins:
            device_id = self._active_pins[pin_hash]['device_id']
            del self._active_pins[pin_hash]
            if device_id in self._device_pins:
                del self._device_pins[device_id]

    def _cleanup_used_pin(self, pin_hash: str):
        """Clean up used PIN."""
        if pin_hash in self._active_pins:
            device_id = self._active_pins[pin_hash]['device_id']
            del self._active_pins[pin_hash]
            if device_id in self._device_pins:
                del self._device_pins[device_id]

    def get_active_pins(self) -> Dict[str, Dict]:
        """Get all currently active (non-expired) PINs."""
        self.cleanup_expired_pins()
        return self._active_pins.copy()

    def revoke_pin(self, device_id: str):
        """Manually revoke a device's PIN."""
        if device_id in self._device_pins:
            pin_hash = self._device_pins[device_id]
            self._cleanup_used_pin(pin_hash)

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
        CRITICAL FIX: Validate secure PIN format (8 digits only).

        Args:
            pin: PIN to validate

        Returns:
            True if PIN is valid format
        """
        return len(pin) == self._pin_length and pin.isdigit()

    def generate_device_name(self) -> str:
        """
        Generate a friendly device name for display.

        Returns:
            Device name string
        """
        # Generate a unique device name using timestamp and secure random suffix
        timestamp = datetime.now().strftime("%m%d%H%M")
        suffix = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(2))
        return f"Device-{timestamp}-{suffix}"

    def get_security_status(self, client_identifier: str) -> Dict:
        """Get security status for a client identifier."""
        now = datetime.now()

        # Check if locked
        is_locked = False
        lockout_remaining = 0
        if client_identifier in self._security_tracker.locked_accounts:
            lockout_end = self._security_tracker.locked_accounts[client_identifier]
            if now < lockout_end:
                is_locked = True
                lockout_remaining = (lockout_end - now).total_seconds()
            else:
                del self._security_tracker.locked_accounts[client_identifier]

        # Get recent attempts
        recent_attempts = 0
        if client_identifier in self._security_tracker.failed_attempts:
            cutoff_time = now - timedelta(minutes=self._security_tracker.attempt_window_minutes)
            recent_attempts = len([
                attempt for attempt in self._security_tracker.failed_attempts[client_identifier]
                if attempt > cutoff_time
            ])

        return {
            'is_locked': is_locked,
            'lockout_remaining_seconds': lockout_remaining,
            'recent_failed_attempts': recent_attempts,
            'max_attempts': self._security_tracker.max_attempts,
            'attempts_remaining': max(0, self._security_tracker.max_attempts - recent_attempts)
        }


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
    """Generate a new secure pairing PIN."""
    auth = get_pin_auth()
    if device_name is None:
        device_name = auth.generate_device_name()
    return auth.generate_pin(device_id, device_name)


def verify_pairing_pin(pin: str, client_identifier: str = "unknown") -> tuple[Optional[Dict], str, float]:
    """Verify a pairing PIN and get device info with security measures."""
    auth = get_pin_auth()
    return auth.verify_pin(pin, client_identifier)


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


def get_security_status(client_identifier: str = "unknown") -> Dict:
    """Get security status for a client."""
    return get_pin_auth().get_security_status(client_identifier)
