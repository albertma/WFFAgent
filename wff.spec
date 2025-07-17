# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['build_desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/wff_agent', 'wff_agent'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'wff_agent.agent_client',
        'wff_agent.agent_factory',
        'wff_agent.stock_agents',
        'wff_agent.stock_analysis_workflow',
        'wff_agent.prompts',
        'wff_agent.utils',
        'wff_agent.datasource',
        'wff_agent.agents',
        'wff_agent.workflows',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'asyncio',
        'logging',
        'typing',
        'datetime',
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
    name='wff',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='wff',
)

app = BUNDLE(
    coll,
    name='wff.app',
    icon=None,
    bundle_identifier='com.wff.stockanalysis',
    info_plist={
        'CFBundleName': 'WFF Stock Analysis',
        'CFBundleDisplayName': 'WFF 股票分析',
        'CFBundleIdentifier': 'com.wff.stockanalysis',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
        'NSRequiresAquaSystemAppearance': False,
    },
)
