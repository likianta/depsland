import os
import shutil
from os.path import exists

try:
    # noinspection PyUnresolvedReferences
    from pyportable_installer import full_build
except ImportError:
    try:
        import sys
        dir_0 = input('pyportable_installer parent dir: ')
        dir_1 = input('pyportable_installer related venv dir: ')
        sys.path.append(dir_0)
        sys.path.append(f'{dir_1}/lib/site-packages')
        # noinspection PyUnresolvedReferences
        from pyportable_installer import full_build
    except Exception as e:
        raise e
    else:
        del sys


def _precheck():
    if not exists('./pyportable_runtime'):
        raise Exception(
            'couldn\'t find precompiled pyportable_runtime package.',
            'see `~/docs/steps-to-prebuild-pyportable-runtime-package.zh.md` '
            'for help.'
        )


def build_standard_version():
    _precheck()
    
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
    _precheck()
    
    conf = full_build('pyproject.json')
    
    _copy_runtime(conf)
    
    d = conf['build']['dist_dir'] + f'/venv/lib/site-packages/embed_python' \
                                    f'_manager/assets'
    if exists(d):
        shutil.rmtree(d)
    # about 33MB
    shutil.copytree('assets/post_build/embed_python_manager/assets', d)
    
    os.rename(conf['build']['dist_dir'],
              conf['build']['dist_dir'] + '-win64-full')


def _copy_runtime(conf):
    if conf['build']['compiler']['name'] != 'pyportable_crypto':
        return
    src_dir = conf['build']['dist_dir'] + '/lib'
    dst_dir = conf['build']['dist_dir'] + '/venv/lib/site-packages'
    shutil.copytree(f'{src_dir}/pyportable_runtime',
                    f'{dst_dir}/pyportable_runtime')


if __name__ == '__main__':
    build_standard_version()
    build_full_version()
