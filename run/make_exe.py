"""
This script is going to replace a legacy one: sidework/make_launcher.py
"""

from argsense import cli
from depsland.platform.launcher.make_exe import add_icon_to_exe
from lk_utils import fs
from lk_utils import run_cmd_args


@cli
def make_check_updates_exe():
    run_cmd_args(('v', 'check_updates.v'), verbose=True, cwd='build/exe')
    add_icon_to_exe(
        file_exe='build/exe/check_updates.exe', file_ico='build/icon/patch.ico'
    )
    fs.filesize('build/exe/check_updates.exe', str, echo=True)


if __name__ == '__main__':
    # python run/make_exe.py -h
    # python run/make_exe.py make_check_updates_exe
    cli.run()
