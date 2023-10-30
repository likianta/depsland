import typing as t

from .system_info import SYSTEM
from ..manifest import T


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
    if SYSTEM == 'darwin':
        from .darwin import create_launcher
        assert manifest
        return create_launcher(manifest, path_o, icon)
    elif SYSTEM == 'linux':
        from .linux import create_launcher
        assert path_i
        return create_launcher(path_i, path_o)  # TODO
    elif SYSTEM == 'windows':
        from .windows import create_launcher
        assert path_i
        return create_launcher(
            path_i, path_o, icon, show_console, uac_admin, remove_bat
        )
    else:
        raise ValueError(SYSTEM)
