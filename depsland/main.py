from os import listdir, mkdir, path as ospath
from os.path import exists

from lk_logger import lk

from .conf import VenvConf
from .finder import PackageFinder
from .pip import Pip, send_cmd
from .typehint import *

finder = ...  # type: PackageFinder


def create_venv(target_name: str, *keys: TKey, **kwargs):
    """
    
    Args:
        target_name: target directory name. for example 'hello_world_venv', this
            will create `{VenvConf.venv_dir}/hello_world_venv` directory.
        *keys: e.g. 'requests', 'pillow', 'py-cui', etc.
            note:
                1. name is case insensitive
        **kwargs:
            pip: a configurable `Pip` class. see `pip.py::class:Pip`.
            finder: `finder.py::class:PackageFinder`. the default finder is
                `PackageFinder(VenvConf.lib_dir)`.
    """
    global finder
    finder = kwargs.get('finder', PackageFinder(VenvConf.lib_dir))
    pip = kwargs.get('pip', Pip())
    
    target = f'{VenvConf.venv_dir}/{target_name}'
    if not exists(target):
        _create_target_dir(target)
    
    pip_install(*keys, pip=pip)
    
    finder.reindexing()
    
    keys = tuple(map(finder.normalize_key, keys))
    deploy(*keys, lib_dir=f'{target}/lib/site-packages')


def _create_target_dir(target: TPath):
    """
    see `../docs/project-structure.md::h1:VENV_HOME`
    """
    mkdir(target)
    mkdir(f'{target}/lib')
    mkdir(f'{target}/lib/site-packages')
    
    mklink(VenvConf.scripts_dir, f'{target}/scripts')
    mklinks(VenvConf.bin_dir, target, listdir(VenvConf.bin_dir))
    
    for d in listdir(extra := f'{VenvConf.venv_home}/lib_extra'):
        # d: 'lib_pip', 'lib_tk'
        mklinks(f'{extra}/{d}', f'{target}/lib/site-packages',
                listdir(f'{extra}/{d}'))
    

def pip_install(*keys: TKey, pip: Pip):
    global finder
    
    for k in keys:
        if not finder.exists(k):
            lk.loga('installing', k)
            pip.install(k)


def deploy(*keys: TNormalizedKey, lib_dir: TPath):
    global finder
    
    def recurse(keys, collect: set):
        for k in keys:
            if k in collect:
                continue
            collect.add(k)
            recurse(finder.get_dependencies(k), collect)
        return collect
    
    all_keys = recurse(keys, set())
    lk.loga(all_keys)
    
    basenames = []
    for k in all_keys:
        try:
            info = finder.get_info(k)
        except ModuleNotFoundError:
            lk.logt('[E0516]', 'module not found', k)
            continue
        basenames.extend(info['path'])
    
    # lk.loga(basenames)
    mklinks(finder.lib_root, lib_dir, basenames)


def mklinks(src_dir: TPath, dst_dir: TPath, names: Union[tuple, list]):
    for n in names:
        mklink(f'{src_dir}/{n}', f'{dst_dir}/{n}')


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
