import os
import typing as t

from lk_utils import Signal
from lk_utils import fs

from ... import paths
from ...manifest import T as T0
from ...manifest import diff_manifest
from ...manifest import dump_manifest
from ...manifest import get_last_installed_version
from ...manifest import init_manifest
from ...manifest import load_manifest
from ...oss import T as T1
from ...oss import get_oss_client
# from ...platform import create_launcher
from ...platform import sysinfo
from ...platform.launcher import create_desktop_shortcut
from ...platform.launcher.make_exe import add_icon_to_exe
from ...pypi import pypi
from ...pypi.pypi import LocalPyPI
from ...utils import make_temp_dir
from ...utils import ziptool
from ...verspec import compare_version


class T(T0):
    LauncherInfo = T0.Launcher  # alias
    Oss = T1.Oss
    Path = str
    PackageResolver = t.Union[LocalPyPI, T1.Oss]
    ProgressStage = t.Literal['assets', 'deps', 'venv', 'cleanup']


# Signal[stage, total, current, text]
#   stage: see T.ProgressStage
#   total: 1-based counter.
#   current: same like `total`.
#   text: we currently use lower-cased descriptive text.
#       the ui side may need to convert it to a more user-friendly format.
progress_updated = Signal(str, int, int, str)  # used by ui side


def install_by_appid(
    appid: str, upgrade: bool = True, reinstall: bool = False
) -> str:
    m1, m0 = _get_manifests(appid)
    if m0 is None:
        m0 = init_manifest(appid, m1['name'])
    return install(m1, m0, upgrade, reinstall)


def install_local(
    manifest_file: T.Path, upgrade: bool = True, reinstall: bool = False
) -> str:
    m1 = load_manifest(manifest_file)
    
    if fs.exists(d := '{}/.oss'.format(m1['start_directory'])):
        custom_oss_root = d
    else:
        custom_oss_root = None
    
    m1.make_tree(d := '{}/{}/{}'.format(
        paths.project.apps, m1['appid'], m1['version']
    ))
    m1.start_directory = d
    
    appid, name = m1['appid'], m1['name']
    if x := _get_dir_to_last_installed_version(appid):
        m0 = load_manifest(f'{x}/manifest.pkl')
    else:
        m0 = init_manifest(appid, name)
    
    return install(m1, m0, upgrade, reinstall, custom_oss_root)


def install(
    manifest_new: T.Manifest,
    manifest_old: T.Manifest = None,
    upgrade: bool = True,
    reinstall: bool = False,
    custom_oss_root: T.Path = None,
) -> str:
    """
    download and install assets from oss & pypi to the target directory of -
    `manifest_new`.
    this is an incremental operation. we download only the different parts and -
    try to reuse existed stuff as much as possible.
    usually the target directory is `<depsland.paths.apps>/<appid>/<version>`.
    """
    appid = manifest_new['appid']
    if _check_version(manifest_new, manifest_old):
        if upgrade:
            # install first, then uninstall old.
            _install(manifest_new, manifest_old, custom_oss_root)
            # TODO: for safety consideration, below is temporarily disabled, -
            #   wait for a future version that supports complete auto-upgrade.
            # _uninstall(
            #     appid, m0['version'],
            #     remove_venv=False, remove_bin=False
            # )
        else:
            print(
                'new version available but not installed. you can use '
                '`depsland install -u {appid}` or `depsland upgrade {appid}` '
                'to get it.'.format(appid=appid)
            )
    else:  # TODO
        if reinstall:
            from .uninstall import main as _uninstall
            # assert m0['version'] == m1['version']
            _uninstall(appid, manifest_old['version'])
            install_by_appid(appid, upgrade=False, reinstall=False)
        else:
            print(
                'current version is up to date. you can use `depsland '
                'install -r {appid}` or `depsland reinstall {appid}` to force '
                'reinstall it.'.format(appid=appid)
            )
    return manifest_new['start_directory']


