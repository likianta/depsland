from argsense import cli
from depsland.platform.launcher import bat_2_exe
from lk_utils import dedent
from lk_utils import fs


@cli
def generate_patch_exe(file_o: str = '') -> None:
    file_bat = fs.here('_request_patch.bat')
    file_exe = file_o or fs.here('_request_patch.exe')

    fs.dump(
        dedent(
            """
            cd /d %~dp0
            cd source
            set "PYTHONUTF8=1"
            ..\\python\\python.exe -m depsland_updater request_patch
            pause
            """
        ),
        file_bat,
    )
    bat_2_exe(
        file_bat, file_exe, icon='build/icon/patch.ico', show_console=True
    )


if __name__ == '__main__':
    cli.run()
