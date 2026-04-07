"""Resource path helpers for local dev and PyInstaller builds."""

from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    """
    Resolve a resource path for both local dev and PyInstaller builds.

    Args:
        relative: Path relative to the packaged resource root (or src/ in dev).

    Returns:
        Absolute Path to the resource.
    """
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return (base / relative).resolve()
