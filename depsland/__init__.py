if True:
    import lk_logger
    lk_logger.setup(quiet=True, show_varnames=True)

# if True:
#     from .doctor import setup_env
#     setup_env()
#
from . import paths
# from . import setup
# from .launch import launch
# from .main import create_venv
# from .pip import Pip
from .pip import pip
# from .utils import mklink
# from .utils import mklinks

__version__ = '0.0.0'
