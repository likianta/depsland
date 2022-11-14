import os
from collections import defaultdict

from lk_logger.console import con_print
from lk_utils import dumps
from lk_utils import fs
from rich.table import Table

from .. import paths
from ..pip import pip
from ..pypi import T
from ..utils import get_updated_time
from ..utils import verspec


def rebuild_index(perform_pip_install: bool = False):
    # dependencies: T.Dependencies = defaultdict(list)
    name_2_versions: T.Name2Versions = defaultdict(list)
    name_id_2_paths: T.NameId2Paths = {}
    updates: T.Updates = {}
    
    table = Table()
    table_index = 0
    table.add_column('index')
    table.add_column('filename')
    table.add_column('name', style='green')
    table.add_column('version', style='cyan')
    
    def update_name_2_versions():
        name_2_versions[ver.name].append(ver.version)
    
    def update_name_id_2_paths():
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
    
    def update_updates():
        name = ver.name
        utime = get_updated_time(f.path)
        if name not in updates:
            updates[name] = utime
        elif utime > updates[name]:
            updates[name] = utime
    
    def update_table():
        nonlocal table_index
        table_index += 1
        table.add_row(str(table_index), f.name, ver.name, ver.version)
    
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
    
    dumps(name_2_versions, paths.pypi.name_2_versions)
    dumps(name_id_2_paths, paths.pypi.name_id_2_paths)
    dumps(updates, paths.pypi.updates)
    
    print(':f2')
    con_print(table)
    print(':t')
