"""
Shared session helpers for mock devices.
Centralizes tracking of the active mock device, scenario, and metadata.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from mock.device_service import MockDevice


@dataclass
class MockSessionState:
    """Tracks the mock device session state shared across backends and UI."""

    device: Optional[MockDevice] = None
    scenario: str = "default"
    pairing_mode: str = "mock"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def attach_device(self, device: MockDevice, scenario: str, mode: str):
        self.device = device
        self.scenario = scenario
        self.pairing_mode = mode
        self.metadata = {
            "scenario": scenario,
            "mode": mode,
        }

    def clear(self):
        self.device = None
        self.scenario = "default"
        self.pairing_mode = "mock"
        self.metadata.clear()


_MOCK_SESSION = MockSessionState()


def get_mock_session_state() -> MockSessionState:
    """Return the current mock session state."""
    return _MOCK_SESSION


def set_mock_session_device(device: MockDevice, scenario: str, mode: str):
    """Bind the given device as the active mock session."""
    _MOCK_SESSION.attach_device(device, scenario, mode)


def clear_mock_session():
    """Clear the current mock session."""
    _MOCK_SESSION.clear()
