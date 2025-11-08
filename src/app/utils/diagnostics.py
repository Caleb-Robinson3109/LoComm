"""
Lightweight diagnostics logger for transport and session events.
Writes JSON lines to ~/.locomm/diagnostics.log and provides helpers
for exporting or retrieving recent entries.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DIAGNOSTICS_PATH = Path.home() / ".locomm" / "diagnostics.log"
EXPORT_PATH = Path.home() / ".locomm" / "diagnostics_export.json"


def _ensure_dir() -> None:
    DIAGNOSTICS_PATH.parent.mkdir(parents=True, exist_ok=True)


def log_transport_event(event_type: str, payload: Dict[str, Any]) -> None:
    _ensure_dir()
    entry = {
        "ts": time.time(),
        "event": event_type,
        "payload": payload,
    }
    try:
        with DIAGNOSTICS_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def read_recent_events(limit: int = 50) -> List[Dict[str, Any]]:
    if not DIAGNOSTICS_PATH.exists():
        return []
    try:
        with DIAGNOSTICS_PATH.open("r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError:
        return []
    entries = [json.loads(line) for line in lines[-limit:] if line.strip()]
    return entries


def export_diagnostics(target: Optional[Path] = None) -> Optional[Path]:
    events = read_recent_events(limit=500)
    if not events:
        return None
    target_path = target or EXPORT_PATH
    try:
        with target_path.open("w", encoding="utf-8") as handle:
            json.dump(events, handle, indent=2)
        return target_path
    except OSError:
        return None
