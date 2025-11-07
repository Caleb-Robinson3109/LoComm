"""
Lightweight logger helper for the Locomm desktop app.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

_LOGGER: Optional[logging.Logger] = None


def get_logger(name: str = "locomm") -> logging.Logger:
    """Return a shared application logger writing to ~/.locomm/locomm.log."""
    global _LOGGER
    if _LOGGER:
        return _LOGGER

    logs_dir = Path(os.path.expanduser("~")) / ".locomm"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "locomm.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    _LOGGER = logger
    return logger
