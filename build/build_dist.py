from os import listdir
from os.path import exists

from lk_logger import lk
from pyportable_installer import full_build

from sidework import analyse_local_packages
from sidework import show_pypi_index_data


def standard_packing():
    conf = full_build('pyproject.json')
    if exists(d := conf['build']['dist_dir'] + '/lib/pytransform'):
        from shutil import move
        move(d, conf['build']['dist_dir'] + '/venv/lib/pytransform')


def full_packing():
    conf = full_build('pyproject.json')
    if exists(d := conf['build']['dist_dir'] + '/lib/pytransform'):
        from shutil import move
        move(d, conf['build']['dist_dir'] + '/venv/lib/pytransform')
    
    lk.logd('preinstall packages')
    lk.logp(listdir('assets/preinstalled_packages'))
    
    # dst_root = conf['build']['dist_dir']
    # for p, n in find_files('assets/preinstalled_packages', fmt='zip'):
    #     copyfile(p, f'{dst_root}/src/pypi/downloads/{n}')
    
    analyse_local_packages.main(
        'assets/preinstalled_packages',
        conf['build']['dist_dir'] + '/src/pypi'
    )
    
    # show indexed data
    show_pypi_index_data.main()


if __name__ == '__main__':
    standard_packing()
    # full_packing()
