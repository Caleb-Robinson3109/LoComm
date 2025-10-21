import json
import os
import hashlib

# Path to users.json file
USER_FILE = os.path.join(os.path.dirname(__file__), "users.json")


# ---------------- Utility Functions ---------------- #
def _hash_password(password: str) -> str:
    """Return SHA-256 hash of password as hex string."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users() -> dict:
    """Load user data from JSON file (username: hashed_password)."""
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users: dict):
    """Save user data to JSON file."""
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ---------------- Core Functions ---------------- #
def register_user(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user if username is unique.
    Passwords are stored as SHA-256 hashes.
    """
    users = load_users()
    if username in users:
        return False, "Username already exists!"

    users[username] = _hash_password(password)
    save_users(users)
    return True, "User registered successfully."


def validate_login(username: str, password: str) -> bool:
    """
    Check if username/password combination is valid.
    Password is hashed before comparison.
    """
    users = load_users()
    if username not in users:
        return False

    hashed = _hash_password(password)
    return users[username] == hashed
