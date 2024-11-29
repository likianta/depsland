if 1:
    import os
    import sys
    _parent_dir = os.path.abspath(f'{__file__}/../..')
    if sys.base_prefix.startswith(_parent_dir):
        # we are using an exclusive python interpreter vendored by depsland.
        # since the interpreter is clean and no third party packages -
        # installed, we need to locate another place to find the site-packages.
        assert os.path.exists(x := f'{_parent_dir}/chore/site_packages'), \
            'see `DEVNOTE.md : search "make site-packages"` for help.'
        sys.path.append(x)

if 2:
    import lk_logger
    lk_logger.setup(quiet=True, show_funcname=False, show_varnames=True)

from . import api
from . import config
from . import launcher
from . import manifest
from . import paths
from . import utils
from . import venv
from . import verspec
# from . import webui
from .api import init
from .api import install
from .api import publish
from .platform import sysinfo
from .platform.launcher import bat_2_exe
from .platform.launcher import create_launcher
from .pypi import pip
from .pypi import pypi

__version__ = '0.8.3'
__date__ = '2024-11-29'
