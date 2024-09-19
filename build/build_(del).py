import os
from os.path import exists

from argsense import cli
from lk_utils import fs

import depsland
from depsland import __version__ as depsland_version
from depsland import bat_2_exe as _b2e
from depsland import paths
from depsland.manifest import dump_manifest
from depsland.manifest import load_manifest
from depsland.utils import make_temp_dir
from depsland.utils import ziptool

print(':v2', f'depsland version: {depsland_version}')


@cli.cmd()  # DELETE
def backup_project_resources() -> None:
    """
    generate/refresh `depsland/chore/*.zip`.
    if you find the following folders have been changed, you need to call this -
    function:
        - build
        - config
        - sidework
    """
    compress_dir = ziptool.compress_dir
    
    dir_i = paths.project.root
    dir_m = make_temp_dir()
    dir_o = paths.project.depsland + '/chore'
    assert exists(dir_o)
    
    def copy_build_dir() -> None:
        fs.make_dir(f'{dir_m}/build')
        
        fs.copy_tree(f'{dir_i}/build/.assets',
                     f'{dir_m}/build/.assets')
        fs.copy_tree(f'{dir_i}/build/exe',
                     f'{dir_m}/build/exe')
        fs.copy_tree(f'{dir_i}/build/icon',
                     f'{dir_m}/build/icon')
        # fs.copy_tree(f'{dir_i}/build/setup_wizard',  # DELETE
        #              f'{dir_m}/build/setup_wizard')
        
        fs.copy_file(f'{dir_i}/build/build.py',
                     f'{dir_m}/build/build.py')
        fs.copy_file(f'{dir_i}/build/init.py',
                     f'{dir_m}/build/init.py')
        # fs.copy_file(f'{dir_i}/build/depsland_setup.py',  # DELETE
        #              f'{dir_m}/build/depsland_setup.py')
        # fs.copy_file(f'{dir_i}/build/readme.zh.md',
        #              f'{dir_m}/build/readme.zh.md')
        compress_dir(f'{dir_m}/build',
                     f'{dir_o}/build.zip', True)
    
    def copy_config_dir() -> None:
        # make sure config/depsland.yaml has configured local oss.
        assert fs.load(f'{dir_i}/config/depsland.yaml')['oss']['server'] == 'local'
        fs.copy_file(f'{dir_i}/config/depsland.yaml', f'{dir_m}/depsland.yaml')
        compress_dir(f'{dir_m}/depsland.yaml', f'{dir_o}/config.zip', True)
    
    def copy_sidework_dir() -> None:
        fs.make_dir(f'{dir_m}/sidework')
        for f in fs.find_files(f'{dir_i}/sidework'):
            i = f.path
            o = f'{dir_m}/sidework/{f.name}'
            fs.copy_file(i, o)
        compress_dir(f'{dir_m}/sidework', f'{dir_o}/sidework.zip', True)
    
    copy_build_dir()
    copy_config_dir()
    copy_sidework_dir()


