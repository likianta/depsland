"""
directory structure (example):
    dist/hello_world-0.1.0
    |- Hello World.exe
    |= source
        |= depsland
        |= apps
            |= hello_world
                |= 0.1.0
                    |= .venv
                    |= src
                        |- main.py
        |= python
            |- python.exe
what does "Hello World.exe" do:
    1. cd to `<curr_dir>/source`
    2. set environment `PYTHONPATH=.`
    3. run "python/python.exe -m depsland run hello_world"
        depsland will find the target's location and launch it.
"""
from lk_utils import dedent
from lk_utils import fs

from ... import paths
from ...manifest import T
from ...manifest import diff_manifest
from ...manifest import dump_manifest
from ...manifest import init_manifest
from ...manifest import load_manifest
from ...platform import sysinfo
from ...platform.launcher import bat_2_exe
from ...platform.launcher import create_launcher
from ...pypi import pypi
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
    # with lk_logger.spinner('creating launcher...'):
    _create_launcher(manifest, dir_o)
    _create_updator(manifest, dir_o)
    print('see result at {}'.format(dir_o))


def _init_dist_tree(manifest: T.Manifest, dst_dir: str) -> None:
    """
    params:
        pypi: 'standard', 'least'
    """
    from ... import __version__
    
    root_i = paths.project.root
    root_o = dst_dir
    
    appid = manifest['appid']
    version = manifest['version']
    
    # ref: build/build.py:full_build
    fs.make_dirs(f'{root_o}')
    fs.make_dir(f'{root_o}/source')
    fs.make_dir(f'{root_o}/source/apps')
    fs.make_dir(f'{root_o}/source/apps/.bin')
    fs.make_dir(f'{root_o}/source/apps/{appid}')
    fs.make_dir(f'{root_o}/source/apps/{appid}/{version}')
    fs.make_dir(f'{root_o}/source/build')
    # fs.make_dir(f'{root_o}/source/build/exe')
    fs.make_dir(f'{root_o}/source/chore')
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
    
    fs.make_link(
        f'{root_i}/build/exe',
        f'{root_o}/source/build/exe'
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-cli.exe',
        f'{root_o}/source/apps/.bin/depsland.exe'
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui.exe',
        f'{root_o}/source/Depsland.exe'
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui-debug.exe',
        f'{root_o}/source/Depsland (Debug).exe'
    )
    fs.make_link(
        f'{root_i}/build/icon',
        f'{root_o}/source/build/icon'
    )
    fs.make_link(
        f'{root_i}/chore/pypi_blank',
        f'{root_o}/source/chore/pypi_blank'
    )
    fs.copy_tree(
        f'{root_i}/chore/pypi_blank',
        f'{root_o}/source/pypi'
    )
    fs.make_link(  # TEST
        f'{root_i}/chore/setup_wizard_logo.png',
        f'{root_o}/source/chore/setup_wizard_logo.png',
    )
    fs.make_link(
        f'{root_i}/chore/site_packages',
        f'{root_o}/source/chore/site_packages'
    )
    fs.make_link(
        f'{root_i}/depsland',
        f'{root_o}/source/depsland'
    )
    fs.make_link(
        f'{root_i}/python',
        f'{root_o}/source/python'
    )
    # fs.make_link(
    #     f'{root_i}/sidework',
    #     f'{root_o}/source/sidework'
    # )
    # TEST
    fs.copy_file(
        f'{root_i}/test/_config/depsland.yaml',
        f'{root_o}/source/config/depsland.yaml'
    )
    
    fs.dump(
        {
            'project_mode': 'shipboard',
            'depsland_version': __version__,
            'unblock_dlls': True,
        },
        f'{root_o}/source/.depsland_project.json'
    )
    fs.dump(
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
    """
    TODO: make sure all required packages have already been installed and
        indexed in pypi. see also `sidework/merge_external_venv_to_local_pypi
        .py`
    """
    # assert all(pypi.exists(x['id']) for x in manifest['dependencies'].values())
    link_venv(
        (x['id'] for x in manifest['dependencies'].values()),
        '{}/source/apps/{}/{}/.venv'.format(
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
    id_2_paths = {
        v['id']: pypi.index.id_2_paths[v['id']]
        for v in manifest['dependencies'].values()
    }
    name_2_vers = {
        v['name']: [v['version']]
        for v in manifest['dependencies'].values()
    }
    fs.dump(id_2_paths, f'{dst_dir}/source/pypi/index/id_2_paths.json')
    fs.dump(name_2_vers, f'{dst_dir}/source/pypi/index/name_2_vers.json')


def _create_launcher(manifest: T.Manifest, dst_dir: str) -> None:
    icon = manifest['launcher']['icon'] or paths.build.python_icon
    create_launcher(manifest, dir_o=dst_dir, icon=icon, custom_cd='cd source')
    if sysinfo.SYSTEM == 'windows':
        create_launcher(
            manifest,
            dir_o=dst_dir,
            name=manifest['name'] + ' (Debug).exe',
            debug=True,
            icon=icon,
            # keep_bat=True,
            # uac_admin=True,
            custom_cd='cd source',
        )
    if manifest['readme']:
        # if x['standalone']:
        #     fs.make_link(
        #         manifest['readme']['file'],
        #         '{}/{}.{}'.format(
        #             dst_dir,
        #             manifest['readme']['name'],
        #             manifest['readme']['file'].rsplit('.', 1)[-1]
        #         )
        #     )
        # else:
        #     create_readme_opener(manifest, dst_dir)
        create_readme_opener(manifest, dst_dir)


def create_readme_opener(
    manifest: T.PseudoManifestDict, dst_dir: T.AbsPath
) -> T.AbsPath:
    fs.dump(
        dedent(
            '''
            @echo off
            cd /d %~dp0
            cd source
            set "PYTHONPATH=.;chore/site_packages"
            set "PYTHONUTF8=1"
            .\\python\\python.exe -m depsland open_readme {appid}
            '''.format(appid=manifest['appid'])
        ),
        x := '{}/open_readme.bat'.format(paths.temp.root)
    )
    bat_2_exe(
        file_bat=x,
        file_exe=(y := '{}/{}.exe'.format(dst_dir, manifest['readme']['name'])),
        icon=manifest['readme']['icon'] or paths.build.help_icon,
        show_console=False,
    )
    return y


def _create_updator(manifest: T.Manifest, dst_dir: str) -> None:  # TODO
    if sysinfo.SYSTEM == 'darwin' or sysinfo.SYSTEM == 'linux':
        file_sh = f'{dst_dir}/Check Updates.sh'
        template = dedent(
            '''
            # cd to current dir
            # https://stackoverflow.com/a/246128
            CURR_DIR=$( cd -- "$( dirname -- "${{BASH_SOURCE[0]}}" )" &> \\
            /dev/null && pwd )
            cd $CURR_DIR/source
            
            export PYTHONPATH=.
            python/bin/python3 -m depsland launch-gui {appid}
            ''',
            join_sep='\\'
        )
        script = template.format(appid=manifest['appid'])
        fs.dump(script, file_sh)
    
    elif sysinfo.SYSTEM == 'windows':
        file_bat = f'{dst_dir}/Check Updates.bat'
        file_exe = f'{dst_dir}/Check Updates.exe'
        template = dedent(
            r'''
            @echo off
            cd /d %~dp0
            cd source
            set "PYTHONPATH=.;chore/site_packages"
            set "PYTHONUTF8=1"
            .\python\python.exe -m depsland launch-gui --app-token {appid}
            '''
        )
        script = template.format(appid=manifest['appid'])
        fs.dump(script, file_bat)
        bat_2_exe(
            file_bat,
            file_exe,
            icon=manifest['launcher']['icon'] or paths.build.launcher_icon,
            show_console=False,
            # show_console=False,
            uac_admin=True,
        )
        fs.remove_file(file_bat)
