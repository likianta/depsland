from textwrap import dedent

from lk_utils import dumps
from lk_utils import fs

from ...manifest import load_manifest
from ...utils import bat_2_exe


def build(manifest_file: str, icon='', gen_exe=True) -> None:
    file_i = fs.normpath(manifest_file, True)
    dir_i = fs.parent_path(file_i)
    manifest = load_manifest(file_i)

    command = dedent('''
        @echo off
        set PYTHONPATH={}:{}
        %DEPSLAND%\python\python.exe %*
    ''').strip().format(
        r'{}\{}\{}'.format(
            r'%DEPSLAND%\apps', manifest['appid'], manifest['version']
        ),
        r'{}\.venv\{}\packages'.format(
            r'%DEPSLAND%\apps', manifest['appid']
        ),
    )
    
    dumps(command, f'{dir_i}/launcher.bat')
    
    if gen_exe:  # TEST: experimental
        bat_2_exe(f'{dir_i}/launcher.bat',
                  f'{dir_i}/launcher.exe', icon)
