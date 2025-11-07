from dataclasses import dataclass


@dataclass
class Session:
    """Lightweight container for the currently paired device."""

    device_name: str = ""
    device_id: str = ""
    paired_at: float = 0.0

    def clear(self):
        self.device_name = ""
        self.device_id = ""
        self.paired_at = 0.0
