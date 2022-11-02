from argsense import CommandLineInterface

from .api.dev_api import init
from .doctor import rebuild_pypi_index

cli = CommandLineInterface('depsland')


@cli.cmd()
def version():
    from . import __version__, __date__
    print('[cyan b]v{}[/] [dim](released at {})[/]'.format(
        __version__, __date__
    ), ':rs1')


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


# -----------------------------------------------------------------------------

cli.add_cmd(init)


@cli.cmd()
def build(manifest='manifest.json', icon='', gen_exe=True):
    from .api.dev_api import build
    build(_fix_manifest_path(manifest), icon, gen_exe)


@cli.cmd()
def upload(manifest='manifest.json'):
    from .api.dev_api import upload
    upload(_fix_manifest_path(manifest))


@cli.cmd()
def install(appid: str):
    from .api.user_api import install
    install(appid)


@cli.cmd()
def run(appid: str, version: str, filename: str, error_output='terminal'):
    from lk_utils import loads
    from .launcher import run
    from .paths import project
    file = '{}/{}/{}/{}'.format(project.apps, appid, version, filename)
    run(appid, version, loads(file), error_output)


# -----------------------------------------------------------------------------

cli.add_cmd(rebuild_pypi_index, 'rebuild-pypi-index')


def _fix_manifest_path(manifest: str):
    from os.path import isdir
    if isdir(manifest):
        return f'{manifest}/manifest.json'
    else:
        return manifest


if __name__ == '__main__':
    cli.run()
