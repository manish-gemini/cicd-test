# -*- mode: python -*-

block_cipher = None


path = 'pysrc/'
a = Analysis([path + 'apporbit-server.py', 
          path + 'action.py',
          path + 'apporbit-server.py',
          path + 'config.py',
          path + 'userinteract.py',
          path + 'utility.py',
          path + 'docker.py',
          path + 'offlinedeploy.py',
          path + 'provider.py',
          path + 'resourcefetcher.py'],
             pathex=['/home/jshah/Gemini-sys/cicd/src/apporbit-server/pysrc'],
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
