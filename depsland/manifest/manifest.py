import os
import typing as t

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads


# noinspection PyTypedDict
class T:
    _AbsPath = str
    _AnyPath = str
    _RelPath = str  # path relative to manifest file's location.
    _Scheme = str  # see details in `depsland.interface.dev_cli.uploader.T.Scheme`
    _Version = str
    
    # manifest (A) made by user
    ManifestA = t.TypedDict('ManifestA', {
        'appid'       : str,
        'name'        : str,
        'version'     : str,
        'assets'      : t.Dict[_AnyPath, str],  # dict[anypath, scheme]
        #   anypath: abspath or relpath, '/' or '\\' both allowed.
        #   scheme: scheme or empty string. the empty means 'all'.
        'dependencies': t.Dict[str, str],  # dict[name, verspec]
        'pypi'        : t.List[_AnyPath],  # list[anypath_to_python_wheel]
        'launcher'    : (Launcher := t.TypedDict('Launcher', {
            'command'   : str,
            'desktop'   : bool,
            'start_menu': bool,
        })),
    }, total=False)
    # manifest (B) made by program
    #   the difference between A and B:
    #       1. B has a unified path form.
    #       2. B has an extra key 'start_directory'.
    ManifestB = t.TypedDict('ManifestB', {
        'appid'          : str,
        'name'           : str,
        'version'        : _Version,
        'start_directory': _AbsPath,
        'assets'         : t.Dict[_RelPath, _Scheme],
        'dependencies'   : t.Dict[str, str],  # dict[name, verspec]
        'pypi'           : t.Dict[str, _AbsPath],  # dict[filename, abspath]
        'launcher'       : Launcher,
    })
    ManifestFile = str  # a '.json' or '.pkl' file


def init_manifest(appid: str, appname: str) -> T.ManifestB:
    return {
        'appid'          : appid,
        'name'           : appname,
        'version'        : '0.0.0',
        'start_directory': '',
        'assets'         : {},
        'dependencies'   : {},
        'pypi'           : {},
        'launcher'       : {
            'command'   : f'depsland show {appid}',
            'desktop'   : False,
            'start_menu': False,
        },
    }


def load_manifest(manifest_file: T.ManifestFile,
                  _is_trusted=False) -> T.ManifestB:
    manifest_file = fs.normpath(manifest_file, force_abspath=True)
    manifest_dir = fs.parent_path(manifest_file)
    
    data_i: t.Union[T.ManifestA, T.ManifestB] = loads(manifest_file)
    data_o: T.ManifestB = {}
    
    if _is_trusted or manifest_file.endswith('.pkl'):
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
        'assets'         : {},  # update later, see below
        'dependencies'   : data_i.get('dependencies', {}),
        'pypi'           : {},  # update later, see below
        'launcher'       : {
            'command'   : 'depsland show {} {}'.format(
                data_i['appid'], data_i['version']
            ),
            'desktop'   : False,
            'start_menu': False,
            **data_i.get('launcher', {}),
        }
    })
    
    # fill `assets` field
    assets_i = data_i['assets']
    assets_o = data_o['assets']
    for path, scheme in assets_i.items():
        if os.path.isabs(path):
            relpath = fs.relpath(path, manifest_dir)
        else:
            relpath = fs.normpath(path)
        assets_o[relpath] = scheme or 'all'
    
    # fill `pypi` field
    pypi_i = data_i.get('pypi', [])
    pypi_o = data_o['pypi']
    for path in pypi_i:
        if os.path.isabs(path):
            abspath = fs.normpath(path)
        else:
            abspath = fs.normpath(f'{manifest_dir}/{path}')
        pypi_o[fs.filename(abspath)] = abspath
    
    return data_o


def dump_manifest(manifest: T.ManifestB, file_o: T.ManifestFile) -> T.ManifestB:
    manifest_i = manifest
    manifest_o: T.ManifestB = manifest_i.copy()
    manifest_o['start_directory'] = fs.parent_path(file_o)
    dumps(manifest_o, file_o)
    return manifest_o
