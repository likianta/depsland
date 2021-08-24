import os
from os import path as ospath
from textwrap import dedent
from zipfile import ZipFile

from lk_utils import send_cmd

from .typehint import Literal, TPath, TPyVersion

_TPyVersionNum = Literal[
    '2.7', '2.7-32',
    '3.0', '3.0-32',
    '3.1', '3.1-32',
    '3.2', '3.2-32',
    '3.3', '3.3-32',
    '3.4', '3.4-32',
    '3.5', '3.5-32',
    '3.6', '3.6-32',
    '3.7', '3.7-32',
    '3.8', '3.8-32',
    '3.9', '3.9-32',
]


def pyversion_2_num(pyversion: TPyVersion) -> _TPyVersionNum:
    v = pyversion.removeprefix('python')
    assert len(v) == 2, v
    major, suffix = v[0], v[1]
    # noinspection PyTypeChecker
    return f'{major}.{suffix}'


def mklink(src_path: TPath, dst_path: TPath):
    """

    References:
        比较 Windows 上四种不同的文件 (夹) 链接方式 (NTFS 的硬链接, 目录联接, 符
            号链接, 和大家熟知的快捷方式) https://blog.walterlv.com/post/ntfs
            -link-comparisons.html
    """
    assert ospath.exists(src_path), src_path
    if ospath.exists(dst_path):
        return
    
    if ospath.isdir(src_path):
        send_cmd(f'mklink /J "{dst_path}" "{src_path}"')
    elif ospath.isfile(src_path):
        send_cmd(f'mklink /H "{dst_path}" "{src_path}"')
    else:
        raise Exception(src_path)


def mklinks(src_dir: TPath, dst_dir: TPath, names=None):
    """

    Args:
        src_dir:
        dst_dir:
        names: Optional[Iterable[str]]
    """
    for n in (names or os.listdir(src_dir)):
        mklink(f'{src_dir}/{n}', f'{dst_dir}/{n}')


def unzip_file(src_file, dst_dir, complete_delete=False):
    file_handle = ZipFile(src_file)
    file_handle.extractall(dst_dir)
    
    if complete_delete:
        # delete zip file
        from os import remove
        remove(src_file)
    
    return dst_dir


def send_cmd_bat(cmd: str):
    cmd = dedent(cmd).replace('|\n', '').replace('\n', '&')
    return os.system(cmd)
