import os
import typing as t
from collections import namedtuple

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

from ..utils import get_file_hash
from ..utils import get_updated_time

__all__ = [
    'T',
    'compare_manifests',
    'dump_manifest',
    'init_manifest',
    'init_target_tree',
    'load_manifest'
]


# noinspection PyTypedDict
class T:
    _AbsPath = _RelPath = _AnyPath = str
    #   the _RelPath is relative to manifest file's location.
    
    Scheme0 = t.Literal['root', 'all', 'all_dirs',
                        'top', 'top_files', 'top_dirs', '']
    #   empty str means 'all'
    Scheme1 = t.Literal['root', 'all', 'all_dirs',
                        'top', 'top_files', 'top_dirs']
    
    Assets0 = t.Dict[_AnyPath, Scheme0]
    #   anypath: abspath or relpath, '/' or '\\' both allowed.
    #   scheme: scheme or empty string. if empty string, it means 'all'.
    Assets1 = t.Dict[
        _RelPath,
        AssetInfo := t.NamedTuple('AssetInfo', (
            ('type', t.Literal['file', 'dir']),
            ('scheme', Scheme1),
            ('utime', int),  # updated time
            ('hash', t.Optional[str]),  # if type is dir, the hash is None
            ('uid', str),  # the uid will be used as key to filename in oss.
        ))
    ]
    
    Dependencies0 = t.Dict[str, str]  # dict[name, verspec]
    Dependencies1 = Dependencies0
    
    PyPI0 = t.List[_AnyPath]  # list[anypath_to_python_wheel]
    PyPI1 = t.Dict[str, str]  # dict[filename, abspath]
    
    Launcher0 = t.TypedDict('Launcher', {
        'command'   : str,
        'desktop'   : bool,
        'start_menu': bool,
    })
    Launcher1 = Launcher0
    
    # -------------------------------------------------------------------------
    
    # Manifest0
    #   Manifest0 is a json-compatible dict. it is either made by user or
    #   dumped by `def dump_manifest` function (when caller passes a '.json'
    #   file param to it).
    Manifest0 = t.TypedDict('Manifest0', {
        'appid'       : str,
        'name'        : str,
        'version'     : str,
        'assets'      : Assets0,
        'dependencies': Dependencies0,
        'pypi'        : PyPI0,
        'launcher'    : Launcher0,
    }, total=False)
    
    # Manifest1
    #   Manifest1 is main data structure for program to use. it is loaded from
    #   a '.pkl' file, or parsed from a '.json' file (i.e. Manifest0 data).
    #   the differences between ~0 and ~1 are:
    #       1. ~1 has a unified path form.
    #       2. ~1 has an extra key 'start_directory'.
    #       3. ~1's assets values are `namedtuple: AssetInfo`.
    Manifest1 = t.TypedDict('Manifest1', {
        'appid'          : str,
        'name'           : str,
        'version'        : str,
        'start_directory': _AbsPath,
        'assets'         : Assets1,
        'dependencies'   : Dependencies1,
        'pypi'           : PyPI1,
        'launcher'       : Launcher1,
    })
    
    ManifestFile = str  # a '.json' or '.pkl' file
    
    # -------------------------------------------------------------------------
    
    Action = t.Literal['append', 'update', 'delete', 'ignore']
    
    AssetsDiff = t.Iterator[
        t.Tuple[
            Action,
            _AbsPath,
            t.Tuple[t.Optional[AssetInfo], t.Optional[AssetInfo]]
            #   tuple[old_info, new_info]
        ]
    ]
    
    DependenciesDiff = t.Iterator[
        t.Tuple[
            Action,
            t.Tuple[str, str]  # tuple[name, verspec]
        ]
    ]
    
    PyPIDiff = t.Iterator[
        t.Tuple[
            Action,
            t.Tuple[str, t.Optional[str]]  # tuple[filename, filepath]
        ]
    ]
    
    ManifestDiff = t.TypedDict('ManifestDiff', {
        'assets'      : AssetsDiff,
        'dependencies': DependenciesDiff,
        'pypi'        : PyPIDiff,
    })


AssetInfo = namedtuple('AssetInfo', (
    'type', 'scheme', 'utime', 'hash', 'uid'
))


# -----------------------------------------------------------------------------

def init_manifest(appid: str, appname: str) -> T.Manifest1:
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


def load_manifest(manifest_file: T.ManifestFile) -> T.Manifest1:
    manifest_file = fs.normpath(manifest_file, force_abspath=True)
    manifest_dir = fs.parent_path(manifest_file)
    
    data_i: t.Union[T.Manifest0, T.Manifest1] = loads(manifest_file)
    data_o: T.Manifest1 = {}
    
    if manifest_file.endswith('.pkl'):
        data_o = data_i  # noqa
        data_o['start_directory'] = manifest_dir
        return data_o
    
    # -------------------------------------------------------------------------
    
    # assert required keys
    required_keys = ('appid', 'name', 'version', 'assets')
    assert all(x in data_i for x in required_keys), (
        'the required keys are not complete',
        required_keys, tuple(data_i.keys())
    )
    
    data_o.update({
        'appid'          : data_i['appid'],
        'name'           : data_i['name'],
        'version'        : data_i['version'],
        'start_directory': manifest_dir,
        'assets'         : _update_assets(data_i['assets'], manifest_dir),
        'dependencies'   : _update_dependencies(data_i.get('dependencies', {})),
        'pypi'           : _update_pypi(data_i.get('pypi', []), manifest_dir),
        'launcher'       : _update_launcher(data_i.get('launcher', {})),
    })
    return data_o


