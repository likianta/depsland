if 1:
    if not __package__:  # noqa
        __package__ = 'depsland'
if 2:
    import os
    import sys
    if sys.orig_argv[0].endswith('.exe'):
        os.environ['LK_LOGGER_MODERN_WINDOW'] = '0'

import os
import sys
import typing as t
from os.path import exists

import pyapp_window
from argsense import CommandLineInterface
from lk_utils import fs
from lk_utils import run_cmd_args

from . import __path__
from . import __version__
from . import api
from . import paths
from .manifest import T
from .manifest import get_last_installed_version
from .normalization import check_name_normalized
from .depsolver import resolve_dependencies

# fix sys.argv
if len(sys.argv) > 1 and sys.argv[1].endswith('.exe'):
    # e.g. ['E:\depsland_app\depsland\__main__.py',
    #       'E:\depsland_app\depsland.exe', ...]
    sys.argv.pop(1)

cli = CommandLineInterface('depsland')
print(
    'depsland [red][dim]v[/]{}[/] [dim]({})[/]'
    .format(__version__, __path__[0]), ':r'
)


@cli.cmd()
def about() -> None:
    """
    show basic information about depsland.
    """
    # ref: the rich text (with gradient color) effect is copied from
    #   likianta/lk-logger project.
    from random import choice
    
    from lk_logger.control import _blend_text  # noqa
    
    from . import __date__
    from . import __path__
    from . import __version__
    
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
def self_location() -> None:
    print('[green b u]{}[/]'.format(fs.xpath('.', True)), ':s1r')


@cli.cmd()
def welcome(confirm_close: bool = False) -> None:
    """
    show welcome message and exit.
    """
    from rich.markdown import Markdown
    from textwrap import dedent
    from . import __date__
    from . import __version__
    
    print(
        ':r1',
        Markdown(
            dedent('''
            # DEPSLAND
            
            Depsland is a python apps manager for non-developer users.
            
            - Version: {}
            - Release date: {}
            - Author: {}
            - Official site: {}
            ''').format(
                __version__,
                __date__,
                'Likianta (likianta@foxmail.com)',
                'https://github.com/likianta/depsland',
            )
        ),
    )
    
    if confirm_close:
        input('press enter to close window...')


@cli.cmd()
def launch_gui(
    port: int = 2028,
    _app_token: str = None,
    _run_at_once: t.Optional[bool] = False,
    _native_window: bool = True,
    _user_call: bool = True,
) -> None:
    """
    launch depsland gui.
    
    kwargs:
        _app_token: an appid or a path to a manifest file.
            if given, the app will launch and instantly install it.
        _run_at_once:
            for `true` example, see `./api/dev_api/publish.py : main() : -
            \\[var] command`
            for `false` example, see `./api/dev_api/offline_build.py : -
            _create_updator()`
    """
    # print(_user_call, sys.argv, ':lv')
    if _user_call:
        run_cmd_args(
            (
                sys.executable, '-m', 'streamlit', 'run',
                'depsland/__main__.py',
            ),
            (
                '--browser.gatherUsageStats', 'false',
                '--global.developmentMode', 'false',
                '--server.headless', 'true',
                '--server.port', port,
            ),
            (
                '--',
                'launch-gui',
                port,
                _app_token or ':empty',
                ':true' if _run_at_once else ':false',
                '--not-user-call',
            ),
            blocking=not _native_window,
            verbose=True,
            force_term_color=True,
        )
        if _native_window:
            pyapp_window.open_window(
                title='Depsland Appstore',
                url='http://localhost:{}'.format(port),
                size=(1200, 2000),
                icon=paths.build.launcher_icon,
                blocking=True,
            )
    else:
        if _app_token == '""':  # FIXME: should be resolved in argsense library.
            _app_token = ''
        if _app_token and os.path.isfile(_app_token):
            _app_token = fs.abspath(_app_token)
            if _run_at_once is None:
                _run_at_once = True
        from .webui import setup_ui
        setup_ui(_app_token, _run_at_once)
    
    # -------------------------------------------------------------------------
    
    # try:
    #     os.environ['QT_API'] = 'pyside6_lite'
    #     import pyside6_lite  # noqa
    # except ModuleNotFoundError:
    #     print(
    #         'launching GUI failed. you may forget to install qt for python '
    #         'library (suggest `pip install pyside6` etc.)',
    #         ':v4',
    #     )
    #     return
    #
    # if sysinfo.IS_WINDOWS:
    #     _toast_notification('Depsland is launching')
    #
    # if _app_token and os.path.isfile(_app_token):
    #     _app_token = fs.abspath(_app_token)
    # # if _run_at_once is None:
    # #     _run_at_once = bool(_app_token)
    #
    # from .ui import launch_app
    # launch_app(_app_token, _run_at_once)


# -----------------------------------------------------------------------------
# ordered by lifecycle


@cli.cmd()
def init(target: str = '.', app_name: str = '') -> None:
    """
    create a "manifest.json" file in project directory.
    
    kwargs:
        target (-t): a directory or file path to generate manifest file at.
            if a directory is given, will create a "manifest.json" file under -
            this directory.
            if a file is given, make sure it's a '.json' file and should not -
            exist (otherwise it will be overwritten).
        app_name (-n): if not given, will use directory name as app name.
    """
    manifest_file = _get_manifest_path(target, ensure_exists=False)
    api.init(manifest_file, app_name)


