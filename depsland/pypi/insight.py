import os
import re
import typing as t
from collections import defaultdict

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads
from lk_utils.read_and_write import ropen

from .pypi import T as T0
from .pypi import pypi
from .. import normalization as norm
from ..paths import pypi as pypi_paths
from ..pip import pip
from ..utils import get_updated_time
from ..utils import verspec


class T(T0):
    PackagesSize = t.NamedTuple('PackagesSize', (
        ('downloaded', t.Dict[str, int]),
        ('installed', t.Dict[str, int]),
    ))


def overview(dir_i: str = None) -> None:
    if dir_i:
        print(loads(f'{dir_i}/name_2_versions.pkl'), ':ls')
        print(loads(f'{dir_i}/name_id_2_paths.pkl'), ':ls')
        print(loads(f'{dir_i}/dependencies.pkl'), ':ls')
        print(loads(f'{dir_i}/updates.pkl'), ':ls')
    else:
        print(pypi.name_2_versions, ':l')
        print(pypi.name_id_2_paths, ':l')
        print(pypi.dependencies, ':l')
        print(pypi.updates, ':l')


def rebuild_index(perform_pip_install: bool = False) -> None:
    name_2_versions: T.Name2Versions = defaultdict(list)
    name_id_2_paths: T.NameId2Paths = {}
    dependencies: T.Dependencies
    updates: T.Updates = {}
    
    def update_name_2_versions() -> None:
        name_2_versions[ver.name].append(ver.version)
    
    def update_name_id_2_paths() -> None:
        name_id = f'{ver.name}-{ver.version}'
        downloaded_path = f.path
        installed_path = '{}/{}/{}'.format(
            pypi_paths.installed, ver.name, ver.version
        )
        name_id_2_paths[name_id] = (
            fs.relpath(downloaded_path, pypi_paths.root),
            fs.relpath(installed_path, pypi_paths.root),
        )
        if not os.path.exists(installed_path) and perform_pip_install:
            fs.make_dirs(installed_path)
            pip.run(
                'install', downloaded_path,
                '--no-deps', '--no-index',
                ('-t', installed_path),
                ('--find-links', pypi_paths.downloads),
            )
    
    def update_updates() -> None:
        name = ver.name
        utime = get_updated_time(f.path)
        if name not in updates:
            updates[name] = utime
        elif utime > updates[name]:
            updates[name] = utime
    
    # -------------------------------------------------------------------------
    
    with pip.multi_processing():
        for f in fs.find_files(pypi_paths.downloads):
            if f.name.startswith('.'):  # '.gitkeep', '.DS_Store', etc.
                continue
            ver = verspec.get_verspec_from_filename(f.name)
            update_name_2_versions()
            update_name_id_2_paths()
            update_updates()
    
    # noinspection PyTypeChecker
    for v in name_2_versions.values():
        v.sort(key=lambda x: verspec.semver_parse(x), reverse=True)
        #   make version list sorted in descending order.
    # print(':l', name_2_versions)
    
    # rebuild `dependencies`. this should be called after complete updating
    # `name_id_2_paths`.
    dependencies = _rebuild_dependencies(name_2_versions)
    
    dumps(name_2_versions, pypi_paths.name_2_versions)
    dumps(name_id_2_paths, pypi_paths.name_id_2_paths)
    dumps(dependencies, pypi_paths.dependencies)
    dumps(updates, pypi_paths.updates)


def _rebuild_dependencies(
    name_2_versions: T.Name2Versions,
    recursive=True
) -> T.Dependencies:
    dependencies: T.Dependencies = {}
    root = pypi_paths.installed
    
    for d0 in fs.find_dirs(root):
        name = d0.name
        
        for d1 in fs.find_dirs(d0.path):
            version = d1.name
            name_id = f'{name}-{version}'
            node = dependencies[name_id] = {'resolved': [], 'unresolved': {}}
            
            for d2 in fs.find_dirs(d1.path):
                if d2.name.endswith('.dist-info'):
                    if os.path.exists(x := f'{d2.path}/METADATA'):
                        for (a, b), is_name_id in analyze_metadata(
                            x, name_2_versions
                        ):
                            if is_name_id:
                                node['resolved'].append(f'{a}-{b}')
                            else:
                                node['unresolved'][a] = tuple(
                                    norm.normalize_version_spec(a, b)
                                )
                    else:
                        raise FileNotFoundError(d2.path)  # TODO: for debug
    
    print(':l', 'origin dependency tree', dependencies)
    
    if recursive:
        def flatten_resolved_dependencies(
            name_id: T.NameId,
            collect: t.Set[T.NameId],
            indent=0,
        ) -> t.Set[T.NameId]:
            print('{}{}'.format(' ' * indent, name_id), ':vs')
            for nid in dependencies[name_id]['resolved']:
                if nid not in collect:
                    collect.add(nid)
                    flatten_resolved_dependencies(nid, collect, indent + 2)
                else:
                    print('{}{}'.format(' ' * (indent + 2), nid), ':vs')
                    if dependencies[nid]['resolved'] \
                        or dependencies[nid]['unresolved']:
                        print('{}...'.format(' ' * (indent + 4)), ':vs')
            return collect
        
        def flatten_unresolved_dependencies(
            name_id: T.NameId,
            collect: t.Dict[T.Name, t.Dict[str, norm.VersionSpec]],
            indent=0,
        ) -> t.Dict[T.Name, T.VersionSpecs]:
            for name, specs in dependencies[name_id]['unresolved'].items():
                if name not in collect:
                    print('{}<{}>'.format(' ' * indent, name), ':vs')
                    collect[name] = {str(x): x for x in specs}
                else:  # merge `specs` into `collect[name]`.
                    for s in specs:
                        if str(s) not in collect[name]:
                            collect[name][str(s)] = s
            for nid in dependencies[name_id]['resolved']:
                flatten_unresolved_dependencies(nid, collect, indent + 2)
            return {k: tuple(v.values()) for k, v in collect.items()}
        
        old_dependencies: T.Dependencies = dependencies
        new_dependencies: T.Dependencies = {}
        for name_id in old_dependencies:
            new_dependencies[name_id] = {
                'resolved'  : flatten_resolved_dependencies(name_id, set()),
                'unresolved': flatten_unresolved_dependencies(name_id, {}),
            }
        print(
            'recursively find dependencies',
            'the flatten dependencies have inflated from {} to {}'.format(
                sum(
                    len(x['resolved']) + len(x['unresolved'])
                    for x in old_dependencies.values()
                ),
                sum(
                    len(x['resolved']) + len(x['unresolved'])
                    for x in new_dependencies.values()
                ),
            ), ':v2'
        )
        dependencies = new_dependencies
    
    return dependencies


