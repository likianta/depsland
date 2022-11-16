import os
import shlex  # a built-in library that splits command line args
import typing as t
from os.path import exists

from lk_utils import fs
from lk_utils import loads

from .manifest import T as T0
from .manifest import dump_manifest
from .manifest import load_manifest
from .. import paths


class T(T0):
    Appinfo = t.TypedDict('Appinfo', {
        'appid'  : str,
        'name'   : str,
        'version': str,
        'src_dir': str,  # abspath
        'dst_dir': str,  # abspath
        'history': t.List[str],  # list[str version]
    })
    Manifest = T0.Manifest1


def get_app_info(manifest_file: str) -> T.Appinfo:
    data_i: T.Manifest = load_manifest(manifest_file)
    data_o: T.Appinfo = {
        'appid'  : data_i['appid'],
        'name'   : data_i['name'],
        'version': data_i['version'],
        'src_dir': fs.dirpath(manifest_file),
        'dst_dir': '{}/{}/{}'.format(
            paths.project.apps,
            data_i['appid'],
            data_i['version']
        ),
        'history': [],
    }
    
    if not exists(d := data_o['dst_dir']): os.makedirs(d)
    dump_manifest(data_i, f'{d}/manifest.json')
    
    # update history
    history_file = paths.apps.get_distribution_history(data_o['appid'])
    if exists(history_file):
        data_o['history'] = loads(history_file, ftype='plain').splitlines()
    else:
        print('no history found, it would be the first release',
              data_o['name'], data_o['version'], ':v2')
        # dumps('', history_file, ftype='plain')
    
    return data_o


def get_last_installed_version(appid: str) -> t.Optional[str]:
    file = paths.apps.get_installation_history(appid)
    if not exists(file): return None
    return _quick_read_line(file)


def get_last_released_version(appid: str) -> t.Optional[str]:
    file = paths.apps.get_distribution_history(appid)
    if not exists(file): return None
    return _quick_read_line(file)


def parse_script_info(manifest: T.Manifest) -> t.Tuple[str, ...]:
    appid = manifest['appid']
    version = manifest['version']
    script = manifest['launcher']['script']
    #   either script is a '.py' file, or a (relpath) directory containing
    #   '__main__.py'.
    
    py = paths.python.python  # interpreter path
    script, args = (script + ' ').split(' ', 1)
    # normalize `script`
    if script.endswith('.py'):
        script = (fs.normpath('{app_dir}/{relpath}'.format(
            app_dir=f'{paths.project.apps}/{appid}/{version}',
            relpath=script
        )),)
    else:
        script = ('-m', script)
    # normalize `args`
    args = shlex.split(args)
    #   https://stackoverflow.com/questions/197233/how-to-parse-a-command-line
    #   -with-regular-expressions
    
    return py, *script, *args


def _quick_read_line(text_file: str) -> str:
    with open(text_file) as f:
        for line in f:  # just read the first line
            return line.strip()
