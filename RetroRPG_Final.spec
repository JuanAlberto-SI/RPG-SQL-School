# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['game_engine.py'],
    pathex=[],
    binaries=[],
    datas=[('bg_forest.png', '.'), ('bg_cave.png', '.'), ('bg_dungeon.png', '.'), ('tree.png', '.'), ('rock.png', '.'), ('pillar.png', '.'), ('player.png', '.'), ('slash.png', '.'), ('fireball.png', '.'), ('goblin.png', '.'), ('shadow.png', '.'), ('ogre.png', '.'), ('brain.png', '.'), ('PressStart2P.ttf', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='RetroRPG_Final',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
