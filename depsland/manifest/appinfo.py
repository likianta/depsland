import os
import typing as t
from os.path import exists

from lk_utils import dumps
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
    history_file = paths.apps.get_history_versions(data_o['appid'])
    if exists(history_file):
        data_o['history'] = loads(history_file)
    else:
        print('no history found, it would be the first release',
              data_o['name'], data_o['version'], ':v2')
        dumps([], history_file)
    
    return data_o
