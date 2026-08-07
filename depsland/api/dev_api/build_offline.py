"""
directory structure (example):
    <depsland_project>
    └── dist
        └── hello_world-0.1.0
            ├── source
            │   ├── apps
            │   │   └── hello_world
            │   │       └── 0.1.0
            │   │           ├── .venv
            │   │           └── src
            │   │               └── main.py
            │   ├── depsland
            │   └── python
            │       ├── python.exe
            │       └── ...
            ├── Hello World.exe
            └── Hello World (Debug).exe

what does "Hello World.exe" do:
    1. cd to `<curr_dir>/source`
    2. set environment variables
    3. run `python/python.exe -m depsland run hello_world`
        depsland will find the target's location and launch it.
"""

import typing as tp
from functools import partial

from lk_utils import dedent
from lk_utils import fs

from ... import paths
from ... import platform
from ...manifest import T as T0
from ...manifest import diff_manifest
from ...manifest import dump_manifest
from ...manifest import init_manifest
from ...manifest import load_manifest
from ...platform import sysinfo
from ...pypi import pypi
from ...venv import link_venv


class T(T0):
    DistributionKeyPaths = tp.TypedDict(
        'DistributionKeyPaths',
        {'dst_app_root': T0.AbsPath, 'dst_app_venv': T0.AbsPath},
    )


def build_offline(manifest_file: str, embed_depsland_engine: bool = False) -> str:
    manifest = load_manifest(manifest_file)
    dir_i = manifest['start_directory']
    dir_o = '{}/dist/{}-{}'.format(
        dir_i, manifest['appid'], manifest['version']
    )
    if embed_depsland_engine:
        dst_paths = _init_dist_tree_full(manifest, dir_o)
    else:
        dst_paths = _init_dist_tree_lite(dir_o)
    _copy_assets(manifest, dst_paths['dst_app_root'])
    _make_venv(manifest, dst_paths['dst_app_venv'])
    if embed_depsland_engine:
        _relink_pypi(manifest, dir_o)
    if embed_depsland_engine:
        _create_launcher(manifest, dir_o)
        if manifest['readme']:
            create_readme_opener(manifest, dir_o)
        _create_updator(manifest, dir_o)
    else:
        _create_launcher(manifest, dir_o)
        # TODO: no-depsland mode does not support creating readme opener yet.
        dump_manifest(
            manifest,
            '{}/source/.depsland/manifest.pkl'.format(dir_o),
            erase_sensitive_data=True,
        )
    print('see result at "{}"'.format(dir_o), ':v4t')
    return dir_o


build_stripped_offline = partial(build_offline, embed_depsland_engine=False)


def _init_dist_tree_full(
    manifest: T.Manifest, dst_dir: str
) -> T.DistributionKeyPaths:
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

    fs.make_link(f'{root_i}/build/exe', f'{root_o}/source/build/exe')
    fs.copy_file(
        f'{root_i}/build/exe/depsland-cli.exe',
        f'{root_o}/source/apps/.bin/depsland.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui.exe', f'{root_o}/source/Depsland.exe'
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui-debug.exe',
        f'{root_o}/source/Depsland (Debug).exe',
    )
    fs.make_link(f'{root_i}/build/icon', f'{root_o}/source/build/icon')
    fs.make_link(
        f'{root_i}/chore/pypi_blank', f'{root_o}/source/chore/pypi_blank'
    )
    fs.copy_tree(f'{root_i}/chore/pypi_blank', f'{root_o}/source/pypi')
    fs.make_link(  # TEST
        f'{root_i}/chore/setup_wizard_logo.png',
        f'{root_o}/source/chore/setup_wizard_logo.png',
    )
    fs.make_link(
        f'{root_i}/chore/site_packages', f'{root_o}/source/chore/site_packages'
    )
    fs.make_link(f'{root_i}/depsland', f'{root_o}/source/depsland')
    fs.make_link(f'{root_i}/python', f'{root_o}/source/python')
    # fs.make_link(
    #     f'{root_i}/sidework',
    #     f'{root_o}/source/sidework'
    # )
    # TEST
    fs.copy_file(
        f'{root_i}/test/_config/depsland.yaml',
        f'{root_o}/source/config/depsland.yaml',
    )

    fs.dump(
        {
            'project_mode': 'shipboard',
            'depsland_version': __version__,
            'unblock_dlls': True,
        },
        f'{root_o}/source/.depsland_project.json',
    )
    fs.dump(version, f'{root_o}/source/apps/{appid}/.inst_history', 'plain')
    dump_manifest(
        tp.cast(T.ManifestObject, manifest),
        f'{root_o}/source/apps/{appid}/{version}/manifest.pkl',
    )

    return {
        'dst_app_root': f'{root_o}/source/apps/{appid}/{version}',
        'dst_app_venv': f'{root_o}/source/apps/{appid}/{version}/.venv',
    }


