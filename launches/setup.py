"""
Deploy depsland on client computer and make sure depsland integrity.
"""
import os
from os.path import exists

from depsland.manager import *
from depsland.setup import download_embed_python
from depsland.utils import unzip_file

assets_dir = f'{proj_dir}/build/assets'


def main():
    _build_dirs()
    _setup_embed_python()
    _add_to_system_environment()
    # TODO: delete `~/dist/setup.bat` file


def _build_dirs():
    os.makedirs(f'{proj_dir}/venv_home/inventory/{platform}', exist_ok=True)
    os.makedirs(f'{proj_dir}/venv_home/venv_links', exist_ok=True)
    SourcePathManager('python39', platform).build_dirs()


def _setup_embed_python():
    if exists(file := f'{assets_dir}/python39_embed_win.zip'):
        # unpack to the bin dir
        unzip_file(file, path_mgr.python)
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
        we did in CMD manually, so I set the path to a soly new environment
        variable.
    """
    path = os.path.abspath(f'{proj_dir}/depsland.bat')
    if path not in os.environ:
        os.system('setx DEPSLAND "{}"'.format(path))


def create_pyvenv_dirs(*pyversions):
    for v in pyversions:
        path_mgr = SourcePathManager(v, platform)
        path_mgr.build_dirs()


if __name__ == '__main__':
    create_pyvenv_dirs('python39')
