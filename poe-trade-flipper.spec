# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — onedir bundle (faster startup than onefile for Flask).
# Run: pyinstaller poe-trade-flipper.spec  (after pip install -r requirements-build.txt)

block_cipher = None

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[("templates", "templates")],
    hiddenimports=[
        "flask",
        "werkzeug",
        "jinja2",
        "click",
        "itsdangerous",
        "blinker",
        "requests",
        "certifi",
        "charset_normalizer",
        "idna",
        "urllib3",
        "dotenv",
        "api",
        "api.poe_ninja",
        "api.cache",
        "analysis",
        "analysis.flip",
        "analysis.crafting",
        "analysis.convert_tricks",
        "analysis.trade_lab",
        "settings",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="poe-trade-flipper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="poe-trade-flipper",
)
