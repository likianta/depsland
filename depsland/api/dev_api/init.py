import os
import sys
import typing as t
from os.path import exists

from lk_utils import dumps
from lk_utils import fs

from ...manifest import T as T0
from ...manifest import init_manifest
from ...venv.target_venv import get_top_package_names


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
    force_create: bool = False,
    auto_find_requirements: bool = False,
    **kwargs,
) -> None:
    # init/update parameters
    file_o = fs.normpath(manifest_file, True)
    del manifest_file
    if exists(file_o):
        if force_create:
            os.remove(file_o)
        else:
            print(':v3s', 'target already exists! (stop processing)', file_o)
            return
    
    dir_o = fs.parent_path(file_o)
    if not exists(dir_o):
        os.mkdir(dir_o)
    
    dirname = fs.dirname(dir_o)
    if appname == '':
        appname = dirname.replace('-', ' ').replace('_', ' ').title()
    appid = appname.replace(' ', '_').replace('-', '_').lower()
    print(':v2f2', appname, appid)
    
    manifest = init_user_manifest(dir_o, appname, appid, **kwargs)
    
    if auto_find_requirements:
        def finetune_name(name: str) -> str:
            return name.replace('_', '-')
        
        deps: t.List[str] = manifest['dependencies']['official_host']
        if exists(f := f'{dir_o}/requirements.txt'):
            deps.extend(map(
                finetune_name,
                sorted(get_top_package_names(f, 'requirements.txt')),
            ))
        elif exists(f := f'{dir_o}/pyproject.toml'):
            deps.extend(map(
                finetune_name,
                sorted(get_top_package_names(f, 'pyproject.toml')),
            ))
        else:
            print(':v3', 'no dependency detected')
        if deps:
            print(':l', deps)
    
    dumps(manifest, file_o)
    print(f'see manifest file at \n\t"{file_o}"', ':tv2s')


def init_user_manifest(
    root: str, appname: str, appid: str, version: str = '0.1.0'
) -> T.UserManifest:
    manifest = init_manifest(appid, appname).model
    
    manifest.pop('start_directory')  # noqa
    manifest['version'] = version
    manifest['dependencies'].pop('root')
    manifest['dependencies']['custom_host'] = []
    manifest['dependencies']['official_host'] = []
    
    if x := _deduce_target(root, appname, appid):
        manifest['launcher']['target'] = x['target']
        manifest['launcher']['type'] = x['type'] or 'module'  # as fallback
        manifest['launcher']['icon'] = x['icon']
        
        manifest['assets'][rel_src_dir := fs.dirpath(x['target'])] = 'all'
        if x['icon'] and not x['icon'].startswith(rel_src_dir):
            manifest['assets'][x['icon']] = 'all'
    else:
        manifest['launcher']['type'] = 'module'  # as default
    
    return manifest


def _deduce_target(
    root: str, appname: str, appid: str
) -> t.Optional[T.TargetInfo]:
    def main() -> t.Optional[T.TargetInfo]:
        for possible_path in (
            f'{root}/{appid}',
            f'{root}/src/{appid}',
            f'{root}/{appid}.py',
            f'{root}/src/{appid}.py',
            f'{root}/{appid}.exe',
            f'{root}/{appid}',
            f'{root}/src',
            f'{root}/src/main.py',
            f'{root}/src/app.py',
            f'{root}/src/run.py',
        ):
            if exists(possible_path):
                # the fields 'target' and 'type' are required, while 'icon' is \
                # optional.
                if t := _possible_type(possible_path):
                    # noinspection PyTypeChecker
                    return {
                        'target': fs.relpath(possible_path, root),  # required
                        'type': t,  # required
                        'icon': _possible_launcher_icon() or '',  # optional
                    }
        return None
    
    def _possible_launcher_icon() -> t.Optional[str]:
        """
        find possible launcher icon in follwing positions:
            - {root}/launcher.{ext}
            - {root}/build/launcher.{ext}
        """
        possible_paths = {
            'darwin': ('launcher.icns', f'{appid}.icns', f'{appname}.icns'),
            'linux': ('launcher.png', f'{appid}.png', f'{appname}.png'),
            'win32': ('launcher.ico', f'{appid}.ico', f'{appname}.ico'),
        }
        # prefer the platform-related candidates, then the others for a \
        # fallback (they can be someway inter-converted then).
        for _, candidates in sorted(
            possible_paths.items(),
            key=lambda x: 0 if x[0] == sys.platform else 1,
        ):
            for x in candidates:
                if exists(y := f'{root}/{x}'):
                    return y
                if exists(y := f'{root}/build/{x}'):
                    return y
        return None
    
    def _possible_type(path: str) -> t.Optional[str]:
        if os.path.isdir(path):
            if exists(f'{path}/__init__.py') and exists(f'{path}/__main__.py'):
                return 'package'
            else:
                return None
        else:
            if path.endswith('.py'):
                return 'module'
            elif path.endswith('.exe'):
                return 'executable'
            else:
                return 'executable'
    
    return main()
