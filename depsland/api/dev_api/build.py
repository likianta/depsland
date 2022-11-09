from textwrap import dedent

from lk_utils import dumps
from lk_utils import fs

from ...manifest import load_manifest
from ...utils import bat_2_exe


def build(manifest_file: str, icon='', gen_exe=True) -> None:
    manifest = load_manifest(manifest_file)
    
    dir_i = manifest['start_directory']
    dir_o = '{}/dist/{}-{}'.format(
        dir_i, manifest['appid'], manifest['version']
    )
    fs.make_dirs(dir_o)

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
    
    dumps(command, f'{dir_o}/launcher.bat')
    
    if gen_exe:
        bat_2_exe(f'{dir_o}/launcher.bat',
                  f'{dir_o}/launcher.exe', icon)
        # os.remove(f'{dir_o}/launcher.bat')

    print(':t', 'build done. see result in {}'.format(dir_o))
