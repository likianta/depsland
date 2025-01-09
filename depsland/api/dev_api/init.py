import os
import typing as t
from random import randint

from lk_utils import fs

from ...manifest import T as T0
from ...manifest import init_manifest


class T(T0):
    # ref: T0.Launcher0
    TargetInfo = t.TypedDict(
        'TargetInfo',
        {
            'target': str,  # relpath
            'type': t.Literal['executable', 'module', 'package'],
            'icon': str,  # relpath or empty
        },
    )


def init(
    manifest_file: str = './manifest.json',
    appname: str = '',
    init_version: str = '0.1.0',
) -> None:
    file_o = fs.normpath(manifest_file, True)
    dir_o = fs.parent(file_o)
    if not fs.exists(dir_o):
        os.mkdir(dir_o)
    
    dirname = fs.dirname(dir_o)
    if appname == '':
        appname = dirname.replace('-', ' ').replace('_', ' ').title()
    appid = '{}_0x{:04x}'.format(
        appname.replace(' ', '_').replace('-', '_').lower(),
        randint(0, 0xFFFF)
    )
    print(':v2', appname, appid)
    
    manifest = init_user_manifest(appname, appid, init_version)
    fs.dump(manifest, file_o)
    print(f'see manifest file at "{file_o}"', ':tv4')


def init_user_manifest(
    appname: str, appid: str, version: str = '0.1.0'
) -> T.UserManifest:
    manifest = init_manifest(appid, appname).model
    manifest.pop('start_directory')  # noqa
    manifest['version'] = version
    manifest['dependencies'] = 'poetry.lock'
    return manifest
