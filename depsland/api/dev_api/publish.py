import os
import typing as t
from textwrap import dedent

from lk_utils import dumps
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
from ...utils import bat_2_exe
from ...utils import compare_version
from ...utils import make_temp_dir
from ...utils import ziptool


class T:
    Manifest = T0.Manifest
    Oss = T1.Oss
    Path = str
    Scheme = T0.Scheme


def main(manifest_file: str, full_upload: bool = False) -> None:
    app_info = get_app_info(manifest_file)
    manifest = load_manifest(manifest_file)
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
        dist_dir=app_info['dst_dir'],
    )
    
    if oss.type_ in ('local', 'fake'):
        print('pack oss assets to dist dir')
        dir_o = f'{dist_dir}/.oss'
        fs.make_dirs(dir_o)
        fs.make_link(oss.path.root, dir_o, True)
        
        print('generate setup script to dist dir')
        bat_file = f'{dist_dir}/setup.bat'
        command = dedent(r'''
            cd /d %~dp0
            "%DEPSLAND%\depsland-sui.exe" launch-gui manifest.pkl
        ''').strip()
        dumps(command, bat_file)
        # noinspection PyTypeChecker
        bat_2_exe(
            bat_file,
            # icon=paths.build.launcher_ico,
            icon=manifest['launcher']['icon'] or paths.build.launcher_ico,
            show_console=False,
            remove_bat=True,
        )
    
    app_info['history'].insert(0, app_info['version'])
    dumps(
        app_info['history'],
        paths.apps.get_distribution_history(app_info['appid']),
        ftype='plain',
    )
    
    dump_manifest(manifest, f'{dist_dir}/manifest.pkl')
    #   note: this is dumped to `dist_dir`, it is different from another usage
    #   in `_upload : the bottom lines`. the latter is dumped to
    #   `appinfo['dst_dir']`, which is pointed to `paths.apps/{appid}/{version}
    #   /manifest.pkl`.
    
    print(
        'publish done. see result at "dist/{}-{}"'.format(
            manifest['appid'], manifest['version']
        ),
        ':t',
    )


