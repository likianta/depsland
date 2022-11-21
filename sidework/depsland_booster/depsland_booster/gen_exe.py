from os import remove
from os.path import abspath
from os.path import basename
from os.path import dirname
from os.path import exists
from shutil import copyfile
from sys import base_exec_prefix
from typing import Tuple


def distribute(file_i: str, file_o: str) -> Tuple[str, str]:
    assert file_i.endswith('.bat')
    assert file_o.endswith('.exe')
    
    file_exe_i = '{}/Scripts/depsland-booster.exe'.format(base_exec_prefix)
    file_exe_o = file_o
    _copy(file_exe_i, file_exe_o)
    
    file_bat_i = file_i
    file_bat_o = '{}/.{}.bat'.format(
        dirname(abspath(file_exe_o)),
        basename(file_exe_o)[:-4]
    )
    _copy(file_bat_i, file_bat_o)
    
    return file_exe_o, file_bat_o


def _copy(file_i: str, file_o: str) -> None:
    assert exists(file_i)
    if exists(file_o):
        remove(file_o)
    copyfile(file_i, file_o)
