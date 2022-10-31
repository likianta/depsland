from argsense import CommandLineInterface

from .doctor import rebuild_pypi_index
from .interface.dev_cli import init

cli = CommandLineInterface('depsland')

cli.add_cmd(init)
cli.add_cmd(rebuild_pypi_index, 'rebuild-pypi-index')


@cli.cmd()
def welcome(confirm_close=False):
    from lk_logger.console import console
    from rich.markdown import Markdown
    from textwrap import dedent
    from . import __date__
    from . import __version__
    
    console.print(Markdown(dedent('''
        # Depsland

        Depsland is a python apps manager for non-developer users.
        
        - Version: {}
        - Release date: {}
        - Author: {}
        - Official website: {}
    ''').format(
        __version__,
        __date__,
        'Likianta <likianta@foxmail.com>',
        'https://github.com/likianta/depsland'
    )))
    
    if confirm_close:
        input('press enter to close window...')


@cli.cmd()
def upload(manifest='./manifest.json'):
    from .interface.dev_cli import upload
    upload(manifest)


if __name__ == '__main__':
    cli.run()
