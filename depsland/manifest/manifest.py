"""
the core conception:
    manifest:
        manifest is a dict.
        all path-typed items in this dict must be relative paths - except \
        'start_directory' and 'pypi' - they are abspath.
        usually if you want to get the file location from an item, you need to \
        use `manifest['start_directory'] + some_relpath_item`.
            to simplify this transition, we provide a function \
            `finalize_manifest(manifest)`.
        why we are using relpaths, why we don't all use abspaths directly?
            because we may change the start_directory in runtime, we don't want
            to couple them too much.
            besides, loading and dumping relpath-typed items are more \
            universal than abs-ones.
"""
import os
import typing as t
from collections import namedtuple
from os.path import exists
from textwrap import dedent
from time import sleep

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

from ..utils import get_content_hash
from ..utils import get_file_hash
from ..utils import get_updated_time
from ..venv import target_venv
from ..venv.target_venv import T as T0

__all__ = [
    'T',
    'change_start_directory',
    'compare_manifests',
    'dump_manifest',
    'finalize_manifest',
    'init_manifest',
    'init_target_tree',
    'load_manifest',
]


# noinspection PyTypedDict
class T:
    AbsPath = RelPath = AnyPath = str
    #   the RelPath is relative to manifest file's location.
    
    ExpandedPackageNames = T0.PackageRelations
    ExpandedPackages = T0.Packages0
    PackageName = T0.PackageName
    PackageVersion = T0.ExactVersion
    Packages = T0.Packages0
    
    Scheme0 = t.Literal[
        'root',
        'all',
        'all_dirs',
        'top',
        'top_files',
        'top_dirs',
        '',
        #   empty str means 'all'
    ]
    Scheme1 = t.Literal[
        'root', 'all', 'all_dirs', 'top', 'top_files', 'top_dirs'
    ]
    
    Assets0 = t.Dict[AnyPath, Scheme0]
    #   anypath: abspath or relpath, '/' or '\\' both allowed.
    #   scheme: scheme or empty string. if empty string, it means 'all'.
    Assets1 = t.Dict[
        RelPath,
        AssetInfo := t.NamedTuple(
            'AssetInfo',
            (
                ('type', t.Literal['file', 'dir']),
                ('scheme', Scheme1),
                ('utime', int),  # updated time
                ('hash', str),  # if type is dir, the hash is empty
                ('uid', str),  # the uid will be used as key to filename in oss.
            ),
        ),
    ]
    
    Dependencies0 = t.TypedDict(
        'Dependencies0',
        {
            'custom_host': t.List[PackageName],
            'official_host': t.List[PackageName],
        },
    )
    Dependencies1 = t.TypedDict(
        'Dependencies1',
        {  # a flatten list
            'custom_host': ExpandedPackages,
            'official_host': ExpandedPackages,
        },
    )
    
    Launcher0 = t.TypedDict(
        'Launcher0',
        {
            'target': AnyPath,
            'type': t.Literal['executable', 'module', 'package'],
            'icon': AnyPath,
            #   the origin icon could be: empty, a relpath, or an abspath.
            'args': t.List[t.Any],
            'kwargs': t.Dict[str, t.Any],
            'enable_cli': bool,
            'add_to_desktop': bool,
            'add_to_start_menu': bool,
            'show_console': bool,
        },
    )
    Launcher1 = Launcher0
    #   same with Launcher0 but 'target' and 'icon' are RelPath.
    
    # -------------------------------------------------------------------------
    
    # Manifest0
    #   this is a json-compatible dict. it is either made by user or dumped by
    #   `dump_manifest` function (when caller passes a '.json' file param to
    #   it).
    Manifest0 = t.TypedDict(
        'Manifest0',
        {
            'appid': str,
            'name': str,
            'version': str,
            'assets': Assets0,
            'dependencies': Dependencies0,
            'launcher': Launcher0,
            'depsland_version': str,
        },
        total=False,
    )
    
    # Manifest1
    #   this is core and unified data structure for program to use. it is
    #   loaded from a '.pkl' file, or parsed and formalized from a '.json' file
    #   (i.e. from `Manifest0` data).
    #   the differences between Manifest0 and Manifest1 are:
    #       1. ~1 has an unified path form (all must be abspath).
    #       2. ~1 has an extra key 'start_directory'.
    #       3. ~1's assets values are `namedtuple AssetInfo`.
    Manifest1 = t.TypedDict(
        'Manifest1',
        {
            'appid': str,
            'name': str,
            'version': str,
            'start_directory': AbsPath,
            'assets': Assets1,
            'dependencies': Dependencies1,
            'launcher': Launcher1,
            'depsland_version': str,
        },
    )
    
    ManifestFile = str  # a '.json' or '.pkl' file
    
    # -------------------------------------------------------------------------
    
    Action = t.Literal['append', 'update', 'delete', 'ignore']
    
    AssetsDiff = t.Iterator[
        t.Tuple[
            Action,
            RelPath,
            t.Tuple[t.Optional[AssetInfo], t.Optional[AssetInfo]],
            #   tuple[old_info, new_info]
        ]
    ]
    
    DependenciesDiff = t.Iterator[
        t.Tuple[Action, t.Tuple[T0.PackageId, str]]  # tuple[pkgid, hash]
    ]
    
    ManifestDiff = t.TypedDict(
        'ManifestDiff',
        {
            'assets': AssetsDiff,
            'dependencies': DependenciesDiff,
        },
    )


