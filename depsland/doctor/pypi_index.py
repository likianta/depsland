import os
from collections import defaultdict

from lk_utils import dumps
from lk_utils import fs

from .. import paths
from ..pypi import T
from ..utils import get_updated_time
from ..utils import verspec


def rebuild_index():
    # dependencies: T.Dependencies = defaultdict(list)
    name_2_versions: T.Name2Versions = defaultdict(list)
    name_id_2_paths: T.NameId2Paths = {}
    updates: T.Updates = {}
    
    def update_name_2_versions():
        name_2_versions[ver.name].append(ver.version)
    
    def update_name_id_2_paths():
        name_id = f'{ver.name}-{ver.version}'
        downloaded_path = f.path
        installed_path = '{}/{}/{}'.format(
            paths.pypi.installed, ver.name, ver.version
        )
        if not os.path.exists(installed_path):
            installed_path = ''
        name_id_2_paths[name_id] = (downloaded_path, installed_path)
    
    def update_updates():
        name = ver.name
        utime = get_updated_time(f.path)
        if name not in updates:
            updates[name] = utime
        elif utime > updates[name]:
            updates[name] = utime
    
    # -------------------------------------------------------------------------
    
    for f in fs.find_files(paths.pypi.downloads):
        if f.name == '.gitkeep':
            continue
        
        print(':i', f.name)
        ver = verspec.get_verspec_from_filename(f.name)
        
        update_name_2_versions()
        update_name_id_2_paths()
        update_updates()
    
    # noinspection PyTypeChecker
    for v in name_2_versions.values():
        v.sort(key=lambda x: verspec.semver_parse(x.version), reverse=True)
        #   make version list sorted in descending order.
    
    dumps(name_2_versions, paths.pypi.name_2_versions)
    dumps(name_id_2_paths, paths.pypi.name_id_2_paths)
    dumps(updates, paths.pypi.updates)
