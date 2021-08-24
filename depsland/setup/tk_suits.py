from shutil import copytree, copyfile

from ..utils import mklinks
from ..manager.venv_manager import proj_dir, path_mgr


def copy_tkinter(system_python_dir, dst_dir):
    """
    Only used for building project from source code.
    
    References:
        https://github.com/Likianta/pyportable-installer/blob/master/docs/add
            -tkinter-to-embed-python.md
    """
    for i, o in (
            (f'{system_python_dir}/tcl', f'{dst_dir}/tcl'),
            (f'{system_python_dir}/Lib/tkinter', f'{dst_dir}/tkinter'),
    ):
        copytree(i, o)
        
    for i, o in (
            (f'{system_python_dir}/DLLs/_tkinter.pyd', f'{dst_dir}/_tkinter.pyd'),
            (f'{system_python_dir}/DLLs/tcl86t.dll', f'{dst_dir}/tcl86t.dll'),
            (f'{system_python_dir}/DLLs/tk86t.dll', f'{dst_dir}/tk86t.dll'),
    ):
        copyfile(i, o)


def get_tkinter(pyversion: str):
    assets_dir = f'{proj_dir}/build/assets'
    if pyversion.startswith('python2'):
        if pyversion.endswith('-32'):
            src_dir = f'{assets_dir}/tk_suits_for_py2_32bit'
        else:
            src_dir = f'{assets_dir}/tk_suits_for_py2'
    else:
        if pyversion.endswith('-32'):
            src_dir = f'{assets_dir}/tk_suits_for_py3_32bit'
        else:
            src_dir = f'{assets_dir}/tk_suits_for_py3'
    
    dst_dir = path_mgr.tk_suits
    
    mklinks(src_dir, dst_dir)
