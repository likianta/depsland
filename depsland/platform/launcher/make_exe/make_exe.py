from lk_utils import fs

from ..make_bat import make_bat
from ....manifest import T


def make_exe(
    manifest: T.Manifest,
    file_o: str,
    *,
    # icon: str = '',
    debug: bool = False,
    # show_console: bool = True,
    uac_admin: bool = False,
    keep_bat: bool = False,
    **kwargs
) -> str:
    assert file_o.endswith('.exe')
    file_bat = fs.replace_ext(file_o, 'bat')
    file_exe = file_o
    make_bat(manifest, file_bat, debug=debug, **kwargs)
    bat_2_exe(
        file_bat,
        file_exe,
        icon=(
            (x := manifest['launcher']['icon']) and
            '{}/{}'.format(manifest.start_directory, x) or ''
        ),
        show_console=manifest['launcher']['show_console'] or debug,
        uac_admin=uac_admin,
    )
    if not keep_bat:
        fs.remove_file(file_bat)
    return file_exe


def bat_2_exe(
    file_bat: str,
    file_exe: str,
    icon: str = '',
    show_console: bool = True,
    uac_admin: bool = False,
) -> str:
    if show_console and not uac_admin:
        from .bat_2_exe_1 import bat_2_exe  # fast but insufficient
    else:
        from .bat_2_exe_2 import bat_2_exe  # slow but powerful
    return bat_2_exe(file_bat, file_exe, icon, show_console, uac_admin)
