import os
import typing as t
from textwrap import dedent

from lk_utils import fs

from ... import paths
from ...manifest import T as T0
from ...manifest import diff_manifest
from ...manifest import dump_manifest
from ...manifest import get_app_info
from ...manifest import init_manifest
from ...manifest import load_manifest
from ...oss import T as T1
from ...oss import get_oss_server
from ...platform.launcher import bat_2_exe
from ...platform.system_info import IS_WINDOWS
from ...pypi import pypi
from ...utils import init_target_tree
from ...utils import ziptool
from ...venv.target_venv import get_library_root
from ...verspec import compare_version


class T:
    AssetInfo = T0.AssetInfo
    Manifest = T0.Manifest
    Oss = T1.Oss
    PackageInfo = T0.PackageInfo
    Path = str
    Scheme = T0.Scheme


def main(
    manifest_file: str,
    full_upload: bool = False,
    upload_dependencies: bool = False,
) -> None:
    app_info = get_app_info(manifest_file)
    manifest = load_manifest(manifest_file)
    
    if upload_dependencies:
        if manifest['experiments']['package_provider'] != 'oss':
            print(':v1', 'force change "package_provider" to "oss"')
            manifest['experiments']['package_provider'] = 'oss'
        # print(manifest['experiments'], ':v')
    else:
        assert manifest['experiments']['package_provider'] == 'pypi'
    
    dist_dir = '{root}/dist/{name}-{ver}'.format(
        root=manifest['start_directory'],
        name=manifest['appid'],
        ver=manifest['version'],
    )
    fs.make_dirs(dist_dir)
    
    oss = _upload(
        manifest_new=manifest,
        manifest_old=(
            load_manifest(
                '{}/{}/{}/manifest.pkl'.format(
                    paths.project.apps,
                    app_info['appid'],
                    app_info['history'][0],
                )
            )
            if not full_upload and app_info['history']
            else init_manifest(app_info['appid'], app_info['name'])
        ),
        upload_dependencies=upload_dependencies,
    )
    
    if oss.type in ('local', 'fake'):
        print('pack oss assets to dist dir')
        dir_o = f'{dist_dir}/.oss'
        # fs.make_dirs(dir_o)
        fs.make_link(oss.path.root, dir_o, True)
        
        # TODO: need to refactor this part.
        if IS_WINDOWS:
            print('generate setup script to dist dir')
            bat_file = f'{dist_dir}/setup.bat'
            command = dedent(r'''
                cd /d %~dp0
                "%DEPSLAND%\depsland-sui.exe" launch-gui manifest.pkl :true
            ''').strip()
            fs.dump(command, bat_file)
            
            bat_2_exe(
                bat_file,
                fs.replace_ext(bat_file, 'exe'),
                icon=(
                    manifest['launcher']['icon'] or
                    paths.build.launcher_icon
                ),
                show_console=False,
            )
            fs.remove_file(bat_file)
        else:
            print('"setup.exe" is not available on other platforms', ':v3')
    
    app_info['history'].insert(0, app_info['version'])
    fs.dump(
        app_info['history'],
        paths.apps.get_distribution_history(app_info['appid']),
        type='plain',
    )
    
    print(
        ':tv4', 'publish done. see snapshot at "<depsland>/apps/{}/{}"'.format(
            manifest['appid'], manifest['version']
        )
    )


