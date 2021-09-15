from time import time

from lk_logger import lk
from lk_utils import dumps
from lk_utils import find_files
from pkginfo import SDist, Wheel

from depsland.data_struct import Requirement
from depsland.path_model import pypi_model
from depsland.utils import sort_versions, unzip_file


def main(dir_i, dir_o):
    """
    This is a copy of `depsland.pypi.LocalPyPI._refresh_local_repo`.
    """
    pypi_model.indexing_dirs(dir_o)
    pypi_model.build_dirs()
    
    deps = {}
    available_namespace = {}
    
    (
        name_versions,
        locations,
        dependencies,
        updates
    ) = pypi_model.load_indexed_data()
    
    for path in _get_path(dir_i):
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
            unzip_file(path, loc)
        except FileExistsError:
            loc = pypi_model.extraced + '/' + name_id
        finally:
            # noinspection PyUnboundLocalVariable
            locations[name_id].append(loc)
        
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
    
    for data, file in zip(
            (name_versions,
             locations,
             dependencies,
             updates),
            pypi_model.get_indexed_files()
    ):
        dumps(data, file)


def _get_path(dir_i):
    for d in find_files(dir_i, suffix=('.whl', '.tar.gz')):
        yield d