def _upload(
    manifest_new: T.Manifest, manifest_old: T.Manifest, dist_dir: str
) -> T.Oss:
    # print(':lv', manifest_new, manifest_old)
    
    _check_manifest(manifest_new, manifest_old)
    _print_change(
        'updating manifest',
        manifest_old['version'],
        manifest_new['version'],
    )
    
    # -------------------------------------------------------------------------
    
    root_new = manifest_new['start_directory']
    root_old = manifest_old['start_directory']  # noqa
    temp_dir = make_temp_dir()
    
    oss = get_oss_server(manifest_new['appid'])
    print(oss.path)
    
    diff = diff_manifest(manifest_new, manifest_old)
    
    # -------------------------------------------------------------------------
    
    def upload_assets() -> None:
        for action, relpath, (info0, info1) in diff['assets']:
            if action == 'ignore':
                continue
            
            _print_change(
                f'{action = }, {relpath = }',
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
    
    def upload_dependencies() -> None:
        # `depsland.manifest.manifest._compare_dependencies`
        for (
            action,
            pkg_name,
            ((pkg_id_0, assets0), (pkg_id_1, assets1)),
        ) in diff['dependencies']:
            if action == 'ignore':
                continue
            
            _print_change(
                f'{action = }, {pkg_name = }', pkg_id_0, pkg_id_1, True
            )
            
            if action in ('append', 'update'):
                zipped_file = _compress_dependency(pkg_id_1, assets1)
            else:
                zipped_file = None
            
            if action == 'append':
                oss.upload(zipped_file, f'{oss.path.pypi}/{pkg_id_1}')
            elif action == 'update':
                oss.delete(f'{oss.path.pypi}/{pkg_id_0}')
                oss.upload(zipped_file, f'{oss.path.pypi}/{pkg_id_1}')
            else:  # action == 'delete'
                oss.delete(f'{oss.path.pypi}/{pkg_id_0}')
    
    # -------------------------------------------------------------------------
    
    def _compress_asset(info, relpath: str) -> T.Path:
        source_path = fs.normpath(f'{root_new}/{relpath}')
        temp_path = _copy_assets(source_path, temp_dir, info.scheme)
        zipped_file = _compress(
            temp_path, temp_path + ('.zip' if info.type == 'dir' else '.fzip')
        )
        return zipped_file
    
    def _compress_dependency(
        name_id: str, assets: t.Tuple[T.Path, ...]
    ) -> T.Path:
        dir0 = make_temp_dir()
        fs.make_dir(dir1 := f'{dir0}/{name_id}')
        
        root0 = os.path.commonpath(assets)
        root1 = dir1
        
        for path_i in assets:
            path_o = '{}/{}'.format(root1, fs.relpath(path_i, root0))
            fs.make_link(path_i, path_o, True)
        
        ziptool.compress_dir(root1, out := f'{dir0}/{name_id}.zip')
        return out
    
    # -------------------------------------------------------------------------
    
    upload_assets()
    upload_dependencies()
    
    print(':i0s')
    
    manifest_new['pypi'] = {k: None for k in manifest_new['pypi'].keys()}
    dump_manifest(manifest_new, x := f'{dist_dir}/manifest.pkl')
    oss.upload(x, oss.path.manifest)
    
    return oss


def _check_manifest(
    manifest_new: T.Manifest,
    manifest_old: T.Manifest,
) -> None:
    assert manifest_new['appid'] == manifest_old['appid']
    v_new, v_old = manifest_new['version'], manifest_old['version']
    assert compare_version(v_new, '>', v_old), (v_new, v_old)


# -----------------------------------------------------------------------------


def _compress(path_i: T.Path, file_o: T.Path) -> T.Path:
    if file_o.endswith('.zip'):
        ziptool.compress_dir(path_i, file_o)
    else:  # file_o.endswith('.fzip'):
        fs.move(path_i, file_o)
        # ziptool.compress_file(path_i, file_o)
    return file_o


def _copy_assets(
    path_i: T.Path, root_dir_o: T.Path, scheme: T.Scheme
) -> T.Path:
    def safe_make_dir(dirname: str) -> str:
        sub_temp_dir = make_temp_dir(root_dir_o)
        os.mkdir(out := '{}/{}'.format(sub_temp_dir, dirname))
        return out
    
    if os.path.isdir(path_i):
        dir_o = safe_make_dir(os.path.basename(path_i))
    else:
        sub_temp_dir = make_temp_dir(root_dir_o)
        file_o = '{}/{}'.format(sub_temp_dir, os.path.basename(path_i))
        fs.make_link(path_i, file_o)
        return file_o
    
    match scheme:
        case 'root':
            pass
        case 'all':
            fs.make_link(path_i, dir_o, True)
        case 'all_dirs':
            fs.clone_tree(path_i, dir_o, True)
        case 'top':
            for dn in fs.find_dir_names(path_i):
                os.mkdir('{}/{}'.format(dir_o, dn))
            for f in fs.find_files(path_i):
                file_i = f.path
                file_o = '{}/{}'.format(dir_o, f.name)
                fs.make_link(file_i, file_o)
        case 'top_files':
            for f in fs.find_files(path_i):
                file_i = f.path
                file_o = '{}/{}'.format(dir_o, f.name)
                fs.make_link(file_i, file_o)
        case 'top_dirs':
            for dn in fs.find_dir_names(path_i):
                os.mkdir('{}/{}'.format(dir_o, dn))
    
    return dir_o


def _print_change(
    title: str, old: t.AnyStr, new: t.AnyStr, show_index: bool = False
) -> None:
    print(
        ':psr{}'.format('i' if show_index else ''),
        '{}: [dim]([red]{}[/] -> [green]{}[/])[/]'.format(title, old, new),
    )
