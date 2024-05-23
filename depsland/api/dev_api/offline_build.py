"""
directory structure (example):
    dist/hello_world-0.1.0
    |- Hello World.exe
    |= source
        |= depsland
        |= apps
            |= hello_world
                |= 0.1.0
                    |= src
                        |- main.py
            |= .venv
                |= hello_world
                    |= 0.1.0
        |= python
            |- python.exe
what does "Hello World.exe" do:
    1. cd to `<curr_dir>/source`
    2. set environment `PYTHONPATH=.`
    3. run "python/python.exe -m depsland run hello_world"
        depsland will find the target's location and launch it.
"""
from lk_utils import dumps
from lk_utils import fs
from lk_utils.textwrap import dedent

from ...manifest import T
from ...manifest import diff_manifest
from ...manifest import dump_manifest
from ...manifest import init_manifest
from ...manifest import load_manifest
from ...paths import project as proj_paths
from ...platform import sysinfo
from ...platform.launcher import bat_2_exe
from ...platform.launcher import create_launcher
from ...pypi import pypi
from ...utils import init_target_tree
from ...venv import link_venv


def main(manifest_file: str) -> None:
    manifest = load_manifest(manifest_file)
    dir_i = manifest['start_directory']
    dir_o = '{}/dist/{}-{}'.format(
        dir_i, manifest['appid'], manifest['version']
    )
    _init_dist_tree(manifest, dir_o)
    _copy_assets(manifest, dir_o)
    _make_venv(manifest, dir_o)
    _relink_pypi(manifest, dir_o)
    print(':t2s', 'creating launcher...')
    _create_launcher(manifest, dir_o)
    _create_updator(manifest, dir_o)
    print(':t2', 'creating launcher done')
    print('see result at {}'.format(fs.relpath(dir_o)))


def _init_dist_tree(
    manifest: T.Manifest, dst_dir: str, pypi: str = 'least'
) -> None:
    """
    params:
        pypi: 'standard', 'least'
    """
    root_i = proj_paths.root
    root_o = dst_dir
    
    appid = manifest['appid']
    version = manifest['version']
    
    fs.make_dirs(f'{root_o}')
    fs.make_dir(f'{root_o}/source')
    fs.make_dir(f'{root_o}/source/apps')
    fs.make_dir(f'{root_o}/source/apps/.bin')
    fs.make_dir(f'{root_o}/source/apps/.venv')
    fs.make_dir(f'{root_o}/source/apps/.venv/{appid}')
    fs.make_dir(f'{root_o}/source/apps/.venv/{appid}/{version}')  # TODO
    fs.make_dir(f'{root_o}/source/apps/{appid}')
    fs.make_dir(f'{root_o}/source/apps/{appid}/{version}')
    fs.make_dir(f'{root_o}/source/build')
    # fs.make_dir(f'{root_o}/source/build/exe')
    fs.make_dir(f'{root_o}/source/config')
    # fs.make_dir(f'{root_o}/source/depsland')
    fs.make_dir(f'{root_o}/source/dist')
    fs.make_dir(f'{root_o}/source/docs')
    fs.make_dir(f'{root_o}/source/oss')
    fs.make_dir(f'{root_o}/source/oss/apps')
    fs.make_dir(f'{root_o}/source/oss/test')
    # fs.make_dir(f'{root_o}/source/pypi')
    # fs.make_dir(f'{root_o}/source/python')
    # fs.make_dir(f'{root_o}/source/sidework')
    fs.make_dir(f'{root_o}/source/temp')
    fs.make_dir(f'{root_o}/source/temp/.self_upgrade')
    fs.make_dir(f'{root_o}/source/temp/.unittests')
    
    fs.make_link(f'{root_i}/build/exe', f'{root_o}/source/build/exe')
    fs.make_link(f'{root_i}/depsland', f'{root_o}/source/depsland')
    fs.make_link(f'{root_i}/python', f'{root_o}/source/python')
    fs.make_link(f'{root_i}/sidework', f'{root_o}/source/sidework')
    
    fs.copy_file(
        f'{root_i}/.depsland_project',
        f'{root_o}/source/.depsland_project'
    )
    # TEST
    fs.copy_file(
        f'{root_i}/tests/config/depsland.yaml',
        f'{root_o}/source/config/depsland.yaml'
    )
    
    if pypi == 'least':
        # notice: do not use `fs.make_link` here. we will inflate files in it \
        # later. see `_relink_pypi`.
        fs.copy_tree(
            f'{root_i}/chore/pypi_clean',
            f'{root_o}/source/pypi'
        )
    else:
        raise NotImplementedError
    
    dumps(
        version,
        f'{root_o}/source/apps/{appid}/.inst_history',
        'plain'
    )
    dump_manifest(
        manifest,
        f'{root_o}/source/apps/{appid}/{version}/manifest.pkl'
    )