def _install(
    manifest_new: T.Manifest,
    manifest_old: T.Manifest,
    custom_oss_root: T.Path = None,
) -> None:
    dir_m = make_temp_dir()
    
    if custom_oss_root:
        print('use local oss server', ':v1')
        oss = get_oss_client(manifest_new['appid'], server='local')
        oss.path.root = custom_oss_root
    else:
        oss = get_oss_client(manifest_new['appid'])
    print(oss.path)
    
    package_resolver = pypi
    if x := manifest_new.get('experiments'):
        if x.get('package_provider') == 'oss':
            print(':v1', 'experimental feature: use oss as package provider')
            package_resolver = oss
    
    _install_files(manifest_new, manifest_old, oss, dir_m)
    _install_packages(manifest_new, manifest_old, package_resolver)
    _create_launchers(manifest_new)
    
    _save_history(manifest_new['appid'], manifest_new['version'])
    _save_manifest(manifest_new)
    
    print(':rt', '[green]installation done[/]')


# -----------------------------------------------------------------------------
# callees for `install_by_appid`


def _check_update(manifest_new: T.Manifest, manifest_old: T.Manifest) -> bool:
    return compare_version(
        manifest_new['version'], '>', manifest_old['version']
    )


def _check_version(new: T.Manifest, old: T.Manifest) -> bool:
    """ check if version upgradale. """
    return compare_version(new['version'], '>', old['version'])


def _get_dir_to_last_installed_version(appid: str) -> t.Optional[str]:
    if last_ver := get_last_installed_version(appid):
        dir_ = '{}/{}/{}'.format(paths.project.apps, appid, last_ver)
        assert fs.exists(dir_), dir_
        return dir_
    return None


def _get_manifests(appid: str) -> t.Tuple[T.Manifest, t.Optional[T.Manifest]]:
    def download_new() -> T.Manifest:
        tmp_dir = make_temp_dir()
        oss = get_oss_client(appid)
        oss.download(oss.path.manifest, x := f'{tmp_dir}/manifest.pkl')
        manifest_new = load_manifest(x)
        manifest_new.start_directory = '{}/{}/{}'.format(
            paths.project.apps,
            manifest_new['appid'],
            manifest_new['version'],
        )
        manifest_new.make_tree()
        fs.move(x, manifest_new['start_directory'] + '/manifest.pkl')
        return manifest_new
    
    def find_old() -> t.Optional[T.Manifest]:
        if x := _get_dir_to_last_installed_version(appid):
            return load_manifest(f'{x}/manifest.pkl')
        else:
            print(
                'no previous version found, it may be your first time to '
                'install "{}"'.format(appid)
            )
            print(
                'be noted the first-time installation may take a long time',
                ':v',
            )
            return None
    
    new, old = download_new(), find_old()
    return new, old


# -----------------------------------------------------------------------------
# callees for main process.


def _install_files(
    manifest_new: T.Manifest,
    manifest_old: T.Manifest,
    oss: T.Oss,
    temp_dir: T.Path,
) -> None:
    root0 = manifest_old['start_directory']
    root1 = manifest_new['start_directory']
    _root00 = fs.parent(root0)
    _root10 = fs.parent(root1)
    
    # noinspection PyUnusedLocal
    def copy_from_old(i: str, o: str, t: str) -> None:
        # `o` must not be child path of `i`.
        assert not o.startswith(i + '/')
        print('{} -> {}'.format(fs.relpath(i, _root00), fs.relpath(o, _root10)))
        fs.make_link(i, o, True)
        # if t == 'file':
        #     fs.copy_file(i, o, True)
        # else:
        #     fs.copy_tree(i, o, True)
    
    def download_from_oss(i: str, m: str, o: str) -> None:
        print(fs.relpath(o, _root10))
        oss.download(i, m)
        ziptool.extract_file(m, o, overwrite=True)
    
    total_diff = diff_manifest(manifest_new, manifest_old)
    assets_diff = tuple(total_diff['assets'])
    assets_diff_cnt = len(assets_diff)
    curr_cnt = 0  # 1-based
    
    for action, relpath, (info0, info1) in assets_diff:
        curr_cnt += 1
        progress_updated.emit(
            'assets', assets_diff_cnt, curr_cnt,
            'updating asset "{}" ({})'.format(relpath, action)
        )
        
        if action == 'ignore':
            path0 = fs.normpath(f'{root0}/{relpath}')
            path1 = fs.normpath(f'{root1}/{relpath}')
            if os.path.exists(path0):
                copy_from_old(path0, path1, info1.type)
                continue
            else:
                print('turn ignore to append action')
                action = 'append'
        
        if action in ('append', 'update'):
            path_i = '{}/{}'.format(oss.path.assets, info1.uid)  # an url
            path_m = fs.normpath(  # an intermediate file (zip)
                '{}/{}.{}'.format(
                    temp_dir,
                    info1.uid,
                    'zip' if info1.type == 'dir' else 'fzip',
                )
            )
            path_o = fs.normpath(f'{root1}/{relpath}')  # a file or a directory
            download_from_oss(path_i, path_m, path_o)


