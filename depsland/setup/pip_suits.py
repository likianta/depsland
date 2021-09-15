"""
If you want only pip package installed, run `get_pip` and it is fast to
generate.
If you need '~/scripts/pip.exe' etc., run `get_pip_scripts`. Note that `get_pip_
scripts` can only generate pip scripts, no package being installed; you may
need also to run `get_pip` after that.

References:
    ~/docs/depsland-venv-setup.md
"""
from os.path import exists
from shutil import rmtree

from lk_utils import send_cmd

from ..path_model import *
from ..utils import mklinks


def get_pip_scripts(dst_dir):
    mklinks(assets_model.setuptools, dst_dir)
    
    send_cmd('cd {pip_src_dir} & {python} setup.py install'.format(
        pip_src_dir=assets_model.pip_src,
        python=src_model.interpreter,
        pip_src=assets_model.pip_src,
    ).replace('/', '\\'))
    
    assert exists(f'{src_model.scripts}/pip.exe')
    
    rmtree(src_model.site_packages + '/' + assets_model.pip_egg)


def get_pip(dst_dir):
    out = []
    out.extend(mklinks(assets_model.setuptools, dst_dir, exist_ok=True))
    out.extend(mklinks(assets_model.pip, dst_dir, exist_ok=False))
    return out
