import os
from os import listdir

from lk_logger import lk

from .path_struct import VEnvDistStruct, VEnvSourceStruct, src_struct
from .pypi import local_pypi
from .typehint import *
from .utils import mklinks


def create_venv(venv_name: str, requirements: list[TRequirement]):
    try:
        dst_struct = VEnvDistStruct(venv_name)
        _init_venv_dir(src_struct, dst_struct)
        for loc in _install_requirements(requirements):
            lk.loga('add package to venv', os.path.basename(loc))
            mklinks(loc, dst_struct.site_packages)
    except Exception as e:
        raise e
    finally:
        lk.loga('save updated local pypi indexed data')
        local_pypi.save()
    return dst_struct.home


def _init_venv_dir(src_struct: VEnvSourceStruct,
                   dst_struct: VEnvDistStruct):
    """
    see `../docs/project-structure.md > chapters:h1:VENV_HOME`
    """
    lk.loga('init venv directory', dst_struct.home)
    dst_struct.build_dirs()
    
    mklinks(src_struct.python, dst_struct.home,
            [x for x in listdir(src_struct.python) if x != 'lib'])
    # mklink(src_struct.dlls, dst_struct.dlls)
    # mklink(src_struct.scripts, dst_struct.scripts)
    
    mklinks(src_struct.site_packages, dst_struct.site_packages,
            src_struct.pip_suits)


def _install_requirements(requirements: list[TRequirement]):
    lk.loga('installing requirements', len(requirements))
    
    pkg_list = []
    for req in requirements:
        lk.loga(req)
        pkg_list.append(local_pypi.main(req))
    
    for pkg in pkg_list:
        for loc in pkg.locations:
            yield loc
    
    all_deps = set()
    for pkg in pkg_list:
        all_deps.update(pkg.dependencies)
    for dep in all_deps:
        for loc in local_pypi.get_locations(dep):
            yield loc
