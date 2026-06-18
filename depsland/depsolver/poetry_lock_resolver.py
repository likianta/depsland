import re
import sys
import typing as tp
from functools import cache

from lk_utils import fs
from lk_utils import run_cmd_args

from ..normalization import normalize_name
from ..venv.target_venv import get_venv_root
from ..venv.target_venv.indexer import analyze_records
from ..venv.target_venv.indexer import index_all_package_references


class T:
    ExactVersion = str
    PackageId = str  # format of '{name}-{version}'
    PackageName = str

    # DependenciesTree0 = tp.Dict[PackageName, tp.Iterable[PackageName]]
    # DependenciesTree1 = tp.Dict[PackageId, tp.Sequence[PackageId]]
    # DependenciesTree = tp.Dict[PackageId, tp.Sequence[PackageId]]
    # Name2Id = tp.Dict[PackageName, PackageId]
    # Name2Version = tp.Dict[PackageName, ExactVersion]

    PackageInfo = tp.TypedDict(
        'PackageInfo',
        {
            'id': PackageId,
            'name': PackageName,
            # the files will finally be used in `depsland.api.dev_api.publish -
            # ._upload.upload_dependencies_._compress_dependency`
            # 'files'   : tp.TypedDict('Files', {
            #     'root' : str,  # absolute dirpath
            #     'paths': tp.Iterable[str],  # relative filepath
            # }),
            'files': tp.Iterable[str],  # (relative_file_path, ...)
            'version': ExactVersion,
            # 'dependencies': tp.Sequence[PackageId],
            # 'appendix': tp.TypedDict(
            #     'Appendix', {'custom_url': str}, total=False
            # ),
        },
    )

    # Packages = tp.Dict[PackageId, PackageInfo]
    Packages = tp.Dict[PackageName, PackageInfo]


def analyze_dependency_tree(
    poetry_file: str, excluded_project_name: str = ''
) -> tp.Dict[
    T.PackageName,
    tp.Tuple[
        T.ExactVersion, tp.Sequence[tp.Tuple[T.PackageName, T.ExactVersion]]
    ],
]:
    """
    returns: {pkg_name: (version, all_tiled_deps), ...}
        pkg_name: include all names found in `poetry_file`.
        all_tiled_deps: ((dep_name, dep_version), ...)
    """
    poetry_data = fs.load(poetry_file, 'toml')

    all_pkgs = _get_all_packages(poetry_data)
    all_pkgs = _flatten_dependencies(
        {k: tuple(v) for k, v in all_pkgs}, excluded_project_name
    )

    name_2_ver = {
        normalize_name(item['name']): item['version']
        for item in poetry_data['package']
    }

    out = {}
    for k, v in all_pkgs:
        out[k] = (name_2_ver[k], tuple((w, name_2_ver[w]) for w in v))
    return out


