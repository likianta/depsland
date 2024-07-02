import os

from argsense import cli

from depsland import paths
from depsland.pypi.insight import rebuild_index

print(os.getenv('DEPSLAND_PYPI_ROOT'))
print(paths.pypi.root)


@cli.cmd()
def rebuild_pypi_index(perform_pip_install: bool = True) -> None:
    rebuild_index(perform_pip_install=perform_pip_install)


if __name__ == '__main__':
    # pox sidework/doctor/pypi.py rebuild-pypi-index
    cli.run()
