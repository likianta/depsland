import os

from lk_utils import dumps
from lk_utils import loads
from lk_utils import run_cmd_args
from lk_utils import xpath

from .....utils.compat_py38 import substitute_suffix

_is_windows = os.name == 'nt'
_template_exe = xpath('template_static.exe')
_rcedit_exe = xpath('rcedit.exe')


# noinspection PyUnusedLocal
def bat_2_exe(
    file_i: str,
    file_o: str = '',
    icon: str = '',
    show_console: bool = True,
    uac_admin: bool = False,
) -> str:
    # validate parameters
    assert file_i.endswith('.bat')
    if file_o:
        assert file_o.endswith('.exe')
    else:
        file_o = substitute_suffix(file_i, '.bat', '.exe')
    if icon:
        assert icon.endswith('.ico')
        assert os.path.exists(icon)
    
    _bat_2_exe(file_i, file_o, show_console)
    
    if _is_windows:
        # adding icon and elevating privilege requires `rcedit.exe`, which is
        # only available on windows.
        if icon:
            add_icon_to_exe(file_o, icon)
        if uac_admin:
            elevate_privilege(file_o)
    elif any((icon, uac_admin)):
        print('[yellow dim]adding icon and/or elevating exe privilege are only '
              'available on windows. (if you are using macos/linux, this '
              'warning can be ignored.)[/]', ':pr')
    
    return file_o


def add_icon_to_exe(file_exe: str, file_ico: str) -> None:
    run_cmd_args(_rcedit_exe, file_exe, '--set-icon', file_ico)


def elevate_privilege(file_exe: str) -> None:  # noqa
    # run_cmd_args(_rcedit_exe, file_exe, '--set-requested-execution-level',
    #              'requireAdministrator')
    raise Exception(
        'using rcedit.exe to elevate privilege is not supported. '
        'please turn to `util_b` or see reason in `../readme.zh.md`.'
    )


def _bat_2_exe(file_bat: str, file_exe: str, show_console: bool = True) -> None:
    """
    https://github.com/silvandeleemput/gen-exe
    https://blog.csdn.net/qq981378640/article/details/52980741
    """
    command = ' && '.join(loads(file_bat).splitlines()).strip()
    command = command.replace('%~dp0', '{EXE_DIR}').replace('%cd%', '{EXE_DIR}')
    #   backup note:
    #       unc path prefix '\\?\<a_very_long_absolute_local_path>'
    #       if you encountered an error like this:
    #           CMD doesn't support UNC paths as current directory
    #       it may becuase you are using an inproper terminal application \
    #       other than "command prompt" terminal.
    #       ref: https://stackoverflow.com/questions/21194530/what-does-mean \
    #       -when-prepended-to-a-file-path
    if command.endswith('%*'): command = command[:-3]
    assert len(command) <= 259, 'command too long'
    command += '\0' * (259 - len(command)) + ('1' if show_console else '0')
    encoded_command = command.encode('ascii')
    
    template: bytes = loads(_template_exe, type='binary')
    output = template.replace(b'X' * 259 + b'1', encoded_command)
    print('add command to exe', command)
    dumps(output, file_exe, type='binary')
