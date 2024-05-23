import os
import typing as t
from collections import namedtuple
from os.path import exists
from textwrap import dedent
from time import sleep

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

from .. import normalization as norm
from ..depsolver import T as T0
from ..depsolver import resolve_dependencies
from ..utils import get_content_hash
from ..utils import get_file_hash
from ..utils import get_updated_time


# noinspection PyTypedDict
class T(T0):
    AbsPath = RelPath = AnyPath = str
    #   the RelPath is relative to manifest file's location.
    
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
    
    Dependencies0 = t.Union[
        # 1. no dependency
        None,
        # 2. a file path, usually 'pyproject.toml', 'requirements.txt', etc.
        str,
        # 3. a list of packages. e.g. ['requests', 'numpy>=1.26', ...]
        t.List[str],
        # 4. packages with more detailed definitions. e.g.
        #   {
        #       'numpy': [
        #           {'version': '1.26.2', 'platform': 'linux'},
        #           {'version': '*', 'platform': '!=linux'},
        #       ], ...
        #   }
        t.Dict[str, t.Union[str, dict, list]],
    ]
    Dependencies1 = T0.Packages
    
    Launcher0 = t.TypedDict(
        'Launcher0',
        {
            'target'           : AnyPath,
            'type'             : t.Literal['executable', 'module', 'package'],
            'icon'             : AnyPath,
            #   the origin icon could be: empty, a relpath, or an abspath.
            'args'             : t.List[t.Any],
            'kwargs'           : t.Dict[str, t.Any],
            'enable_cli'       : bool,
            'add_to_desktop'   : bool,
            'add_to_start_menu': bool,
            'show_console'     : bool,
        },
    )
    Launcher1 = Launcher0
    #   same with Launcher0 but 'target' and 'icon' are RelPath.
    #   FIXME: why we use relpath?
    
    # -------------------------------------------------------------------------
    
    # Manifest0: original manifest
    #   this is a json-compatible dict. it is either made by user or dumped by \
    #   `dump_manifest` function (when caller passes a '.json' file param to \
    #   it).
    Manifest0 = t.TypedDict(
        'Manifest0',
        {
            'appid'           : str,
            'name'            : str,
            'version'         : str,
            'assets'          : Assets0,
            'dependencies'    : Dependencies0,
            'launcher'        : Launcher0,
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
            'appid'           : str,
            'name'            : str,
            'version'         : str,
            'start_directory' : AbsPath,
            'assets'          : Assets1,
            'dependencies'    : Dependencies1,
            'launcher'        : Launcher1,
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
            T0.PackageName,
            t.Tuple[
                t.Optional[T0.PackageInfo],
                t.Optional[T0.PackageInfo],
            ],
        ]
    ]
    
    # see `depsland.api.dev_api.publish._upload`
    ManifestDiff = t.TypedDict(
        'ManifestDiff',
        {
            'assets'      : AssetsDiff,
            'dependencies': DependenciesDiff,
        },
    )


# -----------------------------------------------------------------------------


def init_manifest(appid: str, appname: str) -> 'Manifest':
    return Manifest.init(appid, appname)


def load_manifest(file: T.AnyPath) -> 'Manifest':
    return Manifest.load_from_file(file)


def dump_manifest(manifest: 'Manifest', file: T.AnyPath) -> None:
    assert isinstance(manifest, Manifest)
    manifest.dump_to_file(file)


def diff_manifest(new: 'Manifest', old: 'Manifest') -> T.ManifestDiff:
    return {
        'assets'      : _diff_assets(
            new.model['assets'],
            old.model['assets'],
        ),
        'dependencies': _diff_dependencies(
            new['dependencies'],
            old['dependencies'],
        )
    }


# -----------------------------------------------------------------------------


AssetInfo = namedtuple('AssetInfo', ('type', 'scheme', 'utime', 'hash', 'uid'))


