"""
depsland init
"""
import os

from lk_utils.filesniff import relpath

from ..utils import mklinks


def main(dir_='.'):
    """
    workflow:
        1. get target dir path and dir name
        2. create empty folders (based on dir name)
        3. symlink python interpreter
    """
    os.chdir(dir_)
    dirpath = os.getcwd()
    dirname = os.path.basename(dirpath)
    try:
        _create_empty_folders(dirname)
    except FileExistsError:
        return
    _symlink_python_interpreter(dirpath)


def _create_empty_folders(dirname: str):
    """
    dirs' structure:
        windows
            depsland
            |= venv_home
               |= instances
                  |= <dirname>
                     |= dlls
                     |= lib
                        |= site-packages
                     |= scripts
                     |- python.exe
                     |- ...
        macos
            depsland
            |= venv_home
               |= instances
                  |= <dirname>
                     |= bin
                        |- <python_interpreter>
                     |= lib
                        |= <python_version>
                           |= site-packages
    """
    root = relpath('../../venv_home/instances')
    if os.path.exists(f'{root}/{dirname}'):
        raise FileExistsError(f'{dirname} already exists')
    os.mkdir(f'{root}/{dirname}')
    os.mkdir(f'{root}/{dirname}/dlls')
    os.mkdir(f'{root}/{dirname}/lib')
    os.mkdir(f'{root}/{dirname}/lib/site-packages')
    os.mkdir(f'{root}/{dirname}/scripts')


def _symlink_python_interpreter(dirpath: str):
    dir_i = relpath('../../venv_home/interpreters/3.10')
    dir_o = dirpath
    mklinks(dir_i, dir_o)
