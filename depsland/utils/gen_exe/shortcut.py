import os
from textwrap import dedent

from lk_utils import dumps
from lk_utils import run_cmd_args

from ..chore import make_temp_dir


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