class Manifest:
    _file: T.AbsPath
    _manifest: T.Manifest1
    _start_directory: T.AbsPath
    
    @classmethod
    def init(cls, appid: str, appname: str) -> 'Manifest':
        from .. import __version__
        
        self = Manifest()
        
        self._file = ''
        self._start_directory = ''
        
        self._manifest = {
            'appid'           : appid,
            'name'            : appname,
            'version'         : '0.0.0',
            'start_directory' : '',
            'assets'          : {},
            'dependencies'    : {},
            'launcher'        : {
                'target'           : '',
                'type'             : '',
                'icon'             : '',
                'args'             : [],
                'kwargs'           : {},
                'enable_cli'       : False,
                'add_to_desktop'   : True,
                'add_to_start_menu': False,
                'show_console'     : True,
            },
            'depsland_version': __version__,
        }
        
        return self
    
    @classmethod
    def load_from_file(cls, file: T.AnyPath) -> 'Manifest':
        """
        args:
            file: a '.json' or a '.pkl' file.
        """
        from .. import __version__
        
        self = Manifest()
        self._file = fs.abspath(file)
        self._start_directory = fs.parent(self._file)
        
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
                'appid'           : data0['appid'],
                'name'            : data0['name'],
                'version'         : data0['version'],
                'start_directory' : self._start_directory,
                'assets'          : self._update_assets(
                    data0.get('assets', {}), self._start_directory
                ),
                'dependencies'    : self._update_dependencies(
                    data0.get('dependencies', 'requirements.lock'),
                ),
                'launcher'        : self._update_launcher(
                    data0.get('launcher', {}), self._start_directory
                ),
                'depsland_version': data0.get(
                    'depsland_version', __version__
                ),
            }
            self._postcheck_manifest(data1)
        
        self._manifest = data1
        return self
    
    def dump_to_file(self, file: T.AnyPath = None) -> None:
        if file is None:
            file = self._file
        
        data1: T.Manifest1 = self._manifest
        data0: T.Manifest0 = self._manifest.copy()
        
        if file.endswith('.pkl'):
            data0['start_directory'] = fs.parent_path(fs.abspath(file))  # noqa
            #   or set to ''?
        else:
            data0.pop('start_directory')
            data0['assets'] = self._plainify_assets(data1['assets'])
        
        dumps(data0, file)
    
    # -------------------------------------------------------------------------
    
    @property
    def model(self) -> T.Manifest1:
        return self._manifest
    
    @property
    def start_directory(self) -> T.AbsPath:
        return self._start_directory
    
    @start_directory.setter
    def start_directory(self, path: T.AnyPath) -> None:
        path = fs.abspath(path)
        self._start_directory = path
    
    def __getitem__(self, item: str) -> t.Any:
        if item == 'start_directory':
            return self._start_directory
        return self._manifest[item]  # noqa
    
    def __setitem__(self, key: str, value: t.Any) -> None:
        if key == 'start_directory':
            self.start_directory = value
        else:
            raise Exception('cannot modify top field of manifest!', key, value)
    
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
        
        assert norm.check_name_normalized(manifest['appid']), (
            'the appid should be lowercase and only contains alphanumber and '
            'underscore.'
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
                assert exists(target_path)
            elif target_type == 'package':
                assert os.path.isdir(target_path)
                assert exists('{}/__init__.py'.format(target_path))
                assert exists('{}/__main__.py'.format(target_path))
            else:
                assert exists(target_path)
        except AssertionError as e:
            raise Exception(
                'the target is not found in your file system', target_path
            ) from e
        
        # check icon
        if launcher['icon']:
            icon_path = '{}/{}'.format(
                manifest['start_directory'], launcher['icon']
            )
            assert exists(icon_path)
            
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
    
    def _update_dependencies(self, deps0: T.Dependencies0) -> T.Dependencies1:
        return resolve_dependencies(deps0, self._start_directory)
    
    @staticmethod
    def _update_launcher(
        launcher0: T.Launcher0, start_directory: T.AbsPath
    ) -> T.Launcher1:
        out: T.Launcher1 = {
            'target'           : '',
            'type'             : '',  # noqa
            'icon'             : '',
            'args'             : [],
            'kwargs'           : {},
            'enable_cli'       : False,
            'add_to_desktop'   : False,
            'add_to_start_menu': False,
            'show_console'     : True,
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
                if exists(
                    '{}/__init__.py'.format(d)
                ) and exists(
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


def _diff_dependencies(new: T.Packages, old: T.Packages) -> T.DependenciesDiff:
    info0: T.PackageInfo
    info1: T.PackageInfo
    
    for name0, info0 in old.items():
        if name0 not in new:
            yield 'delete', name0, (info0, None)
            continue
        
        name1, info1 = name0, new[name0]
        if info1['version'] != info0['version']:
            yield 'update', name1, (info0, info1)
        else:
            yield 'ignore', name0, (info0, info1)
    
    for name1, info1 in new.items():
        if name1 not in old:
            yield 'append', name1, (None, info1)
