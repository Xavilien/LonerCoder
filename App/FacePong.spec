# -*- mode: python -*-

block_cipher = None
from kivy.tools.packaging.pyinstaller_hooks import get_deps_all, hookspath, runtime_hooks

a = Analysis(['/Users/xavilien/Desktop/School/1Secondary/2018/Non-Core/CEP/LonerCoder/Multiplayer/multiplayer.py'],
             pathex=['/Users/xavilien/Desktop/School/1Secondary/2018/Non-Core/CEP/LonerCoder/'],
             binaries=None,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             hookspath=hookspath(),
             runtime_hooks=runtime_hooks(),
             **get_deps_all())

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='touchtracer',
          debug=False,
          strip=False,
          upx=True,
          console=False )

coll = COLLECT(exe, Tree('/Users/xavilien/Desktop/School/1Secondary/2018/Non-Core/CEP/LonerCoder/',
                        excludes=['Old', 'Files']),
               Tree('/Library/Frameworks/SDL2_ttf.framework/Versions/A/Frameworks/FreeType.framework'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='FacePong')

app = BUNDLE(coll,
             name='FacePong.app',
             icon=None,
         bundle_identifier=None)