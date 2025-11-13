"""Shared state for the currently active chatroom and its members."""
from __future__ import annotations

from typing import Iterable, Set


_active_members: Set[str] = set()
_active_code: str | None = None


def set_active_chatroom(code: str, members: Iterable[str]) -> None:
    """Set current chatroom code and member list."""
    global _active_code, _active_members
    _active_code = code
    _active_members = set(members)


def add_member(member_id: str) -> None:
    """Add a single member to the active chatroom."""
    global _active_members
    _active_members.add(member_id)


def get_active_members() -> Set[str]:
    """Retrieve the IDs of the currently active members."""
    return set(_active_members)


def get_active_code() -> str | None:
    """Return the active chatroom code, if any."""
    return _active_code
