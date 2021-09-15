import os
import shutil
from os.path import exists

from pyportable_installer import full_build


def build_standard_version():
    conf = full_build('pyproject.json')
    
    _copy_runtime(conf)
    
    d = conf['build']['dist_dir'] + \
        '/venv/lib/site-packages/embed_python_manager'
    if exists(f'{d}/assets'):
        shutil.rmtree(f'{d}/assets')
    os.mkdir(f'{d}/assets')
    os.mkdir(f'{d}/assets/embed_python')
    os.mkdir(f'{d}/assets/embed_python/windows')
    os.mkdir(f'{d}/assets/pip_suits')
    os.mkdir(f'{d}/assets/pip_suits/python2')
    os.mkdir(f'{d}/assets/pip_suits/python3')
    os.mkdir(f'{d}/assets/tk_suits')
    os.mkdir(f'{d}/assets/tk_suits/python2')
    # os.mkdir(f'{d}/assets/tk_suits/python3')
    # about 5MB
    shutil.copytree('assets/post_build/embed_python_manager/assets/tk_suits'
                    '/python3', f'{d}/assets/tk_suits/python3')
    
    os.rename(conf['build']['dist_dir'],
              conf['build']['dist_dir'] + '-win64-standard')


def build_full_version():
    conf = full_build('pyproject.json')
    
    _copy_runtime(conf)

    d = conf['build']['dist_dir'] + f'/venv/lib/site-packages/embed_python' \
                                    f'_manager/assets'
    if exists(d):
        shutil.rmtree(d)
    # about 150MB
    shutil.copytree('assets/post_build/embed_python_manager/assets', d)
    
    # lk.logd('preinstall packages')
    # lk.logp(os.listdir('assets/preinstalled_packages'))
    #
    # # dst_root = conf['build']['dist_dir']
    # # for p, n in find_files('assets/preinstalled_packages', fmt='zip'):
    # #     copyfile(p, f'{dst_root}/src/pypi/downloads/{n}')
    #
    # analyse_local_packages.main(
    #     'assets/preinstalled_packages',
    #     conf['build']['dist_dir'] + '/src/pypi'
    # )
    #
    # # show indexed data
    # show_pypi_index_data.main()
    
    os.rename(conf['build']['dist_dir'],
              conf['build']['dist_dir'] + '-win64-full')


def _copy_runtime(conf):
    if exists(conf['build']['dist_dir'] + '/lib/pyportable_runtime'):
        dir_i = conf['build']['dist_dir'] + '/lib'
        dir_o = conf['build']['dist_dir'] + '/venv/lib/site-packages'
        
        from shutil import move
        move(f'{dir_i}/pyportable_runtime', f'{dir_o}/pyportable_runtime')
        move(f'{dir_i}/Cryptodome', f'{dir_o}/Cryptodome')


if __name__ == '__main__':
    # build_standard_version()
    build_full_version()