def _update_assets(assets0: T.Assets0, manifest_dir: str) -> T.Assets1:
    out = {}
    for path, scheme in assets0.items():
        if os.path.isabs(path):
            abspath = fs.normpath(path)
            relpath = fs.relpath(path, manifest_dir)
        else:
            abspath = fs.normpath(f'{manifest_dir}/{path}')
            relpath = fs.normpath(path)
        out[relpath] = AssetInfo(
            type=(t := 'file' if os.path.isfile(abspath) else 'dir'),
            scheme=scheme or 'all',
            utime=(u := get_updated_time(abspath)),
            hash=(h := get_file_hash(abspath) if t == 'file' else None),
            uid=h or str(u),
        )
    return out  # noqa


def _update_dependencies(deps0: T.Dependencies0) -> T.Dependencies1:
    # just return as is.
    return deps0


def _update_pypi(pypi0: T.PyPI0, manifest_dir: str) -> T.PyPI1:
    out = {}
    for path in pypi0:
        if os.path.isabs(path):
            abspath = fs.normpath(path)
        else:
            abspath = fs.normpath(f'{manifest_dir}/{path}')
        out[fs.filename(abspath)] = abspath
    return out


def _update_launcher(launcher0: T.Launcher0) -> T.Launcher1:
    out = {'command': '', 'desktop': False, 'start_menu': False}
    out.update(launcher0)  # noqa
    return out


# -----------------------------------------------------------------------------

def dump_manifest(manifest: T.Manifest1, file_o: T.ManifestFile) -> None:
    manifest_i = manifest
    manifest_o: T.Manifest1 = manifest_i.copy()
    manifest_o['start_directory'] = fs.parent_path(file_o)
    if file_o.endswith('.json'):
        manifest_o['assets'] = _simplify_assets(manifest_i['assets'])  # noqa
    dumps(manifest_o, file_o)


def _simplify_assets(assets1: T.Assets1) -> T.Assets0:
    out = {}
    for path, info in assets1.items():
        out[path] = info.scheme
    return out


# -----------------------------------------------------------------------------
# more

def init_target_tree(manifest: T.Manifest1, root_dir: str = None) -> None:
    if not root_dir:
        root_dir = manifest['start_directory']
    print('init making tree', root_dir)
    paths_to_be_created = sorted(set(
        fs.normpath(f'{root_dir}/{k}')
        for k, v in manifest['assets'].items()
        if v.type == 'dir'
    ))
    print(':l', paths_to_be_created)
    [os.makedirs(x, exist_ok=True) for x in paths_to_be_created]


def compare_manifests(new: T.Manifest1, old: T.Manifest1) -> T.ManifestDiff:
    return {
        'assets'      : _compare_assets(
            new['assets'], old['assets'], new['start_directory']
        ),
        'dependencies': _compare_dependencies(
            new['dependencies'], old['dependencies']
        ),
        'pypi'        : _compare_pypi(
            new['pypi'], old['pypi']
        ),
    }


def _compare_assets(
        new: T.Assets1, old: T.Assets1, start_directory: str
) -> T.AssetsDiff:
    def is_same(new: T.AssetInfo, old: T.AssetInfo) -> bool:
        if new.scheme != old.scheme:
            return False
        if new.type != old.type:
            return False
        if new.uid != old.uid:
            return False
        return True
    
    for key0, info0 in old.items():
        if key0 not in new:
            yield 'delete', key0, (info0, None)
    
    for key1, info1 in new.items():
        if key1 not in old:
            yield 'append', f'{start_directory}/{key1}', (None, info1)
        info0 = old[key1]
        if not is_same(info1, info0):
            yield 'update', f'{start_directory}/{key1}', (info0, info1)
        else:
            yield 'ignore', f'{start_directory}/{key1}', (info0, info1)


def _compare_dependencies(
        new: T.Dependencies1, old: T.Dependencies1
) -> T.DependenciesDiff:
    for name0, verspec0 in old.items():
        if name0 not in new:
            yield 'delete', (name0, verspec0)
    for name1, verspec1 in new.items():
        if name1 not in old:
            yield 'append', (name1, verspec1)
        verspec0 = old[name1]
        if verspec1 != verspec0:
            yield 'update', (name1, verspec1)
        else:
            yield 'ignore', (name1, verspec1)


def _compare_pypi(
        new: T.PyPI1, old: T.PyPI1
) -> T.PyPIDiff:
    for name0, _ in old.items():  # the old.values() are all None.
        if name0 not in new:
            yield 'delete', (name0, None)
    for name1, path1 in new.items():  # path1 is a local abspath to a whl file.
        if name1 not in old:
            yield 'append', (name1, path1)
        else:
            yield 'ignore', (name1, path1)
