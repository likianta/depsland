import os
from os.path import exists
from subprocess import call

from lk_utils import new_thread
from lk_utils import xpath
from lk_utils.subproc import compose_cmd
from lk_utils.time_utils import timeout_gen

_is_windows = os.name == 'nt'
_b2e_exe = xpath('b2e.exe')


def bat_2_exe(
        file_i: str,
        file_o: str = '',
        icon: str = '',
        show_console: bool = True,
        uac_admin: bool = False,
        remove_bat: bool = False,
) -> str:
    # validate platform
    if not _is_windows:
        raise Exception('the b2e function can only run on Windows')
    
    # validate parameters
    assert file_i.endswith('.bat')
    if file_o:
        assert file_o.endswith('.exe')
    else:
        file_o = file_i.removesuffix('.bat') + '.exe'
    if icon:
        assert icon.endswith('.ico')
        assert os.path.exists(icon)
    
    _bat_2_exe(file_i, file_o, icon, show_console, uac_admin, remove_bat)
    
    return file_o


# @new_thread(daemon=False)
def _bat_2_exe(
        file_bat: str,
        file_exe: str,
        icon: str = '',
        show_console: bool = True,
        uac_admin: bool = False,
        remove_bat: bool = False,
) -> None:
    """
    ./b2e.exe -h
    """
    if exists(file_exe):
        os.remove(file_exe)
    
    call(compose_cmd(
        _b2e_exe,
        ('-bat', file_bat),
        ('-save', file_exe),
        ('-icon', icon),
        ('-invisible' if not show_console else ''),
        ('-admin' if uac_admin else ''),
        ('-overwrite', '-x64')
    ))
    
    # wait exe generated
    for i in timeout_gen(5, 0.1):
        if i > 10 and i % 10 == 0:
            print(':v', 'waiting for converting bat to exe...')
        if exists(file_exe):
            break
    
    if remove_bat:
        os.remove(file_bat)