@cli.cmd()
def build_depsland_standalone(
    oss_scheme: str,
    pypi_scheme: str = 'blank',
    _add_python_sdk: bool = True,
    _new_version: str = 'auto_bump',
) -> None:
    """
    generate `dist/standalone/depsland-<version>`.
    
    args:
        oss_scheme: 'aliyun' or 'local'
            - 'aliyun': you need to prepare a file named -
            'config/depsland_for_dev.yaml', which contains aliyun oss access -
            key and secret key.
    kwargs:
        pypi_scheme (-p): 'full', 'blank'
            - full: link `<proj>/pypi` to `<dist>/pypi`.
            - blank: copy `<proj>/chore/pypi_blank` to `<dist>/pypi`.
            what's the difference?
                'full' is used for local test.
                'blank' is used for production release, it has a minified -
                size.
                if you want to partially release, or try to package a minimal -
                version, use `pypi_scheme='blank'` with `_add_python_sdk=False`.
    """
    if fs.exists('depsland/.project'):
        raise Exception('please remove "depsland/.project" to continue.')
    
    # checks
    if oss_scheme == 'aliyun':
        assert exists(os.getenv('DEPSLAND_CONFIG_ROOT'))
    
    root_i = paths.project.root
    root_o = (
        '{dist}/standalone/depsland-{version}-windows/depsland/{version}'
        .format(dist=paths.project.dist, version=depsland_version)
    )
    # ^ see design note in `wiki/design-tkinking/why-does-dist-standalone-
    #   directory-like-this.md`
    assert not exists(
        '{dist}/standalone/depsland-{version}-windows'
        .format(dist=paths.project.dist, version=depsland_version)
    )
    fs.make_dirs(root_o)
    
    # -------------------------------------------------------------------------
    
    # make empty dirs
    os.mkdir(f'{root_o}/apps')
    os.mkdir(f'{root_o}/apps/.bin')
    os.mkdir(f'{root_o}/apps/.venv')
    os.mkdir(f'{root_o}/build')
    os.mkdir(f'{root_o}/chore')
    os.mkdir(f'{root_o}/config')
    # os.mkdir(f'{root_o}/depsland')
    os.mkdir(f'{root_o}/dist')
    os.mkdir(f'{root_o}/docs')
    os.mkdir(f'{root_o}/oss')
    os.mkdir(f'{root_o}/oss/apps')
    os.mkdir(f'{root_o}/oss/test')
    # os.mkdir(f'{root_o}/pypi')
    # os.mkdir(f'{root_o}/python')
    # os.mkdir(f'{root_o}/sidework')
    os.mkdir(f'{root_o}/temp')
    os.mkdir(f'{root_o}/temp/.self_upgrade')
    os.mkdir(f'{root_o}/temp/.unittests')
    
    # -------------------------------------------------------------------------
    
    # copy files and folders
    fs.make_link(
        f'{root_i}/build/exe',
        f'{root_o}/build/exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-cli.exe',
        f'{root_o}/apps/.bin/depsland.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui.exe',
        f'{root_o}/Depsland.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui-debug.exe',
        f'{root_o}/Depsland (Debug).exe',
    )
    fs.make_link(
        f'{root_i}/build/icon',
        f'{root_o}/build/icon',
    )
    # fs.copy_tree(
    #     f'{root_i}/build/setup_wizard',
    #     f'{root_o}/build/setup_wizard',
    # )
    fs.make_link(
        f'{root_i}/chore/pypi_blank',
        f'{root_o}/chore/pypi_blank',
    )
    # fs.copy_tree(
    #     f'{root_i}/depsland',
    #     f'{root_o}/depsland',
    # )
    fs.make_link(
        f'{root_i}/depsland',
        f'{root_o}/depsland',
    )
    fs.copy_tree(
        f'{root_i}/sidework',
        f'{root_o}/sidework',
    )
    # fs.copy_file(
    #     f'{root_i}/.depsland_project.json',
    #     f'{root_o}/.depsland_project.json',
    # )
    
    fs.dump(
        {'project_mode': 'production', 'depsland_version': depsland_version},
        f'{root_o}/.depsland_project.json'
    )
    
    if oss_scheme == 'aliyun':
        # assert exists(custom := os.getenv('DEPSLAND_CONFIG_ROOT'))
        custom = os.getenv('DEPSLAND_CONFIG_ROOT')
        assert (
            fs.load(f'{custom}/depsland.yaml')
            ['oss']['server'] == 'aliyun'
        )
        fs.copy_file(
            f'{custom}/depsland.yaml',
            f'{root_o}/config/depsland.yaml',
        )
    else:
        assert (
            fs.load(f'{root_i}/config/depsland.yaml')
            ['oss']['server'] == 'local'
        )
        fs.copy_file(
            f'{root_i}/config/depsland.yaml',
            f'{root_o}/config/depsland.yaml',
        )
    
    if pypi_scheme == 'full':
        fs.make_link(f'{root_i}/pypi', f'{root_o}/pypi')
    else:  # 'blank'
        fs.copy_tree(f'{root_i}/chore/pypi_blank', f'{root_o}/pypi')
    
    if _add_python_sdk:
        # fs.make_link(
        #     f'{root_i}/chore/site_packages',
        #     f'{root_o}/chore/site_packages',
        # )
        fs.make_link(
            f'{root_i}/chore/minified_site_packages',
            f'{root_o}/chore/site_packages',
        )
        fs.make_link(
            f'{root_i}/python',
            f'{root_o}/python',
        )
    
    # -------------------------------------------------------------------------
    
    # dump manifest
    dump_manifest(
        load_manifest(f'{root_i}/manifest.json'),
        f'{root_o}/manifest.pkl',
    )
    
    print(':t', 'see result at ' + fs.relpath(root_o))


@cli.cmd()
def bat_2_exe(
    file_i: str,
    show_console: bool = True,
    uac_admin: bool = False,
    icon: str = fs.xpath('exe/launcher.ico'),
) -> None:
    """
    args:
        file_i: the file is ".bat" file, which is under ~/build/exe folder.
    
    kwargs:
        show_console (-c):
        uac_admin (-u):
    """
    _b2e(
        file_bat=file_i,
        file_exe=fs.replace_ext(file_i, 'exe'),
        icon=icon,
        show_console=show_console,
        uac_admin=uac_admin,
    )


@cli.cmd()
def compress_to_zip():
    dir_i = '{}/{}'.format(paths.project.dist, f'depsland-{depsland_version}')
    file_o = '{}/{}'.format(paths.project.dist, f'depsland-{depsland_version}.zip')
    ziptool.compress_dir(dir_i, file_o, overwrite=True)
    print(':t', 'see result at', fs.relpath(file_o))


if __name__ == '__main__':
    # create/refresh depsland launchers:
    #   pox build/build.py bat-2-exe build/exe/depsland-cli.bat
    #   pox build/build.py bat-2-exe build/exe/depsland-gui.bat -C -u
    #   pox build/build.py bat-2-exe build/exe/depsland-gui-debug.bat -u
    #   pox build/build.py bat-2-exe build/exe/depsland-runapp.bat -C --icon
    #       build/icon/python.ico
    #   pox build/build.py bat-2-exe build/exe/depsland-runapp-console.bat
    #       --icon build/icon/python.ico
    #   pox build/build.py bat-2-exe build/exe/depsland-runapp-debug.bat -u
    #       --icon build/icon/python.ico
    
    # pox build/build.py backup-project-resources
    
    # pox build/build.py build-depsland-standalone aliyun
    #   prerequisites:
    #       1. set environment variable:
    #           $env.DEPSLAND_CONFIG_ROOT = 'tests/config'
    #       2. make sure poetry.lock is synced to 'chore/site_packages' and
    #       'chore/minified_site_packages'
    #           see also:
    #               sidework/merge_external_venv_to_local_pypi.py
    #               build/init.py : make_site_packages
    #               build/init.py : make_minified_site_packages
    #               <tree_shaking_project>/examples/depsland_modules.yaml
    cli.run()
