if True:
    import lk_logger
    lk_logger.setup(quiet=True, show_varnames=True)

# if True:
#     from .doctor import setup_env
#     setup_env()

from . import config
from . import paths
# from . import setup
from . import utils
from .interface import dev_cli
from .interface import user_cli
# from .launch import launch
# from .main import create_venv
from .pip import Pip
from .pip import pip
from .pypi import pypi

__version__ = '0.1.0a11'
