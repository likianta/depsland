import os
import typing as t
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads
from os.path import exists
from . import paths

_apps_dir = paths.project.apps


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
        'appid'          : str,
        'name'           : str,
        'version'        : _Version,
        'start_directory': str,
        'assets'         : t.Dict[str, str],  # dict[path, scheme]
        #   path: when loaded, use abspath; when dumped, use relpath.
        #   scheme: see also `./oss/uploader.py > T.Scheme`.
        'dependencies'   : t.Dict[str, str],  # dict[name, version_spec]
    })
    ManifestFile = str  # a '.json' or '.pkl' file


def get_app_info(manifest_file: T.ManifestFile) -> T.Appinfo:
    data_i: T.Manifest = load_manifest(manifest_file)
    data_o: T.Appinfo = {
        'appid'  : data_i['appid'],
        'name'   : data_i['name'],
        'version': data_i['version'],
        'src_dir': fs.dirpath(manifest_file),
        'dst_dir': '{}/{}/{}'.format(
            _apps_dir,
            data_i['appid'],
            data_i['version']
        ),
        'history': [],
    }
    
    if not exists(d := data_o['dst_dir']): os.makedirs(d)
    dump_manifest(data_i, f'{d}/manifest.json')
    
    # update history
    history_file = '{}/{}/released_history.json'.format(
        _apps_dir, data_i['appid']
    )
    if exists(history_file):
        data_o['history'] = loads(history_file)
    else:
        print('no history found, it would be the first release',
              data_o['name'], data_o['version'], ':v2')
        dumps([], history_file)
        
    return data_o


def load_manifest(manifest_file: T.ManifestFile) -> T.Manifest:
    manifest_file = fs.normpath(manifest_file, force_abspath=True)
    manifest_dir = fs.parent_path(manifest_file)
    
    data: dict = loads(manifest_file)
    
    # assert required keys
    required_keys = ('appid', 'name', 'version', 'assets')
    assert all(x in data for x in required_keys)
    
    # fill optional keys
    if 'start_directory' not in data:
        data['start_directory'] = manifest_dir
    else:
        assert data['start_directory'] == manifest_dir
    if 'dependencies' not in data:
        data['dependencies'] = {}
    
    # reformat assets
    reformatted_assets: t.Dict[str, str] = {}
    # noinspection PyTypeChecker
    for path, scheme in data['assets'].items():
        if not os.path.isabs(path):
            path = fs.normpath(f'{manifest_dir}/{path}')
        if scheme == '':
            scheme = 'all_assets'
        reformatted_assets[path] = scheme
    data['assets'] = reformatted_assets
    
    return data


def dump_manifest(manifest: T.Manifest, file_o: T.ManifestFile) -> T.Manifest:
    # when dump to a file, the manifest's assets keys must be relative paths
    root_i = manifest['start_directory']
    root_o = fs.parent_path(file_o)
    
    assets_i = manifest['assets']
    assets_o: t.Dict[str, str] = {}
    
    # noinspection PyTypeChecker
    for abspath, v in assets_i.items():
        relpath = fs.relpath(abspath, root_i)
        assets_o[relpath] = v
    
    manifest_o = manifest.copy()  # FIXME: deepcopy?
    manifest_o['start_directory'] = root_o
    manifest_o['assets'] = assets_o
    
    dumps(manifest_o, file_o)
    return manifest_o
