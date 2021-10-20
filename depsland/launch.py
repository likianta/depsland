from os.path import exists
from uuid import uuid1

from lk_logger import lk
from lk_utils.read_and_write import load_list
from .data_struct import *
from .main import create_venv as _create_venv
from .typehint import *


def launch(name, requirements: Union[List[str], str], venv_id='',
           pyversion='python39'):
    if not requirements:
        requirements = []
    elif isinstance(requirements, str):
        requirements = [Requirement(name) for name in load_list(requirements)
                        if name and not name.startswith('#')]
    else:
        requirements = list(map(Requirement, requirements))
    
    if pyversion != 'python39':  # re-indexing path models
        from .path_model import assets_model, src_model
        assets_model.indexing_dirs(pyversion)
        assets_model.build_dirs()
        src_model.indexing_dirs(pyversion)
        src_model.build_dirs()
    
    venv_options = VenvOptions(
        name=name,
        venv_id=venv_id or str(uuid1()).replace('-', ''),
        requirements=requirements
    )
    return _launch(venv_options)


def _launch(venv_options: VenvOptions):
    if exists(x := venv_options.venv_path):
        lk.loga('request already satisfied', venv_options.venv_id)
        return x
    
    venv_path = _create_venv(venv_options.venv_name, venv_options.requirements)
    #   assert venv_path == venv_options.venv_path
    lk.loga(f'see generated venv path: {venv_path}')
    return venv_path