AssetInfo = namedtuple('AssetInfo', ('type', 'scheme', 'utime', 'hash', 'uid'))


# -----------------------------------------------------------------------------


def init_manifest(appid: str, appname: str) -> T.Manifest1:
    """return a manifest template."""
    from .. import __version__
    
    return {
        'appid': appid,
        'name': appname,
        'version': '0.0.0',
        'start_directory': '',
        'assets': {},
        'dependencies': {
            'custom_host': {},
            'official_host': {},
        },
        'launcher': {
            'target': '',
            'type': '',
            'icon': '',
            'args': [],
            'kwargs': {},
            'enable_cli': False,
            'add_to_desktop': True,
            'add_to_start_menu': False,
            'show_console': True,
        },
        'depsland_version': __version__,
    }


def load_manifest(manifest_file: T.ManifestFile, finalize=False) -> T.Manifest1:
    from .. import __version__
    
    manifest_file = fs.normpath(manifest_file, force_abspath=True)
    manifest_dir = fs.parent_path(manifest_file)
    
    data_i: t.Union[T.Manifest0, T.Manifest1] = loads(manifest_file)
    data_o: T.Manifest1 = {}
    
    if manifest_file.endswith('.pkl'):
        # skip precheck and postcheck.
        data_o = data_i  # noqa
        data_o['start_directory'] = manifest_dir
        if finalize:
            return finalize_manifest(data_o)
        return data_o
    
    # -------------------------------------------------------------------------
    
    _precheck_manifest(data_i)
    data_o.update(
        {
            'appid': data_i['appid'],
            'name': data_i['name'],
            'version': data_i['version'],
            'start_directory': manifest_dir,
            'assets': _update_assets(data_i.get('assets', {}), manifest_dir),
            'dependencies': _update_dependencies(
                manifest_dir,
                data_i.get(
                    'dependencies',
                    {
                        'custom_host': [],
                        'official_host': [],
                    },
                ),
            ),
            'launcher': _update_launcher(
                data_i.get('launcher', {}), manifest_dir
            ),
            'depsland_version': data_i.get('depsland_version', __version__),
        }
    )
    _postcheck_manifest(data_o)
    if finalize:
        return finalize_manifest(data_o)
    return data_o


