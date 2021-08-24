"""
Deploy depsland on client computer and make sure depsland integrity.
"""
import os
from os.path import exists

from lk_logger import lk

from depsland.setup import download_embed_python
from depsland.utils import unzip_file
from depsland.venv_struct import *

assets_dir = f'{proj_dir}/build/assets'


def main():
    build_dirs()
    _setup_embed_python()
    _add_to_system_environment()
    # TODO: delete `~/dist/setup.bat` file


def build_dirs():
    for d in (
        f'{proj_dir}/venv_home',
        f'{proj_dir}/venv_home/inventory',
        f'{proj_dir}/venv_home/inventory/{platform}',
        f'{proj_dir}/venv_home/venv_links',
        f'{proj_dir}/pypi',
        f'{proj_dir}/pypi/cache',
        f'{proj_dir}/pypi/downloads',
    ):
        if not exists(d):
            lk.loga('mkdir', d)
            os.mkdir(d)
    
    path_struct.build_dirs()


def _setup_embed_python():
    if exists(file := f'{assets_dir}/python39_embed_win.zip'):
        # unpack to the bin dir
        unzip_file(file, path_struct.python)
    else:
        # download_embed_python('python27')
        download_embed_python('python39')


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
    lk.loga('Environment variable updated', os.getenv('DEPSLAND'))


def create_pyvenv_dirs(*pyversions):
    for v in pyversions:
        path_mgr = SourcePathStruct(v, platform)
        path_mgr.build_dirs()


if __name__ == '__main__':
    main()
