"""
py build/build.py full-build aliyun
py build/build.py full-build local
"""
import os
from os.path import exists

from argsense import cli
from lk_utils import fs
from lk_utils import loads
from lk_utils import xpath

os.chdir(xpath('..'))
os.environ['DEPSLAND_PYPI_ROOT'] = 'chore/pypi_self'

from depsland import __version__
from depsland import bat_2_exe as _b2e
from depsland import paths
from depsland.manifest import dump_manifest
from depsland.manifest import load_manifest
from depsland.utils import make_temp_dir
from depsland.utils import ziptool

print(':v2', f'depsland version: {__version__}')


@cli.cmd()
def self_check() -> bool:
    ver0 = __version__
    ver1 = loads('manifest.json')['version']
    ver2 = loads('pyproject.toml')['tool']['poetry']['version']
    if not (ver0 == ver1 == ver2):
        print('version is not consistent', (ver0, ver1, ver2), ':v3')
        return False
    return True


@cli.cmd()
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
        fs.copy_tree(f'{dir_i}/build/setup_wizard',
                     f'{dir_m}/build/setup_wizard')
        
        fs.copy_file(f'{dir_i}/build/backup_project_resources.py',
                     f'{dir_m}/build/backup_project_resources.py')
        fs.copy_file(f'{dir_i}/build/build.py',
                     f'{dir_m}/build/build.py')
        fs.copy_file(f'{dir_i}/build/depsland_setup.py',
                     f'{dir_m}/build/depsland_setup.py')
        fs.copy_file(f'{dir_i}/build/init.py',
                     f'{dir_m}/build/init.py')
        # DELETE: about to remove
        fs.copy_file(f'{dir_i}/build/readme.zh.md',
                     f'{dir_m}/build/readme.zh.md')
        fs.copy_file(f'{dir_i}/build/self_build.py',
                     f'{dir_m}/build/self_build.py')
        compress_dir(f'{dir_m}/build', f'{dir_o}/build.zip', True)
    
    def copy_config_dir() -> None:
        # make sure config/depsland.yaml has configured local oss.
        assert loads(f'{dir_i}/config/depsland.yaml')['oss']['server'] == 'local'
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
def full_build(
    oss_scheme: str, pypi_scheme: str = 'full', _add_python_path: bool = True
) -> None:
    """
    generate `dist/depsland-setup-<version>` folder.
    
    args:
        oss_scheme: 'aliyun' or 'local'
            aliyun: you need to prepare a file named -
            'config/depsland_for_dev.yaml', which contains aliyun oss access -
            & secret keys.
    kwargs:
        pypi_scheme (-p): 'full', 'least', 'blank'
            full: link `<proj>/pypi` to `<dist>/pypi`.
                this is used for local test.
            least: link `<proj>/chore/pypi_self` to `<dist>/pypi`.
                this should be used only when you want to publish a version. -
                be careful do not update any content of `<dist>/pypi`.
            blank: copy `<proj>/chore/pypi_blank` to `<dist>/pypi`.
    """
    # checks
    if not self_check():
        # print(':v3s', 'please resolve self-check problems first')
        # exit()
        pass
    if oss_scheme == 'aliyun':
        assert exists(os.getenv('DEPSLAND_CONFIG_ROOT'))
    
    root_i = paths.project.root
    root_o = '{dist}/depsland-setup-{version}'.format(
        dist=paths.project.dist, version=__version__
    )
    assert not exists(root_o)
    os.mkdir(root_o)
    
    # -------------------------------------------------------------------------
    
    # make empty dirs
    os.mkdir(f'{root_o}/apps')
    os.mkdir(f'{root_o}/apps/.bin')
    os.mkdir(f'{root_o}/apps/.venv')
    os.mkdir(f'{root_o}/build')
    os.mkdir(f'{root_o}/build/exe')
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
    fs.copy_file(
        f'{root_i}/build/exe/depsland.exe',
        f'{root_o}/build/exe/depsland.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-sui.exe',
        f'{root_o}/build/exe/depsland-sui.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-suw.exe',
        f'{root_o}/build/exe/depsland-suw.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/desktop.exe',
        f'{root_o}/build/exe/desktop.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/launcher.ico',
        f'{root_o}/build/exe/launcher.ico',
    )
    fs.copy_file(
        f'{root_i}/build/exe/setup.exe',
        f'{root_o}/setup.exe',
    )
    fs.copy_tree(
        f'{root_i}/build/setup_wizard',
        f'{root_o}/build/setup_wizard',
    )
    fs.copy_file(
        f'{root_i}/build/depsland_setup.py',
        f'{root_o}/build/depsland_setup.py',
    )
    fs.make_link(
        f'{root_i}/chore/site_packages',
        f'{root_o}/chore/site_packages',
    )
    fs.copy_tree(
        f'{root_i}/depsland',
        f'{root_o}/depsland',
    )
    fs.copy_tree(
        f'{root_i}/sidework',
        f'{root_o}/sidework',
    )
    fs.copy_file(
        f'{root_i}/.depsland_project',
        f'{root_o}/.depsland_project',
    )
    
    if oss_scheme == 'aliyun':
        # assert exists(custom := os.getenv('DEPSLAND_CONFIG_ROOT'))
        custom = os.getenv('DEPSLAND_CONFIG_ROOT')
        assert (
            loads(f'{custom}/depsland.yaml')
            ['oss']['server'] == 'aliyun'
        )
        fs.copy_file(
            f'{custom}/depsland.yaml',
            f'{root_o}/config/depsland.yaml',
        )
    else:
        assert (
            loads(f'{root_i}/config/depsland.yaml')
            ['oss']['server'] == 'local'
        )
        fs.copy_file(
            f'{root_i}/config/depsland.yaml',
            f'{root_o}/config/depsland.yaml',
        )
    
    if pypi_scheme == 'full':
        fs.make_link(f'{root_i}/pypi', f'{root_o}/pypi')
    elif pypi_scheme == 'least':
        print(':v3s', 'do not edit "pypi" folder in the dist')
        fs.make_link(f'{root_i}/chore/pypi_self', f'{root_o}/pypi')
    else:  # 'blank'
        fs.copy_tree(f'{root_i}/chore/pypi_blank', f'{root_o}/pypi')
    
    if _add_python_path:
        fs.make_link(f'{root_i}/python', f'{root_o}/python')
    
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
    uac_admin: bool = False
) -> None:  # FIXME
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
        icon=xpath('exe/launcher.ico'),
        show_console=show_console,
        uac_admin=uac_admin,
    )


# @cli.cmd()
# def build_all_launchers():  # FIXME
#     for f in fs.find_files(xpath('exe'), '.bat'):
#         print(':i', f.name)
#         _b2e(f.path, icon=xpath('exe/launcher.ico'))


@cli.cmd()
def compress_to_zip():
    dir_i = '{}/{}'.format(paths.project.dist, f'depsland-{__version__}')
    file_o = '{}/{}'.format(paths.project.dist, f'depsland-{__version__}.zip')
    ziptool.compress_dir(dir_i, file_o, overwrite=True)
    print(':t', 'see result at', fs.relpath(file_o))


if __name__ == '__main__':
    # pox build/build.py backup-project-resources
    # pox build/build.py full-build aliyun
    #   before running this command, you need to set environment variable -
    #   'DEPSLAND_CONFIG_ROOT' to the path to your custom config folder.
    # pox build/build.py bat-2-exe build/exe/setup.bat -u
    cli.run()
