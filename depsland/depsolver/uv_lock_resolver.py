import typing as tp

from lk_utils import fs

from ..normalization import normalize_name
from ..venv.target_venv.indexer import analyze_records
from ..venv.target_venv.indexer import index_all_package_references


class T:
    ExactVersion = str
    PackageName = str

    PackageId1 = str  # format of '{name}-{version}'
    PackageId2 = tp.Tuple[PackageName, ExactVersion]

    PackageInfo = tp.TypedDict(
        'PackageInfo',
        {
            'id': PackageId1,
            'name': PackageName,
            'files': tp.Iterable[str],  # (relative_path, ...)
            'version': ExactVersion,
            # 'dependencies': tp.Sequence[PackageId],
        },
    )
    PyProjData = tp.TypedDict(
        'PyProjData',
        {
            'project': tp.TypedDict(
                'Project',
                {
                    'name': PackageName,
                    'version': ExactVersion,
                    'dependencies': tp.List[str],
                },
            ),
            'dependency-group': tp.TypedDict(
                'DependencyGroup', {'dev': tp.List[str]}, total=False
            ),
        },
        total=False,
    )
    UvLockData = tp.TypedDict(
        'UvLockData',
        {
            'package': tp.TypedDict(
                'Package',
                {
                    'name': PackageName,
                    'version': ExactVersion,
                    'dependencies': tp.List[
                        tp.TypedDict('Dependency', {'name': str})
                    ],
                },
            )
        },
        total=False,
    )

    # Packages = tp.Dict[PackageId, PackageInfo]
    Packages = tp.Dict[PackageName, PackageInfo]


def resolve_uv_lock(pyproj_file: str, uvlock_file: str) -> T.Packages:
    """
    return top packages and their dependencies in tiled format.

    for example:
        if pyproject.toml declares A and dev:B, A depends on C and D; B depends
        on C and E.
        the returned data would be:
            {A: InfoA, C: InfoC, D: InfoD}
                no `B: InfoB` because B is in dev group.
                no `E: InfoE` because E is only dependant by dev:B.

    params:
        pyproj_file: the path to "pyproject.toml".
        uvlock_file: the path to "uv.lock".
    """
    pyproj_data: T.PyProjData = fs.load(pyproj_file, 'toml')
    uvlock_data: T.UvLockData = fs.load(uvlock_file, 'toml')
    venv_dir = '{}/.venv'.format(fs.parent(pyproj_file))
    assert fs.exist('{}/Lib/site-packages'.format(venv_dir)), venv_dir

    pkg_2_ver = {}
    pkg_2_direct_deps = {}
    for item in uvlock_data['package']:
        name = normalize_name(item['name'])
        pkg_2_ver[name] = item['version']
        pkg_2_direct_deps[name] = tuple(
            normalize_name(x['name']) for x in item.get('dependencies', ())
        )

    this_proj_name = pyproj_data['project']['name']
    this_proj_deps = pkg_2_direct_deps[this_proj_name]

    # fmt: off
    _recorded = set()
    def flatten_deps(initial_deps):
        for dep in initial_deps:
            if dep not in _recorded:
                _recorded.add(dep)
                yield dep
                yield from flatten_deps(pkg_2_direct_deps[dep])
    this_proj_deps = sorted(flatten_deps(this_proj_deps))
    # fmt: on

    pkgs_info = {}
    all_pkg_refs = dict(
        index_all_package_references('{}/Lib/site-packages'.format(venv_dir))
    )
    for name in this_proj_deps:
        ver = pkg_2_ver[name]
        record_file = '{}/RECORD'.format(all_pkg_refs[name][1])
        relpaths = tuple(sorted(analyze_records(record_file)))
        info = {
            'id': f'{name}-{ver}',
            'name': name,
            'version': ver,
            'files': relpaths,
        }
        pkgs_info[name] = info
    return pkgs_info
