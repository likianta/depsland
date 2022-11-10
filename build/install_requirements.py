import os

from argsense import cli
from lk_utils import run_cmd_args

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
    run_cmd_args(
        pip, 'install', '-r', 'requirements.txt',
        pip_options, verbose=True
    )
    _install_platform_specific()


@cli.cmd()
def install_one(package: str) -> None:
    run_cmd_args(
        pip, 'install', package,
        pip_options, verbose=True
    )


@cli.cmd('install-extra')
def _install_platform_specific() -> None:
    if _IS_WINDOWS:
        run_cmd_args(
            pip, 'install', 'gen-exe',
            pip_options, '--no-deps', verbose=True
        )


if __name__ == '__main__':
    cli.run()
