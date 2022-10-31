from argsense import CommandLineInterface

from .doctor import rebuild_pypi_index
from .interface.dev_cli import init

cli = CommandLineInterface('depsland')

cli.add_cmd(init)
cli.add_cmd(rebuild_pypi_index, 'rebuild-pypi-index')


@cli.cmd()
def upload(manifest='./manifest.json'):
    from .interface.dev_cli import upload
    upload(manifest)


if __name__ == '__main__':
    cli.run()
