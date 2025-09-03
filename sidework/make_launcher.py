from argsense import cli
from depsland.platform.launcher.make_exe import add_icon_to_exe as _i2e
from depsland.platform.launcher.make_exe.bat_2_exe_2 import bat_2_exe as _b2e
from lk_utils import fs


@cli
def bat_2_exe(
    file_i: str,
    show_console: bool = True,
    uac_admin: bool = False,
    icon: str = 'icon/launcher.ico',
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
    _b2e(
        file_i=file_i,
        file_o=fs.replace_ext(file_i, 'exe'),
        icon=icon,
        show_console=show_console,
        uac_admin=uac_admin,
    )


@cli
def add_icon_to_exe(file_exe: str, file_ico: str, file_out: str = None) -> str:
    if file_out is not None:
        fs.copy_file(file_exe, file_out)
    else:
        file_out = file_exe
    _i2e(file_out, file_ico)
    return file_out


@cli
def rebuild_all_executebles(switches: str = '111111') -> None:
    assert len(switches) == 6
    iter_ = iter(switches)
    if next(iter_) == '1':
        bat_2_exe(
            'build/exe/depsland-cli.bat',
            show_console=True,
            uac_admin=False
        )
    if next(iter_) == '1':
        bat_2_exe(
            'build/exe/depsland-gui.bat',
            show_console=False,
            uac_admin=False
        )
    if next(iter_) == '1':
        bat_2_exe(
            'build/exe/depsland-gui-debug.bat',
            show_console=True,
            uac_admin=True
        )
    if next(iter_) == '1':
        bat_2_exe(
            'build/exe/depsland-runapp.bat',
            show_console=False,
            uac_admin=False,
            icon='build/icon/python.ico'
        )
    if next(iter_) == '1':
        bat_2_exe(
            'build/exe/depsland-runapp-console.bat',
            show_console=True,
            uac_admin=False,
            icon='build/icon/python.ico'
        )
    if next(iter_) == '1':
        bat_2_exe(
            'build/exe/depsland-runapp-debug.bat',
            show_console=True,
            uac_admin=True,
            icon='build/icon/python.ico'
        )


if __name__ == '__main__':
    # pox sidework/make_launcher.py -h
    cli.run()
