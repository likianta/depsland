from lk_utils import dedent
from lk_utils import fs

from ... import paths
from ... import platform
from ...manifest import T
from ...manifest import diff_manifest
from ...manifest import init_manifest
from ...manifest import load_manifest
from ...venv import link_venv


def main(manifest_file: str) -> None:
    manifest = load_manifest(manifest_file)
    dir_i = manifest['start_directory']
    dir_o = '{}/dist/{}-{}'.format(
        dir_i, manifest['appid'], manifest['version']
    )
    _init_dist_tree(dir_o)
    _copy_assets(manifest, dir_o)
    _make_venv(manifest, dir_o)
    _create_launcher(manifest, dir_o)
    print('see result at {}'.format(dir_o))


def _init_dist_tree(dst_dir: str) -> None:
    """
    tree structure:
        <dist_app>
        |= source
        |= python
        |= library
        |- launcher.exe
    """
    fs.make_dir('{}'.format(dst_dir))
    # TODO: fs.make_dir('{}/library'.format(dst_dir))
    # fs.make_dir('{}/python'.format(dst_dir))
    fs.make_link(paths.project.python, '{}/python'.format(dst_dir))
    fs.make_dir('{}/source'.format(dst_dir))


def _copy_assets(manifest: T.Manifest, dst_dir: str) -> None:
    # noinspection PyTypeChecker
    diff = diff_manifest(
        new=manifest,
        old=init_manifest(manifest['appid'], manifest['name'])
    )
    
    root_i = manifest['start_directory']
    root_o = f'{dst_dir}/source'
    manifest.make_tree(root_o)
    
    # info1: T.AssetInfo
    for action, relpath, (info0, info1) in diff['assets']:
        assert action == 'append', action
        
        print(':i2s', relpath)
        path_i = f'{root_i}/{relpath}'
        path_o = f'{root_o}/{relpath}'
        
        # ref: `.publish._copy_assets : match case`
        if info1.scheme is None:
            fs.make_link(path_i, path_o, True)
        elif info1.scheme == 0b00:
            pass
        elif info1.scheme == 0b01:
            for f in fs.find_files(path_i):
                file_i = f.path
                file_o = '{}/{}'.format(path_o, f.name)
                fs.make_link(file_i, file_o)
        elif info1.scheme == 0b10:
            for dn in fs.find_dir_names(path_i):
                fs.make_dir('{}/{}'.format(path_o, dn))
            for f in fs.find_files(path_i):
                file_i = f.path
                file_o = '{}/{}'.format(path_o, f.name)
                fs.make_link(file_i, file_o)
        elif info1.scheme == 0b11:
            fs.clone_tree(path_i, path_o, True)
        else:
            raise Exception(info1.scheme)


def _make_venv(manifest: T.Manifest, dst_dir: str) -> None:
    link_venv(
        (x['id'] for x in manifest['dependencies'].values()),
        '{}/library'.format(dst_dir)
    )


def _create_launcher(manifest: T.Manifest, dst_dir: str) -> None:
    icon = manifest['launcher']['icon'] or paths.build.python_icon
    
    script = dedent(
        r'''
        @echo off
        cd /d %~dp0
        cd source
        set "PYTHONUTF8=1"
        {}
        '''.format(
            manifest['launcher']['command'].replace(
                'python', '..\\python\\python.exe', 1
            )
        )
    )
    fs.dump(script, x := '{}/{}.bat'.format(dst_dir, manifest['name']))
    platform.launcher.bat_2_exe(
        file_bat=x,
        file_exe=fs.replace_ext(x, 'exe'),
        icon=icon,
        show_console=manifest['launcher']['show_console'],
    )
    fs.remove_file(x)
    
    script = dedent(
        r'''
        cd /d %~dp0
        cd source
        set "PYTHONUTF8=1"
        {}
        pause
        '''.format(
            manifest['launcher']['command'].replace(
                'python', '..\\python\\python.exe', 1
            )
        )
    )
    fs.dump(script, x := '{}/{} (Debug).bat'.format(dst_dir, manifest['name']))
    platform.launcher.bat_2_exe(
        file_bat=x,
        file_exe=fs.replace_ext(x, 'exe'),
        icon=icon,
        show_console=True,
        # uac_admin=True,
    )
    fs.remove_file(x)
    
    if manifest['readme']:
        raise NotImplementedError
