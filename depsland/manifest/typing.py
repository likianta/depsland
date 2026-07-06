import typing as tp
from types import NoneType

import tree_shaking

from ..depsolver import T as T0


class T(T0):
    AbsPath = RelPath = AnyPath = str
    Appinfo = tp.TypedDict(
        'Appinfo',
        {
            'appid'  : str,
            'name'   : str,
            'version': str,
            'src_dir': str,  # abspath
            'dst_dir': str,  # abspath
            'history': tp.List[str],  # list[str version]
        },
    )
    AssetScheme = tp.Optional[int]  # None | 0b00 | 0b01 | 0b10 | 0b11

    AssetInfo = tp.NamedTuple(
        'AssetInfo',
        (
            ('type', tp.Literal['file', 'dir']),
            # see `depsland.api.dev_api.publish._copy_assets`
            ('scheme', AssetScheme),
            #   AssetScheme: None | 0b00 | 0b01 | 0b10 | 0b11
            ('utime', int),  # updated time
            ('hash', str),  # if type is dir, the hash is empty
            ('uid', str),  # the uid will be used as key to filename in oss.
            # ('redirect', str),
        ),
    )
    StartDirectory = AbsPath

    # --------------------------------------------------------------------------

    Assets0 = tp.List[RelPath]  # all paths relative to `start_directory`
    Assets1 = tp.Dict[RelPath, AssetInfo]
    AssetsRedirection = tp.Dict[RelPath, RelPath]

    Dependencies0 = tp.Optional[
        tp.Union[
            tp.Literal['poetry', 'uv'],
            tp.TypedDict(
                'TreeShakingDependencies',
                {
                    'method': 'tree_shaking',
                    'base': tp.Literal['poetry.lock', 'uv.lock'],
                    'options': tree_shaking.T.Config0,
                },
                total=False,
            ),
        ]
    ]
    Dependencies1 = T0.Packages

    Encryption0 = tp.Optional[
        tp.TypedDict(
            'Encryption0',
            {
                'key': str,
                #   key can be plain string, or literally "$env", or
                #   `$env:<varname>`.
                #   for example:
                #       - 'AjetGCuXouoQJZiZ3faBgGla04j52VzrVAHnf49MbQw'
                #       - '$env'
                #       - '$env:MY_SECRET_KEY'
                'add_salt': bool,
                'packages': tp.List[RelPath],
                'output': RelPath,
            },
        )
    ]
    Encryption1 = tp.TypedDict(
        'Encryption1',
        {'key': str, 'packages': tp.List[RelPath], 'output': RelPath},
    )
    Encryption2 = tp.TypedDict(
        'Encryption2',
        {'key': str, 'packages': tp.Tuple[AbsPath, ...], 'output': AbsPath},
    )

    Experiments0 = tp.TypedDict(
        'Experiments0',
        {'package_provider': tp.Literal['oss', 'pypi']},
        total=False,
    )
    Experiments1 = Experiments0

    Launcher0 = tp.TypedDict(
        'Launcher0',
        {
            'command': tp.Union[str, list],
            'icon': AnyPath,
            'show_console': bool,
            'enable_cli': bool,
            'add_to_desktop': bool,
            'add_to_start_menu': bool,
        },
        total=False,
    )
    Launcher1 = tp.TypedDict(
        'Launcher1',
        {
            'command': str,
            'icon': RelPath,  # relpath or empty
            'show_console': bool,
            'enable_cli': bool,
            'add_to_desktop': bool,
            'add_to_start_menu': bool,
        },
    )
    Launcher2 = Launcher1  # all paths in values turn to absolute.

    # occurrences:
    #   - Manifest._update_readme_file
    #   - /depsland/api/user_api/install.py : _create_launchers
    #   - /depsland/api/dev_api/build_offline.py : _create_launcher
    Readme0 = tp.Union[
        NoneType,
        AnyPath,
        tp.TypedDict(
            'Readme0',
            {'file': AnyPath, 'name': str, 'icon': AnyPath, 'standalone': bool},
            total=False,
        ),
    ]
    Readme1 = tp.TypedDict(
        'Readme1',
        {
            'file': RelPath,  # relpath or empty
            'name': str,  # name without extension, prefer title case.
            'icon': RelPath,  # relpath or empty
            'standalone': bool,  # default true
        },
    )
    Readme2 = Readme1  # all paths in values turn to absolute.

    # --------------------------------------------------------------------------

    # Manifest0: original manifest
    #   this is a json-compatible dict. it is either made by user or dumped by -
    #   `dump_manifest` function (when caller passes a '.json' file param to it).
    Manifest0 = tp.TypedDict(
        'Manifest0',
        # note: not all keys are required, check details in -
        # `Manifest._precheck_manifest`.
        {
            'appid': str,
            'name': str,
            'version': tp.Union[str, tp.Literal['$pyproject_version']],
            'start_directory': AnyPath,
            'readme': Readme0,
            'assets': Assets0,
            'encryption': Encryption0,
            'dependencies': Dependencies0,
            'launcher': Launcher0,
            'experiments': Experiments0,
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
    Manifest1 = tp.TypedDict(
        'Manifest1',
        {
            'appid': str,
            'name': str,
            'version': str,
            'start_directory': StartDirectory,
            'readme': Readme1,
            'assets': Assets1,
            'assets_redirection': AssetsRedirection,
            'encryption': tp.Optional[Encryption1],
            'dependencies': Dependencies1,
            'launcher': Launcher1,
            'experiments': Experiments1,
            'depsland_version': str,
        },
    )

    if tp.TYPE_CHECKING:
        from .manifest import Manifest as ManifestObject
    else:
        ManifestObject = Manifest1

    Manifest = tp.Union[Manifest1, ManifestObject]

    # --------------------------------------------------------------------------

    Action = tp.Literal['append', 'update', 'delete', 'ignore']

    AssetsDiff = tp.Iterator[
        tp.Tuple[
            Action,
            tp.Tuple[RelPath, RelPath],
            #   (relpath, real_relpath)
            #   the `real_relpath` is only valid for `depsland.api.dev_api`.
            tp.Tuple[tp.Optional[AssetInfo], tp.Optional[AssetInfo]],
        ]
    ]

    DependenciesDiff = tp.Iterator[
        tp.Tuple[
            Action,
            T0.PackageName,
            tp.Tuple[tp.Optional[T0.PackageInfo], tp.Optional[T0.PackageInfo]],
        ]
    ]

    # see `depsland.api.dev_api.publish._upload`
    ManifestDiff = tp.TypedDict(
        'ManifestDiff', {'assets': AssetsDiff, 'dependencies': DependenciesDiff}
    )
