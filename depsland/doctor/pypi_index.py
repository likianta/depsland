import os
import re
import typing as t
from collections import defaultdict

from lk_logger.console import con_print
from lk_utils import dumps
from lk_utils import fs
from rich.table import Table

from .. import normalization as norm
from .. import paths
from ..pip import pip
from ..pypi import T
from ..utils import get_updated_time
from ..utils import verspec


def rebuild_index(perform_pip_install: bool = False) -> None:
    name_2_versions: T.Name2Versions = defaultdict(list)
    name_id_2_paths: T.NameId2Paths = {}
    dependencies: T.Dependencies
    updates: T.Updates = {}
    
    table = MyTable()
    
    def update_name_2_versions() -> None:
        name_2_versions[ver.name].append(ver.version)
    
    def update_name_id_2_paths() -> None:
        name_id = f'{ver.name}-{ver.version}'
        downloaded_path = f.path
        installed_path = '{}/{}/{}'.format(
            paths.pypi.installed, ver.name, ver.version
        )
        name_id_2_paths[name_id] = (
            fs.relpath(downloaded_path, paths.pypi.root),
            fs.relpath(installed_path, paths.pypi.root),
        )
        if not os.path.exists(installed_path) and perform_pip_install:
            fs.make_dirs(installed_path)
            pip.run(
                'install', downloaded_path,
                '--no-deps', '--no-index',
                ('-t', installed_path),
                ('--find-links', paths.pypi.downloads),
            )
    
    def update_updates() -> None:
        name = ver.name
        utime = get_updated_time(f.path)
        if name not in updates:
            updates[name] = utime
        elif utime > updates[name]:
            updates[name] = utime
    
    def update_table() -> None:
        table.update(f.name, ver.name, ver.version)
    
    # -------------------------------------------------------------------------
    
    for f in fs.find_files(paths.pypi.downloads):
        if f.name == '.gitkeep':
            continue
        
        ver = verspec.get_verspec_from_filename(f.name)
        
        update_name_2_versions()
        update_name_id_2_paths()
        update_updates()
        update_table()
    
    # noinspection PyTypeChecker
    for v in name_2_versions.values():
        v.sort(key=lambda x: verspec.semver_parse(x), reverse=True)
        #   make version list sorted in descending order.
    
    # rebuild `dependencies`. this should be called after complete updating
    # `name_id_2_paths`.
    dependencies = _rebuild_dependencies(name_2_versions)
    
    dumps(name_2_versions, paths.pypi.name_2_versions)
    dumps(name_id_2_paths, paths.pypi.name_id_2_paths)
    dumps(dependencies, paths.pypi.dependencies)
    dumps(updates, paths.pypi.updates)
    
    table.render()
    print(':t')


class MyTable:
    
    def __init__(self):
        self.table = Table()
        self.table.add_column('index')
        self.table.add_column('filename')
        self.table.add_column('name', style='green')
        self.table.add_column('version', style='cyan')
        self._table_index = 0
    
    def update(self, filename: str, pakgname: str, version: str) -> None:
        self._table_index += 1
        self.table.add_row(str(self._table_index), filename, pakgname, version)
    
    def render(self) -> None:
        print(':f2')
        con_print(self.table)


# -----------------------------------------------------------------------------

def _rebuild_dependencies(
        name_2_versions: T.Name2Versions,
        recursive=True
) -> T.Dependencies:
    dependencies: T.Dependencies = {}
    root = paths.pypi.installed
    
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
    #   e.g. 'argsense (>=0.4.2,<0.5.0)'
    #       -> ('argsense', '>=0.4.2,<0.5.0')
    
    def walk() -> t.Iterator[str]:
        with open(file) as f:
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
