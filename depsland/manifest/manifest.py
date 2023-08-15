import os
import typing as t
from collections import namedtuple
from copy import deepcopy
from os.path import exists
from textwrap import dedent
from time import sleep

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

from .. import normalization as norm
from ..utils import get_content_hash
from ..utils import get_file_hash
from ..utils import get_updated_time
from ..venv import target_venv
from ..venv.target_venv import T as T0
from ..venv.target_venv import get_library_root


# noinspection PyTypedDict
class T:
    AbsPath = RelPath = AnyPath = str
    #   the RelPath is relative to manifest file's location.
    
    ExpandedPackageNames = T0.PackageRelations
    ExpandedPackages = T0.Packages
    # PackageId = T0.PackageId
    PackageInfo = T0.PackageInfo
    PackageName = T0.PackageName
    PackageVersion = T0.ExactVersion
    Packages = T0.Packages
    
    Scheme0 = t.Literal[
        'root', 'all', 'all_dirs', 'top', 'top_files', 'top_dirs',  # fmt:skip
        ''  # empty str means 'all'  # fmt:skip
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
    Assets2 = t.Dict[AbsPath, AssetInfo]
    
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
            'root': AbsPath,
            'custom_host': ExpandedPackages,
            'official_host': ExpandedPackages,
        },
    )
    Dependencies2 = t.TypedDict(
        'Dependencies2',
        {  # all path related items are abspaths.
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
    Launcher2 = Launcher1
    #   same with Launcher1 but 'target' and 'icon' are AbsPath.
    
    # -------------------------------------------------------------------------
    
    # Manifest0: original manifest
    #   this is a json-compatible dict. it is either made by user or dumped by \
    #   `dump_manifest` function (when caller passes a '.json' file param to \
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
    
    # Manifest1: standard manifest
    #   this is core and unified data structure for program to use. it is \
    #   loaded from a '.pkl' file, or parsed from a '.json' file by \
    #   `Manifest.load_from_file`.
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
    
    # Manifest2: finalized manifest for easy accessing path-based items.
    Manifest2 = t.TypedDict(
        'Manifest2',
        {
            'appid': str,
            'name': str,
            'version': str,
            'start_directory': AbsPath,
            'assets': Assets2,
            'dependencies': Dependencies2,
            'launcher': Launcher2,
            'depsland_version': str,
        },
    )
    
    # -------------------------------------------------------------------------
    
    Action = t.Literal['append', 'update', 'delete', 'ignore']
    
    AssetsDiff = t.Iterator[
        t.Tuple[
            Action,
            RelPath,
            t.Tuple[
                t.Optional[AssetInfo],
                t.Optional[AssetInfo],
            ],
        ]
    ]
    
    DependenciesDiff = t.Iterator[
        t.Tuple[
            Action,
            PackageName,
            t.Tuple[
                t.Optional[t.Tuple[T0.PackageId, t.Tuple[AbsPath, ...]]],
                t.Optional[t.Tuple[T0.PackageId, t.Tuple[AbsPath, ...]]],
            ],
        ]
    ]
    
    # see `depsland.api.dev_api.publish._upload`
    ManifestDiff = t.TypedDict(
        'ManifestDiff',
        {
            'assets': AssetsDiff,
            'dependencies': DependenciesDiff,
        },
    )


# -----------------------------------------------------------------------------


def init_manifest(appname: str, appid: str) -> 'Manifest':
    return Manifest.init(appname, appid)


def load_manifest(file: T.AnyPath) -> t.Union[T.Manifest2, 'Manifest']:
    out = Manifest()
    out.load_from_file(file)
    return out


def dump_manifest(manifest: 'Manifest', file: T.AnyPath) -> None:
    assert isinstance(manifest, Manifest)
    manifest.dump_to_file(file)


def diff_manifest(new: 'Manifest', old: 'Manifest') -> T.ManifestDiff:
    return {
        'assets': _diff_assets(
            new['assets'], old['assets']  # fmt:skip
        ),
        'dependencies': _diff_dependencies(
            new['dependencies'], old['dependencies']
        ),
    }


# -----------------------------------------------------------------------------


AssetInfo = namedtuple('AssetInfo', ('type', 'scheme', 'utime', 'hash', 'uid'))


class Manifest:
    _file: T.AbsPath
    _manifest1: T.Manifest1
    _manifest2: T.Manifest2
    _start_directory: T.AbsPath
    _venv_library_root: T.AbsPath
    
    @classmethod
    def init(cls, appid: str, appname: str) -> 'Manifest':
        from .. import __version__
        
        out = Manifest()
        
        out._file = ''
        out._start_directory = ''
        out._venv_library_root = ''
        
        out._manifest2 = out._manifest1 = {
            'appid': appid,
            'name': appname,
            'version': '0.0.0',
            'start_directory': '',
            'assets': {},
            'dependencies': {
                'root': '',
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
        
        return out
    
    def load_from_file(self, file: T.AnyPath) -> None:
        """
        args:
            file: a '.json' or a '.pkl' file.
        """
        from .. import __version__
        
        self._file = fs.abspath(file)
        self._start_directory = fs.parent_path(self._file)
        self._venv_library_root = get_library_root(self._start_directory)
        
        data0: t.Union[T.Manifest0, T.Manifest1]
        data1: T.Manifest1
        
        if self._file.endswith('.pkl'):
            data0: T.Manifest1 = loads(self._file)
            data1 = data0
            data1['start_directory'] = self._start_directory
        else:
            assert self._file.endswith('.json')
            data0: T.Manifest0 = loads(self._file)
            
            self._precheck_manifest(data0)
            data1 = {
                'appid': data0['appid'],
                'name': data0['name'],
                'version': data0['version'],
                'start_directory': self._start_directory,
                'assets': self._update_assets(
                    data0.get('assets', {}),
                    self._start_directory,
                ),
                'dependencies': self._update_dependencies(
                    self._start_directory,
                    data0.get('dependencies', {
                        'custom_host': [],
                        'official_host': [],
                    }),
                ),
                'launcher': self._update_launcher(
                    data0.get('launcher', {}),
                    self._start_directory,
                ),
                'depsland_version': data0.get(
                    'depsland_version',
                    __version__,
                ),
            }
            
            self._postcheck_manifest(data1)
        
        self._manifest1 = data1
        self._finalize_mainfest()
    
    def dump_to_file(self, file: T.AnyPath = None) -> None:
        if file is None:
            file = self._file
        
        data1: T.Manifest1 = self._manifest1
        data0: T.Manifest0 = self._manifest1.copy()
        
        if file.endswith('.pkl'):
            data0['start_directory'] = fs.parent_path(fs.abspath(file))  # noqa
            #   or set to ''?
        else:
            data0.pop('start_directory')
            data0['assets'] = self._plainify_assets(data1['assets'])
            data0['dependencies'] = self._plainify_dependencies(
                data1['dependencies']
            )
        
        dumps(data0, file)
    
    # -------------------------------------------------------------------------
    
    @property
    def data(self) -> T.Manifest2:
        return self._manifest2
    
    def to_dict(self) -> T.Manifest1:
        return self._manifest1
    
    @property
    def start_directory(self) -> T.AbsPath:
        return self._start_directory
    
    @start_directory.setter
    def start_directory(self, path: T.AnyPath) -> None:
        path = fs.abspath(path)
        self._start_directory = path
        self._finalize_mainfest()
    
    def __getitem__(self, item: str) -> t.Any:
        if item == 'start_directory':
            return self._start_directory
        return self._manifest2[item]  # noqa
    
    def __setitem__(self, key: str, value: t.Any) -> None:
        if key == 'start_directory':
            self.start_directory = value
        else:
            raise Exception('cannot modify top field of manifest!', key, value)
    
    def _finalize_mainfest(self) -> None:
        dir0 = self._start_directory
        dir1 = self._venv_library_root
        
        data1: T.Manifest1 = self._manifest1
        data2: T.Manifest2 = {
            'appid': data1['appid'],
            'name': data1['name'],
            'version': data1['version'],
            'start_directory': data1['start_directory'],
            'assets': {f'{dir0}/{k}': v for k, v in data1['assets'].items()},
            'dependencies': deepcopy(data1['dependencies']),
            'launcher': data1['launcher'],
            'depsland_version': data1['depsland_version'],
        }
        # postfix dependencies
        for k, v in data2['dependencies']['custom_host'].items():
            v['paths'] = tuple(f'{dir1}/{x}' for x in v['paths'])
        
        self._manifest2 = data2
    
    # -------------------------------------------------------------------------
    
    @staticmethod
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
            'manifest should be put at the root of project, and there shall be '
            'no "../" in your assets keys.'
        )
        
        launcher: T.Launcher1 = manifest['launcher']
        target = launcher['target']
        assert target, 'field `launcher.target` cannot be empty!'
        assert not target.startswith('../'), (
            (
                'manifest should be put at the root of project, and there '
                'shall be no "../*" in your script path.'
            ),
            target,
        )
        
        # TODO: currently we don't support auto deduce launcher type.
        assert launcher['type'], (
            'you must set `launcher.type` apparently. depsland does not '
            'support auto deducing it yet.'
        )
        assert launcher['type'] in ('executable', 'module', 'package')
    
    @staticmethod
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
                'make sure the icon file is ".ico" format. if you have other '
                'file type, please use a online converter (for example '
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
                            you may stop current progress right now, and
                            re-check your manifest file.
                            (if you confirm that the icon is added, it may be a
                            bug from depsland.)
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
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _update_assets(
        assets0: T.Assets0, start_directory: T.AbsPath
    ) -> T.Assets1:
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
                raise FileNotFoundError(
                    'please check the path you defined in manifest does exist',
                    path
                )
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
    
    @staticmethod
    def _update_dependencies(
        working_root: T.AbsPath, deps0: T.Dependencies0
    ) -> T.Dependencies1:
        indexer = target_venv.LibraryIndexer(working_root)
        
        def expand_packages(
            key: t.Literal['custom_host', 'official_host']
        ) -> T.ExpandedPackages:
            names = target_venv.expand_package_names(
                map(norm.normalize_name, deps0[key]),
                indexer.packages
            )
            return {k: indexer.packages[k] for k in names}
        
        return {
            'root': indexer.library_root,
            'custom_host': expand_packages('custom_host'),
            'official_host': expand_packages('official_host'),
        }
    
    @staticmethod
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
                d := os.path.isdir(
                    '{}/{}'.format(start_directory, out['target'])
                )
            ):
                if os.path.exists(
                    '{}/__init__.py'.format(d)
                ) and os.path.exists(
                    '{}/__main__.py'.format(d)
                ):  # noqa
                    out['type'] = 'package'
                else:
                    out['type'] = 'executable'
            else:
                raise Exception(
                    'cannot deduce the launcher type!', out['target']
                )
        
        normalize_paths()
        if not out['type']:
            deduce_type()
        return out
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _plainify_assets(assets1: T.Assets1) -> T.Assets0:
        out = {}
        for path, info in assets1.items():
            out[path] = info.scheme
        return out
    
    @staticmethod
    def _plainify_dependencies(deps: T.Dependencies1) -> T.Dependencies0:
        return {
            'custom_host': [k for k in deps['custom_host']],
            'official_host': [k for k in deps['official_host']],
        }


# -----------------------------------------------------------------------------


def _diff_assets(new: T.Assets1, old: T.Assets1) -> T.AssetsDiff:
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


def _diff_dependencies(
    new: T.Dependencies2, old: T.Dependencies2
) -> T.DependenciesDiff:
    old_custom = old['custom_host']
    new_custom = new['custom_host']
    
    v0: T.PackageInfo
    v1: T.PackageInfo
    
    for name0, v0 in old_custom.items():
        if name0 not in new_custom:
            yield 'delete', name0, (
                (v0['package_id'], v0['paths']),
                (None, None),
            )
            continue
        
        name1, v1 = name0, new_custom[name0]
        if v1['package_id'] != v0['package_id']:
            yield 'update', name1, (
                (v0['package_id'], v0['paths']),
                (v1['package_id'], v1['paths']),
            )
        else:
            yield 'ignore', name0, (
                (v0['package_id'], v0['paths']),
                (v1['package_id'], v1['paths']),
            )
    
    for name1, v1 in new_custom.items():
        if name1 not in old_custom:
            yield 'append', name1, (
                (None, None),
                (v1['package_id'], v1['paths']),
            )
