"""Enhanced message models and managers for the redesigned chat system."""
import time
import uuid
from enum import Enum
from typing import List, Optional, Callable, Any
from dataclasses import dataclass, field


class MessageStatus(Enum):
    """Status indicators for message delivery."""
    PENDING = "pending"          # Message queued for sending
    SENT = "sent"               # Message sent to transport
    DELIVERED = "delivered"     # Message delivered to peer
    FAILED = "failed"           # Message sending failed


class MessageType(Enum):
    """Types of messages in the chat system."""
    TEXT = "text"              # Regular text message
    SYSTEM = "system"          # System notification
    ERROR = "error"            # Error message
    STATUS = "status"          # Status update


@dataclass
class ChatMessage:
    """Enhanced message model with rich metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    content: str = ""
    timestamp: float = field(default_factory=time.time)
    status: MessageStatus = MessageStatus.PENDING
    message_type: MessageType = MessageType.TEXT
    metadata: dict = field(default_factory=dict)

    @property
    def formatted_time(self) -> str:
        """Get formatted timestamp for display."""
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))

    @property
    def is_own_message(self) -> bool:
        """Check if this is the current user's message."""
        return self.sender.lower() == "me"

    @property
    def status_icon(self) -> str:
        """Get status icon for display."""
        icons = {
            MessageStatus.PENDING: "⏳",
            MessageStatus.SENT: "✓",
            MessageStatus.DELIVERED: "✓✓",
            MessageStatus.FAILED: "❌"
        }
        return icons.get(self.status, "")


class MessageManager:
    """Manages chat messages with efficient operations."""

    def __init__(self):
        self.messages: List[ChatMessage] = []
        self.message_callbacks: List[Callable[[ChatMessage], None]] = []
        self.history_callbacks: List[Callable[[], None]] = []

    def add_message(self, message: ChatMessage) -> None:
        """Add a new message and notify callbacks."""
        self.messages.append(message)
        self._notify_message_callbacks(message)

    def add_message_by_parts(self, sender: str, content: str,
                           message_type: MessageType = MessageType.TEXT,
                           status: MessageStatus = MessageStatus.PENDING,
                           metadata: Optional[dict] = None) -> ChatMessage:
        """Add a message by individual parts."""
        message = ChatMessage(
            sender=sender,
            content=content,
            message_type=message_type,
            status=status,
            metadata=metadata or {}
        )
        self.add_message(message)
        return message

    def update_message_status(self, message_id: str, status: MessageStatus) -> bool:
        """Update the status of a specific message."""
        for message in self.messages:
            if message.id == message_id:
                old_status = message.status
                message.status = status
                # Only notify if status actually changed
                if old_status != status:
                    self._notify_message_callbacks(message)
                return True
        return False

    def get_recent_messages(self, limit: int = 50) -> List[ChatMessage]:
        """Get the most recent messages (most efficient for display)."""
        return self.messages[-limit:] if limit > 0 else self.messages

    def get_messages_since(self, timestamp: float) -> List[ChatMessage]:
        """Get messages newer than the given timestamp."""
        return [msg for msg in self.messages if msg.timestamp > timestamp]

    def clear_history(self) -> None:
        """Clear all messages and notify callbacks."""
        self.messages.clear()
        self._notify_history_callbacks()

    def get_history_text(self) -> List[str]:
        """Get formatted history text for export."""
        lines = []
        for msg in self.messages:
            if msg.message_type == MessageType.SYSTEM:
                lines.append(f"[{msg.formatted_time}] {msg.content}")
            else:
                status_str = f" {msg.status_icon}" if msg.is_own_message else ""
                lines.append(f"[{msg.formatted_time}] {msg.sender}: {msg.content}{status_str}")
        return lines

    def on_message_update(self, callback: Callable[[ChatMessage], None]) -> None:
        """Register callback for individual message updates."""
        self.message_callbacks.append(callback)

    def on_history_update(self, callback: Callable[[], None]) -> None:
        """Register callback for history changes."""
        self.history_callbacks.append(callback)

    def _notify_message_callbacks(self, message: ChatMessage) -> None:
        """Notify all registered message callbacks."""
        for callback in self.message_callbacks:
            try:
                callback(message)
            except Exception as e:
                print(f"Error in message callback: {e}")

    def _notify_history_callbacks(self) -> None:
        """Notify all registered history callbacks."""
        for callback in self.history_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in history callback: {e}")
