from .b2e_a import add_icon_to_exe
# from .b2e_a import bat_2_exe as bat_2_exe_legacy
# from .b2e_b import bat_2_exe
from .shortcut import create_shortcut


def bat_2_exe(
    file_i: str,
    file_o: str = '',
    icon: str = '',
    show_console: bool = True,
    uac_admin: bool = False,
    remove_bat: bool = False,
) -> str:
    if show_console and not uac_admin:
        from .b2e_a import bat_2_exe  # fast but insufficient
    else:
        from .b2e_b import bat_2_exe  # slow but powerful
    return bat_2_exe(file_i, file_o, icon, show_console, uac_admin, remove_bat)
