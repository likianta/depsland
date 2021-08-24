from os import path as ospath

from lk_logger import lk
from lk_utils import dumps
from lk_utils.read_and_write import load_list

from .pip import Pip
from .typehint import *
from .utils import mklink, mklinks
from .venv_struct import DestinationPathStruct, SourcePathStruct, path_struct


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
    src_struct = path_struct
    dst_struct = DestinationPathStruct(venv_name)
    
    _init_venv_dir(src_struct, dst_struct)
    
    if not pip:
        pip = Pip(f'{ospath.abspath("../venv/python.exe")} -m pip',
                  src_struct.downloads, quiet=False)
    
    if isinstance(requirements, str):
        f = requirements
        requirements = [name for name in load_list(f)
                        if name and not name.startswith('#')]
    else:
        f = '../cache/requirements.txt'
        dumps(requirements, f)

    if not requirements:
        return

    pip.download_r(f, src_struct.downloads)
    pip.install_r(f, src_struct.site_packages)
    
    all_requirements = set()
    for name in requirements:
        all_requirements.add(name)
        all_requirements.update(pip.show_dependencies(name))
    lk.logp(all_requirements)
    
    locations = set()
    for name in all_requirements:
        locations.update(pip.show_locations(name))
    
    # deploy
    lk.logt('[D2943]', src_struct, dst_struct)
    lk.logp('[D2944]', locations)
    mklinks(src_struct.site_packages, dst_struct.site_packages, locations)


def _init_venv_dir(src_path_mgr: SourcePathStruct,
                   dst_path_mgr: DestinationPathStruct):
    """
    see `../docs/project-structure.md > chapters:h1:VENV_HOME`
    """
    mklinks(src_path_mgr.python, dst_path_mgr.home)
    mklink(src_path_mgr.scripts, dst_path_mgr.scripts)
    mklinks(src_path_mgr.pip_suits, dst_path_mgr.site_packages)
    mklinks(src_path_mgr.tk_suits, dst_path_mgr.home)
