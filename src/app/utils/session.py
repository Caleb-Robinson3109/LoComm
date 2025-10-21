from dataclasses import dataclass
from typing import Optional

@dataclass
class Session:
    username: str = ""
    password_bytes: Optional[bytearray] = None
    login_time: float = 0.0

    def clear(self):
        if self.password_bytes:
            for i in range(len(self.password_bytes)):
                self.password_bytes[i] = 0
        self.password_bytes = None
        self.username = ""
        self.login_time = 0.0
