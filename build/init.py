"""
see DEVNOTE.md
"""

import os

from argsense import cli
from lk_utils import run_cmd_args, xpath

os.chdir(xpath('..'))
os.environ['DEPSLAND_PYPI_ROOT'] = 'chore/pypi_self'

from depsland import paths
from depsland.pypi.insight import rebuild_index


@cli.cmd()
def download_requirements() -> None:
    """
    prerequisite:
        - `python/python.exe` or `python/bin/python3`. if not exist, see
          `python/README.zh.md`.
    """
    run_cmd_args(
        paths.python.python, '-m', 'pip', 'wheel',
        '-r', 'requirements.lock',
        '--wheel-dir', 'chore/pypi_self/downloads',
        '--no-deps', '--disable-pip-version-check',
        verbose=True
    )


@cli.cmd()
def self_build_pypi_index() -> None:
    assert paths.pypi.root.endswith('chore/pypi_self')
    rebuild_index(perform_pip_install=True)


@cli.cmd()
def make_site_packages(target_dir: str = 'chore/site_packages') -> None:
    run_cmd_args(
        paths.python.python, '-m', 'pip', 'install',
        '-r', 'requirements.lock',
        '-t', target_dir,
        '--find-links', 'chore/pypi_self/downloads',
        '--no-deps', '--no-index', '--disable-pip-version-check',
        verbose=True
    )


if __name__ == '__main__':
    # pox build/init.py download-requirements
    # pox build/init.py self-build-pypi-index
    # pox build/init.py make-site-packages
    cli.run()
