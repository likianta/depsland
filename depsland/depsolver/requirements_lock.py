"""
reference:
    https://github.com/likianta/poetry-extensions : \
    poetry_extensions/requirements_lock.py
"""
import re
import sys
import typing as t

from lk_utils import fs
from lk_utils import run_cmd_args

from ..normalization import normalize_name


class T:
    ExactVersion = str
    PackageId = str  # str['{name}-{version}']
    PackageName = str
    
    # DependenciesTree0 = t.Dict[PackageName, t.Iterable[PackageName]]
    # DependenciesTree1 = t.Dict[PackageId, t.Sequence[PackageId]]
    DependenciesTree = t.Dict[PackageId, t.Sequence[PackageId]]
    
    # noinspection PyTypedDict
    PackageInfo = t.TypedDict('PackageInfo', {
        'id'      : PackageId,
        'name'    : PackageName,
        'version' : ExactVersion,
        # 'dependencies': t.Sequence[PackageId],
        'appendix': t.Optional[
            t.TypedDict('Appendix', {'custom_url': str}, total=False)
        ]
        # 'appendix': t.TypedDict('Appendix', {'custom_url': str}, total=False)
    })
    
    # Packages = t.Dict[PackageId, PackageInfo]
    Packages = t.Dict[PackageName, PackageInfo]


class _Regex:
    
    @staticmethod
    def simple_extract_name_and_version(
        text: str
    ) -> t.Tuple[T.PackageName, T.ExactVersion]:
        return t.cast(
            t.Tuple[T.PackageName, T.ExactVersion],
            re.match(r'(.+)==(.+)', text).groups()
        )
    
    @staticmethod
    def extract_version_from_url(url: str, name: str) -> str:
        return re.search(
            r'{}-([^-]+)-py3-none-any\.whl'
            .format(normalize_name(name)),
            url
        ).group(1)


_regex = _Regex()


def resolve_requirements_lock(
    pyproj_file: str,  # DELETE: no usage
    poetry_file: str,
    requirements_file: str,
) -> T.Packages:
    """
    `requirements_file` provides a tiled package id list.
    `pyproj_file` helps to filter inexistent packages in above list.
    `poetry_file` provides tree-like relations for dependencies.
    """
    pyproj_data: dict = fs.load(pyproj_file, 'toml')
    poetry_data: dict = fs.load(poetry_file, 'toml')
    reqlock_data: str = fs.load(requirements_file, 'plain')
    
    valid_names = _get_valid_package_names(
        pyproj_data,
        poetry_data,
        reqlock_data,
        fs.parent(poetry_file)
    )
    # print(sorted(valid_names), ':vl')
    
    out = {}
    for line in reqlock_data.splitlines():
        if not line or line.startswith(('# ', '--')):
            continue
        if pkg := _resolve_line(line):
            if (name := pkg['name']) in valid_names:
                out[name] = pkg
            else:
                print(f'drop line in requirements.lock', line, ':vs')
    return out


# noinspection PyPep8Naming
def _get_valid_package_names(
    pyproj_data: dict,  # noqa
    poetry_data: dict,
    reqlock_data: str,
    working_root: str,
) -> t.Set[T.PackageName]:
    class T1:
        # ((str pkg, iter direct_deps), ...)
        A = t.Iterator[t.Tuple[T.PackageName, t.Iterator[T.PackageName]]]
        # {str pkg: tuple direct_deps, ...}
        B = t.Dict[T.PackageName, t.Tuple[T.PackageName, ...]]
        # ((str pkg, iter expanded_deps), ...)
        C = A
        D = t.Iterator[T.PackageName]
    
    def get_all_package_names() -> T1.A:
        for item in poetry_data['package']:
            yield (
                normalize_name(item['name']),
                map(normalize_name, item.get('dependencies', {}).keys())
            )
    
    def expand_dependencies(all_pkgs: T1.B) -> T1.C:
        def recurse(
            key: str, _recorded: set = None
        ) -> t.Iterator[T.PackageName]:
            if _recorded is None:
                _recorded = set()
            for dep_name in all_pkgs[key]:
                if dep_name not in _recorded:
                    _recorded.add(dep_name)
                    yield dep_name
                    yield from recurse(dep_name, _recorded)
        
        for key in all_pkgs:
            yield key, recurse(key)
    
    def filter_packages_1(all_pkgs: T1.C) -> T1.C:
        required_names = tuple(map(
            normalize_name,
            re.findall(r'^(\w[-\w]+)', reqlock_data, re.M)
        ))
        # print(required_names, ':vl')
        for name, deps in all_pkgs:
            if name in required_names:
                yield name, deps
    
    def filter_packages_2(pkgs: T1.C) -> T1.D:
        """ filter invalid markers, i.e. inexistent packages. """
        existent_names = tuple(_get_existent_names())
        # print(existent_names, ':vl')
        for name, deps in pkgs:
            if name in existent_names:
                yield name
                for dep_name in deps:
                    if dep_name in existent_names:
                        yield dep_name
    
    def _get_existent_names() -> T1.D:
        # dev_group_names = tuple(
        #     normalize_name(x)
        #     for x in pyproj_data
        #     ['tool']['poetry']['group']['dev']['dependencies'].keys()
        # )
        content: str = run_cmd_args(
            (sys.executable, '-m', 'poetry'),
            ('show', '--no-ansi'),
            ('--directory', working_root),
        )
        pattern = re.compile(r'[^ ]+')
        for line in content.splitlines():
            # print(':vi2', line)
            name = pattern.match(line).group()
            name = normalize_name(name)
            yield name
    
    pkgs = get_all_package_names()
    pkgs = expand_dependencies({k: tuple(v) for k, v in pkgs})
    pkgs = filter_packages_1(pkgs)
    pkgs = filter_packages_2(pkgs)
    return set(pkgs)


def _resolve_line(line: str) -> T.PackageInfo:
    appendix = {}
    if ' @ ' in line:
        #   e.g. 'lk-logger @ http://likianta.pro:2006/lk-logger/lk_logger \
        #   -5.7.0a10-py3-none-any.whl'
        a, b = line.split(' @ ', 1)
        raw_name, ver = a, _regex.extract_version_from_url(b, a)
        name = normalize_name(raw_name)
        appendix['custom_url'] = b
    elif ' ; ' in line:
        a, b = line.split(' ; ', 1)
        raw_name, ver = _regex.simple_extract_name_and_version(a)
        name = normalize_name(raw_name)
    else:
        raw_name, ver = _regex.simple_extract_name_and_version(line)
        name = normalize_name(raw_name)
    return {
        'id'      : f'{name}-{ver}',
        'name'    : name,
        'version' : ver,
        'appendix': appendix
    }
