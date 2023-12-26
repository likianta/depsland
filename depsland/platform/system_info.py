import platform as _platform
import typing as t

__all__ = [
    'IS_WINDOWS', 'PYVERSION', 'SYSTEM',
    'platform', 'python'
]


class Platform:
    IS_WINDOWS: bool
    MACHINE: t.Literal['arm', 'x64']
    SYSTEM: t.Literal['darwin', 'linux', 'windows']
    
    # noinspection PyTypeChecker
    def __init__(self):
        sysname = _platform.system().lower()
        if sysname in ('darwin', 'linux', 'windows'):
            self.SYSTEM = sysname
        else:
            raise Exception(f'unsupported system: {sysname}')
        
        self.IS_WINDOWS = self.SYSTEM == 'windows'
        
        machine = _platform.machine().lower()
        if machine in ('amd64', 'x86_64'):
            self.MACHINE = 'x64'
        elif machine in ('arm64', 'aarch64'):
            self.MACHINE = 'arm'
        else:
            raise Exception(f'unsupported machine: {machine}')


class Python:
    VERSION: t.Tuple[int, int, int]
    VERSION_STR: str  # always <major>.<minor>
    
    # noinspection PyTypeChecker
    def __init__(self):
        ver = _platform.python_version_tuple()
        self.VERSION = tuple(map(int, ver))
        self.VERSION_STR = '.'.join(ver[:2])


platform = Platform()
python = Python()

# shortcuts
IS_WINDOWS = platform.IS_WINDOWS
SYSTEM = platform.SYSTEM
PYVERSION = python.VERSION
# PYVERSION_ = python.VERSION_STR
