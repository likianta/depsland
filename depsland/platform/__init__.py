"""
platform-specific modules.
the platform names are according to `sys.platform` (darwin, linux, win32).
"""
from . import darwin
from . import linux
from . import windows
from ._api import IS_WINDOWS
from ._api import PLATFORM
from ._api import create_launcher
