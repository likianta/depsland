import os
import shutil
import typing as t
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile

from lk_utils import fs

_IS_WINDOWS = os.name == 'nt'


def compress_dir(
    dir_i: str,
    file_o: str,
    overwrite: bool = None,
    top_name: str = None,
) -> str:
    """
    ref: https://likianta.blog.csdn.net/article/details/126710855
    """
    if fs.exist(file_o):
        if not _overwrite(file_o, overwrite):
            return file_o
    if top_name is None:
        top_name = fs.basename(dir_i)
    with ZipFile(file_o, 'w', compression=ZIP_DEFLATED, compresslevel=7) as z:
        z.write(dir_i, arcname=top_name)
        for f in tuple(fs.findall_files(dir_i)):
            z.write(f.path, arcname='{}/{}'.format(
                top_name, fs.relpath(f.path, dir_i)
            ))
    return file_o


def compress_file(file_i: str, file_o: str, overwrite: bool = None) -> str:
    if fs.exist(file_o):
        if not _overwrite(file_o, overwrite):
            return file_o
    if file_o.endswith('.fzip'):  # trick: just rename file_i to file_o
        shutil.copyfile(file_i, file_o)
        return file_o
    with ZipFile(file_o, 'w', compression=ZIP_DEFLATED, compresslevel=7) as z:
        z.write(file_i, arcname=fs.basename(file_i))
    return file_o


def extract_file(file_i: str, path_o: str, overwrite: bool = None) -> str:
    # print(file_i, path_o, overwrite, fs.exist(path_o), ':lv')
    if fs.exist(path_o):
        if not _overwrite(path_o, overwrite):
            return path_o
    
    if file_i.endswith('.fzip'):
        file_o = path_o
        shutil.copyfile(file_i, file_o)
        return file_o
    else:
        dir_o = path_o
        # if dir_o.endswith('/.'):
        #     dir_o = dir_o[:-2]
    
    dirname_o = fs.basename(fs.abspath(dir_o))
    with ZipFile(file_i, 'r', compression=ZIP_DEFLATED, compresslevel=7) as z:
        if _IS_WINDOWS:
            # avoid path limit error in windows.
            # ref: docs/devnote/issues-summary-202401.zh.md
            z.extractall('\\\\?\\' + dir_o.replace('/', '\\'))
        else:
            z.extractall(dir_o)
    
    dlist = tuple(
        x for x in os.listdir(dir_o)
        if x not in ('.DS_Store', '__MACOSX')
    )
    if len(dlist) == 1:
        x = dlist[0]
        if fs.isdir(f'{dir_o}/{x}'):
            if x == dirname_o:
                print(
                    f'move up sub folder [cyan]({x})[/] to be'
                    ' parent',
                    ':vspr',
                )
                dir_m = f'{dir_o}_tmp'
                assert not fs.exist(dir_m)
                os.rename(dir_o, dir_m)
                shutil.move(f'{dir_m}/{x}', dir_o)
                shutil.rmtree(dir_m)
            else:
                print(
                    f'notice there is only one folder [magenta]({x})[/] in '
                    f'this folder: [yellow]{dir_o}[/]. '
                    '[dim](we don\'t move up it because its name is not same '
                    'with its parent.)[/]',
                    ':r',
                )
    return dir_o


def _overwrite(target: str, scheme: t.Optional[bool]) -> bool:
    """
    args:
        scheme:
            True: overwrite
            False: no overwrite, and raise an FileExistsError
            None: no overwrite, no error (skip)
    returns:
        True tells the caller that we DID overwrite.
        False tells the caller that we CANNOT overwrite.
        the caller should check this value and care about what to do next.
        usually, the caller will go on its work if it True, or return directly \
        if it False.
    """
    if scheme is None:
        return False
    if scheme is True:
        if os.path.isdir(target):
            shutil.rmtree(target)
        elif os.path.isfile(target):
            os.remove(target)
        elif os.path.islink(target):
            os.unlink(target)
        else:
            raise Exception(target)
        return True
    if scheme is False:
        raise FileExistsError(target)
