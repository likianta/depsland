import os
import typing as t
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads
from os.path import exists
from . import paths


# noinspection PyTypedDict
class T:
    _Version = str
    Appinfo = t.TypedDict('Appinfo', {
        'appid'  : str,
        'name'   : str,
        'version': _Version,
        'src_dir': str,
        'dst_dir': str,
        'history': t.List[_Version],
    })
    Manifest = t.TypedDict('Manifest', {
        'appid'  : str,
        'name'   : str,
        'version': _Version,
        'assets' : t.Dict[str, str],
    })


def get_app_info(manifest_file: str) -> T.Appinfo:
    data_i: T.Manifest = get_manifest(manifest_file)
    data_o: T.Appinfo = {
        'appid'  : data_i['appid'],
        'name'   : data_i['name'],
        'version': data_i['version'],
        'src_dir': fs.dirpath(manifest_file),
        'dst_dir': '{}/{}/{}'.format(
            paths.apps_dir,
            data_i['appid'],
            data_i['version']
        ),
        'history': [],
    }
    
    if not exists(d := fs.parent_path(data_o['dst_dir'])): os.mkdir(d)
    if not exists(d := data_o['dst_dir']): os.mkdir(d)
    dumps(data_i, f'{data_o["dst_dir"]}/manifest.json')
    
    history_file = '{}/{}/released_history.json'.format(
        paths.apps_dir, data_i['appid']
    )
    if exists(history_file):
        data_o['history'] = loads(history_file)
    else:
        dumps([], history_file)
    return data_o


def get_manifest(manifest_file: str) -> T.Manifest:
    manifest_file = fs.normpath(manifest_file, force_abspath=True)
    manifest_dir = fs.parent_path(manifest_file)
    
    data: T.Manifest = loads(manifest_file)
    reformatted_assets: dict[str, str] = {}

    # noinspection PyTypeChecker
    for path, scheme in data['assets'].items():
        if not os.path.isabs(path):
            path = fs.normpath(f'{manifest_dir}/{path}')
        if scheme == '':
            scheme = 'all_assets'
        reformatted_assets[path] = scheme
    
    data['assets'] = reformatted_assets
    return data