def resolve_poetry_lock(pyproj_file: str, poetry_file: str) -> T.Packages:
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
        poetry_file: the path to "poetry.lock".
    """
    pyproj_root = fs.parent(pyproj_file)
    pyproj_data = fs.load(pyproj_file, 'toml')
    poetry_data = fs.load(poetry_file, 'toml')

    all_pkgs = _get_all_packages(poetry_data)
    all_pkgs = _flatten_dependencies(
        {k: tuple(v) for k, v in all_pkgs},
        pyproj_data['project']['name']
        if 'project' in pyproj_data
        else pyproj_data['tool']['poetry']['name'],
    )
    top_names = _get_top_package_names(pyproj_root, pyproj_data)
    top_pkgs = _filter_top_packages(all_pkgs, tuple(top_names))
    tiled_pkgs = _get_tiled_packages(fs.parent(poetry_file))
    top_pkgs = _filter_invalid_markers(top_pkgs, dict(tiled_pkgs))
    tiled_pkgs = _flatten_packages(top_pkgs)
    # breakpoint()

    pkgs_info = _fill_packages_info(pyproj_root, tuple(tiled_pkgs), poetry_data)
    return dict(pkgs_info)


def _get_all_packages(
    poetry_data: dict,
) -> tp.Iterator[tp.Tuple[T.PackageName, tp.Iterable[T.PackageName]]]:
    for item in poetry_data['package']:
        name = normalize_name(item['name'])
        # ver = item['version']
        deps = item.get('dependencies', {})
        yield name, map(normalize_name, deps.keys())


def _flatten_dependencies(
    all_pkgs: tp.Dict[T.PackageName, tp.Tuple[T.PackageName, ...]],
    ignored_current_project_name: str = '',
) -> tp.Iterator[tp.Tuple[T.PackageName, tp.Iterable[T.PackageName]]]:
    def flatten_deps(
        key: str, _recorded: tp.Optional[set] = None
    ) -> tp.Iterator[T.PackageName]:
        if _recorded is None:
            _recorded = set()
        try:
            for dep_name in all_pkgs[key]:
                if dep_name not in _recorded:
                    _recorded.add(dep_name)
                    yield dep_name
                    yield from flatten_deps(dep_name, _recorded)
        except KeyError as e:
            if e.args[0] == ignored_current_project_name:
                print(
                    ':v5',
                    'ignore a key error for "{}" since it is the project '
                    'name'.format(ignored_current_project_name),
                )
            else:
                raise e

    for key in all_pkgs:
        yield key, flatten_deps(key)


def _get_top_package_names(
    working_root: str, pyproj_data: dict
) -> tp.Iterator[T.PackageName]:
    if (
        'group' in pyproj_data['tool']['poetry']
        and 'dev' in pyproj_data['tool']['poetry']['group']
    ):
        dev_deps = frozenset(
            map(
                normalize_name,
                pyproj_data['tool']['poetry']['group']['dev']['dependencies'],
            )
        )
        non_dev_deps = set()
        for dep_name in pyproj_data['tool']['poetry']['dependencies'].keys():
            if dep_name != 'python':
                non_dev_deps.add(normalize_name(dep_name))
        for k, v in pyproj_data['tool']['poetry']['group'].items():
            if k != 'dev':
                non_dev_deps.update(
                    map(normalize_name, v['dependencies'].keys())
                )
        names_in_dev_group_only = dev_deps - non_dev_deps
    else:
        names_in_dev_group_only = frozenset()

    content = _poetry_list(working_root)
    # print(':v', content, content.count('\n'))
    pattern = re.compile(r'^[-\w]+')
    for line in content.splitlines():
        # skip non-leading lines
        if line.startswith((' ', '│', '├', '└')):
            continue
        # print(':vi2', line, bool(pattern.match(line)))
        if m := pattern.match(line):
            top_name = normalize_name(m.group())
            if top_name not in names_in_dev_group_only:
                yield top_name


def _filter_top_packages(
    all_pkgs: tp.Iterator[tp.Tuple[T.PackageName, tp.Iterable[T.PackageName]]],
    top_names: tp.Tuple[T.PackageName, ...],
) -> tp.Iterator[tp.Tuple[T.PackageName, tp.Iterable[T.PackageName]]]:
    for name, deps in all_pkgs:
        if name in top_names:
            yield name, deps


def _get_tiled_packages(
    working_root: str,
) -> tp.Iterator[tp.Tuple[T.PackageName, T.ExactVersion]]:
    content = _poetry_list(working_root)
    pattern = re.compile(r'([^ ]+) +(?:\(!\) )?([^ ]+)')
    for line in content.splitlines():
        # print(':vi2', line)
        name, ver = pattern.match(line).groups()
        name = normalize_name(name)
        yield name, ver


def _filter_invalid_markers(
    top_pkgs: tp.Iterator[tp.Tuple[T.PackageName, tp.Iterable[T.PackageName]]],
    tiled_pkgs: tp.Dict[T.PackageName, T.ExactVersion],
) -> tp.Iterator[tp.Tuple[T.PackageId, tp.Iterable[T.PackageId]]]:
    for top_name, deps in top_pkgs:
        if top_name in tiled_pkgs:
            top_ver = tiled_pkgs[top_name]
            top_id = f'{top_name}-{top_ver}'
            filtered_deps = []
            for dep_name in deps:
                if dep_name in tiled_pkgs:
                    dep_ver = tiled_pkgs[dep_name]
                    dep_id = f'{dep_name}-{dep_ver}'
                    filtered_deps.append(dep_id)
            yield top_id, filtered_deps


def _flatten_packages(
    top_pkgs: tp.Iterator[tp.Tuple[T.PackageId, tp.Iterable[T.PackageId]]],
) -> tp.Set[T.PackageId]:
    out = set()
    for id, deps in top_pkgs:
        out.add(id)
        out.update(deps)
    return out


def _fill_packages_info(
    pyproj_root: str, tiled_pkgs: tp.Tuple[T.PackageId, ...], poetry_data: dict
) -> tp.Iterator[tp.Tuple[T.PackageName, T.PackageInfo]]:
    def get_custom_url() -> tp.Optional[str]:
        if item['source']['type'] == 'legacy':
            # FIXME: the url of likianta source may be a "localhost" path.
            if item['source']['reference'] == 'likianta':
                return '{}/{}/{}'.format(
                    item['source']['url'],
                    name.replace('_', '-'),
                    item['files'][0]['file'],
                )

    lib_root = get_venv_root(pyproj_root)
    all_pkg_refs = dict(index_all_package_references(lib_root))
    print(pyproj_root, lib_root, len(all_pkg_refs), len(tiled_pkgs), ':l')

    for item in poetry_data['package']:
        name = normalize_name(item['name'])
        ver = item['version']
        id = f'{name}-{ver}'
        if id in tiled_pkgs:
            record_file = '{}/RECORD'.format(all_pkg_refs[name][1])
            relpaths = tuple(sorted(analyze_records(record_file)))
            info: T.PackageInfo = {
                'id': id,
                'name': name,
                'version': ver,
                'files': relpaths,
            }
            yield name, info


@cache
def _poetry_list(working_root: str) -> str:  # this is slow (3 ~ 5s)
    return tp.cast(
        str,
        run_cmd_args(
            (
                (sys.executable, '-m', 'poetry'),
                ('show', '--no-ansi'),
                ('--directory', working_root),
            ),
            cwd=working_root,
        ),
    )


# -----------------------------------------------------------------------------
# DELETE


def _filter_dependencies(
    pkgs: tp.Iterator[tp.Tuple[T.PackageName, tp.Iterable[T.PackageName]]],
    tiled_pkgs: dict,
) -> tp.Iterator[tp.Tuple[T.PackageId, tp.Tuple[T.PackageId, ...]]]:
    # print(tiled_pkgs, ':lv')
    # exit(0)

    for top_name, deps in pkgs:
        top_ver = tiled_pkgs[top_name]
        top_id = f'{top_name}-{top_ver}'

        filtered_deps = []
        for dep_name in deps:
            if dep_name in tiled_pkgs:
                dep_ver = tiled_pkgs[dep_name]
                dep_id = f'{dep_name}-{dep_ver}'
                filtered_deps.append(dep_id)

        yield top_id, tuple(sorted(filtered_deps))


def _filter_packages(
    all_pkgs: tp.Iterator[tp.Tuple[T.PackageName, tp.Iterable[T.PackageName]]],
    tiled_pkgs: tp.Dict[T.PackageName, T.ExactVersion],
) -> tp.Iterator[T.PackageId]:
    for name, _ in all_pkgs:
        if name in tiled_pkgs:
            yield f'{name}-{tiled_pkgs[name]}'


# def _flatten_packages(
#     pkgs_dict: tp.Dict[T.PackageId, tp.Tuple[T.PackageId, ...]]
# ) -> tp.Set[T.PackageId]:
#     def recurse(key: T.PackageId) -> tp.Iterator[T.PackageId]:
#         for dep_id in pkgs_dict[key]:
#             if dep_id not in recorded:
#                 recorded.add(dep_id)
#                 yield dep_id
#                 yield from recurse(dep_id)
#
#     recorded = set(pkgs_dict.keys())
#     for key in pkgs_dict.keys():
#         for _ in recurse(key):
#             pass
#     return recorded
