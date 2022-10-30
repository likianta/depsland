from argsense import CommandLineInterface

from .doctor import rebuild_pypi_index
from .interface.dev_cli.cli import init

cli = CommandLineInterface('depsland')

cli.cmd()(init)
cli.cmd('rebuild-pypi-index')(rebuild_pypi_index)

if __name__ == '__main__':
    cli.run()
