from shutil import copyfile
from shutil import copytree

from ..typehint import TPathStruct
from ..utils import mklinks


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


def get_tkinter(assets_struct: TPathStruct, dst_dir):
    return mklinks(assets_struct.tkinter, dst_dir)
