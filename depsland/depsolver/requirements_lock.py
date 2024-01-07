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
    
    out = {}
    for line in data0.splitlines():
        if not line or line.startswith(('# ', '--')):
            continue
        pkg = _resolve_line(line, deps_tree)
        # pid = '{}-{}'.format(pkg['name'], pkg['version'])
        out[pkg['name']] = pkg
    return out


# DELETE
def _load_poetry_lock_data(file: str) -> T.PoetryLockedData:
    """
    reference:
        https://github.com/likianta/poetry-extensions : \
        poetry_extensions/requirements_lock.py : def _reformat_locked_data
    
    returns:
        {
            name: {
                'version': str,
                'source': dict,
                'files': [dict, ...],
                'dependencies': {name: spec, ...}
            }, ...
        }
    """
    raw_data = loads(file, 'toml')
    out = {}
    all_declared_extras = {}  # {name: container, ...}
    #   `container` is a dict or tuple which implements `__contains__` method.
    
    for item in raw_data['package']:
        name = normalize_name(item['name'])
        out[name] = {
            'version'     : item['version'],
            'source'      : item['source'],
            'files'       : item['files'],
            'dependencies': {
                normalize_name(k): v
                for k, v in item.get('dependencies', {}).items()
            },
        }
        all_declared_extras[name] = item.get('extras', ())
    
    # make clear extras
    for k0, v0 in out.items():
        required_extras = all_declared_extras.get(k0, ())
        deps = v0['dependencies']
        for k1, v1 in tuple(deps.items()):
            if isinstance(v1, dict) and v1.get('optional', False):
                try:
                    assert (m := v1['markers']).startswith('extra ==')
                    ex_name = re.search(r'extra == "(\w+)"', m).group(1)
                    v1.pop('markers')
                    v1['extra'] = ex_name
                    if ex_name not in required_extras:
                        deps.pop(k1)
                except (AssertionError, AttributeError) as e:
                    print(k0, k1, v1)
                    raise e
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


def _resolve_line(line: str, deps_tree: T.DependenciesTree) -> T.PackageInfo:
    if ' @ ' in line:
        #   e.g. 'lk-logger @ http://likianta.pro:2006/lk-logger/lk_logger \
        #   -5.7.0a10-py3-none-any.whl'
        a, b = line.split(' @ ', 1)
        raw_name, ver = a, _regex.extract_version_from_url(b, a)
        name = normalize_name(raw_name)
        return {
            'id'          : (id := f'{name}-{ver}'),
            'name'        : name,
            'version'     : ver,
            'dependencies': deps_tree[id],
            'appendix'    : {
                'custom_url': b,
            }
        }
    
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
        return {
            'id'          : (id := f'{name}-{ver}'),
            'name'        : name,
            'version'     : ver,
            'dependencies': deps_tree[id],
            'appendix'    : {},
            # 'appendix'    : {
            #     'platform'  : platforms,
            #     'python'    : pyverspecs,
            # }
        }
    
    else:
        raw_name, ver = _regex.simple_extract_name_and_version(line)
        name = normalize_name(raw_name)
        return {
            'id'          : (id := f'{name}-{ver}'),
            'name'        : name,
            'version'     : ver,
            'dependencies': deps_tree[id],
            'appendix'    : {},
        }
