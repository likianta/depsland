"""
Deploy depsland on client computer and make sure depsland integrity.
"""
import os
from os.path import exists

from lk_logger import lk

from depsland.path_struct import *
from depsland.setup import *
from depsland.utils import unzip_file


def main(pyversion='python39'):
    src_struct.indexing_dirs(pyversion)
    assets_struct.indexing_dirs(pyversion)
    
    _build_dirs()
    _setup_embed_python()
    _setup_python_suits()
    _add_to_system_environment()

    lk.loga('successfully setup depsland :)')


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
    path = os.path.abspath(f'{proj_dir}/depsland.bat')
    if path not in os.environ.get('DEPSLAND', []):
        os.system('setx DEPSLAND "{}"'.format(path))
    lk.loga('Environment variable updated', f'DEPSLAND => {path}')


if __name__ == '__main__':
    main('python39')
