if 1:
    import lk_logger
    lk_logger.setup(quiet=True, show_funcname=False, show_varnames=True)
    
# if 2:
#     # check python version, if lower than 3.11, import typing_extensions
#     import sys
#     if sys.version_info < (3, 11):
#         import typing
#         from typing_extensions import Self
#         setattr(typing, 'Self', Self)

from . import api
from . import config
from . import launcher
from . import manifest
from . import paths
from . import utils
from . import venv
from .api import init
from .api import install
from .api import publish
from .pip import pip
from .platform import sysinfo
from .platform.launcher import bat_2_exe
from .platform.launcher import create_launcher
from .pypi import pypi

__version__ = '0.7.0b4'
__date__ = '2024-04-28'
