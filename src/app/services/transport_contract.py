"""
Transport contract definitions shared by all backends.
Provides dataclasses for pairing, messages, and status updates
so every backend—mock, demo, or production—speaks the same language.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Dict, Literal, Optional


class TransportStatusLevel(str, Enum):
    """Normalized status levels used by the UI and status manager."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass(frozen=True)
class PairingContext:
    """
    Metadata provided when initiating a transport session.
    Additional backend-specific information can live inside metadata.
    """

    device_id: str
    device_name: str
    mode: Literal["pin", "demo", "mock", "hardware"] = "pin"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransportMessage:
    """Normalized representation of LoRa payloads exchanged between peers."""

    sender: str
    payload: str
    timestamp: float = field(default_factory=lambda: time.time())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender": self.sender,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransportMessage":
        return cls(
            sender=data.get("sender", ""),
            payload=data.get("payload", ""),
            timestamp=float(data.get("timestamp", time.time())),
            metadata=data.get("metadata") or {},
        )


@dataclass(frozen=True)
class TransportStatus:
    """Structured status updates emitted by transport backends."""

    text: str
    level: TransportStatusLevel = TransportStatusLevel.INFO
    detail: Optional[str] = None

