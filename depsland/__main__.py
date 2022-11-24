import typing as t

from argsense import CommandLineInterface

from . import __path__
from . import __version__
from . import api
from . import paths
from .manifest import T
from .manifest import get_last_installed_version

cli = CommandLineInterface('depsland')
print('depsland [red][dim]v[/]{}[/] [dim]({})[/]'.format(
    __version__, __path__[0]
), ':r')


@cli.cmd()
def version() -> None:
    """
    show basic information about depsland.
    """
    # ref: the rich text (with gradient color) effect is copied from
    #   likianta/lk-logger project.
    from lk_logger.control import _blend_text  # noqa
    from random import choice
    from . import __date__, __path__, __version__
    
    color_pairs_group = (
        ('#0a87ee', '#9294f0'),  # calm blue -> light blue
        ('#2d34f1', '#9294f0'),  # ocean blue -> light blue
        ('#ed3b3b', '#d08bf3'),  # rose red -> violet
        ('#f38cfd', '#d08bf3'),  # light magenta -> violet
        ('#f47fa4', '#f49364'),  # cold sandy -> camel tan
    )
    
    color_pair = choice(color_pairs_group)
    colorful_title = _blend_text(
        '♥ depsland v{} ♥'.format(__version__), color_pair
    )
    print(f'[b]{colorful_title}[/]', ':rs1')
    
    print(':rs1', '[cyan]released at [u]{}[/][/]'.format(__date__))
    print(':rs1', '[magenta]located at [u]{}[/][/]'.format(__path__[0]))


@cli.cmd()
def welcome(confirm_close=False) -> None:
    """
    show welcome message and exit.
    """
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
def init(manifest='.', app_name='', overwrite=False,
         auto_find_requirements=False) -> None:
    """
    create a "manifest.json" file in project directory.
    
    kwargs:
        manifest (-m): if directory of manifest not exists, it will be created.
        appname (-n): if not given, will use directory name as app name.
        auto_find_requirements (-a):
        overwrite (-w):
    """
    api.init(_fix_manifest_param(manifest), app_name, overwrite,
             auto_find_requirements)


@cli.cmd()
def build(manifest='.', gen_exe=True) -> None:
    """
    build your python application based on manifest file.
    the build result is stored in "dist" directory.
    [dim]if "dist" not exists, it will be auto created.[/]
    
    kwargs:
        manifest (-m): a path to the project directory (suggested) or to a -
            mainfest file.
            if project directory is given, will search 'manifest.json' file -
            under this dir.
            [red dim]╰─ if no such file found, will raise a FileNotFound -
            error.[/]
            if a file is given, it must be '.json' type. depsland will treat -
            its folder as the project directory.
            [blue dim]╰─ if a file is given, the file name could be custom. -
            (we suggest using 'manifest.json' as canondical.)[/]
        icon: a '.ico' file (optional), suggest size above 128 * 128.
            if you don't have '.ico' format, please use a convert tool (for -
            example [u i]https://findicons.com/convert[/]) to get it.
    """
    api.build(_fix_manifest_param(manifest), gen_exe)


@cli.cmd()
def publish(manifest='.', full_upload=False) -> None:
    """
    publish dist assets to oss.
    if you configured a local oss server, it will generate assets to -
    `~/oss/apps/<appid>/<version>` directory.
    
    kwargs:
        full_upload (-f): if true, will upload all assets, ignore the files -
            which may already exist in oss (they all will be overwritten).
            this option is useful if you found the oss server not work properly.
    """
    api.publish(_fix_manifest_param(manifest), full_upload)


