from argsense import cli
from lk_utils import fs

from depsland.platform.launcher.make_exe import bat_2_exe


@cli.cmd()
def main(bat_file: str):
    exe_file = fs.replace_ext(bat_file, 'exe')
    bat_2_exe(
        bat_file,
        exe_file,
        show_console=True,
    )


if __name__ == '__main__':
    # pox sidework/bat_2_exe.py <file>
    cli.run(main)
