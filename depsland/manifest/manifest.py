import os
import typing as t
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads


# noinspection PyTypedDict
class T:
    _AbsPath = str
    _RelPath = str  # path relative to manifest file's location.
    _Scheme = str  # see details in `depsland.interface.dev_cli.uploader.T.Scheme`
    _Version = str
    
    # manifest made by user
    ManifestA = t.TypedDict('ManifestA', {
        'appid'       : str,
        'name'        : str,
        'version'     : str,
        'assets'      : t.Dict[str, str],  # dict[anypath, scheme]
        #   anypath: abspath or relpath, '/' or '\\' both allowed.
        #   scheme: scheme or empty string. the empty means 'all'.
        'dependencies': t.Dict[str, str],  # dict[name, verspec]
    })
    # manifest made by program
    #   the difference between A and B is B has a unified path form.
    ManifestB = t.TypedDict('ManifestB', {
        'appid'       : str,
        'name'        : str,
        'version'     : _Version,
        'assets'      : t.Dict[_RelPath, _Scheme],
        'dependencies': t.Dict[str, str],
    })
    # manifest in runtime
    #   the difference between B and C is C has an extra key 'start_directory'.
    ManifestC = t.TypedDict('ManifestC', {
        'appid'          : str,
        'name'           : str,
        'version'        : _Version,
        'start_directory': str,
        'assets'         : t.Dict[_RelPath, _Scheme],
        'dependencies'   : t.Dict[str, str],
    })
    ManifestFile = str  # a '.json' or '.pkl' file


def init_manifest(appid: str, appname: str) -> T.ManifestC:
    return {
        'appid'          : appid,
        'name'           : appname,
        'version'        : '0.0.0',
        'start_directory': '',
        'assets'         : {},
        'dependencies'   : {},
    }


def load_manifest(manifest_file: T.ManifestFile,
                  _is_trusted=False) -> T.ManifestC:
    manifest_file = fs.normpath(manifest_file, force_abspath=True)
    manifest_dir = fs.parent_path(manifest_file)
    
    data_i: t.Union[T.ManifestA, T.ManifestB] = loads(manifest_file)
    data_o: T.ManifestC = {}
    
    if _is_trusted:
        data_o = data_i  # noqa
        data_o['start_directory'] = manifest_dir
        return data_o
    
    # assert required keys
    required_keys = ('appid', 'name', 'version', 'assets')
    assert all(x in data_i for x in required_keys)
    
    data_o.update({
        'appid'          : data_i['appid'],
        'name'           : data_i['name'],
        'version'        : data_i['version'],
        'start_directory': manifest_dir,
        'assets'         : {},  # later, see below
        'dependencies'   : data_i.get('dependencies', {}),
    })
    
    # fill assets
    assets_i = data_i['assets']
    assets_o = data_o['assets']
    # noinspection PyTypeChecker
    for path, scheme in assets_i.items():
        if os.path.isabs(path):
            relpath = fs.relpath(path, manifest_dir)
        else:
            relpath = fs.normpath(path)
        assets_o[relpath] = scheme or 'all'
    
    return data_o


def dump_manifest(manifest: T.ManifestC, file_o: T.ManifestFile) -> T.ManifestC:
    manifest_i = manifest
    manifest_o: T.ManifestC = manifest_i.copy()
    manifest_o['start_directory'] = fs.parent_path(file_o)
    dumps(manifest_o, file_o)
    return manifest_o
