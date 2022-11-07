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
        set PYTHONPATH={app_dir};{pkg_dir}
        {py} %*
    ''').strip().format(
        app_dir=r'{}\{}\{}'.format(
            r'%DEPSLAND%\apps', manifest['appid'], manifest['version']
        ),
        pkg_dir=r'{}\.venv\{}\packages'.format(
            r'%DEPSLAND%\apps', manifest['appid']
        ),
        py=r'%DEPSLAND%\python\python.exe',
    )
    
    dumps(command, f'{dir_i}/launcher.bat')
    
    if gen_exe:  # TEST: experimental
        bat_2_exe(f'{dir_i}/launcher.bat',
                  f'{dir_i}/launcher.exe', icon)
