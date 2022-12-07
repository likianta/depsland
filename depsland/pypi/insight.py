import os
import re
import typing as t
from collections import defaultdict

from lk_utils import dumps
from lk_utils import fs
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
    
    for f in fs.find_files(pypi_paths.downloads):
        if f.name == '.gitkeep':
            continue
        
        ver = verspec.get_verspec_from_filename(f.name)
        
        update_name_2_versions()
        update_name_id_2_paths()
        update_updates()
    
    # noinspection PyTypeChecker
    for v in name_2_versions.values():
        v.sort(key=lambda x: verspec.semver_parse(x), reverse=True)
        #   make version list sorted in descending order.
    
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
            dependencies[name_id] = []
            
            for d2 in fs.find_dirs(d1.path):
                if d2.name.endswith('.dist-info'):
                    if os.path.exists(x := f'{d2.path}/METADATA'):
                        for required_name_id in _analyse_metadata_1(
                                x, name_2_versions):
                            dependencies[name_id].append(required_name_id)
                    else:
                        raise FileNotFoundError(d2.path)  # TODO: for debug
    
    if recursive:
        def recursively_find_dependencies_2(
                name_id: T.NameId,
                collected: t.Set[T.NameId],
                indent=0,
        ) -> t.Set[T.NameId]:
            for nid in dependencies[name_id]:
                if nid not in collected:
                    print('{}{}'.format(' ' * indent, nid), ':vs')
                    collected.add(nid)
                    recursively_find_dependencies_2(nid, collected, indent + 2)
            return collected
        
        old_dependencies = dependencies
        new_dependencies = {}
        for name_id in old_dependencies:
            new_dependencies[name_id] = \
                recursively_find_dependencies_2(name_id, set())
        print(
            'recursively find dependencies',
            'the flatten dependencies have inflated from {} to {}'.format(
                sum(map(len, old_dependencies.values())),
                sum(map(len, new_dependencies.values())),
            ), ':v2'
        )
        dependencies = new_dependencies
    
    return dependencies


def _analyse_metadata_1(
        file: T.Path,
        name_2_versions: T.Name2Versions
) -> t.Iterator[T.NameId]:
    """ analyse 'METADATA' file. """
    pattern = re.compile(r'([-\w]+)(?: \(([^)]+)\))?')
    
    #                      ^~~~~~~1      ^~~~~~2
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
            print(':v4', file, line)
            raise e
        name = norm.normalize_name(raw_name)
        verspecs = norm.normalize_version_spec(
            name, raw_verspec or '')
        proper_version = verspec.find_proper_version(
            *verspecs,
            candidates=name_2_versions[name]
        )
        if not proper_version:
            print(':v4l', file, name, raw_verspec, name_2_versions.get(name))
            raise Exception()
        name_id = f'{name}-{proper_version}'
        yield name_id


# noinspection PyUnusedLocal
def _analyse_metadata_2(
        file: str,
        name_2_versions: T.Name2Versions
) -> t.Iterator[T.NameId]:
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
