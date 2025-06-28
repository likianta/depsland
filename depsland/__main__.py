if 1:
    if not __package__:  # noqa
        __package__ = 'depsland'
if 2:
    import os
    import sys
    if sys.orig_argv[0].endswith('.exe'):
        os.environ['LK_LOGGER_MODERN_WINDOW'] = '0'

import sys
import typing as t

from argsense import CommandLineInterface
from lk_utils import fs

from . import __path__
from . import __version__
from . import api
from . import paths
from .depsolver import resolve_dependencies
from .manifest import T
from .manifest import get_last_installed_version
from .manifest import load_manifest
from .normalization import check_name_normalized

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


# -----------------------------------------------------------------------------
# depsland intro

@cli
def about() -> None:
    """
    show basic information about depsland.
    """
    from . import __date__
    from . import __path__
    from . import __version__
    print(':rs1', '[red b]♥ depsland [u]v{}[/] ♥[/]'.format(__version__))
    print(':rs1', '  [cyan]released at [u]{}[/][/]'.format(__date__))
    print(':rs1', '  [magenta]located  at [u]{}[/][/]'.format(__path__[0]))


@cli
def self_location() -> None:
    print('[green b u]{}[/]'.format(fs.xpath('.')), ':s1r')


@cli
def welcome(confirm_close: bool = False) -> None:
    """
    show welcome message and exit.
    """
    from . import __date__
    from . import __version__
    
    print(
        ':r2',
        '''
        # DEPSLAND
        
        Depsland is a python apps manager for non-developer users.
        
        - Version: {}
        - Release date: {}
        - Author: {}
        - Official site: {}
        '''.format(
            __version__,
            __date__,
            'Likianta (likianta@foxmail.com)',
            'https://github.com/likianta/depsland',
        )
    )
    
    if confirm_close:
        input('press enter to close window...')


# -----------------------------------------------------------------------------
# depsland ui

@cli
def launch_gui(
    port: int = 2180,
    _app_token: str = None,
    _run_at_once: t.Optional[bool] = False,
) -> None:
    """
    launch depsland gui.
    
    params:
        _app_token: an appid or a path to a manifest file.
            if given, the app will launch and instantly install it.
        _run_at_once:
            for `true` example, see `./api/dev_api/publish.py : main() : -
            \\[var] command`
            for `false` example, see `./api/dev_api/offline_build.py : -
            _create_updator()`
    """
    import streamlit_canary as sc
    sc.run(
        title='Depsland Appstore',
        target='depsland/webui/app.py',
        extra_args=(
            _app_token or ':empty',
            ':true' if _run_at_once else ':false'
        ),
        port=port,
        show_window=True,
        size=(1200, 2000),
        icon=paths.build.launcher_icon,
    )


# -----------------------------------------------------------------------------
# development process (ordered by lifecycle)

@cli
def init(target: str = '.', app_name: str = '') -> None:
    """
    create a "manifest.json" file in project directory.
    
    params:
        target (-t): a directory or file path to generate manifest file at.
            if given a directory, will create a "manifest.json" file under -
            this directory.
            if given a file, the file can be:
                - a '.json' file, suggest naming as 'manifest.json'.
                - a '.yaml' file, suggest naming as 'manifest.yaml'.
                - 'pyproject.toml' file, make sure there is a section named -
                    '[tool.depsland.manifest]'.
            be noticed if file exists, will overwrite it.
        app_name (-n): if not given, will use directory name as app name.
    """
    manifest_file = _normalize_manifest_path(target, ensure_exists=False)
    api.init(manifest_file, app_name)


