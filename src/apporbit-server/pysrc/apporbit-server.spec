# -*- mode: python -*-

block_cipher = None


a = Analysis(['action.py', 'apporbit-server.py', 'config.py',
              'userinteract.py', 'utility.py', 'docker_ao.py',
              'offlinedeploy.py', 'provider.py', 'resourcefetcher.py'],
             pathex=['pysrc'],
             binaries=None,
             datas=[ ('conf', 'conf') ],
             hiddenimports=[],
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
          console=True )
