# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Student_Lookup.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['openpyxl'],
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
    [],
    exclude_binaries=True,
    name='Student Lookup',
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Student Lookup',
)
app = BUNDLE(
    coll,
    name='Student Lookup.app',
    icon="Student_Lookup.icns",
    version='2.0.0',
    bundle_identifier="com.digiasati.Student_Lookup",
    osx_plist={
        'CFBundleName': 'Student Lookup',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundleVersion': '2.0.0',
        'CFBundleIdentifier': 'com.digiasati.Student_Lookup',
    },
)
