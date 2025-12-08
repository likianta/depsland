from lk_utils import dedent
from lk_utils import fs
from lk_utils import run_cmd_args

from ... import paths


def make_shortcut(file_i: str, file_o: str = None) -> None:
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
    assert fs.exist(file_i) and not file_i.endswith('.lnk')
    if file_o:
        assert file_o.endswith('.lnk')
    else:
        file_o = fs.replace_ext(file_i, 'lnk')
    if fs.exist(file_o):
        fs.remove_file(file_o)
    
    script = dedent(
        '''
        Set objWS = WScript.CreateObject("WScript.Shell")
        lnkFile = "{file_o}"
        Set objLink = objWS.CreateShortcut(lnkFile)
        objLink.TargetPath = "{file_i}"
        objLink.Save
        '''
    ).format(
        file_i=file_i.replace('/', '\\'),
        file_o=file_o.replace('/', '\\'),
    )
    fs.dump(script, paths.temp.shortcut_vbs, type='plain')
    
    run_cmd_args('cscript', '/nologo', paths.temp.shortcut_vbs)
