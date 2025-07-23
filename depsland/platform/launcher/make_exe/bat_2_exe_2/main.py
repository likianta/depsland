import os
from os.path import exists
from subprocess import call

from lk_utils import wait
from lk_utils import fs
from lk_utils.subproc import compose_cmd

_is_windows = os.name == 'nt'
_b2e_exe = fs.xpath('b2e.exe')


def bat_2_exe(
    file_i: str,
    file_o: str = '',
    icon: str = '',
    show_console: bool = True,
    uac_admin: bool = False,
) -> str:
    # validate platform
    if not _is_windows:
        raise Exception('the b2e function can only run on Windows')
    
    # validate parameters
    assert file_i.endswith('.bat')
    if file_o:
        assert file_o.endswith('.exe')
    else:
        file_o = fs.replace_ext(file_i, 'exe')
    if icon:
        assert icon.endswith('.ico')
        assert os.path.exists(icon)
    
    _bat_2_exe(file_i, file_o, icon, show_console, uac_admin)
    
    return file_o


# @new_thread(daemon=False)
def _bat_2_exe(
    file_bat: str,
    file_exe: str,
    icon: str = '',
    show_console: bool = True,
    uac_admin: bool = False,
) -> None:
    """
    ./b2e.exe -h
    """
    if exists(file_exe):
        os.remove(file_exe)
    
    call(compose_cmd(
        _b2e_exe,
        '-admin' if uac_admin else '',
        '-invisible' if not show_console else '',
        '-overwrite',
        '-x64',
        ('-bat', file_bat),
        ('-icon', icon),
        ('-save', file_exe),
    ))
    
    # wait exe generated
    for _ in wait(5, 0.05):
        if exists(file_exe):
            break
