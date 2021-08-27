import os
from os import listdir

from lk_logger import lk

from .path_struct import VEnvDistStruct, VEnvSourceStruct, src_struct
from .pypi import local_pypi
from .typehint import *
from .utils import mergelinks, mklinks


def create_venv(venv_name: str, requirements: list[TRequirement]):
    try:
        dst_struct = VEnvDistStruct(venv_name)
        _init_venv_dir(src_struct, dst_struct)
        for loc in _install_requirements(requirements):
            lk.loga('add package to venv', os.path.basename(loc))
            try:
                mklinks(loc, dst_struct.site_packages, exist_ok=False)
            except FileExistsError:
                lk.logt('[I1457]', 'merging existed target venv',
                        os.path.basename(loc))
                mergelinks(loc, dst_struct.site_packages,
                           file_exist_handle='keep')
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
    lk.logp(requirements)
    
    pkg_list = []  # list[PackageInfo]
    for req in requirements:
        lk.loga(req)
        pkg_list.append(local_pypi.analyse_requirement(req))
    
    all_pkgs = set()
    for pkg in pkg_list:
        all_pkgs.add(pkg.name_id)
        all_pkgs.update(pkg.dependencies)
    for name_id in all_pkgs:
        for loc in local_pypi.get_locations(name_id):
            yield loc
