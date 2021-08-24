"""
References:
    ~/docs/depsland-venv-setup.md
"""
from ..main import mklinks
from ..manager.venv_manager import proj_dir, path_mgr


def get_pip(pyversion):
    assets_dir = f'{proj_dir}/build/assets'
    if pyversion.startswith('python2'):
        src_path = f'{assets_dir}/pip_suits_for_py2'
    else:
        src_path = f'{assets_dir}/pip_suits_for_py3'
    
    dst_path = path_mgr.pip_suits
    
    mklinks(src_path, dst_path)


# class PathsForPy2:
#     _assets_dir = f'{proj_dir}/build/assets/python2_offline_pkgs'
#     setuptools = f'{_assets_dir}/setuptools-45.0.0-py2.py3-none-any'
#     pip = f'{_assets_dir}/pip-20.3.4-py2.py3-none-any'
#
#
# class PathsForPy3:
#     _assets_dir = f'{proj_dir}/build/assets/python3_offline_pkgs'
#     setuptools = f'{_assets_dir}/setuptools-57.4.0-py3-none-any'
#     pip = f'{_assets_dir}/pip-21.2.4-py3-none-any'
