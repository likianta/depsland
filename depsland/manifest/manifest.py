import os
import typing as t
from collections import namedtuple
from textwrap import dedent
from time import sleep

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

from ..utils import get_content_hash
from ..utils import get_file_hash
from ..utils import get_updated_time

__all__ = [
    'T',
    'change_start_directory',
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
            ('hash', str),  # if type is dir, the hash is empty
            ('uid', str),  # the uid will be used as key to filename in oss.
        ))
    ]
    
    Dependencies0 = t.Dict[str, str]  # dict[name, verspec]
    Dependencies1 = Dependencies0
    
    PyPI0 = t.List[_AnyPath]  # list[anypath_to_python_wheel]
    PyPI1 = t.Dict[str, str]  # dict[filename, abspath]
    
    Launcher0 = t.TypedDict('Launcher0', {
        'script'      : str,
        'icon'        : str,
        #   the origin icon could be: empty, a relpath, or an abspath.
        #   when it is loaded to program, it converts to an abspath.
        #   when it is dumped to a file, it converts to a relpath.
        'cli_tool'    : bool,
        'desktop'     : bool,
        'start_menu'  : bool,
        'show_console': bool,
    })
    Launcher1 = Launcher0
    
    # -------------------------------------------------------------------------
    
    # Manifest0
    #   this is a json-compatible dict. it is either made by user or dumped by
    #   `def dump_manifest` function (when caller passes a '.json' file param
    #   to it).
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
    #   this is main data structure for program to use. it is loaded from a
    #   '.pkl' file, or parsed from a '.json' file (i.e. Manifest0 data).
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
            _RelPath,
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
            'script'      : '',
            'icon'        : '',
            'cli_tool'    : False,
            'desktop'     : True,
            'start_menu'  : False,
            'show_console': True,
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
        if data_o['launcher']['icon']:
            # fix icon path (from relpath to abspath)
            data_o['launcher']['icon'] = fs.normpath(
                '{}/{}'.format(manifest_dir, data_o['launcher']['icon'])
            )
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
        'assets'         : _update_assets(
            data_i.get('assets'), manifest_dir),
        'dependencies'   : _update_dependencies(
            data_i.get('dependencies', {})),
        'pypi'           : _update_pypi(
            data_i.get('pypi', []), manifest_dir),
        'launcher'       : _update_launcher(
            data_i.get('launcher', {}), manifest_dir),
    })
    
    _check_manifest(data_o)
    return data_o


def change_start_directory(manifest: T.Manifest1, new_dir: str) -> None:
    r"""
    if you want to change manifest['start_directory'], you should use this
    function instead of changing it directly.
    
    tip: for IDE refactoring, you can search
    `manifest\w*\['start_directory'\] = ` to find all misused occurrences.
    """
    old_dir = manifest['start_directory']
    manifest['start_directory'] = new_dir
    if manifest['launcher']['icon']:
        manifest['launcher']['icon'] = '{}/{}'.format(
            new_dir, fs.relpath(manifest['launcher']['icon'], old_dir)
        )


def _check_manifest(manifest: T.Manifest1) -> None:
    assert manifest['assets'], 'field `assets` cannot be empty!'
    assert all(not x.startswith('../') for x in manifest['assets']), (
        'manifest should be put at the root of project, and there shall be no '
        '"../" in your assets keys.'
    )
    
    launcher: T.Launcher1 = manifest['launcher']
    
    # check script
    script = launcher['script']
    assert script, 'field `script` cannot be empty!'
    assert not script.startswith('../'), (
        'manifest should be put at the root of project, and there shall be no '
        '"../" in your script path.', script
    )
    script_path = '{}/{}'.format(
        manifest['start_directory'], script.split(' ', 1)[0]
    )
    assert os.path.exists(script_path), (
        'the script is not found, you may check: 1. do not use abspath in '
        'script; 2. the path should exist.'
    )
    assert script_path.endswith('.py') or (
            os.path.isdir(script_path)
            and os.path.exists(f'{script_path}/__init__.py')
    ), (
        'either the script should be a ".py" file, or be a directory that '
        'includes "__init__.py" file.'
    )
    
    # check icon
    icon = launcher['icon']
    if icon:
        assert os.path.isabs(icon)
        
        assert icon.endswith('.ico'), (
            'make sure the icon file is ".ico" format. if you have another '
            'file type, please use a online converter (for example '
            'https://findicons.com/convert) to get one.'
        )
        
        icon_relpath = fs.relpath(icon, manifest['start_directory'])
        try:
            assert icon_relpath.startswith(
                tuple(manifest['assets'].keys())
            )
        except AssertionError:
            if '' in manifest['assets']:
                pass
            else:
                print(dedent('''
                    the launcher icon is not added to your assets list.
                    you may stop current progress right now, and re-check your
                    manifest file.
                    (if you confirm that the icon is added, it may be a bug
                    from depsland.)
                '''), ':v3')
                sleep(1)
        
        # TODO: check icon size and give suggestions (the icon is suggested
        #  128x128 or above.)
    
    if launcher['start_menu']:
        print(':v3', 'start_menu is not tested yet. this is an experimental '
                     'feature.')


def _update_assets(assets0: T.Assets0, manifest_dir: str) -> T.Assets1:
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
            relpath = fs.relpath(path, manifest_dir)
        else:
            abspath = fs.normpath(f'{manifest_dir}/{path}')
            relpath = fs.normpath(path)
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


def _update_launcher(
        launcher0: T.Launcher0,
        start_directory: str
) -> T.Launcher1:
    out = {
        'script'      : '',
        'icon'        : '',
        'cli_tool'    : False,
        'desktop'     : False,
        'start_menu'  : False,
        'show_console': True,
    }
    out.update(launcher0)  # noqa
    if out['icon']:
        if os.path.isabs(out['icon']):
            out['icon'] = fs.normpath(out['icon'])
        else:
            out['icon'] = fs.normpath(f'{start_directory}/{out["icon"]}')
    return out


# -----------------------------------------------------------------------------

def dump_manifest(manifest: T.Manifest1, file_o: T.ManifestFile) -> None:
    manifest_i = manifest
    manifest_o: T.Manifest1 = manifest_i.copy()
    
    if manifest_i['launcher']['icon']:
        manifest_o['launcher'] = manifest_i['launcher'].copy()
        manifest_o['launcher']['icon'] = fs.relpath(
            manifest_o['launcher']['icon'],
            manifest_o['start_directory']
        )
    if file_o.endswith('.json'):
        manifest_o['assets'] = _plainify_assets(manifest_i['assets'])  # noqa
    
    manifest_o['start_directory'] = fs.parent_path(file_o)
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
        'assets'      : _compare_assets(
            new['assets'], old['assets']
        ),
        'dependencies': _compare_dependencies(
            new['dependencies'], old['dependencies']
        ),
        'pypi'        : _compare_pypi(
            new['pypi'], old['pypi']
        ),
    }


def _compare_assets(
        new: T.Assets1, old: T.Assets1
) -> T.AssetsDiff:
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


def _compare_dependencies(
        new: T.Dependencies1, old: T.Dependencies1
) -> T.DependenciesDiff:
    for name0, verspec0 in old.items():
        if name0 not in new:
            yield 'delete', (name0, verspec0)
    for name1, verspec1 in new.items():
        if name1 not in old:
            yield 'append', (name1, verspec1)
            continue
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