@cli.cmd()
def install(appid: str, upgrade=True, reinstall=False) -> None:
    """
    install an app from oss by querying appid.
    
    kwargs:
        upgrade (-u):
        reinstall (-r):
    """
    from .manifest import init_manifest
    
    m0, m1 = _get_manifests(appid)
    
    if m0 is None:
        m0 = init_manifest(m1['appid'], m1['name'])
        api.install2(m1, m0)
    elif _check_version(m1, m0):
        if upgrade:
            # install first, then uninstall old.
            api.install2(m1, m0)
            api.uninstall(appid, m0['version'],
                          remove_venv=False, remove_bin=False)
        else:
            print('new version available but not installed. you can use '
                  '`depsland install -u {appid}` or `depsland upgrade {appid}` '
                  'to get it.'.format(appid=appid))
            return
    else:
        if reinstall:
            # assert m0['version'] == m1['version']
            api.uninstall(appid, m0['version'])
            m0 = init_manifest(m1['appid'], m1['name'])
            api.install2(m1, m0)
        else:
            print('current version is up to date. you can use `depsland '
                  'install -r {appid}` or `depsland reinstall {appid} to force '
                  'reinstall it.'.format(appid=appid))
            return


@cli.cmd()
def install_dist(manifest: str) -> None:
    """
    to install a distributed package.
    this function is provided for user that clicks '<some_dist>/setup.exe' to -
    get to work.
    
    TODO: is it better to rename this function to 'setup'?
    """
    from os.path import exists
    from .manifest import change_start_directory
    from .manifest import init_manifest
    from .manifest import init_target_tree
    from .manifest import load_manifest
    
    m1 = load_manifest(_fix_manifest_param(manifest))
    
    if exists(d := '{}/.oss'.format(m1['start_directory'])):
        custom_oss_root = d
    else:
        custom_oss_root = None
    
    init_target_tree(m1, d := '{}/{}/{}'.format(
        paths.project.apps, m1['appid'], m1['version']
    ))
    change_start_directory(m1, d)
    
    appid, name = m1['appid'], m1['name']
    if x := _get_dir_to_last_installed_version(appid):
        m0 = load_manifest(f'{x}/manifest.pkl')
        if _check_version(m1, m0):
            # install first, then uninstall old.
            api.install2(m1, m0, custom_oss_root)
            api.uninstall(appid, m0['version'],
                          remove_venv=False, remove_bin=False)
        else:
            print('you already have the latest version installed: '
                  + m0['version'])
    else:
        m0 = init_manifest(appid, name)
        api.install2(m1, m0, custom_oss_root)
    
    print(':rt', '[green]installation done.[/]')


@cli.cmd()
def upgrade(appid: str) -> None:
    """
    upgrade an app from oss by querying appid.
    """
    m0, m1 = _get_manifests(appid)
    if m0 is None:
        from .manifest import init_manifest
        m0 = init_manifest(m1['appid'], m1['name'])
        api.install2(m1, m0)
    elif _check_version(m1, m0):
        # install first, then uninstall old.
        api.install(appid)
        api.uninstall(appid, m0['version'],
                      remove_venv=False, remove_bin=False)
    else:
        print('[green dim]no update available[/]', ':r')


# @cli.cmd()
# def reinstall(appid: str) -> None:
#     # TODO: reinstall is not supported. the server side provides only latest
#     #     verison. which may not be matched with local one.
#     from .manifest import load_manifest
#     if x := _get_dir_to_last_installed_version(appid):
#         manifest0 = load_manifest(f'{x}/manifest.pkl')
#         api.uninstall(appid, manifest0['version'])
#         api.install(appid, manifest0['version'])


@cli.cmd()
def uninstall(appid: str, version: str = None) -> None:
    """
    uninstall an application.
    """
    if version is None:
        version = get_last_installed_version(appid)
    if version is None:
        print(f'{appid} is already uninstalled.')
        return
    api.uninstall(appid, version)


# @cli.cmd()
# def self_upgrade() -> None:
#     """
#     upgrade depsland itself.
#     """
#     api.self_upgrade()


# -----------------------------------------------------------------------------

@cli.cmd()
def show(appid: str, version: str = None) -> None:
    """
    show manifest of an app.
    """
    from .manifest import load_manifest
    if version is None:
        version = get_last_installed_version(appid)
    assert version is not None
    dir_ = '{}/{}/{}'.format(paths.project.apps, appid, version)
    manifest = load_manifest(f'{dir_}/manifest.pkl')
    print(manifest, ':l')


