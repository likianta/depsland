"""
Deploy depsland on client computer and make sure depsland integrity.
"""
import os
import sys
from os.path import exists, normpath
from textwrap import dedent

from lk_logger import lk
from lk_utils import dumps, loads

from depsland.path_struct import *
from depsland.setup import *
from depsland.utils import unzip_file


def main(pyversion='python39'):
    src_struct.indexing_dirs(pyversion)
    assets_struct.indexing_dirs(pyversion)
    
    _build_dirs()
    _setup_embed_python()
    _setup_python_suits()
    _create_depsland_bat()
    _add_to_system_environment()
    
    lk.loga('Successfully setup depsland :)')
    lk.logt('[I4238]', dedent('''
        THE NEXT STEP:
            You need to add "%DEPSLAND%" to your environment PATH manullay.
            Then test it in the CMD:
                depsland -V
            There're should be shown "Python 3.9.6".
        NOTES:
            1. You need to restart CMD before running `depsland -V` in CMD.
    '''))
    '''
        Warnings:
            If you are using the third party files manager -- for example
            "XYPlorer" -- you cannot see any environment variable changes
            when you double click any bat script file (which includes `echo
            %PATH%` command) in it.
            The simplest resolution is restarting the third party files
            manager, or just open Windows files explorer and double click on
            that bat script. You will see `echo %PATH%` has been updated and
            `depsland -V` works as expected then.
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
    
    src_struct.build_dirs()


def _setup_embed_python():
    if exists(zip_file := assets_struct.embed_python_zip):
        # unpack to `src_struct.python`
        unzip_file(zip_file, src_struct.python)
        disable_pth_file(src_struct.python_pth)
    else:
        # download_embed_python('python27')
        download_embed_python('python39')


def _setup_python_suits():
    get_tkinter(assets_struct, src_struct.python)
    get_pip_scripts(src_struct.site_packages)
    get_pip(src_struct.site_packages)


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
        The command `setx PATH "%PATH%;{my_path}"` doesn't work as expected as
        we did in CMD manually, it overwrote existed variables and couldn't
        distinguish the system paths and user paths. So I set the path to a
        soly new environment variable.
    """
    path = normpath(proj_dir)
    os.system('setx DEPSLAND "{}"'.format(path))
    lk.loga('Environment variable updated', f'DEPSLAND => {path}')


if __name__ == '__main__':
    lk.lite_mode = True
    main('python39')
