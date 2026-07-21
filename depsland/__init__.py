# fmt: off
if 1:
    import os
    import sys
    _projdir = os.path.abspath(f'{__file__}/../../')
    # print(f'{_projdir=}, {sys.base_prefix=}')
    if sys.base_prefix.startswith(_projdir):
        # we are using an exclusive python interpreter vendored by depsland.
        # since the interpreter is clean and no third party packages installed,
        # we need to lookup another place for packages.
        assert os.path.exists(x := f'{_projdir}/chore/minideps'), (
            'see `DEVNOTE.md : search "make site-packages"` for help.'
        )
        sys.path.append(x)

if 2:
    import neoprint as _np
    # print(f'{_np.__path__=}')
    from lk_utils import fs as _fs
    if _fs.exist(f'{_projdir}/.depsland_project.json'):
        if _fs.load(
            f'{_projdir}/.depsland_project.json'
        )['project_mode'] == 'production':
            _np.config(legacy_windows=True)
    _np.setup()
# fmt: on

# ------------------------------------------------------------------------------

from . import api
from . import config
from . import depsolver
from . import launcher
from . import manifest
from . import paths
from . import utils
from . import venv
from . import verspec
from .api import init
from .api import install
from .api import publish
from .manifest import T
from .manifest import dump_manifest
from .manifest import load_manifest
from .platform import sysinfo
from .platform.launcher import bat_2_exe
from .platform.launcher import create_launcher
from .pypi import pip
from .pypi import pypi
from .utils import make_temp_dir

__version__ = '0.12.2a0'
