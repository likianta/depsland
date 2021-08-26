import os
from distutils.version import LooseVersion, StrictVersion
from os import listdir, mkdir
from os.path import exists, isdir, isfile
from textwrap import dedent
from zipfile import ZipFile

from dephell_specifier import RangeSpecifier
from lk_logger import lk
from lk_utils import send_cmd

from .data_struct.special_versions import IGNORE, LATEST
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
    assert exists(src_path), src_path
    if exists(dst_path):
        if exist_ok:
            return dst_path
        else:
            raise FileExistsError(dst_path)
    
    if isdir(src_path):
        send_cmd(f'mklink /J "{dst_path}" "{src_path}"')
    elif isfile(src_path):
        send_cmd(f'mklink /H "{dst_path}" "{src_path}"')
    else:
        raise Exception(src_path)
    
    return dst_path


def mklinks(src_dir: TPath, dst_dir: TPath, names=None, exist_ok=False):
    out = []
    for n in (names or listdir(src_dir)):
        out.append(mklink(f'{src_dir}/{n}', f'{dst_dir}/{n}', exist_ok))
    return out


def mergelink(src_dir, dst_dir, new_dir, file_exist_handle='error'):
    src_names = listdir(src_dir)
    dst_names = listdir(dst_dir)
    
    for sn in src_names:
        sub_src_path = f'{src_dir}/{sn}'
        sub_dst_path = f'{dst_dir}/{sn}'
        sub_new_path = f'{new_dir}/{sn}'
        if sn in dst_names:
            if isdir(sub_src_path):
                mkdir(sub_new_path)
                mergelink(
                    sub_src_path, sub_dst_path, sub_new_path,
                    file_exist_handle
                )
            else:
                if file_exist_handle == 'error':
                    raise FileExistsError(sub_dst_path)
                elif file_exist_handle == 'keep':
                    mklink(sub_dst_path, sub_new_path)
                elif file_exist_handle == 'override':
                    mklink(sub_src_path, sub_new_path)
        else:
            mklink(sub_src_path, sub_new_path)
    
    new_names = listdir(new_dir)
    for n in dst_names:
        sub_dst_path = f'{dst_dir}/{n}'
        sub_new_path = f'{new_dir}/{n}'
        assert exists(sub_dst_path), (
            n,
            n in listdir(dst_dir),
            sub_dst_path
        )
        if n not in new_names:
            mklink(sub_dst_path, sub_new_path)
    
    return new_dir


def mergelinks(src_dir, dst_dir, file_exist_handle='error'):
    out = []
    dst_names = listdir(dst_dir)
    
    for n in listdir(src_dir):
        src_path = f'{src_dir}/{n}'
        dst_path = f'{dst_dir}/{n}'
        
        if n in dst_names:
            if isdir(src_path):
                lk.logt('[D2205]', f'merging "{n}" ({src_dir} -> {dst_dir})')
                
                temp = dst_path
                while exists(temp):
                    temp += '_bak'
                else:
                    os.rename(dst_path, temp)
                new_path = dst_path
                dst_path = temp
                if not exists(new_path):
                    mkdir(new_path)
                # os.makedirs(new_path, exist_ok=True)
                
                mergelink(src_path, dst_path, new_path, file_exist_handle)
            else:
                if file_exist_handle == 'error':
                    raise FileExistsError(dst_path)
                elif file_exist_handle == 'keep':
                    pass
                elif file_exist_handle == 'override':
                    os.remove(dst_path)
                    mklink(src_path, dst_path)
        else:
            mklink(src_path, dst_path, exist_ok=False)
        
        out.append(dst_path)
    
    return out


def unzip_file(src_file, dst_dir, complete_delete=False):
    file_handle = ZipFile(src_file)
    file_handle.extractall(dst_dir)
    
    if complete_delete:
        # delete zip file
        from os import remove
        remove(src_file)
    
    return dst_dir


def send_cmd_bat(cmd: str):  # DELETE
    cmd = dedent(cmd).replace('|\n', '').replace('\n', '&')
    return os.system(cmd)


# -----------------------------------------------------------------------------

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
    # case 1
    if not ver_list:
        return None
    
    # case 2
    if ver_list == [IGNORE]:  # see `pypi.py > LocalPyPI > _refresh_local
        #   _repo > code:'lk.logt('[D3411]', 'ignoring this req', req) ...'`
        return IGNORE
    else:
        assert IGNORE not in ver_list
    
    # case 3
    if ver_spec in (LATEST, ''):
        return ver_list[0]
    
    # case 4
    spec = RangeSpecifier(ver_spec)
    for v in ver_list:
        if v in spec:
            return v
    else:
        return None


def sort_versions(versions: list[TVersion], reverse=True):
    """
    References:
        Sort versions in Python:
            https://stackoverflow.com/questions/12255554/sort-versions-in-python
            /12255578
        The LooseVersion and StrictVersion difference:
            https://www.python.org/dev/peps/pep-0386/
    """
    
    def _normalize_version(v: Union[TNameId, TVersion]):
        # TODO: the incoming `param:v` type must be TVersion; TNameId should be
        #   removed.
        if '-' in v:
            v = v.split('-', 1)[-1]
        if v in ('', '*', 'latest'):
            return '999999.999.999'
        else:
            return v
    
    try:
        versions.sort(key=lambda v: StrictVersion(_normalize_version(v)),
                      # `x` type is Union[TNameId, TVersion], for TNameId we
                      # need to split out the name part.
                      reverse=reverse)
    except ValueError as exception_point:
        lk.logt('[I1543]', f'strict version comparison failed because of: '
                           f'"{exception_point}"', 'use loose compare instead')
        try:
            versions.sort(key=lambda v: LooseVersion(_normalize_version(v)),
                          reverse=reverse)
        except Exception as e:
            lk.logt('[E2123]', versions)
            raise e
    return versions
