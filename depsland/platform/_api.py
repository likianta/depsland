import typing as t
from platform import system as _get_system

from ..manifest import T as T0

__all__ = [
    'IS_WINDOWS',
    'PLATFORM',
    'create_launcher',
]


class T:
    Manifest = T0.Manifest
    # use this as standard across the whole project
    Platfrom = t.Literal['darwin', 'linux', 'windows']


def _get_platform() -> T.Platfrom:
    # https://blog.csdn.net/Likianta/article/details/131784141
    x = _get_system()
    if x == 'Darwin':
        return 'darwin'
    elif x == 'Linux':
        return 'linux'
    elif x == 'Windows':
        return 'windows'
    else:  # 'Java' etc.
        raise RuntimeError(f'unsupported platform: {x}')


PLATFORM = _get_platform()
IS_WINDOWS = bool(PLATFORM == 'windows')


# -----------------------------------------------------------------------------


def create_launcher(
    path_i: str = '',
    path_o: str = '',
    icon: str = None,
    # darwin only
    manifest: T.Manifest = None,
    # windows only
    show_console: bool = True,
    uac_admin: bool = False,
    remove_bat: bool = False,
    **_,
) -> t.Union[str, None]:
    if PLATFORM == 'darwin':
        from .darwin import create_launcher
        
        assert manifest
        return create_launcher(manifest, path_o, icon)
    elif PLATFORM == 'linux':
        from .linux import create_launcher
        
        assert path_i
        return create_launcher(path_i, path_o)  # TODO
    else:
        from .windows import create_launcher
        
        assert path_i
        return create_launcher(
            path_i, path_o, icon, show_console, uac_admin, remove_bat
        )
