import os
import re
import typing as t
from collections import defaultdict

from lk_logger.console import con_print
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads
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
    
    # rebuild `dependencies`. this should be called after complete updating
    # `name_id_2_paths`.
    dependencies = _rebuild_dependencies()
    
    # noinspection PyTypeChecker
    for v in name_2_versions.values():
        v.sort(key=lambda x: verspec.semver_parse(x), reverse=True)
        #   make version list sorted in descending order.
    
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

def _rebuild_dependencies(recursive=True) -> T.Dependencies:
    name_2_versions: T.Name2Versions = loads(paths.pypi.name_2_versions)
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
        def recursively_find_dependencies(
                source_name_id: str,
                current_name_id: str,
                collected: t.Set[T.NameId],
        ) -> t.Set[T.NameId]:
            # nonlocal dependencies
            nid0 = source_name_id
            nid1 = current_name_id
            directs = dependencies[nid0]
            collected.update(directs)
            
            for nid2 in directs:
                indirects = dependencies[nid2]
                for nid3 in indirects:
                    if (
                            (n0 := nid3 == nid0) or
                            (n1 := nid3 == nid1)  # noqa
                    ):
                        raise Exception(
                            'circular dependency: '
                            '[green dim]{}[/] '
                            '-> [green]{}[/] '
                            '-> [yellow]{}[/] '
                            '-> [red u]{}[/] '
                            '-> [red dim]{}[/]'
                            .format(nid0, nid1, nid2, nid3,
                                    nid0 if n0 else nid1)
                        )
                    elif nid3 in directs or nid3 in collected:
                        continue
                    else:
                        collected.add(nid3)
                        recursively_find_dependencies(nid0, nid3, collected)
            
            return collected
        
        old_dependencies = dependencies
        new_dependencies = {}
        for name_id in old_dependencies:
            new_dependencies[name_id] = recursively_find_dependencies(
                name_id, name_id, set()
            )
        print('recursively find dependencies', '{} -> {}'.format(
            len(old_dependencies), len(new_dependencies)
        ))
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
            head1 = 'Requires-Dist: '
            head2 = 'Description-Content-Type: '
            for line in f:
                if line.startswith(head2):
                    break
                if flag == 0:
                    if line.startswith(head1):
                        flag = 1
                    else:
                        continue
                else:
                    if line.startswith(head1):
                        pass
                    else:
                        break
                # assert flag == 1
                yield line[len(head1):]
    
    for line in walk():
        if ';' in line:
            # e.g. 'Requires-Dist: toml; extra == "ext"'
            continue
        raw_name, raw_verspec = pattern.match(line).groups()
        name = norm.normalize_name(raw_name)
        verspecs = norm.normalize_version_spec(
            name, raw_verspec or '')
        proper_version = verspec.find_proper_version(
            *verspecs,
            candidates=name_2_versions.get(name, [])
        )
        if not proper_version:
            raise Exception(file, name, raw_verspec)
        name_id = f'{name}-{proper_version}'
        yield name_id


# noinspection PyUnusedLocal
def _analyse_metadata_2(
        file: str,
        name_2_versions: T.Name2Versions
) -> t.Iterator[T.NameId]:
    """ analyse 'metadata.json' file. """
    raise NotImplementedError
