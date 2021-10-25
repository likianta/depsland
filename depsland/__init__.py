try:
    from .doctor import setup_env
    
    setup_env()
except Exception as e:
    raise e

from . import path_model
from . import setup
from .launch import launch
from .main import create_venv
from .pip import Pip
from .pip import default_pip
from .utils import mklink
from .utils import mklinks

__version__ = '0.3.2'
