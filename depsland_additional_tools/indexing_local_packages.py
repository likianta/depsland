from time import time

from lk_logger import lk
from lk_utils import find_files
from pkginfo import SDist
from pkginfo import Wheel

from depsland.data_struct import Requirement
from depsland.path_model import pypi_model, pypi_dir
from depsland.utils import sort_versions
from depsland.utils import unzip_file


def main(dir_i, dir_o=pypi_dir):
    """
    This is a copy of `depsland.pypi.LocalPyPI._refresh_local_repo`.
    
    Args:
        dir_i: input any dir that includes downloaded whl files
        dir_o: default is `depsland.path_model.pypi_model.home` (i.e.
            `f'{proj_dir}/pypi'`)
            
    Notes:
        - if dir_o/index has existed pkl file, the new data will be added to
          them.
        - after indexing done, the dir_i is free to delete.
    """
    pypi_model.indexing_dirs(dir_o)
    pypi_model.build_dirs()
    
    deps = {}
    available_namespace = {}
    
    (
        name_versions,
        dependencies,
        updates
    ) = pypi_model.load_indexed_data()
    
    for path in _get_path(dir_i):
        lk.logax(path)
        if path.endswith(('.whl', '.zip')):
            pkg = Wheel(path)
        elif path.endswith(('.tar.gz', '.tar')):
            pkg = SDist(path)
        else:
            raise Exception('This file type is not recognized', path)
        
        req = Requirement(pkg.name, pkg.version)
        name, version, name_id = req.name, req.version, req.name_id
        
        available_namespace[name] = version
        
        updates[name] = int(time())
        
        if version in name_versions[name]:
            continue
        else:
            name_versions[name].append(version)
            sort_versions(name_versions[name])
        
        try:
            loc = pypi_model.mkdir(name_id)
        except FileExistsError:
            pass
        else:
            unzip_file(path, loc)
        
        deps[name_id] = pkg.requires_dist
    
    for name_id, requires_dist in deps.items():
        for raw_name in requires_dist:
            dep = Requirement(raw_name)
            
            if dep.name not in available_namespace:
                lk.loga('ignoring', dep.raw_name)
                continue
            
            version = available_namespace[dep.name]
            dep.set_fixed_version(version)
            dependencies[name_id].append(dep.name_id)
    
    pypi_model.save_indexed_data(name_versions, dependencies, updates)
    lk.logt('[I5533]', 'see (updated) indexed data at: {}'.format(
        pypi_model.index
    ))


def _get_path(dir_i):
    for d in find_files(dir_i, suffix=('.whl', '.tar.gz')):
        yield d