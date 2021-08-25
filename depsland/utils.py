import os
from os import path as ospath
from textwrap import dedent
from zipfile import ZipFile

from dephell_specifier import RangeSpecifier
from lk_utils import send_cmd

from .typehint import *


def pyversion_2_num(pyversion: TPyVersion) -> TPyVersionNum:
    v = pyversion.removeprefix('python')
    assert len(v) == 2, v
    major, suffix = v[0], v[1]
    # noinspection PyTypeChecker
    return f'{major}.{suffix}'


def mklink(src_path: TPath, dst_path: TPath, exist_ok=False):
    """

    References:
        比较 Windows 上四种不同的文件 (夹) 链接方式 (NTFS 的硬链接, 目录联接, 符
            号链接, 和大家熟知的快捷方式) https://blog.walterlv.com/post/ntfs
            -link-comparisons.html
    """
    assert ospath.exists(src_path), src_path
    if ospath.exists(dst_path):
        if exist_ok:
            return dst_path
        else:
            raise FileExistsError(dst_path)
    
    if ospath.isdir(src_path):
        send_cmd(f'mklink /J "{dst_path}" "{src_path}"')
    elif ospath.isfile(src_path):
        send_cmd(f'mklink /H "{dst_path}" "{src_path}"')
    else:
        raise Exception(src_path)
    
    return dst_path


def mklinks(src_dir: TPath, dst_dir: TPath, names=None, exist_ok=False):
    out = []
    for n in (names or os.listdir(src_dir)):
        out.append(mklink(f'{src_dir}/{n}', f'{dst_dir}/{n}', exist_ok))
    return out


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


def find_best_matched_version(
        ver_spec: TVersionSpec, ver_list: list[TVersion]
) -> Optional[TVersion]:
    """
    
    Args:
        ver_spec: 'version specifier', e.g. '>=3.0', '==1.*', '>=1.2,!=1.2.4',
            ...
        ver_list: a group of fixed version numbers.
            e.g. ['2014.04', '2.0.0.post3', '1.0.2a0', '1.0.2', ...]
            note the elements have already been sorted by descending order.
            i.e. `ver_list[0]` is latest version, `ver_list[-1]` is oldest.
            see PEP-440: https://www.python.org/dev/peps/pep-0440/#version
            -specifiers
    
    References:
        https://github.com/dephell/dephell_specifier
            Usages:
                >>> from dephell_specifier import RangeSpecifier
                >>> '3.4' in RangeSpecifier('*')
                True
                >>> '3.4' in RangeSpecifier('<=2.7')
                False
                >>> '3.4' in RangeSpecifier('>2.7')
                True
    """
    if ver_spec == 'latest' or ver_spec == '':
        return ver_list[0]
    
    spec = RangeSpecifier(ver_spec)
    for v in ver_list:
        if v in spec:
            return v
    else:
        return None
