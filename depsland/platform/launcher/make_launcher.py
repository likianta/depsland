from ..system_info import IS_WINDOWS
from ..system_info import SYSTEM
from ...manifest import T


def make_launcher(
    manifest: T.Manifest,
    dir_o: str,
    name: str = None,
    target_platform: str = SYSTEM,
    **kwargs,
) -> str:
    """
    kwargs:
        for windows:
            debug: bool = False
            keep_bat: bool = False
            uac_admin: bool = False
    """
    path_o = '{dir}/{name}'.format(
        dir=dir_o,
        name=name or '{}.{}'.format(
            IS_WINDOWS and manifest['name'] or manifest['appid'],
            IS_WINDOWS and 'exe' or 'sh'
        )
    )
    
    if target_platform == 'darwin':
        # TODO
        # # from .darwin import create_launcher
        # # return create_launcher(manifest, path_o, icon)
        # from .make_app import make_app
        # make_app(manifest, path_o, icon)
        from .make_shell import make_shell
        make_shell(manifest, path_o)
    
    elif target_platform == 'linux':
        from .make_shell import make_shell
        make_shell(manifest, path_o)
    
    elif target_platform == 'windows':
        from .make_exe import make_exe
        make_exe(manifest, path_o, **kwargs)
    
    else:
        raise ValueError(target_platform)
    
    return path_o