def _init_dist_tree_lite(dst_dir: T.AbsPath) -> T.DistributionKeyPaths:
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
    return {
        'dst_app_root': f'{dst_dir}/source',
        'dst_app_venv': f'{dst_dir}/library',
    }


def _copy_assets(manifest: T.Manifest, dir_o: T.AbsPath) -> None:
    diff = diff_manifest(
        new=manifest, old=init_manifest(manifest['appid'], manifest['name'])
    )

    root_i = manifest['start_directory']
    root_o = dir_o
    manifest.make_tree(root_o)

    # info1: T.AssetInfo
    for action, (relpath, real_relpath), (info0, info1) in diff['assets']:
        assert action == 'append', action

        print(':i2s', relpath)
        path_i = f'{root_i}/{real_relpath}'
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


def _make_venv(manifest: T.Manifest, dir_o: T.AbsPath) -> None:
    link_venv((x['id'] for x in manifest['dependencies'].values()), dir_o)


def _relink_pypi(manifest: T.Manifest, dst_dir: T.AbsPath) -> None:
    info: T.PackageInfo
    for name, info in manifest['dependencies'].items():
        fs.make_dir('{}/source/pypi/installed/{}'.format(dst_dir, name))
        fs.make_link(
            pypi.index[info['id']][1],
            '{}/source/pypi/installed/{}/{}'.format(
                dst_dir, name, info['version']
            ),
        )
    # save index
    id_2_paths = {
        v['id']: pypi.index.id_2_paths[v['id']]
        for v in manifest['dependencies'].values()
    }
    name_2_vers = {
        v['name']: [v['version']] for v in manifest['dependencies'].values()
    }
    fs.dump(id_2_paths, f'{dst_dir}/source/pypi/index/id_2_paths.json')
    fs.dump(name_2_vers, f'{dst_dir}/source/pypi/index/name_2_vers.json')


def _create_launcher(manifest: T.Manifest, dst_dir: T.AbsPath) -> None:
    icon = manifest['launcher']['icon'] or paths.build.python_icon

    # default launcher
    script = dedent(
        """
        @echo off
        cd /d %~dp0
        cd source
        set "PYTHONUTF8=1"
        {}
        """.format(
            manifest['launcher']['command']
            .replace('python', '..\\python\\python.exe', 1)
            .replace("'", '"')
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

    # debug launcher
    script = dedent(
        """
        cd /d %~dp0
        cd source
        set "PYTHONUTF8=1"
        {}
        pause
        """.format(
            manifest['launcher']['command']
            .replace('python', '..\\python\\python.exe', 1)
            .replace("'", '"')
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


def create_readme_opener(manifest: T.Manifest, dst_dir: T.AbsPath) -> T.AbsPath:
    fs.dump(
        dedent(
            """
            @echo off
            cd /d %~dp0
            cd source
            set "PYTHONPATH=.;chore/site_packages"
            set "PYTHONUTF8=1"
            .\\python\\python.exe -m depsland open_readme {appid}
            """.format(appid=manifest['appid'])
        ),
        x := '{}/open_readme.bat'.format(paths.temp.root),
    )
    platform.launcher.bat_2_exe(
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
            """
            # cd to current dir
            # https://stackoverflow.com/a/246128
            CURR_DIR=$( cd -- "$( dirname -- "${{BASH_SOURCE[0]}}" )" &> \\
            /dev/null && pwd )
            cd $CURR_DIR/source
            
            export PYTHONPATH=.
            python/bin/python3 -m depsland launch-gui {appid}
            """,
            join_sep='\\',
        )
        script = template.format(appid=manifest['appid'])
        fs.dump(script, file_sh)

    elif sysinfo.SYSTEM == 'windows':
        file_bat = f'{dst_dir}/Check Updates.bat'
        file_exe = f'{dst_dir}/Check Updates.exe'
        template = dedent(
            r"""
            @echo off
            cd /d %~dp0
            cd source
            set "PYTHONPATH=.;chore/site_packages"
            set "PYTHONUTF8=1"
            .\python\python.exe -m depsland launch-gui --app-token {appid}
            """
        )
        script = template.format(appid=manifest['appid'])
        fs.dump(script, file_bat)
        platform.launcher.bat_2_exe(
            file_bat,
            file_exe,
            icon=manifest['launcher']['icon'] or paths.build.launcher_icon,
            show_console=False,
            # show_console=False,
            uac_admin=True,
        )
        fs.remove_file(file_bat)
