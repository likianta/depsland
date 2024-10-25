"""
what a "poetry.lock" can provide:
    - the package names and their exact versions
    - filtered markers by 'dry-run' mode
    - the dependencies tree
    - packages with custom urls
references:
    - https://github.com/likianta/poetry-extensions
    - poetry install --dry-run ...
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
    Name2Id = t.Dict[PackageName, PackageId]
    # Name2Version = t.Dict[PackageName, ExactVersion]
    
    # noinspection PyTypedDict
    PackageInfo = t.TypedDict('PackageInfo', {
        'id'          : PackageId,
        'name'        : PackageName,
        'version'     : ExactVersion,
        'dependencies': t.Sequence[PackageId],
        'appendix'    : t.TypedDict('Appendix', {
            'custom_url': str,
        }, total=False)
    })
    
    # Packages = t.Dict[PackageId, PackageInfo]
    Packages = t.Dict[PackageName, PackageInfo]


def resolve_poetry_lock(poetry_lock_file: str) -> T.Packages:
    data = fs.load(poetry_lock_file, 'toml')
    name_2_id = _get_tiled_dict(poetry_lock_file)
    deps_tree = _parse_dependencies_tree(data, name_2_id)
    
    out: T.Packages = {}
    for item in data['package']:
        name = normalize_name(item['name'])
        if name in deps_tree:
            custom_url = None
            if item['source']['type'] == 'legacy':  # TEST
                if item['source']['reference'] == 'likianta-hosted':
                    custom_url = '{}/{}/{}'.format(
                        item['source']['url'],
                        name,
                        item['files'][0]['file']
                    )
            # noinspection PyTypeChecker
            info: T.PackageInfo = {
                'id'          : name_2_id[name],
                'name'        : name,
                'version'     : item['version'],
                'dependencies': deps_tree[name],
                'appendix'    : custom_url and {'custom_url': custom_url} or {}
            }
            out[name] = info
    return out


def _get_tiled_dict(poetry_lock_file: str) -> T.Name2Id:
    resp: str = run_cmd_args(
        (sys.executable, '-m', 'poetry', 'install'),
        ('--no-root', '--dry-run', '--no-ansi'),
        ('-C', fs.parent(poetry_lock_file)),
    )
    ''' examples:
        Installing dependencies from lock file
        
        Package operations: 0 installs, 26 updates, 0 removals, 134 skipped
    
          • Updating pip (23.3.1 -> 23.3.2)
          • Updating textual (0.45.1 -> 0.46.0)
          • Installing charset-normalizer (3.3.2): Skipped for the following \\
        reason: Already installed
          • Downgrading argsense (0.5.6a0 -> 0.5.5)
        ...
    '''
    
    def parsing_lines() -> t.Iterator[t.Tuple[T.PackageName, T.ExactVersion]]:
        pattern = re.compile(
            r' {2}'
            r'• (?:Updating|Installing|Downgrading) '
            r'(.+) \((?:.+ -> )?(.+)\)'
        )
        for line in resp.splitlines()[4:]:
            try:
                assert line.startswith('  • ')
                name, ver = pattern.match(line).groups()
                yield normalize_name(name), ver
            except Exception as e:
                print(line, e, ':lv4')
                exit(1)
    
    return {name: f'{name}-{ver}' for name, ver in parsing_lines()}


def _get_top_packages():
    pass


# noinspection PyPep8Naming
def _parse_dependencies_tree(
    poetry_data: dict, name_2_id: T.Name2Id
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
    
    def shrink_tree(flatten_tree: T1) -> T2:
        out = {}
        for k, v in flatten_tree.items():
            if k not in name_2_id: continue
            out[name_2_id[k]] = tuple(sorted(name_2_id[x] for x in v))
        return out
    
    tree = get_nested_tree()
    tree = flatten_tree(tree)
    tree = shrink_tree(tree)
    return tree
