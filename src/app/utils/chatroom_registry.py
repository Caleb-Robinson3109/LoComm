"""Shared state for the currently active chatroom and its members."""
from __future__ import annotations

from typing import Callable, Iterable, Set


_active_members: Set[str] = set()
_active_code: str | None = None
_listeners: list[Callable[[str | None], None]] = []


def set_active_chatroom(code: str, members: Iterable[str]) -> None:
    """Set current chatroom code and member list."""
    global _active_code, _active_members
    print(f"Call to set_active_chatroom: setting _active_code to {code}")
    _active_code = code
    _active_members = set(members)
    _notify_listeners()


def add_member(member_id: str) -> None:
    """Add a single member to the active chatroom."""
    global _active_members
    _active_members.add(member_id)
    _notify_listeners()


def get_active_members() -> Set[str]:
    """Retrieve the IDs of the currently active members."""
    return set(_active_members)


def get_active_code() -> str | None:
    
    global _active_code
    """Return the active chatroom code, if any."""
    print(f"Call to get_active_code: code is {_active_code}")
    return _active_code


def format_chatroom_code(code: str | None) -> str:
    """Return code formatted with dash groups or placeholder text."""
    if not code:
        return "No Chatrooms Connected"
    clean = ''.join(ch for ch in code if ch.isalnum())
    if not clean:
        return "No Chatrooms Connected"
    return '-'.join(clean[i:i+5] for i in range(0, len(clean), 5))


def register_chatroom_listener(callback: Callable[[str | None], None]):
    global _active_code
    if callback not in _listeners:
        _listeners.append(callback)
        callback(_active_code)


def unregister_chatroom_listener(callback: Callable[[str | None], None]):
    if callback in _listeners:
        _listeners.remove(callback)


def clear_chatroom():
    print("Call to clear chatroom")
    global _active_code, _active_members
    _active_code = None
    _active_members.clear()
    _notify_listeners()


def _notify_listeners():
    global _active_code
    for callback in list(_listeners):
        try:
            callback(_active_code)
        except Exception:
            pass
