"""
Centralized validation utilities for the LoRa Chat application.
"""
from typing import Set

# Constants for validation
ASCII_RANGE: Set[int] = set(range(0x20, 0x7F))
MAX_CRED_LEN = 32


def is_printable_ascii(text: str) -> bool:
    """
    Check if a string contains only printable ASCII characters.

    Args:
        text: The string to validate

    Returns:
        True if all characters are printable ASCII, False otherwise
    """
    return all(ord(c) in ASCII_RANGE for c in text)


def enforce_ascii_and_limit(text: str) -> str:
    """
    Filter text to contain only printable ASCII characters and enforce length limit.

    Args:
        text: The input text to filter

    Returns:
        Filtered text with only printable ASCII characters and length limit applied
    """
    return ''.join(c for c in text if ord(c) in ASCII_RANGE)[:MAX_CRED_LEN]


def validate_credentials(username: str, password: str) -> tuple[bool, str]:
    """
    Validate username and password credentials.

    Args:
        username: Username to validate
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username or not password:
        return False, "Username and password required."

    if not is_printable_ascii(username) or not is_printable_ascii(password):
        return False, "Only printable ASCII allowed."

    if len(username) > MAX_CRED_LEN or len(password) > MAX_CRED_LEN:
        return False, f"Username and password must be {MAX_CRED_LEN} characters or less."

    return True, ""
