import os
from textwrap import dedent

from lk_utils import dumps
from lk_utils import loads
from lk_utils import run_cmd_args
from lk_utils import xpath

from ..chore import make_temp_dir

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
        remove_bat: bool = False,
) -> str:
    # validate parameters
    assert file_i.endswith('.bat')
    if file_o:
        assert file_o.endswith('.exe')
    else:
        file_o = file_i.removesuffix('.bat') + '.exe'
    if icon:
        assert icon.endswith('.ico')
        assert os.path.exists(icon)
    
    _bat_2_exe(file_i, file_o, show_console)
    if remove_bat:
        os.remove(file_i)
    
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


def elevate_privilege(file_exe: str) -> None:
    run_cmd_args(_rcedit_exe, file_exe, '--set-requested-execution-level',
                 'requireAdministrator')


def _bat_2_exe(file_bat: str, file_exe: str, show_console: bool = True) -> None:
    """
    https://github.com/silvandeleemput/gen-exe
    https://blog.csdn.net/qq981378640/article/details/52980741
    """
    command = ' && '.join(loads(file_bat).splitlines()).strip()
    command = command.replace('%~dp0', '{EXE_DIR}').replace('%cd%', '{EXE_DIR}')
    if command.endswith('%*'): command = command[:-3]
    assert len(command) <= 259, 'command too long'
    command += '\0' * (259 - len(command)) + ('1' if show_console else '0')
    encoded_command = command.encode('ascii')
    
    template: bytes = loads(_template_exe, ftype='binary')
    output = template.replace(b'X' * 259 + b'1', encoded_command)
    print('add command to exe', command)
    dumps(output, file_exe, ftype='binary')


# DELETE: not use this anymore: it will crash if we add icon to exe.
# def _bat_2_exe_2(
#         file_bat: str,
#         file_exe: str,
#         show_console: bool = True
# ) -> None:
#     file_exe_o, file_bat_o = depsland_booster.distribute(file_bat, file_exe)
#     if not show_console:
#         data_r: str = loads(file_bat_o)
#         data_w: str = data_r.replace('python.exe', 'pythonw.exe')
#         dumps(data_w, file_bat_o)
#
#
# def _bat_2_exe_3(
#         file_bat: str,
#         file_exe: str,
#         file_ico: str = '',
#         show_console: bool = True
# ) -> None:
#     """
#     https://github.com/tokyoneon/B2E
#     """
#     b2e = xpath('bat_to_exe_converter.exe')
#
#     @new_thread(daemon=False)
#     def convert():
#         """
#         this function works a little slow, so we put it in another thread.
#         """
#         run_cmd_args(*compose_cmd(
#             b2e, '/bat', file_bat, '/exe', file_exe,
#             ('/icon', file_ico),
#             ('/invisible' if not show_console else ''),
#             '/overwrite'
#         ))
#
#     th = convert()
#     atexit.register(th.join)


# -----------------------------------------------------------------------------

def create_shortcut(file_i: str, file_o: str = None) -> None:
    """
    use batch script to create shortcut, no pywin32 required.
    
    args:
        file_o: if not given, will create a shortcut in the same folder as
            `file_i`, with the same base name.
    
    https://superuser.com/questions/455364/how-to-create-a-shortcut-using-a
    -batch-script
    https://www.blog.pythonlibrary.org/2010/01/23/using-python-to-create
    -shortcuts/
    """
    assert os.path.exists(file_i) and not file_i.endswith('.lnk')
    if not file_o:
        file_o = os.path.splitext(os.path.basename(file_i))[0] + '.lnk'
    else:
        assert file_o.endswith('.lnk')
    if os.path.exists(file_o):
        os.remove(file_o)
    
    vbs = make_temp_dir() + '/shortcut_gen.vbs'
    command = dedent('''
        Set objWS = WScript.CreateObject("WScript.Shell")
        lnkFile = "{file_o}"
        Set objLink = objWS.CreateShortcut(lnkFile)
        objLink.TargetPath = "{file_i}"
        objLink.Save
    ''').format(
        file_i=file_i.replace('/', '\\'),
        file_o=file_o.replace('/', '\\'),
    )
    dumps(command, vbs, ftype='plain')
    
    run_cmd_args('cscript', '/nologo', vbs)
