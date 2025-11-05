"""
Authentication service that handles login/registration logic.
Provides clean separation between UI and business logic.
"""
import threading
import time
from typing import Callable, Optional, Tuple
from dataclasses import dataclass

from utils.user_store import register_user, validate_login
from utils.validation import validate_credentials
from utils.status_manager import get_status_manager


@dataclass
class AuthResult:
    """Result of authentication operation"""
    success: bool
    error_message: Optional[str] = None
    username: Optional[str] = None


class AuthService:
    """
    Authentication service that handles login and registration operations.
    Provides clean callbacks for UI updates without complex callback chains.
    """

    def __init__(self, transport):
        """
        Initialize authentication service.

        Args:
            transport: LoCommTransport instance
        """
        self.transport = transport
        self.status_manager = get_status_manager()
        self._current_username: Optional[str] = None
        self._is_authenticating = False

    def register_user(self, username: str, password: str) -> AuthResult:
        """
        Register a new user.

        Args:
            username: Username to register
            password: Password for the new user

        Returns:
            AuthResult with success status and error message if any
        """
        # Use centralized validation
        is_valid, error_msg = validate_credentials(username, password)
        if not is_valid:
            return AuthResult(success=False, error_message=error_msg)

        # Register user using existing store
        success, msg = register_user(username, password)
        if success:
            return AuthResult(success=True, username=username)
        else:
            return AuthResult(success=False, error_message=msg)

    def validate_credentials(self, username: str, password: str) -> AuthResult:
        """
        Validate user credentials.

        Args:
            username: Username to validate
            password: Password to validate

        Returns:
            AuthResult with validation result
        """
        # Use centralized validation
        is_valid, error_msg = validate_credentials(username, password)
        if not is_valid:
            return AuthResult(success=False, error_message=error_msg)

        # Validate against user store
        if validate_login(username, password):
            return AuthResult(success=True, username=username)
        else:
            return AuthResult(success=False, error_message="Incorrect username or password.")

    def authenticate_with_device(self, username: str, password: str,
                                success_callback: Callable[[], None],
                                error_callback: Callable[[str], None],
                                progress_callback: Optional[Callable[[bool], None]] = None) -> bool:
        """
        Authenticate with LoComm device.

        Args:
            username: Username for authentication
            password: Password for authentication
            success_callback: Called when authentication succeeds
            error_callback: Called when authentication fails with error message
            progress_callback: Called to update progress state (True=loading, False=idle)

        Returns:
            True if authentication was initiated, False if already in progress
        """
        if self._is_authenticating:
            return False

        # Validate credentials locally first
        cred_result = self.validate_credentials(username, password)
        if not cred_result.success:
            error_callback(cred_result.error_message or "Invalid credentials")
            return False

        self._is_authenticating = True
        self._current_username = username

        # Update progress indicator
        if progress_callback:
            progress_callback(True)

        def _authenticate():
            try:
                # Start transport authentication
                success = self.transport.start(password)

                # Switch back to UI thread
                def _finish_auth(success):
                    self._is_authenticating = False

                    if progress_callback:
                        progress_callback(False)

                    if success:
                        self.status_manager.update_status("Authenticated and ready")
                        success_callback()
                    else:
                        error_callback("Connection or password invalid.")

                # Schedule on UI thread
                self.transport.root.after(0, lambda: _finish_auth(success))

            except Exception as e:
                # Handle any unexpected errors
                def _handle_error():
                    self._is_authenticating = False
                    if progress_callback:
                        progress_callback(False)
                    error_callback(f"Authentication error: {str(e)}")

                self.transport.root.after(0, _handle_error)

        # Start authentication in background thread
        threading.Thread(target=_authenticate, daemon=True).start()
        return True

    def logout(self, logout_callback: Callable[[], None]):
        """
        Logout from the system.

        Args:
            logout_callback: Called when logout is complete
        """
        def _logout():
            try:
                self.transport.stop()
                if logout_callback:
                    self.transport.root.after(0, logout_callback)
            except Exception:
                # Always call logout callback even if transport error
                if logout_callback:
                    self.transport.root.after(0, logout_callback)

        threading.Thread(target=_logout, daemon=True).start()

    def is_authenticating(self) -> bool:
        """Check if authentication is currently in progress."""
        return self._is_authenticating

    def get_current_username(self) -> Optional[str]:
        """Get the current username if authenticated."""
        return self._current_username

    def cancel_authentication(self):
        """Cancel ongoing authentication if possible."""
        if self._is_authenticating:
            self._is_authenticating = False
            try:
                self.transport.stop()
            except Exception:
                pass  # Ignore errors during cancellation
