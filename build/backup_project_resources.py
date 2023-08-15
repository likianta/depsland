"""
py build/backup_project_resources.py
"""
if True:
    import os
    from lk_utils import xpath
    # make sure config root is original value
    os.environ['DEPSLAND_CONFIG_ROOT'] = xpath('../config')

from os.path import exists

from lk_utils import fs
from lk_utils import loads

from depsland import paths
from depsland.utils import make_temp_dir
from depsland.utils.ziptool import compress_dir

dir_i = paths.project.root
dir_m = make_temp_dir()
dir_o = paths.project.depsland + '/chore'
assert exists(dir_o), f'if {dir_o} not exists, you may manually create it ' \
                      f'(as an empty folder)'


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
    # DELETE: about to remove
    fs.copy_file(f'{dir_i}/build/install_requirements.py',
                 f'{dir_m}/build/install_requirements.py')
    fs.copy_file(f'{dir_i}/build/readme.zh.md',
                 f'{dir_m}/build/readme.zh.md')
    fs.copy_file(f'{dir_i}/build/self_build.py',
                 f'{dir_m}/build/self_build.py')
    compress_dir(f'{dir_m}/build', f'{dir_o}/build.zip', True)


def copy_conf_dir() -> None:
    # make sure conf/depsland.yaml has configured local oss.
    assert loads(f'{dir_i}/conf/depsland.yaml')['oss']['server'] == 'local'
    fs.copy_file(f'{dir_i}/conf/depsland.yaml', f'{dir_m}/depsland.yaml')
    compress_dir(f'{dir_m}/depsland.yaml', f'{dir_o}/conf.zip', True)


def copy_sidework_dir() -> None:
    fs.make_dir(f'{dir_m}/sidework')
    for f in fs.find_files(f'{dir_i}/sidework'):
        i = f.path
        o = f'{dir_m}/sidework/{f.name}'
        fs.copy_file(i, o)
    compress_dir(f'{dir_m}/sidework', f'{dir_o}/sidework.zip', True)


copy_build_dir()
copy_conf_dir()
copy_sidework_dir()
