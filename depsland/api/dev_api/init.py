import os
import re
import typing as t
from os.path import exists

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

from ...manifest import T as T0
from ...manifest import init_manifest
from ...venv.target_venv import get_top_level_package_names


class T(T0):
    # ref: T0.Launcher0
    TargetInfo = t.TypedDict('TargetInfo', {
        'name': str,
        'type': t.Literal['executable', 'module', 'package']
    })


def init(
    manifest_file: str = './manifest.json',
    appname: str = '',
    force_create: bool = False,
    auto_find_requirements: bool = False,
) -> None:
    # init/update parameters
    filepath = fs.normpath(manifest_file, True)
    if exists(filepath):
        if force_create:
            os.remove(filepath)
        else:
            print(':v3s', 'target already exists! (stop processing)', filepath)
            return
    
    dirpath = fs.parent_path(filepath)
    if not exists(dirpath):
        os.mkdir(dirpath)
    
    dirname = fs.dirname(dirpath)
    if appname == '':
        appname = dirname.replace('-', ' ').replace('_', ' ').title()
    appid = appname.replace(' ', '_').replace('-', '_').lower()
    print(':v2f2', appname, appid)
    
    manifest = init_user_manifest(dirpath, appname, appid)
    
    if auto_find_requirements:
        # TODO (2023-08-14): currently only support poetry environment.
        deps: t.List[str] = manifest['dependencies']['official_host']
        if exists(f'{dirpath}/poetry.lock'):
            deps.extend(get_top_level_package_names(dirpath))
        elif exists(x := f'{dirpath}/requirements.txt'):
            print(
                ':v3',
                'experimentally finding dependencies from requirements.txt',
            )
            re_name = re.compile(r'^ *([-\w]+)', re.M)
            deps.extend(re_name.findall(loads(x)))
        else:
            print(':v3', 'no dependency found')
        if deps:
            print(':l', deps)
    
    dumps(manifest, x := f'{dirpath}/manifest.json')
    print(f'see manifest file at \n\t"{x}"', ':tv2s')


def init_user_manifest(root: str, appname: str, appid: str) -> T.UserManifest:
    manifest: T.Manifest = init_manifest(appid, appname)
    manifest.pop('start_directory')  # noqa
    manifest['version'] = '0.1.0'
    manifest['dependencies']['custom_host'] = []
    manifest['dependencies']['official_host'] = []
    if x := _deduce_target(root, appid):
        manifest['launcher']['target'] = x['name']
        manifest['launcher']['type'] = x['type']
    else:
        manifest['launcher']['type'] = 'module'  # as default
    return manifest


def _deduce_target(root: str, appid: str) -> t.Optional[T.TargetInfo]:
    for possible_path in (
        f'{root}/{appid}',
        f'{root}/src/{appid}',
        f'{root}/{appid}.py',
        f'{root}/src/{appid}.py',
        f'{root}/{appid}.exe',
        f'{root}/{appid}',
    ):
        if exists(possible_path):
            if os.path.isdir(possible_path):
                if exists(f'{possible_path}/__init__.py') and exists(
                    f'{possible_path}/__main__.py'
                ):
                    return {'name': appid, 'type': 'package'}
            else:
                if possible_path.endswith('.py'):
                    return {'name': appid, 'type': 'module'}
                elif possible_path.endswith('.exe'):
                    return {'name': appid, 'type': 'executable'}
                else:
                    return {'name': appid, 'type': 'executable'}
    return None
