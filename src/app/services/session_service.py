"""
Session persistence and management service.
Handles loading and saving session state to disk.
"""
from __future__ import annotations

import json
from pathlib import Path


from utils.state.session import Session


class SessionService:
    """Manages session persistence and hydration."""

    def __init__(self):
        self.base_dir = Path.home() / ".locomm"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.base_dir / "session.json"

    def load(self) -> dict | None:
        """Load raw session data from disk."""
        if not self.path.exists():
            return None
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError):
            return None

    def save(self, session: Session) -> None:
        """Save current session state to disk."""
        local_name = getattr(session, "local_device_name", "Orion") or "Orion"
        if local_name == "This Device":
            local_name = "Orion"
            
        data = {
            "device_id": session.device_id,
            "device_name": session.device_name,
            "local_device_name": local_name,
            "paired_at": session.paired_at,
            "transport_profile": getattr(session, "transport_profile", "auto"),
        }
        try:
            with self.path.open("w", encoding="utf-8") as handle:
                json.dump(data, handle)
        except OSError:
            pass

    def clear(self) -> None:
        """Clear persisted session data."""
        try:
            if self.path.exists():
                self.path.unlink()
        except OSError:
            pass

    def hydrate_session(self, session: Session) -> None:
        """Populate a Session object with persisted data."""
        cached = self.load()
        if not cached:
            return
            
        session.device_id = cached.get("device_id", "")
        session.device_name = cached.get("device_name", "")
        
        local_name = cached.get("local_device_name") or "Orion"
        if local_name == "This Device":
            local_name = "Orion"
        session.local_device_name = local_name
        
        session.paired_at = cached.get("paired_at", 0.0)
        session.transport_profile = cached.get("transport_profile", "auto")
