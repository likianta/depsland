import os
import typing as t
from collections import defaultdict
from os.path import exists
from textwrap import dedent

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

from ... import paths
from ...manifest import T as T0
from ...manifest import change_start_directory
from ...manifest import compare_manifests
from ...manifest import dump_manifest
from ...manifest import get_last_installed_version
from ...manifest import init_manifest
from ...manifest import init_target_tree
from ...manifest import load_manifest
from ...normalization import normalize_name
from ...normalization import normalize_version_spec
from ...oss import T as T1
from ...oss import get_oss_client
from ...pypi import pypi
from ...utils import bat_2_exe
from ...utils import compare_version
from ...utils import create_shortcut
from ...utils import make_temp_dir
from ...utils import ziptool
from ...utils.verspec import semver_parse


class T:
    AssetInfo = T0.AssetInfo
    LauncherInfo = T0.Launcher1
    Manifest = T0.Manifest1
    ManifestPypi = t.Dict[str, None]
    Oss = T1.Oss
    Path = str


# -----------------------------------------------------------------------------

def install_by_appid(
        appid: str,
        upgrade: bool = True,
        reinstall: bool = False,
) -> None:
    m1, m0 = _get_manifests(appid)
    if m0 is None:
        m0 = init_manifest(appid, m1['name'])
    install(m1, m0, upgrade, reinstall)


def install_local(
        manifest_file: T.Path,
        upgrade: bool = True,
        reinstall: bool = False,
) -> None:
    m1 = load_manifest(manifest_file)
    
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
    else:
        m0 = init_manifest(appid, name)
    
    install(m1, m0, upgrade, reinstall, custom_oss_root)


def install(
        manifest_new: T.Manifest,
        manifest_old: T.Manifest = None,
        upgrade: bool = True,
        reinstall: bool = False,
        custom_oss_root: T.Path = None,
) -> None:
    appid = manifest_new['appid']
    if _check_version(manifest_new, manifest_old):
        if upgrade:
            # install first, then uninstall old.
            _install(manifest_new, manifest_old, custom_oss_root)
            # TODO: for safety consideration, below is temporarily disabled,
            #   wait for a future version that supports complete auto-upgrade.
            # _uninstall(appid, m0['version'],
            #            remove_venv=False, remove_bin=False)
        else:
            print('new version available but not installed. you can use '
                  '`depsland install -u {appid}` or `depsland upgrade {appid}` '
                  'to get it.'.format(appid=appid))
    else:  # TODO
        if reinstall:
            from .uninstall import main as _uninstall
            # assert m0['version'] == m1['version']
            _uninstall(appid, manifest_old['version'])
            install_by_appid(appid, upgrade=False, reinstall=False)
        else:
            print('current version is up to date. you can use `depsland '
                  'install -r {appid}` or `depsland reinstall {appid} to force '
                  'reinstall it.'.format(appid=appid))


def _install(
        manifest_new: T.Manifest,
        manifest_old: T.Manifest,
        custom_oss_root: T.Path = None
) -> None:
    dir_m = make_temp_dir()
    
    if custom_oss_root:
        print('use local oss server', ':v2')
        oss = get_oss_client(manifest_new['appid'], server='local')
        oss.path.root = custom_oss_root
    else:
        oss = get_oss_client(manifest_new['appid'])
    print(oss.path)
    
    _install_files(manifest_new, manifest_old, oss, dir_m)
    _install_custom_packages(manifest_new, manifest_old, oss)
    _install_dependencies(manifest_new, manifest_old)
    _create_launcher(manifest_new)
    
    _save_history(manifest_new['appid'], manifest_new['version'])
    _save_manifest(manifest_new)


# -----------------------------------------------------------------------------
# callees for `install_by_appid`

def _check_update(
        manifest_new: T.Manifest,
        manifest_old: T.Manifest,
) -> bool:
    return compare_version(
        manifest_new['version'], '>', manifest_old['version']
    )


