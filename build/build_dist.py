from shutil import copyfile

from lk_logger import lk
from lk_utils import find_files
from pyportable_installer import full_build

from sidework import analyse_local_packages


def standard_packing():
    full_build('pyproject.json')


def full_packing():
    conf = full_build('pyproject.json')
    
    lk.logd()
    
    dst_root = conf['build']['dist_dir']
    for p, n in find_files('assets/preinstalled_packages', fmt='zip'):
        copyfile(p, f'{dst_root}/src/pypi/downloads/{n}')
    
    analyse_local_packages.main(
        f'{dst_root}/src/pypi/downloads',
        conf['build']['dist_dir'] + '/src/pypi'
    )


if __name__ == '__main__':
    full_packing()
