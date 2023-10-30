from textwrap import dedent

from lk_utils import dumps
from lk_utils import fs

from ...manifest import T
from ...manifest import load_manifest
from ...platform import create_launcher
from ...platform.system_info import SYSTEM


def build(manifest_file: str, **kwargs) -> None:
    """
    what does this function do:
        - create a dist folder
        - create a launcher (exe or bat)
    """
    manifest = load_manifest(manifest_file)
    
    dir_i = manifest['start_directory']
    dir_o = '{}/dist/{}-{}'.format(
        dir_i, manifest['appid'], manifest['version']
    )
    fs.make_dirs(dir_o)
    
    if SYSTEM == 'darwin':
        create_launcher(
            manifest=manifest,
            path_o=f'{dir_o}/{manifest["name"]}.app',
        )
    elif SYSTEM == 'linux':
        create_launcher(
            path_i=manifest['start_directory'],
            path_o=f'{dir_o}/{manifest["name"]}.desktop',
        )
    elif SYSTEM == 'windows':
        if kwargs.get('gen_exe', True):
            create_launcher(
                path_i=f'{dir_o}/launcher.bat',
                path_o=f'{dir_o}/launcher.exe',
                icon=manifest['launcher']['icon'],  # noqa
                remove_bat=True,
            )
    
    print(
        ':t',
        'build done. see result in "dist/{}-{}"'.format(
            manifest['appid'], manifest['version']
        ),
    )


def _create_bat(manifest: T.Manifest, file: str) -> None:
    command = (
        dedent('''
        @echo off
        set PYTHONPATH={app_dir};{pkg_dir}
        {py} %*
    ''')
        .strip()
        .format(
            app_dir=r'{}\{}\{}'.format(
                r'%DEPSLAND%\apps', manifest['appid'], manifest['version']
            ),
            pkg_dir=r'{}\.venv\{}'.format(
                r'%DEPSLAND%\apps', manifest['appid']
            ),
            py=r'"%DEPSLAND%\python\python.exe"',
        )
    )
    dumps(command, file)