def finalize_manifest(manifest: T.Manifest1) -> T.Manifest1:
    """replace all relpathed items to abs ones."""
    final_dict: T.Manifest1 = manifest.copy()
    root = final_dict['start_directory']
    
    def toabs(p: T.RelPath) -> T.AbsPath:
        return f'{root}/{p}'
    
    final_dict['assets'].clear()
    for k, v in manifest['assets'].items():
        final_dict['assets'][toabs(k)] = v
    
    for k in ('target', 'icon'):
        if v := final_dict['launcher'][k]:
            final_dict['launcher'][k] = toabs(v)  # noqa
    
    return t.cast(T.Manifest1, _FronzenDict(manifest, final_dict))


class _FronzenDict:
    def __init__(self, data0: T.Manifest1, data1: T.Manifest1):
        self.origin = data0
        self._data = data1
    
    def __getitem__(self, item: str) -> t.Any:
        return self._data[item]  # noqa
    
    def __setitem__(self, key: str, value: t.Any) -> None:
        raise Exception(
            'the finalized manifest cannot be modified.', (key, value)
        )
    
    def __iter__(self) -> t.Iterator:
        return iter(self._data)
    
    def __copy__(self) -> '_FronzenDict':
        return _FronzenDict(self.origin.copy(), self._data.copy())


def change_start_directory(manifest: T.Manifest1, new_dir: str) -> None:
    r"""
    this is (slightly) a better way to update `manifest['start_directory']`.
    ps: the traditional way (`manifest['start_directory'] = ...`) is still \
    available. but as a suggestion, if you want to follow this paradigm, you \
    can use regex to search `manifest\w*\['start_directory'\] = ` in your IDE \
    to find all legacy use cases.
    """
    manifest['start_directory'] = fs.abspath(new_dir)


# -----------------------------------------------------------------------------


def _precheck_manifest(manifest: T.Manifest0) -> None:
    # assert required keys
    required_keys = ('appid', 'name', 'version', 'assets')
    assert all(x in manifest for x in required_keys), (
        'the required keys are not complete',
        required_keys,
        tuple(manifest.keys()),
    )
    
    assert manifest['assets'], 'field `assets` cannot be empty!'
    assert all(not x.startswith('../') for x in manifest['assets']), (
        'manifest should be put at the root of project, and there shall be no '
        '"../" in your assets keys.'
    )
    
    launcher: T.Launcher1 = manifest['launcher']
    target = launcher['target']
    assert target, 'field `launcher.target` cannot be empty!'
    assert not target.startswith('../'), (
        (
            'manifest should be put at the root of project, and there shall be'
            ' no "../*" in your script path.'
        ),
        target,
    )
    
    # TODO: currently we don't support auto deduce launcher type.
    assert launcher['type'], (
        'you must set `launcher.type` apparently. depsland does not support '
        'auto deducing it yet.'
    )
    assert launcher['type'] in ('executable', 'module', 'package')


