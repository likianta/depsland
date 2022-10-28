import os
import shutil

# from .paths import VEnvDistModel
# from .paths import VEnvSourceModel
# from .paths import src_model
from .pypi import pypi
from .setup import setup_embed_python
from .typehint import *
from .utils import mergelinks
from .utils import mklinks


def create_venv(venv_name: str, requirements: List[TRequirement]):
    """
    workflow:
        1. build (virtual) path model
        2. init venv directory
            1. create folder
            2. symlink embedded python interpreter
            3. symlink basically required packages (pip, setuptools, etc.)
        3. install user defined requirements
            1. we will always use cached packages first
            2. if not cached, we will download from pypi to local center
                repository, then symlink to venv
        4. synchronize latest packages info to database
    """
    dst_model = VEnvDistModel(venv_name)
    try:
        _init_venv_dir(src_model, dst_model)
        for loc in _install_requirements(requirements):  # loc: 'location'
            loc_name = os.path.basename(loc)
            print(':s', 'add package to venv', loc_name)
            try:
                mklinks(loc, dst_model.site_packages, force=False)
            except FileExistsError:
                print(':v2', 'merging existed target venv', loc_name)
                mergelinks(loc, dst_model.site_packages)
    except Exception as e:
        if os.path.exists(dst_model.home):
            print(':v3', 'creating venv failed, withdraw target venv',
                  dst_model.home)
            shutil.rmtree(dst_model.home)
        raise e
    finally:
        print('save updated local pypi indexed data')
        pypi.save()
    return dst_model.home


def _init_venv_dir(src_model: VEnvSourceModel,
                   dst_model: VEnvDistModel):
    """
    see `~/docs/project-structure.md : chapters : (h1) VENV_HOME`
    """
    lk.loga('init venv directory', dst_model.home)
    dst_model.build_dirs()
    
    # MARK: 20210915153053
    if not os.path.exists(src_model.python_exe):
        assert not os.path.exists(src_model.python)
        setup_embed_python(src_model.pyversion, src_model.python)
    
    mklinks(src_model.python, dst_model.home,
            [x for x in os.listdir(src_model.python) if x != 'lib'])
    # mklink(src_model.dlls, dst_model.dlls)
    # mklink(src_model.scripts, dst_model.scripts)
    
    mklinks(src_model.site_packages, dst_model.site_packages,
            src_model.pip_suits)


def _install_requirements(requirements: List[TRequirement]):
    print('installing requirements', len(requirements))
    print(':l', requirements)
    
    pkg_list = []  # type: list[TPackageInfo]
    for req in requirements:
        print(':i', req)
        pkg_list.append(pypi.analyse_requirement(req))
    
    all_pkgs = set()
    for pkg in pkg_list:
        all_pkgs.add(pkg.name_id)
        all_pkgs.update(pkg.dependencies)
    for name_id in all_pkgs:
        loc = pypi.get_location(name_id)
        yield loc
