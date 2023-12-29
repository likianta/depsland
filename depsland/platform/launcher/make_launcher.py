import typing as t

from ..system_info import SYSTEM
from ...manifest import T


def make_launcher(
    manifest: T.Manifest,
    path_o: str,
    **kwargs,
) -> t.Optional[str]:
    """
    kwargs:
        for windows:
            debug: bool = False
            keep_bat: bool = False
            uac_admin: bool = False
    """
    
    if SYSTEM == 'darwin':
        # TODO
        # # from .darwin import create_launcher
        # # return create_launcher(manifest, path_o, icon)
        # from .make_app import make_app
        # make_app(manifest, path_o, icon)
        from .make_shell import make_shell
        make_shell(manifest, path_o)
    
    elif SYSTEM == 'linux':
        from .make_shell import make_shell
        make_shell(manifest, path_o)
    
    elif SYSTEM == 'windows':
        from .make_exe import make_exe
        return make_exe(manifest, path_o, **kwargs)
    
    else:
        raise ValueError(SYSTEM)
