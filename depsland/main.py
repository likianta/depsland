import os

from lk_logger import lk

from .path_model import VEnvDistModel
from .path_model import VEnvSourceModel
from .path_model import src_model
from .pypi import local_pypi
from .setup import setup_embed_python
from .typehint import *
from .utils import mergelinks
from .utils import mklinks


def create_venv(venv_name: str, requirements: List[TRequirement]):
    try:
        dst_model = VEnvDistModel(venv_name)
        _init_venv_dir(src_model, dst_model)
        for loc in _install_requirements(requirements):
            lk.log('add package to venv', os.path.basename(loc))
            try:
                mklinks(loc, dst_model.site_packages, exist_ok=False)
            except FileExistsError:
                lk.logt('[I1457]', 'merging existed target venv',
                        os.path.basename(loc))
                mergelinks(loc, dst_model.site_packages,
                           file_exist_scheme='keep')
    except Exception as e:
        raise e
    finally:
        lk.loga('save updated local pypi indexed data')
        local_pypi.save()
    return dst_model.home


def _init_venv_dir(src_model: VEnvSourceModel,
                   dst_model: VEnvDistModel):
    """
    see `../docs/project-structure.md > chapters:h1:VENV_HOME`
    """
    lk.loga('init venv directory', dst_model.home)
    dst_model.build_dirs()
    
    if not os.path.exists(src_model.python_exe):
        setup_embed_python(src_model.pyversion, src_model.python)
    
    # MARK: 20210915105256
    mklinks(src_model.python, dst_model.home,
            [x for x in os.listdir(src_model.python) if x != 'lib'])
    # mklink(src_model.dlls, dst_model.dlls)
    # mklink(src_model.scripts, dst_model.scripts)
    
    mklinks(src_model.site_packages, dst_model.site_packages,
            src_model.pip_suits)


def _install_requirements(requirements: List[TRequirement]):
    lk.loga('installing requirements', len(requirements))
    lk.logp(requirements)
    
    pkg_list = []  # list[PackageInfo]
    with lk.counting(len(requirements)):
        for req in requirements:
            lk.logax(req)
            pkg_list.append(local_pypi.analyse_requirement(req))
    
    all_pkgs = set()
    for pkg in pkg_list:
        all_pkgs.add(pkg.name_id)
        all_pkgs.update(pkg.dependencies)
    for name_id in all_pkgs:
        for loc in local_pypi.get_locations(name_id):
            yield loc