def analyze_metadata(
    file: T.Path,
    name_2_versions: dict  # FIXME
) -> t.Iterator[t.Tuple[t.Tuple[str, str], bool]]:
    """
    analyse 'METADATA' file.
    yields: iter[tuple[result, is_resolved]]
        result: tuple[str, str]
            if `is_resolved` is True, result is a `tuple[name, version]`.
            if `is_resolved` is False, result is a `tuple[name, raw_verspec]`.
    """
    pattern = re.compile(r'([-\w]+)(?: \(([^)]+)\))?')
    #                      ~~~~~~~1      ~~~~~~2
    #   e.g. 'argsense (>=0.4.2,<0.5.0)' -> ('argsense', '>=0.4.2,<0.5.0')
    
    def walk() -> t.Iterator[str]:
        with ropen(file) as f:
            flag = 0
            head = 'Requires-Dist: '
            for line in f:
                if not line:
                    break
                if flag == 0:
                    if line.startswith(head):
                        flag = 1
                    else:
                        continue
                else:
                    if not line.startswith(head):
                        break
                # assert flag == 1
                yield line[len(head):]
    
    for line in walk():
        if ';' in line:
            # e.g. 'Requires-Dist: toml; extra == "ext"'
            continue
        try:
            raw_name, raw_verspec = pattern.match(line).groups()
        except AttributeError as e:
            print(':lv4', file, line, e)
            raise e
        name = norm.normalize_name(raw_name)
        verspecs = norm.normalize_version_spec(name, raw_verspec or '')
        proper_version = verspec.find_proper_version(
            *verspecs,
            candidates=name_2_versions[name]
        )
        if proper_version:
            yield (name, proper_version), True
        else:
            print('cannot find a proper version from local index. you may '
                  'download it manually later', file, name, raw_verspec, ':v3')
            yield (name, raw_verspec), False


# noinspection PyUnusedLocal
def analyze_metadata_2(
    file: str,
    name_2_versions: dict  # FIXME
) -> t.Iterator[T.PackageId]:
    """ analyse 'metadata.json' file. """
    raise NotImplementedError


# -----------------------------------------------------------------------------

def measure_package_size(
    name: str,
    version: str = None,
    include_dependencies=True
) -> T.PackagesSize:
    assert name in pypi.name_2_versions
    if version is None:
        version = pypi.name_2_versions[name][0]
    print('measuring package size', name, version)
    
    downloaded_size = 0
    installed_size = 0
    simple_count = 0
    out = T.PackagesSize(downloaded={}, installed={})
    
    calculated = set()
    
    def recurse_measure(name_id: str, indent: int):
        nonlocal downloaded_size, installed_size, simple_count
        
        simple_count += 1
        print('[dim]\\[{:>02d}][/]{}|- [cyan]{}[/]'.format(
            simple_count, '   ' * indent, name_id
        ), ':r')
        if name_id in calculated:
            return
        calculated.add(name_id)
        
        downloaded_path, installed_path = pypi.name_id_2_paths[name_id]
        #   the downloaded_path is a file.
        #   the installed_path is a directory.
        #   both are relative paths. be noted to convert them to absolute.
        
        downloaded_path, installed_path = (
            f'{pypi_paths.root}/{downloaded_path}',
            f'{pypi_paths.root}/{installed_path}'
        )
        
        size1 = _get_file_size(downloaded_path)
        size2 = _get_folder_size(installed_path)
        downloaded_size += size1
        installed_size += size2
        out.downloaded[name_id] = size1
        out.installed[name_id] = size2
        
        if include_dependencies:
            for nid in pypi.dependencies[name_id]:
                recurse_measure(nid, indent + 1)
    
    recurse_measure(f'{name}-{version}', 0)
    
    print('downloaded size:', _pretty_size(downloaded_size), ':v2')
    print('installed size:', _pretty_size(installed_size), ':v2')
    return out


def _get_file_size(file: str) -> int:
    return os.path.getsize(file)


def _get_folder_size(folder: str) -> int:
    return sum(os.path.getsize(x) for x in fs.findall_file_paths(folder))


def _pretty_size(size: int) -> str:
    if size < 1024:
        return f'{size}B'
    elif size < 1024 ** 2:
        return f'{size / 1024:.2f}KB'
    elif size < 1024 ** 3:
        return f'{size / 1024 ** 2:.2f}MB'
    else:
        return f'{size / 1024 ** 3:.2f}GB'
