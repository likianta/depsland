try:
    from os import path as ospath
    from sys import path as syspath
    
    # add `~/lib/pyportable_runtime` to sys.path
    # tree like:
    #   dist
    #   |= lib  # 2. add this dir to sys.path
    #      |= pyportable_runtime  # 3. then we can use `import pyportable_runtime`
    #   |= src
    #      |= depsland
    #         |- __init__.py  # 1. here we located
    _lib_dir = ospath.abspath(f'{__file__}/../../../lib')
    if ospath.exists(_lib_dir):
        syspath.append(_lib_dir)
finally:
    del ospath, syspath

from . import path_model
from . import setup
from .launch import launch
from .main import create_venv
from .pip import Pip
from .pip import default_pip
from .utils import mklink
from .utils import mklinks

__version__ = '0.2.4'
