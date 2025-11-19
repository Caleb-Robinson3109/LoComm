from dataclasses import dataclass


@dataclass
class Session:
    """Lightweight container for the currently paired device."""

    device_name: str = ""      # Peer device name
    device_id: str = ""        # Peer device ID
    local_device_name: str = "Orion"  # Local device name for proper message attribution
    paired_at: float = 0.0
    transport_profile: str = "auto"

    def clear(self):
        self.device_name = ""
        self.device_id = ""
        self.local_device_name = ""
        self.paired_at = 0.0
        self.transport_profile = "auto"