def _copy_assets(manifest: T.Manifest, dst_dir: str) -> None:
    diff = diff_manifest(
        new=manifest,
        old=init_manifest(manifest['appid'], manifest['name'])
    )
    
    root_i = manifest['start_directory']
    root_o = f'{dst_dir}/source/apps/{manifest["appid"]}/{manifest["version"]}'
    init_target_tree(manifest, root_o)
    
    # info1: T.AssetInfo
    for action, relpath, (info0, info1) in diff['assets']:
        assert action == 'append', action
        
        print(':i2s', relpath)
        path_i = f'{root_i}/{relpath}'
        path_o = f'{root_o}/{relpath}'
        
        # ref: `.publish._copy_assets : match case`
        if info1.scheme == 'all':
            fs.make_link(path_i, path_o, True)
        elif info1.scheme == 'all_dirs':
            fs.clone_tree(path_i, path_o, True)
        elif info1.scheme == 'root':
            pass
        elif info1.scheme == 'top':
            for dn in fs.find_dir_names(path_i):
                fs.make_dir('{}/{}'.format(path_o, dn))
            for f in fs.find_files(path_i):
                file_i = f.path
                file_o = '{}/{}'.format(path_o, f.name)
                fs.make_link(file_i, file_o)
        elif info1.scheme == 'top_files':
            for f in fs.find_files(path_i):
                file_i = f.path
                file_o = '{}/{}'.format(path_o, f.name)
                fs.make_link(file_i, file_o)
        elif info1.scheme == 'top_dirs':
            for dn in fs.find_dir_names(path_i):
                fs.make_dir('{}/{}'.format(path_o, dn))
        else:
            raise Exception(info1.scheme)


def _make_venv(manifest: T.Manifest, dst_dir: str) -> None:
    # TODO: make sure all required packages have been installed and indexed \
    #   pypi. see also `sidework/prepare_packages.py : preindex`.
    info: T.PackageInfo
    for info in manifest['dependencies'].values():
        if not pypi.exists(id := info['id']):
            print('add missing package', id, ':v3s')
            pypi.install_one(
                id, pypi.download_one(
                    id, info['appendix'].get('custom_url')
                )
            )
    # assert all(pypi.exists(x['id']) for x in manifest['dependencies'].values())
    link_venv(
        (x['id'] for x in manifest['dependencies'].values()),
        '{}/source/apps/.venv/{}/{}'.format(
            dst_dir, manifest['appid'], manifest['version']
        )
    )


def _relink_pypi(manifest: T.Manifest, dst_dir: str) -> None:
    info: T.PackageInfo
    for name, info in manifest['dependencies'].items():
        fs.make_dir(
            '{}/source/pypi/installed/{}'.format(dst_dir, name)
        )
        fs.make_link(
            pypi.index[info['id']][1],
            '{}/source/pypi/installed/{}/{}'.format(
                dst_dir, name, info['version']
            )
        )
    # save index
    name_2_ids = {
        k: pypi.index.name_2_ids[k]
        for k in manifest['dependencies'].keys()
    }
    id_2_paths = {
        v['id']: pypi.index.id_2_paths[v['id']]
        for v in manifest['dependencies'].values()
    }
    dumps(name_2_ids, f'{dst_dir}/source/pypi/index/name_2_ids.pkl')
    dumps(id_2_paths, f'{dst_dir}/source/pypi/index/id_2_paths.pkl')


def _create_launcher(manifest: T.Manifest, dst_dir: str) -> None:
    create_launcher(manifest, dir_o=dst_dir)
    if sysinfo.SYSTEM == 'windows':
        create_launcher(
            manifest,
            dir_o=dst_dir,
            name=manifest['name'] + ' (Debug).exe',
            debug=True,
            # keep_bat=True,  # TEST
            # uac_admin=True,
        )


def _create_updator(manifest: T.Manifest, dst_dir: str) -> None:  # TODO
    if sysinfo.SYSTEM == 'darwin' or sysinfo.SYSTEM == 'linux':
        file_sh = f'{dst_dir}/Check Updates.sh'
        template = dedent('''
            # cd to current dir
            # https://stackoverflow.com/a/246128
            CURR_DIR=$( cd -- "$( dirname -- "${{BASH_SOURCE[0]}}" )" &> \\
            /dev/null && pwd )
            cd $CURR_DIR/source
            
            export PYTHONPATH=.
            python/bin/python3 -m depsland launch-gui {appid}
        ''', join_sep='\\')
        script = template.format(appid=manifest['appid'])
        dumps(script, file_sh)
    
    elif sysinfo.SYSTEM == 'windows':
        file_bat = f'{dst_dir}/Check Updates.bat'
        file_exe = f'{dst_dir}/Check Updates.exe'
        template = dedent(r'''
            @echo off
            cd /d %~dp0
            cd source
            set PYTHONPATH=.
            .\python\python.exe -m depsland launch-gui {appid}
        ''')
        script = template.format(appid=manifest['appid'])
        dumps(script, file_bat)
        bat_2_exe(
            file_bat,
            file_exe,
            icon=(
                (x := manifest['launcher']['icon']) and
                '{}/{}'.format(manifest.start_directory, x) or ''
            ),
            show_console=True,
            # show_console=False,
            uac_admin=True,
        )
        fs.remove_file(file_bat)
