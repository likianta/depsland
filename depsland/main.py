from os import path as ospath

from lk_logger import lk
from lk_utils import dumps
from lk_utils.read_and_write import load_list

from .manager import DestinationPathManager, SourcePathManager, path_mgr
from .pip import Pip
from .typehint import *
from .utils import mklink, mklinks


def create_venv(
        venv_name: str,
        requirements: Union[TPath, list[TRawName]],
        pip=None
):
    """
    
    Args:
        venv_name: target directory name. for example 'hello_world_venv',
            this will create `{VenvConf.venv_dir}/hello_world_venv` directory.
        requirements: e.g. 'requests', 'pillow', 'numpy', etc.
            note:
                1. the name is case insensitive
        pip: Optional[Pip]
    """
    src_path_mgr = path_mgr
    dst_path_mgr = DestinationPathManager(venv_name)
    
    _init_venv_dir(src_path_mgr, dst_path_mgr)
    
    if not pip:
        pip = Pip(f'{ospath.abspath("../venv/python.exe")} -m pip',
                  src_path_mgr.downloads, quiet=False)
    
    if isinstance(requirements, str):
        f = requirements
        requirements = [name for name in load_list(f)
                        if name and not name.startswith('#')]
    else:
        f = '../cache/requirements.txt'
        dumps(requirements, f)

    if not requirements:
        return

    pip.download_r(f, src_path_mgr.downloads)
    pip.install_r(f, src_path_mgr.site_packages)
    
    all_requirements = set()
    for name in requirements:
        all_requirements.add(name)
        all_requirements.update(pip.show_dependencies(name))
    lk.logp(all_requirements)
    
    locations = set()
    for name in all_requirements:
        locations.update(pip.show_locations(name))
    
    # deploy
    lk.logt('[D2943]', src_path_mgr, dst_path_mgr)
    lk.logp('[D2944]', locations)
    mklinks(src_path_mgr.site_packages, dst_path_mgr.site_packages, locations)


def _init_venv_dir(src_path_mgr: SourcePathManager,
                   dst_path_mgr: DestinationPathManager):
    """
    see `../docs/project-structure.md > chapters:h1:VENV_HOME`
    """
    mklinks(src_path_mgr.bin, dst_path_mgr.home)
    mklink(src_path_mgr.scripts, dst_path_mgr.scripts)
    mklinks(src_path_mgr.pip_suits, dst_path_mgr.site_packages)
    mklinks(src_path_mgr.tk_suits, dst_path_mgr.home)