import os
from os.path import exists
from pathlib import Path

from lk_logger import lk


class T:
    import typing as t
    FileExistScheme = t.Literal['error', 'keep', 'overwrite']
    List = t.List
    Optional = t.Optional
    Path = str
    Paths = t.List[Path]


def mklink(src: T.Path, dst: T.Path, force=False) -> T.Path:
    """
    references:
        common method to create symlink:
            https://csatlas.com/python-create-symlink/
    """
    assert exists(src), f'source path does not exist: {src}'
    if force is True and exists(dst):
        return dst
    if force is False and exists(dst):
        raise Exception(f'destination path already exists: {dst}')
    Path(dst).symlink_to(src)
    return dst


def mklinks(src_dir: T.Path, dst_dir: T.Path,
            names: T.Optional[T.List[str]] = None,
            force=False) -> T.Paths:
    out = []
    for n in (names or os.listdir(src_dir)):
        out.append(mklink(f'{src_dir}/{n}', f'{dst_dir}/{n}', force=force))
    return out


def mergelink(src_dir: T.Path, dst_dir: T.Path, new_dir: T.Path,
              file_exist_scheme: T.FileExistScheme = 'error') -> T.Path:
    src_names = os.listdir(src_dir)
    dst_names = os.listdir(dst_dir)
    
    for sn in src_names:
        sub_src_path = f'{src_dir}/{sn}'
        sub_dst_path = f'{dst_dir}/{sn}'
        sub_new_path = f'{new_dir}/{sn}'
        if sn in dst_names:
            if os.path.isdir(sub_src_path):
                os.mkdir(sub_new_path)
                mergelink(
                    sub_src_path, sub_dst_path, sub_new_path,
                    file_exist_scheme
                )
            else:
                if file_exist_scheme == 'error':
                    raise FileExistsError(sub_dst_path)
                elif file_exist_scheme == 'keep':
                    mklink(sub_dst_path, sub_new_path)
                elif file_exist_scheme == 'overwrite':
                    mklink(sub_src_path, sub_new_path)
        else:
            mklink(sub_src_path, sub_new_path)
    
    new_names = os.listdir(new_dir)
    for n in dst_names:
        sub_dst_path = f'{dst_dir}/{n}'
        sub_new_path = f'{new_dir}/{n}'
        assert exists(sub_dst_path), (
            n,
            n in os.listdir(dst_dir),
            sub_dst_path
        )
        if n not in new_names:
            mklink(sub_dst_path, sub_new_path)
    
    return new_dir


def mergelinks(src_dir: T.Path, dst_dir: T.Path,
               file_exist_scheme: T.FileExistScheme = 'error') -> T.Paths:
    out = []
    dst_names = os.listdir(dst_dir)
    
    for n in os.listdir(src_dir):
        src_path = f'{src_dir}/{n}'
        dst_path = f'{dst_dir}/{n}'
        
        if n in dst_names:
            if os.path.isdir(src_path):
                lk.logt('[D2205]', f'merging "{n}" ({src_dir} -> {dst_dir})')
                
                temp = dst_path
                while exists(temp):
                    temp += '_bak'
                else:
                    os.rename(dst_path, temp)
                new_path = dst_path
                dst_path = temp
                if not exists(new_path):
                    os.mkdir(new_path)
                # os.makedirs(new_path, exist_ok=True)
                
                mergelink(src_path, dst_path, new_path, file_exist_scheme)
            else:
                if file_exist_scheme == 'error':
                    raise FileExistsError(dst_path)
                elif file_exist_scheme == 'keep':
                    pass
                elif file_exist_scheme == 'override':
                    os.remove(dst_path)
                    mklink(src_path, dst_path)
        else:
            mklink(src_path, dst_path, force=False)
        
        out.append(dst_path)
    
    return out
