"""
References:
    ~/docs/depsland-venv-setup.md
"""
from ..utils import mklinks
from ..venv_struct import proj_dir


def get_pip(pyversion, dst_dir):
    assets_dir = f'{proj_dir}/build/assets'
    if pyversion.startswith('python2'):
        src_dir = f'{assets_dir}/pip_suits_for_py2'
    else:
        src_dir = f'{assets_dir}/pip_suits_for_py3'
    return mklinks(src_dir, dst_dir)
