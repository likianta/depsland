if True:
    import lk_logger
    lk_logger.setup(quiet=True, show_varnames=True)

from . import api
from . import config
from . import launcher
from . import paths
from . import utils
from .api import init
from .api import install
from .api import upload
from .pip import Pip
from .pip import pip
from .pypi import pypi

__version__ = '0.1.0a34'
__date__ = '2021-11-02'
