from os import listdir, mkdir, path as ospath
from os.path import exists

from lk_logger import lk
from lk_utils import send_cmd, dumps

from .conf import VenvConf
from .pip import Pip
from .typehint import *


def create_venv(target_name: str, requirements: Union[TPath, list[TRawName]],
                pip=None):
    """
    
    Args:
        target_name: target directory name. for example 'hello_world_venv',
            this will create `{VenvConf.venv_dir}/hello_world_venv` directory.
        requirements: e.g. 'requests', 'pillow', 'numpy', etc.
            note:
                1. the name is case insensitive
        pip: Optional[Pip]
    """
    # global finder
    # finder = kwargs.get('finder', PackageFinder(VenvConf.lib_dir))
    # pip = kwargs.get('pip', Pip())
    
    dl_dir = VenvConf.download_dir
    src_dir = VenvConf.lib_dir
    dst_dir = VenvConf.venv_dir + '/' + target_name
    
    if not pip:
        pip = Pip(dl_dir, quiet=False)
        
    if not exists(dst_dir):
        _init_venv_dir(dst_dir)
        
    if not isinstance(requirements, str):
        dumps(requirements, f := '../cache/requirements.txt')
    else:
        from lk_utils.read_and_write import load_list
        f = requirements
        requirements = [name for name in load_list(f)
                        if name and not name.startswith('#')]
        
    pip.download_r(f, dl_dir)
    pip.install_r(f, src_dir)
    
    all_requirements = set()
    for name in requirements:
        all_requirements.update(pip.show_dependencies(name))
    lk.logp(all_requirements)

    locations = set()
    for name in all_requirements:
        locations.update(pip.show_locations(name))
    
    # deploy
    lk.logt('[D2943]', src_dir, dst_dir)
    lk.logp('[D2944]', locations)
    mklinks(src_dir, dst_dir + '/' + 'site-packages', locations)


def _init_venv_dir(target: TPath):
    """
    see `../docs/project-structure.md > chapters:h1:VENV_HOME`
    """
    mkdir(f'{target}')
    mkdir(f'{target}/site-packages')
    
    mklinks(VenvConf.bin_dir, f'{target}')
    mklink(VenvConf.scripts_dir, f'{target}/scripts')
    
    # FIXME
    # mklinks(f'{VenvConf.lib_extra_dir}/lib_tk', f'{target}/site-packages')
    # mklinks(f'{VenvConf.lib_extra_dir}/lib_pip', f'{target}/site-packages')


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
    for n in (names or listdir(src_dir)):
        mklink(f'{src_dir}/{n}', f'{dst_dir}/{n}')
