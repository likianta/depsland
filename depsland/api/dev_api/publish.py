import os

from lk_utils import dumps
from lk_utils import fs

from ... import paths
from ...manifest import T as T0
from ...manifest import compare_manifests
from ...manifest import dump_manifest
from ...manifest import get_app_info
from ...manifest import init_manifest
from ...manifest import load_manifest
from ...oss import T as T1
from ...oss import get_oss_server
from ...utils import compare_version
from ...utils import make_temp_dir
from ...utils import ziptool


class T:
    Manifest = T0.Manifest
    Oss = T1.Oss
    Path = str
    Scheme = T0.Scheme1


def main(manifest_file: str) -> None:
    appinfo = get_app_info(manifest_file)
    
    oss = _upload(
        manifest_new=(m := load_manifest(manifest_file)),
        manifest_old=(
            load_manifest('{}/{}/{}/manifest.pkl'.format(
                paths.Project.apps,
                appinfo['appid'],
                appinfo['history'][0]
            )) if appinfo['history'] else
            init_manifest(
                appinfo['appid'], appinfo['name']
            )
        ),
        dist_dir=appinfo['dst_dir']
    )
    
    if oss.type_ in ('local', 'fake'):
        print('pack oss assets to dist dir')
        dir_o = '{root}/dist/{name}-{ver}/.oss'.format(
            root=m['start_directory'],
            name=m['appid'],
            ver=m['version'],
        )
        fs.make_dirs(dir_o)
        fs.make_link(oss.path.root, dir_o, True)
    
    appinfo['history'].insert(0, appinfo['version'])
    dumps(appinfo['history'], paths.apps.get_history_versions(appinfo['appid']))
    
    print('publish done. see result at {}/dist/{}-{}'.format(
        fs.relpath(m['start_directory']), m['appid'], m['version']
    ), ':t')


def _upload(
        manifest_new: T.Manifest,
        manifest_old: T.Manifest,
        dist_dir: str
) -> T.Oss:
    print(':lv', manifest_new, manifest_old)
    
    _check_manifest(manifest_new, manifest_old)
    print('updating manifest: [red]{}[/] -> [green]{}[/]'.format(
        manifest_old['version'], manifest_new['version']
    ), ':r')
    
    # -------------------------------------------------------------------------
    
    root_new = manifest_new['start_directory']
    root_old = manifest_old['start_directory']  # noqa
    temp_dir = make_temp_dir()
    
    oss = get_oss_server(manifest_new['appid'])
    print(oss.path)
    
    diff = compare_manifests(manifest_new, manifest_old)
    
    # -------------------------------------------------------------------------
    
    for action, relpath, (info0, info1) in diff['assets']:
        if action == 'ignore':
            continue
        print(
            ':sri', action, relpath,
            '[dim]([red]{}[/] -> [green]{}[/])[/]'.format(
                info0 and info0.uid,
                info1 and info1.uid,
            )
        )
        
        if info1 is not None:  # i.e. action != 'delete'
            source_path = f'{root_new}/{relpath}'
            temp_path = _copy_assets(source_path, temp_dir, info1.scheme)
            zipped_file = _compress(temp_path, temp_path + (
                '.zip' if info1.type == 'dir' else '.fzip'
            ))
        else:
            zipped_file = ''
        
        match action:
            case 'append':
                oss.upload(zipped_file, f'{oss.path.assets}/{info1.uid}')
            case 'update':
                # delete old, upload new.
                oss.delete(f'{oss.path.assets}/{info0.uid}')
                oss.upload(zipped_file, f'{oss.path.assets}/{info1.uid}')
            case 'delete':
                oss.delete(f'{oss.path.assets}/{info0.uid}')
    
    # for action, (name, verspec) in diff['dependencies']:
    #     pass
    
    for action, (whl_name, whl_file) in diff['pypi']:
        if action == 'ignore':
            continue
        print(':sri', action, '[{}]{}[/]'.format(
            'green' if action == 'append' else 'red',
            whl_name
        ))
        match action:
            case 'append':
                oss.upload(whl_file, f'{oss.path.pypi}/{whl_name}')
            case 'delete':
                oss.delete(f'{oss.path.pypi}/{whl_name}')
    print(':i0s')
    
    manifest_new['pypi'] = {k: None for k in manifest_new['pypi'].keys()}
    dump_manifest(manifest_new, x := f'{dist_dir}/manifest.pkl')
    oss.upload(x, oss.path.manifest)
    
    return oss


def _check_manifest(
        manifest_new: T.Manifest, manifest_old: T.Manifest,
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
        path_i: T.Path,
        root_dir_o: T.Path,
        scheme: T.Scheme
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