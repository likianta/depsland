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
def build(directory='.', icon='', gen_exe=True):
    from lk_utils import dumps
    from textwrap import dedent
    command = dedent('''
        @echo off
        set PYTHONPATH={}:{}
        %DEPSLAND%\python\python.exe %*
    ''')
    dumps(command, f'{directory}/launcher.bat')
    if gen_exe:  # TEST: experimental
        import sys
        from lk_utils import xpath
        sys.path.insert(0, xpath('../build', True))
        from bat_2_exe import bat_2_exe  # noqa
        bat_2_exe(f'{directory}/launcher.bat',
                  f'{directory}/launcher.exe', icon)


@cli.cmd()
def upload(manifest='manifest.json'):
    from .api.dev_api import upload
    upload(manifest)


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

if __name__ == '__main__':
    cli.run()
