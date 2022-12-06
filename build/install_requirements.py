import os

from argsense import cli
from lk_utils.subproc import compose_cmd
from lk_utils.subproc import run_cmd_args

_IS_WINDOWS = os.name == 'nt'

if _IS_WINDOWS:
    py = 'python/python.exe'
else:
    py = 'python/bin/python3'

pip = (py, '-m', 'pip')
pip_options = (
    '--find-links', 'chore/custom_packages',
    '--disable-pip-version-check', '--no-warn-script-location',
)


@cli.cmd()
def install_all() -> None:
    run_cmd_args(*compose_cmd(
        pip, 'install', '-r', 'requirements.txt', pip_options
    ), verbose=True)


@cli.cmd()
def install_one(package: str) -> None:
    run_cmd_args(*compose_cmd(
        pip, 'install', package, pip_options
    ), verbose=True)


if __name__ == '__main__':
    cli.run()
