# -*- mode: python -*-

block_cipher = None


a = Analysis(['pysrc/apporbit-server.py', 'pysrc/action.py', 'pysrc/apporbit-server.py', 'pysrc/config.py', 'pysrc/userinteract.py', 'pysrc/utility.py'],
             pathex=['/home/jshah/Gemini-sys/cicd/src/apporbit-server'],
             binaries=None,
             datas=None,
             hiddenimports=['action', 'config', 'utility', 'userinteract'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='apporbit-server',
          debug=False,
          strip=False,
          upx=True,
          console=True )
