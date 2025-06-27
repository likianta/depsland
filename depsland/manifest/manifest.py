import os
import shlex
import typing as t
from collections import namedtuple
from functools import cache

from lk_utils import fs

from .. import normalization as norm
from ..depsolver import T as T0
from ..depsolver import resolve_dependencies
from ..utils import get_content_hash
from ..utils import get_file_hash
from ..utils import get_updated_time
from ..utils import init_target_tree


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
    # ^ see also `depsland.api.dev_api.publish._copy_assets`
    
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
    
    # fmt:off
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
    # fmt:on
    
    Launcher0 = t.TypedDict(
        'Launcher0',
        {
            'command'          : t.Union[str, list],
            'icon'             : AnyPath,  # empty, relpath, or abspath.
            'show_console'     : bool,
            'enable_cli'       : bool,
            'add_to_desktop'   : bool,
            'add_to_start_menu': bool,
        },
        total=False,
    )
    Launcher1 = t.TypedDict(
        'Launcher1',
        {
            'command'          : str,
            'icon'             : AbsPath,  # abspath or empty
            'show_console'     : bool,
            'enable_cli'       : bool,
            'add_to_desktop'   : bool,
            'add_to_start_menu': bool,
        },
    )
    
    Experiments0 = t.TypedDict(
        'Experiments0',
        {
            'package_provider'  : t.Literal['oss', 'pypi'],
        },
        total=False
    )
    Experiments1 = Experiments0
    
    # -------------------------------------------------------------------------
    
    # Manifest0: original manifest
    #   this is a json-compatible dict. it is either made by user or dumped by -
    #   `dump_manifest` function (when caller passes a '.json' file param to it).
    Manifest0 = t.TypedDict(
        'Manifest0',
        # note: not all keys are required, check details in -
        # `Manifest._precheck_manifest`.
        {
            'appid'           : str,
            'name'            : str,
            'version'         : str,
            'start_directory' : AnyPath,
            'readme'          : AnyPath,
            'assets'          : Assets0,
            'dependencies'    : Dependencies0,
            'launcher'        : Launcher0,
            'experiments'     : Experiments0,
            'depsland_version': str,
        },
        total=False,
    )
    
    # Manifest1: standard manifest
    #   this is core and unified data structure for program to use. it is -
    #   loaded from a '.pkl' file, or parsed from a '.json' file by -
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
            'readme'          : AbsPath,  # abspath or empty
            'assets'          : Assets1,
            'dependencies'    : Dependencies1,
            'launcher'        : Launcher1,
            'experiments'     : Experiments1,
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
            'readme'          : '',
            'assets'          : {},
            'dependencies'    : {},
            'launcher'        : {
                'command'          : '',
                'icon'             : '',
                'show_console'     : True,
                'enable_cli'       : False,
                'add_to_desktop'   : True,
                'add_to_start_menu': False,
            },
            'experiments'     : {
                'package_provider'  : 'pypi',
            },
            'depsland_version': __version__,
        }
        
        return self
    
    @classmethod
    @cache
    def load_from_file(cls, file: T.AnyPath) -> 'Manifest':
        """
        args:
            file: support '.json', '.yaml'/'.yml', '.pkl' formats.
                the pickle format was generated by depsland itself, and trusted
                by depsland. loading pickle file is faster (since it skips many
                check steps) and more stable (reproducible).
        """
        from .. import __version__
        
        self = Manifest()
        self._file = fs.abspath(file)
        self._start_directory = fs.parent(self._file)
        
        data0: t.Union[T.Manifest0, T.Manifest1]
        data1: T.Manifest1
        
        if self._file.endswith('.pkl'):
            data0: T.Manifest1 = fs.load(self._file)
            data1 = data0
            data1['start_directory'] = self._start_directory
            if relpath := data0.get('readme'):
                data1['readme'] = '{}/{}'.format(
                    self._start_directory, relpath
                )
            if relpath := data0['launcher']['icon']:
                data1['launcher']['icon'] = '{}/{}'.format(
                    self._start_directory, relpath
                )
        else:
            data0: T.Manifest0
            if self._file.endswith(('.json', '.yaml')):
                data0 = fs.load(self._file)
            elif fs.basename(self._file) == 'pyproject.toml':
                data0 = fs.load(self._file)['tool']['depsland']['manifest']
            elif self._file.endswith('.toml'):
                try:
                    # noinspection PyUnusedLocal
                    data0 = fs.load(self._file)['tool']['depsland']['manifest']
                except KeyError:
                    data0 = fs.load(self._file)
            else:
                raise Exception('unsupported manifest file format', self._file)
            
            if 'start_directory' in data0:
                x = data0['start_directory']
                if x.startswith('.'):
                    self._start_directory = fs.abspath(
                        '{}/{}'.format(fs.parent(self._file), x)
                    )
                else:
                    self._start_directory = fs.abspath(x)
                print('change `start_directory` to {}'.format(
                    self._start_directory
                ))
            if data0.get('readme'):
                data0['assets'][data0['readme']] = 'all'
            if data0['launcher'].get('icon'):
                data0['assets'][data0['launcher']['icon']] = 'all'
            
            self._precheck_manifest(data0)
            data1 = {
                'appid'           : data0['appid'],
                'name'            : data0['name'],
                'version'         : data0['version'],
                'start_directory' : self._start_directory,
                'readme'          : self._update_readme_file(
                    data0.get('readme', '')
                ),
                'assets'          : self._update_assets(
                    data0['assets'], self._start_directory,
                ),
                'dependencies'    : self._update_dependencies(
                    data0.get('dependencies', 'requirements.lock'),
                ),
                'launcher'        : self._update_launcher(
                    data0['launcher'], self._start_directory,
                ),
                'experiments'     : data0.get('experiments', {
                    'package_provider'  : 'pypi',
                }),
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
        if fs.basename(file) == 'pyproject.toml':
            # TODO: how to reserve original comments?
            raise NotImplementedError(file)
        
        data1: T.Manifest1 = self._manifest
        data0: T.Manifest0 = self._manifest.copy()
        
        # modify `data0` fields
        # be noticed some of `data0.values()` are list or dict types, which -
        # should be deep copied if we want to modify their inner items, to -
        # avoid affecting the original data of `data1`.
        data0.pop('start_directory')
        if abspath := data1['readme']:
            data0['readme'] = fs.relpath(
                abspath, self._start_directory
            )
        if abspath := data1['launcher']['icon']:
            data0['launcher'] = data1['launcher'].copy()  # "deepcopy"
            data0['launcher']['icon'] = fs.relpath(
                abspath, self._start_directory
            )
            # print(
            #     file,
            #     icon_path,
            #     self._start_directory,
            #     data0['launcher']['icon'],
            #     ':vl'
            # )
        if not file.endswith('.pkl'):
            data0['assets'] = self._plainify_assets(data1['assets'])
            if file.endswith('.toml'):
                data0 = {'tool': {'depsland': {'manifest': data0}}}  # noqa
        
        fs.dump(data0, file)
    
    def make_tree(self, root: str = None) -> None:
        if not root:
            root = self.start_directory
        relpaths = []
        for k, v in self._manifest['assets'].items():
            if v.type == 'dir':
                relpaths.append(k)
            else:
                if '/' in k:
                    relpaths.append(k.rsplit('/', 1)[0])
        init_target_tree(root, relpaths)
    
    # -------------------------------------------------------------------------
    
    @property
    def model(self) -> T.Manifest1:
        return self._manifest
    
    @property
    def start_directory(self) -> T.AbsPath:
        return self._start_directory
    
    @start_directory.setter
    def start_directory(self, path: T.AnyPath) -> None:
        old, new = self._start_directory, fs.abspath(path)
        if x := self._manifest['launcher']['icon']:
            relpath = fs.relpath(x, old)
            self._manifest['launcher']['icon'] = '{}/{}'.format(new, relpath)
        self._start_directory = new
    
    def get(self, item: str) -> t.Any:
        return self._manifest.get(item)  # noqa
    
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
        required_keys = ('appid', 'name', 'version', 'assets', 'launcher')
        assert all(x in manifest for x in required_keys), (
            'the required keys are not complete',
            required_keys,
            tuple(manifest.keys()),
        )
        
        assert norm.check_name_normalized(manifest['appid']), (
            'the appid should be lowercase and only contain alphanumber and '
            'underscore.'
        )
        
        if manifest.get('readme'):
            assert '.' in fs.filename(manifest['readme']), (
                'there should be a file extension in your readme file name.'
                # otherwise it maybe a directory or, we cannot make a proper -
                # name for it in installation stage.
                # see also:
                #   - `self._postcheck_manifest`
                #   - `/depsland/api/dev_api/build_offline.py:_create_launcher`
                #   - `/depsland/api/user_api/install.py:_create_launchers`
            )
        
        assert manifest['assets'], 'field `assets` cannot be empty!'
        assert all(not x.startswith('../') for x in manifest['assets']), (
            'manifest should be put at the root of project, and there shall be '
            'no "../" in your assets keys.'
        )
        
        launcher: T.Launcher0 = manifest['launcher']
        assert launcher['command'], 'field `launcher.command` cannot be empty!'
        if '<python>' in launcher['command']:
            # print(':v6', '"<python>" is deprecate to use, use just "python"')
            # if isinstance(launcher['command'], str):
            #     launcher['command'] = \
            #         launcher['command'].replace('<python>', 'python')
            # else:
            #     assert launcher['command'][0] == '<python>'
            #     launcher['command'][0] = 'python'
            raise Exception(
                '"<python>" is deprecate to use, use just "python" in your '
                'launcher command.'
            )
    
    @staticmethod
    def _postcheck_manifest(manifest: T.Manifest1) -> None:
        if manifest['readme']:
            assert fs.isfile(manifest['readme'])
        if icon_path := manifest['launcher']['icon']:
            # assert fs.exist(icon_path) and os.path.isabs(icon_path)
            assert icon_path.endswith('.ico'), (
                'make sure the icon file is ".ico" format. if you have other '
                'file type, please use a online converter (for example '
                'https://findicons.com/convert) to get one.'
            )
            # TODO: check icon size and give suggestions (the icon is suggested
            #  128x128 or above.)
        if manifest['launcher']['add_to_start_menu']:
            print(
                ':v6',
                '`launcher.add_to_start_menu` is not tested yet. this is an '
                'experimental feature.',
            )
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _update_assets(
        assets0: T.Assets0, start_directory: T.AbsPath,
    ) -> T.Assets1:
        """
        varibale abbreviations:
            ftype: file type
            relpath: relative path
            utime: updated time
        """
        def generate_hash(abspath: str, ftype: str) -> str:
            if ftype == 'file':
                return get_file_hash(abspath)
            # if calculate_dir_hash:
            #     meta_info = []
            #     for d in fs.findall_dirs(abspath):
            #         meta_info.append('dir:{}'.format(d.relpath))
            #     for f in fs.findall_files(abspath):
            #         meta_info.append('file:{}:{}'.format(
            #             f.relpath, os.path.getsize(f.path)
            #         ))
            #     return get_content_hash('\n'.join(meta_info))
            return ''
        
        def generate_utime(abspath: str, scheme: str) -> int:
            if scheme in ('root', 'top', 'top_files', 'top_dirs'):
                return get_updated_time(abspath, recursive=False)
            else:
                return get_updated_time(abspath, recursive=True)
        
        def generate_uid(ftype: str, relpath: str) -> str:
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
            if not fs.exist(abspath):
                raise FileNotFoundError(
                    'please check the path you defined in manifest does exist',
                    path
                )
            # minor fix relpath
            if relpath == '.': relpath = ''
            ftype = 'file' if os.path.isfile(abspath) else 'dir'
            out[relpath] = AssetInfo(
                type=ftype,
                scheme=scheme,
                utime=generate_utime(abspath, ftype),
                hash=generate_hash(abspath, ftype),
                uid=generate_uid(ftype, relpath),
            )
        return out  # noqa
    
    def _update_dependencies(self, deps0: T.Dependencies0) -> T.Dependencies1:
        return resolve_dependencies(deps0, self._start_directory)
    
    @staticmethod
    def _update_launcher(
        launcher0: T.Launcher0, start_directory: T.AbsPath
    ) -> T.Launcher1:
        out: T.Launcher1 = {
            'command'          : '',
            'icon'             : '',
            'show_console'     : True,
            'enable_cli'       : False,
            'add_to_desktop'   : False,
            'add_to_start_menu': False,
        }
        
        if isinstance(launcher0['command'], str):
            out['command'] = launcher0['command']
        else:
            out['command'] = shlex.join(launcher0['command'])
        
        if icon := launcher0.get('icon'):
            if os.path.isabs(icon):
                out['icon'] = fs.normpath(icon)
            else:
                out['icon'] = fs.normpath('{}/{}'.format(start_directory, icon))
            # print(out['icon'], ':v')
        
        for k in (
            'show_console', 'enable_cli', 'add_to_desktop', 'add_to_start_menu'
        ):
            if k in launcher0:
                # noinspection PyTypedDict
                assert isinstance((v := launcher0[k]), bool)
                # noinspection PyTypedDict
                out[k] = v
        
        return out
    
    def _update_readme_file(self, readme: T.AbsPath) -> T.AbsPath:
        if readme:
            if os.path.isabs(readme):
                out = fs.normpath(readme)
            else:
                out = fs.normpath(f'{self._start_directory}/{readme}')
            assert fs.real_exist(out)
            return out
        return ''
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _plainify_assets(assets1: T.Assets1) -> T.Assets0:
        out = {}
        for path, info in assets1.items():
            out[path] = info.scheme
        return out


# -----------------------------------------------------------------------------

# noinspection PyTypeChecker
def _diff_assets(new: T.Assets1, old: T.Assets1) -> T.AssetsDiff:
    """
    ref: docs/devnote/assets-diff-strategy.zh.md
    """
    
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
        if new.type == 'file' and new.hash == old.hash:
            return True
        if new.utime == old.utime:  # FIXME: used for dir only?
            return True
        if new.type == 'dir' and new.hash == old.hash != '':
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


# noinspection PyTypeChecker
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
