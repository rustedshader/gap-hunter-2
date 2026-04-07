# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from PyInstaller.building.datastruct import Tree

# PyInstaller does not always populate __file__ for spec files.
# Use the root injected by packaging/build_backend.py, falling back to cwd.
_root_env = os.environ.get("GAP_HUNTER_ROOT")
ROOT = Path(_root_env).resolve() if _root_env else Path.cwd().resolve()
SRC = ROOT / "src"

_datas = []
_hidden = []

# Third-party packages that bundle data or use dynamic imports
for pkg in [
    "docling",
    "langchain_community",
    "langchain_ollama",
    "llama_cpp",
]:
    _datas += collect_data_files(pkg)
    _hidden += collect_submodules(pkg)

# NIST framework assets
_datas += [(str(SRC / "nist" / "nist_config.yaml"), "nist")]
_datas += [Tree(str(SRC / "nist" / "framework-documents"), prefix="nist/framework-documents")]

block_cipher = None


a = Analysis(
    ["src/main.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=_datas,
    hiddenimports=_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="gap-hunter-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
