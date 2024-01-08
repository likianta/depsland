"""
reference:
    https://github.com/likianta/poetry-extensions : \
    poetry_extensions/requirements_lock.py
"""
import re
import typing as t

from lk_utils import loads

from ..normalization import VersionSpec
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
        'id'          : PackageId,
        'name'        : PackageName,
        'version'     : ExactVersion,
        'dependencies': t.Sequence[PackageId],
        'appendix'    : t.TypedDict('Appendix', {
            'custom_url': str,
            'platform'  : t.Set[str],
            'python'    : t.List[VersionSpec],
        }, total=False)
    })
    
    PoetryLockedData = t.Dict[
        PackageName,
        t.TypedDict('PackageInfo', {
            'version'     : str,
            'source'      : dict,
            'files'       : t.List[dict],
            'dependencies': t.Dict[PackageName, t.Any]
        }, total=False)
    ]
    
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
    req_lock_file: str,
    poetry_lock_file: str,
) -> T.Packages:
    """
    `req_lock_file` provides a tiled package id list.
    `poetry_lock_file` provides tree-like relations of dependencies.
    """
    data0: str = loads(req_lock_file, 'plain')
    data1: dict = loads(poetry_lock_file, 'toml')
    deps_tree = _parse_dependencies_tree(data1, data0)
    deps_tree = _shrink_dependencies_range(deps_tree)
    
    out = {}
    for line in data0.splitlines():
        if not line or line.startswith(('# ', '--')):
            continue
        if pkg := _resolve_line(line, deps_tree):
            # pid = '{}-{}'.format(pkg['name'], pkg['version'])
            out[pkg['name']] = pkg
    return out


# noinspection PyPep8Naming
def _parse_dependencies_tree(
    poetry_data: dict, reqlock_data: str
) -> T.DependenciesTree:
    T0 = t.Dict[T.PackageName, t.Tuple[T.PackageName, ...]]
    T1 = t.Dict[T.PackageName, t.Iterable[T.PackageName]]
    T2 = T.DependenciesTree
    
    def get_nested_tree() -> T0:
        """
        be noticed the result may contain redandunt packages.
        """
        out = {}
        for item in poetry_data['package']:
            name = normalize_name(item['name'])
            if deps := item.get('dependencies'):
                # note: we don't take care of markers in `deps.values()`. this \
                # means some inexistent packages may be included in the result.
                out[name] = tuple(map(normalize_name, deps.keys()))
            else:
                out[name] = ()
        return out
    
    def flatten_tree(nested_tree: T0) -> T1:
        def recurse(
            key: str, _recorded: set = None
        ) -> t.Iterator[T.PackageName]:
            if _recorded is None:
                _recorded = set()
            for dep_name in nested_tree[key]:
                if dep_name not in _recorded:
                    _recorded.add(dep_name)
                    yield dep_name
                    yield from recurse(dep_name, _recorded)
        
        out = {}
        for key in nested_tree.keys():
            out[key] = recurse(key)
        return out
    
    def reformat_tree(flatten_tree: T1) -> T2:
        name_2_id = {}
        for line in reqlock_data.splitlines():
            if not line or line.startswith(('# ', '--')):
                continue
            # print(line, ':vi2')
            # following code is copied from `def _resolve_line`.
            if ' @ ' in line:
                a, b = line.split(' @ ', 1)
                raw_name, ver = a, _regex.extract_version_from_url(b, a)
            elif ' ; ' in line:
                a, b = line.split(' ; ', 1)
                raw_name, ver = _regex.simple_extract_name_and_version(a)
            else:
                raw_name, ver = _regex.simple_extract_name_and_version(line)
            name = normalize_name(raw_name)
            pkg_id = f'{name}-{ver}'
            name_2_id[name] = pkg_id
        # print(name_2_id, ':lv')
        
        # notice: the `flatten_tree` param may contain redandunt packages, we \
        # finally on the basis of `name_2_id` dict.
        out = {}
        for k, v in flatten_tree.items():
            if k not in name_2_id: continue
            out[name_2_id[k]] = tuple(sorted(name_2_id[x] for x in v))
        return out
    
    tree = get_nested_tree()
    tree = flatten_tree(tree)
    tree = reformat_tree(tree)
    return tree


def _resolve_line(
    line: str, deps_tree: T.DependenciesTree
) -> t.Optional[T.PackageInfo]:
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
        # marker: str
        # platforms = set()
        # pyverspecs = []
        # for marker in re.split(r' and | or ', b):
        #     d, e, f = marker.split(' ')
        #     if d == 'python_version':
        #         pyverspecs.append(
        #             VersionSpec(name=name, version=f, comparator=e)
        #         )
        #     elif d == 'sys_platform':
        #         assert e == '=='
        #         assert f in ('darwin', 'linux', 'win32')
        #         platforms.add('windows' if f == 'win32' else f)
        #     elif d == 'os_name':
        #         assert e == '=='
        #         assert f == 'nt'
        #         platforms.add('windows')
        #     else:
        #         raise Exception(line)
        # appendix.update({
        #     'platform'  : platforms,
        #     'python'    : pyverspecs,
        # })
    
    else:
        raw_name, ver = _regex.simple_extract_name_and_version(line)
        name = normalize_name(raw_name)
    
    id = f'{name}-{ver}'
    if id in deps_tree:
        return {
            'id'          : (id := f'{name}-{ver}'),
            'name'        : name,
            'version'     : ver,
            'dependencies': deps_tree[id],
            'appendix'    : appendix
        }
    else:
        print(
            ':r', 'skip inexistent package: '
            '[red]{}[/] [bright_black]({})[/]'.format(id, line)
        )
        return None


_warning_once = 1  # see its only usage.


def _shrink_dependencies_range(
    deps_tree: T.DependenciesTree
) -> T.DependenciesTree:
    """
    make sure `pypi` has indexed all packages from `req_lock_file` - this can \
    be done by `sidework/prepare_packages.py:preindex`.
    since `[func] _parse_dependencies_tree : [func] get_nested_tree` doesn't \
    take care of markers info, here we according to `pypi:index` to trim off \
    inexistent packages.
    """
    from ..pypi import pypi
    global _warning_once
    inexistent_packages = set()
    new_deps_tree: T.DependenciesTree = {}
    for k, v in deps_tree.items():
        if not pypi.exists(k):
            inexistent_packages.add(k)
            continue
        node = new_deps_tree[k] = []
        for x in v:
            if not pypi.exists(x):
                inexistent_packages.add(x)
            else:
                node.append(x)
    if inexistent_packages:
        # about _warning_once:
        #   in publish stage, both new manifest and old manifest file will be \
        #   loaded. the new one goes first, it triggers warning's print; the \
        #   old one although has inexistent packages, too, but it should not \
        #   bother us two times.
        if _warning_once:
            print(
                'there are {} packages were declared in requirements file but '
                'not indexed in `pypi`. it may not be a problem (since the '
                'markers are in chaos). otherwise you can use '
                '`sidework/prepare_packages.py preindex <your_requirements'
                '_lock_file>` to fix this.'
                .format(len(inexistent_packages))
            )
            print({i: n for i, n in enumerate(sorted(inexistent_packages), 1)},
                  ':lvs')
            _warning_once = 0
        else:  # uncomment this to trace who is calling the second time.
            raise Exception
    return new_deps_tree