@cli
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
    
    params:
        manifest (-m): see `init : [param] target : [docstring]`.
    """
    if offline:
        api.build_offline(_normalize_manifest_path(manifest))
    else:
        api.build(_normalize_manifest_path(manifest))


@cli
def publish(
    target: str = '.',
    full_upload: bool = False,
    upload_dependencies: bool = False,
) -> None:
    """
    publish dist assets to oss.
    if you configured a local oss server, it will generate assets to -
    `~/oss/apps/<appid>/<version>` directory.
    
    params:
        target (-t): see `init : [param] target : [docstring]`.
        full_upload (-f): if true, will upload all assets, ignore the files -
            which may already exist in oss (they all will be overwritten).
            this option is useful if you found the oss server not work properly.
        upload_dependencies (-d):
    """
    api.publish(
        _normalize_manifest_path(target), full_upload, upload_dependencies
    )


@cli
def install(appid: str, upgrade: bool = True, reinstall: bool = False) -> None:
    """
    install an app from oss by querying appid.
    
    params:
        upgrade (-u):
        reinstall (-r):
    """
    assert check_name_normalized(appid)
    api.install_by_appid(appid, upgrade, reinstall)


@cli
def upgrade(appid: str) -> None:
    """
    upgrade an app from oss by querying appid.
    """
    api.install_by_appid(appid, upgrade=True, reinstall=False)


@cli
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


# -----------------------------------------------------------------------------
# launch application

cli.add_cmd(api.user_api.run_app, 'run', transfer_help=True)


# @cli
# def run(appid: str = None, version: str = None, *args, **kwargs) -> None:
#     # if 'VIRTURAL_ENV' in os.environ:
#     #     del os.environ['VIRTURAL_ENV']
#     api.user_api.run_app(appid, _version=version, *args, **kwargs)


@cli
def runx(
    appid: str,
    version: str = None,
    use_exist: bool = True,
    *,
    dry_run: bool = False,
) -> None:
    """
    check app exists, if not, download and install it. then run the application.
    prerequisite:
        make sure your network available.
    """
    app_exists = False
    ver_exists = False
    if fs.exist(x := '{}/{}'.format(paths.apps.root, appid)):
        app_exists = True
        if version:
            if fs.exist('{}/{}'.format(x, version)):
                ver_exists = True
        else:
            if use_exist:
                assert _get_dir_to_last_installed_version(appid)
                ver_exists = True
            else:
                raise NotImplementedError
    
    if app_exists and ver_exists:
        api.user_api.run_app(appid, _version=version)
    else:
        m: T.Manifest
        if app_exists:
            x = _get_dir_to_last_installed_version(appid)
            m = load_manifest(f'{x}/manifest.pkl')
        else:
            _, m = _get_manifests(appid)
            # FIXME: what if `m['version'] > version`?
        
        # show a mini UI to notify user the installation progress.
        import streamlit_canary as sc
        sc.run(
            title='Depsland Setup Wizard',
            icon=paths.build.launcher_icon,
            target=fs.xpath('webui/setup_wizard/app.py'),
            extra_args=(
                m['name'],
                m['appid'],
                ':empty',  # TODO: description
                '--dry-run' if dry_run else '--not-dry-run',
                # ':true' if dry_run else ':false',
            ),
            port=2181,
            show_window=True,
            size=(1010, 700),
        )


def _cli() -> None:
    """
    this function is for poetry to generate script entry.
    see also `pyproject.toml : [tool.poetry.scripts]`.
    """
    cli.run()


# -----------------------------------------------------------------------------
# view application


@cli
def list_apps() -> None:
    """
    list installed apps.
    """
    rows = [('index', 'app name', 'appid', 'version')]
    i = 0
    for d in fs.find_dirs(paths.project.apps):
        if not d.name.startswith('.'):
            if fs.exist(x := f'{d.path}/.inst_history'):
                latest_version = None
                with open(x, 'r', encoding='utf-8') as f:
                    for first_line in f.readlines():
                        latest_version = first_line.strip()
                        break
                assert latest_version
                i += 1
                rows.append((
                    str(i),
                    fs.load('{}/{}/manifest.pkl'.format(
                        d.path, latest_version))['name'],
                    d.name,
                    latest_version,
                ))
    if len(rows) > 1:
        print(rows, ':r2')
    else:
        print('there is no installed apps in "{}"'.format(paths.project.apps))


@cli
def show(appid: str, version: str = None) -> None:
    """
    show manifest of an app.
    """
    if version is None:
        version = get_last_installed_version(appid)
    assert version is not None
    dir_ = '{}/{}/{}'.format(paths.project.apps, appid, version)
    manifest = load_manifest(f'{dir_}/manifest.pkl')
    print(manifest, ':l')


@cli
def view_manifest(manifest: str = '.') -> None:
    if manifest.endswith('.pkl'):
        manifest = load_manifest(manifest).model
    else:
        manifest = load_manifest(_normalize_manifest_path(manifest))
    print(manifest, ':l')


@cli
def show_packages(poetry_file: str, save_result: str = None) -> None:
    pkgs = resolve_dependencies('poetry.lock', fs.parent(poetry_file))
    rows = [('index', 'name', 'version', 'files count')]
    indx = 0
    for name, info in pkgs.items():
        indx += 1
        # noinspection PyTypeChecker
        rows.append((indx, name, info['version'], len(info['files'])))
    print(rows, ':r2')
    if save_result:
        fs.dump(pkgs, save_result)


@cli
def get_package_size(
    name: str, version: str = None, include_dependencies: bool = False
) -> None:
    """
    params:
        include_dependencies (-d):
    """
    from .pypi import insight
    insight.measure_package_size(name, version, include_dependencies)


# -----------------------------------------------------------------------------
# utilities

@cli
def open_readme(target: str, scheme: str = 'default', **kwargs) -> None:
    if scheme == 'default':
        raise NotImplementedError
    elif scheme == 'mkdocs_material':
        assert fs.isdir(target)
        port = kwargs['port']
        print('mkdocs server -a 0.0.0.0:{}'.format(port))
        ...


# -----------------------------------------------------------------------------
# misc

def _check_version(new: T.Manifest, old: T.Manifest) -> bool:
    from .verspec import compare_version
    return compare_version(new['version'], '>', old['version'])


def _get_dir_to_last_installed_version(appid: str) -> t.Optional[str]:
    if last_ver := get_last_installed_version(appid):
        dir_ = '{}/{}/{}'.format(paths.project.apps, appid, last_ver)
        assert fs.exist(dir_), dir_
        return dir_
    return None


def _get_manifests(appid: str) -> t.Tuple[t.Optional[T.Manifest], T.Manifest]:
    """ get old and new manifests by appid. """
    from .oss import get_oss_client
    from .utils import make_temp_dir
    
    temp_dir = make_temp_dir()
    
    oss = get_oss_client(appid)
    oss.download(oss.path.manifest, x := f'{temp_dir}/manifest.pkl')
    manifest_new = load_manifest(x)
    manifest_new['start_directory'] = '{}/{}/{}'.format(
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


def _normalize_manifest_path(target: str, ensure_exists: bool = True) -> str:
    """ return an abspath to manifest file. """
    if target.endswith(('.json', '.yaml', '.toml')):
        out = fs.normpath(target, True)
    else:
        assert fs.isdir(target)
        if not fs.exist(target):
            fs.make_dir(target)
        out = fs.normpath(f'{target}/manifest.json', True)
    if ensure_exists:
        assert fs.exist(out)
    print(f'manifest file: {out}', ':pv')
    return out


if __name__ == '__main__':
    # pox -m depsland -h
    # pox -m depsland launch-gui
    # pox -m depsland run hello_world_tkinter
    cli.run()
