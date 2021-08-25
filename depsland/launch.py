from os.path import exists
from uuid import uuid1

from lk_utils.read_and_write import load_list

from .data_struct import *
from .main import create_venv as _create_venv


def launch(name, requirements: list[str], venv_id=''):
    venv_options = VenvOptions(
        name=name,
        venv_id=venv_id or str(uuid1()).replace('-', ''),
        requirements=requirements
    )
    return standard_launch(venv_options)


def standard_launch(venv_options: VenvOptions):
    if exists(x := venv_options.venv_path):
        return x
    
    if isinstance((f := venv_options.requirements), str):
        requirements = [Requirement(name) for name in load_list(f)
                        if name and not name.startswith('#')]
    else:
        requirements = list(map(Requirement, venv_options.requirements))
    
    return _create_venv(venv_options.venv_name, requirements)
    # return venv_options.venv_path
