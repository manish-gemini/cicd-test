# -*- mode: python -*-

block_cipher = None


path_prefix = 'pysrc/'
file_list = ['apporbit-server.py', 'action.py', 'docker_ao.py',
             'config.py', 'userinteract.py', 'utility.py',
             'offlinedeploy.py', 'provider.py', 'resourcefetcher.py']
analyse_files = [path_prefix + f for f in file_list]
a = Analysis(analyse_files,
             pathex=['/home/jshah/Gemini-sys/cicd/src/apporbit-server'],
             binaries=None,
             datas=[ (path_prefix + 'conf', 'conf')],
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
