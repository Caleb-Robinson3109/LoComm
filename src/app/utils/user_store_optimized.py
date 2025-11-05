"""
Optimized user store with reduced file I/O operations.
Provides caching and batch operations for better performance.
"""
import json
import os
import hashlib
import threading
from typing import Dict, Optional, Tuple

# Path to users.json file
USER_FILE = os.path.join(os.path.dirname(__file__), "users.json")


class OptimizedUserStore:
    """
    Optimized user store that caches user data and reduces file I/O operations.
    """

    def __init__(self):
        self._users_cache: Dict[str, str] = {}
        self._cache_dirty = False
        self._lock = threading.RLock()
        self._load_users()

    def _load_users(self) -> Dict[str, str]:
        """Load user data from JSON file (synchronized)"""
        with self._lock:
            if not os.path.exists(USER_FILE):
                self._users_cache = {}
                return {}

            try:
                with open(USER_FILE, "r") as f:
                    self._users_cache = json.load(f)
                return self._users_cache
            except Exception:
                self._users_cache = {}
                return {}

    def _save_users(self):
        """Save user data to JSON file (synchronized)"""
        with self._lock:
            try:
                with open(USER_FILE, "w") as f:
                    json.dump(self._users_cache, f, indent=2)
                self._cache_dirty = False
            except Exception as e:
                print(f"Failed to save users: {e}")

    def _ensure_loaded(self):
        """Ensure user data is loaded (lazy loading)"""
        if not self._users_cache:
            self._load_users()

    def _hash_password(self, password: str) -> str:
        """Return SHA-256 hash of password as hex string."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Register a new user if username is unique.
        Passwords are stored as SHA-256 hashes.
        """
        self._ensure_loaded()

        with self._lock:
            if username in self._users_cache:
                return False, "Username already exists!"

            self._users_cache[username] = self._hash_password(password)
            self._cache_dirty = True
            return True, "User registered successfully."

    def validate_login(self, username: str, password: str) -> bool:
        """
        Check if username/password combination is valid.
        Password is hashed before comparison.
        """
        self._ensure_loaded()

        with self._lock:
            if username not in self._users_cache:
                return False

            hashed = self._hash_password(password)
            return self._users_cache[username] == hashed

    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists.
        """
        self._ensure_loaded()
        return username in self._users_cache

    def get_all_users(self) -> Dict[str, str]:
        """
        Get all users (copy for safety).
        """
        self._ensure_loaded()
        with self._lock:
            return self._users_cache.copy()

    def delete_user(self, username: str) -> bool:
        """
        Delete a user (if exists).
        """
        self._ensure_loaded()

        with self._lock:
            if username in self._users_cache:
                del self._users_cache[username]
                self._cache_dirty = True
                return True
            return False

    def force_save(self):
        """Force save to disk immediately (useful for testing)"""
        with self._lock:
            if self._cache_dirty:
                self._save_users()

    def get_cache_stats(self) -> Dict:
        """Get cache statistics for debugging"""
        with self._lock:
            return {
                "users_count": len(self._users_cache),
                "cache_dirty": self._cache_dirty,
                "file_exists": os.path.exists(USER_FILE)
            }


# Global optimized user store instance
_user_store: Optional[OptimizedUserStore] = None


def get_optimized_user_store() -> OptimizedUserStore:
    """Get the global optimized user store instance."""
    global _user_store
    if _user_store is None:
        _user_store = OptimizedUserStore()
    return _user_store


# Convenience functions that use the optimized store
def register_user_optimized(username: str, password: str) -> Tuple[bool, str]:
    """Register a user using the optimized store."""
    return get_optimized_user_store().register_user(username, password)


def validate_login_optimized(username: str, password: str) -> bool:
    """Validate login using the optimized store."""
    return get_optimized_user_store().validate_login(username, password)


def user_exists_optimized(username: str) -> bool:
    """Check if user exists using the optimized store."""
    return get_optimized_user_store().user_exists(username)


def force_save_users():
    """Force save users to disk."""
    get_optimized_user_store().force_save()