def _check_version(new: T.Manifest, old: T.Manifest) -> bool:
    return compare_version(new['version'], '>', old['version'])


def _get_dir_to_last_installed_version(appid: str) -> t.Optional[str]:
    if last_ver := get_last_installed_version(appid):
        dir_ = '{}/{}/{}'.format(paths.project.apps, appid, last_ver)
        assert exists(dir_), dir_
        return dir_
    return None


def _get_manifests(appid: str) -> t.Tuple[T.Manifest, t.Optional[T.Manifest]]:
    def download_new() -> T.Manifest:
        tmp_dir = make_temp_dir()
        oss = get_oss_client(appid)
        oss.download(oss.path.manifest, x := f'{tmp_dir}/manifest.pkl')
        manifest_new = load_manifest(x)
        change_start_directory(manifest_new, '{}/{}/{}'.format(
            paths.project.apps,
            manifest_new['appid'],
            manifest_new['version']
        ))
        init_target_tree(manifest_new)
        fs.move(x, manifest_new['start_directory'] + '/manifest.pkl')
        return manifest_new
    
    def find_old() -> t.Optional[T.Manifest]:
        if x := _get_dir_to_last_installed_version(appid):
            return load_manifest(f'{x}/manifest.pkl')
        else:
            print(f'no previous version found, it may be your first time to '
                  f'install {appid}')
            print('[dim]be noted the first-time installation may consume a '
                  'long time. depsland will try to reduce the consumption in '
                  'the succeeding upgrades/installations.[/]', ':r')
            return None
    
    new, old = download_new(), find_old()
    return new, old


# -----------------------------------------------------------------------------
# callees for main process.

def _install_files(
        manifest_new: T.Manifest,
        manifest_old: T.Manifest,
        oss: T.Oss,
        temp_dir: T.Path
) -> None:
    root0 = manifest_old['start_directory']
    root1 = manifest_new['start_directory']
    
    diff = compare_manifests(manifest_new, manifest_old)
    
    def download_from_oss(i: str, m: str, o: str) -> None:
        print(fs.relpath(o, root1))
        oss.download(i, m)
        ziptool.extract_file(m, o, overwrite=True)
    
    def copy_from_old(i: str, o: str, t: str) -> None:
        # `o` must not be child path of `i`.
        assert not o.startswith(i + '/')
        print('{} -> {}'.format(i, fs.relpath(o, root1)))
        # TODO: shall we use `fs.move` to make it faster?
        if t == 'file':
            fs.copy_file(i, o, True)
        else:
            fs.copy_tree(i, o, True)
    
    for action, relpath, (info0, info1) in diff['assets']:
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
            path_m = fs.normpath('{}/{}.{}'.format(
                # an intermediate file (zip)
                temp_dir, info1.uid,
                'zip' if info1.type == 'dir' else 'fzip'
            ))
            path_o = fs.normpath(f'{root1}/{relpath}')  # a file or a directory
            download_from_oss(path_i, path_m, path_o)


def _install_custom_packages(
        manifest_new: T.Manifest,
        manifest_old: T.Manifest,
        oss: T.Oss,
) -> None:
    pypi0: T.ManifestPypi = manifest_old['pypi']
    pypi1: T.ManifestPypi = manifest_new['pypi']
    downloads_dir = paths.pypi.downloads
    
    new_files = []
    for name in pypi1:
        if name not in pypi0:
            if not os.path.exists(f'{downloads_dir}/{name}'):
                print('download package (whl) from oss', name)
                oss.download(
                    f'{oss.path.pypi}/{name}',
                    dl := f'{downloads_dir}/{name}',
                )
                new_files.append(dl)
    
    if new_files:
        pypi.add_to_indexes(*new_files, download_dependencies=True)


