import os
import typing as t
from os.path import exists
from pathlib import Path


def mklink(src: str, dst: str, force=False) -> str:
    """
    references:
        common method to create symlink:
            https://csatlas.com/python-create-symlink/
    """
    assert exists(src), f'source path does not exist: {src}'
    if force is True and exists(dst): return dst
    if force is False and exists(dst):
        raise FileExistsError(f'destination path already exists: {dst}')
    Path(dst).symlink_to(src)
    return dst


def mklinks(
    src_dir: str,
    dst_dir: str,
    names: t.Optional[t.List[str]] = None,
    force=False,
) -> t.List[str]:
    out = []
    for n in names or os.listdir(src_dir):
        out.append(mklink(f'{src_dir}/{n}', f'{dst_dir}/{n}', force=force))
    return out


def mergelink(
    src_dir: str, dst_dir: str, new_dir: str, overwrite: bool = None
) -> str:
    src_names = os.listdir(src_dir)
    dst_names = os.listdir(dst_dir)
    
    for sn in src_names:
        sub_src_path = f'{src_dir}/{sn}'
        sub_dst_path = f'{dst_dir}/{sn}'
        sub_new_path = f'{new_dir}/{sn}'
        if sn in dst_names:
            if os.path.isdir(sub_src_path):
                os.mkdir(sub_new_path)
                mergelink(sub_src_path, sub_dst_path, sub_new_path, overwrite)
            else:
                if overwrite is None:
                    mklink(sub_dst_path, sub_new_path)
                elif overwrite is True:
                    mklink(sub_src_path, sub_new_path)
                else:  # False
                    raise FileExistsError(sub_dst_path)
        else:
            mklink(sub_src_path, sub_new_path)
    
    new_names = os.listdir(new_dir)
    for n in dst_names:
        sub_dst_path = f'{dst_dir}/{n}'
        sub_new_path = f'{new_dir}/{n}'
        assert exists(sub_dst_path), (n, n in os.listdir(dst_dir), sub_dst_path)
        if n not in new_names:
            mklink(sub_dst_path, sub_new_path)
    
    return new_dir


def mergelinks(
    src_dir: str, dst_dir: str, overwrite: bool = None
) -> t.List[str]:
    out = []
    dst_names = os.listdir(dst_dir)
    
    for n in os.listdir(src_dir):
        src_path = f'{src_dir}/{n}'
        dst_path = f'{dst_dir}/{n}'
        
        if n in dst_names:
            if os.path.isdir(src_path):
                print(':v', f'merging "{n}" ({src_dir} -> {dst_dir})')
                
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
                
                mergelink(src_path, dst_path, new_path, overwrite)
            else:
                if overwrite is None:
                    pass
                elif overwrite is True:
                    os.remove(dst_path)
                    mklink(src_path, dst_path)
                else:  # False
                    raise FileExistsError(dst_path)
        else:
            mklink(src_path, dst_path, force=False)
        
        out.append(dst_path)
    
    return out