@cli.cmd()
def build(
    manifest: str = '.',
    offline: bool = False,
    # gen_exe: bool = True,
    # target_system: str = sysinfo.SYSTEM,
) -> None:
    """
    build your python application based on manifest file.
    the build result is stored in "dist" directory.
    [dim i](if "dist" not exists, it will be auto created.)[/]
    
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
    """
    if offline:
        api.build_offline(_get_manifest_path(manifest))
    else:
        api.build(_get_manifest_path(manifest))


@cli.cmd()
def publish(
    target: str = '.',
    full_upload: bool = False,
    upload_dependencies: bool = False,
) -> None:
    """
    publish dist assets to oss.
    if you configured a local oss server, it will generate assets to -
    `~/oss/apps/<appid>/<version>` directory.
    
    kwargs:
        target (-t):
        full_upload (-f): if true, will upload all assets, ignore the files -
            which may already exist in oss (they all will be overwritten).
            this option is useful if you found the oss server not work properly.
        upload_dependencies (-d):
    """
    api.publish(_get_manifest_path(target), full_upload, upload_dependencies)


@cli.cmd()
def install(appid: str, upgrade: bool = True, reinstall: bool = False) -> None:
    """
    install an app from oss by querying appid.
    
    kwargs:
        upgrade (-u):
        reinstall (-r):
    """
    assert check_name_normalized(appid)
    api.install_by_appid(appid, upgrade, reinstall)


@cli.cmd()
def upgrade(appid: str) -> None:
    """
    upgrade an app from oss by querying appid.
    """
    api.install_by_appid(appid, upgrade=True, reinstall=False)


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
def show_packages(poetry_file: str, save_result: str = None) -> None:
    pkgs = resolve_dependencies('poetry.lock', fs.parent(poetry_file))
    rows = [('index', 'name', 'version', 'files count')]
    indx = 0
    for name, info in pkgs.items():
        indx += 1
        rows.append((indx, name, info['version'], len(info['files'])))
    print(rows, ':r2')
    if save_result:
        fs.dump(pkgs, save_result)


@cli.cmd()
def view_manifest(manifest: str = '.') -> None:
    from .manifest import load_manifest
    manifest = load_manifest(_get_manifest_path(manifest))
    print(manifest, ':l')


cli.add_cmd(api.user_api.run_app, 'run', transport_help=True)

# -----------------------------------------------------------------------------


@cli.cmd()
def get_package_size(
    name: str, version: str = None, include_dependencies: bool = False
) -> None:
    """
    kwargs:
        include_dependencies (-d):
    """
    from .pypi import insight
    insight.measure_package_size(name, version, include_dependencies)


# -----------------------------------------------------------------------------


def _check_version(new: T.Manifest, old: T.Manifest) -> bool:
    from .verspec import compare_version
    return compare_version(new['version'], '>', old['version'])


def _get_dir_to_last_installed_version(appid: str) -> t.Optional[str]:
    if last_ver := get_last_installed_version(appid):
        dir_ = '{}/{}/{}'.format(paths.project.apps, appid, last_ver)
        assert exists(dir_), dir_
        return dir_
    return None


def _get_manifest_path(target: str, ensure_exists: bool = True) -> str:
    """ return an abspath to manifest file. """
    if target.endswith('.json'):
        out = fs.normpath(target, True)
    else:
        assert not os.path.isfile(target)
        if not os.path.exists(target):
            os.mkdir(target)
        out = fs.normpath(f'{target}/manifest.json', True)
    if ensure_exists:
        assert exists(out)
    print(f'manifest file: {out}', ':pv')
    return out


def _get_manifests(appid: str) -> t.Tuple[t.Optional[T.Manifest], T.Manifest]:
    from .manifest import load_manifest
    from .oss import get_oss_client
    from .utils import make_temp_dir
    
    temp_dir = make_temp_dir()
    
    oss = get_oss_client(appid)
    oss.download(oss.path.manifest, x := f'{temp_dir}/manifest.pkl')
    manifest_new = load_manifest(x)
    manifest_new.start_directory = '{}/{}/{}'.format(
        paths.project.apps, manifest_new['appid'], manifest_new['version']
    )
    manifest_new.make_tree()
    fs.move(x, manifest_new['start_directory'] + '/manifest.pkl')
    
    if x := _get_dir_to_last_installed_version(appid):
        manifest_old = load_manifest(f'{x}/manifest.pkl')
    else:
        print(
            'no previous version found, it may be your first time to install '
            f'{appid}'
        )
        print(
            '[dim]be noted the first-time installation may consume a long '
            'time. depsland will try to reduce the consumption in the '
            'succeeding upgrades/installations.[/]',
            ':r',
        )
        manifest_old = None
    
    return manifest_old, manifest_new


def _run_cli() -> None:
    """ this function is for poetry to generate script entry point. """
    cli.run()


if __name__ == '__main__':
    # pox -m depsland -h
    # pox -m depsland launch-gui
    cli.run()
