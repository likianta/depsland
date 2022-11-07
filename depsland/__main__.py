import typing as t

from argsense import CommandLineInterface

from . import api
from . import paths
from .manifest import T

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
# ordered by lifecycle

@cli.cmd()
def init():
    api.init()


@cli.cmd()
def build(manifest='manifest.json', icon='', gen_exe=True):
    api.build(_fix_manifest_param(manifest), icon, gen_exe)


@cli.cmd()
def upload(manifest='manifest.json'):
    api.upload(_fix_manifest_param(manifest))


@cli.cmd()
def install(appid: str, upgrade=True, reinstall=False):
    """
    kwargs:
        upgrade (-u):
        reinstall (-r):
    """
    m0, m1 = _get_manifests(appid)
    
    if m0 is None:
        api.install(appid)
    elif _check_version(m1, m0):
        if upgrade:
            api.uninstall(appid, m0['version'])
            api.install(appid)
        else:
            print('new version available but not installed. you can use '
                  '`depsland install -u {appid}` or `depsland upgrade {appid}` '
                  'to get it.'.format(appid=appid))
            return
    else:
        if reinstall:
            # assert m0['version'] == m1['version']
            api.uninstall(appid, m0['version'])
            api.install(appid)
        else:
            print('current version is up to date. you can use `depsland '
                  'install -r {appid}` or `depsland reinstall {appid} to force '
                  'reinstall it.'.format(appid=appid))
            return


@cli.cmd()
def uninstall(appid: str, version: str = None):
    api.uninstall(appid)


@cli.cmd()
def self_upgrade():
    api.self_upgrade()


# -----------------------------------------------------------------------------

@cli.cmd()
def show(appid: str, version: str = None):
    from .manifest import load_manifest
    if version is None:
        history = paths.apps.get_history_versions(appid)
        version = history[0]
    dir_ = '{}/{}/{}'.format(paths.project.apps, appid, version)
    manifest = load_manifest(f'{dir_}/manifest.pkl')
    print(manifest, ':l')


@cli.cmd()
def run(appid: str, version: str, filename: str, error_output='terminal'):
    from lk_utils import loads
    from .launcher import run
    from .paths import project
    file = '{}/{}/{}/{}'.format(project.apps, appid, version, filename)
    run(appid, version, loads(file), error_output)


@cli.cmd()
def rebuild_pypi_index():
    from .doctor import rebuild_pypi_index
    rebuild_pypi_index()


# -----------------------------------------------------------------------------

def _check_version(new: T.Manifest, old: T.Manifest) -> bool:
    from .utils import compare_version
    return compare_version(new['version'], '>', old['version'])


def _fix_manifest_param(manifest: str):
    from os.path import isdir
    if isdir(manifest):
        return f'{manifest}/manifest.json'
    else:
        return manifest


def _get_dir_to_last_installed_version(appid: str) -> t.Optional[str]:
    from lk_utils import loads
    from os.path import exists
    dir_ = '{}/{}'.format(paths.project.apps, appid)
    history_file = paths.apps.get_history_versions(appid)
    if exists(history_file):
        last_ver = loads(history_file)[0]
        out = f'{dir_}/{last_ver}'
        assert exists(out)
        return out
    return None


def _get_manifests(appid: str) -> t.Tuple[t.Optional[T.Manifest], T.Manifest]:
    from .manifest import load_manifest
    from .oss import get_oss_client
    from .utils import make_temp_dir
    
    temp_dir = make_temp_dir()
    
    oss = get_oss_client(appid)
    oss.download(oss.path.manifest, x := f'{temp_dir}/manifest.pkl')
    manifest_new = load_manifest(x)
    
    if x := _get_dir_to_last_installed_version(appid):
        manifest_old = load_manifest(f'{x}/manifest.pkl')
    else:
        manifest_old = None

    return manifest_old, manifest_new


if __name__ == '__main__':
    cli.run()
