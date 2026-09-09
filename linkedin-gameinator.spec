# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build for LinkedIn-GameInator.

Bundles SWI-Prolog so that the Sudoku resolver works on a machine that does not
have it installed. If SWI-Prolog is missing at *build* time the executable is
still produced, just without it: the application then starts normally and only
tells the user to install SWI-Prolog when a Sudoku grid is opened.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(SPECPATH) / "packaging"))

from collect_swipl import SwiplNotFound, collect  # noqa: E402

try:
    swipl_binaries, swipl_datas = collect()
    print(f"[spec] bundling SWI-Prolog: {len(swipl_datas)} home entries")
except SwiplNotFound as error:
    print(f"[spec] WARNING: building without SWI-Prolog ({error})")
    swipl_binaries, swipl_datas = [], []

a = Analysis(
    ["src/linkedin_gameinator/__main__.py"],
    pathex=["src"],
    binaries=swipl_binaries,
    datas=[("src/Sudoku/sudoku_resolver.pl", "Sudoku"), *swipl_datas],
    hiddenimports=[
        "selenium.webdriver.firefox.webdriver",
        "pyswip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["packaging/runtime_hook_swipl.py"],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="linkedin-gameinator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