def _install_dependencies(
        manifest_new: T.Manifest,
        manifest_old: T.Manifest,
        dst_dir: str = None
) -> None:
    if dst_dir is None:
        dst_dir = paths.apps.make_packages(
            manifest_new['appid'], manifest_new['version'], clear_exists=True
        )
    
    # else: make sure `dst_dir` does exist.
    
    def is_same() -> bool:
        if manifest_old['version'] == '0.0.0':
            return False
        new_deps = set(manifest_new['dependencies'].items())
        old_deps = set(manifest_old['dependencies'].items())
        return new_deps == old_deps
    
    if is_same():
        src_dir = paths.apps.get_packages(
            manifest_old['appid'], manifest_old['version']
        )
        fs.make_link(src_dir, dst_dir, True)
        return
    
    packages = {}
    for name, vspec in manifest_new['dependencies'].items():
        name = normalize_name(name)
        vspecs = tuple(normalize_version_spec(name, vspec))
        packages[name] = vspecs
    if not packages: return
    print(':vl', packages)
    
    name_ids = pypi.install(packages, include_dependencies=True)
    name_ids = tuple(dict.fromkeys(name_ids))  # deduplicate and remain sequence
    name_ids = _resolve_conflicting_name_ids(name_ids)
    pypi.save_index()
    pypi.linking(sorted(name_ids), dst_dir)


def _create_launcher(manifest: T.Manifest) -> None:
    appid = manifest['appid']
    appname = manifest['name']
    version = manifest['version']
    
    # bat command
    command = dedent(r'''
        @echo off
        set PYTHONPATH=%DEPSLAND%
        {py} -m depsland run {appid} --:version {version}
    ''').strip().format(
        py=r'"%DEPSLAND%\python\python.exe"',
        appid=appid,
        version=version,
    )
    
    # bat to exe
    dumps(command, bat_file := '{apps}/{appid}/{version}/{appid}.bat'.format(
        apps=paths.project.apps, appid=appid, version=version
    ))
    exe_file = bat_2_exe(
        bat_file,
        icon=manifest['launcher']['icon'],
        show_console=manifest['launcher']['show_console'],
        remove_bat=True
    )
    
    # create shortcuts
    if manifest['launcher']['cli_tool']:
        fs.copy_file(exe_file, '{}/{}.exe'.format(
            paths.apps.bin, appid,
        ))
    if manifest['launcher']['desktop']:
        create_shortcut(
            file_i=exe_file,
            file_o='{}/{}.lnk'.format(
                paths.system.desktop, appname
            )
        )
    if manifest['launcher']['start_menu']:
        # WARNING: not tested
        fs.copy_file(exe_file, '{}/{}.exe'.format(
            paths.system.start_menu, appname
        ))


def _save_history(appid: str, version: str) -> None:
    file = paths.apps.get_installation_history(appid)
    if os.path.exists(file):
        data: list = loads(file).splitlines()
    else:
        data = []
    data.insert(0, version)
    dumps(data, file)


def _save_manifest(manifest: T.Manifest) -> None:
    file_o = '{}/{}/{}/manifest.pkl'.format(
        paths.project.apps, manifest['appid'], manifest['version']
    )
    dump_manifest(manifest, file_o)


# -----------------------------------------------------------------------------

def _resolve_conflicting_name_ids(name_ids: t.Iterable[str]) -> t.Iterable[str]:
    """
    if there are multiple versions for one name, for example 'lk_utils-2.4.1'
    and 'lk_utils-2.5.0', remain the most latest version.
    FIXME: this may not be a good idea, better to raise an error right once.
    """
    name_2_versions = defaultdict(list)
    for nid in name_ids:
        a, b = nid.split('-', 1)
        name_2_versions[a].append(b)
    if conflicts := {k: v for k, v in name_2_versions.items() if len(v) > 1}:
        print('found {} conflicting name ids'.format(len(conflicts)),
              conflicts, ':lv3')
        for v in conflicts.values():
            v.sort(key=lambda x: semver_parse(x), reverse=True)
        return (f'{k}-{v[0]}' for k, v in name_2_versions.items())
    else:
        return name_ids
