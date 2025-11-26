# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['project.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('images/icon.png', 'images'),
        ('images/font.png', 'images'),
        ('images/ghost.png', 'images'),
        ('images/bullet.png', 'images'),
        ('images/coin.png', 'images'),
        ('images/player_right/player_right1.png', 'images/player_right'),
        ('images/player_right/player_right2.png', 'images/player_right'),
        ('images/player_right/player_right3.png', 'images/player_right'),
        ('images/player_right/player_right4.png', 'images/player_right'),
        ('images/player_left/player_left1.png', 'images/player_left'),
        ('images/player_left/player_left2.png', 'images/player_left'),
        ('images/player_left/player_left3.png', 'images/player_left'),
        ('images/player_left/player_left4.png', 'images/player_left'),
        ('sounds/sounds.mp3', 'sounds'),
    ],
    hiddenimports=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Mini_Mario_Game',
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
