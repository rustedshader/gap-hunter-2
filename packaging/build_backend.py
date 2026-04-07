"""Build the Python backend binary and stage it for Electron packaging."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "packaging" / "backend.spec"
DIST = ROOT / "packaging" / "dist"
BUILD = ROOT / "packaging" / "build"
TARGET_DIR = ROOT / "app" / "resources" / "backend"


def _binary_name() -> str:
    if sys.platform.startswith("win"):
        return "gap-hunter-backend.exe"
    return "gap-hunter-backend"


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(SPEC),
        "--distpath",
        str(DIST),
        "--workpath",
        str(BUILD),
        "--clean",
    ]

    print("Running:", " ".join(cmd))
    env = {**os.environ, "GAP_HUNTER_ROOT": str(ROOT)}
    subprocess.check_call(cmd, cwd=ROOT, env=env)

    binary_path = DIST / _binary_name()
    if not binary_path.exists():
        raise FileNotFoundError(f"Backend binary not found: {binary_path}")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    staged_path = TARGET_DIR / binary_path.name
    shutil.copy2(binary_path, staged_path)

    print(f"Staged backend: {staged_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