def _install_packages(
    manifest_new: T.Manifest,
    manifest_old: T.Manifest,
    # package_resolver: t.Literal['oss', 'pypi'] = 'pypi',
    package_resolver: T.PackageResolver = pypi,
) -> None:
    if not manifest_new['dependencies']:
        print('no dependency for this project')
        return
    
    total_diff = diff_manifest(manifest_new, manifest_old)
    deps_diff = tuple(total_diff['dependencies'])
    # deps_diff_cnt = len(deps_diff)
    
    # curr_cnt = 0
    package_ids = set()
    tasks_ignitor = []  # list[T.PackageInfo]
    
    action: T.Action
    info0: T.PackageInfo
    info1: T.PackageInfo
    pkg_id: T.PackageId
    pkg_name: T.PackageName
    
    for action, pkg_name, (info0, info1) in deps_diff:
        # curr_cnt += 1
        # progress_updated.emit(
        #     'deps', deps_diff_cnt, curr_cnt,
        #     'updating "{}" ({})'.format(pkg_name, action)
        # )
        if action == 'delete':  # this is handled by oss util.
            continue
        pkg_id = info1['id']
        if action in ('append', 'update'):
            tasks_ignitor.append(info1)
        package_ids.add(pkg_id)
    
    has_new_packages = bool(tasks_ignitor)
    if tasks_ignitor:
        print(len(tasks_ignitor))
        
        def pip_download_and_install(info: T.PackageInfo) -> None:
            if info['id'] in pypi.index.id_2_paths:
                # this case should always be False in production environment. -
                # but may be True in development environment.
                return
            dl_path = pypi.download_one(
                info['id'],
                info['appendix'] and info['appendix'].get('custom_url')
            )
            pypi.install_one(info['id'], dl_path)
        
        def oss_download_and_install(info: T.PackageInfo) -> None:
            if info['id'] in pypi.index.id_2_paths:
                # this case should always be False in production environment. -
                # but may be True in development environment.
                return
            resource_path = '{}/{}'.format(_oss.path.pypi, info['id'])
            download_path = '{}/{}.zip'.format(paths.pypi.downloads, info['id'])
            #   note: we use '<name>-<id>.zip' as downloaded filename, the -
            #   normalization module supports segamenting this format.
            #   see `depsland.normalization.split_filename_of_package`.
            install_path = '{}/{}/{}'.format(
                paths.pypi.installed, info['name'], info['version']
            )
            fs.make_dirs('{}/{}'.format(paths.pypi.installed, info['name']))
            
            _oss.download(resource_path, download_path)
            ziptool.extract_file(download_path, install_path, True)
            pypi.index.update_index(info['id'], download_path, install_path)
        
        # FIXME: thread_pool makes pip install stucked, and ctrl+c cannot -
        #   terminate the process.
        # we will have IO heavy tasks, so promoting max workers is fine.
        # http://c.biancheng.net/view/2627.html
        # https://stackoverflow.com/questions/42541893
        # thread_pool = ThreadPoolExecutor(max_workers=len(tasks_ignitor))
        # tasks = [
        #     thread_pool.submit(download_and_install, info)
        #     for info in tasks_ignitor
        # ]
        # for x in tasks: x.result()
        
        if package_resolver is pypi:
            resolve = pip_download_and_install
        else:
            _oss: T.Oss = package_resolver
            resolve = oss_download_and_install
        
        for i, info in enumerate(tasks_ignitor, 1):
            progress_updated.emit(
                'deps', len(tasks_ignitor), i,
                'fetching dependency "{}"'.format(info['id'])
            )
            resolve(info)
    
    progress_updated.emit('cleanup', 2, 1, 'linking venv')
    venv_dir = paths.apps.make_packages(
        manifest_new['appid'], manifest_new['version'], clear_exists=True
    )
    if has_new_packages:
        pypi.linking(package_ids, venv_dir)
    else:
        def fast_link_venv(dst_dir: T.Path) -> None:
            print('fast link venv from old version')
            assert (
                manifest_old['version'] != '0.0.0'
            ), 'cannot do fast linking from a void version'
            src_dir = paths.apps.get_packages(
                manifest_old['appid'], manifest_old['version']
            )
            fs.make_link(src_dir, dst_dir, True)
        
        fast_link_venv(venv_dir)
    
    pypi.index.save_index()