def _postcheck_manifest(manifest: T.Manifest1) -> None:
    launcher: T.Launcher1 = manifest['launcher']
    
    # check script
    target_path = '{}/{}'.format(
        manifest['start_directory'], launcher['target']
    )
    target_type = launcher['type']
    try:
        if target_type == 'module':
            assert target_path.endswith('.py')
            assert os.path.exists(target_path)
        elif target_type == 'package':
            assert os.path.isdir(target_path)
            assert os.path.exists('{}/__init__.py'.format(target_path))
            assert os.path.exists('{}/__main__.py'.format(target_path))
        else:
            assert os.path.exists(target_path)
    except AssertionError as e:
        raise Exception(
            'the target is not found in your file system', target_path
        ) from e
    
    # check icon
    if launcher['icon']:
        icon_path = '{}/{}'.format(
            manifest['start_directory'], launcher['icon']
        )
        assert os.path.exists(icon_path)
        
        assert icon_path.endswith('.ico'), (
            'make sure the icon file is ".ico" format. if you have other file '
            'type, please use a online converter (for example '
            'https://findicons.com/convert) to get one.'
        )
        
        icon_relpath = fs.relpath(icon_path, manifest['start_directory'])
        try:
            assert icon_relpath.startswith(tuple(manifest['assets'].keys()))
        except AssertionError:
            if '' in manifest['assets']:
                pass
            else:
                print(
                    dedent('''
                        the launcher icon is not added to your assets list.
                        you may stop current progress right now, and re-check
                        your manifest file.
                        (if you confirm that the icon is added, it may be a bug
                        from depsland.)
                    '''),
                    ':v3',
                )
                sleep(1)
        
        # TODO: check icon size and give suggestions (the icon is suggested
        #  128x128 or above.)
    
    if kwargs := launcher['kwargs']:
        assert all(' ' not in k for k in kwargs)
        # TODO: shall we check `'-' not in k`?
    
    if launcher['add_to_start_menu']:
        print(
            ':v3',
            '`launcher.add_to_start_menu` is not tested yet. this is an '
            'experimental feature.',
        )


# -----------------------------------------------------------------------------


def _update_assets(assets0: T.Assets0, start_directory: T.AbsPath) -> T.Assets1:
    def generate_hash() -> str:
        # nonlocal: abspath, ftype (file_type)
        # generate: fhash (file_hash)
        if ftype == 'file':
            return get_file_hash(abspath)
        return ''
    
    def generate_utime() -> int:
        # nonlocal: abspath, scheme
        # generate: utime (updated_time)
        if scheme in ('root', 'top', 'top_files', 'top_dirs'):
            return get_updated_time(abspath, recursive=False)
        else:
            return get_updated_time(abspath, recursive=True)
    
    def generate_uid() -> str:
        # nonlocal: ftype, relpath
        # generate: uid (hash_of_relpath)
        return get_content_hash(f'{ftype}:{relpath}')
    
    out = {}
    for path, scheme in assets0.items():
        if scheme == '':
            scheme = 'all'
        if os.path.isabs(path):
            abspath = fs.normpath(path)
            relpath = fs.relpath(path, start_directory)
        else:
            abspath = fs.normpath(f'{start_directory}/{path}')
            relpath = fs.normpath(path)
        if not exists(abspath):
            raise FileNotFoundError(path)
        # minor fix relpath
        if relpath == '.':
            # `fs.relpath` may return '.', we need to convert it to ''.
            relpath = ''
        out[relpath] = AssetInfo(
            type=(ftype := 'file' if os.path.isfile(abspath) else 'dir'),
            scheme=scheme,
            utime=generate_utime(),
            hash=generate_hash(),
            uid=generate_uid(),
        )
    return out  # noqa


def _update_dependencies(
    target_root: T.AbsPath, deps0: T.Dependencies0
) -> T.Dependencies1:
    _venv_index = target_venv.PackagesIndex(target_root)
    
    def expand_packages(
        key: t.Literal['custom_host', 'official_host']
    ) -> T.ExpandedPackages:
        names = target_venv.expand_package_names(
            deps0[key], _venv_index.packages
        )
        return {k: _venv_index.packages[k] for k in names}
    
    return {
        'custom_host': expand_packages('custom_host'),
        'official_host': expand_packages('official_host'),
    }