def _upload(
    manifest_new: T.Manifest,
    manifest_old: T.Manifest,
    upload_dependencies: bool = False,
) -> T.Oss:
    # print(':lv', manifest_new, manifest_old)
    
    _check_manifest(manifest_new, manifest_old)
    _print_change(
        'updating manifest',
        manifest_old['version'],
        manifest_new['version'],
    )
    
    # -------------------------------------------------------------------------
    
    root_new = manifest_new['start_directory']  # noqa
    root_old = manifest_old['start_directory']  # noqa
    
    oss = get_oss_server(manifest_new['appid'])
    print(oss.path)
    
    diff = diff_manifest(manifest_new, manifest_old)
    
    # -------------------------------------------------------------------------
    
    def upload_assets() -> None:
        action: T.Scheme
        info0: t.Optional[T.AssetInfo]
        info1: t.Optional[T.AssetInfo]
        
        for action, relpath, (info0, info1) in diff['assets']:
            if action == 'ignore':
                continue
            
            _print_change(
                f'{action=}, {relpath=}',
                info0 and info0.uid,
                info1 and info1.uid,
                True,
            )
            
            if action in ('append', 'update'):
                zipped_file = _compress_asset(info1, relpath)
            else:
                zipped_file = None
            
            if action == 'append':
                oss.upload(zipped_file, f'{oss.path.assets}/{info1.uid}')
            elif action == 'update':
                oss.delete(f'{oss.path.assets}/{info0.uid}')
                oss.upload(zipped_file, f'{oss.path.assets}/{info1.uid}')
            else:  # action == 'delete'
                oss.delete(f'{oss.path.assets}/{info0.uid}')
    
    def upload_dependencies_() -> None:
        # `depsland.manifest.manifest._diff_dependencies`
        action: T.Scheme
        info0: t.Optional[T.PackageInfo]
        info1: t.Optional[T.PackageInfo]
        
        for action, pkg_name, (info0, info1) in diff['dependencies']:
            if action == 'ignore':
                continue
            
            _print_change(
                f'{action=}, {pkg_name=}',
                info0 and info0['version'],
                info1 and info1['version'],
                True,
            )
            
            if action in ('append', 'update'):
                zipped_file = _compress_dependency(info1['id'], info1['files'])
            else:
                zipped_file = None
            
            if action == 'append':
                oss.upload(
                    zipped_file, f'{oss.path.pypi}/{info1["id"]}'
                )
            elif action == 'update':
                oss.delete(f'{oss.path.pypi}/{info0["id"]}')
                oss.upload(
                    zipped_file, f'{oss.path.pypi}/{info1["id"]}'
                )
            else:  # action == 'delete'
                oss.delete(f'{oss.path.pypi}/{info0["id"]}')
    
    # -------------------------------------------------------------------------
    
    def _compress_asset(info: T.AssetInfo, relpath: str) -> T.Path:
        source_path = fs.normpath(f'{root_new}/{relpath}')
        temp_path = _copy_assets(source_path, info.scheme)
        zipped_file = _compress(
            temp_path, temp_path + ('.zip' if info.type == 'dir' else '.fzip')
        )
        return zipped_file
    
    _lib_root = get_library_root(manifest_new['start_directory'])
    
    def _compress_dependency(
        package_id: str, relpaths: t.Tuple[str, ...]
    ) -> T.Path:
        path0 = '{}/{}.zip'.format(paths.pypi.downloads, package_id)
        path1 = '{}/{}/{}'.format(paths.pypi.installed, *package_id.split('-'))
        if fs.exist(path0):
            assert fs.exist(path1)
            return path0
        
        reldirs: t.Set[str] = set()
        for p in relpaths:
            if p.startswith('../'):
                reldirs.add('bin')
            else:
                if '/' in p:
                    reldirs.add(p.rsplit('/', 1)[0])
        init_target_tree(path1, reldirs)
        
        # copy files
        for p in relpaths:
            if p.startswith('../'):
                file_i = fs.normpath('{}/{}'.format(_lib_root, p))
                file_o = '{}/bin/{}'.format(path1, fs.basename(p))
            else:
                file_i = '{}/{}'.format(_lib_root, p)
                file_o = '{}/{}'.format(path1, p)
            # note that `file_i` is from record file, which may not exist, we
            # should check its validity.
            if os.path.isfile(file_i):
                fs.copy_file(file_i, file_o)
        
        ziptool.compress_dir(path1, path0, True)
        pypi.index.update_index(package_id, path0, path1)
        return path0
    
    # -------------------------------------------------------------------------
    
    upload_assets()
    if upload_dependencies:
        upload_dependencies_()
    
    pkl_file = _save_manifest(manifest_new)
    oss.upload(pkl_file, oss.path.manifest)
    
    return oss


def _check_manifest(
    manifest_new: T.Manifest,
    manifest_old: T.Manifest,
) -> None:
    assert manifest_new['appid'] == manifest_old['appid']
    v_new, v_old = manifest_new['version'], manifest_old['version']
    assert compare_version(v_new, '>', v_old), (v_new, v_old)


def _save_manifest(manifest_new: T.Manifest) -> str:
    dump_manifest(
        manifest_new,
        out := '{}/{}/{}/manifest.pkl'.format(
            paths.project.apps,
            manifest_new['appid'],
            manifest_new['version'],
        )
    )
    return out


# -----------------------------------------------------------------------------


def _compress(path_i: T.Path, file_o: T.Path) -> T.Path:
    if file_o.endswith('.zip'):
        ziptool.compress_dir(path_i, file_o)
    else:  # file_o.endswith('.fzip'):
        fs.move(path_i, file_o)
        # ziptool.compress_file(path_i, file_o)
    return file_o


def _copy_assets(path_i: T.Path, scheme: T.Scheme) -> T.Path:
    if os.path.isdir(path_i):
        dir_o = paths.temp.make_unique_dir(fs.basename(path_i))
    else:
        file_o = '{}/{}'.format(paths.temp.make_dir(), fs.basename(path_i))
        fs.make_link(path_i, file_o)
        return file_o
    
    '''
    scheme:
        None: full copy.
        0b00: create empty root dir.
        0b01: copy direct files.
        0b10: create empty direct subdirs, copy direct files.
        0b11: create empty dirs, recursively.
    see full doc in `/wiki/topics/manifest-assets-path-forms.md`
    '''
    
    if scheme is None:
        fs.make_link(path_i, dir_o, True)
    elif scheme == 0b00:
        pass
    elif scheme == 0b01:
        for f in fs.find_files(path_i):
            file_i = f.path
            file_o = '{}/{}'.format(dir_o, f.name)
            fs.make_link(file_i, file_o)
    elif scheme == 0b10:
        for dn in fs.find_dir_names(path_i):
            os.mkdir('{}/{}'.format(dir_o, dn))
        for f in fs.find_files(path_i):
            file_i = f.path
            file_o = '{}/{}'.format(dir_o, f.name)
            fs.make_link(file_i, file_o)
    elif scheme == 0b11:
        fs.clone_tree(path_i, dir_o, True)
    else:
        raise Exception(path_i, scheme)
    
    return dir_o


def _print_change(
    title: str, old: t.AnyStr, new: t.AnyStr, show_index: bool = False
) -> None:
    """ a print info with form of '<title>: <old> -> <new>'. """
    print(
        ':psr{}'.format('i2' if show_index else ''),
        '{}: [dim]([red]{}[/] -> [green]{}[/])[/]'.format(title, old, new),
    )