def _create_launchers(manifest: T.Manifest) -> None:
    print('creating launcher... (this may be slow)')
    progress_updated.emit('cleanup', 2, 2, 'creating launcher')
    
    exe_file = '{}/{}/{}/{}.exe'.format(
        paths.project.apps,
        manifest['appid'],
        manifest['version'],
        manifest['name'],
    )
    if manifest['launcher']['show_console']:
        fs.copy_file(paths.build.depsland_runapp_console_exe, exe_file)
    else:
        fs.copy_file(paths.build.depsland_runapp_exe, exe_file)
    if x := manifest['launcher']['icon']:
        add_icon_to_exe(exe_file, x)
    
    if sysinfo.IS_WINDOWS:
        launcher: T.LauncherInfo = manifest['launcher']
        
        # if not launcher['show_console']:
        #     # since console-less application is hard to debug if failed at -
        #     # startup, we provide a "debug" launcher for user.
        #     create_launcher(
        #         manifest,
        #         dir_o='{apps}/{appid}/{version}'.format(
        #             apps=paths.project.apps,
        #             appid=manifest['appid'],
        #             version=manifest['version'],
        #         ),
        #         name=manifest['name'] + ' (Debug).exe',
        #         debug=True,
        #         # keep_bat=False,
        #         uac_admin=True,
        #     )
        # create debug launcher
        dbg_exe_file = '{}/{}/{}/{} (Debug).exe'.format(
            paths.project.apps,
            manifest['appid'],
            manifest['version'],
            manifest['name'],
        )
        fs.copy_file(paths.build.depsland_runapp_debug_exe, dbg_exe_file)
        if x := manifest['launcher']['icon']:
            add_icon_to_exe(dbg_exe_file, x)
        
        if launcher['enable_cli']:
            fs.copy_file(exe_file, '{}/{}.exe'.format(
                paths.apps.bin, manifest['appid']
            ))
        if launcher['add_to_desktop']:
            create_desktop_shortcut(
                file_i=exe_file,
                file_o='{}/{}.lnk'.format(
                    paths.system.desktop, manifest['name']
                ),
            )
        if launcher['add_to_start_menu']:
            # WARNING: not tested
            fs.copy_file(
                exe_file, '{}/{}.exe'.format(
                    paths.system.start_menu, manifest['name']
                )
            )
    
    if paths.project.project_mode == 'shipboard':
        # ref: `/depsland/paths.py:Project:_setup_shipboard_mode`
        if manifest['readme']:
            fs.make_link(
                manifest['readme'],
                '{}/README.{}'.format(
                    fs.parent(paths.project.root),
                    fs.split(manifest['readme'], 3)[2]
                ),
                True
            )


def _save_history(appid: str, version: str) -> None:
    file = paths.apps.get_installation_history(appid)
    if os.path.exists(file):
        data: list = fs.load(file).splitlines()
    else:
        data = []
    data.insert(0, version)
    fs.dump(data, file)
    print('new installation is recorded')


def _save_manifest(manifest: T.Manifest) -> None:
    file_o = '{}/{}/{}/manifest.pkl'.format(
        paths.project.apps, manifest['appid'], manifest['version']
    )
    dump_manifest(manifest, file_o)
