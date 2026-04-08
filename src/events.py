"""Structured event emitter for UI telemetry."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any


def emit_event(name: str, payload: dict[str, Any] | None = None) -> None:
    event: dict[str, Any] = {
        "name": name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if payload:
        event.update(payload)

    try:
        sys.stdout.write(f"EVENT {json.dumps(event, ensure_ascii=False)}\n")
        sys.stdout.flush()
    except Exception:
        # Events are best-effort; avoid breaking the CLI on emit errors.
        pass
