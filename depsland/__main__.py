from argsense import cli
from .doctor import rebuild_pypi_index

cli.cmd('rebuild-pypi-index')(rebuild_pypi_index)

if __name__ == '__main__':
    cli.run()
