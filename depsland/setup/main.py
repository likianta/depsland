"""
Deploy depsland on client computer and make sure depsland integrity.
"""
import os
import sys
from os.path import dirname
from os.path import exists
from os.path import normpath
from textwrap import dedent

from lk_logger import lk
from lk_utils import dumps
from lk_utils import loads

from depsland.path_model import *
from depsland.setup import *
from depsland.utils import unzip_file


def _fuzzy_find_path(name):
    parent_dir = proj_dir
    for try_times in range(2):
        parent_dir = dirname(parent_dir)
        if exists(out := f'{parent_dir}/{name}'):
            return out
    raise FileNotFoundError(name)


def main(pyversion='python39'):
    curr_build_dir = _fuzzy_find_path('build')
    if exists(f'{curr_build_dir}/setup_done.txt'):
        lk.logt('[I4139]', dedent('''
            Despland has been installed on your computer.
            For re-installation, you can delete '~/build/setup_done.txt' then
            run 'setup.exe' again.
        '''))
        return
    
    src_model.indexing_dirs(pyversion)
    assets_model.indexing_dirs(pyversion)
    
    _build_dirs()
    _setup_embed_python()
    _setup_python_suits()
    _create_depsland_bat()
    env_var = _add_to_system_environment()
    
    # mark setup done
    dumps('', f'{curr_build_dir}/setup_done.txt')
    
    # remove <root>/setup.exe
    # parent_dir = proj_dir
    # for try_times in range(2):
    #     parent_dir = dirname(parent_dir)
    #     if exists(setup_exe := f'{parent_dir}/setup.exe'):
    #         os.remove(setup_exe)
    #         #   FIXME: OSError happend because 'setup.exe' is running.
    #         break
    
    lk.loga('Successfully setup depsland :)')
    if '%DEPSLAND%' not in os.getenv('PATH') and \
            env_var not in os.getenv('PATH'):
        lk.logt('[I4238]', dedent('''
            THE NEXT STEP:
                (Suggest) You can add "%DEPSLAND%" to your environment PATH
                manullay. Then test it in the CMD:
                    depsland -V
                There're should be shown "Python 3.9.6".
            NOTE:
                1. You need to restart CMD before running `depsland -V` in it.
        '''))
        '''
            Warnings:
                If you are using a third party files manager -- for example
                "XYPlorer" -- you cannot see any environment variable changes
                when you double click any bat script file (which includes `echo
                %PATH%` command) in it.
                The simplest resolution is restarting the third party files
                manager, or just open Windows files explorer and double click
                on that bat script. You will see `echo %PATH%` has been updated
                and `depsland -V` works as expected then.
        '''


def _build_dirs():
    for d in (
            f'{proj_dir}/venv_home',
            f'{proj_dir}/venv_home/inventory',
            f'{proj_dir}/venv_home/inventory/{platform}',
            f'{proj_dir}/venv_home/venv_links',
            f'{proj_dir}/pypi',
            f'{proj_dir}/pypi/cache',
            f'{proj_dir}/pypi/downloads',
            f'{proj_dir}/pypi/extracted',
            f'{proj_dir}/pypi/index',
    ):
        if not exists(d):
            lk.loga('mkdir', d)
            os.mkdir(d)
    
    src_model.build_dirs()


def _setup_embed_python():
    if exists(zip_file := assets_model.embed_python_zip):
        # unpack to `src_model.python`
        unzip_file(zip_file, src_model.python)
        disable_pth_file(src_model.python_pth)
    else:
        # download_embed_python('python27')
        download_embed_python('python39')


def _setup_python_suits():
    get_tkinter(assets_model, src_model.python)
    get_pip_scripts(src_model.site_packages)
    get_pip(src_model.site_packages)


def _create_depsland_bat():
    template = loads(f'{proj_dir}/build/depsland.bat')
    code = template.format(PYTHON=sys.executable)
    dumps(code, f'{proj_dir}/depsland.bat')


def _add_to_system_environment():
    """
    References:
        https://stackoverflow.com/questions/17657686/is-it-possible-to-set-an
            -environment-variable-from-python-permanently
    
    Notice:
        1. The command `setx PATH "%PATH%;{my_path}"` doesn't work as expected
           as we did in CMD manually, it overwrote existed variables and
           couldn't distinguish the system paths and user paths. So I set the
           path to a soly new environment variable.
        2. The `setx` command is only available in Windows 7 and later.
    """
    path = normpath(proj_dir)
    os.system('setx DEPSLAND "{}"'.format(path))
    lk.loga('Added DEPSLAND to environment variable', f'DEPSLAND => {path}')
    
    ''' Note: How does PyPortable-Installer work with Depsland?
    
    1. Using `%DEPSLAND%\\depsland.bat ...` to call depsland in cmd.
    2. If user has added %DEPSLAND% to user %PATH% manually, the user can use
       `depsland ...` to call depsland in cmd.
    3. A Python script can add `sys.path.append(os.getenv('DEPSLAND'))` to
       import depsland package.
    '''
    
    # add `%DEPSLAND%` to `%PATH%`
    # FIXME: The method below will mix user path and system path values and
    #   messy up user one's. We may need to find a way to modify register table
    #   instead of using `setx` command.
    # if '%DEPSLAND%' not in os.getenv('PATH') and path not in os.getenv('PATH'):
    #     os.system('setx PATH "%PATH%;%DEPSLAND%"'.format(path))
    # lk.loga('Added DEPSLAND to USER_PATH')
    
    return path


if __name__ == '__main__':
    lk.lite_mode = True
    main('python39')
