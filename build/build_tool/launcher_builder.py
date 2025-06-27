from lk_utils import fs

from depsland.platform.launcher.make_exe \
    import add_icon_to_exe as _add_icon_to_exe
from depsland.platform.launcher.make_exe.bat_2_exe_2 import bat_2_exe as _b2e2


def bat_2_exe(
    file_i: str,
    show_console: bool = True,
    uac_admin: bool = False,
    icon: str = fs.xpath('../icon/launcher.ico'),
) -> None:
    """
    params:
        file_i: the file is ".bat" file, which is under ~/build/exe folder.
        show_console (-c):
        uac_admin (-u):
    """
    # _b2e(
    #     file_bat=file_i,
    #     file_exe=fs.replace_ext(file_i, 'exe'),
    #     icon=icon,
    #     show_console=show_console,
    #     uac_admin=uac_admin,
    # )
    _b2e2(
        file_i=file_i,
        file_o=fs.replace_ext(file_i, 'exe'),
        icon=icon,
        show_console=show_console,
        uac_admin=uac_admin,
    )


def add_icon_to_exe(file_exe, file_ico, file_out: str = None) -> str:
    if file_out is not None:
        fs.copy_file(file_exe, file_out)
    else:
        file_out = file_exe
    _add_icon_to_exe(file_out, file_ico)
    return file_out