def _update_launcher(
    launcher0: T.Launcher0, start_directory: T.AbsPath
) -> T.Launcher1:
    out: T.Launcher1 = {
        'target': '',
        'type': '',  # noqa
        'icon': '',
        'args': [],
        'kwargs': {},
        'enable_cli': False,
        'add_to_desktop': False,
        'add_to_start_menu': False,
        'show_console': True,
    }
    out.update(launcher0)  # noqa
    
    # noinspection PyTypedDict
    def normalize_paths() -> None:
        for k in ('target', 'icon'):
            if v := out[k]:
                if os.path.isabs(v):
                    out[k] = fs.relpath(v, start_directory)
                else:
                    out[k] = fs.normpath(v)
    
    # noinspection PyUnusedLocal,PyTypedDict
    def deduce_type() -> None:
        if out['target'].endswith('.py'):
            out['type'] = 'module'
        elif out['target'] and (
            d := os.path.isdir('{}/{}'.format(start_directory, out['target']))
        ):
            if os.path.exists('{}/__init__.py'.format(d)) and os.path.exists(
                '{}/__main__.py'.format(d)
            ):  # noqa
                out['type'] = 'package'
            else:
                out['type'] = 'executable'
        else:
            raise Exception('cannot deduce the launcher type!', out['target'])
    
    normalize_paths()
    if not out['type']:
        deduce_type()
    return out


# -----------------------------------------------------------------------------


def dump_manifest(manifest: T.Manifest1, file_o: T.ManifestFile) -> None:
    if isinstance(manifest, _FronzenDict):
        manifest = manifest.origin
    manifest_i = manifest
    manifest_o: T.Manifest1 = manifest_i.copy()
    if file_o.endswith('.json'):
        manifest_o['assets'] = _plainify_assets(manifest_i['assets'])  # noqa
    manifest_o['start_directory'] = fs.parent_path(file_o)  # or set to ''?
    dumps(manifest_o, file_o)


def _plainify_assets(assets1: T.Assets1) -> T.Assets0:
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
    paths_to_be_created = set()
    for k, v in manifest['assets'].items():
        abspath = fs.normpath(f'{root_dir}/{k}')
        if v.type == 'dir':
            paths_to_be_created.add(abspath)
        else:
            paths_to_be_created.add(fs.parent_path(abspath))
    paths_to_be_created = sorted(paths_to_be_created)
    print(':l', paths_to_be_created)
    [os.makedirs(x, exist_ok=True) for x in paths_to_be_created]


def compare_manifests(new: T.Manifest1, old: T.Manifest1) -> T.ManifestDiff:
    return {
        'assets': _compare_assets(new['assets'], old['assets']),
        'dependencies': _compare_dependencies(
            new['dependencies'], old['dependencies']
        ),
    }


def _compare_assets(new: T.Assets1, old: T.Assets1) -> T.AssetsDiff:
    def is_same(new: T.AssetInfo, old: T.AssetInfo) -> bool:
        """
        comparing assets is considered based on a variety of factors:
            - scheme
            - type
            - hash
            - utime
        """
        if new.scheme == old.scheme == 'root':
            return True
        if new.scheme != old.scheme:
            return False
        if new.type != old.type:
            return False
        if new.hash == old.hash != '':
            return True
        if new.utime == old.utime:
            return True
        return False
    
    for key0, info0 in old.items():
        if key0 not in new:
            yield 'delete', key0, (info0, None)
    
    for key1, info1 in new.items():
        if key1 not in old:
            yield 'append', key1, (None, info1)
            continue
        info0 = old[key1]
        if not is_same(info1, info0):
            yield 'update', key1, (info0, info1)
        else:
            yield 'ignore', key1, (info0, info1)


# TODO
def _compare_dependencies(
    new: T.Dependencies1, old: T.Dependencies1
) -> T.DependenciesDiff:
    old_custom = old['custom_host']
    new_custom = new['custom_host']
    
    for name0, v0 in old_custom.items():
        if name0 not in new_custom:
            yield 'delete', (name0, v0['hash'])
            continue
        
        name1, v1 = name0, new_custom[name0]
        if v1['type'] != v0['type'] or v1['hash'] != v0['hash']:
            # TODO: update?
            yield 'delete', (name0, v0['hash'])
            yield 'append', (name1, v1['hash'])
        else:
            yield 'ignore', (name0, v0['hash'])
    
    for name1, v1 in new_custom.items():
        if name1 not in old_custom:
            yield 'append', (name1, v1['hash'])