@cli.cmd()
def view_manifest(manifest: str = '.') -> None:
    from .manifest import load_manifest
    manifest = load_manifest(_fix_manifest_param(manifest))
    print(manifest, ':l')


@cli.cmd(transport_help=True)
def run(appid: str, *args, _version: str = None, **kwargs) -> None:
    """
    a general launcher to start an installed app.
    """
    import sys
    print(sys.argv, ':lv')
    
    version = _version or get_last_installed_version(appid)
    if not version:
        print(':v4', f'cannot find installed version of {appid}')
        return
    
    import lk_logger
    import os
    import subprocess
    from argsense import args_2_cargs
    from .manifest import load_manifest
    from .manifest import parse_script_info
    
    manifest = load_manifest('{}/{}/{}/manifest.pkl'.format(
        paths.project.apps, appid, version
    ))
    assert manifest['version'] == version
    command = parse_script_info(manifest)
    os.environ['DEPSLAND'] = paths.project.root
    os.environ['PYTHONPATH'] = '.;{app_dir};{pkg_dir}'.format(
        app_dir=manifest['start_directory'],
        pkg_dir=paths.apps.get_packages(appid)
    )
    
    # print(':v', args, kwargs)
    lk_logger.unload()
    subprocess.run(
        (*command, *args_2_cargs(*args, **kwargs)),
        cwd=manifest['start_directory']
    )


@cli.cmd()
def rebuild_pypi_index(full: bool = False) -> None:
    """
    rebuild local pypi index. this may resolve some historical problems caused -
    by pip network issues.
    
    kwargs:
        full (-f): if a package is downloaded but not installed, will perform -
            a `pip install` action.
    """
    from .doctor import rebuild_pypi_index
    rebuild_pypi_index(perform_pip_install=full)


# -----------------------------------------------------------------------------

def _check_version(new: T.Manifest, old: T.Manifest) -> bool:
    from .utils import compare_version
    return compare_version(new['version'], '>', old['version'])


def _fix_manifest_param(manifest: str) -> str:  # return a file path to manifest
    from lk_utils.filesniff import normpath
    from os.path import exists, isdir
    if isdir(manifest):
        out = normpath(f'{manifest}/manifest.json', True)
    else:
        out = normpath(manifest, True)
        assert exists(out), f'path not exists: {out}'
    # print(':v', out)
    return out


def _get_dir_to_last_installed_version(appid: str) -> t.Optional[str]:
    from os.path import exists
    if last_ver := get_last_installed_version(appid):
        dir_ = '{}/{}/{}'.format(paths.project.apps, appid, last_ver)
        assert exists(dir_), dir_
        return dir_
    return None


def _get_manifests(appid: str) -> t.Tuple[t.Optional[T.Manifest], T.Manifest]:
    from lk_utils import fs
    from .manifest import change_start_directory
    from .manifest import init_target_tree
    from .manifest import load_manifest
    from .oss import get_oss_client
    from .utils import make_temp_dir
    
    temp_dir = make_temp_dir()
    
    oss = get_oss_client(appid)
    oss.download(oss.path.manifest, x := f'{temp_dir}/manifest.pkl')
    manifest_new = load_manifest(x)
    change_start_directory(manifest_new, '{}/{}/{}'.format(
        paths.project.apps,
        manifest_new['appid'],
        manifest_new['version']
    ))
    init_target_tree(manifest_new)
    fs.move(x, manifest_new['start_directory'] + '/manifest.pkl')
    
    if x := _get_dir_to_last_installed_version(appid):
        manifest_old = load_manifest(f'{x}/manifest.pkl')
    else:
        print('no previous version found, it may be your first time to install '
              f'{appid}')
        print('[dim]be noted the first-time installation may consume a long '
              'time. depsland will try to reduce the consumption in the '
              'succeeding upgrades/installations.[/]', ':r')
        manifest_old = None
    
    return manifest_old, manifest_new


def _run_cli():
    """ this function is for poetry to generate script entry point. """
    cli.run()


if __name__ == '__main__':
    cli.run()
